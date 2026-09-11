"""Synthetic contract/pixel fixtures only. No real art or user approval is produced."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import ui_fixtures as fixtures

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ui_adapter.py"
spec = importlib.util.spec_from_file_location("ui_adapter_under_test", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class UiAdapterTests(unittest.TestCase):
    def setUp(self):
        # Keep synthetic artifacts outside either relocated checkout; the production
        # cropper correctly rejects any output nested in a repository.
        self.temp = tempfile.TemporaryDirectory(prefix="ui-fixture-")
        self.root = Path(self.temp.name) / "case"
        self.fixture = fixtures.create_fixture(self.root)
        self.packet = self.fixture["packet"]

    def tearDown(self):
        self.temp.cleanup()

    def test_real_synthetic_crops_are_validation_only_and_do_not_accept_downstream(self):
        before = Path(self.fixture["journal"]).read_bytes()
        result = fixtures.complete_fixture(self.packet, self.root)
        gate = adapter.validate_result(self.packet, result, self.root)
        self.assertEqual(gate["status"], "VALIDATION_COMPLETE")
        self.assertFalse(gate["accepted"])
        self.assertEqual(gate["profiles_checked"], ["big", "small"])
        self.assertEqual(Path(self.fixture["journal"]).read_bytes(), before)
        _, jobs = adapter._load(self.fixture["journal"])
        self.assertIsNone(jobs["A-big"]["accepted"])

    def test_unrelated_progress_does_not_invalidate_unit(self):
        before = Path(self.fixture["journal"]).read_bytes()
        adapter.workflow.mutate(self.fixture["journal"], "A-unrelated", "revise", {"changes": {"requirements": {"identity_id": "A", "purpose": "unrelated", "synthetic": True, "progress": "independent"}}})
        self.assertNotEqual(Path(self.fixture["journal"]).read_bytes(), before)
        self.assertTrue(adapter.validate_release(self.packet, self.root)["valid"])

    def test_claimed_output_directory_contains_every_result_file(self):
        work = self.root / "assigned-worker-output"
        work.mkdir()
        self.packet["work_directory"] = str(work)
        result = fixtures.complete_fixture(self.packet, self.root)
        for item in result["files"]:
            self.assertTrue(Path(item["path"]).resolve().is_relative_to(work.resolve()))
        self.assertTrue(adapter.validate_result(self.packet, result, self.root)["valid"])

    def test_rejected_master_invalidates_publication_and_collection(self):
        result = fixtures.complete_fixture(self.packet, self.root)
        adapter.workflow.mutate(self.fixture["journal"], "A-U1", "reject", {"reason": "synthetic rejection fixture"})
        with self.assertRaises(ValueError):
            adapter.validate_release(self.packet, self.root)
        with self.assertRaises(ValueError):
            adapter.validate_result(self.packet, result, self.root)

    def test_waiting_manual_source_blocks_publication(self):
        adapter.workflow.mutate(self.fixture["journal"], "A-U0", "wait", {"reason": "WAITING_FOR_MANUAL_PORTRAIT_COMPLETION"})
        with self.assertRaises(ValueError):
            adapter.validate_release(self.packet, self.root)

    def test_master_must_be_exact_accepted_U1_output(self):
        impostor = self.root / "other-master.png"
        Image.new("RGB", (900, 1200), (1, 2, 3)).save(impostor)
        self.packet["files"][0] = adapter.workflow.snapshot(impostor, "ui_master")
        with self.assertRaisesRegex(ValueError, "accepted output"):
            adapter.validate_release(self.packet, self.root)

    def test_scope_cannot_omit_U0(self):
        self.packet["authority"]["upstream_jobs"].remove("A-U0")
        del self.packet["payload"]["acceptance_bindings"]["A-U0"]
        with self.assertRaisesRegex(ValueError, "include U0"):
            adapter.validate_release(self.packet, self.root)

    def test_wrong_producer_task_cannot_rebind_original_journal(self):
        self.packet["producer_task_id"] = "new-child-task"
        with self.assertRaisesRegex(ValueError, "different producer"):
            adapter.validate_release(self.packet, self.root)

    def test_full_journal_hash_is_not_a_release_file(self):
        self.packet["files"].append(adapter.workflow.snapshot(self.fixture["journal"], "journal"))
        with self.assertRaisesRegex(ValueError, "mutable journal"):
            adapter.validate_release(self.packet, self.root)

    def test_stale_accepted_context_fingerprint_is_rejected(self):
        self.packet["payload"]["acceptance_bindings"]["A-U1"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "acceptance changed"):
            adapter.validate_release(self.packet, self.root)

    def test_missing_small_preserves_historical_big_without_old_receipt(self):
        case = fixtures.create_fixture(Path(self.temp.name) / "missing", "B", missing_profiles=["small"])
        packet = case["packet"]
        kept = next(f for f in packet["files"] if f["role"] == "preserved_big")
        before = Path(kept["path"]).read_bytes()
        result = fixtures.complete_fixture(packet, case["base"])
        self.assertEqual(result["payload"]["profile_roles"], {"small": "ui_small"})
        self.assertEqual(Path(kept["path"]).read_bytes(), before)
        self.assertTrue(adapter.validate_result(packet, result, Path(case["base"]))["preserved_bytes_unchanged"])
        self.assertFalse((Path(case["base"]) / "historical-composition.json").exists())

    def test_pair_receipt_cannot_redraw_preserved_profile(self):
        case = fixtures.create_fixture(Path(self.temp.name) / "missing", "B", missing_profiles=["small"])
        packet = case["packet"]
        master = next(f for f in packet["files"] if f["role"] == "ui_master")
        out = Path(case["base"]) / "wrong-pair"
        receipt = adapter.ui.compose(master["path"], case["landmarks"], packet["payload"]["stem"], out)
        result = {"status": "VALIDATION_COMPLETE", "files": [adapter.workflow.snapshot(out / "composition.json", "receipt"), adapter.workflow.snapshot(case["landmarks"], "landmarks"), adapter.workflow.snapshot(out / receipt["profiles"]["small"]["path"], "small")], "payload": {"validation_only": True, "receipts": ["receipt"], "profile_roles": {"small": "small"}}}
        with self.assertRaisesRegex(ValueError, "preserved profile"):
            adapter.validate_result(packet, result, Path(case["base"]))

    def test_altered_crop_fails_existing_technical_audit(self):
        result = fixtures.complete_fixture(self.packet, self.root)
        target = next(f for f in result["files"] if f["role"] == "ui_big")
        with Image.open(target["path"]) as image:
            image.putpixel((0, 0), (255, 0, 0))
            image.save(target["path"])
        target["sha256"] = adapter.workflow.file_hash(target["path"])
        with self.assertRaises(ValueError):
            adapter.validate_result(self.packet, result, self.root)

    def test_result_must_declare_actual_landmark_file(self):
        result = fixtures.complete_fixture(self.packet, self.root)
        result["files"] = [f for f in result["files"] if f["role"] != "landmarks"]
        with self.assertRaisesRegex(ValueError, "landmarks must be"):
            adapter.validate_result(self.packet, result, self.root)

    def test_synthetic_packet_cannot_be_promoted_to_production(self):
        self.packet["execution_mode"] = "production"
        with self.assertRaisesRegex(ValueError, "synthetic fixture"):
            adapter.validate_release(self.packet, self.root)

    def test_validation_result_cannot_claim_production_PASS(self):
        result = fixtures.complete_fixture(self.packet, self.root)
        result["status"] = "PASS"
        with self.assertRaisesRegex(ValueError, "validation cannot"):
            adapter.validate_result(self.packet, result, self.root)

    def test_actual_failed_or_manual_return_does_not_require_fake_PASS(self):
        for status in ("FAIL", "WAITING_MANUAL"):
            result = {"status": status, "files": [], "payload": {"reason": "Synthetic test found a source scope issue", "return_stage": "U0"}}
            gate = adapter.validate_result(self.packet, result, self.root)
            self.assertFalse(gate["accepted"])
            self.assertEqual(gate["status"], status)

    def test_production_result_branch_requires_original_current_downstream_acceptance(self):
        # Isolate the production return branch; synthetic packet is NOT released to production.
        result = fixtures.complete_fixture(self.packet, self.root)
        release_tuple = adapter._release(self.packet, self.root)
        packet = copy.deepcopy(self.packet)
        packet["execution_mode"] = "production"
        result["status"] = "PASS"
        with patch.object(adapter, "_release", return_value=release_tuple):
            with self.assertRaisesRegex(ValueError, "accepted current"):
                adapter.validate_result(packet, result, self.root)
        for profile, key in packet["payload"]["profile_jobs"].items():
            target = next(f for f in result["files"] if f["role"] == "ui_" + profile)
            fixtures._fixture_accept(self.fixture["journal"], key, [target], self.root, Path(self.fixture["fixture_validator"]))
        _, jobs = adapter._load(self.fixture["journal"])
        with patch.object(adapter, "_release", return_value=(release_tuple[0], jobs, release_tuple[2])):
            self.assertEqual(adapter.validate_result(packet, result, self.root)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
