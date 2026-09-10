"""Contract tests for the three-plus-cast back-composition evidence gate."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from validate_multicast_back_composition import validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MulticastBackCompositionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        artifact = root / "whitebox.png"
        artifact.write_bytes(b"synthetic image fixture")
        ui_contract = root / "ui-contract.json"
        ui_contract.write_text(json.dumps({
            "schema": "ndc-ui-safety/v1",
            "actors": [
                {"actorId": "active-a"},
                {"actorId": "support-b"},
                {"actorId": "support-c"},
            ],
        }), encoding="utf-8")
        ui_report = root / "ui-report.json"
        ui_report.write_text(json.dumps({
            "schema": "ndc-ui-safety-report/v1",
            "status": "pass",
            "contract": str(ui_contract.resolve()),
            "contractSha256": digest(ui_contract),
            "actors": [
                {"actorId": "active-a", "status": "pass"},
                {"actorId": "support-b", "status": "pass"},
                {"actorId": "support-c", "status": "pass"},
            ],
        }), encoding="utf-8")
        self.ui_contract = ui_contract
        self.ui_report = ui_report
        self.data = {
            "schema": "ndc-multicast-back-composition/v1",
            "scene_id": "SC0001",
            "snapshot_id": "beat-01",
            "stage": "whitebox",
            "artifact": {"path": str(artifact.resolve()), "sha256": digest(artifact)},
            "ui_report": {"path": str(ui_report.resolve()), "sha256": digest(ui_report)},
            "actors": [
                {"actor_id": "active-a", "active": True, "depth_band": "midground", "facing": "front"},
                {"actor_id": "support-b", "active": False, "depth_band": "foreground", "facing": "back", "visible_back_region_bbox": [10, 20, 100, 200]},
                {"actor_id": "support-c", "active": False, "depth_band": "background", "facing": "side"},
            ],
        }

    def test_valid_three_cast_passes(self):
        result = validate(self.data)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checks"]["candidate_actor_ids"], ["support-b"])
        self.assertTrue(result["checks"]["ui_actor_coverage"])

    def test_all_front_or_active_back_fails(self):
        self.data["actors"][1].update(active=True, facing="back")
        self.assertEqual(validate(self.data)["status"], "FAIL")
        self.data["actors"][1].update(active=False, facing="front")
        self.assertEqual(validate(self.data)["status"], "FAIL")

    def test_two_cast_is_not_applicable(self):
        self.data["actors"] = self.data["actors"][:2]
        result = validate(self.data)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["checks"]["applicable"])

    def test_exact_user_exception_passes(self):
        self.data["actors"][1]["facing"] = "front"
        self.data["exception"] = {
            "source_kind": "user_instruction", "scene_id": "SC0001", "snapshot_id": "beat-01",
            "instruction": "This exact scene intentionally uses a frontal ensemble.",
        }
        result = validate(self.data)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["checks"]["exception_used"])

    def test_failed_ui_or_stale_artifact_fails(self):
        ui_path = Path(self.data["ui_report"]["path"])
        ui_data = json.loads(ui_path.read_text(encoding="utf-8"))
        ui_data["status"] = "fail"
        ui_path.write_text(json.dumps(ui_data), encoding="utf-8")
        self.data["ui_report"]["sha256"] = digest(ui_path)
        self.assertEqual(validate(self.data)["status"], "FAIL")
        self.data["artifact"]["sha256"] = "0" * 64
        self.assertEqual(validate(self.data)["status"], "FAIL")

    def test_missing_snapshot_actor_in_ui_contract_and_report_fails(self):
        contract = json.loads(self.ui_contract.read_text(encoding="utf-8"))
        report = json.loads(self.ui_report.read_text(encoding="utf-8"))
        contract["actors"] = contract["actors"][:2]
        report["actors"] = report["actors"][:2]
        self.ui_contract.write_text(json.dumps(contract), encoding="utf-8")
        report["contractSha256"] = digest(self.ui_contract)
        self.ui_report.write_text(json.dumps(report), encoding="utf-8")
        self.data["ui_report"]["sha256"] = digest(self.ui_report)
        result = validate(self.data)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("missing snapshot actors: support-c" in error for error in result["errors"]))

    def test_unknown_or_duplicate_ui_actor_fails(self):
        contract = json.loads(self.ui_contract.read_text(encoding="utf-8"))
        report = json.loads(self.ui_report.read_text(encoding="utf-8"))
        contract["actors"].append({"actorId": "outsider"})
        report["actors"].append({"actorId": "support-c", "status": "pass"})
        self.ui_contract.write_text(json.dumps(contract), encoding="utf-8")
        report["contractSha256"] = digest(self.ui_contract)
        self.ui_report.write_text(json.dumps(report), encoding="utf-8")
        self.data["ui_report"]["sha256"] = digest(self.ui_report)
        result = validate(self.data)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("outside the snapshot: outsider" in error for error in result["errors"]))
        self.assertTrue(any("duplicate actor IDs" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
