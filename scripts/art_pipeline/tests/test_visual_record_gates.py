"""Contract checks with disposable synthetic images, never production approvals."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from validate_stage_visual_self_check import GateError, TYPE7_CRITERIA, sha256, validate_record
from validate_texture_gate import TEXTURE_CRITERIA, validate_record as validate_texture
from validate_final_visual_record_presence import validate_directory


class VisualRecordGates(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ndc-visual-contract-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.records = self.root / "reviews"
        self.formal = self.root / "formal"
        self.records.mkdir()
        self.formal.mkdir()
        self.output = self.root / "output.png"
        self.anchor = self.root / "anchor.png"
        self.local = self.root / "local.png"
        Image.new("RGB", (8, 8), "red").save(self.output)
        Image.new("RGB", (8, 8), "blue").save(self.anchor)
        Image.new("RGB", (16, 16), "red").save(self.local)
        self.record = self.records / "visual_review.json"
        self.data = {
            "schema": "ndc-stage-visual-self-check/v1", "stage_id": "synthetic_contract_test",
            "reviewer": "automated-test-fixture-only", "reviewed_at": "2026-09-05T12:00:00+08:00",
            "inputs": [self.ref(self.anchor)], "output": self.ref(self.output),
            "visual_check_status": "PASS", "required_criteria": ["visual_self_check"],
            "criteria": {"visual_self_check": self.finding()},
            "views": {
                "whole_100": {**self.ref(self.output), **self.finding(), "scale_percent": 100,
                              "source": self.ref(self.output)},
                "local_200_or_tiles": {**self.finding(), "source": self.ref(self.output),
                    "mode": "nearest_neighbor_200", "resampling": "nearest", "scale_percent": 200,
                    "images": [{**self.ref(self.local), **self.finding(), "bbox": [0, 0, 8, 8]}]},
            },
        }
        self.write()

    @staticmethod
    def finding():
        return {"status": "PASS", "finding": "Synthetic contract fixture; not an artistic approval."}

    @staticmethod
    def ref(path):
        return {"path": str(path), "sha256": sha256(path)}

    def write(self, data=None, path=None):
        (path or self.record).write_text(json.dumps(data or self.data), encoding="utf-8")

    def test_valid_record_and_byte_identical_final_copy(self):
        self.assertEqual(validate_record(self.record, self.output)["sha256"], sha256(self.output))
        (self.formal / "released.png").write_bytes(self.output.read_bytes())
        self.assertEqual(validate_directory(self.formal, self.records)["status"], "PASS")

    def test_artifact_or_source_hash_change_fails(self):
        Image.new("RGB", (8, 8), "green").save(self.output)
        with self.assertRaisesRegex(GateError, "stale"):
            validate_record(self.record, self.output)

    def test_input_or_review_image_hash_change_fails(self):
        for path in (self.anchor, self.local):
            original = path.read_bytes()
            with self.subTest(path=path.name):
                Image.new("RGB", (8, 8), "green").save(path)
                with self.assertRaisesRegex(GateError, "stale"):
                    validate_record(self.record, self.output)
            path.write_bytes(original)

    def test_unknown_schema_and_ambiguous_batch_are_rejected(self):
        data = copy.deepcopy(self.data)
        data["schema"] = "ndc-stage-visual-review-report/v1"
        self.write(data)
        with self.assertRaisesRegex(GateError, "Unsupported schema"):
            validate_record(self.record, self.output)
        data = copy.deepcopy(self.data)
        data["outputs"] = [data.pop("output"), self.ref(self.anchor)]
        self.write(data)
        with self.assertRaises(GateError):
            validate_record(self.record, self.output)

    def test_missing_view_required_criterion_or_not_checked_fails(self):
        for mutation in ("view", "criterion", "not_checked", "overall", "required_list", "finding"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                if mutation == "view":
                    del data["views"]["whole_100"]
                elif mutation == "criterion":
                    del data["criteria"]["visual_self_check"]
                elif mutation == "not_checked":
                    data["criteria"]["visual_self_check"]["status"] = "NOT_CHECKED"
                elif mutation == "overall":
                    data["visual_check_status"] = "FAIL"
                elif mutation == "finding":
                    data["criteria"]["visual_self_check"]["finding"] = ""
                else:
                    del data["required_criteria"]
                self.write(data)
                with self.assertRaises(GateError):
                    validate_record(self.record, self.output)

    def test_every_formal_png_needs_its_own_current_hash(self):
        (self.formal / "first.png").write_bytes(self.output.read_bytes())
        (self.formal / "unreviewed.png").write_bytes(self.anchor.read_bytes())
        report = validate_directory(self.formal, self.records)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(sum(row["status"] == "BLOCKED" for row in report["artifacts"]), 1)

    def test_conflicting_current_hash_failure_blocks_terminal(self):
        (self.formal / "first.png").write_bytes(self.output.read_bytes())
        failed = copy.deepcopy(self.data)
        failed["visual_check_status"] = "FAIL"
        self.write(failed, self.records / "failed_review.json")
        self.assertEqual(validate_directory(self.formal, self.records)["status"], "BLOCKED")

    def test_type7_requires_context_anchor_and_containment(self):
        data = copy.deepcopy(self.data)
        data["stage_id"] = "container_type7_borderless"
        data["required_criteria"] = sorted(TYPE7_CRITERIA)
        data["criteria"] = {name: self.finding() for name in TYPE7_CRITERIA}
        data["type7_visual_context"] = {
            "real_container_identity": "synthetic low drawer", "environment_derivation": "Synthetic source relation",
            "height_class": "low", "observation_direction": "downward", "first_person_viewpoint_rationale": "Synthetic standing viewpoint",
            "method": "direct_image_generation", "child_fully_contained": True,
        }
        data["original_scene_visual_anchor"] = self.ref(self.anchor)
        data["source_anchor_side_by_side"] = self.ref(self.local)
        self.write(data)
        validate_record(self.record, self.output)
        for mutation in ("containment", "anchor", "method", "direction"):
            broken = copy.deepcopy(data)
            if mutation == "anchor":
                del broken["original_scene_visual_anchor"]
            else:
                field, value = {"containment": ("child_fully_contained", False), "method": ("method", "paste_big"),
                                "direction": ("observation_direction", "upward")}[mutation]
                broken["type7_visual_context"][field] = value
            self.write(broken)
            with self.assertRaises(GateError):
                validate_record(self.record, self.output)

    def texture_record(self):
        views = copy.deepcopy(self.data["views"])
        views["local_200_or_tiles"] = {
            **self.finding(), "source": self.ref(self.output), "mode": "complete_original_pixel_tiles",
            "coverage_mode": "full_image_tiles", "source_size": [8, 8], "local_tile_coverage_complete": True,
            "tiles": [{**self.ref(self.output), **self.finding(), "bbox": [0, 0, 8, 8]}],
        }
        return {"schema": "ndc-texture-coherence/v1", "reviewer": self.data["reviewer"], "reviewed_at": self.data["reviewed_at"],
                "artifact": self.ref(self.output), "formal_status": "FORMAL_PASS", "whole_image_checked": True,
                "local_tile_coverage_complete": True, "views": views,
                "STYLE_LOCK_GATE": {**self.finding(), "references": [self.ref(self.anchor)], "frozen_invariants": ["Synthetic blue source"]},
                "TEXTURE_COHERENCE_GATE": {**self.finding(), "required_criteria": sorted(TEXTURE_CRITERIA),
                                           "criteria": {name: self.finding() for name in TEXTURE_CRITERIA}}}

    def test_texture_complete_coverage_and_fail_closed_checks(self):
        data = self.texture_record()
        self.write(data)
        validate_texture(self.record)
        for mutation in ("gap", "check", "not_checked", "style", "coverage"):
            broken = copy.deepcopy(data)
            if mutation == "gap":
                broken["views"]["local_200_or_tiles"]["tiles"][0]["bbox"] = [0, 0, 7, 8]
            elif mutation == "check":
                del broken["TEXTURE_COHERENCE_GATE"]["criteria"]["quiet_plane_control"]
            elif mutation == "not_checked":
                broken["TEXTURE_COHERENCE_GATE"]["criteria"]["quiet_plane_control"]["status"] = "NOT_CHECKED"
            elif mutation == "style":
                broken["STYLE_LOCK_GATE"]["status"] = "FAIL"
            else:
                broken["local_tile_coverage_complete"] = False
            self.write(broken)
            with self.assertRaises(GateError):
                validate_texture(self.record)

    def test_cli_codes_and_no_implicit_report_write(self):
        command = [sys.executable, "-B", str(SCRIPTS / "validate_stage_visual_self_check.py"),
                   "--record", str(self.record), "--artifact", str(self.output)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.data["visual_check_status"] = "NOT_CHECKED"
        self.write()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_texture_and_terminal_cli_interfaces(self):
        texture_path = self.records / "texture_review.json"
        self.write(self.texture_record(), texture_path)
        texture_command = [sys.executable, "-B", str(SCRIPTS / "validate_texture_gate.py"), "--record", str(texture_path)]
        self.assertEqual(subprocess.run(texture_command, capture_output=True).returncode, 0)
        (self.formal / "released.png").write_bytes(self.output.read_bytes())
        terminal_command = [sys.executable, "-B", str(SCRIPTS / "validate_final_visual_record_presence.py"),
                            "--formal-dir", str(self.formal), "--record-root", str(self.records)]
        self.assertEqual(subprocess.run(terminal_command, capture_output=True).returncode, 0)
        self.assertEqual(len(list(self.formal.iterdir())), 1)
        report_path = self.root / "terminal_report.json"
        self.assertEqual(subprocess.run(terminal_command + ["--report", str(report_path)], capture_output=True).returncode, 0)
        self.assertEqual(json.loads(report_path.read_text())["status"], "PASS")
        self.assertNotEqual(subprocess.run(terminal_command + ["--report", str(self.formal / "report.json")], capture_output=True).returncode, 0)
        self.assertFalse((self.formal / "report.json").exists())


if __name__ == "__main__":
    unittest.main()
