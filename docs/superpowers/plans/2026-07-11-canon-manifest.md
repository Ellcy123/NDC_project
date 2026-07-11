# Canon Manifest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a machine-readable Canon Manifest that defines Unit1–Unit5 identity, sources, maturity, history, and U9/U10 aliases without migrating or translating any existing ID.

**Architecture:** `canon_manifest.json` is the sole authority for chapter identity and flow aliases. A dependency-free Python validator enforces structure, paths, history dates, and the no-ID-migration policy; `avg_editor_v2/build_unit_flow.py` consumes only chapter metadata and compatibility aliases while preserving all table IDs byte-for-byte. Documentation links to the Manifest instead of duplicating the mapping.

**Tech Stack:** JSON, Python 3.11 standard library, `unittest`, existing `avg_editor_v2/build_unit_flow.py`, Markdown.

## Global Constraints

- Canonical chapters are exactly `Unit1`, `Unit2`, `Unit3`, `Unit4`, and `Unit5`.
- `Unit9` is an active authoring alias of `Unit1`; `Unit10` is a source-title alias of `Unit2`; neither is an additional chapter.
- `policy.idMigration` is exactly `"none"` and `policy.automaticIdTranslation` is exactly `false`.
- Unit1 keeps authoring `EPI09` / `9xxx` and runtime `EPI01` / `1xxx` as separate preserved namespaces.
- Unit2 keeps current `EPI02` / `2xxx`; historical `10xxx` appears only in `history`.
- Unit4 / EPI04 / 4xxx and Unit5 / EPI05 / 5xxx are `reserved`, not implemented.
- No state, AVG, `avg_editor_v2/data/table/*.json`, or existing business ID may be edited.
- Do not run the builder with its default output path while `avg_editor_v2/data/formal/unit_flow.json` has unrelated user changes; tests must use temporary output paths.
- Stage and commit only files named by the current task; preserve all unrelated dirty-worktree changes.
- Local verification interpreter: `C:\Users\Ellcy\.local\bin\python3.11.exe` (Python 3.11.14).

---

## File Structure

- Create `canon_manifest.json`: chapter identity, source paths, maturity, history, tooling participation, and flow aliases.
- Create `scripts/validate_canon_manifest.py`: reusable loader/validator plus CLI; standard library only.
- Create `tests/test_canon_manifest.py`: validator behavior and repository Manifest tests.
- Create `tests/test_build_unit_flow_manifest.py`: builder metadata, alias, and no-ID-translation regression tests.
- Modify `avg_editor_v2/build_unit_flow.py`: load validated Manifest, derive unit labels, apply configured aliases, support temporary table/output paths.
- Modify `AGENTS.md`: replace obsolete Unit9/Unit10 independence rules with canonical mapping rules.
- Modify `README.md`: add one Canon Manifest entry; do not duplicate the full mapping.

---

### Task 1: Dependency-Free Manifest Validator

**Files:**
- Create: `scripts/validate_canon_manifest.py`
- Create: `tests/test_canon_manifest.py`

**Interfaces:**
- Consumes: a JSON object and a repository root `pathlib.Path`.
- Produces: `load_manifest(path: Path) -> dict[str, Any]`, `validate_manifest(data: dict[str, Any], repo_root: Path) -> list[str]`, and `load_and_validate_manifest(path: Path, repo_root: Path) -> dict[str, Any]`.
- CLI: `python scripts/validate_canon_manifest.py [manifest] [--repo-root PATH]` returns 0 on success and 1 on validation failure.

- [ ] **Step 1: Write validator behavior tests**

Create `tests/test_canon_manifest.py` with this complete initial content:

```python
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
```

- [ ] **Step 2: Run tests and verify the validator is absent**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -m unittest tests.test_canon_manifest -v
```

Expected: FAIL during import with `ModuleNotFoundError: No module named 'validate_canon_manifest'`.

- [ ] **Step 3: Implement the validator**

Create `scripts/validate_canon_manifest.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


SUPPORTED_SCHEMA_VERSION = 1
FORBIDDEN_CANONICAL_UNITS = {"Unit9", "Unit10"}
FORBIDDEN_MAPPING_KEYS = {"idMap", "idMappings", "idRewrite", "idTranslationRules"}
SOURCE_PATH_KEYS = ("outline", "avgCurrent", "tableDrafts", "runtimeTables")
LOOP_STATUSES_WITH_FILES = {"present"}
LOOP_STATUSES_WITHOUT_FILES = {"absent", "reserved"}


class ManifestValidationError(ValueError):
    """Raised when a Canon Manifest fails validation."""


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ManifestValidationError("manifest root must be a JSON object")
    return data


