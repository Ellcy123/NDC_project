import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "batch_update.py"
SPEC = importlib.util.spec_from_file_location("batch_update", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BatchUpdateTests(unittest.TestCase):
    def make_batch(self, root: Path) -> Path:
        path = root / "batch.json"
        path.write_text(json.dumps({
            "schema": "ndc-prop-batch/v1", "next_action": "old",
            "artifacts": {"a": {"status": "PENDING", "rejected": False}},
        }), encoding="utf-8")
        return path

    def test_artifact_transition_binds_files_and_journals(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            batch = self.make_batch(root)
            output, review = root / "asset.png", root / "review.json"
            output.write_bytes(b"png")
            review.write_text("{}", encoding="utf-8")
            result = MODULE.update_artifact(Namespace(
                batch=batch, artifact_id="a", expect_status="PENDING", status="PASS",
                rejected=False, output=output, review=review, published_path=None,
                frozen=True, expect_batch_sha256=MODULE.sha256(batch), reason="review passed"))
            data = MODULE.read_json(batch)
            self.assertEqual(data["artifacts"]["a"]["sha256"], MODULE.sha256(output))
            self.assertEqual(data["state_events"][0]["sequence"], 1)
            self.assertEqual(result["status"], "PASS")

    def test_next_action_is_capped_and_compare_and_swap_blocks_stale_writer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            batch = self.make_batch(root)
            old_hash = MODULE.sha256(batch)
            result = MODULE.update_next_action(Namespace(
                batch=batch, action=["audit candidates", "finish local gate"],
                expect_batch_sha256=old_hash, reason="compact active queue"))
            self.assertIn("audit candidates", result["next_action"])
            with self.assertRaisesRegex(ValueError, "batch bytes changed"):
                MODULE.update_next_action(Namespace(
                    batch=batch, action=["another"], expect_batch_sha256=old_hash, reason="stale"))
            with self.assertRaisesRegex(ValueError, "one to three"):
                MODULE.update_next_action(Namespace(
                    batch=batch, action=["1", "2", "3", "4"], expect_batch_sha256=None, reason="too many"))

    def test_state_event_hash_changes_if_event_is_tampered(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            batch = self.make_batch(root)
            MODULE.update_next_action(Namespace(
                batch=batch, action=["audit"], expect_batch_sha256=None, reason="test event"))
            data = MODULE.read_json(batch)
            event = data["state_events"][0]
            original = event["event_sha256"]
            event["reason"] = "tampered"
            recalculated = MODULE.json_digest({key: value for key, value in event.items()
                                               if key != "event_sha256"})
            self.assertNotEqual(original, recalculated)


if __name__ == "__main__":
    unittest.main()
