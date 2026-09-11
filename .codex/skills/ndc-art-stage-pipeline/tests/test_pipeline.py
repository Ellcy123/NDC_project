"""Concurrency, durable dispatch, scope, and stale-input tests with synthetic adapters."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline as p

class FakeAdapter:
    @staticmethod
    def validate_result(packet, result, base):
        if result['status'] in ('FAIL', 'WAITING_MANUAL'):
            p.need(bool(result.get('reason')), 'Explain the stopped branch')
        return {'verified': True}

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.work_base = self.project / 'managed-work'
        self.root = self.work_base / 'pipeline-test'
        self.root.mkdir(parents=True)
        self.environment = patch.dict(os.environ, {
            'NDC_PLANNING_ROOT': str(self.project),
            'NDC_ART_WORK_ROOT': str(self.work_base),
        })
        self.environment.start(); self.addCleanup(self.environment.stop)
        self.file = self.root / 'synthetic.txt'
        self.file.write_text('fixture')
        (self.root / 'original.jsonl').write_text('{}\n', encoding='utf-8')
        self.plan = {'schema': p.PLAN, 'pipeline_id': 'test', 'pipeline_kind': 'ui_portrait', 'controller_task_id': 'controller', 'execution_mode': 'validation', 'project_root': str(self.project), 'work_root': str(self.root), 'units': [{'unit_id': key, 'producer_task_id': 'upstream', 'authority': {'journal': str(self.root / 'original.jsonl'), 'upstream_jobs': [key + '-master'], 'downstream_jobs': [key + '-big', key + '-small']}} for key in ('A', 'B')]}
        self.db = self.root / 'pipeline.sqlite'
        p.Pipeline.initialize(self.db, self.plan)
        self.pipe = p.Pipeline(self.db)
        self.addCleanup(self.pipe.close)
        def checked(packet):
            p.files_current(packet['files'])
            return {'validation_only': True, 'can_execute': False}
        self.validation = patch.object(p, 'validate_packet', side_effect=checked)
        self.validation.start(); self.addCleanup(self.validation.stop)
        self.settled = patch.object(p.Pipeline, 'operations_settled', return_value=None)
        self.settled.start(); self.addCleanup(self.settled.stop)
        self.adapter = patch.object(p.importlib, 'import_module', return_value=FakeAdapter)
        self.adapter.start(); self.addCleanup(self.adapter.stop)

    def packet(self, key='A', revision=1):
        unit = next(x for x in self.plan['units'] if x['unit_id'] == key)
        return {'schema': p.SCHEMA, 'unit_id': key, 'revision': revision, 'producer_task_id': 'upstream', 'authority': unit['authority'], 'payload': {'synthetic_fixture': True}, 'files': [{'role': 'fixture', 'path': str(self.file), 'sha256': p.file_hash(self.file)}]}

    def publish(self, key='A', revision=1):
        return self.pipe.publish(self.packet(key, revision), 'upstream', self.root)

    def dispatch(self, worker='worker'):
        d = self.pipe.reserve_dispatch('controller')
        self.pipe.dispatch_sent('controller', d['dispatch_id'])
        self.pipe.bind_dispatch('controller', d['dispatch_id'], {'threadId': worker})
        return d

    def complete(self, lease, status='VALIDATION_COMPLETE', reason=None):
        return self.pipe.result(lease, {'status': status, 'unit_id': lease['unit_id'], 'revision': lease['revision'], 'files': [], 'reason': reason})

    def test_first_unit_dispatches_while_second_is_unpublished(self):
        self.publish()
        first = self.dispatch()
        lease = self.pipe.claim('worker', first['dispatch_id'])
        self.publish('B')
        status = self.pipe.status()
        self.assertEqual(status['total_units'], 2)
        self.assertEqual({u['unit_id']:u['status'] for u in status['units']}, {'A':'RUNNING','B':'READY'})
        self.assertFalse(status['whole_pipeline_complete'])
        self.complete(lease)
        next_unit = self.pipe.reserve_dispatch('controller')
        self.assertEqual(next_unit['action'], 'send')
        self.assertEqual(next_unit['target_thread_id'], 'worker')

    def test_repeated_publication_does_not_dispatch_twice(self):
        self.publish()
        self.assertEqual(self.publish()['status'], 'ALREADY_PUBLISHED')
        self.assertEqual(self.pipe.reserve_dispatch('controller')['status'], 'RESERVED')
        blocked = self.pipe.reserve_dispatch('controller')
        self.assertEqual(blocked['status'], 'BLOCKED_EXISTING_DISPATCH')

    def test_atomic_dispatch_send_marker_cannot_repeat(self):
        self.publish(); d = self.pipe.reserve_dispatch('controller')
        self.pipe.dispatch_sent('controller', d['dispatch_id'])
        with self.assertRaisesRegex(ValueError, 'Do not repeat'):
            self.pipe.dispatch_sent('controller', d['dispatch_id'])
        self.pipe.dispatch_unknown('controller', d['dispatch_id'], 'Network result unknown')
        self.assertEqual(self.pipe.reserve_dispatch('controller')['status'], 'BLOCKED_EXISTING_DISPATCH')

    def test_setup_id_is_not_usable_worker_id(self):
        self.publish(); d = self.pipe.reserve_dispatch('controller')
        self.pipe.dispatch_sent('controller', d['dispatch_id'])
        result = self.pipe.bind_dispatch('controller', d['dispatch_id'], {'clientThreadId': 'pending-id'})
        self.assertEqual(result['status'], 'SETUP_PENDING')
        with self.assertRaises(ValueError):
            self.pipe.claim('pending-id', d['dispatch_id'])
        self.pipe.bind_dispatch('controller', d['dispatch_id'], {'threadId': 'real-worker'})
        self.assertEqual(self.pipe.claim('real-worker', d['dispatch_id'])['task_id'], 'real-worker')

    def test_delivered_unclaimed_stale_dispatch_can_be_cancelled_truthfully(self):
        self.publish(); d = self.dispatch()
        self.publish('A', 2)
        with self.assertRaises(ValueError):
            self.pipe.claim('worker', d['dispatch_id'])
        self.pipe.cancel_dispatch('controller', d['dispatch_id'], {'dispatch_id':d['dispatch_id'],'target_task_id':'worker','no_active_turn':True,'confirmed_not_claimed':True,'external_operations_settled':True,'observation':'Delivered task returned a stale-version block before claim'})
        self.assertEqual(self.pipe.reserve_dispatch('controller')['revision'], 2)

    def test_complete_count_rechecks_source_currency(self):
        self.publish(); self.publish('B')
        d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id']); self.complete(lease)
        lease = self.pipe.claim_next('worker'); self.complete(lease)
        self.assertTrue(self.pipe.status()['whole_pipeline_complete'])
        self.file.write_text('source changed after completion')
        report = self.pipe.status()
        self.assertEqual(report['completed_units'], 0)
        self.assertFalse(report['whole_pipeline_complete'])
        self.assertTrue(all(u['status'] == 'STALE' for u in report['units']))

    def test_binding_cannot_precede_app_submission_marker(self):
        self.publish(); d = self.pipe.reserve_dispatch('controller')
        with self.assertRaises(ValueError):
            self.pipe.bind_dispatch('controller', d['dispatch_id'], {'threadId': 'fake'})

    def test_two_simultaneous_claims_have_exactly_one_winner(self):
        self.publish(); d = self.dispatch()
        barrier = threading.Barrier(2)
        winners = []
        def attempt():
            db = p.Pipeline(self.db)
            try:
                barrier.wait()
                winners.append(db.claim('worker', d['dispatch_id']))
            except ValueError:
                pass
            finally:
                db.close()
        threads = [threading.Thread(target=attempt) for _ in range(2)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(len(winners), 1)

    def test_new_revision_fences_old_outputs_and_does_not_drop_full_scope(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        self.publish('A', 2)
        with self.assertRaisesRegex(ValueError, 'new version'):
            self.pipe.guard(lease)
        result = self.complete(lease, reason='Upstream version changed during work')
        self.assertEqual(result['status'], 'STALE')
        self.assertEqual(self.pipe.reserve_dispatch('controller')['revision'], 2)
        self.assertEqual(self.pipe.status()['total_units'], 2)

    def test_character_scene_references_wait_for_own_lease_but_other_scene_can_publish(self):
        # Synthetic core wiring only; native geometry and artistic gates are mocked.
        plan = copy.deepcopy(self.plan)
        root = self.work_base / 'integration-lease-test'
        plan.update(pipeline_kind='character_scene', model_policy=p.INTEGRATION_MODELS, work_root=str(root))
        for unit in plan['units']:
            unit['scope'] = {'cases': [{'case_id': unit['unit_id'] + '-day', 'snapshots': [
                {'snapshot_id': 'whole', 'actor_pose_ids': {'actor': 'pose'}}]}]}
        db = root / 'pipeline.sqlite'
        p.Pipeline.initialize(db, plan)
        pipe = p.Pipeline(db)
        try:
            pipe.publish(self.packet(), 'upstream', self.root)
            d = pipe.reserve_dispatch('controller')
            pipe.dispatch_sent('controller', d['dispatch_id'])
            pipe.bind_dispatch('controller', d['dispatch_id'], {'threadId': 'worker'})
            lease = pipe.claim('worker', d['dispatch_id'])
            self.assertEqual(pipe.publish(self.packet(), 'upstream', self.root)['status'], 'ALREADY_PUBLISHED')
            with self.assertRaisesRegex(ValueError, 'active production lease'):
                pipe.publish(self.packet('A', 2), 'upstream', self.root)
            self.assertEqual(pipe.packet('A')[0]['revision'], 1)
            self.assertEqual(pipe.publish(self.packet('B'), 'upstream', self.root)['status'], 'READY')
            self.assertEqual(pipe.guard(lease)['status'], 'CURRENT')
            pipe.result(lease, {'unit_id': 'A', 'revision': 1, 'status': 'FAIL', 'files': [],
                               'reason': 'Synthetic reference defect; no actual art review'})
            self.assertEqual(pipe.publish(self.packet('A', 2), 'upstream', self.root)['status'], 'READY')
        finally:
            pipe.close()

    def test_same_revision_changed_payload_is_rejected(self):
        self.publish()
        changed = self.packet(); changed['payload']['value'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'Same revision'):
            self.pipe.publish(changed, 'upstream', self.root)

    def test_changed_input_blocks_dispatch_and_preserves_history(self):
        self.publish(); self.file.write_text('changed')
        self.assertEqual(self.pipe.reserve_dispatch('controller')['status'], 'NO_READY_UNIT')
        self.assertEqual(self.pipe.status()['units'][0]['status'], 'STALE')

    def test_manual_wait_frees_worker_for_independent_next_unit(self):
        self.publish(); self.publish('B')
        d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        self.complete(lease, 'WAITING_MANUAL', 'Explicit manual review boundary')
        self.assertEqual(self.pipe.reserve_dispatch('controller')['unit_id'], 'B')

    def test_validation_cannot_claim_artistic_production_pass(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        with self.assertRaisesRegex(ValueError, 'production PASS'):
            self.complete(lease, 'PASS')

    def test_unknown_generation_outcome_blocks_result_release(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        with patch.object(p.Pipeline, 'operations_settled', side_effect=ValueError('unknown submission')):
            with self.assertRaisesRegex(ValueError, 'unknown submission'):
                self.complete(lease)
        self.assertIsNotNone(self.pipe.status()['worker'])

    def test_foreign_output_directory_is_rejected(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        result = {'status':'VALIDATION_COMPLETE','unit_id':'A','revision':1,'files':[{'role':'foreign','path':str(self.file),'sha256':p.file_hash(self.file)}]}
        with self.assertRaisesRegex(ValueError, 'assigned directory'):
            self.pipe.result(lease, result)

    def test_worker_recovery_requires_evidence_and_fences_old_lease(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        with self.assertRaises(ValueError):
            self.pipe.recover_worker('controller', {'worker_task_id':'worker','elapsed_seconds':99999})
        self.pipe.recover_worker('controller', {'worker_task_id':'worker','no_active_turn':True,'external_operations_settled':True,'observation':'Synthetic app/tool observations'})
        with self.assertRaises(ValueError):
            self.pipe.guard(lease)

    def test_original_job_scope_cannot_be_replaced(self):
        changed = self.packet(); changed['authority'] = copy.deepcopy(changed['authority']); changed['authority']['downstream_jobs'] = ['new-zero-budget-job']
        with self.assertRaisesRegex(ValueError, 'original authority'):
            self.pipe.publish(changed, 'upstream', self.root)

    def test_existing_worker_drains_ready_units_without_another_app_send(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        self.publish('B')
        self.complete(lease)
        next_lease = self.pipe.claim_next('worker')
        self.assertEqual(next_lease['unit_id'], 'B')
        self.assertEqual(self.pipe.dispatch(next_lease['dispatch_id'])['action'], 'continue')
        self.complete(next_lease)
        self.assertTrue(self.pipe.status()['whole_pipeline_complete'])
        self.assertEqual(self.pipe.claim_next('worker')['status'], 'WAITING_UPSTREAM')

    def test_unregistered_worker_cannot_take_self_continuation(self):
        self.publish(); self.dispatch()
        with self.assertRaises(ValueError):
            self.pipe.claim_next('another-worker')

    def test_late_setup_response_cannot_downgrade_bound_worker(self):
        self.publish(); d = self.dispatch()
        response = self.pipe.bind_dispatch('controller', d['dispatch_id'], {'clientThreadId': 'late-setup'})
        self.assertEqual(response['status'], 'BOUND')
        self.assertEqual(self.pipe.claim('worker', d['dispatch_id'])['task_id'], 'worker')

    def test_modified_result_receipt_withdraws_completion(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        receipt = self.complete(lease)
        result = p.read(receipt['result_path']); result['status'] = 'FAIL'
        Path(receipt['result_path']).write_text(p.stable(result), encoding='utf-8')
        self.assertEqual(self.pipe.status()['completed_units'], 0)
        self.assertEqual(self.pipe.status()['units'][0]['status'], 'STALE')

    def test_short_journal_writer_is_busy_without_persisting_stale(self):
        self.publish(); d = self.dispatch(); lease = self.pipe.claim('worker', d['dispatch_id'])
        self.complete(lease)
        lock = self.root / 'original.jsonl.lock'; lock.write_text('writer')
        self.assertEqual(self.pipe.status()['units'][0]['status'], 'BUSY')
        lock.unlink()
        self.assertEqual(self.pipe.status()['units'][0]['status'], 'VALIDATION_COMPLETE')

    def test_append_during_read_is_retryable_even_for_partial_json(self):
        packet = self.packet()
        def append_then_partial_read():
            with (self.root / 'original.jsonl').open('a', encoding='utf-8') as handle:
                handle.write('{partial')
            raise ValueError('temporary partial JSON')
        with self.assertRaises(p.PipelineBusy):
            p.consistent_read(packet, append_then_partial_read)

    def test_init_cannot_overwrite_existing_pipeline(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            p.Pipeline.initialize(self.db, self.plan)

    def test_durable_reservation_survives_process_reopen(self):
        self.publish(); self.pipe.reserve_dispatch('controller')
        other = p.Pipeline(self.db)
        try:
            self.assertEqual(other.reserve_dispatch('controller')['status'], 'BLOCKED_EXISTING_DISPATCH')
        finally:
            other.close()

if __name__ == '__main__':
    unittest.main()
