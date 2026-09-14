from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "delivery_candidate_registry.py"
SPEC = importlib.util.spec_from_file_location("delivery_candidate_registry", SCRIPT)
REGISTRY = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(REGISTRY)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class DeliveryCandidateRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.delivery = self.root / "最终交付"
        self.work = self.root / "工作过程文件"
        self.delivery.mkdir()
        self.work.mkdir()
        self.old_delivery = os.environ.get("NDC_ART_DELIVERY_ROOT")
        self.old_work = os.environ.get("NDC_ART_WORK_ROOT")
        os.environ["NDC_ART_DELIVERY_ROOT"] = str(self.delivery)
        os.environ["NDC_ART_WORK_ROOT"] = str(self.work)
        self.source = self.work / "candidate.png"
        Image.new("RGBA", (12, 10), (20, 40, 60, 255)).save(self.source)

    def tearDown(self) -> None:
        if self.old_delivery is None:
            os.environ.pop("NDC_ART_DELIVERY_ROOT", None)
        else:
            os.environ["NDC_ART_DELIVERY_ROOT"] = self.old_delivery
        if self.old_work is None:
            os.environ.pop("NDC_ART_WORK_ROOT", None)
        else:
            os.environ["NDC_ART_WORK_ROOT"] = self.old_work
        self.temp.cleanup()

    def registration(
        self, candidate_id: str = "scene-r1-c01", requirement_id: str = "scene:final"
    ) -> dict:
        return {
            "schema": REGISTRY.REGISTRATION_SCHEMA,
            "candidateId": candidate_id,
            "requirementId": requirement_id,
            "artifactRole": "delivery_candidate",
            "source": {"path": self.source.name, "sha256": digest(self.source)},
            "deliveryParent": "角色融入场景/Unit1/测试场景__scene",
            "targetFilename": "selected.png",
            "scenePlacement": {"mode": "NOT_SCENE_PLACEABLE", "basis": "opaque full-scene candidate"},
            "selectedAt": "2026-09-12T14:00:00+08:00",
            "selectionBasis": "current image selected for delivery",
            "processEvidence": [],
            "supersedesCandidateId": None,
        }

    def register(self, value: dict) -> dict:
        path = self.work / f"{value['candidateId']}.json"
        source_value = value["source"]
        source_value["path"] = str(self.source)
        write_json(path, value)
        return REGISTRY.register_candidate(path)

    def test_register_copies_exact_bytes_and_marks_candidate_not_formal(self) -> None:
        result = self.register(self.registration())
        manifest_path = Path(result["manifestPath"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        copied = manifest_path.parent / manifest["candidateFile"]["name"]
        self.assertEqual(digest(copied), digest(self.source))
        self.assertEqual(manifest["state"], "DELIVERY_CANDIDATE_PENDING_REVIEW")
        self.assertFalse(manifest["formalApproval"])
        self.assertFalse(manifest["engineSyncAllowed"])
        self.assertIn("非正式 PASS", (manifest_path.parent / "00_交付候选_状态.txt").read_text(encoding="utf-8"))

    def test_selected_reference_is_a_supported_delivery_candidate_role(self) -> None:
        value = self.registration(candidate_id="reference-r1-c01", requirement_id="scene:reference")
        value["artifactRole"] = "selected_reference"
        result = self.register(value)
        self.assertEqual(result["artifactRole"], "selected_reference")

    def test_transparent_scene_ready_candidate_requires_xy_in_filename(self) -> None:
        Image.new("RGBA", (12, 10), (0, 0, 0, 0)).save(self.source)
        with Image.open(self.source) as image:
            pixels = image.load()
            pixels[4, 5] = (20, 40, 60, 255)
            image.save(self.source)
        value = self.registration(candidate_id="scene-ready-r1-c01", requirement_id="scene:actor-layer")
        value["targetFilename"] = "SC2206_Zack_pose.png"
        value["scenePlacement"] = {"mode": "SCENE_READY_RGBA", "x": 30, "y": 20, "basis": "Photoshop top-left registration"}
        with self.assertRaisesRegex(ValueError, "must end with __XY"):
            self.register(value)
        value["targetFilename"] = "SC2206_Zack_pose__XY_x30_y20.png"
        result = self.register(value)
        self.assertEqual(result["scenePlacement"]["x"], 30)

    def test_xy_suffix_must_match_declared_scene_placement(self) -> None:
        Image.new("RGBA", (12, 10), (0, 0, 0, 0)).save(self.source)
        with Image.open(self.source) as image:
            pixels = image.load()
            pixels[4, 5] = (20, 40, 60, 255)
            image.save(self.source)
        value = self.registration(candidate_id="scene-ready-r1-c02", requirement_id="scene:actor-layer-2")
        value["targetFilename"] = "SC2206_Zack_pose__XY_x30_y21.png"
        value["scenePlacement"] = {"mode": "SCENE_READY_RGBA", "x": 30, "y": 20, "basis": "Photoshop top-left registration"}
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.register(value)

    def test_new_current_candidate_requires_explicit_supersedes_chain(self) -> None:
        first = self.register(self.registration())
        second_value = self.registration(candidate_id="scene-r1-c02")
        with self.assertRaisesRegex(ValueError, "supersedesCandidateId"):
            self.register(second_value)
        second_value["supersedesCandidateId"] = first["candidateId"]
        second = self.register(second_value)
        prior = json.loads(Path(first["manifestPath"]).read_text(encoding="utf-8"))
        self.assertEqual(prior["state"], "DELIVERY_CANDIDATE_SUPERSEDED")
        self.assertFalse(prior["current"])
        self.assertEqual(prior["supersededByCandidateId"], second["candidateId"])

    def test_failed_review_stays_in_candidate_folder_and_becomes_move_eligible(self) -> None:
        result = self.register(self.registration())
        manifest_path = Path(result["manifestPath"])
        reviewed = REGISTRY.review_candidate(
            manifest_path,
            "fail",
            "2026-09-12T14:05:00+08:00",
            "visible identity defect",
            [],
        )
        self.assertTrue(manifest_path.is_file())
        self.assertEqual(
            reviewed["state"], "DELIVERY_CANDIDATE_REVIEW_FAILED_MOVE_ELIGIBLE"
        )
        self.assertTrue(reviewed["review"]["moveEligible"])

    def test_passing_candidate_review_does_not_grant_formal_or_engine_state(self) -> None:
        result = self.register(self.registration())
        manifest_path = Path(result["manifestPath"])
        reviewed = REGISTRY.review_candidate(
            manifest_path,
            "pass",
            "2026-09-12T14:05:00+08:00",
            "candidate review complete",
            [],
        )
        self.assertEqual(reviewed["state"], "DELIVERY_CANDIDATE_REVIEW_PASS")
        self.assertFalse(reviewed["formalApproval"])
        self.assertFalse(reviewed["engineSyncAllowed"])

    def test_inventory_uses_candidate_manifests_for_progress_but_not_formal_approval(self) -> None:
        self.register(self.registration())
        scope = self.work / "scope.json"
        write_json(
            scope,
            {
                "schema": REGISTRY.SCOPE_SCHEMA,
                "requiredArtifactIds": ["scene:final", "scene:reference"],
            },
        )
        inventory = REGISTRY.inventory_candidates(scope)
        self.assertEqual(inventory["counts"]["currentCandidateCount"], 1)
        self.assertEqual(inventory["scope"]["candidateCoveragePercent"], 50.0)
        self.assertEqual(inventory["scope"]["missingRequirementIds"], ["scene:reference"])
        self.assertFalse(inventory["candidateCoverageIsFormalApproval"])

    def test_source_hash_and_delivery_parent_are_fail_closed(self) -> None:
        value = self.registration()
        value["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "sha256"):
            self.register(value)
        value = self.registration(candidate_id="bad-parent")
        value["deliveryParent"] = "../outside"
        with self.assertRaisesRegex(ValueError, "safe path"):
            self.register(value)

    def test_inventory_rejects_tampered_candidate_state_and_does_not_count_coverage(self) -> None:
        result = self.register(self.registration())
        manifest_path = Path(result["manifestPath"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["formalApproval"] = True
        write_json(manifest_path, manifest)
        inventory = REGISTRY.inventory_candidates()
        self.assertEqual(inventory["counts"]["invalidCount"], 1)
        self.assertEqual(inventory["counts"]["currentCandidateCount"], 0)
        self.assertIn("formal approval", inventory["invalid"][0]["error"])


if __name__ == "__main__":
    unittest.main()
