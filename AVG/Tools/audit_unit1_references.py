#!/usr/bin/env python3
"""Audit current Unit1 authoring IDs against formal and preview configuration tables."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


UNIT1_ID = re.compile(r"(?<![A-Za-z0-9_])(?:1\d{8}|1\d{6}|1\d{5}|1[0-7]\d{2})(?!\d)")
LEGACY_ID = re.compile(r"(?<![A-Za-z0-9_])9(?:\d{8}|\d{6}|\d{5}|\d{3})(?!\d)")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}


def load_rebuilder(repo_root: Path):
    path = repo_root / "AVG" / "Tools" / "rebuild_unit1_runtime_script.py"
    spec = importlib.util.spec_from_file_location("unit1_rebuilder", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def walk_scalars(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_scalars(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_scalars(child)
    else:
        yield str(value)


def table_numeric_values(rebuilder, roots: list[Path]) -> set[str]:
    values: set[str] = set()
    for root in roots:
        for path in sorted(root.glob("*.json")):
            try:
                rows = rebuilder.load_unity_table(path)
            except (ValueError, json.JSONDecodeError):
                continue
            for value in walk_scalars(rows):
                if value.isdigit():
                    values.add(value)
    return values


def collect_references(repo_root: Path, roots: list[Path]):
    refs: dict[str, set[str]] = defaultdict(set)
    legacy: dict[str, set[str]] = defaultdict(set)
    for root in roots:
        paths = [root] if root.is_file() else root.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or "备份" in path.parts:
                continue
            text = path.read_text(encoding="utf-8-sig")
            relative = path.relative_to(repo_root).as_posix()
            for match in UNIT1_ID.finditer(text):
                refs[match.group()].add(relative)
            for match in LEGACY_ID.finditer(text):
                legacy[match.group()].add(relative)
    return refs, legacy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument("--unity-root", type=Path, default=Path(r"D:\NDC"))
    parser.add_argument(
        "--report",
        type=Path,
        default=repo_root / "AVG" / "对话配置工作及草稿" / "Unit1" / "Unit1_ID引用审查报告.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    rebuilder = load_rebuilder(repo_root)
    authoring_roots = [
        repo_root / "剧情设计" / "Unit1",
        repo_root / "avg_editor_v2" / "data" / "_table_drafts" / "Unit1",
    ]
    refs, legacy = collect_references(repo_root, authoring_roots)
    table_values = table_numeric_values(
        rebuilder,
        [args.unity_root.resolve() / "Assets" / "table", repo_root / "avg_editor_v2" / "data" / "table"],
    )
    unresolved = {
        entry_id: sorted(paths)
        for entry_id, paths in sorted(refs.items())
        if entry_id not in table_values
    }
    legacy_rows = {entry_id: sorted(paths) for entry_id, paths in sorted(legacy.items())}
    report = {
        "authoringRoots": [path.relative_to(repo_root).as_posix() for path in authoring_roots],
        "uniqueUnit1References": len(refs),
        "resolvedInFormalOrPreviewTables": len(refs) - len(unresolved),
        "unresolvedCount": len(unresolved),
        "unresolved": unresolved,
        "legacy9xxxCount": len(legacy_rows),
        "legacy9xxx": legacy_rows,
        "note": "Unresolved IDs may be design-only labels; each must be reviewed before claiming runtime coverage.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Unit1 references: {len(refs)}")
    print(f"Resolved in formal/preview tables: {len(refs) - len(unresolved)}")
    print(f"Unresolved: {len(unresolved)}")
    print(f"Legacy 9xxx references: {len(legacy_rows)}")
    print(f"Report: {args.report}")
    return 1 if legacy_rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
