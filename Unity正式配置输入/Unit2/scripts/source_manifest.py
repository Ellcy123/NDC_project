#!/usr/bin/env python3
"""Create and verify provenance for the isolated Unit2 formal-config snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


UNIT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = UNIT_ROOT.parents[1]
MANIFEST_PATH = UNIT_ROOT / "source_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def source_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []

    source_dialogue = PROJECT_ROOT / "AVG/对话配置工作及草稿/Unit2"
    derived_dialogue = UNIT_ROOT / "dialogue"
    for loop in range(1, 7):
        pairs.append(
            (
                source_dialogue / f"Loop{loop}_生成草稿.md",
                derived_dialogue / f"Loop{loop}_正式配置稿.md",
            )
        )

    source_state = PROJECT_ROOT / "剧情设计/Unit2/state"
    derived_state = UNIT_ROOT / "state"
    for loop in range(1, 7):
        pairs.append(
            (
                source_state / f"loop{loop}_state.yaml",
                derived_state / f"loop{loop}_state.yaml",
            )
        )

    source_planning = PROJECT_ROOT / "剧情设计/Unit2"
    derived_planning = UNIT_ROOT / "planning"
    for relative in relative_files(source_planning):
        pairs.append((source_planning / relative, derived_planning / relative))

    context_names = [
        ".briefing_L4.md",
        ".phase2a_L6.md",
        "Unit2_衔接伏笔表.md",
        "Unit2_角色进退场记录.md",
    ]
    for name in context_names:
        pairs.append(
            (
                source_dialogue / name,
                derived_planning / "dialogue_context" / name,
            )
        )

    pairs.extend(
        [
            (
                PROJECT_ROOT / "canon_manifest.json",
                derived_planning / "canon_manifest.json",
            ),
            (
                PROJECT_ROOT / "AVG/对话配置工作及草稿/assign_unit2_dialogue_ids.py",
                UNIT_ROOT / "scripts/assign_unit2_dialogue_ids.py",
            ),
            (
                PROJECT_ROOT / "AVG/对话配置工作及草稿/sync_to_json.py",
                UNIT_ROOT / "scripts/sync_to_json.py",
            ),
        ]
    )
    return pairs


def project_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def create_manifest() -> int:
    entries = []
    for source, derived in source_pairs():
        if not source.is_file():
            raise FileNotFoundError(f"Missing source: {source}")
        if not derived.is_file():
            raise FileNotFoundError(f"Missing derived copy: {derived}")
        source_hash = sha256(source)
        derived_hash = sha256(derived)
        if source_hash != derived_hash:
            raise ValueError(f"Initial copy differs: {source} -> {derived}")
        entries.append(
            {
                "source": str(source.relative_to(PROJECT_ROOT)),
                "derived": str(derived.relative_to(UNIT_ROOT)),
                "sourceSha256": source_hash,
                "initialCopySha256": derived_hash,
            }
        )

    manifest = {
        "schemaVersion": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sourceRepository": str(PROJECT_ROOT),
        "sourceCommit": project_commit(),
        "excludedSources": [
            "preview_new2/**",
            "avg_editor_v2/data/backup*/**",
        ],
        "files": entries,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Created {MANIFEST_PATH} with {len(entries)} source files")
    return 0


def verify_originals() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures = []
    for entry in manifest["files"]:
        source = PROJECT_ROOT / entry["source"]
        if not source.is_file():
            failures.append(f"missing: {entry['source']}")
            continue
        actual = sha256(source)
        if actual != entry["sourceSha256"]:
            failures.append(f"changed: {entry['source']}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print(f"PASS: {len(manifest['files'])} original files match source_manifest.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--create", action="store_true")
    action.add_argument("--verify-originals", action="store_true")
    args = parser.parse_args()
    return create_manifest() if args.create else verify_originals()


if __name__ == "__main__":
    raise SystemExit(main())
