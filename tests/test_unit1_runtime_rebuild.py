from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "AVG" / "Tools" / "rebuild_unit1_runtime_script.py"
SPEC = importlib.util.spec_from_file_location("rebuild_unit1_runtime_script", MODULE_PATH)
assert SPEC and SPEC.loader
rebuild = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rebuild
SPEC.loader.exec_module(rebuild)

MIGRATION_MODULE_PATH = ROOT / "AVG" / "Tools" / "migrate_unit1_authoring_ids.py"
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "migrate_unit1_authoring_ids", MIGRATION_MODULE_PATH
)
assert MIGRATION_SPEC and MIGRATION_SPEC.loader
migration = importlib.util.module_from_spec(MIGRATION_SPEC)
sys.modules[MIGRATION_SPEC.name] = migration
MIGRATION_SPEC.loader.exec_module(migration)


class Unit1RuntimeRebuildTests(unittest.TestCase):
    def test_formalizes_business_ids_inside_trusted_annotations(self) -> None:
        text, count = rebuild.formalize_annotation_ids(
            "委托协议书（9103）、证词 9031002、指证 910001、对话 904001001"
        )
        self.assertEqual(
            "委托协议书（1103）、证词 1031002、指证 110001、对话 104001001",
            text,
        )
        self.assertEqual(4, count)

    def test_preserves_real_asset_keys_and_source_paths(self) -> None:
        text, count = rebuild.formalize_annotation_ids(
            "SC9003_item_01 / EPI09/static / archive_9103 / 1920"
        )
        self.assertEqual("SC9003_item_01 / EPI09/static / archive_9103 / 1920", text)
        self.assertEqual(0, count)


class Unit1AuthoringMigrationScopeTests(unittest.TestCase):
    def test_accepts_only_explicit_unit1_authoring_roots(self) -> None:
        migration.validate_root_scope(
            ROOT,
            [
                ROOT / "剧情设计" / "Unit1",
                ROOT / "avg_editor_v2" / "data" / "_table_drafts" / "Unit1",
            ],
        )

    def test_rejects_repository_and_tooling_roots(self) -> None:
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            migration.validate_root_scope(ROOT, [ROOT])
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            migration.validate_root_scope(ROOT, [ROOT / ".agents"])


if __name__ == "__main__":
    unittest.main()
