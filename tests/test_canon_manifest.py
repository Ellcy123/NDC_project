from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_canon_manifest import (  # noqa: E402
    ManifestValidationError,
    load_and_validate_manifest,
    validate_manifest,
)


def make_valid_manifest(repo_root: Path) -> dict:
    (repo_root / "planning" / "state").mkdir(parents=True)
    (repo_root / "planning" / "outline.md").write_text("# Outline\n", encoding="utf-8")
    for loop in range(1, 7):
        (repo_root / "planning" / "state" / f"loop{loop}_state.yaml").write_text(
            f"loop: {loop}\n", encoding="utf-8"
        )
    (repo_root / "AVG" / "EPI01").mkdir(parents=True)
    (repo_root / "tables").mkdir()

    return {
        "schemaVersion": 1,
        "updatedAt": "2026-07-11",
        "policy": {
            "idMigration": "none",
            "automaticIdTranslation": False,
            "canonicalUnits": ["Unit1"],
        },
        "chapters": [
            {
                "canonicalUnit": "Unit1",
                "playerChapter": 1,
                "playerTitle": "Test Chapter",
                "aliases": [{"name": "Unit9", "role": "active_authoring_alias"}],
                "planningDirectory": "planning",
                "unityEpisode": "EPI01",
                "idSpaces": [
                    {
                        "scope": "current_authoring_and_runtime",
                        "range": "1xxx",
                        "episode": "EPI01",
                        "status": "current",
                        "migration": "preserve",
                    }
                ],
                "sources": {
                    "outline": "planning/outline.md",
                    "statePattern": "planning/state/loop{1-6}_state.yaml",
                    "avgCurrent": "AVG/EPI01",
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
        ],
        "flowAliases": [
            {
                "name": "Unit9",
                "target": "Unit1",
                "enabled": True,
                "title": "Test Chapter (Unit1 mapping)",
                "reason": "Compatibility",
            }
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

    def test_valid_manifest_has_no_errors(self) -> None:
        self.assertEqual([], self.errors_for(self.manifest))

    def test_duplicate_canonical_unit_is_rejected(self) -> None:
        duplicate = deepcopy(self.manifest["chapters"][0])
        duplicate["playerChapter"] = 2
        duplicate["unityEpisode"] = "EPI02"
        self.manifest["chapters"].append(duplicate)
        errors = self.errors_for(self.manifest)
        self.assertTrue(any("duplicate canonicalUnit Unit1" in error for error in errors))

    def test_unit9_cannot_be_canonical(self) -> None:
        self.manifest["chapters"][0]["canonicalUnit"] = "Unit9"
        self.manifest["policy"]["canonicalUnits"] = ["Unit9"]
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
