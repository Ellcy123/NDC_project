"""Queue inspection completion must not turn a failed image into a passing asset."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ReviewAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'fixture.png'
        self.output.write_bytes(b'synthetic test artifact; no artistic approval')
        self.record = {
            'schema': 'ndc-stage-visual-self-check/v1', 'stage_id': 'test',
            'reviewer': 'test fixture', 'reviewed_at': '2026-09-08T00:00:00Z',
            'visual_check_status': 'FAIL', 'rework_stage': 'test',
            'outputs': [{'path': str(self.output), 'sha256': hashlib.sha256(self.output.read_bytes()).hexdigest()}],
            'inputs': [],
            'views': [{'kind': kind, 'path': str(self.output)} for kind in ('whole_100', 'local_200_or_tiles')],
            'criteria': [{'name': 'edge', 'applicable': True, 'status': 'FAIL', 'finding': 'Synthetic edge defect for adapter regression.'}]
        }

    def check(self, record=None):
        path = self.root / 'review.json'
        path.write_text(json.dumps(record or self.record), encoding='utf-8')
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'validate-queue-review.py'
        result = subprocess.run([sys.executable, '-B', str(script), str(path), str(self.output)], capture_output=True, text=True, encoding='utf-8', check=True)
        return json.loads(result.stdout)

    def test_complete_fail_can_finish_queue_review_without_rewriting_status(self):
        self.assertTrue(self.check()['valid'])
        self.assertEqual(self.record['visual_check_status'], 'FAIL')

    def test_current_pass_remains_accepted(self):
        record = copy.deepcopy(self.record)
        record['visual_check_status'] = record['criteria'][0]['status'] = 'PASS'
        self.assertTrue(self.check(record)['valid'])

    def test_unchecked_criterion_is_not_finished_review(self):
        self.record['criteria'].append({'name': 'identity', 'applicable': True, 'status': 'NOT_CHECKED', 'finding': 'Pending inspection'})
        self.assertFalse(self.check()['valid'])

    def test_missing_local_view_is_rejected_even_for_fail(self):
        self.record['views'] = self.record['views'][:1]
        self.assertFalse(self.check()['valid'])

    def test_changed_output_rejects_stale_review(self):
        self.output.write_bytes(b'changed after inspection')
        self.assertFalse(self.check()['valid'])

    def test_fail_without_explicit_failed_finding_is_rejected(self):
        self.record['criteria'][0]['status'] = 'PASS'
        self.assertFalse(self.check()['valid'])

    def test_review_for_different_output_is_rejected(self):
        other = self.root / 'different.png'
        other.write_bytes(self.output.read_bytes())
        self.record['outputs'][0]['path'] = str(other)
        self.assertFalse(self.check()['valid'])


if __name__ == '__main__':
    unittest.main()
