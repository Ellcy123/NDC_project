import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from validate_reference_handoff import validate  # noqa: E402
from manual_review_node import approval_for  # noqa: E402
PIPELINE_TESTS = SCRIPTS.parent.parent / "ndc-art-stage-pipeline" / "tests"
sys.path.insert(0, str(PIPELINE_TESTS))
from character_node_fixture import attach_character_node_delivery  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReferenceHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scope = self.root / "scope.json"
        self.scope.write_text(json.dumps({"scope": {"cases": [{"snapshots": [{"actor_pose_ids": {"A": "pose-a"}}]}]}}))
        self.files = []
        for name in ("whitebox.png", "scene.png", "card.png", "review.json", "master.png", "source-index.json", "handoff.md", "names.json", "prompt.md", "joint.png", "ui.png", "workspace.json", "asset-index.json"):
            path = self.root / name
            if path.suffix == ".png":
                mode = "RGBA" if name == "master.png" else "RGB"
                background = (0, 0, 0, 0) if mode == "RGBA" else (20, 30, 40)
                image = Image.new(mode, (256, 256), background)
                draw = ImageDraw.Draw(image)
                variant = sum(name.encode("utf-8")) % 24
                for offset in range(96):
                    color = (40 + offset * 2, 70 + offset, 126 + variant - offset, 255) if mode == "RGBA" else (40 + offset * 2, 70 + offset, 126 + variant - offset)
                    draw.line((80 + offset, 20, 80 + offset, 235), fill=color)
                image.save(path)
            else:
                path.write_bytes(name.encode())
            self.files.append(path)
        self.handoff = self.root / "handoff.json"

    def ref(self, path: Path, role=None):
        value = {"path": str(path), "sha256": digest(path)}
        if role:
            value["role"] = role
        return value

    def data(self, mode="FULL_IN_FRAME"):
        scope_sha = digest(self.scope)
        discovery = {
            "schema": "ndc-asset-discovery-receipt/v1", "status": "CONFIRMED_ABSENT",
            "checked_at": "2026-09-13T12:00:00+08:00",
            "scope": {"domain": "character_scene", "scene_id": "SC1", "revision": 1, "actor_id": "A", "pose_or_state": "pose-a", "artifact_role": "whitebox"},
            "freshness": {"scope_revision_sha256": scope_sha, "asset_index": self.ref(self.files[12])},
            "searches": [{"root_role": role, "root_path": str(self.root), "query_ids": ["A"], "aliases": ["A"], "completed": True} for role in ("official_runtime", "approved_archive", "formal_delivery")],
            "candidates": [],
        }
        discovery_path = self.root / "discovery.json"; discovery_path.write_text(json.dumps(discovery))
        anatomy = {part: True for part in (
            "head", "neck", "torso", "pelvis", "left_arm", "right_arm", "left_hand", "right_hand",
            "left_leg", "right_leg", "left_foot", "right_foot")}
        absent = {key: True for key in (
            "stick_or_joint_figure", "programmatic_geometry_blocks", "flat_color_silhouette",
            "technical_ruler", "combined_scene_preview_as_master")}
        node = {
            "schema": "ndc-manual-review-node/v1", "status": "NODE_DELIVERABLE_READY", "node_id": "SC1-r1-node",
            "unit": "Unit1", "domain": "character_scene", "scene_id": "SC1", "revision": 1, "created_at": "2026-09-13T12:00:00+08:00",
            "scope": self.ref(self.scope), "source_index": self.ref(self.files[5]), "handoff_document": self.ref(self.files[6]),
            "naming_table": self.ref(self.files[7]), "web_prompt": self.ref(self.files[8]),
            "deliverables": {
                "production_whiteboxes": [{
                    "actor_id": "A", "pose_id": "pose-a", "anatomy_mode": mode,
                    "whitebox_kind": "3d-anatomical-mannequin-exact-pose",
                    "complete_anatomy_master": self.ref(self.files[4]),
                    "final_submission_whitebox": self.ref(self.files[0]),
                    "final_submission_authority": True,
                    "anatomy_coverage": anatomy,
                    "prohibited_proxy_types_absent": absent,
                    "technical_review": self.ref(self.files[3]),
                    "visual_review": self.ref(self.files[3]),
                    "discovery_receipt": self.ref(discovery_path),
                }],
                "joint_whitebox_preview": self.ref(self.files[9]),
                "actual_ui_clearance_preview": self.ref(self.files[10]),
                "discovery_receipts": [self.ref(discovery_path)],
            },
            "user_review_focus": ["proportion", "narrative_pose", "landing_plausibility", "ui_clearance"],
            "manual_return_workspace": self.ref(self.files[11]),
        }
        if mode == "FRAME_CROPPED_FOREGROUND":
            node_entry = node["deliverables"]["production_whiteboxes"][0]
            node_entry.update(
                visible_anatomy_complete=True,
                natural_frame_exit=True,
                off_frame_scale_support_evidence=[self.ref(self.files[3])],
            )
        node_path = self.root / "node.json"
        attach_character_node_delivery(node, node_path, sys.modules[approval_for.__module__])
        node_path.write_text(json.dumps(node))
        approval_path = self.root / "approval.json"
        approval_path.write_text(json.dumps(approval_for(node_path, "2026-09-13T12:10:00+08:00", "用户明确通过节点")))
        unit = {
            "generation_unit_id": "A-pose-a", "actor_id": "A", "pose_ids": ["pose-a"],
            "anatomy_mode": mode,
            "references": [self.ref(self.files[i], role) for i, role in enumerate(
                ("local-whitebox-crop", "untouched-full-scene", "approved-character-card"))],
            "coverage_evidence": [self.ref(self.files[3])],
            "complete_master": self.ref(self.files[4]),
            "discovery": {"receipt": self.ref(discovery_path), "scope_revision_sha256": scope_sha},
        }
        return {"schema": "ndc-character-scene-reference-handoff/v1", "scene_id": "SC1", "revision": 1,
                "scope": self.ref(self.scope), "source_revision": {"status": "CURRENT", "superseded": False},
                "manual_review_node": self.ref(node_path), "manual_review_approval": self.ref(approval_path),
                "generation_units": [unit]}

    def write(self, data):
        self.handoff.write_text(json.dumps(data))
        return self.handoff

    def test_full_master_ready(self):
        result = validate(self.write(self.data()))
        self.assertEqual(result["status"], "CURRENT")

    def test_parallel_manual_return_branch_does_not_block_mainline_handoff(self):
        data = self.data()
        data["manual_review_branch_mode"] = "PARALLEL_NONBLOCKING"
        data.pop("manual_review_approval")
        result = validate(self.write(data))
        self.assertEqual(result["status"], "CURRENT")
        self.assertEqual(result["manual_review_branch"]["mode"], "PARALLEL_NONBLOCKING")
        self.assertFalse(result["manual_review_branch"]["blocks_mainline"])
        self.assertIsNone(result["manual_review_approval"])

    def test_user_hold_still_requires_explicit_node_approval(self):
        data = self.data()
        data["manual_review_branch_mode"] = "USER_HOLD"
        data.pop("manual_review_approval")
        with self.assertRaisesRegex(ValueError, "manual_review_approval"):
            validate(self.write(data))

    def test_cropped_foreground_needs_visible_and_off_frame_evidence_but_not_feet(self):
        data = self.data("FRAME_CROPPED_FOREGROUND")
        unit = data["generation_units"][0]
        unit.update(natural_frame_exit=True, visible_anatomy_complete=True,
                    off_frame_scale_support_evidence=[self.ref(self.files[3])])
        self.assertEqual(validate(self.write(data))["status"], "CURRENT")
        unit["visible_anatomy_complete"] = False
        with self.assertRaisesRegex(ValueError, "complete visible anatomy"):
            validate(self.write(data))

    def test_three_reference_order_and_full_scope_are_hard(self):
        data = self.data()
        data["generation_units"][0]["references"].reverse()
        with self.assertRaisesRegex(ValueError, "exact order"):
            validate(self.write(data))
        data = self.data()
        data["generation_units"][0]["pose_ids"] = ["wrong-pose"]
        with self.assertRaisesRegex(ValueError, "scope mismatch|differs from frozen scope|no matching whitebox authority"):
            validate(self.write(data))

    def test_superseded_source_never_becomes_ready(self):
        data = self.data()
        data["source_revision"]["superseded"] = True
        with self.assertRaisesRegex(ValueError, "not superseded"):
            validate(self.write(data))

    def test_handoff_must_use_exact_node_whitebox_bytes(self):
        data = self.data()
        replacement = self.root / "other-whitebox.png"
        Image.new("RGB", (256, 256), (50, 60, 70)).save(replacement)
        data["generation_units"][0]["references"][0] = self.ref(replacement, "local-whitebox-crop")
        with self.assertRaisesRegex(ValueError, "exact final_submission_whitebox"):
            validate(self.write(data))


if __name__ == "__main__":
    unittest.main()
