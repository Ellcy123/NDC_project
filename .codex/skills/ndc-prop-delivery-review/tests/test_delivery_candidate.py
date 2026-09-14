import importlib.util
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "delivery_candidate.py"
SPEC = importlib.util.spec_from_file_location("delivery_candidate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DeliveryCandidateTests(unittest.TestCase):
    def test_register_marks_candidate_and_selected_reference(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate.png"
            reference = root / "reference.png"
            candidate.write_bytes(b"candidate")
            reference.write_bytes(b"reference")
            args = Namespace(
                delivery_root=root / "delivery",
                category="道具",
                unit="Unit4",
                scene="SC4002",
                artifact="4112.big",
                revision="r001",
                candidate=candidate,
                reference=[reference],
                scope_revision_sha256="a" * 64,
                reason="selected for delivery",
                selected_by="test",
            )
            result = MODULE.register(args)
            manifest = Path(result["manifest"])
            self.assertEqual(MODULE.audit_manifest(manifest), [])
            data = MODULE.read_json(manifest)
            self.assertIn("__DELIVERY_CANDIDATE", data["candidate"]["path"])
            self.assertIn("__SELECTED_REFERENCE", data["selected_references"][0]["path"])
            self.assertIn("交付候选", manifest.parts)

    def test_failed_candidate_is_retained_after_status_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate.png"
            review = root / "review.json"
            candidate.write_bytes(b"candidate")
            review.write_text("{}", encoding="utf-8")
            registered = MODULE.register(Namespace(
                delivery_root=root / "delivery", category="道具", unit="Unit4", scene="SC4002",
                artifact="4112.big", revision="r001", candidate=candidate, reference=[],
                scope_revision_sha256="a" * 64, reason="selected", selected_by="test"))
            manifest = Path(registered["manifest"])
            result = MODULE.status_update(Namespace(
                manifest=manifest, expect_status="DELIVERY_CANDIDATE_SELECTED",
                status="REVIEW_FAILED_PENDING_MOVE", reason="visual review failed",
                review=review, formal_file=None))
            self.assertEqual(result["status"], "REVIEW_FAILED_PENDING_MOVE")
            self.assertTrue(manifest.is_file())
            self.assertTrue((manifest.parent / MODULE.read_json(manifest)["candidate"]["path"]).is_file())

    def test_only_failed_candidate_can_be_moved_and_bytes_are_retained(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate, review = root / "candidate.png", root / "review.json"
            candidate.write_bytes(b"candidate")
            review.write_text("{}", encoding="utf-8")
            registered = MODULE.register(Namespace(
                delivery_root=root / "delivery", category="道具", unit="Unit4", scene="SC4002",
                artifact="4112.big", revision="r001", candidate=candidate, reference=[],
                scope_revision_sha256="a" * 64, reason="selected", selected_by="test"))
            manifest = Path(registered["manifest"])
            with self.assertRaisesRegex(ValueError, "only a reviewed failed"):
                MODULE.move_failed(Namespace(manifest=manifest, destination_root=root / "work", reason="too early"))
            MODULE.status_update(Namespace(
                manifest=manifest, expect_status="DELIVERY_CANDIDATE_SELECTED",
                status="REVIEW_FAILED_PENDING_MOVE", reason="failed", review=review, formal_file=None))
            result = MODULE.move_failed(Namespace(
                manifest=manifest, destination_root=root / "work", reason="replace after failed review"))
            moved = Path(result["moved_manifest"])
            self.assertTrue(moved.is_file())
            self.assertFalse(manifest.exists())
            self.assertEqual(MODULE.audit_manifest(moved), [])


if __name__ == "__main__":
    unittest.main()
