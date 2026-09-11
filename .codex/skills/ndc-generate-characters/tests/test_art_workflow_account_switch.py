"""Journal contract for an inaccessible ChatGPT account record; no browser or art call is made."""
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "art_workflow_state.py"


class AccountSwitchJournalTests(unittest.TestCase):
    def test_inaccessible_account_record_stays_counted_and_allows_new_attempt(self):
        api = runpy.run_path(str(SCRIPT))
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            plan = {
                "schema": "ndc-art-production-plan/v1",
                "task_id": "account-switch-fixture",
                "jobs": [{
                    "job_id": "web-job",
                    "asset_key": "synthetic-web-asset",
                    "requirements": {"fixture": True},
                    "source_decision": {"mode": "generate", "evidence": "synthetic contract test"},
                    "limits": {"model": 3},
                    "required_criteria": ["synthetic-only"],
                    "output_roles": ["candidate"],
                }],
            }
            plan_path = root / "plan.json"
            journal = root / "journal.jsonl"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with patch.dict(os.environ, {"CODEX_THREAD_ID": "account-switch-fixture"}):
                api["initialize"](plan_path, journal)
                submission = {"tool": "chatgpt_web_browser", "operation": "generate_image", "arguments": {"conversation_url": "https://chatgpt.com/c/old"}}
                api["mutate"](journal, "web-job", "attempt", {"kind": "model", "submission_id": "old", "submission": submission})
                api["mutate"](journal, "web-job", "resolve", {"submission_id": "old", "result": "unknown", "evidence": "old account result unknown"})
                api["mutate"](journal, "web-job", "resolve", {"submission_id": "old", "result": "account_record_unavailable", "evidence": "account switch evidence with old URL and non-secret profile label"})
                replacement = {"tool": "chatgpt_web_browser", "operation": "generate_image", "arguments": {"conversation_url": "https://chatgpt.com/c/new"}}
                api["mutate"](journal, "web-job", "attempt", {"kind": "model", "submission_id": "new", "submission": replacement})
                header, events, _ = api["load"](journal)
                job = api["state"](header, events)["web-job"]
                used = api["used"](job, "model", "account-switch-fixture")

            self.assertEqual(job["attempts"]["old"]["result"], "account_record_unavailable")
            self.assertEqual(job["attempts"]["new"]["result"], "pending")
            self.assertEqual(used, 2)
            self.assertEqual(job["tool_failures"], 0)


if __name__ == "__main__":
    unittest.main()
