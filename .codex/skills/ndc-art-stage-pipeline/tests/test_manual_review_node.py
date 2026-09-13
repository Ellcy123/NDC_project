import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "manual_review_node.py"
SPEC = importlib.util.spec_from_file_location("manual_review_node", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ManualReviewNodeTests(unittest.TestCase):
    def binding(self, path):
        return {"path": str(path), "sha256": MODULE.sha256(path)}

    def write(self, root, name, content=b"x"):
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content); return path

    def image(self, root, name, *, rgba=False, flat=False):
        path = root / name
        mode = "RGBA" if rgba else "RGB"
        background = (0, 0, 0, 0) if rgba else (20, 30, 40)
        image = Image.new(mode, (256, 256), background)
        draw = ImageDraw.Draw(image)
        variant = sum(name.encode("utf-8")) % 24
        if flat:
            draw.rectangle((80, 20, 175, 235), fill=(80, 140, 200, 255) if rgba else (80, 140, 200))
        else:
            for offset in range(96):
                color = (40 + offset * 2, 70 + offset, 126 + variant - offset, 255) if rgba else (40 + offset * 2, 70 + offset, 126 + variant - offset)
                draw.line((80 + offset, 20, 80 + offset, 235), fill=color)
        image.save(path)
        return path

    def node(self, root):
        scope = self.write(root, "scope.json", json.dumps({"scope": {"cases": [{"snapshots": [{"actor_pose_ids": {"A": "pose-a"}}]}]}}).encode())
        source = self.write(root, "source.json", b"{}")
        handoff = self.write(root, "handoff.md")
        names = self.write(root, "names.json", b"{}")
        prompt = self.write(root, "prompt.md")
        wb = self.image(root, "whitebox-master.png", rgba=True)
        final_submission = self.image(root, "whitebox-final-submission.png")
        joint = self.image(root, "joint.png")
        ui = self.image(root, "ui.png")
        discovery = self.write(root, "discovery.json", b"{}")
        technical = self.write(root, "whitebox-technical.json", b"{}")
        visual = self.write(root, "whitebox-visual.json", b"{}")
        workspace = self.write(root, "workspace.json", b"{}")
        anatomy = {part: True for part in MODULE.ANATOMY_PARTS}
        absent = {part: True for part in MODULE.PROXY_ABSENCE_KEYS}
        node = {
            "schema": MODULE.NODE_SCHEMA, "status": "NODE_DELIVERABLE_READY", "node_id": "SC1-r1-node",
            "unit": "Unit1", "domain": "character_scene", "scene_id": "SC1", "revision": 1, "created_at": "2026-09-13T12:00:00+08:00",
            "scene_label": {"display_name": "Test Bedroom (Night)", "location": "Test Bedroom", "time": "Night"},
            "scope": self.binding(scope), "source_index": self.binding(source), "handoff_document": self.binding(handoff),
            "naming_table": self.binding(names), "web_prompt": self.binding(prompt),
            "deliverables": {
                "production_whiteboxes": [{
                    "actor_id": "A", "pose_id": "pose-a", "anatomy_mode": "FULL_IN_FRAME",
                    "whitebox_kind": "3d-anatomical-mannequin-exact-pose",
                    "complete_anatomy_master": self.binding(wb),
                    "final_submission_whitebox": self.binding(final_submission),
                    "final_submission_authority": True,
                    "anatomy_coverage": anatomy,
                    "prohibited_proxy_types_absent": absent,
                    "technical_review": self.binding(technical),
                    "visual_review": self.binding(visual),
                    "discovery_receipt": self.binding(discovery),
                }],
                "joint_whitebox_preview": self.binding(joint),
                "actual_ui_clearance_preview": self.binding(ui),
                "discovery_receipts": [self.binding(discovery)],
            },
            "user_review_focus": ["proportion", "narrative_pose", "landing_plausibility", "ui_clearance"],
            "manual_return_workspace": self.binding(workspace),
        }
        package = root / "delivery" / "角色融入场景" / "Unit1" / "节点交付" / "SC1"
        package.mkdir(parents=True)
        artifact_specs = [
            ("A", "pose-a", "complete_anatomy_master", wb, "SC1_A_pose-a_whitebox-master.png"),
            ("A", "pose-a", "final_submission_whitebox", final_submission, "SC1_A_pose-a_image1-whitebox.png"),
            ("scene", "1", "joint_whitebox_preview", joint, "SC1_scene_r1_joint-whitebox.png"),
            ("scene", "1", "actual_ui_clearance_preview", ui, "SC1_scene_r1_ui-whitebox.png"),
        ]
        artifacts = []
        for index, (actor, pose, role, source_path, delivery_name) in enumerate(artifact_specs):
            copied = package / delivery_name
            copied.write_bytes(source_path.read_bytes())
            stem = copied.stem
            candidate = package / "_节点资料" / stem / f"{stem}_节点候选.json"
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text("{}", encoding="utf-8")
            artifacts.append({
                "artifact_id": f"artifact-{index}", "actor_id": actor, "pose_id": pose, "role": role,
                "package_file": {"relative_path": copied.name, "sha256": MODULE.sha256(copied)},
                "candidate_record": {"relative_path": str(candidate.relative_to(package)), "sha256": MODULE.sha256(candidate)},
            })
        manifest_path = package / "_节点资料" / "_节点" / node["node_id"] / "节点交付清单.json"
        manifest_path.parent.mkdir(parents=True)
        manifest = {
            "schema": MODULE.CHARACTER_NODE_DELIVERY_SCHEMA,
            "status": MODULE.CHARACTER_NODE_DELIVERY_STATUS,
            "unit": node["unit"], "node_id": node["node_id"], "scene_id": node["scene_id"], "revision": node["revision"],
            "scene_label": node["scene_label"],
            "legacy_migration_backfill": {"enabled": False, "reason": None, "asset_count": 0},
            "formal_pass": False, "package_root": str(package),
            "scope_source": {"path": str(scope), "sha256": MODULE.sha256(scope)},
            "coverage": {"actor_poses_required": 1, "actor_poses_packaged": 1, "missing": [], "extra": []},
            "support_files": [{"kind": "human_preview_index"}, {"kind": "human_asset_list"}, {"kind": "non_formal_warning"}],
            "artifacts": artifacts,
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        node["deliverables"]["node_delivery_manifest"] = self.binding(manifest_path)
        return node

    def test_approved_node_binds_exact_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            node = self.node(root); path = root / "node.json"; path.write_text(json.dumps(node), encoding="utf-8")
            approval = MODULE.approval_for(path, "2026-09-13T13:00:00+08:00", "用户明确通过节点审核")
            approval_path = root / "approval.json"; approval_path.write_text(json.dumps(approval), encoding="utf-8")
            self.assertEqual(MODULE.verify_approval(path, approval_path)["status"], "USER_NODE_APPROVED")
            node["revision"] = 2; path.write_text(json.dumps(node), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact node manifest|delivery revision differs"):
                MODULE.verify_approval(path, approval_path)

    def test_return_accepts_present_slots_and_reports_gaps(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / "manual"; workspace.mkdir(); (workspace / "actor.png").write_bytes(b"rgba")
            contract = {"schema": MODULE.WORKSPACE_SCHEMA, "return_kind": "character_render_return", "node_id": "SC1-r1-node", "domain": "character_scene", "scene_id": "SC1", "revision": 1,
                        "slots": [{"slot_id": "actor", "role": "actor_layer", "relative_path": "actor.png"}, {"slot_id": "missing", "role": "actor_layer", "relative_path": "missing.png"}]}
            contract_path = root / "workspace-contract.json"; contract_path.write_text(json.dumps(contract), encoding="utf-8")
            node = self.node(root); node["manual_return_workspace"] = self.binding(contract_path)
            node_path = root / "node.json"; node_path.write_text(json.dumps(node), encoding="utf-8")
            approval = MODULE.approval_for(node_path, "2026-09-13T13:00:00+08:00", "已生成好了")
            approval_path = root / "approval.json"; approval_path.write_text(json.dumps(approval), encoding="utf-8")
            result = MODULE.receive_return(contract_path, approval_path, workspace, root / "return.json", "2026-09-13T14:00:00+08:00", "已经生成好了")
            self.assertEqual(result["status"], "USER_RETURN_ACCEPTED_FOR_PACKAGING")
            self.assertEqual(len(result["input_gaps"]), 1)
            contract["slots"].append({"slot_id": "late", "role": "late_file", "relative_path": "late.png"})
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "frozen bytes"):
                MODULE.receive_return(contract_path, approval_path, workspace, root / "return-2.json", "2026-09-13T14:01:00+08:00", "已经生成好了")

    def test_character_node_rejects_flat_block_proxy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            node = self.node(root)
            flat = self.image(root, "flat-block.png", rgba=True, flat=True)
            node["deliverables"]["production_whiteboxes"][0]["complete_anatomy_master"] = self.binding(flat)
            path = root / "node.json"
            path.write_text(json.dumps(node), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "flat block/stick proxy"):
                MODULE.validate_node(path)

    def test_character_node_rejects_joint_preview_as_final_whitebox(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            node = self.node(root)
            node["deliverables"]["production_whiteboxes"][0]["final_submission_whitebox"] = node["deliverables"]["joint_whitebox_preview"]
            path = root / "node.json"
            path.write_text(json.dumps(node), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "joint/UI preview"):
                MODULE.validate_node(path)

    def test_character_node_rejects_scene_code_only_label(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            node = self.node(root)
            node["scene_label"] = {"display_name": "SC1", "location": "SC1", "time": "Night"}
            path = root / "node.json"
            path.write_text(json.dumps(node), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cannot be only the scene code"):
                MODULE.validate_node(path)

    def test_character_node_accepts_bound_one_time_scene_ready_migration_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            node = self.node(root)
            manifest_path = Path(node["deliverables"]["node_delivery_manifest"]["path"])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            package = Path(manifest["package_root"])
            rgba = self.image(package, "SC1_A_pose-a_old01_legacy-rgba__XY_x12_y34.png", rgba=True)
            candidate = package / "_节点资料" / rgba.stem / f"{rgba.stem}_节点候选.json"
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text("{}", encoding="utf-8")
            manifest["artifacts"].append({
                "artifact_id": "legacy-rgba", "actor_id": "A", "pose_id": "pose-a",
                "role": "legacy_scene_ready_rgba", "placement_xy": {"x": 12, "y": 34},
                "package_file": {"relative_path": rgba.name, "sha256": MODULE.sha256(rgba)},
                "candidate_record": {"relative_path": str(candidate.relative_to(package)), "sha256": MODULE.sha256(candidate)},
            })
            migration = {"enabled": True, "reason": "one-time workflow migration review", "asset_count": 1}
            manifest["legacy_migration_backfill"] = migration
            node["legacy_migration_backfill"] = migration
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            node["deliverables"]["node_delivery_manifest"] = self.binding(manifest_path)
            path = root / "node.json"
            path.write_text(json.dumps(node), encoding="utf-8")
            self.assertEqual(MODULE.validate_node(path)["legacy_migration_backfill"]["asset_count"], 1)

    def test_prop_node_requires_flat_assets_and_isolated_same_name_candidate_records(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            node_id = "SC4002-r1-node"
            scope = self.write(root, "scope.json", b'{"scope":"r1"}')
            package = root / "delivery" / "道具" / "Unit4" / "节点交付" / "SC4002"
            package.mkdir(parents=True)
            asset = self.image(package, "SC4002_4112_big.png")
            candidate = self.write(
                package,
                "_节点资料/SC4002_4112_big/SC4002_4112_big_交付候选.json",
                b'{"status":"DELIVERY_CANDIDATE_SELECTED"}',
            )
            manifest_path = package / "_节点资料" / "_节点" / node_id / "节点交付清单.json"
            manifest_path.parent.mkdir(parents=True)
            manifest = {
                "schema": MODULE.PROP_NODE_DELIVERY_SCHEMA,
                "status": MODULE.PROP_NODE_DELIVERY_STATUS,
                "node_id": node_id,
                "scene_id": "SC4002",
                "scene_label": {"display_name": "Test Study (Day)", "location": "Test Study", "time": "Day"},
                "revision": 1,
                "formal_pass": False,
                "package_root": str(package),
                "scope_source": {"path": str(scope), "sha256": MODULE.sha256(scope)},
                "coverage": {"required": 1, "packaged": 1, "missing": [], "extra": []},
                "support_files": [
                    {"kind": "human_preview_index"},
                    {"kind": "human_asset_list"},
                    {"kind": "non_formal_warning"},
                ],
                "artifacts": [{
                    "artifact_id": "4112.big", "role": "big", "placement_xy": None,
                    "package_file": {"relative_path": asset.name, "sha256": MODULE.sha256(asset)},
                    "candidate_record": {
                        "relative_path": str(candidate.relative_to(package)),
                        "sha256": MODULE.sha256(candidate),
                    },
                }],
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            node = {"node_id": node_id, "scene_id": "SC4002", "revision": 1, "scene_label": manifest["scene_label"]}
            MODULE.validate_prop_node_delivery(manifest_path, node, scope)
            manifest["artifacts"][0]["role"] = "map_hotspot"
            manifest["artifacts"][0]["placement_xy"] = {"x": 12, "y": 34}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scene-ready PNG must end with"):
                MODULE.validate_prop_node_delivery(manifest_path, node, scope)
            manifest["artifacts"][0]["role"] = "big"
            manifest["artifacts"][0]["placement_xy"] = None
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (package / "guide.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scene root must contain delivery assets only"):
                MODULE.validate_prop_node_delivery(manifest_path, node, scope)


if __name__ == "__main__":
    unittest.main()
