"""Regression cases for stale reviews and shared, hash-bound inspection scopes."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import production_gate as production
import visual_review_gate as visual


class VisualEvidenceBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.frame = self.root / "frame.png"
        self.source = self.root / "source.png"
        frame = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
        frame.paste((100, 80, 50, 255), (10, 5, 30, 25))
        frame.save(self.frame)
        self.tile = self.root / "local-200.png"
        frame.crop((10, 5, 30, 25)).resize((40, 40), Image.Resampling.NEAREST).save(self.tile)
        Image.new("RGB", (40, 30), (40, 50, 60)).save(self.source)

    def write(self, name, data):
        path = self.root / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def ref(self, path):
        return {"path": str(path), "sha256": visual.sha256(path)}

    def contract(self, stage="matte-extraction", decision="pass"):
        return {
            "schema": "ndc-stage-visual-review/v1", "stage": stage,
            "reviewAuthority": "codex-self-check",
            "artifacts": [
                {"role": "actual-output", **self.ref(self.frame), "poseIds": ["a-v1", "b-v1"], "snapshotIds": ["s0", "s1"]},
                {"role": "source-scene", **self.ref(self.source)},
            ],
            "checks": {key: decision for key in visual.STAGE_CHECKS[stage]},
            "localTiles": [{"id": "body-contact", "bbox": [10, 5, 30, 25], **self.ref(self.tile)}],
            "observations": ["Explicit inspection fixture, not an inferred artistic verdict."],
            "decision": decision,
        }

    def build(self, contract=None):
        contract = contract or self.contract()
        contract_path = self.write("contract.json", contract)
        report = visual.build_review(contract_path, self.root / "review")
        path = self.root / "review" / f"{contract['stage']}-visual-review-report.json"
        return contract_path, report, path

    def test_changed_image_cannot_rebind_old_pass_contract(self):
        contract = self.contract()
        self.build(contract)
        Image.new("RGBA", (40, 30), (255, 0, 0, 255)).save(self.frame)
        with self.assertRaisesRegex(ValueError, "reviewed SHA-256 is stale"):
            self.build(contract)

    def test_reviewed_sha_is_required(self):
        contract = self.contract()
        del contract["artifacts"][0]["sha256"]
        with self.assertRaisesRegex(ValueError, "actually reviewed"):
            self.build(contract)

    def test_navigation_board_without_actual_local_view_cannot_pass(self):
        contract = self.contract()
        del contract["localTiles"]
        with self.assertRaisesRegex(ValueError, "requires actual localTiles"):
            self.build(contract)

    def test_local_view_must_be_200_percent_and_hash_bound(self):
        contract = self.contract()
        Image.new("RGB", (20, 20), (100, 80, 50)).save(self.tile)
        with self.assertRaisesRegex(ValueError, "reviewed SHA-256 is stale"):
            self.build(contract)
        contract["localTiles"][0].update(self.ref(self.tile))
        with self.assertRaisesRegex(ValueError, "at least 200 percent"):
            self.build(contract)

    def test_unchanged_report_cannot_hide_changed_local_view(self):
        _, _, report_path = self.build()
        ref = self.ref(report_path)
        Image.new("RGB", (40, 40), (250, 50, 60)).save(self.tile)
        with self.assertRaisesRegex(ValueError, "reviewed SHA-256 is stale"):
            production.validate_visual_report(ref, "review", self.root / "ledger.json")

    def test_same_bytes_allow_repeat_validation_and_report_reuse(self):
        contract_path, first, report_path = self.build()
        second = visual.build_review(contract_path, self.root / "review")
        self.assertEqual(first["artifacts"], second["artifacts"])
        ref = self.ref(report_path)
        for _ in range(2):
            actual = production.validate_visual_report(ref, "review", self.root / "ledger.json")
            self.assertEqual(actual["status"], "VISUAL_REVIEW_PASS")

    def test_reuse_provenance_preserves_original_time_and_is_hash_bound(self):
        record_path = self.write("actual-self-check.json", {"schema": "ndc-stage-visual-self-check/v1", "stage_id": "actual-joint-review"})
        contract = self.contract()
        contract.update({"inspectionId": "one-real-inspection", "reviewedAt": "2026-09-08T10:00:00+08:00", "sourceReviewRecord": self.ref(record_path)})
        _, report, report_path = self.build(contract)
        self.assertEqual(report["reviewedAt"], contract["reviewedAt"])
        self.assertEqual(report["inspectionId"], contract["inspectionId"])
        ref = self.ref(report_path)
        self.write("actual-self-check.json", {"changed": True})
        with self.assertRaisesRegex(ValueError, "sourceReviewRecord SHA-256 is stale"):
            production.validate_visual_report(ref, "review", self.root / "ledger.json")

    def test_unchanged_report_cannot_hide_changed_source_image(self):
        _, _, report_path = self.build()
        ref = self.ref(report_path)
        Image.new("RGB", (40, 30), (250, 50, 60)).save(self.source)
        with self.assertRaisesRegex(ValueError, "hash does not match"):
            production.validate_visual_report(ref, "review", self.root / "ledger.json")

    def test_unchanged_report_cannot_hide_changed_board(self):
        _, report, report_path = self.build()
        ref = self.ref(report_path)
        Image.new("RGB", (2, 2), (255, 0, 0)).save(report["board"])
        with self.assertRaisesRegex(ValueError, "hash does not match"):
            production.validate_visual_report(ref, "review", self.root / "ledger.json")

    def coverage_fixture(self):
        placements = [
            {"characterName": name, "target": {"poseDefinition": {"poseId": pose}}}
            for name, pose in (("A", "a-v1"), ("B", "b-v1"))
        ]
        stagings = [{
            "timelineSnapshotId": snapshot,
            "characters": [{"name": "A"}, {"name": "B"}],
            "combinedWhiteboxReview": {"poseIds": {"A": "a-v1", "B": "b-v1"}},
        } for snapshot in ("s0", "s1")]
        reports = [self.build(self.contract(stage))[1] for stage in production.REQUIRED_VISUAL_STAGES["post-generation"]]
        return placements, stagings, reports

    def test_joint_review_covers_multiple_actors_and_snapshots(self):
        placements, stagings, reports = self.coverage_fixture()
        production.validate_visual_coverage(reports, "post-generation", placements, stagings, "case")

    def test_new_path_new_whitebox_bytes_reject_old_pass_with_unchanged_pose_ids(self):
        placements, stagings, reports = self.coverage_fixture()
        production.validate_visual_coverage(reports, "post-generation", placements, stagings, "case")
        revised = self.root / "revised-whitebox-same-pose.png"
        with Image.open(self.frame) as image:
            image.putpixel((20, 15), (255, 10, 20, 255))
            image.save(revised)
        with self.assertRaisesRegex(ValueError, "current artifact lacks exact-pose-whitebox review coverage"):
            production.require_reviewed_artifacts(reports, "exact-pose-whitebox", [self.ref(revised)], self.root / "ledger.json", "whitebox")

    def test_byte_identical_whitebox_new_path_reuses_existing_review(self):
        _, _, reports = self.coverage_fixture()
        copied = self.root / "same-reviewed-whitebox-copy.png"
        copied.write_bytes(self.frame.read_bytes())
        production.require_reviewed_artifacts(reports, "exact-pose-whitebox", [self.ref(copied)], self.root / "ledger.json", "whitebox")

    def test_current_final_composite_must_match_reviewed_bytes(self):
        _, _, reports = self.coverage_fixture()
        revised = self.root / "new-final.png"
        Image.new("RGB", (40, 30), (220, 40, 30)).save(revised)
        with self.assertRaisesRegex(ValueError, "current artifact lacks final-full-composite review coverage"):
            production.require_reviewed_artifacts(reports, "final-full-composite", [self.ref(revised)], self.root / "final-contract.json", "finalComposite")

    def test_byte_identical_final_copy_reuses_existing_review(self):
        _, _, reports = self.coverage_fixture()
        copied = self.root / "final-copy.png"
        copied.write_bytes(self.frame.read_bytes())
        production.require_reviewed_artifacts(reports, "final-full-composite", [self.ref(copied)], self.root / "final-contract.json", "finalComposite")

    def test_one_actor_five_stages_cannot_replace_whole_cast(self):
        placements, stagings, reports = self.coverage_fixture()
        for report in reports:
            report["artifacts"][0]["poseIds"] = ["a-v1"]
        with self.assertRaisesRegex(ValueError, "lacks reviewed pose coverage"):
            production.validate_visual_coverage(reports, "post-generation", placements, stagings, "case")

    def test_missing_snapshot_fails_even_when_all_actors_are_named(self):
        placements, stagings, reports = self.coverage_fixture()
        for report in reports:
            if report["stage"] == "final-full-composite":
                report["artifacts"][0]["snapshotIds"] = ["s0"]
        with self.assertRaisesRegex(ValueError, "lacks reviewed snapshot/pose coverage"):
            production.validate_visual_coverage(reports, "post-generation", placements, stagings, "case")

    def test_fail_cli_retains_report_and_exits_nonzero(self):
        contract = self.write("failed-contract.json", self.contract(decision="fail"))
        result = subprocess.run([sys.executable, "-B", visual.__file__, str(contract), str(self.root / "failed")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        report = json.loads((self.root / "failed/matte-extraction-visual-review-report.json").read_text())
        self.assertEqual(report["status"], "VISUAL_REVIEW_FAIL")

    def test_existing_matte_readiness_is_readonly_and_bound_to_visual_review(self):
        _, _, review_path = self.build()
        extract_path = self.write("extraction.json", {"schema": "ndc-chroma-green-matte/v1", "input": str(self.source), "output": str(self.frame)})
        audit = {
            "schema": "ndc-matte-readiness-audit/v1", "source": self.ref(self.source),
            "output": self.ref(self.frame), "extractionReport": self.ref(extract_path),
            "expectedCanvas": [40, 30], "visualReviewReport": self.ref(review_path),
        }
        audit_path = self.write("audit.json", audit)
        before = self.frame.read_bytes()
        production.validate_matte_readiness(self.ref(audit_path), "matte", self.root / "ledger.json")
        self.assertEqual(before, self.frame.read_bytes())
        audit["output"] = self.ref(self.source)
        audit_path = self.write("audit.json", audit)
        with self.assertRaisesRegex(ValueError, "must be RGBA"):
            production.validate_matte_readiness(self.ref(audit_path), "matte", self.root / "ledger.json")

    def test_matte_readiness_rejects_unreviewed_rgba(self):
        _, _, review_path = self.build()
        other = self.root / "other.png"
        image = Image.open(self.frame)
        image.putpixel((20, 15), (220, 10, 50, 255))
        image.save(other)
        extract_path = self.write("extraction.json", {"input": str(self.source), "output": str(other)})
        audit_path = self.write("audit.json", {
            "schema": "ndc-matte-readiness-audit/v1", "source": self.ref(self.source),
            "output": self.ref(other), "extractionReport": self.ref(extract_path),
            "expectedCanvas": [40, 30], "visualReviewReport": self.ref(review_path),
        })
        with self.assertRaisesRegex(ValueError, "requires the actual RGBA output"):
            production.validate_matte_readiness(self.ref(audit_path), "matte", self.root / "ledger.json")

    def test_internal_alpha_hole_does_not_prove_transparent_exterior(self):
        _, _, review_path = self.build()
        image = Image.new("RGBA", (40, 30), (100, 80, 50, 255))
        image.putpixel((20, 15), (0, 0, 0, 0))
        image.save(self.frame)
        extract_path = self.write("extraction.json", {"input": str(self.source), "output": str(self.frame)})
        audit_path = self.write("audit.json", {
            "schema": "ndc-matte-readiness-audit/v1", "source": self.ref(self.source),
            "output": self.ref(self.frame), "extractionReport": self.ref(extract_path),
            "expectedCanvas": [40, 30], "visualReviewReport": self.ref(review_path),
        })
        with self.assertRaisesRegex(ValueError, "transparent exterior"):
            production.validate_matte_readiness(self.ref(audit_path), "matte", self.root / "ledger.json")

    def test_handoff_report_rechecks_recorded_scene_and_identity_hashes(self):
        handoff = self.write("handoff.json", {
            "schema": "ndc-local-generation-handoff-report/v1",
            "roles": {"image2": str(self.source), "image3": str(self.frame)},
            "sourceHashes": {"scene": visual.sha256(self.source), "characterCard": visual.sha256(self.frame)},
        })
        ref = self.ref(handoff)
        production.validate_handoff_source_bindings(ref, "handoff", self.root / "ledger.json")
        Image.new("RGBA", (40, 30), (220, 50, 60, 255)).save(self.frame)
        with self.assertRaisesRegex(ValueError, "sourceHashes.characterCard hash does not match"):
            production.validate_handoff_source_bindings(ref, "handoff", self.root / "ledger.json")


if __name__ == "__main__":
    unittest.main()
