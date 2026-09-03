from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_avg_cast_plan.py"
SPEC = importlib.util.spec_from_file_location("validate_avg_cast_plan", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_png(path: Path, width: int, height: int, rgba: tuple[int, int, int, int]) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    row = b"\x00" + bytes(rgba) * width
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(row * height))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ValidateAvgCastPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.files: dict[str, str] = {}
        for index, name in enumerate(
            (
                "scene.png",
                "ui.png",
                "combined.png",
                "a-card.png",
                "b-card.png",
                "c-card.png",
                "a-isolated.png",
                "b-isolated.png",
                "c-isolated.png",
                "ui-preview.png",
                "scene-scale-preview.png",
                "whitebox-review.png",
                "a-support.png",
                "b-support.png",
                "c-support.png",
            )
        ):
            path = self.root / name
            write_png(path, 240, 200, (30 + index, 40 + index, 50 + index, 255))
            self.files[name] = str(path)

        for name in ("a.md", "b.md", "c.md"):
            path = self.root / name
            path.write_text("height canon", encoding="utf-8")
            self.files[name] = str(path)

        for name in (
            "timeline-report.json",
            "ui-report.json",
            "scene-scale-contract.json",
            "scene-scale-report.json",
            "cast-scale-contract.json",
            "cast-scale-report.json",
            "whitebox-review.json",
            "a-support-report.json",
            "b-support-report.json",
            "c-support-report.json",
        ):
            path = self.root / name
            path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
            self.files[name] = str(path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _hashed(self, name: str) -> str:
        return sha256(Path(self.files[name]))

    def _review(
        self,
        report: str,
        *,
        preview: str | None = None,
        contract: str | None = None,
        status: str = "PASS",
    ) -> dict:
        value = {
            "report": self.files[report],
            "reportSha256": self._hashed(report),
            "status": status,
        }
        if preview:
            value["preview"] = self.files[preview]
        if contract:
            value["contract"] = self.files[contract]
        return value

    def _actor(
        self,
        actor_id: str,
        prefix: str,
        color: str,
        *,
        height: int,
        back: bool = False,
    ) -> dict:
        return {
            "actorId": actor_id,
            "name": actor_id,
            "presenceAtSnapshot": "already-present",
            "characterCard": self.files[f"{prefix}-card.png"],
            "characterCardSha256": self._hashed(f"{prefix}-card.png"),
            "canonicalHeightCm": height,
            "canonicalHeightSource": self.files[f"{prefix}.md"],
            "canonicalHeightSourceSha256": self._hashed(f"{prefix}.md"),
            "identityScaleReference": {
                "referenceFullBodyHeightPx": 180,
                "referenceAnatomicalHeadHeightPx": 22,
                "bodyBuild": "identity-specific body build",
                "headToBodyNotes": "preserve approved card proportions",
            },
            "whiteboxColor": color,
            "isolatedWhitebox": self.files[f"{prefix}-isolated.png"],
            "isolatedWhiteboxSha256": self._hashed(f"{prefix}-isolated.png"),
            "whiteboxCanvasSize": [240, 200],
            "depthClass": "foreground" if back else "midground",
            "framing": "half-body" if back else "full-body",
            "backFacing": back,
            "feetVisible": not back,
            "poseFamily": "standing-three-quarter-back" if back else "standing-alert",
            "seatedJustification": "",
            "facing": "screen-left",
            "gazeTarget": "NPC-A" if actor_id != "NPC-A" else "NPC-B",
            "support": "scene:off-frame-floor" if back else "scene:floor",
            "supportPoint": [120, 190],
            "anchor": "head-and-frame-edge" if back else "feet-bottom-center",
            "standingEquivalentHeightPx": 170,
            "poseLandmarks": {
                "headBox": [105, 10, 135, 40],
                "neck": [120, 45],
                "leftShoulder": [100, 50],
                "rightShoulder": [140, 50],
                "leftElbow": [95, 80],
                "rightElbow": [145, 80],
                "leftHand": [100, 105],
                "rightHand": [140, 105],
                "hipCenter": [120, 115],
                "leftKnee": [108, 150],
                "rightKnee": [132, 150],
                "leftFoot": [108, 190],
                "rightFoot": [132, 190],
                "outerBBox": [90, 10, 150, 195],
            },
            "performance": {
                "silentFrameVerb": "contains",
                "beatEnergy": "controlled pressure",
                "ongoingOccupation": "holds position during the negotiation",
                "performanceFamily": "restrained pressure",
                "action": "holds a stable position",
                "emotion": "contained tension",
                "facialExpression": "alert with restrained jaw tension",
                "bodyLine": "upright diagonal",
                "weightDistribution": "balanced over support",
                "leftHandMotivation": "guards personal space",
                "rightHandMotivation": "rests without reaching",
                "namedSupport": "scene:off-frame-floor" if back else "scene:floor",
                "socialTerritory": "separate readable silhouette",
                "actionFocus": "the opposing actor",
                "subtext": "refuses to give ground",
                "costumeState": "approved card costume remains intact",
                "propContinuity": "holds no prop at this snapshot",
                "depthHonesty": "scale follows the named floor support",
                "tenSecondHold": True,
            },
            "supportContactReview": self._review(
                f"{prefix}-support-report.json", preview=f"{prefix}-support.png"
            ),
            "prop": None,
        }

    def _plan(self) -> dict:
        return {
            "schema": "ndc-multichar-avg-plan/v2",
            "stage": "whitebox-approved",
            "sceneId": "SC-test",
            "sceneKind": "static-multichar-avg",
            "sourceScene": self.files["scene.png"],
            "sourceSceneSha256": self._hashed("scene.png"),
            "sceneSize": [240, 200],
            "castClusterSide": "right",
            "uiSide": "left",
            "uiReference": self.files["ui.png"],
            "uiReferenceSha256": self._hashed("ui.png"),
            "uiPlacement": {"canvasSize": [240, 200], "topLeft": [0, 0], "mirrorX": False},
            "timelineReview": {
                "snapshotId": "beat-01",
                **self._review("timeline-report.json"),
            },
            "uiSafetyReview": {
                **self._review("ui-report.json", preview="ui-preview.png"),
                "protectedRegions": ["headBox", "leftHand", "rightHand", "ownedProp", "actionFocus"],
                "maxHeadOverlapRatio": 0.0,
                "maxCriticalOverlapRatio": 0.0,
            },
            "silentFrameStatement": "One suspect is boxed in while two investigators control the exit.",
            "combinedWhitebox": self.files["combined.png"],
            "combinedWhiteboxSha256": self._hashed("combined.png"),
            "actorContacts": [],
            "sceneAbsoluteScaleReview": {
                **self._review(
                    "scene-scale-report.json",
                    preview="scene-scale-preview.png",
                    contract="scene-scale-contract.json",
                ),
                "projectionModel": "single-horizon floor-plane projection",
                "horizonY": 50,
                "anchorGroups": [
                    {
                        "id": "sofa",
                        "scope": "cross-depth",
                        "depthBand": "near",
                        "measuredAxes": ["horizontal", "vertical"],
                        "confidence": "medium",
                        "measurementLines": [
                            {
                                "axis": "horizontal",
                                "start": [10, 150],
                                "end": [80, 150],
                                "realWorldRangeCm": [180, 230],
                                "assumption": "three-seat sofa",
                            },
                            {
                                "axis": "vertical",
                                "start": [10, 100],
                                "end": [10, 150],
                                "realWorldRangeCm": [75, 100],
                                "assumption": "floor-to-back height",
                            },
                        ],
                    },
                    {
                        "id": "bookcase",
                        "scope": "actor-local",
                        "depthBand": "mid",
                        "measuredAxes": ["horizontal", "vertical"],
                        "confidence": "high",
                        "measurementLines": [
                            {
                                "axis": "horizontal",
                                "start": [150, 80],
                                "end": [200, 80],
                                "realWorldRangeCm": [75, 105],
                                "assumption": "single cabinet bay",
                            },
                            {
                                "axis": "vertical",
                                "start": [150, 30],
                                "end": [150, 180],
                                "realWorldRangeCm": [210, 260],
                                "assumption": "floor-standing bookcase",
                            },
                        ],
                    },
                    {
                        "id": "window",
                        "scope": "cross-depth",
                        "depthBand": "far",
                        "measuredAxes": ["vertical"],
                        "confidence": "medium",
                        "measurementLines": [
                            {
                                "axis": "vertical",
                                "start": [110, 20],
                                "end": [110, 120],
                                "realWorldRangeCm": [220, 300],
                                "assumption": "architectural span",
                            }
                        ],
                    },
                ],
            },
            "castScaleReview": {
                **self._review("cast-scale-report.json", contract="cast-scale-contract.json"),
                "headScalePriority": True,
                "maxDeviationRatio": 0.03,
                "maxHeadDeviationRatio": 0.05,
            },
            "whiteboxVisualReview": {
                **self._review("whitebox-review.json", preview="whitebox-review.png"),
                "wholeFrameZoomPercent": 100,
                "localZoomPercent": 200,
            },
            "occlusionGraph": {
                "pairwise": [
                    {"actors": ["NPC-A", "NPC-B"], "relation": "no-overlap"},
                    {"actors": ["NPC-A", "NPC-C"], "relation": "second-in-front"},
                    {"actors": ["NPC-B", "NPC-C"], "relation": "second-in-front"},
                ],
                "sceneOccluders": [],
            },
            "outputPsd": str(self.root / "final.psd"),
            "outputPng": str(self.root / "final.png"),
            "actors": [
                self._actor("NPC-A", "a", "#D68A28", height=181),
                self._actor("NPC-B", "b", "#9B4DCC", height=183),
                self._actor("NPC-C", "c", "#2D9BCB", height=180, back=True),
            ],
        }

    def assert_error_contains(self, plan: dict, fragment: str) -> None:
        errors, _warnings = MODULE.validate_plan(plan)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_valid_three_actor_whitebox_plan(self) -> None:
        errors, warnings = MODULE.validate_plan(self._plan())
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_blocking_allows_declared_pending_whitebox_reviews(self) -> None:
        plan = self._plan()
        plan["stage"] = "blocking"
        for field in ("uiSafetyReview", "sceneAbsoluteScaleReview", "castScaleReview", "whiteboxVisualReview"):
            plan[field]["status"] = "PENDING"
        for actor in plan["actors"]:
            actor["supportContactReview"]["status"] = "PENDING"
        errors, warnings = MODULE.validate_plan(plan)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_legacy_v1_fails(self) -> None:
        plan = self._plan()
        plan["schema"] = "ndc-multichar-avg-plan/v1"
        self.assert_error_contains(plan, "migrate legacy v1")

    def test_canonical_height_is_required(self) -> None:
        plan = self._plan()
        del plan["actors"][1]["canonicalHeightCm"]
        self.assert_error_contains(plan, "canonicalHeightCm")

    def test_identity_head_scale_is_required(self) -> None:
        plan = self._plan()
        del plan["actors"][0]["identityScaleReference"]["referenceAnatomicalHeadHeightPx"]
        self.assert_error_contains(plan, "referenceAnatomicalHeadHeightPx")

    def test_real_ui_reference_hash_is_required(self) -> None:
        plan = self._plan()
        plan["uiReferenceSha256"] = "0" * 64
        self.assert_error_contains(plan, "uiReferenceSha256 does not match")

    def test_ui_placement_must_use_scene_canvas(self) -> None:
        plan = self._plan()
        plan["uiPlacement"]["canvasSize"] = [200, 200]
        self.assert_error_contains(plan, "uiPlacement.canvasSize must equal sceneSize")

    def test_ui_protected_regions_are_required(self) -> None:
        plan = self._plan()
        plan["uiSafetyReview"]["protectedRegions"].remove("actionFocus")
        self.assert_error_contains(plan, "protectedRegions must include")

    def test_three_absolute_scale_anchors_are_required(self) -> None:
        plan = self._plan()
        plan["sceneAbsoluteScaleReview"]["anchorGroups"] = plan["sceneAbsoluteScaleReview"]["anchorGroups"][:2]
        self.assert_error_contains(plan, "at least three groups")

    def test_absolute_scale_requires_both_scopes(self) -> None:
        plan = self._plan()
        for anchor in plan["sceneAbsoluteScaleReview"]["anchorGroups"]:
            anchor["scope"] = "cross-depth"
        self.assert_error_contains(plan, "actor-local and cross-depth")

    def test_absolute_scale_requires_measurement_lines(self) -> None:
        plan = self._plan()
        del plan["sceneAbsoluteScaleReview"]["anchorGroups"][0]["measurementLines"]
        self.assert_error_contains(plan, "measurementLines must be a non-empty array")

    def test_head_scale_priority_is_mandatory(self) -> None:
        plan = self._plan()
        plan["castScaleReview"]["headScalePriority"] = False
        self.assert_error_contains(plan, "headScalePriority must be true")

    def test_pose_landmark_is_required(self) -> None:
        plan = self._plan()
        del plan["actors"][0]["poseLandmarks"]["leftHand"]
        self.assert_error_contains(plan, "poseLandmarks.leftHand")

    def test_named_support_must_match_actor_support(self) -> None:
        plan = self._plan()
        plan["actors"][0]["performance"]["namedSupport"] = "scene:wrong-floor"
        self.assert_error_contains(plan, "performance.namedSupport must equal")

    def test_every_actor_pair_needs_occlusion_decision(self) -> None:
        plan = self._plan()
        plan["occlusionGraph"]["pairwise"].pop()
        self.assert_error_contains(plan, "missing actor pairs")

    def test_isolated_whitebox_canvas_must_match_scene(self) -> None:
        plan = self._plan()
        plan["actors"][0]["whiteboxCanvasSize"] = [200, 200]
        self.assert_error_contains(plan, "whiteboxCanvasSize must equal sceneSize")

    def test_duplicate_colors_fail(self) -> None:
        plan = self._plan()
        plan["actors"][1]["whiteboxColor"] = plan["actors"][0]["whiteboxColor"]
        self.assert_error_contains(plan, "distinct whiteboxColor")

    def test_three_actors_require_a_back_facing_actor(self) -> None:
        plan = self._plan()
        plan["actors"][2]["backFacing"] = False
        self.assert_error_contains(plan, "require at least one back-facing actor")

    def test_back_facing_actor_hides_feet(self) -> None:
        plan = self._plan()
        plan["actors"][2]["feetVisible"] = True
        self.assert_error_contains(plan, "feetVisible=false")

    def test_prop_handoff_fails(self) -> None:
        plan = self._plan()
        plan["actors"][0]["prop"] = {
            "id": "sealed-envelope",
            "ownership": "held",
            "hand": "right",
            "handoff": True,
        }
        self.assert_error_contains(plan, "prop.handoff must be false")


if __name__ == "__main__":
    unittest.main()
