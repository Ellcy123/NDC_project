"""Synthetic tests for append-only registration of a previously omitted scene job."""
import unittest
from pathlib import Path

import workflow_state as w
import test_workflow_state as legacy


class JobAddendumTests(unittest.TestCase):
    def setUp(self):
        self.fixture = legacy.WorkflowTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.path = self.fixture.path
        self.root = self.fixture.root
        self.job = 'p|scene|s|environment_rebuild'
        self.artifact = 'scene'
        batch = w.read(self.path)
        batch['artifacts'][self.artifact]['status'] = 'PENDING'
        w.write_json(self.path, batch)
        self.source = self.root / 'legacy-scene-attempt.txt'
        self.source.write_text('One original native SC4012-equivalent scene candidate was generated.')
        self.evidence_path = self.root / 'job-addendum-history.json'

    def evidence(self):
        return {
            'schema': 'ndc-prop-job-addendum-history/v1',
            'batch_id': 'test', 'job_id': self.job, 'artifact_id': self.artifact,
            'confirmed_count': 1, 'determination': 'known_historical',
            'reviewer': 'synthetic source reviewer',
            'reason': 'The preserved source explicitly records one prior scene candidate for this exact output role.',
            'sources': [{'path': str(self.source), 'sha256': w.sha(self.source)}],
        }

    def add(self, evidence=None):
        w.write_json(self.evidence_path, evidence or self.evidence())
        return w.register_job_addendum(
            self.path, self.job, self.artifact, self.evidence_path,
            'The locked fixture omitted the required scene job; append the verified historical job only.',
        )

    def test_addendum_preserves_history_and_reserves_the_second_attempt(self):
        result = self.add()
        self.assertEqual(result['historical_attempts'], 1)
        batch = w.load_batch(self.path)
        self.assertEqual(batch['jobs'][self.job]['legacy_attempts'], 1)
        self.assertEqual(batch['artifacts'][self.artifact]['job_id'], self.job)
        events = w.log_events(self.path, batch)
        self.assertEqual(events[-1]['type'], 'job_addendum')
        prompt = self.root / 'actual-prompt.txt'
        prompt.write_text('A distinct second native scene candidate.')
        self.assertEqual(w.reserve_attempt(self.path, self.job, prompt, 'first call in current conversation'), 1)
        self.assertEqual(w.log_events(self.path, w.load_batch(self.path))[-1]['number'], 2)

    def test_addendum_rejects_invalid_history_without_changing_batch_or_log(self):
        proposal = self.evidence()
        proposal['confirmed_count'] = 4
        w.write_json(self.evidence_path, proposal)
        before = (self.path.read_bytes(), (self.root / 'attempts.jsonl').read_bytes())
        with self.assertRaisesRegex(ValueError, 'incomplete job-addendum'):
            w.register_job_addendum(self.path, self.job, self.artifact, self.evidence_path, 'specific reason')
        self.assertEqual(before, (self.path.read_bytes(), (self.root / 'attempts.jsonl').read_bytes()))

    def test_addendum_detects_job_and_history_tampering(self):
        self.add()
        batch = w.read(self.path)
        batch['jobs'][self.job]['legacy_attempts'] = 0
        w.write_json(self.path, batch)
        self.assertTrue(any('invalid job addendum' in error for error in w.validate(self.path, 1)))
        batch = w.read(self.path)
        batch['jobs'][self.job]['legacy_attempts'] = 1
        w.write_json(self.path, batch)
        self.source.write_text('Unreviewed changed historical source.')
        self.assertTrue(any('history source bytes changed' in error for error in w.validate(self.path, 1)))

    def test_addendum_remains_valid_after_its_bound_scene_passes(self):
        self.add()
        batch = w.read(self.path)
        batch['artifacts'][self.artifact]['status'] = 'PASS'
        w.write_json(self.path, batch)
        errors = w.validate(self.path, 1)
        self.assertFalse(any('job addendum must bind' in error for error in errors))

    def test_addendum_cannot_rebind_a_passed_or_existing_job_artifact(self):
        batch = w.read(self.path)
        batch['artifacts'][self.artifact]['status'] = 'PASS'
        w.write_json(self.path, batch)
        w.write_json(self.evidence_path, self.evidence())
        with self.assertRaisesRegex(ValueError, 'unbound pending'):
            w.register_job_addendum(self.path, self.job, self.artifact, self.evidence_path, 'specific reason')
        batch = w.read(self.path)
        batch['artifacts'][self.artifact]['status'] = 'PENDING'
        batch['artifacts'][self.artifact]['job_id'] = 'p|scene|s|old'
        w.write_json(self.path, batch)
        with self.assertRaisesRegex(ValueError, 'unbound pending'):
            w.register_job_addendum(self.path, self.job, self.artifact, self.evidence_path, 'specific reason')


if __name__ == '__main__':
    unittest.main()
