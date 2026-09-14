import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "node_delivery.py"
SPEC = importlib.util.spec_from_file_location("character_node_delivery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CharacterNodeDeliveryTests(unittest.TestCase):
    def write(self, root, name, content=b"x"):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def image(self, root, name, *, rgba=False, flat=False):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "RGBA" if rgba else "RGB"
        background = (0, 0, 0, 0) if rgba else (18, 24, 35)
        image = Image.new(mode, (256, 256), background)
        draw = ImageDraw.Draw(image)
        variant = sum(name.encode("utf-8")) % 20
        if flat:
            draw.rectangle((80, 20, 175, 235), fill=(80, 140, 200, 255) if rgba else (80, 140, 200))
        else:
            for offset in range(96):
                color = (45 + 2 * offset, 65 + offset, 140 + variant - offset, 255) if rgba else (45 + 2 * offset, 65 + offset, 140 + variant - offset)
                draw.line((80 + offset, 20, 80 + offset, 235), fill=color)
        image.save(path)
        return path

    def binding(self, path):
        return {"path": str(path), "sha256": MODULE.sha256(path)}

    def fixture(self, root):
        scope = self.write(root, "scope.json", json.dumps({
            "scope": {"cases": [{"snapshots": [
                {"actor_pose_ids": {"A": "pose-a", "B": "pose-b"}}
            ]}]}
        }).encode())
        source_index = self.write(root, "source-index.json", b"{}")
        handoff = self.write(root, "handoff.md", b"handoff")
        names = self.write(root, "names.json", b"{}")
        prompt = self.write(root, "prompt.md", b"prompt")
        joint = self.image(root, "joint.png")
        ui = self.image(root, "ui.png")
        psd = self.write(root, "whitebox.psd", b"8BPS source")
        entries = []
        for actor, pose in (("A", "pose-a"), ("B", "pose-b")):
            master = self.image(root, f"{actor}-master.png", rgba=True)
            image1 = self.image(root, f"{actor}-image1.png")
            technical = self.write(root, f"checks/{actor}-technical.json", b'{"status":"PASS"}')
            visual = self.write(root, f"checks/{actor}-visual.json", b'{"status":"PASS"}')
            discovery = self.write(root, f"checks/{actor}-discovery.json", b'{"status":"CONFIRMED_ABSENT"}')
            entries.append({
                "actor_id": actor, "pose_id": pose, "anatomy_mode": "FULL_IN_FRAME",
                "whitebox_kind": "3d-anatomical-mannequin-exact-pose",
                "prohibited_proxy_types_absent": {key: True for key in MODULE.PROXY_ABSENCE_KEYS},
                "technical_review": self.binding(technical), "visual_review": self.binding(visual),
                "discovery_receipt": self.binding(discovery),
                "complete_anatomy_master": {
                    "artifact_id": f"{actor}.{pose}.master", "source": self.binding(master),
                    "delivery_name": f"SC2206_{actor}_{pose}_whitebox-master.png",
                    "review_status": "PASS", "selection_basis": "current complete mannequin master",
                },
                "final_submission_whitebox": {
                    "artifact_id": f"{actor}.{pose}.image1", "source": self.binding(image1),
                    "delivery_name": f"SC2206_{actor}_{pose}_image1-whitebox.png",
                    "review_status": "PASS", "selection_basis": "exact ChatGPT Image 1",
                },
            })
        pack = {
            "schema": MODULE.PACK_SCHEMA, "unit": "Unit2", "scene_id": "SC2206", "revision": "r5",
            "scene_label": {"display_name": "Lakeshore Bedroom (Night)", "location": "Lakeshore Bedroom", "time": "Night"},
            "node_id": "SC2206-r5-character-node", "created_at": "2026-09-13T17:00:00+08:00",
            "scope": self.binding(scope), "source_index": self.binding(source_index),
            "handoff_document": self.binding(handoff), "naming_table": self.binding(names), "web_prompt": self.binding(prompt),
            "production_whiteboxes": entries,
            "joint_whitebox_preview": {
                "artifact_id": "scene.joint", "source": self.binding(joint),
                "delivery_name": "SC2206_scene_r5_joint-whitebox.png", "review_status": "PASS",
                "selection_basis": "joint cast relationship review only",
            },
            "actual_ui_clearance_preview": {
                "artifact_id": "scene.ui", "source": self.binding(ui),
                "delivery_name": "SC2206_scene_r5_ui-whitebox.png", "review_status": "PASS",
                "selection_basis": "actual UI clearance review",
            },
            "editable_sources": [{
                "artifact_id": "scene.source", "source": self.binding(psd),
                "delivery_name": "SC2206_scene_r5_source.psd", "review_status": "SOURCE_ONLY",
                "selection_basis": "recoverable scene whitebox source",
            }],
        }
        path = root / "pack.json"
        path.write_text(json.dumps(pack), encoding="utf-8")
        return path, pack

    def test_builds_flat_scene_package_with_real_assets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack, _ = self.fixture(root)
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(pack, delivery)
            result = MODULE.verify_manifest(manifest, delivery)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["actor_poses"], 2)
            self.assertEqual(result["artifacts"], 7)
            package = MODULE.package_target(delivery, {"unit": "Unit2", "scene_id": "SC2206"})
            self.assertEqual({path.name for path in package.iterdir() if path.is_dir()}, {MODULE.METADATA_DIR})
            root_files = {path.name for path in package.iterdir() if path.is_file()}
            self.assertIn("SC2206_A_pose-a_whitebox-master.png", root_files)
            self.assertIn("SC2206_A_pose-a_image1-whitebox.png", root_files)
            self.assertIn("SC2206_scene_r5_source.psd", root_files)
            self.assertFalse(any(name.endswith(".json") for name in root_files))
            node_meta = package / MODULE.METADATA_DIR / MODULE.NODE_METADATA_DIR / "SC2206-r5-character-node"
            self.assertIn("Lakeshore Bedroom", (node_meta / MODULE.HUMAN_INDEX_NAME).read_text(encoding="utf-8"))

    def test_missing_other_actor_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            pack["production_whiteboxes"].pop()
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "coverage differs"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_flat_block_master_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            flat = self.image(root, "flat.png", rgba=True, flat=True)
            pack["production_whiteboxes"][0]["complete_anatomy_master"]["source"] = self.binding(flat)
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "flat block/stick proxy"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_joint_preview_cannot_replace_image1(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            pack["production_whiteboxes"][0]["final_submission_whitebox"]["source"] = pack["joint_whitebox_preview"]["source"]
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "joint/UI preview"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_noncanonical_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            pack["production_whiteboxes"][0]["final_submission_whitebox"]["delivery_name"] = "image-1-local-whitebox.png"
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must use"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_extra_root_file_or_actor_folder_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack, _ = self.fixture(root)
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(pack, delivery)
            package = manifest.parents[3]
            (package / "guide.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "actual whitebox/source assets only"):
                MODULE.verify_manifest(manifest, delivery)
            (package / "guide.json").unlink()
            (package / "A").mkdir()
            with self.assertRaisesRegex(ValueError, "role/actor/revision"):
                MODULE.verify_manifest(manifest, delivery)

    def test_changed_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack, _ = self.fixture(root)
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(pack, delivery)
            package = manifest.parents[3]
            next(package.glob("*.png")).write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "frozen package bytes"):
                MODULE.verify_manifest(manifest, delivery)

    def test_packaged_scope_supports_portable_verification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack, pack_data = self.fixture(root)
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(pack, delivery)
            Path(pack_data["scope"]["path"]).unlink()
            self.assertEqual(MODULE.verify_manifest(manifest, delivery)["status"], "PASS")

    def test_one_time_migration_backfill_packages_historical_candidates_and_xy_rgba(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack_path, pack = self.fixture(root)
            inventory = self.write(root, "legacy-inventory.json", b'{"reason":"workflow migration review"}')
            technical = self.write(root, "checks/legacy-technical.json", b'{"status":"TECHNICAL_FILE_PASS"}')
            visual = self.write(root, "checks/legacy-visual.json", b'{"status":"NOT_REVIEWED"}')
            provenance = self.write(root, "checks/legacy-provenance.json", b'{"source":"historical work ledger"}')
            rgb = self.image(root, "legacy-rgb.png")
            rgba = self.image(root, "legacy-rgba.png", rgba=True)
            shared = {
                "actor_id": "A", "pose_id": "pose-a", "review_status": "UNREVIEWED_MIGRATION_COPY",
                "technical_review": self.binding(technical), "visual_review": self.binding(visual),
                "provenance_receipt": self.binding(provenance),
            }
            pack["legacy_migration_backfill"] = {
                "enabled": True, "reason": "one-time review of candidates made before the new node workflow",
                "source_inventory": self.binding(inventory),
            }
            pack["legacy_review_assets"] = [
                {
                    **shared, "artifact_id": "A.pose-a.legacy-rgb", "role": "legacy_render_candidate",
                    "source": self.binding(rgb),
                    "delivery_name": "SC2206_A_pose-a_old01_legacy-candidate.png",
                    "selection_basis": "historical generated candidate for one-time reuse review",
                },
                {
                    **shared, "artifact_id": "A.pose-a.legacy-rgba", "role": "legacy_scene_ready_rgba",
                    "source": self.binding(rgba),
                    "delivery_name": "SC2206_A_pose-a_old02_legacy-rgba__XY_x31_y47.png",
                    "selection_basis": "historical extracted layer for one-time reuse review",
                },
            ]
            pack_path.write_text(json.dumps(pack), encoding="utf-8")
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(pack_path, delivery)
            result = MODULE.verify_manifest(manifest, delivery)
            self.assertEqual(len(result["legacy_migration_assets"]), 2)
            self.assertEqual(result["legacy_migration_assets"][1]["placement_xy"], {"x": 31, "y": 47})
            package = MODULE.package_target(delivery, {"unit": "Unit2", "scene_id": "SC2206"})
            self.assertTrue((package / "SC2206_A_pose-a_old02_legacy-rgba__XY_x31_y47.png").is_file())
            batch_source = self.write(root, "migration-batch-source.json", b'{"scene_ids":["SC2206"]}')
            batch_path = root / "migration-batch.json"
            batch_path.write_text(json.dumps({
                "schema": MODULE.BATCH_AUDIT_SCHEMA, "unit": "Unit2",
                "created_at": "2026-09-13T18:00:00+08:00",
                "source_batch_scope": self.binding(batch_source),
                "expected_scene_ids": ["SC2206"],
                "scenes": [{"scene_id": "SC2206", "scene_label": pack["scene_label"], "scope": pack["scope"]}],
            }), encoding="utf-8")
            audit = MODULE.audit_batch(batch_path, delivery, root / "migration-report")
            self.assertEqual(audit["counts"]["migration_review_assets"], 2)
            self.assertIn("old02_legacy-rgba__XY_x31_y47", Path(audit["outputs"]["markdown"]).read_text(encoding="utf-8-sig"))

    def test_legacy_asset_requires_explicit_one_time_migration_mode(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack_path, pack = self.fixture(root)
            pack["legacy_review_assets"] = [{}]
            pack_path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "allowed only"):
                MODULE.build(pack_path, root / "delivery" / "角色融入场景")

    def test_batch_audit_finds_missing_scenes_and_writes_human_location_time_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack_path, pack = self.fixture(root)
            delivery = root / "delivery" / "角色融入场景"
            MODULE.build(pack_path, delivery)
            second_scope = self.write(root, "scope-2316.json", json.dumps({
                "scope": {"cases": [{"snapshots": [{"actor_pose_ids": {"Emma": "letter"}}]}]}
            }).encode())
            batch_source = self.write(root, "all-scenes.json", b'{"scene_ids":["SC2206","SC2316"]}')
            batch = {
                "schema": MODULE.BATCH_AUDIT_SCHEMA,
                "unit": "Unit2",
                "created_at": "2026-09-13T18:00:00+08:00",
                "source_batch_scope": self.binding(batch_source),
                "expected_scene_ids": ["SC2206", "SC2316"],
                "scenes": [
                    {"scene_id": "SC2206", "scene_label": pack["scene_label"], "scope": pack["scope"]},
                    {"scene_id": "SC2316", "scene_label": {"display_name": "City Hall Stairs (Time Unspecified)", "location": "City Hall Stairs", "time": "Time Unspecified"}, "scope": self.binding(second_scope)},
                ],
            }
            batch_path = root / "batch.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            report = MODULE.audit_batch(batch_path, delivery, root / "reports")
            self.assertEqual(report["status"], "INCOMPLETE")
            self.assertEqual(report["counts"]["verified_scenes"], 1)
            self.assertEqual(report["counts"]["manual_supply_or_repackaging"], 4)
            self.assertIn("City Hall Stairs", Path(report["outputs"]["markdown"]).read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
