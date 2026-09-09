"""Conversation quotas: provenance survives while other conversations do not spend it."""
import copy
import os
from unittest import TestCase
from unittest.mock import patch
import workflow_state as w
import test_workflow_state as fixtures

class TaskBudgets(TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'CODEX_THREAD_ID': 'conversation-A'})
        self.env.start(); self.addCleanup(self.env.stop)
        self.f = fixtures.WorkflowTests(); self.f.setUp(); self.addCleanup(self.f.tearDown)
        self.path, self.job = self.f.path, self.f.job
        self.prompt = self.f.root/'task-prompt.txt'

    def call(self, number):
        self.prompt.write_text('actual revised content '+str(number))
        return w.reserve_attempt(self.path, self.job, self.prompt, 'synthetic test')

    def test_new_conversation_fresh_same_conversation_still_exhausted(self):
        for n in range(1,7): self.assertEqual(self.call(n),n)
        old = (self.f.root/'attempts.jsonl').read_bytes()
        with patch.dict(os.environ, {'CODEX_THREAD_ID':'conversation-B'}):
            self.assertEqual(self.call(7),1)
            self.assertEqual(self.call(8),2)
        self.assertTrue((self.f.root/'attempts.jsonl').read_bytes().startswith(old))
        with self.assertRaisesRegex(ValueError,'exhausted'): self.call(9)
        self.assertEqual(w.validate(self.path,2),[])

    def test_unknown_asset_history_does_not_exhaust_new_task(self):
        b = copy.deepcopy(self.f.b); b.pop('attempt_head')
        b['attempt_log']='unknown-assets.jsonl'
        b['jobs'][self.job].update(legacy_attempts=6,legacy_evidence={
            'status':'UNKNOWN_CONSERVATIVE_EXHAUSTION','actual_count':None})
        self.path=self.f.root/'unknown-assets.json'; w.write_json(self.path,b); w.initialize(self.path)
        self.assertEqual(self.call(1),1)
        self.assertEqual(w.load_batch(self.path)['jobs'][self.job]['legacy_attempts'],6)

    def test_known_other_task_history_is_not_current_spend(self):
        b = copy.deepcopy(self.f.b); b.pop('attempt_head'); b['attempt_log']='old-assets.jsonl'
        b['jobs'][self.job].update(legacy_attempts=12,legacy_evidence='old real provenance',legacy_task_id='old-task')
        self.path=self.f.root/'old-assets.json'; w.write_json(self.path,b); w.initialize(self.path)
        self.assertEqual(self.call(1),1)
        self.assertEqual(w.log_events(self.path,w.load_batch(self.path))[-1]['number'],13)

    def test_attempt_cannot_supply_another_task_id(self):
        self.prompt.write_text('test')
        with self.assertRaisesRegex(ValueError,'executing conversation'):
            w.reserve_attempt(self.path,self.job,self.prompt,'test',task_id='forged-B')

    def test_legacy_attribution_preserves_same_task_calls(self):
        b=copy.deepcopy(self.f.b); b.pop('attempt_head'); b['attempt_log']='legacy-unattributed.jsonl'
        self.path=self.f.root/'legacy-unattributed.json'; w.write_json(self.path,b)
        with patch.dict(os.environ, {'CODEX_THREAD_ID':''}): w.initialize(self.path)
        self.prompt.write_text('old exact prompt')
        w.append(self.path,w.load_batch(self.path),dict(type='attempt',job_id=self.job,number=1,
                 prompt_path=str(self.prompt),prompt_sha256=w.sha(self.prompt),reason='old synthetic call'))
        before=(self.f.root/'legacy-unattributed.jsonl').read_bytes()
        w.attribute_legacy_task(self.path,'conversation-A','synthetic original task record')
        self.assertTrue((self.f.root/'legacy-unattributed.jsonl').read_bytes().startswith(before))
        # Keep immutable old prompt intact; reserve against a new file.
        self.prompt=self.f.root/'next-prompt.txt'
        self.assertEqual(self.call(2),2)
        w.attribute_legacy_task(self.path,'conversation-A','same provenance')
        with self.assertRaisesRegex(ValueError,'immutable'):
            w.attribute_legacy_task(self.path,'conversation-B','wrong attribution')
