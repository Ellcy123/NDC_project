#!/usr/bin/env python3
"""Assign stable Unit3 dialogue IDs without modifying the source drafts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import assign_unit2_dialogue_ids as core


SCRIPT_DIR = Path(__file__).resolve().parent
UNIT_DIR = SCRIPT_DIR / "Unit3"
OUT_DIR = UNIT_DIR / "编号稿"

# The owner selects the first three digits of a nine-digit Talk ID. Openings
# use Zack, matching Unit2's convention. Expose IDs use their own 3Lxxxx range.
SECTION_OWNER = {
    "L1_opening_mickey": 310,
    "L1_scene3005_foster": 304,
    "L1_scene3004_morrison": 303,
    "L2_opening_talk": 310,
    "L2_scene3013_mary": 302,
    "L2_scene3007_priest": 309,
    "L3_opening": 310,
    "L3_scene3008_helen_encounter": 305,
    "L3_scene3008_helen_room": 305,
    "L3_scene3009_bernard": 306,
    "L3_scene3006_seamus": 308,
    "L4_opening": 310,
    "L4_scene3005_foster": 304,
    "L4_scene3010_margaret": 307,
    "L4_scene3008_helen_opening": 305,
    "L4_postexpose_mickey": 301,
    "L4_postexpose_mary": 302,
    "L5_opening": 310,
    "L5_scene3009_charles": 312,
    "L5_scene3014_bernard": 306,
    "L5_scene3008_helen": 305,
    "L6_opening": 310,
    "L6_scene3005_foster": 304,
    "L6_scene3006_seamus": 308,
    "L6_ending_emma": 311,
    "L6_ending_leonard": 314,
}

EXPOSE_OWNER = {
    "L1_expose_morrison": "morrison",
    "L2_expose_mary": "mary",
    "L3_expose_helen": "helen",
    "L4_expose_helen": "helen",
    "L5_expose_bernard": "bernard",
    "L6_expose_mickey": "mickey",
}

DESCRIPTIVE_EXPOSE_HEADING_RE = re.compile(
    r"^##\s+(?:§\d+\.?\s*)?Expose\s*[—\-–]+"
)


def make_expose_id(loop: int, seq: int) -> int:
    return int(f"3{loop}{seq:04d}")


def base_for_section(
    section: core.Section,
    used_conv: dict[int, set[int]],
) -> tuple[int, int]:
    stem = Path(section.filename).stem
    if stem not in SECTION_OWNER:
        raise ValueError(f"Unit3 Talk section has no ID owner: {stem}")

    npc = SECTION_OWNER[stem]
    conv = section.loop
    used = used_conv.setdefault(npc, set())
    if conv in used:
        conv += 100
        while conv in used:
            conv += 100
    used.add(conv)
    return npc, conv


def normalize_expose_filename(section: core.Section) -> None:
    old_stem = Path(section.filename).stem
    npc = EXPOSE_OWNER.get(old_stem)
    if not npc:
        raise ValueError(f"Unit3 Expose section has no runtime filename: {old_stem}")
    new_stem = f"Expose_L{section.loop}_{npc}"
    section.filename = new_stem
    section.prelude = [
        re.sub(
            r"^##\s+Expose:\s*\S+\.json\s*$",
            f"## Expose: {new_stem}.json",
            line,
        )
        for line in section.prelude
    ]


def hide_descriptive_expose_headings(section: core.Section) -> None:
    section.prelude = [
        f"<!-- {line[3:].strip()} -->"
        if DESCRIPTIVE_EXPOSE_HEADING_RE.match(line)
        else line
        for line in section.prelude
    ]


def build_numbered_sections(loop: int) -> list[core.Section]:
    source = UNIT_DIR / f"Loop{loop}_生成草稿.md"
    if not source.exists():
        raise FileNotFoundError(source)

    sections = core.parse_sections(source)
    for section in sections:
        hide_descriptive_expose_headings(section)
        if section.kind == "Expose":
            normalize_expose_filename(section)

    core.split_line_nodes(sections)
    original_base = core.base_for_section
    original_expose_id = core.make_expose_id
    try:
        core.base_for_section = base_for_section
        core.make_expose_id = make_expose_id
        core.assign_ids(sections)
    finally:
        core.base_for_section = original_base
        core.make_expose_id = original_expose_id
    return sections


def render_numbered(loop: int, sections: list[core.Section]) -> str:
    source = UNIT_DIR / f"Loop{loop}_生成草稿.md"
    rendered = core.render(sections, source)
    rendered = rendered.replace(
        f"# Unit2 Loop{loop} 对白编号稿",
        f"# Unit3 Loop{loop} 对白编号稿",
        1,
    )
    rendered = rendered.replace(
        "> 用途：派生编号稿，给 Unit2 对话 JSON 同步流程读取。",
        "> 用途：派生编号稿，给 Unit3 对话 JSON 同步流程读取。",
        1,
    )
    return rendered


def process_loop(loop: int, write: bool) -> tuple[Path, str]:
    sections = build_numbered_sections(loop)
    rendered = render_numbered(loop, sections)
    output = OUT_DIR / f"Loop{loop}_编号稿.md"
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return output, rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign Unit3 dialogue IDs.")
    parser.add_argument("--loop", type=int, action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    loops = args.loop or []
    if args.all or not loops:
        loops = list(range(1, 7))

    seen: set[str] = set()
    for loop in sorted(set(loops)):
        output, rendered = process_loop(loop, write=not args.dry_run)
        ids = re.findall(r"^###\s+(\d+)", rendered, flags=re.M)
        duplicates = sorted(set(ids) & seen)
        if duplicates:
            raise ValueError(f"Cross-loop duplicate IDs: {', '.join(duplicates)}")
        seen.update(ids)
        mode = "DRY" if args.dry_run else "WRITE"
        section_count = rendered.count("## Talk:") + rendered.count("## Expose:")
        print(f"[{mode}] Loop{loop}: {output} sections={section_count} ids={len(ids)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
