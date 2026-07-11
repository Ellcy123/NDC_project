from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from copy import deepcopy
from io import StringIO
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_canon_manifest import (  # noqa: E402
    ManifestValidationError,
    load_and_validate_manifest,
    main,
    validate_manifest,
)


def make_valid_manifest(repo_root: Path) -> dict:
    (repo_root / "tables").mkdir()

    chapters = []
    for unit in range(1, 6):
        planning_directory = f"planning/Unit{unit}"
        state_directory = repo_root / planning_directory / "state"
        state_directory.mkdir(parents=True)
        (repo_root / planning_directory / "outline.md").write_text(
            f"# Unit {unit} Outline\n", encoding="utf-8"
        )
        for loop in range(1, 7):
            (state_directory / f"loop{loop}_state.yaml").write_text(
                f"loop: {loop}\n", encoding="utf-8"
            )

        episode = f"EPI{unit:02d}"
        (repo_root / "AVG" / episode).mkdir(parents=True)
        aliases = []
        if unit == 1:
            aliases.append({"name": "Unit9", "role": "active_authoring_alias"})
        elif unit == 2:
            aliases.append({"name": "Unit10", "role": "active_authoring_alias"})

        chapters.append(
            {
                "canonicalUnit": f"Unit{unit}",
                "playerChapter": unit,
                "playerTitle": f"Test Chapter {unit}",
                "aliases": aliases,
                "planningDirectory": planning_directory,
                "unityEpisode": episode,
                "idSpaces": [
                    {
                        "scope": "current_authoring_and_runtime",
                        "range": f"{unit}xxx",
                        "episode": episode,
                        "status": "current",
                        "migration": "preserve",
                    }
                ],
                "sources": {
                    "outline": f"{planning_directory}/outline.md",
                    "statePattern": f"{planning_directory}/state/loop{{1-6}}_state.yaml",
                    "avgCurrent": f"AVG/{episode}",
                    "tableDrafts": None,
                    "runtimeTables": "tables",
                },
                "maturity": {
                    "phase": "active_iteration",
                    "outline": "present_active",
                    "state": {
                        "status": "present",
                        "expectedLoops": 6,
                        "presentLoops": [1, 2, 3, 4, 5, 6],
                    },
                    "avg": {
                        "status": "present",
                        "expectedLoops": 6,
                        "presentLoops": [1, 2, 3, 4, 5, 6],
                    },
                    "tables": "present",
                    "finality": "not_declared",
                    "verifiedAt": "2026-07-11",
                },
                "tooling": {"buildUnitFlow": True},
                "history": [],
            }
        )

    return {
        "schemaVersion": 1,
        "updatedAt": "2026-07-11",
        "policy": {
            "idMigration": "none",
            "automaticIdTranslation": False,
            "canonicalUnits": [f"Unit{unit}" for unit in range(1, 6)],
        },
        "chapters": chapters,
        "flowAliases": [
            {
                "name": "Unit9",
                "target": "Unit1",
                "enabled": True,
                "title": "Test Chapter (Unit1 mapping)",
                "reason": "Compatibility",
            },
            {
                "name": "Unit10",
                "target": "Unit2",
                "enabled": True,
                "title": "Test Chapter (Unit2 mapping)",
                "reason": "Compatibility",
            },
        ],
    }


class CanonManifestValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        self.manifest = make_valid_manifest(self.repo_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def errors_for(self, data: dict) -> list[str]:
        return validate_manifest(data, self.repo_root)

    def assert_field_error(self, data: dict, field_message: str) -> None:
        try:
            errors = self.errors_for(data)
        except TypeError as exc:
            self.fail(f"validate_manifest raised TypeError instead of returning errors: {exc}")
        self.assertTrue(any(field_message in error for error in errors), errors)

    def test_valid_manifest_has_no_errors(self) -> None:
        self.assertEqual([], self.errors_for(self.manifest))

    def test_repository_manifest_is_valid_and_has_expected_identity(self) -> None:
        manifest_path = REPO_ROOT / "canon_manifest.json"
        data = load_and_validate_manifest(manifest_path, REPO_ROOT)
        chapters = {chapter["canonicalUnit"]: chapter for chapter in data["chapters"]}
        self.assertEqual(["Unit1", "Unit2", "Unit3", "Unit4", "Unit5"], data["policy"]["canonicalUnits"])
        self.assertEqual("EPI01", chapters["Unit1"]["unityEpisode"])
        self.assertEqual("none", data["policy"]["idMigration"])
        self.assertFalse(data["policy"]["automaticIdTranslation"])

    def test_repository_manifest_has_only_enabled_unit9_flow_alias(self) -> None:
        manifest_path = REPO_ROOT / "canon_manifest.json"
        data = load_and_validate_manifest(manifest_path, REPO_ROOT)

        self.assertEqual(1, len(data["flowAliases"]))
        flow_alias = data["flowAliases"][0]
        self.assertEqual("Unit9", flow_alias["name"])
        self.assertEqual("Unit1", flow_alias["target"])
        self.assertIs(True, flow_alias["enabled"])
        self.assertNotIn("Unit10", [alias["name"] for alias in data["flowAliases"]])

    def test_repository_manifest_locks_current_unit1_and_unit2_id_spaces(self) -> None:
        manifest_path = REPO_ROOT / "canon_manifest.json"
        data = load_and_validate_manifest(manifest_path, REPO_ROOT)
        chapters = {chapter["canonicalUnit"]: chapter for chapter in data["chapters"]}

        self.assertEqual(
            [
                {
                    "scope": "authoring_state_and_avg",
                    "range": "9xxx",
                    "episode": "EPI09",
                    "status": "current",
                    "migration": "preserve",
                },
                {
                    "scope": "runtime_tables",
                    "range": "1xxx",
                    "episode": "EPI01",
                    "status": "current",
                    "migration": "preserve",
                },
            ],
            chapters["Unit1"]["idSpaces"],
        )
        self.assertEqual(
            [
                {
                    "scope": "current_authoring_and_runtime",
                    "range": "2xxx",
                    "episode": "EPI02",
                    "status": "current",
                    "migration": "preserve",
                }
            ],
            chapters["Unit2"]["idSpaces"],
        )
        self.assertNotIn(
            "10xxx", [id_space["range"] for id_space in chapters["Unit2"]["idSpaces"]]
        )
        self.assertEqual(
            ["10xxx"],
            [
                entry["formerIdRange"]
                for entry in chapters["Unit2"]["history"]
                if "formerIdRange" in entry
            ],
        )

    def test_repository_manifest_keeps_unit4_and_unit5_reserved(self) -> None:
        manifest_path = REPO_ROOT / "canon_manifest.json"
        data = load_and_validate_manifest(manifest_path, REPO_ROOT)
        chapters = {chapter["canonicalUnit"]: chapter for chapter in data["chapters"]}

        for canonical_unit in ("Unit4", "Unit5"):
            with self.subTest(canonical_unit=canonical_unit):
                chapter = chapters[canonical_unit]
                self.assertEqual(
                    ["reserved"],
                    [id_space["status"] for id_space in chapter["idSpaces"]],
                )
                self.assertEqual("reserved", chapter["maturity"]["state"]["status"])
                self.assertEqual("reserved", chapter["maturity"]["avg"]["status"])
                self.assertEqual("reserved", chapter["maturity"]["tables"])
                self.assertIsNone(chapter["sources"]["statePattern"])
                self.assertIsNone(chapter["sources"]["avgCurrent"])
                self.assertIsNone(chapter["sources"]["runtimeTables"])

    def test_canonical_unit_json_values_return_field_errors(self) -> None:
        for value in [None, False, 0, 1.5, "UnitX", [], {}]:
            with self.subTest(value=value):
                manifest = deepcopy(self.manifest)
                manifest["chapters"][0]["canonicalUnit"] = value
                self.assert_field_error(manifest, "chapters[0].canonicalUnit is invalid")

    def test_canonical_units_must_be_a_string_array(self) -> None:
        for value in [None, False, 0, 1.5, "Unit1", {}]:
            with self.subTest(field_value=value):
                manifest = deepcopy(self.manifest)
                manifest["policy"]["canonicalUnits"] = value
                self.assert_field_error(manifest, "policy.canonicalUnits must be an array")

        for value in [None, False, 0, 1.5, [], {}]:
            with self.subTest(element_value=value):
                manifest = deepcopy(self.manifest)
                manifest["policy"]["canonicalUnits"][0] = value
                self.assert_field_error(
                    manifest, "policy.canonicalUnits[0] must be a string"
                )

    def test_loop_status_json_values_return_field_errors(self) -> None:
        for component_name in ("state", "avg"):
            for value in [None, False, 0, 1.5, [], {}]:
                with self.subTest(component=component_name, value=value):
                    manifest = deepcopy(self.manifest)
                    manifest["chapters"][0]["maturity"][component_name]["status"] = value
                    self.assert_field_error(
                        manifest,
                        f"chapters[0].maturity.{component_name}.status is invalid",
                    )

    def test_flow_alias_json_values_return_field_errors(self) -> None:
        for field_name in ("name", "target"):
            for value in [None, False, 0, 1.5, [], {}]:
                with self.subTest(field=field_name, value=value):
                    manifest = deepcopy(self.manifest)
                    manifest["flowAliases"][0][field_name] = value
                    self.assert_field_error(
                        manifest, f"flowAliases[0].{field_name} must be a string"
                    )

    def test_history_must_be_an_array(self) -> None:
        for value in [None, False, 0, 1.5, "history", {}]:
            with self.subTest(value=value):
                manifest = deepcopy(self.manifest)
                manifest["chapters"][0]["history"] = value
                self.assert_field_error(manifest, "chapters[0].history must be an array")

    def test_cli_returns_one_for_invalid_json_value_types(self) -> None:
        self.manifest["chapters"][0]["canonicalUnit"] = []
        self.manifest["policy"]["canonicalUnits"][0] = []
        path = self.repo_root / "canon_manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        stderr = StringIO()

        try:
            with redirect_stderr(stderr):
                exit_code = main([str(path), "--repo-root", str(self.repo_root)])
        except TypeError as exc:
            self.fail(f"CLI leaked TypeError instead of returning 1: {exc}")

        self.assertEqual(1, exit_code)
        self.assertIn("chapters[0].canonicalUnit is invalid", stderr.getvalue())

    def test_updated_at_rejects_basic_iso_date(self) -> None:
        self.manifest["updatedAt"] = "20260711"

        self.assert_field_error(self.manifest, "updatedAt must be YYYY-MM-DD")

    def test_verified_at_rejects_basic_iso_date(self) -> None:
        self.manifest["chapters"][0]["maturity"]["verifiedAt"] = "20260711"

        self.assert_field_error(
            self.manifest, "chapters[0].maturity.verifiedAt must be YYYY-MM-DD"
        )

    def test_history_dates_reject_basic_iso_date(self) -> None:
        (self.repo_root / "history.md").write_text("# History\n", encoding="utf-8")
        self.manifest["chapters"][0]["history"] = [
            {"path": "history.md", "deprecatedDate": "20260711"}
        ]

        self.assert_field_error(
            self.manifest,
            "chapters[0].history[0].deprecatedDate must be YYYY-MM-DD or null",
        )

    def test_extra_unit6_is_rejected(self) -> None:
        extra = deepcopy(self.manifest["chapters"][-1])
        extra["canonicalUnit"] = "Unit6"
        extra["playerChapter"] = 6
        extra["unityEpisode"] = "EPI06"
        extra["aliases"] = []
        extra["idSpaces"][0]["range"] = "6xxx"
        extra["idSpaces"][0]["episode"] = "EPI06"
        self.manifest["chapters"].append(extra)
        self.manifest["policy"]["canonicalUnits"].append("Unit6")

        errors = self.errors_for(self.manifest)

        self.assertTrue(
            any("chapters[].canonicalUnit must be exactly Unit1-Unit5" in error for error in errors)
        )

    def test_missing_formal_unit_is_rejected(self) -> None:
        self.manifest["chapters"].pop()
        self.manifest["policy"]["canonicalUnits"].remove("Unit5")

        errors = self.errors_for(self.manifest)

        self.assertTrue(
            any("chapters[].canonicalUnit must be exactly Unit1-Unit5" in error for error in errors)
        )

    def test_duplicate_canonical_unit_is_rejected(self) -> None:
        duplicate = deepcopy(self.manifest["chapters"][0])
        duplicate["playerChapter"] = 6
        duplicate["unityEpisode"] = "EPI06"
        self.manifest["chapters"].append(duplicate)
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("duplicate canonicalUnit Unit1" in error for error in errors))

    def test_unit9_cannot_be_canonical(self) -> None:
        self.manifest["chapters"][0]["canonicalUnit"] = "Unit9"
        self.manifest["policy"]["canonicalUnits"][0] = "Unit9"
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("Unit9 cannot be canonical" in error for error in errors))

    def test_id_translation_policy_is_rejected(self) -> None:
        self.manifest["policy"]["automaticIdTranslation"] = True
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("automaticIdTranslation must be false" in error for error in errors))

    def test_unknown_flow_alias_target_is_rejected(self) -> None:
        self.manifest["flowAliases"][0]["target"] = "Unit99"
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("unknown target Unit99" in error for error in errors))

    def test_missing_current_source_is_rejected(self) -> None:
        self.manifest["chapters"][0]["sources"]["outline"] = "planning/missing.md"
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("sources.outline does not exist" in error for error in errors))

    def test_missing_planning_directory_is_rejected(self) -> None:
        self.manifest["chapters"][0]["planningDirectory"] = "missing-planning"
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("planningDirectory does not exist" in error for error in errors))

    def test_id_space_migration_must_preserve_ids(self) -> None:
        self.manifest["chapters"][0]["idSpaces"][0]["migration"] = "rewrite"
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("idSpaces[0].migration must be preserve" in error for error in errors))

    def test_reserved_missing_sources_are_allowed(self) -> None:
        chapter = self.manifest["chapters"][0]
        chapter["sources"]["statePattern"] = None
        chapter["sources"]["avgCurrent"] = None
        chapter["maturity"]["state"] = {
            "status": "reserved",
            "expectedLoops": 6,
            "presentLoops": [],
        }
        chapter["maturity"]["avg"] = {
            "status": "reserved",
            "expectedLoops": 6,
            "presentLoops": [],
        }
        self.assertEqual([], self.errors_for(self.manifest))

    def test_load_and_validate_raises_with_field_path(self) -> None:
        self.manifest["policy"]["idMigration"] = "rewrite"
        path = self.repo_root / "canon_manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        with self.assertRaisesRegex(ManifestValidationError, "policy.idMigration must be none"):
            load_and_validate_manifest(path, self.repo_root)


if __name__ == "__main__":
    unittest.main()
