#!/usr/bin/env python3
r"""Safely sync editable Unit1 script text back to local AVG/EPI01 JSON.

Only localized ``Words`` values are writable. IDs, speakers, routing, scripts,
parameters, scene ownership, and runtime presentation fields are validated
against the existing strict-JSON AVG mirror and are never synthesized from MD.
The default mode is read-only; ``--write`` must be supplied explicitly.
This tool never writes to D:\NDC.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ENTRY_HEADING = re.compile(r"^###\s+(\d{6}|\d{9})(?:\s|$)")
SCENE_HEADING = re.compile(r"^##\s+[^:]+:\s+(.+?)\s*$")
NEXT_LINE = re.compile(r"^→\s+下一节点\s+`([^`]+)`\s*$")
SKIP_QUOTES = ("> EN:", "> EN·", "> - ", "> 系统", "> 指证", "> 设计标注")


@dataclass
class MdEntry:
    entry_id: str
    loop: str
    scene: str
    cn_words: str | None
    en_words: str | None
    next_value: str | None


def parse_markdown(path: Path) -> list[MdEntry]:
    loop_match = re.search(r"Loop([1-6])", path.stem, flags=re.IGNORECASE)
    if not loop_match:
        raise ValueError(f"Cannot infer loop from {path}")
    loop_name = f"loop{loop_match.group(1)}"
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    entries: list[MdEntry] = []
    current_scene = ""
    index = 0
    while index < len(lines):
        scene_match = SCENE_HEADING.match(lines[index])
        if scene_match:
            current_scene = scene_match.group(1).strip()
            index += 1
            continue
        entry_match = ENTRY_HEADING.match(lines[index])
        if not entry_match:
            index += 1
            continue
        entry_id = entry_match.group(1)
        block_end = index + 1
        while block_end < len(lines) and not ENTRY_HEADING.match(lines[block_end]) and not SCENE_HEADING.match(lines[block_end]):
            block_end += 1
        block = lines[index + 1:block_end]
        cn_parts: list[str] = []
        en_parts: list[str] = []
        next_value: str | None = None
        for line in block:
            next_match = NEXT_LINE.match(line)
            if next_match:
                next_value = next_match.group(1)
                continue
            if line.startswith("> EN: "):
                en_parts.append(line.removeprefix("> EN: "))
                continue
            if line.startswith("> EN· "):
                en_parts.append(line.removeprefix("> EN· "))
                continue
            if not line.startswith("> ") or line.startswith(SKIP_QUOTES):
                continue
            value = line.removeprefix("> ")
            if value != "（无台词）":
                cn_parts.append(value)
        entries.append(MdEntry(
            entry_id=entry_id,
            loop=loop_name,
            scene=current_scene,
            cn_words="\n".join(cn_parts) if cn_parts else None,
            en_words="\n".join(en_parts) if en_parts else None,
            next_value=next_value,
        ))
        index = block_end
    return entries


def load_avg(avg_dir: Path) -> tuple[dict[str, tuple[Path, dict[str, Any]]], list[Path]]:
    by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    paths = sorted((avg_dir / "Talk").rglob("*.json")) + sorted((avg_dir / "Expose").glob("*.json"))
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, list):
            raise ValueError(f"Expected array: {path}")
        for row in payload:
            entry_id = str(row.get("id", ""))
            if not entry_id:
                raise ValueError(f"Missing id: {path}")
            if entry_id in by_id:
                raise ValueError(f"Duplicate AVG id {entry_id}: {path} and {by_id[entry_id][0]}")
            by_id[entry_id] = (path, row)
    return by_id, paths


def set_localized_words(row: dict[str, Any], cn_words: str | None, en_words: str | None) -> bool:
    if cn_words is None and en_words is None:
        return False
    current = row.get("Words")
    words = list(current) if isinstance(current, list) else []
    while len(words) < 2:
        words.append("")
    changed = False
    if cn_words is not None and str(words[0]) != cn_words:
        words[0] = cn_words
        changed = True
    if en_words is not None and str(words[1]) != en_words:
        words[1] = en_words
        changed = True
    if changed:
        row["Words"] = words
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    repo_root = Path(__file__).resolve().parents[2]
    parser.add_argument("--md-dir", type=Path, default=repo_root / "AVG" / "对话配置工作及草稿" / "Unit1")
    parser.add_argument("--avg-dir", type=Path, default=repo_root / "AVG" / "EPI01")
    parser.add_argument("--write", action="store_true", help="Write text-only changes to local AVG/EPI01")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    md_paths = sorted(args.md_dir.glob("Loop[1-6]_完整台本.md"))
    if len(md_paths) != 6:
        raise FileNotFoundError(f"Expected six Loop scripts in {args.md_dir}, found {len(md_paths)}")
    md_entries = [entry for path in md_paths for entry in parse_markdown(path)]
    md_ids = [entry.entry_id for entry in md_entries]
    if len(md_ids) != len(set(md_ids)):
        raise ValueError("Duplicate dialogue IDs in Markdown")

    avg_by_id, json_paths = load_avg(args.avg_dir)
    missing_in_avg = sorted(set(md_ids) - set(avg_by_id))
    missing_in_md = sorted(set(avg_by_id) - set(md_ids))
    scene_mismatches: list[str] = []
    loop_mismatches: list[str] = []
    next_mismatches: list[str] = []
    changed_ids: list[str] = []
    touched_paths: set[Path] = set()

    for entry in md_entries:
        if entry.entry_id not in avg_by_id:
            continue
        path, row = avg_by_id[entry.entry_id]
        if str(row.get("videoScene", "")) != entry.scene:
            scene_mismatches.append(entry.entry_id)
        if str(row.get("videoLoop", "")).lower() != entry.loop:
            loop_mismatches.append(entry.entry_id)
        runtime_next = str(row.get("next", "")) or None
        if runtime_next != entry.next_value:
            next_mismatches.append(entry.entry_id)
        before = json.dumps(row.get("Words"), ensure_ascii=False)
        changed = set_localized_words(row, entry.cn_words, entry.en_words)
        if changed:
            changed_ids.append(entry.entry_id)
            touched_paths.add(path)
        if not args.write:
            # Restore the row so read-only verification has no in-memory side effects.
            previous = json.loads(before)
            if previous is None:
                row.pop("Words", None)
            else:
                row["Words"] = previous

    hard_errors = missing_in_avg + missing_in_md + scene_mismatches + loop_mismatches + next_mismatches
    print(f"Markdown entries: {len(md_entries)}")
    print(f"AVG entries: {len(avg_by_id)}")
    print(f"Missing in AVG: {len(missing_in_avg)}")
    print(f"Missing in Markdown: {len(missing_in_md)}")
    print(f"Scene mismatches: {len(scene_mismatches)}")
    print(f"Loop mismatches: {len(loop_mismatches)}")
    print(f"Routing mismatches: {len(next_mismatches)}")
    print(f"Text changes: {len(changed_ids)} across {len(touched_paths)} files")
    if hard_errors:
        print("ERROR IDs: " + ", ".join(sorted(set(hard_errors))))
        return 1

    if args.write and touched_paths:
        rows_by_path: dict[Path, list[dict[str, Any]]] = {}
        for path in json_paths:
            rows_by_path[path] = [row for source_path, row in avg_by_id.values() if source_path == path]
        for path in sorted(touched_paths):
            path.write_text(
                json.dumps(rows_by_path[path], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print("WRITE COMPLETE (local AVG/EPI01 only; Unity tables unchanged)")
    else:
        print("CHECK COMPLETE (no files written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
