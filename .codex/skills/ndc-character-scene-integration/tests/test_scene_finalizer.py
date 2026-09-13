from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "character_scene_pipeline_finalizer", SCRIPT_DIR / "character_scene_pipeline.py"
)
PIPELINE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(PIPELINE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class SceneFinalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scene = self.root / "scene.png"
        self.layout = self.root / "layout.png"
        self.ui_left = self.root / "ui-left.png"
        self.ui_right = self.root / "ui-right.png"
        Image.new("RGB", (96, 64), (80, 70, 60)).save(self.scene)
        Image.new("RGB", (96, 64), (95, 85, 75)).save(self.layout)
        for path, x in ((self.ui_left, 0), (self.ui_right, 48)):
            image = Image.new("RGBA", (96, 64), (0, 0, 0, 0))
            ImageDraw.Draw(image).rectangle((x, 45, x + 47, 63), fill=(20, 20, 20, 210))
            image.save(path)
        self.actor = self.root / "actor.png"
        image = Image.new("RGBA", (24, 40), (0, 0, 0, 0))
        ImageDraw.Draw(image).ellipse((5, 2, 18, 15), fill=(210, 170, 140, 255))
        ImageDraw.Draw(image).rectangle((7, 14, 17, 37), fill=(70, 100, 140, 255))
        image.save(self.actor)
        self.evidence = self.root / "review.json"
        write_json(self.evidence, {"reviewAuthority": "codex-self-check", "status": "PASS"})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def manifest(self, *, quality: str = "usable", edge: str = "PROVISIONAL") -> dict:
        criteria = {
            name: {
                "status": "PASS",
                "evidence": [{"path": self.evidence.name, "sha256": sha256(self.evidence)}],
            }
            for name in PIPELINE.FINALIZATION_BASE_CHECKS
        }
        return {
            "schema": PIPELINE.FINALIZATION_SCHEMA,
            "sceneId": "test-scene",
            "scope": {
                "interactionType": "pure-narrative",
                "simultaneousCastCount": 1,
                "supportTypes": ["ground"],
                "hasSoftSupport": False,
                "hasRecliningOrElevatedActor": False,
                "requiredLayerIds": ["actor:idle"],
                "anatomyCoverage": [
                    {
                        "id": "actor:idle",
                        "mode": "FULL_IN_FRAME",
                        "visibleAnatomyReview": "PASS",
                        "completeMaster": {"path": self.actor.name, "sha256": sha256(self.actor)},
                        "completeMasterReview": "PASS",
                        "evidence": [{"path": self.evidence.name, "sha256": sha256(self.evidence)}],
                    }
                ],
            },
            "ui": {
                "required": True,
                "variant": "left",
                "references": {"left": self.ui_left.name, "right": self.ui_right.name},
            },
            "artifacts": {"sourceScene": self.scene.name, "layoutSource": self.layout.name},
            "criteria": criteria,
            "extraction": {
                "layers": [
                    {
                        "id": "actor:idle",
                        "path": self.actor.name,
                        "quality": quality,
                        "xy": [30, 20],
                        "structuralReview": "PASS",
                        "edgeReview": edge,
                        "reviewEvidence": [
                            {"path": self.evidence.name, "sha256": sha256(self.evidence)}
                        ],
                    }
                ],
                "routeExhaustion": [{"id": "native-alpha", "status": "FORMAL_PASS"}],
            },
            "validators": [],
            "reconstruction": {"enabled": True},
            "outputDir": "output",
            "timingLedger": [],
        }

    def run_manifest(self, data: dict, profile: str) -> dict:
        path = self.root / "manifest.json"
        write_json(path, data)
        return PIPELINE.finalize_scene(path, profile)

    def add_formal_validators(self, data: dict) -> None:
        ledger = self.root / "ledger.json"
        conformance = self.root / "conformance.json"
        write_json(ledger, {"synthetic": "production-ledger contract for invocation test"})
        write_json(conformance, {"synthetic": "final-conformance contract for invocation test"})
        data["validators"] = [
            {"name": "production-ledger", "contract": ledger.name, "profiles": ["formal"]},
            {"name": "final-conformance", "contract": conformance.name, "profiles": ["formal"]},
        ]

    def test_all_npc_scenes_require_actual_ui(self) -> None:
        data = self.manifest()
        data["ui"]["required"] = False
        with self.assertRaisesRegex(ValueError, "ui.required must be true"):
            self.run_manifest(data, "probe")

    def test_branch_resolver_keeps_base_universal_and_adds_only_factual_checks(self) -> None:
        branches = PIPELINE.finalization_branches(
            {
                "interactionType": "exploration-click-pair",
                "simultaneousCastCount": 3,
                "supportTypes": ["bed"],
                "hasSoftSupport": True,
                "hasRecliningOrElevatedActor": True,
            }
        )
        self.assertEqual(
            branches,
            [
                "idle_click_continuity",
                "multicast_links",
                "multi_actor_relative_scale",
                "pairwise_actor_occlusion",
                "multicast_back_composition",
                "soft_support_response",
                "reclining_elevated_projection",
            ],
        )
        self.assertIn("scene_scale", PIPELINE.FINALIZATION_BASE_CHECKS)
        self.assertIn("occlusion_layer_order", PIPELINE.FINALIZATION_BASE_CHECKS)

    def test_probe_requires_first_usable_rgba_but_skips_matte_and_formal_packaging(self) -> None:
        data = self.manifest()
        data["extraction"]["layers"] = []
        blocked = self.run_manifest(data, "probe")
        self.assertEqual(blocked["result"], "BLOCKED")
        report = self.run_manifest(self.manifest(), "probe")
        self.assertEqual(report["result"], "PASS")
        self.assertTrue(Path(report["outputs"]["layoutPreview"]).is_file())
        self.assertTrue(Path(report["outputs"]["pixelProofPreview"]).is_file())
        self.assertNotIn("matteContactSheet", report["outputs"])
        self.assertNotIn("xyManifest", report["outputs"])

    def test_first_usable_rgba_produces_pixel_proof_and_one_matte_board(self) -> None:
        report = self.run_manifest(self.manifest(), "provisional")
        self.assertEqual(report["result"], "PROVISIONAL")
        self.assertEqual(report["packageState"], "PROVISIONAL_SCENE_PACKAGE")
        self.assertTrue(Path(report["outputs"]["pixelProofPreview"]).is_file())
        self.assertTrue(Path(report["outputs"]["matteContactSheet"]).is_file())
        self.assertTrue(Path(report["outputs"]["xyManifest"]).is_file())
        self.assertTrue(Path(report["outputs"]["finalization"]).is_file())
        self.assertTrue(Path(report["outputs"]["summary"]).is_file())
        self.assertTrue(Path(report["outputs"]["packageIndex"]).is_file())
        self.assertTrue(report["routeState"]["firstUsableRgba"])

    def test_h0_failed_rgba_is_not_composited_as_first_usable(self) -> None:
        data = self.manifest()
        data["extraction"]["layers"][0]["structuralReview"] = "FAIL"
        report = self.run_manifest(data, "provisional")
        self.assertEqual(report["result"], "BLOCKED")
        self.assertEqual(report["packageState"], "H0_BLOCKED_PACKAGE")
        self.assertFalse(report["routeState"]["firstUsableRgba"])
        self.assertNotIn("pixelProofPreview", report["outputs"])

    def test_missing_alpha_review_evidence_keeps_preview_but_blocks_claim(self) -> None:
        data = self.manifest()
        del data["extraction"]["layers"][0]["reviewEvidence"]
        report = self.run_manifest(data, "provisional")
        self.assertEqual(report["result"], "BLOCKED")
        self.assertTrue(Path(report["outputs"]["pixelProofPreview"]).is_file())
        self.assertTrue(any("review evidence is missing" in reason for reason in report["blockedReasons"]))

    def test_formal_requires_formal_rgba_and_passed_edge_review(self) -> None:
        blocked = self.run_manifest(self.manifest(), "formal")
        self.assertEqual(blocked["result"], "BLOCKED")
        data = self.manifest(quality="formal", edge="PASS")
        self.add_formal_validators(data)
        validator_results = ([
            {"name": "production-ledger", "status": "PASS", "detail": "synthetic invocation"},
            {"name": "final-conformance", "status": "PASS", "detail": "synthetic invocation"},
        ], [])
        with patch.object(PIPELINE, "run_finalization_validators", return_value=validator_results) as invoked:
            passed = self.run_manifest(data, "formal")
        self.assertEqual(passed["result"], "PASS")
        self.assertEqual(passed["packageState"], "FORMAL_CANDIDATE")
        self.assertTrue(passed["routeState"]["stopRemainingRoutes"])
        invoked.assert_called_once()

    def test_metadata_only_change_hits_pixel_and_criteria_cache(self) -> None:
        data = self.manifest()
        first = self.run_manifest(data, "provisional")
        self.assertFalse(first["cacheHit"])
        data["notes"] = "metadata that does not change pixels or criteria"
        second = self.run_manifest(data, "provisional")
        self.assertTrue(second["cacheHit"])
        self.assertEqual(first["cacheKey"], second["cacheKey"])

    def test_byte_identical_evidence_copy_does_not_invalidate_cache(self) -> None:
        data = self.manifest()
        first = self.run_manifest(data, "provisional")
        copied = self.root / "review-copy.json"
        copied.write_bytes(self.evidence.read_bytes())
        for entry in data["criteria"].values():
            entry["evidence"][0]["path"] = copied.name
        second = self.run_manifest(data, "provisional")
        self.assertTrue(second["cacheHit"])
        self.assertEqual(first["cacheKey"], second["cacheKey"])

    def test_cache_reuses_pixels_but_reruns_dependency_validators(self) -> None:
        data = self.manifest(quality="formal", edge="PASS")
        self.add_formal_validators(data)
        validator_results = ([
            {"name": "production-ledger", "status": "PASS", "detail": "fresh"},
            {"name": "final-conformance", "status": "PASS", "detail": "fresh"},
        ], [])
        with patch.object(PIPELINE, "run_finalization_validators", return_value=validator_results) as invoked:
            first = self.run_manifest(data, "formal")
            second = self.run_manifest(data, "formal")
        self.assertFalse(first["cacheHit"])
        self.assertTrue(second["cacheHit"])
        self.assertEqual(invoked.call_count, 2)

    def test_timing_actions_separate_external_wait_and_trigger_method_switch(self) -> None:
        records = [
            {
                "phase": "layout",
                "started_at": "2026-09-11T10:00:00+08:00",
                "finished_at": "2026-09-11T10:35:00+08:00",
                "active_seconds": 1801,
                "external_wait_seconds": 299,
                "cache_hit": False,
                "result": "IN_PROGRESS",
                "block_reason": "",
            }
        ]
        _, actions, total_active = PIPELINE.validate_timing_ledger(records, pixel_preview_ready=False)
        self.assertTrue(any("SWITCH_METHOD" in item for item in actions))
        self.assertFalse(any("PACKAGE_PROVISIONAL" in item for item in actions))
        self.assertEqual(total_active, 1801)

    def test_frame_cropped_foreground_needs_visible_exit_and_offframe_evidence_not_feet(self) -> None:
        data = self.manifest()
        data["scope"]["anatomyCoverage"] = [{
            "id": "actor:idle",
            "mode": "FRAME_CROPPED_FOREGROUND",
            "visibleAnatomyReview": "PASS",
            "naturalFrameExit": True,
            "visibleAnatomyComplete": True,
            "offFrameScaleSupportEvidence": [{"path": self.evidence.name, "sha256": sha256(self.evidence)}],
            "evidence": [{"path": self.evidence.name, "sha256": sha256(self.evidence)}],
        }]
        report = self.run_manifest(data, "provisional")
        self.assertEqual(report["packageState"], "PROVISIONAL_SCENE_PACKAGE")
        data["scope"]["anatomyCoverage"][0]["naturalFrameExit"] = False
        report = self.run_manifest(data, "provisional")
        self.assertEqual(report["packageState"], "H0_BLOCKED_PACKAGE")

    def test_h2_review_failure_remains_visible_but_does_not_zero_provisional_output(self) -> None:
        data = self.manifest()
        data["criteria"]["whole_scene_review"].update(status="FAIL", tier="H2")
        report = self.run_manifest(data, "provisional")
        self.assertEqual(report["result"], "PROVISIONAL")
        self.assertEqual(report["packageState"], "PROVISIONAL_SCENE_PACKAGE")
        self.assertTrue(any("H2" in item for item in report["provisionalReasons"]))

    def test_ps_release_requires_actual_docs0_queue0_and_capability_binding(self) -> None:
        capability = self.root / "capability.json"
        write_json(capability, {"bridge": "connected", "supported": ["open", "export"]})
        data = self.manifest()
        data["psSession"] = {
            "used": True,
            "ownerTaskId": "test-task",
            "openDocumentCount": 0,
            "inFlightCommandCount": 0,
            "unknownCommandCount": 0,
            "handoffStatus": "RELEASED",
            "capabilitySnapshot": {"path": capability.name, "sha256": sha256(capability)},
            "evidence": [{"path": self.evidence.name, "sha256": sha256(self.evidence)}],
        }
        self.assertEqual(self.run_manifest(data, "provisional")["packageState"], "PROVISIONAL_SCENE_PACKAGE")
        data["psSession"]["openDocumentCount"] = 1
        report = self.run_manifest(data, "provisional")
        self.assertEqual(report["packageState"], "H0_BLOCKED_PACKAGE")

    def test_package_index_is_deterministic_across_metadata_only_resume(self) -> None:
        data = self.manifest()
        first = self.run_manifest(data, "provisional")
        first_hash = sha256(Path(first["outputs"]["packageIndex"]))
        data["operator_note"] = "resume note does not alter deliverables"
        second = self.run_manifest(data, "provisional")
        self.assertTrue(second["cacheHit"])
        self.assertEqual(first_hash, sha256(Path(second["outputs"]["packageIndex"])))


if __name__ == "__main__":
    unittest.main()
