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

    def image(self, root, name, *, rgba=False, flat=False, gradient_flat=False):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "RGBA" if rgba else "RGB"
        background = (0, 0, 0, 0) if rgba else (18, 24, 35)
        image = Image.new(mode, (256, 256), background)
        draw = ImageDraw.Draw(image)
        variant = sum(name.encode("utf-8")) % 20
        if flat:
            draw.rectangle((80, 20, 175, 235), fill=(80, 140, 200, 255) if rgba else (80, 140, 200))
        elif gradient_flat:
            for offset in range(96):
                color = (45 + 2 * offset, 65 + offset, 140 + variant - offset, 255) if rgba else (45 + 2 * offset, 65 + offset, 140 + variant - offset)
                draw.line((80 + offset, 20, 80 + offset, 235), fill=color)
        else:
            mask = Image.new("L", (256, 256), 0)
            anatomy = ImageDraw.Draw(mask)
            anatomy.ellipse((106, 16, 150, 60), fill=255)
            anatomy.rectangle((119, 54, 137, 72), fill=255)
            anatomy.polygon(((94, 68), (162, 68), (153, 142), (103, 142)), fill=255)
            anatomy.ellipse((101, 128, 155, 164), fill=255)
            anatomy.line((101, 78, 72, 138), fill=255, width=18)
            anatomy.line((155, 78, 184, 138), fill=255, width=18)
            anatomy.ellipse((63, 130, 82, 149), fill=255)
            anatomy.ellipse((174, 130, 193, 149), fill=255)
            anatomy.line((116, 154, 105, 225), fill=255, width=20)
            anatomy.line((140, 154, 151, 225), fill=255, width=20)
            anatomy.ellipse((92, 216, 116, 238), fill=255)
            anatomy.ellipse((140, 216, 164, 238), fill=255)
            shade = Image.new(mode, (256, 256), background)
            shade_draw = ImageDraw.Draw(shade)
            for y in range(256):
                color = (45 + y // 2, 65 + y // 3, 155 + variant - y // 4, 255) if rgba else (45 + y // 2, 65 + y // 3, 155 + variant - y // 4)
                shade_draw.line((0, y, 255, y), fill=color)
            image.paste(shade, (0, 0), mask)
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
        psd = self.write(root, "whitebox.psd", b"8BPS\x00\x01source")
        entries = []
        authority = []
        for actor, pose in (("A", "pose-a"), ("B", "pose-b")):
            master = self.image(root, f"{actor}-master.png", rgba=True)
            image1 = self.image(root, f"{actor}-image1.png")
            technical = self.write(root, f"checks/{actor}-technical.json", b'{"status":"PASS"}')
            visual = self.write(root, f"checks/{actor}-visual.json", json.dumps({
                "schema": MODULE.WHITEBOX_VISUAL_REVIEW_SCHEMA,
                "status": "PASS",
                "actor_id": actor,
                "pose_id": pose,
                "complete_anatomy_master_sha256": MODULE.sha256(master),
                "final_submission_whitebox_sha256": MODULE.sha256(image1),
                "reviewed_at": "2026-09-14T14:00:00+08:00",
                "review_scales": {"whole_frame_percent": 100, "local_percent": 200},
                "visual_gate": {key: True for key in MODULE.WHITEBOX_VISUAL_GATE_KEYS},
                "decision_basis": "synthetic test mannequin fixture with readable volume and complete body coverage",
            }).encode())
            discovery = self.write(root, f"checks/{actor}-discovery.json", b'{"status":"CONFIRMED_ABSENT"}')
            authority.append({
                "actor_id": actor,
                "pose_id": pose,
                "complete_anatomy_master_sha256": MODULE.sha256(master),
                "independently_editable": True,
                "current_position_and_scale_preserved": True,
                "accepted_3d_whitebox_only": True,
            })
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
        structure_review = self.write(root, "checks/psd-structure-review.json", json.dumps({
            "schema": MODULE.EDITABLE_PSD_REVIEW_SCHEMA,
            "status": "PASS",
            "psd_sha256": MODULE.sha256(psd),
            "reviewed_at": "2026-09-14T14:05:00+08:00",
            "canvas_size": {"width": 256, "height": 256},
            "original_scene_canvas_size": {"width": 256, "height": 256},
            "structure_gate": {key: True for key in MODULE.EDITABLE_PSD_GATE_KEYS},
            "actor_pose_layers": authority,
            "decision_basis": "synthetic Photoshop layer receipt covering the frozen scope",
        }).encode())
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
                "delivery_name": "SC2206_scene_r5_performance-editable_source.psd", "review_status": "SOURCE_ONLY",
                "selection_basis": "per-scene editable performance source",
                "editable_structure": {key: True for key in MODULE.EDITABLE_STRUCTURE_KEYS},
                "structure_review": self.binding(structure_review),
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
            self.assertIn("SC2206_scene_r5_performance-editable_source.psd", root_files)
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

    def test_v2_requires_exactly_one_performance_editable_psd(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            pack["editable_sources"] = []
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_v2_rejects_psb_in_place_of_required_psd(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            psb = self.write(root, "whitebox.psb", b"8BPS large source")
            pack["editable_sources"][0]["source"] = self.binding(psb)
            pack["editable_sources"][0]["delivery_name"] = "SC2206_scene_r5_performance-editable_source.psb"
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be a PSD"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_v2_rejects_file_with_psd_extension_but_no_psd_header(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            fake = self.write(root, "renamed.psd", b"not a photoshop document")
            pack["editable_sources"][0]["source"] = self.binding(fake)
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "actual PSD"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_legacy_v1_pack_remains_verifiable_without_editable_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            pack["schema"] = MODULE.LEGACY_PACK_SCHEMA
            pack["editable_sources"] = []
            path.write_text(json.dumps(pack), encoding="utf-8")
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(path, delivery)
            result = MODULE.verify_manifest(manifest, delivery)
            self.assertEqual(result["source_pack_schema"], MODULE.LEGACY_PACK_SCHEMA)
            self.assertIsNone(result["performance_editable_psd"])

    def test_flat_block_master_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            flat = self.image(root, "flat.png", rgba=True, flat=True)
            pack["production_whiteboxes"][0]["complete_anatomy_master"]["source"] = self.binding(flat)
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "flat block/stick proxy"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_gradient_flat_proxy_cannot_pass_by_pixel_statistics(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            flat = self.image(root, "gradient-flat.png", rgba=True, gradient_flat=True)
            entry = pack["production_whiteboxes"][0]
            entry["complete_anatomy_master"]["source"] = self.binding(flat)
            visual_path = Path(entry["visual_review"]["path"])
            visual = json.loads(visual_path.read_text(encoding="utf-8"))
            visual["complete_anatomy_master_sha256"] = MODULE.sha256(flat)
            visual["visual_gate"]["continuous_3d_volume_and_shading"] = False
            visual_path.write_text(json.dumps(visual), encoding="utf-8")
            entry["visual_review"] = self.binding(visual_path)
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "visual invariant"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_v3_psd_review_rejects_flat_proxy_layer_declaration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            review_path = Path(pack["editable_sources"][0]["structure_review"]["path"])
            review = json.loads(review_path.read_text(encoding="utf-8"))
            review["structure_gate"]["accepted_3d_whiteboxes_only"] = False
            review_path.write_text(json.dumps(review), encoding="utf-8")
            pack["editable_sources"][0]["structure_review"] = self.binding(review_path)
            path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "visual invariant"):
                MODULE.build(path, root / "delivery" / "角色融入场景")

    def test_previous_v2_pack_remains_historically_verifiable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, pack = self.fixture(root)
            pack["schema"] = MODULE.PREVIOUS_PACK_SCHEMA
            pack["editable_sources"][0].pop("structure_review")
            path.write_text(json.dumps(pack), encoding="utf-8")
            delivery = root / "delivery" / "角色融入场景"
            manifest = MODULE.build(path, delivery)
            self.assertEqual(MODULE.verify_manifest(manifest, delivery)["source_pack_schema"], MODULE.PREVIOUS_PACK_SCHEMA)

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
            for entry in pack_data["production_whiteboxes"]:
                for kind in ("technical_review", "visual_review", "discovery_receipt"):
                    Path(entry[kind]["path"]).unlink()
            Path(pack_data["editable_sources"][0]["structure_review"]["path"]).unlink()
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
            self.assertEqual(report["counts"]["manual_supply_or_repackaging"], 5)
            self.assertIn("City Hall Stairs", Path(report["outputs"]["markdown"]).read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
