"""Synthetic recovery fixtures; no production evidence or artwork is changed."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import workflow_state as w
import test_workflow_state as legacy


class HistorySourceRevalidationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = legacy.WorkflowTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root, self.job = self.fixture.root, self.fixture.job
        self.path, evidence = self.fixture.history_fixture()
        w.resolve_history(self.path, self.job, evidence)
        self.original = w.log_events(self.path, w.load_batch(self.path))[-1]
        self.source = self.root / 'prior-task.txt'
        self.log = self.root / 'unknown.jsonl'
        self.proposal_path = self.root / 'source-review.json'
        self.original_sources = w.read(Path(self.original['evidence_path']))['sources']
        self.source.write_text('Synthetic prior-task count: two. Later unrelated note.')

    def proposal(self, event=None, sources=None):
        event = event or self.original
        sources = sources or self.original_sources
        return {'schema': 'ndc-prop-history-source-revalidation/v1', 'batch_id': 'test',
                'reviewer': 'synthetic actual-source reviewer', 'reason': 'Read later appended note.',
                'reviews': [{'job_id': self.job, 'resolution_hash': self.original['hash'],
                    'previous_evidence_sha256': event['evidence_sha256'],
                    'confirmed_count': 2, 'determination': 'known_historical',
                    'reason': 'Prior-task two calls are unchanged; appended note has no additional calls.',
                    'sources': [dict(s, previous_sha256=s['sha256'], sha256=w.sha(s['path'])) for s in sources]}]}

    def recover(self, proposal=None):
        w.write_json(self.proposal_path, proposal or self.proposal())
        return w.revalidate_history_source(self.path, self.proposal_path)

    def rejected(self, proposal, pattern):
        before = self.log.read_bytes(), self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, pattern):
            self.recover(proposal)
        self.assertEqual(before, (self.log.read_bytes(), self.path.read_bytes()))

    def test_unreviewed_source_change_still_blocks_progress_and_attempt(self):
        with self.assertRaisesRegex(ValueError, 'source bytes changed'):
            w.progress(self.path)
        prompt = self.root / 'prompt.txt'; prompt.write_text('new fixture prompt')
        with self.assertRaisesRegex(ValueError, 'source bytes changed'):
            w.reserve_attempt(self.path, self.job, prompt, 'fixture retry')

    def test_recovery_preserves_all_bytes_counts_and_next_attempt_number(self):
        old_log = self.log.read_bytes()
        original_evidence = Path(self.original['evidence_path']).read_bytes()
        b = w.load_batch(self.path)
        result = self.recover()
        self.assertEqual(result['counts_preserved'][self.job], 2)
        self.assertTrue(self.log.read_bytes().startswith(old_log))
        self.assertEqual(Path(self.original['evidence_path']).read_bytes(), original_evidence)
        current = w.load_batch(self.path)
        self.assertEqual({k:v for k,v in current.items() if k != 'attempt_head'},
                         {k:v for k,v in b.items() if k != 'attempt_head'})
        self.assertEqual(w.validate(self.path, 2), [])
        prompt = self.root / 'prompt.txt'; prompt.write_text('fixture pair two')
        self.assertEqual(w.reserve_attempt(self.path, self.job, prompt, 'third actual call'), 3)

    def test_revalidation_after_real_attempts_keeps_exhausted_budget(self):
        # Recover the source first, append real calls, then recover a second drift.
        self.recover()
        for n in range(3, 7):
            prompt = self.root / 'prompt.txt'; prompt.write_text('fixture pair ' + str((n+1)//2))
            w.reserve_attempt(self.path, self.job, prompt, 'fixture revision')
        events = w.log_events(self.path, w.load_batch(self.path))
        previous = next(e for e in events if e['type'] == 'history_source_revalidation')
        sources = w.read(Path(previous['evidence_path']))['reviews'][0]['sources']
        self.source.write_text('Still two historical calls. Another unrelated note.')
        self.assertEqual(self.recover(self.proposal(previous, sources))['counts_preserved'][self.job], 6)
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            w.reserve_attempt(self.path, self.job, prompt, 'cannot refund calls')

    def test_changed_count_or_determination_or_bool_count_rejected(self):
        for field, value in [('confirmed_count', 0), ('confirmed_count', True), ('determination', 'new')]:
            with self.subTest(field=field, value=value):
                p = self.proposal(); p['reviews'][0][field] = value
                self.rejected(p, 'cannot change count/determination')

    def test_wrong_job_predecessor_or_old_source_hash_rejected(self):
        for field in ['job_id', 'resolution_hash', 'previous_evidence_sha256']:
            with self.subTest(field=field):
                p = self.proposal(); p['reviews'][0][field] = 'wrong'
                self.rejected(p, 'existing history resolution|predecessor mismatch')
        p = self.proposal(); p['reviews'][0]['sources'][0]['previous_sha256'] = '0'*64
        self.rejected(p, 'previous source hash mismatch')

    def test_source_path_substitution_omission_and_duplicates_rejected(self):
        other = self.root / 'other.txt'; other.write_text('another source')
        p = self.proposal(); p['reviews'][0]['sources'][0].update(path=str(other), sha256=w.sha(other))
        self.rejected(p, 'replace or omit source paths')
        p = self.proposal(); p['reviews'][0]['sources'] = []
        self.rejected(p, 'nonempty')
        p = self.proposal(); p['reviews'][0]['sources'] *= 2
        self.rejected(p, 'duplicate history source path')

    def test_nonexistent_and_incorrect_current_source_rejected(self):
        p = self.proposal(); p['reviews'][0]['sources'][0]['sha256'] = '0'*64
        self.rejected(p, 'source bytes changed')
        self.source.unlink()
        w.write_json(self.proposal_path, p)
        with self.assertRaises(OSError):
            w.revalidate_history_source(self.path, self.proposal_path)

    def test_duplicate_review_and_noop_and_replay_rejected(self):
        p = self.proposal(); p['reviews'] *= 2
        self.rejected(p, 'unique existing')
        p = self.proposal(); p['reviews'][0]['sources'][0]['sha256'] = self.original_sources[0]['sha256']
        self.rejected(p, 'requires changed source bytes')
        p = self.proposal(); self.recover(p)
        self.rejected(p, 'predecessor mismatch')

    def test_missing_findings_rejected(self):
        p = self.proposal(); p['reason'] = ' '
        self.rejected(p, 'incomplete')
        p = self.proposal(); p['reviews'][0]['reason'] = ''
        self.rejected(p, 'actual review findings')

    def test_new_snapshot_tamper_rejected(self):
        result = self.recover()
        Path(result['history_source_revalidation']).write_text('{}')
        self.assertTrue(any('revalidation evidence changed' in e for e in w.validate(self.path, 2)))

    def test_original_snapshot_tamper_remains_rejected_after_recovery(self):
        self.recover()
        Path(self.original['evidence_path']).write_text('{}')
        self.assertTrue(any('history resolution evidence changed' in e for e in w.validate(self.path, 2)))

    def test_log_chain_and_head_and_job_changes_still_block_recovery(self):
        original_log, original_batch = self.log.read_bytes(), self.path.read_bytes()
        for defect in ['chain', 'head', 'jobs']:
            with self.subTest(defect=defect):
                self.log.write_bytes(original_log); self.path.write_bytes(original_batch)
                if defect == 'chain':
                    events = [json.loads(s) for s in self.log.read_text().splitlines()]
                    events[-1]['at'] = 'tampered'
                    self.log.write_text('\n'.join(json.dumps(e) for e in events)+'\n')
                else:
                    b = w.read(self.path)
                    if defect == 'head': b['attempt_head'] = '0'*64
                    else: b['jobs'][self.job]['legacy_attempts'] = 0
                    w.write_json(self.path, b)
                self.rejected(self.proposal(), 'chain damaged|head mismatch|scope/jobs changed')

    def test_multiple_jobs_sharing_a_changed_source_require_complete_atomic_review(self):
        # Set up a second independently resolved job in a separate synthetic batch.
        b = copy.deepcopy(self.fixture.b); b.pop('attempt_head')
        b['attempt_log'] = 'two-jobs.jsonl'
        job2 = 'q|master||closed'
        for key, iid in [(self.job,'p'), (job2,'q')]:
            b['jobs'][key] = dict(item_id=iid, kind='master', scene_id='', state='closed',
                legacy_attempts=6, legacy_evidence={'status':'UNKNOWN_CONSERVATIVE_EXHAUSTION','actual_count':None})
        # A fresh subdirectory avoids colliding with immutable first-fixture snapshots.
        self.path = self.root / 'two' / 'batch.json'; self.path.parent.mkdir()
        b['content_archive'] = str(self.root/'content.json')
        w.write_json(self.path,b); w.initialize(self.path)
        self.log = self.path.parent / 'two-jobs.jsonl'
        for key in [self.job, job2]:
            ep = self.root / ('evidence-' + key[0] + '.json')
            w.write_json(ep, dict(schema='ndc-prop-history-resolution/v1', batch_id='test', job_id=key,
                confirmed_count=2, determination='known_historical', reviewer='fixture', reason='two calls',
                sources=[{'path':str(self.source),'sha256':w.sha(self.source)}]))
            w.resolve_history(self.path,key,ep)
        events = w.log_events(self.path,w.load_batch(self.path))
        resolutions = [e for e in events if e['type']=='legacy_resolution']
        self.source.write_text('Both original jobs still have two calls; later note.')
        reviews = []
        for e in resolutions:
            old = w.read(Path(e['evidence_path']))
            reviews.append(dict(job_id=e['job_id'], resolution_hash=e['hash'], previous_evidence_sha256=e['evidence_sha256'],
                confirmed_count=2, determination='known_historical', reason='Independent two-call history unchanged.',
                sources=[dict(s,previous_sha256=s['sha256'],sha256=w.sha(s['path'])) for s in old['sources']]))
        p = self.proposal(); p['reviews'] = reviews[:1]
        self.rejected(p,'source bytes changed')
        p['reviews'] = reviews
        result = self.recover(p)
        self.assertEqual(result['counts_preserved'],{self.job:2,job2:2})

    def test_recovery_does_not_make_failed_artwork_pass(self):
        b = w.read(self.path); b['artifacts']['master']['rejected'] = True; w.write_json(self.path,b)
        self.recover()
        self.assertTrue(any('rejected' in e for e in w.validate(self.path,5)))

    def test_actual_cli_and_changed_sources_after_recovery(self):
        w.write_json(self.proposal_path,self.proposal())
        result = subprocess.run([sys.executable,str(Path(w.__file__).resolve()),'revalidate-history-source',
            '--batch',str(self.path),'--evidence',str(self.proposal_path)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['counts_preserved'][self.job],2)
        self.source.write_text('Unreviewed later mutation.')
        with self.assertRaisesRegex(ValueError,'source bytes changed'):
            w.progress(self.path)


if __name__ == '__main__':
    unittest.main()
