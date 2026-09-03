from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "scene_staging_tools.py"
SPEC = importlib.util.spec_from_file_location("scene_staging_tools", SCRIPT_PATH)
TOOLS = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(TOOLS)

PIPELINE_PATH = SCRIPT_PATH.with_name("character_scene_pipeline.py")
PIPELINE_SPEC = importlib.util.spec_from_file_location("character_scene_pipeline", PIPELINE_PATH)
PIPELINE = importlib.util.module_from_spec(PIPELINE_SPEC)
assert PIPELINE_SPEC and PIPELINE_SPEC.loader
PIPELINE_SPEC.loader.exec_module(PIPELINE)

PRODUCTION_GATE_PATH = SCRIPT_PATH.with_name("production_gate.py")
PRODUCTION_GATE_SPEC = importlib.util.spec_from_file_location(
    "production_gate", PRODUCTION_GATE_PATH
)
PRODUCTION_GATE = importlib.util.module_from_spec(PRODUCTION_GATE_SPEC)
assert PRODUCTION_GATE_SPEC and PRODUCTION_GATE_SPEC.loader
PRODUCTION_GATE_SPEC.loader.exec_module(PRODUCTION_GATE)

VISUAL_GATE_PATH = SCRIPT_PATH.with_name("visual_review_gate.py")
VISUAL_GATE_SPEC = importlib.util.spec_from_file_location("visual_review_gate", VISUAL_GATE_PATH)
VISUAL_GATE = importlib.util.module_from_spec(VISUAL_GATE_SPEC)
assert VISUAL_GATE_SPEC and VISUAL_GATE_SPEC.loader
VISUAL_GATE_SPEC.loader.exec_module(VISUAL_GATE)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class SceneStagingToolTests(unittest.TestCase):
    def _placement_contract(self, root: Path, scene: Path) -> dict:
        pose = {
            "headBox": [96, 15, 114, 32],
            "neck": [105, 37],
            "leftShoulder": [88, 48],
            "rightShoulder": [122, 46],
            "leftElbow": [82, 78],
            "rightElbow": [130, 82],
            "leftHand": [90, 105],
            "rightHand": [122, 110],
            "leftHip": [96, 105],
            "rightHip": [116, 106],
            "leftKnee": [94, 145],
            "rightKnee": [119, 150],
            "leftFoot": [95, 185],
            "rightFoot": [125, 185],
            "supportObject": "floor-1",
        }
        return {
            "scene": str(scene),
            "deliveryRoot": str(root / scene.stem),
            "sceneSize": [240, 200],
            "characterName": "A",
            "characterHeightCm": 170,
            "calibration": {
                "aggregationMethod": "median-after-depth-projection",
                "maxSpreadRatio": 0.08,
                "maxCrossDepthMedianDeltaRatio": 0.08,
                "projectedHeightEstimatesPx": [
                    {"objectId": "door", "independenceGroup": "door-1", "dimension": "height", "realWorldRangeCm": [190, 210], "assumedCm": 200, "imageMeasurementPx": 200, "projectedMeasurementPxAtTarget": 200, "projectionMethod": "same support band", "planeRelation": "adjacent depth", "depthBand": "actor-local", "value": 170, "confidence": "high"},
                    {"objectId": "desk", "independenceGroup": "desk-1", "dimension": "height", "realWorldRangeCm": [90, 110], "assumedCm": 100, "imageMeasurementPx": 70, "projectedMeasurementPxAtTarget": 100, "projectionMethod": "floor-grid projection", "planeRelation": "farther depth projected to actor", "depthBand": "cross-depth", "projectionEvidence": {"sourceSupportPoint": [180, 90], "targetSupportPoint": [110, 185], "perspectiveBasisIds": ["floor-grid-1"]}, "value": 170, "confidence": "high"},
                ],
            },
            "target": {
                "placementClass": "standing",
                "affordanceZoneId": "stand-1",
                "foot": [110, 185],
                "visibleHeightPx": 170,
                "outerBBox": [70, 10, 150, 190],
                "poseDefinition": {"poseId": "a-v1", "action": "reads chart", "facing": "right", "gazeTarget": "chart", "leftHandAction": "supports chart", "rightHandAction": "holds edge", "requiredProps": ["chart"]},
                "standingPose": pose,
                "sceneRelations": [{"objectId": "floor-1", "relation": "supported-by", "regions": ["leftFoot", "rightFoot"], "reason": "feet meet floor"}],
            },
        }

    def test_pipeline_requires_affordance_and_snapshot_ui_report(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            old_root = PIPELINE.NDC_ROOT
            PIPELINE.NDC_ROOT = root
            try:
                scene = root / "scene.png"
                Image.new("RGBA", (240, 200), (0, 0, 0, 255)).save(scene)
                placement = self._placement_contract(root, scene)
                placement_path = root / "placement.json"
                write_json(placement_path, placement)
                PIPELINE.validate_contract(placement)
                missing_cross_depth = json.loads(json.dumps(placement))
                missing_cross_depth["calibration"]["projectedHeightEstimatesPx"][1]["depthBand"] = "actor-local"
                with self.assertRaisesRegex(ValueError, "actor-local and cross-depth"):
                    PIPELINE.validate_contract(missing_cross_depth)
                conflicting_bands = json.loads(json.dumps(placement))
                conflicting_bands["calibration"]["maxSpreadRatio"] = 0.25
                conflicting_bands["calibration"]["maxCrossDepthMedianDeltaRatio"] = 0.05
                far = conflicting_bands["calibration"]["projectedHeightEstimatesPx"][1]
                far["projectedMeasurementPxAtTarget"] = 110
                far["value"] = 187
                with self.assertRaisesRegex(ValueError, "cross-depth scale estimates disagree"):
                    PIPELINE.validate_contract(conflicting_bands)
                missing_zone = json.loads(json.dumps(placement))
                missing_zone["target"].pop("affordanceZoneId")
                with self.assertRaisesRegex(ValueError, "affordanceZoneId"):
                    PIPELINE.validate_contract(missing_zone)
                ui_report = root / "ui-report.json"
                write_json(ui_report, {"schema": "ndc-ui-safety-report/v1", "status": "pass", "actors": []})
                staging = {
                    "scene": str(scene),
                    "sceneSize": [240, 200],
                    "timelineSnapshotId": "beat-01",
                    "uiSide": "left",
                    "uiSafetyReview": {"status": "passed", "report": str(ui_report), "reportSha256": PIPELINE.sha256_file(ui_report)},
                    "characters": [{"name": "A", "contract": str(placement_path), "layerOrder": 10}],
                    "occlusionGraph": [],
                }
                loaded = PIPELINE.validate_staging(staging)
                self.assertEqual(len(loaded), 1)
            finally:
                PIPELINE.NDC_ROOT = old_root

    def test_production_gate_rejects_false_pass_and_bbox_scale_driver(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            scene = root / "scene.png"
            Image.new("RGB", (160, 100), "black").save(scene)
            ledger = root / "ledger.json"
            base_case = {
                "caseId": "case-1",
                "branch": "pure-narrative",
                "sourceScene": str(scene),
                "sourceSceneSha256": PRODUCTION_GATE.sha256(scene),
                "technicalStatus": "PASS",
                "scaleDriver": "target-bbox",
                "affordanceContract": {},
                "uiSafetyReports": [],
                "placementContracts": [],
                "stagingContracts": [],
                "whiteboxEvidence": {},
                "supportContactReports": [],
                "castScaleReport": {},
                "localGenerationHandoffs": [],
                "visualReviewReports": [],
            }
            with self.assertRaisesRegex(ValueError, "file checks only"):
                PRODUCTION_GATE.validate_case(base_case, 0, ledger, "pre-generation")
            base_case["technicalStatus"] = "TECHNICAL_FILE_PASS"
            with self.assertRaisesRegex(ValueError, "target-box or alpha-box"):
                PRODUCTION_GATE.validate_case(base_case, 0, ledger, "pre-generation")

    def test_visual_review_gate_requires_explicit_checks_and_builds_board(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            primary = root / "composite.png"
            reference = root / "reference.png"
            Image.new("RGB", (320, 200), (30, 40, 50)).save(primary)
            Image.new("RGB", (320, 200), (50, 40, 30)).save(reference)
            checks = {name: "pass" for name in VISUAL_GATE.STAGE_CHECKS["pre-composite-registration"]}
            contract = {
                "schema": "ndc-stage-visual-review/v1",
                "stage": "pre-composite-registration",
                "reviewAuthority": "codex-self-check",
                "artifacts": [
                    {"role": "registration-preview", "path": str(primary)},
                    {"role": "accepted-local", "path": str(reference)},
                ],
                "localTiles": [{"id": "actor-a", "bbox": [80, 20, 220, 195]}],
                "checks": checks,
                "observations": ["Actor scale remains consistent with the accepted contextual crop."],
                "decision": "pass",
            }
            path = root / "review.json"
            write_json(path, contract)
            report = VISUAL_GATE.build_review(path, root / "review")
            self.assertEqual(report["status"], "VISUAL_REVIEW_PASS")
            self.assertTrue(Path(report["board"]).is_file())
            contract["checks"].pop("headScale")
            write_json(path, contract)
            with self.assertRaisesRegex(ValueError, "missing checks"):
                VISUAL_GATE.build_review(path, root / "review-2")

    def test_tolerant_tables_and_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            talk = root / "Talk.json"
            npc = root / "NPCLoopData.json"
            talk.write_text(
                """[{
\t\"id\" : \"100\",
\t\"step\" : \"1\",
\t\"Speaker\" : {
\t\"id\" : \"1\"
},
\t\"Words\" : [\"B 进场。\",\"B says \"hello\".\"],
\t\"next\" : \"101\",
\t\"script\" : \"13\",
\t\"Parameters\" : [{\"ParameterInt\" : \"20\"}],
\t\"videoScene\" : \"room\"
},
{
\t\"id\" : \"101\",
\t\"step\" : \"2\",
\t\"Speaker\" : {
\t\"id\" : \"2\"
},
\t\"Words\" : [\"A 退场。\",\"A exits.\"],
\t\"next\" : \"0\",
\t\"script\" : \"14\",
\t\"Parameters\" : [{\"ParameterInt\" : \"1\"}]
}]""",
                encoding="utf-8",
            )
            npc.write_text(
                """[{
\t\"id\" : \"10\",
\t\"NPC\" : {
\t\"id\" : \"1\",
\t\"Name\" : [\"A\",\"A\"]
},
\t\"TalkInfo\" : {\n\t\"id\" : \"900\"\n},
\t\"LoopTalkInfo\" : {\n\t\"id\" : \"901\"\n},
\t\"ResPath\" : \"Art\\Scene\\NPC\\a_idle\",
\t\"ClickResPath\" : \"Art\\Scene\\NPC\\a_active\",
\t\"PosX\" : \"10\",\n\t\"Posy\" : \"20\",\n\t\"PosZ\" : \"-1\"
},
{
\t\"id\" : \"20\",
\t\"NPC\" : {
\t\"id\" : \"2\",
\t\"Name\" : [\"B\",\"B\"]
},
\t\"ResPath\" : \"Art\\Scene\\NPC\\b\",
\t\"ClickResPath\" : \"Art\\Scene\\NPC\\b\",
\t\"PosX\" : \"30\",\n\t\"Posy\" : \"40\",\n\t\"PosZ\" : \"-2\"
}]""",
                encoding="utf-8",
            )
            result = TOOLS.extract_timeline(talk, npc, "100", ["10"], None, 10)
            self.assertEqual(result["summary"]["nodeCount"], 2)
            self.assertEqual(result["summary"]["enterCount"], 1)
            self.assertEqual(result["summary"]["exitCount"], 1)
            self.assertEqual(result["nodes"][0]["frozenActorIds"], ["npc:1"])
            self.assertEqual(result["nodes"][1]["afterCast"], ["npc:2"])
            self.assertFalse(result["issues"])

    def test_unresolved_dialogue_branch_stops_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            talk = root / "Talk.json"
            npc = root / "NPCLoopData.json"
            talk.write_text(
                """[{\n\t\"id\" : \"100\",\n\t\"Parameters\" : [{\"ParameterInt\" : \"101\"},{\"ParameterInt\" : \"102\"}]\n},\n{\n\t\"id\" : \"101\",\n\t\"next\" : \"0\"\n},\n{\n\t\"id\" : \"102\",\n\t\"next\" : \"0\"\n}]""",
                encoding="utf-8",
            )
            npc.write_text("[]", encoding="utf-8")
            unresolved = TOOLS.extract_timeline(talk, npc, "100", [], None, 10)
            self.assertEqual(unresolved["issues"][0]["code"], "UNRESOLVED_BRANCH")
            selected = TOOLS.extract_timeline(talk, npc, "100", [], None, 10, choice_map={"100": "102"})
            self.assertEqual([node["nodeId"] for node in selected["nodes"]], ["100", "102"])

    def test_scene_config_initial_cast_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "SceneConfig.json"
            path.write_text(
                """[{\n\t\"sceneId\" : \"1\",\n\t\"NPCInfos\" : [{\n\t\"id\" : \"10\",\n\t\"NPC\" : {\n\t\"id\" : \"1\"\n}\n},\n{\n\t\"id\" : \"20\",\n\t\"NPC\" : {\n\t\"id\" : \"2\"\n}\n}]\n},\n{\n\t\"sceneId\" : \"2\",\n\t\"note\" : \"empty\"\n}]""",
                encoding="utf-8",
            )
            self.assertEqual(TOOLS.parse_scene_config_initial_loops(path, "1"), ["10", "20"])
            self.assertEqual(TOOLS.parse_scene_config_initial_loops(path, "2"), [])

    def test_directing_timeline_rejects_existing_actor_drift(self) -> None:
        performance = {
            "action": "hold a chart",
            "emotion": "contained worry",
            "energy": "low",
            "beatEnergy": "low",
            "silentFrameVerb": "guard",
            "ongoingOccupation": "reads the chart before anyone enters",
            "performanceFamily": "ongoing-occupation",
            "bodyLine": "slightly curved",
            "weightDistribution": "left foot",
            "facialExpression": "tight brow",
            "handBusiness": "thumb rubs chart edge",
            "gestureMotivation": {"leftHand": "supports chart", "rightHand": "checks chart edge"},
            "namedSupport": "floor-1",
            "socialTerritory": "bedside work zone",
            "costumeState": "working uniform",
            "holdPoseValidity": "pass",
            "tenSecondHold": "pass",
            "depthHonesty": "pass",
        }
        actor = {
            "actorId": "A",
            "poseId": "a-v1",
            "transformId": "a-transform-v1",
            "placementId": "a-place-v1",
            "affordanceZoneId": "stand-1",
            "gazeTarget": {"type": "scene-object", "id": "chart"},
            "futureActorDependency": False,
            "reciprocityRequired": False,
            "performance": performance,
        }
        beat = {
            "objective": "hide concern",
            "conflict": "news is worsening",
            "emotion": "worry",
            "subtext": "do not alarm the patient",
            "actionFocus": "chart",
        }
        contract = {
            "schema": "ndc-directing-timeline/v1",
            "timelineType": "pure-narrative",
            "snapshots": [
                {"id": "s0", "storyBeat": beat, "silentFrameStatement": "A hides worry.", "event": {"type": "initial"}, "actors": [actor]},
                {"id": "s1", "storyBeat": beat, "silentFrameStatement": "B enters while A holds.", "event": {"type": "enter", "actorId": "B"}, "actors": [
                    {**actor, "poseId": "a-v2"},
                    {**actor, "actorId": "B", "poseId": "b-v1", "transformId": "b-transform-v1", "placementId": "b-place-v1"},
                ]},
            ],
        }
        with self.assertRaisesRegex(ValueError, "later entrant"):
            TOOLS.validate_directing_timeline(contract)

    def test_affordance_and_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            contract = {
                "schema": "ndc-scene-affordance/v1",
                "sceneSize": [320, 200],
                "zones": [
                    {"id": "seat-1", "polygon": [[20, 40], [180, 40], [180, 170], [20, 170]], "capabilities": ["sit"], "depthClass": "midground"}
                ],
                "supportSurfaces": [
                    {"id": "chair-1", "evidence": "fixture chair", "occupancy": {"status": "clear", "evidence": "fixture seat is clear"}, "contacts": [
                        {"regions": ["hipSeat"], "polyline": [[80, 130], [120, 130]], "tolerancePx": 2}
                    ]}
                ],
                "placements": [
                    {"actorId": "A", "placementClass": "seated", "anchor": [100, 130], "zoneId": "seat-1", "supportObjectId": "chair-1"}
                ],
            }
            path = root / "affordance.json"
            output = root / "affordance.png"
            write_json(path, contract)
            TOOLS.render_affordance(path, output, None)
            with Image.open(output) as rendered:
                self.assertEqual(rendered.size, (320, 200))

    def test_support_contact_rejects_floating_whitebox(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            scene = root / "scene.png"
            Image.new("RGBA", (240, 200), (25, 30, 35, 255)).save(scene)
            placement = self._placement_contract(root, scene)
            placement_path = root / "placement.json"
            write_json(placement_path, placement)
            affordance = {
                "schema": "ndc-scene-affordance/v1",
                "sceneSize": [240, 200],
                "zones": [{"id": "stand-1", "polygon": [[70, 175], [150, 175], [150, 195], [70, 195]], "capabilities": ["stand"], "depthClass": "midground"}],
                "supportSurfaces": [{"id": "floor-1", "evidence": "fixture floor line", "occupancy": {"status": "clear", "evidence": "fixture floor is clear"}, "contacts": [
                    {"regions": ["leftFoot", "rightFoot"], "polyline": [[70, 190], [150, 190]], "tolerancePx": 2}
                ]}],
                "placements": [{"actorId": "A", "placementClass": "standing", "anchor": [110, 185], "zoneId": "stand-1", "supportObjectId": "floor-1"}],
            }
            affordance_path = root / "affordance.json"
            write_json(affordance_path, affordance)
            with self.assertRaisesRegex(ValueError, "floating"):
                TOOLS.validate_support_contact(
                    affordance_path,
                    placement_path,
                    root / "support.json",
                    root / "support.png",
                )
            placement["target"]["standingPose"]["leftFoot"][1] = 190
            placement["target"]["standingPose"]["rightFoot"][1] = 190
            placement["target"]["foot"][1] = 190
            write_json(placement_path, placement)
            report = TOOLS.validate_support_contact(affordance_path, placement_path)
            self.assertEqual(report["status"], "pass")

    def test_cast_scale_uses_height_and_support_depth(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            scene = root / "scene.png"
            Image.new("RGBA", (240, 200), (25, 30, 35, 255)).save(scene)
            actor_a = self._placement_contract(root, scene)
            actor_b = json.loads(json.dumps(actor_a))
            actor_b["characterName"] = "B"
            actor_b["characterHeightCm"] = 180
            actor_b["target"]["poseDefinition"]["poseId"] = "b-v1"
            actor_b["target"]["foot"][1] = 165
            actor_b["target"]["visibleHeightPx"] = 153.3333333333
            write_json(root / "a.json", actor_a)
            write_json(root / "b.json", actor_b)
            contract = {
                "schema": "ndc-cast-scale/v1",
                "sceneSize": [240, 200],
                "horizonY": 50,
                "referenceActorId": "A",
                "maxDeviationRatio": 0.03,
                "actors": [
                    {"actorId": "A", "placementContract": "a.json"},
                    {"actorId": "B", "placementContract": "b.json"},
                ],
            }
            contract_path = root / "cast-scale.json"
            write_json(contract_path, contract)
            report = TOOLS.validate_cast_scale(contract_path)
            self.assertEqual(report["status"], "pass")
            actor_b["target"]["visibleHeightPx"] = 170
            write_json(root / "b.json", actor_b)
            with self.assertRaisesRegex(ValueError, "CAST_SCALE_FAILED"):
                TOOLS.validate_cast_scale(contract_path)

    def test_cast_scale_v2_makes_pairwise_head_ratio_a_primary_gate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            scene = root / "scene.png"
            card = root / "card.png"
            Image.new("RGBA", (240, 200), (25, 30, 35, 255)).save(scene)
            Image.new("RGBA", (120, 200), (245, 245, 245, 255)).save(card)
            actor_a = self._placement_contract(root, scene)
            actor_a["target"]["standingPose"]["headBox"] = [96, 15, 114, 32]
            actor_b = json.loads(json.dumps(actor_a))
            actor_b["characterName"] = "B"
            actor_b["target"]["poseDefinition"]["poseId"] = "b-v1"
            actor_b["target"]["foot"][1] = 165
            actor_b["target"]["visibleHeightPx"] = 144.8148148148
            actor_b["target"]["standingPose"]["headBox"] = [98, 20, 112, 34.4814814815]
            write_json(root / "a.json", actor_a)
            write_json(root / "b.json", actor_b)
            identity = {
                "referenceArtifact": "card.png",
                "referenceFullBodyHeightPx": 170,
                "referenceAnatomicalHeadHeightPx": 17,
                "measurementMethod": "approved-card-front-view",
                "confidence": "high",
            }
            contract = {
                "schema": "ndc-cast-scale/v2",
                "sceneSize": [240, 200],
                "horizonY": 50,
                "referenceActorId": "A",
                "maxDeviationRatio": 0.03,
                "maxHeadDeviationRatio": 0.05,
                "headScalePriority": True,
                "actors": [
                    {"actorId": "A", "placementContract": "a.json", "identityScaleReference": identity},
                    {"actorId": "B", "placementContract": "b.json", "identityScaleReference": identity},
                ],
            }
            contract_path = root / "cast-scale-v2.json"
            write_json(contract_path, contract)
            report = TOOLS.validate_cast_scale(contract_path)
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["headScalePriority"])
            actor_b["target"]["standingPose"]["headBox"] = [98, 20, 112, 28]
            write_json(root / "b.json", actor_b)
            with self.assertRaisesRegex(ValueError, "CAST_SCALE_FAILED"):
                TOOLS.validate_cast_scale(contract_path)

    def test_scene_absolute_scale_catches_shared_cast_oversize(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            Image.new("RGBA", (240, 200), (25, 30, 35, 255)).save(root / "scene.png")
            projection = {
                "perspectiveBasisIds": ["floor-grid"],
                "sourceSupportPoint": [180, 150],
                "targetSupportPoint": [110, 185],
            }
            contract = {
                "schema": "ndc-scene-absolute-scale/v1",
                "scene": "scene.png",
                "sceneSize": [240, 200],
                "actors": [
                    {
                        "actorId": "A",
                        "characterHeightCm": 170,
                        "standingEquivalentHeightPx": 170,
                    }
                ],
                "limits": {
                    "maxGlobalDeviationRatio": 0.05,
                    "maxAnchorSpreadRatio": 0.08,
                    "minimumIndependentAnchors": 3,
                },
                "anchors": [
                    {
                        "anchorId": "door-height",
                        "actorId": "A",
                        "objectId": "door",
                        "independenceGroup": "door-1",
                        "axis": "vertical",
                        "depthBand": "actor-local",
                        "realWorldRangeCm": [95, 105],
                        "assumedCm": 100,
                        "measurementLine": [[20, 20], [20, 120]],
                        "projectionScaleToActorPlane": 1,
                        "projectionEvidence": projection,
                        "confidence": "high",
                    },
                    {
                        "anchorId": "bed-length",
                        "actorId": "A",
                        "objectId": "bed",
                        "independenceGroup": "bed-1",
                        "axis": "horizontal",
                        "depthBand": "cross-depth",
                        "realWorldRangeCm": [95, 105],
                        "assumedCm": 100,
                        "measurementLine": [[80, 120], [180, 120]],
                        "projectionScaleToActorPlane": 1,
                        "projectionEvidence": projection,
                        "confidence": "high",
                    },
                    {
                        "anchorId": "window-height",
                        "actorId": "A",
                        "objectId": "window",
                        "independenceGroup": "window-1",
                        "axis": "vertical",
                        "depthBand": "cross-depth",
                        "realWorldRangeCm": [95, 105],
                        "assumedCm": 100,
                        "measurementLine": [[210, 40], [210, 90]],
                        "projectionScaleToActorPlane": 2,
                        "projectionEvidence": projection,
                        "confidence": "medium",
                    },
                ],
            }
            path = root / "absolute-scale.json"
            write_json(path, contract)
            report = TOOLS.validate_scene_absolute_scale(
                path, root / "absolute-scale-report.json", root / "absolute-scale.png"
            )
            self.assertEqual(report["status"], "pass")
            contract["actors"][0]["standingEquivalentHeightPx"] = 200
            write_json(path, contract)
            with self.assertRaisesRegex(ValueError, "recommendedGlobalScaleFactor=0.8500"):
                TOOLS.validate_scene_absolute_scale(path)

    def test_final_gaze_conformance_rejects_wrong_side(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            contract = {
                "schema": "ndc-gaze-conformance/v1",
                "sceneSize": [240, 200],
                "actors": [
                    {
                        "actorId": "Lula",
                        "poseId": "lula-v1",
                        "eyeCenter": [100, 60],
                        "directionPoint": [120, 60],
                        "gazeTarget": {"type": "actor", "id": "Zack"},
                        "targetPoint": [180, 65],
                        "maxAngularDeviationDeg": 12,
                    }
                ],
            }
            path = root / "gaze.json"
            write_json(path, contract)
            self.assertEqual(TOOLS.validate_gaze_conformance(path)["status"], "pass")
            contract["actors"][0]["directionPoint"] = [80, 60]
            write_json(path, contract)
            with self.assertRaisesRegex(ValueError, "GAZE_CONFORMANCE_FAILED"):
                TOOLS.validate_gaze_conformance(path)

    def test_component_policy_keeps_fixed_chair_out_of_actor_layer(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            Image.new("L", (20, 20), 255).save(root / "old-mask.png")
            Image.new("L", (20, 20), 255).save(root / "new-mask.png")
            Image.new("RGB", (20, 20), "black").save(root / "scene.png")
            contract = {
                "schema": "ndc-interaction-component-policy/v1",
                "sourceScene": "scene.png",
                "structuralSceneObjectIds": ["chair-1"],
                "layers": [
                    {
                        "layerId": "actor",
                        "kind": "actor",
                        "contentObjectIds": ["Zack", "note"],
                        "sourcePolicy": "generated-contextual-rgb",
                    },
                    {
                        "layerId": "blanket-repair",
                        "kind": "loose-prop-source-repair",
                        "contentObjectIds": ["blanket"],
                        "sourcePolicy": "bounded-scene-repair",
                    },
                    {
                        "layerId": "blanket-new",
                        "kind": "loose-prop-relocated",
                        "contentObjectIds": ["blanket"],
                        "sourcePolicy": "generated-contextual-rgb",
                    },
                    {
                        "layerId": "chair-occluder",
                        "kind": "source-occluder",
                        "contentObjectIds": ["chair-1"],
                        "sourcePolicy": "exact-source-pixels",
                        "uniformScale": 1,
                    },
                ],
                "relocations": [
                    {
                        "objectId": "blanket",
                        "sourceRepairLayerId": "blanket-repair",
                        "destinationLayerId": "blanket-new",
                        "originalRegionMask": "old-mask.png",
                        "destinationRegionMask": "new-mask.png",
                    }
                ],
            }
            path = root / "component.json"
            write_json(path, contract)
            self.assertEqual(TOOLS.validate_component_policy(path)["status"], "pass")
            contract["layers"][0]["contentObjectIds"].append("chair-1")
            write_json(path, contract)
            with self.assertRaisesRegex(ValueError, "fixed structural objects"):
                TOOLS.validate_component_policy(path)

    def test_ui_safety_uses_reference_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = Image.new("RGB", (200, 100), "white")
            right = Image.new("RGB", (200, 100), "white")
            ImageDraw.Draw(left).rectangle((0, 0, 60, 99), fill="black")
            ImageDraw.Draw(right).rectangle((140, 0, 199, 99), fill="black")
            left.save(root / "left.png")
            right.save(root / "right.png")
            contract = {
                "schema": "ndc-ui-safety/v1",
                "sceneSize": [200, 100],
                "uiReferences": {"left": "left.png", "right": "right.png"},
                "limits": {"maxHeadOcclusionRatio": 0, "maxActionOcclusionRatio": 0},
                "actors": [
                    {"actorId": "A", "uiSide": "left", "headBBox": [80, 10, 110, 40], "actionBBox": [75, 5, 120, 90], "criticalPoints": [{"name": "hand", "point": [100, 50]}]}
                ],
            }
            path = root / "ui.json"
            write_json(path, contract)
            report = TOOLS.validate_ui_safety(path)
            self.assertEqual(report["status"], "pass")
            contract["actors"][0]["headBBox"] = [10, 10, 50, 40]
            write_json(path, contract)
            with self.assertRaisesRegex(ValueError, "UI safety failed"):
                TOOLS.validate_ui_safety(path)

    def test_ui_safety_ignores_transparent_padding_rgb(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
            right = Image.new("RGBA", (200, 100), (255, 255, 255, 0))
            ImageDraw.Draw(left).rectangle((0, 0, 60, 99), fill=(0, 0, 0, 255))
            ImageDraw.Draw(right).rectangle((140, 0, 199, 99), fill=(0, 0, 0, 255))
            left.save(root / "left.png")
            right.save(root / "right.png")
            contract = {
                "schema": "ndc-ui-safety/v1",
                "sceneSize": [200, 100],
                "uiReferences": {"left": "left.png", "right": "right.png"},
                "limits": {"maxHeadOcclusionRatio": 0, "maxActionOcclusionRatio": 0},
                "actors": [
                    {"actorId": "A", "uiSide": "left", "headBBox": [80, 10, 110, 40], "actionBBox": [75, 5, 120, 90], "criticalPoints": [{"name": "hand", "point": [100, 50]}]}
                ],
            }
            path = root / "ui.json"
            write_json(path, contract)
            report = TOOLS.validate_ui_safety(path)
            self.assertEqual(report["status"], "pass")

    def test_exploration_complete_state_outputs_review_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            idle = Image.new("RGBA", (100, 120), (0, 0, 0, 0))
            active = Image.new("RGBA", (100, 120), (0, 0, 0, 0))
            ImageDraw.Draw(idle).ellipse((30, 20, 70, 115), fill=(80, 110, 150, 255))
            ImageDraw.Draw(active).ellipse((25, 15, 75, 115), fill=(100, 125, 155, 255))
            idle.save(root / "idle.png")
            active.save(root / "active.png")
            contract = {
                "schema": "ndc-exploration-state-pair/v1",
                "interactionType": "exploration-click-pair",
                "assemblyMode": "registered-complete-state",
                "assetCanvasSize": [100, 120],
                "idleAttentionTarget": "scene-object",
                "activeAttentionTarget": "player",
                "supportAnchors": [{"name": "feet", "idle": [50, 115], "active": [50, 115], "tolerancePx": 1}],
                "maxAlphaSupportDriftPx": 1,
                "reuseMasterTransform": True,
                "statesIndependentlyNormalized": False,
                "stateDeltaScope": {
                    "regions": ["whole-body"],
                    "wholeBodyAuthorized": True,
                    "reason": "test fixture uses a registered complete state",
                },
                "visualReview": {
                    "reviewAuthority": "codex-self-check",
                    "identityContinuity": "pass",
                    "supportAndShadowContinuity": "pass",
                    "stateReadability": "pass",
                    "edgeContinuity": "pass",
                    "flicker": "pass",
                },
            }
            path = root / "states.json"
            write_json(path, contract)
            output = root / "review"
            report = TOOLS.verify_exploration_states(path, root / "idle.png", root / "active.png", output)
            self.assertEqual(report["status"], "pass")
            self.assertTrue((output / "state-flicker.gif").exists())
            self.assertTrue((output / "state-report.json").exists())

    def test_timeline_board(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            Image.new("RGB", (160, 100), "white").save(root / "left.png")
            Image.new("RGB", (160, 100), "white").save(root / "right.png")
            Image.new("RGBA", (160, 100), (40, 50, 60, 255)).save(root / "frame.png")
            contract = {
                "schema": "ndc-timeline-board/v1",
                "sceneSize": [160, 100],
                "uiReferences": {"left": "left.png", "right": "right.png"},
                "snapshots": [{"id": "beat-01", "image": "frame.png", "uiSide": "left", "caption": "A holds; B has not entered"}],
            }
            path = root / "board.json"
            write_json(path, contract)
            output = root / "board"
            TOOLS.render_timeline_board(path, output)
            self.assertTrue((output / "timeline-contact-sheet.png").exists())

    def test_automatic_blocking_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            Image.new("RGBA", (320, 200), (55, 62, 70, 255)).save(root / "scene.png")
            ui = Image.new("RGB", (320, 200), "white")
            ImageDraw.Draw(ui).rectangle((0, 0, 70, 199), fill="black")
            ui.save(root / "left.png")
            affordance = {
                "schema": "ndc-scene-affordance/v1",
                "sceneSize": [320, 200],
                "zones": [{"id": "stand-1", "polygon": [[90, 45], [300, 45], [300, 195], [90, 195]], "capabilities": ["stand"], "depthClass": "midground"}],
                "placements": [],
            }
            write_json(root / "affordance.json", affordance)
            request = {
                "schema": "ndc-blocking-request/v1",
                "scene": "scene.png",
                "sceneSize": [320, 200],
                "actorId": "A",
                "placementClass": "standing",
                "standingEquivalentHeightPx": 120,
                "affordanceContract": "affordance.json",
                "zoneId": "stand-1",
                "posePresets": ["attentive-task", "guarded-hold", "reach-target"],
                "facing": "right",
                "gazePoint": [270, 70],
                "actionTarget": [270, 100],
                "uiSide": "left",
                "uiReferences": {"left": "left.png"},
                "performance": {
                    "action": "reach for the chart",
                    "gazeTarget": {"type": "scene-object", "id": "chart"},
                    "leftHandAction": "balances body",
                    "rightHandAction": "reaches toward chart",
                    "supportObject": "floor-1",
                    "beatEnergy": "medium",
                    "silentFrameVerb": "check",
                    "ongoingOccupation": "checks the chart beside the bed",
                    "performanceFamily": "ongoing-occupation",
                    "gestureMotivation": {"leftHand": "balances weight", "rightHand": "touches chart"},
                    "namedSupport": "floor-1",
                    "socialTerritory": "bedside work zone",
                    "tenSecondHold": "pass",
                    "depthHonesty": "pass",
                    "requiredProps": [],
                },
                "maxCandidates": 4,
            }
            write_json(root / "request.json", request)
            output = root / "blocking"
            report = TOOLS.build_blocking_candidates(root / "request.json", output)
            self.assertEqual(report["candidateCount"], 4)
            self.assertTrue((output / "blocking-candidates.png").exists())
            candidate = json.loads((output / "candidate-01.json").read_text(encoding="utf-8"))
            self.assertEqual(candidate["schema"], "ndc-auto-blocking-candidate/v1")
            self.assertIn("standingPose", candidate["target"])
            self.assertEqual(candidate["target"]["poseDefinition"]["silentFrameVerb"], "check")

    def test_prepare_local_generation_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            Image.new("RGBA", (320, 200), (30, 40, 50, 255)).save(root / "scene.png")
            whitebox = Image.new("RGBA", (320, 200), (30, 40, 50, 255))
            ImageDraw.Draw(whitebox).rectangle((120, 40, 180, 180), fill=(220, 220, 220, 255))
            whitebox.save(root / "whitebox.png")
            Image.new("RGBA", (100, 160), (80, 90, 100, 255)).save(root / "card.png")
            contract = {
                "schema": "ndc-local-generation-handoff/v1",
                "actorId": "A",
                "poseId": "A-hold-v1",
                "scene": "scene.png",
                "whiteboxComposite": "whitebox.png",
                "characterCard": "card.png",
                "actorBBox": [120, 40, 180, 180],
                "cropPaddingPx": 20,
                "generationAspectRatio": [4, 5],
                "outputMode": "contextual-local-replacement",
                "generationPrompt": "Replace only the reviewed whitebox with A.",
            }
            write_json(root / "handoff.json", contract)
            output = root / "handoff"
            report = TOOLS.prepare_local_generation_handoff(root / "handoff.json", output)
            self.assertEqual(report["cropBBox"], [78, 20, 222, 200])
            self.assertEqual(report["actorBBoxLocal"], [42, 20, 102, 160])
            self.assertEqual(report["cropPolicy"], "expand-original-pixels-no-resize")
            self.assertEqual(report["status"], "READY_FOR_CONTEXTUAL_LOCAL_GENERATION")
            self.assertTrue((output / "image-1-local-whitebox.png").exists())
            self.assertTrue((output / "local-generation-handoff.json").exists())
            contract["outputMode"] = "isolated-transparent-character"
            write_json(root / "handoff.json", contract)
            with self.assertRaisesRegex(ValueError, "contextual-local-replacement"):
                TOOLS.prepare_local_generation_handoff(root / "handoff.json", output)

    def test_project_asset_baseline_and_diff(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            asset_root = root / "Resources"
            npc_dir = asset_root / "Art" / "Scene" / "NPC"
            backgrounds = root / "Backgrounds"
            npc_dir.mkdir(parents=True)
            backgrounds.mkdir()
            idle = Image.new("RGBA", (40, 60), (0, 0, 0, 0))
            active = idle.copy()
            ImageDraw.Draw(idle).rectangle((10, 10, 30, 58), fill=(10, 20, 30, 255))
            ImageDraw.Draw(active).rectangle((8, 8, 32, 58), fill=(20, 30, 40, 255))
            idle.save(npc_dir / "a_idle.png")
            active.save(npc_dir / "a_active.png")
            Image.new("RGB", (160, 100), "gray").save(backgrounds / "scene.png")
            left = Image.new("RGB", (160, 100), "white")
            right = left.copy()
            ImageDraw.Draw(left).rectangle((0, 0, 30, 99), fill="black")
            ImageDraw.Draw(right).rectangle((130, 0, 159, 99), fill="black")
            left.save(root / "left.png")
            right.save(root / "right.png")
            table = root / "NPCLoopData.json"
            table.write_text(
                """[{\n\t\"id\" : \"10\",\n\t\"NPC\" : {\n\t\"id\" : \"1\",\n\t\"Name\" : [\"A\",\"A\"]\n},\n\t\"ResPath\" : \"Art\\Scene\\NPC\\a_idle\",\n\t\"ClickResPath\" : \"Art\\Scene\\NPC\\a_active\",\n\t\"PosX\" : \"1\",\n\t\"Posy\" : \"2\",\n\t\"PosZ\" : \"3\"\n}]""",
                encoding="utf-8",
            )
            report = TOOLS.audit_project_assets(table, asset_root, backgrounds, root / "left.png", root / "right.png", None)
            self.assertEqual(report["summary"]["distinctStatePairCount"], 1)
            baseline = root / "baseline.json"
            write_json(baseline, report)
            unchanged = TOOLS.audit_project_assets(table, asset_root, backgrounds, root / "left.png", root / "right.png", baseline)
            self.assertEqual(unchanged["baselineComparison"]["status"], "unchanged")
            ImageDraw.Draw(active).ellipse((0, 0, 5, 5), fill=(255, 0, 0, 255))
            active.save(npc_dir / "a_active.png")
            changed = TOOLS.audit_project_assets(table, asset_root, backgrounds, root / "left.png", root / "right.png", baseline)
            self.assertEqual(changed["baselineComparison"]["status"], "changed")

    def test_pose_editor_contract_markers(self) -> None:
        editor = SCRIPT_PATH.with_name("pose_blocking_editor.html").read_text(encoding="utf-8")
        for marker in ("poseDefinition", "affordanceZoneId", "gazeTarget", "supportObject"):
            self.assertIn(marker, editor)


if __name__ == "__main__":
    unittest.main()
