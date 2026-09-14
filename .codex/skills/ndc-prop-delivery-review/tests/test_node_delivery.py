import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "node_delivery.py"
SPEC = importlib.util.spec_from_file_location("node_delivery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NodeDeliveryTests(unittest.TestCase):
    def write(self, root, name, content=b"x"):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def binding(self, path):
        return {"path": str(path), "sha256": MODULE.sha256(path)}

    def subject(self, subject_id, kind, semantic_class, required):
        dispositions = []
        for role in MODULE.ROLE_CATALOG:
            artifact_ids = required.get(role)
            if artifact_ids:
                dispositions.append({"role": role, "disposition": "REQUIRED", "artifact_ids": artifact_ids})
            else:
                dispositions.append({"role": role, "disposition": "NOT_APPLICABLE", "reason": "not required by frozen acquisition and runtime contract"})
        return {
            "subject_id": subject_id,
            "subject_kind": kind,
            "semantic_class": semantic_class,
            "role_dispositions": dispositions,
        }

    def fixture(self, root):
        active_scope = self.write(root, "active-scope.json", b'{"revision":"r1"}')
        scope = {
            "schema": MODULE.SCOPE_SCHEMA,
            "unit": "Unit4",
            "scene_id": "SC4011",
            "scene_label": {"display_name": "Lakeshore Study (Day)", "location": "Lakeshore Study", "time": "Day"},
            "revision": "r1",
            "node_id": "SC4011-r1-complete-prop-node",
            "source_scope": self.binding(active_scope),
            "subjects": [
                self.subject("SC4011", "scene", "scene", {
                    "scene_original": ["scene.original"],
                    "scene_final": ["scene.final"],
                    "scene_preview": ["scene.preview"],
                }),
                self.subject("4211", "item", "prop", {
                    "source_master": ["4211.master"],
                    "psd_source": ["4211.psd"],
                    "big": ["4211.big"],
                    "icon": ["4211.icon"],
                    "scene_original": ["4211.original"],
                    "carrier_without_prop": ["4211.carrier"],
                    "pickup_layer": ["4211.pickup-layer"],
                    "scene_before_pickup": ["4211.before"],
                    "map_hotspot": ["4211.map"],
                    "xy": ["4211.xy"],
                }),
                self.subject("4212", "item", "clue", {
                    "state_master": ["4212.master"],
                    "big": ["4212.big"],
                    "icon": ["4212.icon"],
                    "map_hotspot": ["4212.map"],
                    "xy": ["4212.xy"],
                }),
                self.subject("4213", "item", "environment_narrative", {
                    "source_master": ["4213.master"],
                    "big": ["4213.big"],
                    "map_hotspot": ["4213.map"],
                    "xy": ["4213.xy"],
                }),
                self.subject("4214", "container", "container", {
                    "source_master": ["4214.master"],
                    "xy": ["4214.xy"],
                    "type6_container": ["4214.type6"],
                    "type7_menu": ["4214.type7"],
                    "menu_preview": ["4214.menu-preview"],
                }),
            ],
        }
        scope_path = root / "node-scope.json"
        scope_path.write_text(json.dumps(scope), encoding="utf-8")
        _, expected = MODULE.validate_scope(scope_path)
        artifacts = []
        for artifact_id, expected_entry in expected.items():
            suffix = ".txt" if expected_entry["role"] == "xy" else ".psd" if expected_entry["role"] == "psd_source" else ".png"
            source = self.write(root, f"sources/{artifact_id}{suffix}", f"asset:{artifact_id}".encode())
            technical = self.write(root, f"checks/{artifact_id}.technical.json", b'{"status":"PASS"}')
            checks = [{"kind": "technical_review", "file": self.binding(technical)}]
            if suffix in MODULE.IMAGE_SUFFIXES:
                visual = self.write(root, f"checks/{artifact_id}.visual.json", b'{"status":"PASS"}')
                checks.append({"kind": "visual_review", "file": self.binding(visual)})
            prefix = MODULE.subject_file_prefix(scope["scene_id"], expected_entry["subject_id"])
            token = MODULE.ROLE_FILE_TOKENS[expected_entry["role"]]
            xy_suffix = "__XY_x120_y340" if expected_entry["role"] in MODULE.SCENE_READY_ROLES else ""
            artifacts.append({
                "artifact_id": artifact_id,
                "subject_id": expected_entry["subject_id"],
                "role": expected_entry["role"],
                "source": self.binding(source),
                "delivery_name": f"{prefix}_{token}{xy_suffix}{suffix}",
                "review_status": "PASS",
                "selection_basis": "current frozen node-delivery target",
                "checks": checks,
            })
        pack = {
            "schema": MODULE.PACK_SCHEMA,
            "unit": scope["unit"],
            "scene_id": scope["scene_id"],
            "scene_label": scope["scene_label"],
            "revision": scope["revision"],
            "node_id": scope["node_id"],
            "created_at": "2026-09-13T16:00:00+08:00",
            "scope": self.binding(scope_path),
            "artifacts": artifacts,
        }
        pack_path = root / "pack.json"
        pack_path.write_text(json.dumps(pack), encoding="utf-8")
        return scope_path, pack_path, pack

    def test_pack_contains_directly_usable_assets_and_human_preview(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            manifest = MODULE.build(scope, pack, delivery)
            result = MODULE.verify_manifest(manifest, delivery)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["required"], 27)
            package = MODULE.package_target(delivery, {"unit": "Unit4", "scene_id": "SC4011"})
            node_meta = package / MODULE.METADATA_DIR / MODULE.NODE_METADATA_DIR / "SC4011-r1-complete-prop-node"
            self.assertEqual(manifest, node_meta / MODULE.MANIFEST_NAME)
            self.assertTrue((node_meta / MODULE.HUMAN_INDEX_NAME).is_file())
            self.assertIn("<img", (node_meta / MODULE.HUMAN_INDEX_NAME).read_text(encoding="utf-8"))
            self.assertIn("Lakeshore Study", (node_meta / MODULE.HUMAN_INDEX_NAME).read_text(encoding="utf-8"))
            root_files = sorted(path.name for path in package.iterdir() if path.is_file())
            self.assertEqual(len(root_files), 27)
            self.assertFalse(any(name.endswith(".json") for name in root_files))
            self.assertIn("SC4011_4211_psd.psd", root_files)
            self.assertTrue((package / MODULE.METADATA_DIR / "SC4011_4211_big" / "SC4011_4211_big_交付候选.json").is_file())
            self.assertFalse((package / "02_Big").exists())

    def test_missing_scoped_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack_path, pack = self.fixture(root)
            pack["artifacts"].pop()
            pack_path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "coverage differs"):
                MODULE.build(scope, pack_path, root / "delivery" / "道具")

    def test_incomplete_role_matrix_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope_path, _, _ = self.fixture(root)
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            scope["subjects"][0]["role_dispositions"].pop()
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "explicitly cover all"):
                MODULE.validate_scope(scope_path)

    def test_mainline_after_node_is_recorded_but_not_required_in_node_payload(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope_path, _, _ = self.fixture(root)
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            item = next(subject for subject in scope["subjects"] if subject["subject_id"] == "4211")
            icon = next(entry for entry in item["role_dispositions"] if entry["role"] == "icon")
            icon["disposition"] = "MAINLINE_AFTER_NODE"
            icon["reason"] = "continues in the frozen production mainline after the requested master and Big review node"
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            validated, expected = MODULE.validate_scope(scope_path)
            self.assertNotIn("4211.icon", expected)
            self.assertEqual(MODULE.mainline_after_node(validated)[0]["artifact_ids"], ["4211.icon"])

    def test_scene_payload_is_not_forced_when_initial_node_only_requests_prop_assets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            active_scope = self.write(root, "active-scope.json", b'{"revision":"r1"}')
            scope = {
                "schema": MODULE.SCOPE_SCHEMA,
                "unit": "Unit4",
                "scene_id": "SC4011",
                "scene_label": {"display_name": "Lakeshore Study (Day)", "location": "Lakeshore Study", "time": "Day"},
                "revision": "r1",
                "node_id": "SC4011-r1-initial-prop-node",
                "source_scope": self.binding(active_scope),
                "subjects": [
                    self.subject("4211", "item", "prop", {
                        "source_master": ["4211.master"],
                        "big": ["4211.big"],
                    }),
                ],
            }
            scope_path = root / "initial-node-scope.json"
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            _, expected = MODULE.validate_scope(scope_path)
            self.assertEqual(set(expected), {"4211.master", "4211.big"})

    def test_json_only_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            manifest = MODULE.build(scope, pack, delivery)
            package = manifest.parents[3]
            first_asset = next(package.glob("*.png"))
            first_asset.unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                MODULE.verify_manifest(manifest, delivery)

    def test_asset_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            manifest = MODULE.build(scope, pack, delivery)
            package = manifest.parents[3]
            first_asset = next(package.glob("*.png"))
            first_asset.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "frozen package bytes"):
                MODULE.verify_manifest(manifest, delivery)

    def test_undeclared_extra_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            manifest = MODULE.build(scope, pack, delivery)
            (manifest.parents[3] / "extra.png").write_bytes(b"extra")
            with self.assertRaisesRegex(ValueError, "delivery assets only|undeclared files"):
                MODULE.verify_manifest(manifest, delivery)

    def test_noncanonical_or_foldered_delivery_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack_path, pack = self.fixture(root)
            pack["artifacts"][0]["delivery_name"] = "4211_big.png"
            pack_path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must identify scene and prop"):
                MODULE.build(scope, pack_path, root / "delivery" / "道具")

    def test_scene_ready_png_requires_matching_xy_filename_suffix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack_path, pack = self.fixture(root)
            scene_ready = next(item for item in pack["artifacts"] if item["role"] == "map_hotspot")
            scene_ready["delivery_name"] = scene_ready["delivery_name"].replace("__XY_x120_y340", "")
            pack_path.write_text(json.dumps(pack), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must end with __XY"):
                MODULE.build(scope, pack_path, root / "delivery" / "道具")

    def test_scene_label_must_include_location_and_time(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope_path, _, _ = self.fixture(root)
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            scope["scene_label"]["display_name"] = scope["scene_id"]
            scope_path.write_text(json.dumps(scope), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cannot be only the scene code"):
                MODULE.validate_scope(scope_path)

    def test_per_type_folder_is_rejected_even_when_empty(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            manifest = MODULE.build(scope, pack, delivery)
            (manifest.parents[3] / "02_Big").mkdir()
            with self.assertRaisesRegex(ValueError, "per-type"):
                MODULE.verify_manifest(manifest, delivery)

    def test_wrong_scene_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope, pack, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            manifest = MODULE.build(scope, pack, delivery)
            with self.assertRaisesRegex(ValueError, "节点交付"):
                MODULE.verify_manifest(manifest, root / "other" / "道具")

    def test_batch_audit_reports_every_scene_location_time_and_missing_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope_path, pack_path, _ = self.fixture(root)
            delivery = root / "delivery" / "道具"
            MODULE.build(scope_path, pack_path, delivery)
            second_scope = json.loads(scope_path.read_text(encoding="utf-8"))
            second_scope["scene_id"] = "SC4012"
            second_scope["scene_label"] = {"display_name": "City Hall Stairs (Time Unspecified)", "location": "City Hall Stairs", "time": "Time Unspecified"}
            second_scope["node_id"] = "SC4012-r1-complete-prop-node"
            for subject in second_scope["subjects"]:
                if subject["subject_id"] == "SC4011":
                    subject["subject_id"] = "SC4012"
            second_path = root / "node-scope-4012.json"
            second_path.write_text(json.dumps(second_scope), encoding="utf-8")
            batch_source = self.write(root, "batch-source.json", b'{"scene_ids":["SC4011","SC4012"]}')
            batch = {
                "schema": MODULE.BATCH_AUDIT_SCHEMA,
                "unit": "Unit4",
                "created_at": "2026-09-13T18:00:00+08:00",
                "source_batch_scope": self.binding(batch_source),
                "expected_scene_ids": ["SC4011", "SC4012"],
                "scenes": [
                    {"scene_id": "SC4011", "scene_label": {"display_name": "Lakeshore Study (Day)", "location": "Lakeshore Study", "time": "Day"}, "scope": self.binding(scope_path)},
                    {"scene_id": "SC4012", "scene_label": second_scope["scene_label"], "scope": self.binding(second_path)},
                ],
            }
            batch_path = root / "batch-audit.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            report = MODULE.audit_batch(batch_path, delivery, root / "reports")
            self.assertEqual(report["status"], "INCOMPLETE")
            self.assertEqual(report["counts"]["verified_scenes"], 1)
            self.assertEqual(report["scenes"][1]["location"], "City Hall Stairs")
            self.assertGreater(report["counts"]["manual_supply_or_repackaging"], 0)
            self.assertIn("City Hall Stairs", Path(report["outputs"]["markdown"]).read_text(encoding="utf-8-sig"))

    def test_optional_hotspot_reconciliation_finds_exact_pass_bytes_with_xy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scope_path, pack_path, pack = self.fixture(root)
            delivery = root / "delivery" / "道具"
            MODULE.build(scope_path, pack_path, delivery)
            hotspot = next(item for item in pack["artifacts"] if item["artifact_id"] == "4212.map")
            source_path = Path(hotspot["source"]["path"])
            review_path = root / "stage4-hotspot-review.json"
            review_path.write_text(json.dumps({
                "visual_check_status": "PASS",
                "coordinate": {"x": 120, "y": 340},
                "outputs": [{"path": str(source_path), "sha256": hotspot["source"]["sha256"]}],
            }), encoding="utf-8")
            batch = {
                "schema": "ndc-prop-batch/v1",
                "batch_id": "Unit4_test_batch",
                "scope": {"required_artifacts": ["4212.map"]},
                "artifacts": {
                    "4212.map": {
                        "item_ids": ["4212"],
                        "stage": 4,
                        "role": "scene_pickup_map",
                        "status": "PASS",
                        "rejected": False,
                        "scene_id": "4011",
                        "path": str(source_path),
                        "sha256": hotspot["source"]["sha256"],
                        "review": str(review_path),
                    }
                },
            }
            batch_path = root / "batch.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            result = MODULE.reconcile_hotspots(batch_path, delivery, root / "reports", "Unit4")
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["counts"]["packaged_exact_with_xy"], 1)

    def test_optional_hotspot_reconciliation_reports_omitted_pass_asset(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_path = self.write(root, "stage4/map.png", b"stage4-pass-map")
            digest = MODULE.sha256(source_path)
            review_path = root / "stage4/review.json"
            review_path.write_text(json.dumps({
                "visual_check_status": "PASS",
                "outputs": [{"path": str(source_path), "sha256": digest}],
            }), encoding="utf-8")
            batch = {
                "schema": "ndc-prop-batch/v1",
                "batch_id": "Unit4_test_batch",
                "scope": {"required_artifacts": ["4112.map"]},
                "artifacts": {
                    "4112.map": {
                        "item_ids": ["4112"],
                        "stage": 4,
                        "role": "container_child_map",
                        "status": "PASS",
                        "rejected": False,
                        "scene_id": "4002",
                        "path": str(source_path),
                        "sha256": digest,
                        "review": str(review_path),
                    }
                },
            }
            batch_path = root / "batch.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            result = MODULE.reconcile_hotspots(
                batch_path,
                root / "delivery" / "道具",
                root / "reports",
                "Unit4",
            )
            self.assertEqual(result["status"], "INCOMPLETE")
            self.assertEqual(result["hotspots"][0]["status"], "MISSING_FROM_NODE")


if __name__ == "__main__":
    unittest.main()
