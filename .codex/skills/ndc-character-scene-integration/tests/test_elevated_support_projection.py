"""Regression tests for lying actors on elevated support planes."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene_staging_tools as tools
import visual_review_gate as visual
import test_scene_staging_tools as existing_tests


class ElevatedSupportProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scene = self.root / "scene.png"
        self.card = self.root / "card.png"
        Image.new("RGB", (240, 200), (35, 45, 55)).save(self.scene)
        Image.new("RGB", (120, 200), (230, 230, 225)).save(self.card)

        fixture = existing_tests.SceneStagingToolTests()
        self.actor_a = fixture._placement_contract(self.root, self.scene)
        self.actor_a["target"]["supportPlaneId"] = "floor"
        self.actor_a_path = self.write("actor-a.json", self.actor_a)

        self.actor_b = copy.deepcopy(self.actor_a)
        self.actor_b["characterName"] = "B"
        self.actor_b["target"] = {
            "placementClass": "lying",
            "affordanceZoneId": "lie-bed-1",
            "supportPlaneId": "bed-mattress",
            "supportPlaneClass": "elevated",
            "foot": [110, 120],
            "standingEquivalentHeightPx": 170,
            "visibleHeightPx": 80,
            "outerBBox": [20, 50, 220, 150],
            "poseDefinition": {
                "poseId": "b-lying-v1",
                "action": "rests on bed",
                "facing": "right",
                "gazeTarget": "ceiling",
                "leftHandAction": "rests on blanket",
                "rightHandAction": "rests beside torso",
                "requiredProps": [],
            },
            "lyingPose": {
                "headBox": [30, 70, 47, 87],
                "headAxis": {
                    "crown": [38.5, 70],
                    "chin": [38.5, 87],
                    "measurementEvidence": "Synthetic exact-pose fixture.",
                    "projectionReview": "Synthetic in-plane axis with no foreshortening claim.",
                },
            },
            "sceneRelations": [
                {
                    "objectId": "bed-1",
                    "relation": "supported-by",
                    "regions": ["back", "pelvis", "legs"],
                    "reason": "body rests on mattress",
                }
            ],
        }
        self.actor_b_path = self.write("actor-b.json", self.actor_b)
        self.identity = {
            "referenceArtifact": str(self.card),
            "referenceFullBodyHeightPx": 170,
            "referenceAnatomicalHeadHeightPx": 17,
            "measurementMethod": "synthetic-approved-card",
            "confidence": "high",
        }

    def write(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def ref(self, path: Path) -> dict:
        return {"path": str(path), "sha256": tools.sha256(path)}

    def review(self, include_elevated_checks: bool = True) -> tuple[Path, Path, Path]:
        whole = self.root / "whole-whitebox.png"
        local = self.root / "local-whitebox.png"
        tile = self.root / "whole-local-200.png"
        Image.new("RGB", (240, 200), (80, 70, 65)).save(whole)
        Image.new("RGB", (200, 120), (90, 80, 75)).save(local)
        Image.new("RGB", (200, 220), (100, 90, 85)).save(tile)
        checks = {name: "pass" for name in visual.STAGE_CHECKS["exact-pose-whitebox"]}
        if include_elevated_checks:
            checks.update(
                {
                    "elevatedSupportPlane": "pass",
                    "projectedGroundDepth": "pass",
                    "wholeLocalConsistency": "pass",
                }
            )
        review_contract = {
            "schema": "ndc-stage-visual-review/v1",
            "stage": "exact-pose-whitebox",
            "reviewAuthority": "codex-self-check",
            "decision": "pass",
            "artifacts": [
                {"role": "whole-scene-lying-whitebox", **self.ref(whole), "poseIds": ["b-lying-v1"], "snapshotIds": ["shot-1"]},
                {"role": "local-lying-whitebox", **self.ref(local), "poseIds": ["b-lying-v1"], "snapshotIds": ["shot-1"]},
            ],
            "localTiles": [
                {"id": "bed-contact-200", "bbox": [20, 40, 120, 150], **self.ref(tile)}
            ],
            "checks": checks,
            "observations": ["Synthetic fixture verifies evidence binding only; it is not art approval."],
        }
        review_contract_path = self.write("review-contract.json", review_contract)
        out = self.root / "review"
        visual.build_review(review_contract_path, out)
        return whole, local, out / "exact-pose-whitebox-visual-review-report.json"

    def projection(self, mode: str = "projected-ground-plane", include_elevated_checks: bool = True) -> Path:
        whole, local, report = self.review(include_elevated_checks)
        support_evidence = self.root / "support-plane-evidence.png"
        depth_evidence = self.root / "ground-depth-evidence.png"
        Image.new("RGB", (240, 200), (10, 80, 120)).save(support_evidence)
        Image.new("RGB", (240, 200), (120, 80, 10)).save(depth_evidence)
        depth = {
            "mode": mode,
            "evidence": self.ref(depth_evidence),
            "perspectiveBasisIds": ["floor-grid-1", "bed-leg-drop-1"],
        }
        if mode == "projected-ground-plane":
            depth["projectedGroundPoint"] = [110, 185]
        else:
            depth["referenceActorId"] = "A"
        data = {
            "schema": "ndc-elevated-support-projection/v1",
            "scene": self.ref(self.scene),
            "sceneSize": [240, 200],
            "actorId": "B",
            "poseId": "b-lying-v1",
            "placementContract": self.ref(self.actor_b_path),
            "supportPlane": {
                "supportPlaneId": "bed-mattress",
                "supportObjectId": "bed-1",
                "supportPoint": [110, 120],
                "evidence": self.ref(support_evidence),
            },
            "depthProjection": depth,
            "wholeArtifact": self.ref(whole),
            "localArtifact": self.ref(local),
            "visualReviewReport": self.ref(report),
        }
        return self.write("projection.json", data)

    def cast(self, schema: str, projection: Path | None = None) -> Path:
        actors = [
            {
                "actorId": "A",
                "placementContract": str(self.actor_a_path),
                "identityScaleReference": self.identity,
            },
            {
                "actorId": "B",
                "placementContract": str(self.actor_b_path),
                "identityScaleReference": self.identity,
            },
        ]
        if schema == "ndc-cast-scale/v3":
            actors[0]["depthProjection"] = {"mode": "ground-support-point"}
            actors[1]["depthProjection"] = {
                "mode": "elevated-support-projection",
                "contract": self.ref(projection),
            }
        return self.write(
            "cast.json",
            {
                "schema": schema,
                "sceneSize": [240, 200],
                "horizonY": 50,
                "referenceActorId": "A",
                "maxDeviationRatio": 0.03,
                "maxHeadDeviationRatio": 0.05,
                "maxPairwiseHeadDeviationRatio": 0.05,
                "headScalePriority": True,
                "actors": actors,
            },
        )

    def test_v3_uses_projected_ground_depth_without_rewriting_authored_support(self) -> None:
        with self.assertRaisesRegex(ValueError, "CAST_SCALE_FAILED"):
            tools.validate_cast_scale(self.cast("ndc-cast-scale/v2"))
        result = tools.validate_cast_scale(
            self.cast("ndc-cast-scale/v3", self.projection())
        )
        lying = next(actor for actor in result["actors"] if actor["actorId"] == "B")
        self.assertEqual(result["schema"], "ndc-cast-scale-report/v3")
        self.assertEqual(lying["supportPoint"], [110, 120])
        self.assertEqual(lying["depthPoint"], [110, 185])
        self.assertEqual(lying["depthSource"], "elevated-support-projection")

    def test_same_depth_reference_is_resolved_without_a_reference_chain(self) -> None:
        result = tools.validate_cast_scale(
            self.cast("ndc-cast-scale/v3", self.projection("same-depth-reference"))
        )
        lying = next(actor for actor in result["actors"] if actor["actorId"] == "B")
        self.assertEqual(lying["depthPoint"], [110, 185])
        self.assertEqual(lying["depthSource"], "same-depth-reference")

    def test_v3_rejects_stale_pose_binding_and_incomplete_visual_evidence(self) -> None:
        projection = self.projection()
        self.actor_b["target"]["poseDefinition"]["poseId"] = "b-lying-v2"
        self.write("actor-b.json", self.actor_b)
        with self.assertRaisesRegex(ValueError, "SHA-256 is stale"):
            tools.validate_cast_scale(self.cast("ndc-cast-scale/v3", projection))

        self.actor_b["target"]["poseDefinition"]["poseId"] = "b-lying-v1"
        self.write("actor-b.json", self.actor_b)
        incomplete = self.projection(include_elevated_checks=False)
        with self.assertRaisesRegex(ValueError, "elevatedSupportPlane=pass"):
            tools.validate_cast_scale(self.cast("ndc-cast-scale/v3", incomplete))

    def test_v3_rejects_lying_ground_mode_without_explicit_ground_plane(self) -> None:
        contract = json.loads(self.cast("ndc-cast-scale/v3", self.projection()).read_text(encoding="utf-8"))
        contract["actors"][1]["depthProjection"] = {"mode": "ground-support-point"}
        path = self.write("cast-ground.json", contract)
        with self.assertRaisesRegex(ValueError, "supportPlaneClass='ground'"):
            tools.validate_cast_scale(path)


if __name__ == "__main__":
    unittest.main()
