import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scope_status.py"
SPEC = importlib.util.spec_from_file_location("scope_status", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ScopeStatusTests(unittest.TestCase):
    def test_active_scope_never_readds_excluded_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            revision = {
                "execution_required_artifacts": ["a", "b"],
                "reporting_asset_artifacts": ["a"],
                "excluded_artifacts": ["c"],
            }
            revision_path = root / "scope.json"
            revision_path.write_text(json.dumps(revision), encoding="utf-8")
            batch = {
                "batch_id": "x",
                "scope": {"required_artifacts": ["a", "b", "c"]},
                "artifacts": {
                    "a": {"status": "PASS", "rejected": False},
                    "b": {"status": "CANDIDATE", "rejected": False},
                    "c": {"status": "PENDING", "rejected": False},
                },
                "active_delivery_scope_revision": {
                    "path": str(revision_path),
                    "sha256": MODULE.sha256(revision_path),
                },
                "next_action": "review b",
            }
            batch_path = root / "batch.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            result = MODULE.summarize(batch_path)
            self.assertEqual(result["execution"]["required"], 2)
            self.assertEqual(result["reporting"]["required"], 1)
            self.assertEqual(result["excluded"], 1)


if __name__ == "__main__":
    unittest.main()
