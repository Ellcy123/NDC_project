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
EXPECTED_CANONICAL_UNITS = {f"Unit{unit}" for unit in range(1, 6)}
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
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
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
    if not isinstance(status, str) or status not in (
        LOOP_STATUSES_WITH_FILES | LOOP_STATUSES_WITHOUT_FILES
    ):
        errors.append(f"{field_path}.status is invalid")
    if type(expected) is not int or expected < 0:
        errors.append(f"{field_path}.expectedLoops must be a non-negative integer")
        return
    if not isinstance(present, list) or any(type(loop) is not int for loop in present):
        errors.append(f"{field_path}.presentLoops must be an integer array")
        return
    if len(present) != len(set(present)):
        errors.append(f"{field_path}.presentLoops contains duplicates")
    if any(loop < 1 or loop > expected for loop in present):
        errors.append(f"{field_path}.presentLoops contains an out-of-range loop")

    if isinstance(status, str) and status in LOOP_STATUSES_WITHOUT_FILES:
        if present:
            errors.append(f"{field_path}.presentLoops must be empty when {status}")
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
    chapter_alias_locations: dict[str, str] = {}
    chapter_alias_names: dict[str, set[str]] = {}
    chapter_alias_entries: list[tuple[str, str]] = []

    for index, chapter in enumerate(chapters):
        chapter_path = f"chapters[{index}]"
        if not isinstance(chapter, dict):
            errors.append(f"{chapter_path} must be an object")
            continue

        canonical = chapter.get("canonicalUnit")
        player_chapter = chapter.get("playerChapter")
        episode = chapter.get("unityEpisode")
        canonical_number: int | None = None
        if not isinstance(canonical, str) or not re.fullmatch(r"Unit[1-9][0-9]*", canonical):
            errors.append(f"{chapter_path}.canonicalUnit is invalid")
        else:
            canonical_number = int(canonical.removeprefix("Unit"))
            if canonical in canonical_units:
                errors.append(f"{chapter_path}: duplicate canonicalUnit {canonical}")
            if canonical in FORBIDDEN_CANONICAL_UNITS:
                errors.append(f"{chapter_path}: {canonical} cannot be canonical")
            else:
                canonical_units.add(canonical)

        if type(player_chapter) is not int or player_chapter < 1:
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

        if canonical_number is not None:
            if (
                type(player_chapter) is int
                and player_chapter >= 1
                and player_chapter != canonical_number
            ):
                errors.append(
                    f"{chapter_path}.playerChapter must equal {canonical_number} "
                    f"for canonicalUnit {canonical}"
                )
            expected_episode = f"EPI{canonical_number:02d}"
            if (
                isinstance(episode, str)
                and re.fullmatch(r"EPI[0-9]{2}", episode)
                and episode != expected_episode
            ):
                errors.append(
                    f"{chapter_path}.unityEpisode must equal {expected_episode} "
                    f"for canonicalUnit {canonical}"
                )

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
            aliases_for_chapter = []
        alias_names_for_chapter: set[str] = set()
        for alias_index, alias in enumerate(aliases_for_chapter):
            alias_path = f"{chapter_path}.aliases[{alias_index}]"
            if not isinstance(alias, dict):
                errors.append(f"{alias_path} must be an object")
                continue
            name = alias.get("name")
            role = alias.get("role")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{alias_path}.name must be a non-empty string")
            else:
                if name in chapter_alias_locations:
                    errors.append(f"{alias_path}.name duplicates alias {name}")
                else:
                    chapter_alias_locations[name] = alias_path
                alias_names_for_chapter.add(name)
                chapter_alias_entries.append((alias_path, name))
            if not isinstance(role, str) or not role.strip():
                errors.append(f"{alias_path}.role must be a non-empty string")
        if isinstance(canonical, str):
            chapter_alias_names[canonical] = alias_names_for_chapter

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

        history_entries = chapter.get("history")
        if not isinstance(history_entries, list):
            errors.append(f"{chapter_path}.history must be an array")
            history_entries = []
        for history_index, history in enumerate(history_entries):
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

    if canonical_units != EXPECTED_CANONICAL_UNITS:
        errors.append("chapters[].canonicalUnit must be exactly Unit1-Unit5")

    for alias_path, alias_name in chapter_alias_entries:
        if alias_name in canonical_units:
            errors.append(
                f"{alias_path}.name cannot shadow canonical unit {alias_name}"
            )

    declared_units = policy.get("canonicalUnits")
    if not isinstance(declared_units, list):
        errors.append("policy.canonicalUnits must be an array")
    else:
        declared_units_are_strings = True
        for unit_index, unit in enumerate(declared_units):
            if not isinstance(unit, str):
                errors.append(f"policy.canonicalUnits[{unit_index}] must be a string")
                declared_units_are_strings = False
        if declared_units_are_strings and set(declared_units) != canonical_units:
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
        if not isinstance(name, str):
            errors.append(f"{alias_path}.name must be a string")
        else:
            if name in alias_names:
                errors.append(f"{alias_path}: duplicate alias {name}")
            else:
                alias_names.add(name)
            if name in canonical_units:
                errors.append(f"{alias_path}.name cannot shadow canonical unit {name}")
        if not isinstance(target, str):
            errors.append(f"{alias_path}.target must be a string")
        elif target not in canonical_units:
            errors.append(f"{alias_path} has unknown target {target}")
        elif isinstance(name, str) and name not in chapter_alias_names.get(target, set()):
            errors.append(
                f"{alias_path}.name {name} is not declared in aliases for target {target}"
            )
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