def _valid_date(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _walk_forbidden_keys(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in FORBIDDEN_MAPPING_KEYS:
                errors.append(f"{child_path} is forbidden because IDs are not translated")
            _walk_forbidden_keys(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_forbidden_keys(child, f"{path}[{index}]", errors)


def _validate_loop_component(
    chapter_path: str,
    component_name: str,
    component: Any,
    source_value: Any,
    repo_root: Path,
    errors: list[str],
) -> None:
    field_path = f"{chapter_path}.maturity.{component_name}"
    if not isinstance(component, dict):
        errors.append(f"{field_path} must be an object")
        return

    status = component.get("status")
    expected = component.get("expectedLoops")
    present = component.get("presentLoops")
    if status not in LOOP_STATUSES_WITH_FILES | LOOP_STATUSES_WITHOUT_FILES:
        errors.append(f"{field_path}.status is invalid")
    if not isinstance(expected, int) or expected < 0:
        errors.append(f"{field_path}.expectedLoops must be a non-negative integer")
        return
    if not isinstance(present, list) or any(not isinstance(loop, int) for loop in present):
        errors.append(f"{field_path}.presentLoops must be an integer array")
        return
    if len(present) != len(set(present)):
        errors.append(f"{field_path}.presentLoops contains duplicates")
    if any(loop < 1 or loop > expected for loop in present):
        errors.append(f"{field_path}.presentLoops contains an out-of-range loop")

    if status in LOOP_STATUSES_WITHOUT_FILES:
        if source_value is not None:
            errors.append(f"{chapter_path}.sources for {component_name} must be null when {status}")
        return

    if not isinstance(source_value, str) or not source_value:
        errors.append(f"{chapter_path}.sources for {component_name} must be a path")
        return

    if component_name == "state":
        if "{1-6}" not in source_value:
            errors.append(f"{chapter_path}.sources.statePattern must contain {{1-6}}")
            return
        for loop in present:
            state_path = repo_root / source_value.replace("{1-6}", str(loop))
            if not state_path.exists():
                errors.append(
                    f"{chapter_path}.sources.statePattern loop {loop} does not exist: {state_path}"
                )
    elif not (repo_root / source_value).exists():
        errors.append(f"{chapter_path}.sources.avgCurrent does not exist: {source_value}")


def validate_manifest(data: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    if data.get("schemaVersion") != SUPPORTED_SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SUPPORTED_SCHEMA_VERSION}")
    if not isinstance(data.get("updatedAt"), str) or not _valid_date(data.get("updatedAt")):
        errors.append("updatedAt must be YYYY-MM-DD")

    policy = data.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
        policy = {}
    if policy.get("idMigration") != "none":
        errors.append("policy.idMigration must be none")
    if policy.get("automaticIdTranslation") is not False:
        errors.append("policy.automaticIdTranslation must be false")

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        errors.append("chapters must be a non-empty array")
        chapters = []

    canonical_units: set[str] = set()
    player_chapters: set[int] = set()
    unity_episodes: set[str] = set()

    for index, chapter in enumerate(chapters):
        chapter_path = f"chapters[{index}]"
        if not isinstance(chapter, dict):
            errors.append(f"{chapter_path} must be an object")
            continue

        canonical = chapter.get("canonicalUnit")
        player_chapter = chapter.get("playerChapter")
        episode = chapter.get("unityEpisode")
        if canonical in canonical_units:
            errors.append(f"{chapter_path}: duplicate canonicalUnit {canonical}")
        if canonical in FORBIDDEN_CANONICAL_UNITS:
            errors.append(f"{chapter_path}: {canonical} cannot be canonical")
        if not isinstance(canonical, str) or not re.fullmatch(r"Unit[1-9][0-9]*", canonical):
            errors.append(f"{chapter_path}.canonicalUnit is invalid")
        elif canonical not in FORBIDDEN_CANONICAL_UNITS:
            canonical_units.add(canonical)

        if not isinstance(player_chapter, int) or player_chapter < 1:
            errors.append(f"{chapter_path}.playerChapter must be a positive integer")
        elif player_chapter in player_chapters:
            errors.append(f"{chapter_path}: duplicate playerChapter {player_chapter}")
        else:
            player_chapters.add(player_chapter)

        if not isinstance(episode, str) or not re.fullmatch(r"EPI[0-9]{2}", episode):
            errors.append(f"{chapter_path}.unityEpisode is invalid")
        elif episode in unity_episodes:
            errors.append(f"{chapter_path}: duplicate unityEpisode {episode}")
        else:
            unity_episodes.add(episode)

        planning_directory = chapter.get("planningDirectory")
        if not isinstance(planning_directory, str) or not planning_directory:
            errors.append(f"{chapter_path}.planningDirectory must be a path")
        elif not (repo_root / planning_directory).exists():
            errors.append(
                f"{chapter_path}.planningDirectory does not exist: {planning_directory}"
            )

        aliases_for_chapter = chapter.get("aliases")
        if not isinstance(aliases_for_chapter, list):
            errors.append(f"{chapter_path}.aliases must be an array")

        id_spaces = chapter.get("idSpaces")
        if not isinstance(id_spaces, list) or not id_spaces:
            errors.append(f"{chapter_path}.idSpaces must be a non-empty array")
        else:
            for id_index, id_space in enumerate(id_spaces):
                id_path = f"{chapter_path}.idSpaces[{id_index}]"
                if not isinstance(id_space, dict):
                    errors.append(f"{id_path} must be an object")
                    continue
                if id_space.get("migration") != "preserve":
                    errors.append(f"{id_path}.migration must be preserve")

        tooling = chapter.get("tooling")
        if not isinstance(tooling, dict) or not isinstance(tooling.get("buildUnitFlow"), bool):
            errors.append(f"{chapter_path}.tooling.buildUnitFlow must be boolean")

        sources = chapter.get("sources")
        if not isinstance(sources, dict):
            errors.append(f"{chapter_path}.sources must be an object")
            sources = {}
        for source_key in SOURCE_PATH_KEYS:
            source_value = sources.get(source_key)
            if source_value is None:
                continue
            if not isinstance(source_value, str) or not source_value:
                errors.append(f"{chapter_path}.sources.{source_key} must be a path or null")
            elif not (repo_root / source_value).exists():
                errors.append(f"{chapter_path}.sources.{source_key} does not exist: {source_value}")

        maturity = chapter.get("maturity")
        if not isinstance(maturity, dict):
            errors.append(f"{chapter_path}.maturity must be an object")
            maturity = {}
        if not isinstance(maturity.get("verifiedAt"), str) or not _valid_date(
            maturity.get("verifiedAt")
        ):
            errors.append(f"{chapter_path}.maturity.verifiedAt must be YYYY-MM-DD")
        _validate_loop_component(
            chapter_path,
            "state",
            maturity.get("state"),
            sources.get("statePattern"),
            repo_root,
            errors,
        )
        _validate_loop_component(
            chapter_path,
            "avg",
            maturity.get("avg"),
            sources.get("avgCurrent"),
            repo_root,
            errors,
        )

        for history_index, history in enumerate(chapter.get("history") or []):
            history_path = f"{chapter_path}.history[{history_index}]"
            if not isinstance(history, dict):
                errors.append(f"{history_path} must be an object")
                continue
            stored_path = history.get("path")
            if not isinstance(stored_path, str) or not (repo_root / stored_path).exists():
                errors.append(f"{history_path}.path does not exist: {stored_path}")
            for date_key in (
                "deprecatedDate",
                "archivedDate",
                "archivedSnapshotDate",
                "declarationCommitDate",
            ):
                if date_key in history and not _valid_date(history.get(date_key)):
                    errors.append(f"{history_path}.{date_key} must be YYYY-MM-DD or null")

    declared_units = policy.get("canonicalUnits")
    if not isinstance(declared_units, list) or set(declared_units) != canonical_units:
        errors.append("policy.canonicalUnits must exactly match chapters[].canonicalUnit")

    aliases = data.get("flowAliases")
    if not isinstance(aliases, list):
        errors.append("flowAliases must be an array")
        aliases = []
    alias_names: set[str] = set()
    for index, alias in enumerate(aliases):
        alias_path = f"flowAliases[{index}]"
        if not isinstance(alias, dict):
            errors.append(f"{alias_path} must be an object")
            continue
        name = alias.get("name")
        target = alias.get("target")
        if name in alias_names:
            errors.append(f"{alias_path}: duplicate alias {name}")
        elif isinstance(name, str):
            alias_names.add(name)
        if name in canonical_units:
            errors.append(f"{alias_path}.name cannot shadow canonical unit {name}")
        if target not in canonical_units:
            errors.append(f"{alias_path} has unknown target {target}")
        if not isinstance(alias.get("enabled"), bool):
            errors.append(f"{alias_path}.enabled must be boolean")

    _walk_forbidden_keys(data, "", errors)
    return errors


def load_and_validate_manifest(path: Path, repo_root: Path) -> dict[str, Any]:
    data = load_manifest(path)
    errors = validate_manifest(data, repo_root)
    if errors:
        raise ManifestValidationError("\n".join(errors))
    return data


def main(argv: list[str] | None = None) -> int:
    default_repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate NDC Canon Manifest")
    parser.add_argument("manifest", nargs="?", default=str(default_repo_root / "canon_manifest.json"))
    parser.add_argument("--repo-root", default=str(default_repo_root))
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest).resolve()
    repo_root = Path(args.repo_root).resolve()
    try:
        data = load_and_validate_manifest(manifest_path, repo_root)
    except (OSError, json.JSONDecodeError, ManifestValidationError) as exc:
        print(f"Canon manifest validation failed:\n{exc}", file=sys.stderr)
        return 1
    print(f"Canon manifest OK: {len(data['chapters'])} chapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run validator tests and verify they pass**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -m unittest tests.test_canon_manifest -v
```

Expected: 10 tests, all `ok`.

- [ ] **Step 5: Commit the validator task**

```powershell
git add -- scripts/validate_canon_manifest.py tests/test_canon_manifest.py
git commit -m "feat: add Canon Manifest validator"
```

Expected: commit contains exactly the two task files.

---

### Task 2: Repository Canon Manifest

**Files:**
- Create: `canon_manifest.json`
- Modify: `tests/test_canon_manifest.py`

**Interfaces:**
- Consumes: the schema enforced by `validate_manifest` from Task 1.
- Produces: a validated project registry for Unit1–Unit5 and one enabled `Unit9 -> Unit1` flow alias.

- [ ] **Step 1: Add a failing repository-manifest test**

Add this method to `CanonManifestValidationTests` in `tests/test_canon_manifest.py`:

```python
    def test_repository_manifest_is_valid_and_has_expected_identity(self) -> None:
        manifest_path = REPO_ROOT / "canon_manifest.json"
        data = load_and_validate_manifest(manifest_path, REPO_ROOT)
        chapters = {chapter["canonicalUnit"]: chapter for chapter in data["chapters"]}
        self.assertEqual(["Unit1", "Unit2", "Unit3", "Unit4", "Unit5"], data["policy"]["canonicalUnits"])
        self.assertEqual("EPI01", chapters["Unit1"]["unityEpisode"])
        self.assertEqual("EPI09", chapters["Unit1"]["idSpaces"][0]["episode"])
        self.assertEqual("2xxx", chapters["Unit2"]["idSpaces"][0]["range"])
        self.assertEqual("reserved", chapters["Unit4"]["idSpaces"][0]["status"])
        self.assertEqual("reserved", chapters["Unit5"]["idSpaces"][0]["status"])
        self.assertEqual("none", data["policy"]["idMigration"])
        self.assertFalse(data["policy"]["automaticIdTranslation"])
```

- [ ] **Step 2: Run the repository test and verify the file is absent**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -m unittest tests.test_canon_manifest.CanonManifestValidationTests.test_repository_manifest_is_valid_and_has_expected_identity -v
```

Expected: FAIL with `FileNotFoundError` for `canon_manifest.json`.

- [ ] **Step 3: Create the complete repository Manifest**

Create `canon_manifest.json` with this exact content:

```json
{
  "schemaVersion": 1,
  "updatedAt": "2026-07-11",
  "policy": {
    "idMigration": "none",
    "automaticIdTranslation": false,
    "canonicalUnits": [
      "Unit1",
      "Unit2",
      "Unit3",
      "Unit4",
      "Unit5"
    ]
  },
  "chapters": [
    {
      "canonicalUnit": "Unit1",
      "playerChapter": 1,
      "playerTitle": "黑哨之夜",
      "aliases": [
        {
          "name": "Unit9",
          "role": "active_authoring_alias"
        }
      ],
      "planningDirectory": "剧情设计/Unit1",
      "unityEpisode": "EPI01",
      "idSpaces": [
        {
          "scope": "authoring_state_and_avg",
          "range": "9xxx",
          "episode": "EPI09",
          "status": "current",
          "migration": "preserve"
        },
        {
          "scope": "runtime_tables",
          "range": "1xxx",
          "episode": "EPI01",
          "status": "current",
          "migration": "preserve"
        }
      ],
      "sources": {
        "outline": "剧情设计/Unit1/Unit1_大纲.md",
        "statePattern": "剧情设计/Unit1/state/loop{1-6}_state.yaml",
        "avgCurrent": "AVG/EPI09",
        "tableDrafts": "avg_editor_v2/data/_table_drafts/Unit9",
        "runtimeTables": "avg_editor_v2/data/table"
      },
      "maturity": {
        "phase": "active_iteration",
        "outline": "present_active",
        "state": {
          "status": "present",
          "expectedLoops": 6,
          "presentLoops": [1, 2, 3, 4, 5, 6]
        },
        "avg": {
          "status": "present",
          "expectedLoops": 6,
          "presentLoops": [1, 2, 3, 4, 5, 6]
        },
        "tables": "draft_and_runtime_mapping_present",
        "finality": "not_declared",
        "verifiedAt": "2026-07-11"
      },
      "tooling": {
        "buildUnitFlow": true
      },
      "history": [
        {
          "path": "AVG/EPI08",
          "status": "deprecated_retained",
          "deprecatedDate": null,
          "declarationCommit": "1abe679",
          "declarationCommitDate": "2026-04-23"
        },
        {
          "path": "旧文档/剧情设计废弃_20260612/Unit1",
          "status": "archived_snapshot",
          "archivedSnapshotDate": "2026-06-12",
          "deprecatedDate": null
        }
      ]
    },
    {
      "canonicalUnit": "Unit2",
      "playerChapter": 2,
      "playerTitle": "黄昏悲歌",
      "aliases": [
        {
          "name": "Unit10",
          "role": "source_title_alias"
        }
      ],
      "planningDirectory": "剧情设计/Unit2",
      "unityEpisode": "EPI02",
      "idSpaces": [
        {
          "scope": "current_authoring_and_runtime",
          "range": "2xxx",
          "episode": "EPI02",
          "status": "current",
          "migration": "preserve"
        }
      ],
      "sources": {
        "outline": "剧情设计/Unit2/Unit2_大纲.md",
        "statePattern": "剧情设计/Unit2/state/loop{1-6}_state.yaml",
        "avgCurrent": "AVG/EPI02",
        "tableDrafts": null,
        "runtimeTables": "avg_editor_v2/data/table"
      },
      "maturity": {
        "phase": "active_iteration",
        "outline": "present_draft_with_known_risks",
        "state": {
          "status": "present",
          "expectedLoops": 6,
          "presentLoops": [1, 2, 3, 4, 5, 6]
        },
        "avg": {
          "status": "present",
          "expectedLoops": 6,
          "presentLoops": [1, 2, 3, 4, 5, 6]
        },
        "tables": "present",
        "finality": "not_declared",
        "verifiedAt": "2026-07-11"
      },
      "tooling": {
        "buildUnitFlow": true
      },
      "history": [
        {
          "path": "旧文档/Unit2_重构前备份_20260519",
          "status": "archived",
          "archivedDate": "2026-05-19",
          "formerUnit": "Unit10",
          "formerEpisode": "EPI10",
          "formerIdRange": "10xxx",
          "migrationCommit": "42e935e"
        }
      ]
    },
    {
      "canonicalUnit": "Unit3",
      "playerChapter": 3,
      "playerTitle": "漫长的坠落",
      "aliases": [],
      "planningDirectory": "剧情设计/Unit3",
      "unityEpisode": "EPI03",
      "idSpaces": [
        {
          "scope": "current_authoring_and_tables",
          "range": "3xxx",
          "episode": "EPI03",
          "status": "current",
          "migration": "preserve"
        }
      ],
      "sources": {
        "outline": "剧情设计/Unit3/大纲0626.md",
        "statePattern": "剧情设计/Unit3/state/loop{1-6}_state.yaml",
        "avgCurrent": null,
        "tableDrafts": null,
        "runtimeTables": "avg_editor_v2/data/table"
      },
      "maturity": {
        "phase": "active_iteration",
        "outline": "present_active",
        "state": {
          "status": "present",
          "expectedLoops": 6,
          "presentLoops": [1, 2, 3, 4, 5, 6]
        },
        "avg": {
          "status": "absent",
          "expectedLoops": 6,
          "presentLoops": []
        },
        "tables": "design_rows_present_with_unresolved_entries",
        "finality": "not_declared",
        "verifiedAt": "2026-07-11"
      },
      "tooling": {
        "buildUnitFlow": false
      },
      "history": [
        {
          "path": "旧文档/Unit3_重构前备份_20260626",
          "status": "archived_snapshot",
          "archivedSnapshotDate": "2026-06-26",
          "deprecatedDate": null
        }
      ]
    },
    {
      "canonicalUnit": "Unit4",
      "playerChapter": 4,
      "playerTitle": "四十二层之前",
      "aliases": [],
      "planningDirectory": "剧情设计/Unit4",
      "unityEpisode": "EPI04",
      "idSpaces": [
        {
          "scope": "future_authoring_and_runtime",
          "range": "4xxx",
          "episode": "EPI04",
          "status": "reserved",
          "migration": "preserve"
        }
      ],
      "sources": {
        "outline": "剧情设计/Unit4/Unit4_大纲0710_逻辑重构版_v2.md",
        "statePattern": null,
        "avgCurrent": null,
        "tableDrafts": null,
        "runtimeTables": null
      },
      "maturity": {
        "phase": "outline_revision",
        "outline": "present_active",
        "structure": "5_loops_plus_non_loop_finale",
        "state": {
          "status": "reserved",
          "expectedLoops": 5,
          "presentLoops": []
        },
        "avg": {
          "status": "reserved",
          "expectedLoops": 5,
          "presentLoops": []
        },
        "tables": "reserved",
        "finality": "not_declared",
        "verifiedAt": "2026-07-11"
      },
      "tooling": {
        "buildUnitFlow": false
      },
      "history": []
    },
    {
      "canonicalUnit": "Unit5",
      "playerChapter": 5,
      "playerTitle": "系统没有主人",
      "aliases": [],
      "planningDirectory": "剧情设计/Unit5",
      "unityEpisode": "EPI05",
      "idSpaces": [
        {
          "scope": "future_authoring_and_runtime",
          "range": "5xxx",
          "episode": "EPI05",
          "status": "reserved",
          "migration": "preserve"
        }
      ],
      "sources": {
        "outline": "剧情设计/Unit5/Unit5_大纲_0601.md",
        "statePattern": null,
        "avgCurrent": null,
        "tableDrafts": null,
        "runtimeTables": null
      },
      "maturity": {
        "phase": "outline_draft",
        "outline": "present_active",
        "state": {
          "status": "reserved",
          "expectedLoops": 6,
          "presentLoops": []
        },
        "avg": {
          "status": "reserved",
          "expectedLoops": 6,
          "presentLoops": []
        },
        "tables": "reserved",
        "finality": "not_declared",
        "verifiedAt": "2026-07-11"
      },
      "tooling": {
        "buildUnitFlow": false
      },
      "history": []
    }
  ],
  "flowAliases": [
    {
      "name": "Unit9",
      "target": "Unit1",
      "enabled": true,
      "title": "黑哨之夜（正式配置映射 Unit1）",
      "reason": "Preserve current avg_editor flow lookup without changing IDs"
    }
  ]
}
```

- [ ] **Step 4: Run repository validation and all validator tests**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python scripts/validate_canon_manifest.py canon_manifest.json --repo-root .
& $python -m unittest tests.test_canon_manifest -v
```

Expected:

```text
Canon manifest OK: 5 chapters
Ran 11 tests
OK
```

- [ ] **Step 5: Commit the Manifest task**

```powershell
git add -- canon_manifest.json tests/test_canon_manifest.py
git commit -m "feat: register canonical chapter mapping"
```

Expected: commit contains exactly `canon_manifest.json` and the updated validator test.

---

### Task 3: Manifest-Driven Unit Flow Metadata

**Files:**
- Create: `tests/test_build_unit_flow_manifest.py`
- Modify: `avg_editor_v2/build_unit_flow.py:10-32`
- Modify: `avg_editor_v2/build_unit_flow.py:156-188`
- Modify: `avg_editor_v2/build_unit_flow.py:336-356`

**Interfaces:**
- Consumes: `load_and_validate_manifest()` from Task 1 and `chapters[].tooling.buildUnitFlow` plus `flowAliases[]` from Task 2.
- Produces: `unit_labels_from_manifest(manifest: dict) -> dict[str, dict]`, `apply_flow_aliases(units: dict, manifest: dict) -> dict`, and configurable `build(table_dir, out_path, manifest_path) -> dict`.
- Compatibility: default invocation still writes `avg_editor_v2/data/formal/unit_flow.json`; tests always pass a temporary `out_path`.

- [ ] **Step 1: Write builder regression tests**

Create `tests/test_build_unit_flow_manifest.py`:

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from avg_editor_v2 import build_unit_flow


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "canon_manifest.json"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class UnitFlowManifestTests(unittest.TestCase):
    def test_unit_labels_come_from_manifest(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        labels = build_unit_flow.unit_labels_from_manifest(manifest)
        self.assertEqual({"1", "2"}, set(labels))
        self.assertEqual("Unit1", labels["1"]["key"])
        self.assertEqual("黑哨之夜", labels["1"]["title"])
        self.assertEqual("EPI01", labels["1"]["chapter"])
        self.assertEqual("Unit2", labels["2"]["key"])
        self.assertEqual("EPI02", labels["2"]["chapter"])

    def test_flow_alias_preserves_every_business_id(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        units = {
            "Unit1": {
                "unit": "Unit1",
                "formalUnit": "Unit1",
                "chapter": "EPI01",
                "title": "黑哨之夜",
                "loops": [
                    {
                        "id": "loop1",
                        "chapterId": "101",
                        "initTalk": "101001001",
                        "initScene": "1103",
                        "doubts": [{"id": "1101"}],
                    }
                ],
            }
        }
        result = build_unit_flow.apply_flow_aliases(units, manifest)
        self.assertEqual("Unit1", result["Unit9"]["formalUnit"])
        self.assertEqual("EPI01", result["Unit9"]["chapter"])
        self.assertEqual("101001001", result["Unit9"]["loops"][0]["initTalk"])
        self.assertEqual("1103", result["Unit9"]["loops"][0]["initScene"])
        self.assertEqual("1101", result["Unit9"]["loops"][0]["doubts"][0]["id"])
        self.assertNotIn("Unit10", result)

    def test_build_uses_temp_output_and_keeps_ids(self) -> None:
        formal_output = Path(build_unit_flow.OUT_PATH)
        before = formal_output.read_bytes() if formal_output.exists() else None
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            table_dir = temp / "table"
            table_dir.mkdir()
            write_json(
                table_dir / "ChapterConfig.json",
                [
                    {
                        "id": "101",
                        "chapterTitle": ["Fixture Loop"],
                        "initTalk": "101001001",
                        "initScene": "1103",
                        "doubts": [],
                        "exposes": [],
                        "postExposeSegments": [],
                    }
                ],
            )
            for table_name in ("SceneConfig", "ItemStaticData", "TestimonyItem", "ArtAssetConfig"):
                write_json(table_dir / f"{table_name}.json", [])
            temp_output = temp / "unit_flow.json"
            payload = build_unit_flow.build(
                table_dir=str(table_dir),
                out_path=str(temp_output),
                manifest_path=str(MANIFEST_PATH),
            )
            self.assertTrue(temp_output.exists())
            self.assertEqual("101001001", payload["units"]["Unit1"]["loops"][0]["initTalk"])
            self.assertEqual("101001001", payload["units"]["Unit9"]["loops"][0]["initTalk"])
            self.assertEqual("1103", payload["units"]["Unit9"]["loops"][0]["initScene"])
        after = formal_output.read_bytes() if formal_output.exists() else None
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run builder tests and verify missing interfaces**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -m unittest tests.test_build_unit_flow_manifest -v
```

Expected: FAIL with `AttributeError` for `unit_labels_from_manifest`.

- [ ] **Step 3: Add Manifest loading and configurable paths**

In `avg_editor_v2/build_unit_flow.py`, replace the import/constants block at lines 10–24 with:

```python
import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
TABLE_DIR = os.path.join(HERE, "data", "table")
OUT_DIR = os.path.join(HERE, "data", "formal")
OUT_PATH = os.path.join(OUT_DIR, "unit_flow.json")
CANON_MANIFEST_PATH = os.path.join(REPO_ROOT, "canon_manifest.json")
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from validate_canon_manifest import load_and_validate_manifest  # noqa: E402
```

Replace `load_table()` with:

```python
def load_table(name: str, table_dir: str = TABLE_DIR):
    path = os.path.join(table_dir, f"{name}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
```

Add these functions immediately before `build()`:

```python
def unit_labels_from_manifest(manifest: dict) -> dict[str, dict]:
    labels: dict[str, dict] = {}
    for chapter in manifest["chapters"]:
        if not chapter["tooling"]["buildUnitFlow"]:
            continue
        canonical_unit = chapter["canonicalUnit"]
        unit_number = canonical_unit.removeprefix("Unit")
        labels[unit_number] = {
            "key": canonical_unit,
            "title": chapter["playerTitle"],
            "chapter": chapter["unityEpisode"],
        }
    return labels


def apply_flow_aliases(units: dict[str, dict], manifest: dict) -> dict[str, dict]:
    for alias_config in manifest["flowAliases"]:
        if not alias_config["enabled"]:
            continue
        alias_name = alias_config["name"]
        target_name = alias_config["target"]
        if target_name not in units:
            raise ValueError(f"flow alias {alias_name} target {target_name} was not built")
        alias = deepcopy(units[target_name])
        alias["unit"] = alias_name
        alias["formalUnit"] = target_name
        alias["title"] = alias_config["title"]
        units[alias_name] = alias
    return units
```

Change the start of `build()` to:

```python
def build(
    table_dir: str = TABLE_DIR,
    out_path: str = OUT_PATH,
    manifest_path: str = CANON_MANIFEST_PATH,
):
    manifest = load_and_validate_manifest(Path(manifest_path), Path(REPO_ROOT))
    unit_labels = unit_labels_from_manifest(manifest)
    chapters = load_table("ChapterConfig", table_dir)
    scenes = load_table("SceneConfig", table_dir)
    items = load_table("ItemStaticData", table_dir)
    testimonies = load_table("TestimonyItem", table_dir)
    art_assets = load_table("ArtAssetConfig", table_dir)
```

Within `build()`, replace every reference to `UNIT_LABELS` with `unit_labels`:

```python
    units: dict[str, dict] = {}
    for unit_num, meta in unit_labels.items():
        units[meta["key"]] = {
            "unit": meta["key"],
            "formalUnit": meta["key"],
            "chapter": meta["chapter"],
            "title": meta["title"],
            "loops": [],
        }

    for ch in sorted(chapters, key=lambda c: first_number(c.get("id"))):
        unit_num, loop_num = unit_loop_from_chapter(ch.get("id"))
        if not unit_num or unit_num not in unit_labels:
            continue
        unit_key = unit_labels[unit_num]["key"]
```

Replace the hardcoded Unit9 alias block at lines 336–344 with:

```python
    apply_flow_aliases(units, manifest)
```

Replace the output block with:

```python
    output_dir = os.path.dirname(out_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload
```

Leave the `__main__` block using default paths; do not run it during this task.

- [ ] **Step 4: Run builder and validator tests**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -m unittest tests.test_build_unit_flow_manifest tests.test_canon_manifest -v
```

Expected: 14 tests, all `ok`; the test asserts the existing formal `unit_flow.json` bytes are unchanged.

- [ ] **Step 5: Confirm the hardcoded mapping is gone**

Run:

```powershell
rg -n "Design alias|units\[\"Unit9\"\]|UNIT_LABELS" avg_editor_v2/build_unit_flow.py
```

Expected: no matches and exit code 1.

- [ ] **Step 6: Commit the builder task**

```powershell
git add -- avg_editor_v2/build_unit_flow.py tests/test_build_unit_flow_manifest.py
git commit -m "refactor: load unit flow identity from Canon Manifest"
```

Expected: commit contains exactly the builder and its new test.

---

### Task 4: Canonical Mapping Documentation

**Files:**
- Modify: `AGENTS.md:9-19`
- Modify: `README.md:15-23`

**Interfaces:**
- Consumes: `canon_manifest.json` as the single detailed mapping source.
- Produces: concise human entry points; no duplicated maturity table.

- [ ] **Step 1: Replace the obsolete AGENTS mapping section**

Replace `AGENTS.md` lines 9–19 with:

```markdown
## Canon 章节映射（重要）

章节身份、来源路径、完成度和历史版本的机器可读真源是仓库根目录的 `canon_manifest.json`。涉及 Unit / Episode / ID 段判断时，先读取该文件，不凭目录名猜测。

- 玩家第 1 章的正式身份是 Unit1，现行策划别名是 Unit9；玩家第 2 章的正式身份是 Unit2，现行策划标题别名是 Unit10。
- Unit9、Unit10 不计作额外章节。现行策划内容直接位于 `剧情设计/Unit1`、`剧情设计/Unit2`。
- Unit1 的策划 state 与 AVG/EPI09 保留 9xxx，Unity／正式表保留 EPI01 与 1xxx；两套 ID 不迁移、不自动转换。
- Unit2 当前保留 EPI02 与 2xxx；10xxx 只作为 Manifest 中的历史命名空间记录。
- 旧版内容只从 Manifest 的 `history[]` 所列归档路径读取，不能把归档内容当作当前既定事实。
```

- [ ] **Step 2: Add the README entry without duplicating the table**

Insert this section after the content declaration and before `## Preview 预览工具`:

```markdown
## Canon 章节映射

项目当前以 Unit1–Unit5 为正式章节身份；Unit9 是 Unit1 的现行策划别名，Unit10 是 Unit2 的策划标题别名。完整的 Episode、ID 命名空间、内容来源、完成度及历史版本以 [`canon_manifest.json`](canon_manifest.json) 为准。现有 ID 不迁移、不自动转换。
```

- [ ] **Step 3: Verify documentation points to one source**

Run:

```powershell
rg -n "canon_manifest.json|Unit9|Unit10|不迁移|不自动转换" AGENTS.md README.md
```

Expected:

- `AGENTS.md` contains the Manifest authority rule and five mapping bullets.
- `README.md` contains one short Canon section.
- The old sentence `把 Unit9 / Unit10 当作独立的新章节处理` has no match.

- [ ] **Step 4: Commit the documentation task**

```powershell
git add -- AGENTS.md README.md
git commit -m "docs: define canonical Unit1 and Unit2 aliases"
```

Expected: commit contains exactly `AGENTS.md` and `README.md`.

---

### Task 5: Full Verification and Safety Audit

**Files:**
- Verify only; no production-file edits.

**Interfaces:**
- Consumes: all implementation tasks.
- Produces: evidence that the Manifest is valid, tests pass, hardcoding is removed, and protected content was not touched by the implementation.

- [ ] **Step 1: Run the complete focused test suite**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -m unittest discover -s tests -p 'test_*manifest*.py' -v
```

Expected: 14 tests, all `ok`.

- [ ] **Step 2: Run the production Manifest validator**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python scripts/validate_canon_manifest.py canon_manifest.json --repo-root .
```

Expected: `Canon manifest OK: 5 chapters`.

- [ ] **Step 3: Check JSON and Python syntax independently**

Run:

```powershell
$python = 'C:\Users\Ellcy\.local\bin\python3.11.exe'
& $python -c "import json, pathlib; json.loads(pathlib.Path('canon_manifest.json').read_text(encoding='utf-8'))"
& $python -m py_compile scripts/validate_canon_manifest.py avg_editor_v2/build_unit_flow.py tests/test_canon_manifest.py tests/test_build_unit_flow_manifest.py
```

Expected: both commands exit 0 without output.

- [ ] **Step 4: Check formatting and expected implementation files**

Run:

```powershell
git diff --check
git status --short -- canon_manifest.json scripts/validate_canon_manifest.py tests/test_canon_manifest.py tests/test_build_unit_flow_manifest.py avg_editor_v2/build_unit_flow.py AGENTS.md README.md
```

Expected: no whitespace errors; only the seven approved implementation paths appear if commits have not yet been made.

- [ ] **Step 5: Verify protected content remains outside all task commits**

Run:

```powershell
git log --name-only --pretty=format: -4 | Where-Object { $_ } | Sort-Object -Unique
```

Expected committed implementation paths are limited to:

```text
AGENTS.md
README.md
avg_editor_v2/build_unit_flow.py
canon_manifest.json
scripts/validate_canon_manifest.py
tests/test_build_unit_flow_manifest.py
tests/test_canon_manifest.py
```

The output must not contain `AVG/`, `剧情设计/*/state/`, `avg_editor_v2/data/table/`, or `avg_editor_v2/data/formal/unit_flow.json`. Existing unrelated dirty-worktree files may still appear in `git status`; do not stage, reset, clean, or modify them.

- [ ] **Step 6: Review the final diff against the approved design**

Run:

```powershell
git show --stat --oneline HEAD~3..HEAD
rg -n '"idMigration": "none"|"automaticIdTranslation": false|"canonicalUnit": "Unit[1-5]"|"name": "Unit9"|"target": "Unit1"' canon_manifest.json
```

Expected: four small implementation commits and explicit proof of the no-migration policy, five canonical units, and one Unit9 flow alias.
