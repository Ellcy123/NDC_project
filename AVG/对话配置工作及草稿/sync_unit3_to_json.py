#!/usr/bin/env python3
"""Sync Unit3 numbered dialogue drafts to AVG/EPI03 JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import assign_unit3_dialogue_ids as assigner
import sync_to_json as core


EPISODE = "EPI03"
SCRIPT_DIR = Path(__file__).resolve().parent
AVG_DIR = SCRIPT_DIR.parent
NUMBERED_DIR = SCRIPT_DIR / "Unit3" / "编号稿"

EPI03_SPEAKER_MAP = {
    "米奇·唐纳利": ("NPC301", "Mickey Donnelly"),
    "Mickey Donnelly": ("NPC301", "Mickey Donnelly"),
    "玛丽·史密斯": ("NPC302", "Mary Smith"),
    "Mary Smith": ("NPC302", "Mary Smith"),
    "莫里森警探": ("NPC303", "Morrison"),
    "莫里森": ("NPC303", "Morrison"),
    "Morrison": ("NPC303", "Morrison"),
    "福斯特医生": ("NPC304", "Foster"),
    "福斯特（电话中）": ("NPC304", "Foster"),
    "福斯特": ("NPC304", "Foster"),
    "Foster": ("NPC304", "Foster"),
    "海伦": ("NPC305", "Helen"),
    "Helen": ("NPC305", "Helen"),
    "伯纳德·威尔斯": ("NPC306", "Bernard"),
    "Bernard": ("NPC306", "Bernard"),
    "玛格丽特": ("NPC307", "Margaret Brennan"),
    "Margaret": ("NPC307", "Margaret Brennan"),
    "西莫斯·伯恩": ("NPC308", "Seamus"),
    "Seamus": ("NPC308", "Seamus"),
    "奥康奈尔神父": ("NPC309", "Priest"),
    "St.Patrick 神父": ("NPC309", "Priest"),
    "扎克·布伦南": ("NPC310", "Zack Brennan"),
    "Zack Brennan": ("NPC310", "Zack Brennan"),
    "艾玛·奥马利": ("NPC311", "Emma O'Malley"),
    "Emma O'Malley": ("NPC311", "Emma O'Malley"),
    "查尔斯·米勒": ("NPC312", "Charles Miller"),
    "Charles Miller": ("NPC312", "Charles Miller"),
    "哈里森法官": ("NPC313", "Harrison"),
    "Harrison": ("NPC313", "Harrison"),
    "伦纳德·罗索": ("NPC314", "Leonard Ross"),
    "Leonard Ross": ("NPC314", "Leonard Ross"),
}

SPEAKER_RE = re.compile(r"^\*\*(.+?)\*\*")
QUOTED_SPEAKER_RE = re.compile(r"^>\s+\*\*(.+?)\*\*")


def configure_core() -> None:
    core.NPC_SPEAKER_MAP = EPI03_SPEAKER_MAP


def raw_speakers(path: Path) -> set[str]:
    speakers = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = SPEAKER_RE.match(line.strip())
        if match:
            speakers.add(match.group(1).strip())
    return speakers


def unknown_speakers(path: Path) -> list[str]:
    configure_core()
    return sorted(
        speaker
        for speaker in raw_speakers(path)
        if core._lookup_speaker(speaker) is None
    )


def quoted_speaker_headers(path: Path) -> list[str]:
    malformed = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if QUOTED_SPEAKER_RE.match(line):
            malformed.append(f"{path.name}:{lineno}: {line.strip()}")
    return malformed


def numbered_path(loop: int) -> Path:
    return NUMBERED_DIR / f"Loop{loop}_编号稿.md"


def preflight(loop: int) -> list[str]:
    errors = []
    source = assigner.UNIT_DIR / f"Loop{loop}_生成草稿.md"
    numbered = numbered_path(loop)
    if not numbered.exists():
        errors.append(f"missing numbered draft: {numbered}")
        return errors

    if not re.search(r"^###\s+\d+", numbered.read_text(encoding="utf-8"), re.M):
        errors.append(f"numbered draft has no dialogue IDs: {numbered}")
    errors.extend(f"unknown speaker: {name}" for name in unknown_speakers(source))
    errors.extend(f"quoted speaker header: {row}" for row in quoted_speaker_headers(source))
    return errors


def is_expose_filename(filename: str) -> bool:
    return filename.lower().startswith("expose_l")


def reconcile_loop(loop: int, dry_run: bool, purge: bool) -> None:
    parsed = core.parse_md_file(numbered_path(loop))
    talk_buckets = {}
    expose_buckets = {}
    for filename, entries in parsed.items():
        target = expose_buckets if is_expose_filename(filename) else talk_buckets
        target[filename] = entries

    if talk_buckets:
        talk_dir = AVG_DIR / EPISODE / "Talk" / f"loop{loop}"
        core._reconcile_dir(
            talk_dir,
            talk_buckets,
            EPISODE,
            loop,
            dry_run,
            purge,
            is_expose=False,
        )

    if expose_buckets:
        expose_dir = AVG_DIR / EPISODE / "Expose"
        core._reconcile_dir(
            expose_dir,
            expose_buckets,
            EPISODE,
            loop,
            dry_run,
            purge,
            is_expose=True,
            scope_filter=lambda name: name.lower().startswith(f"expose_l{loop}_"),
        )


def branch_parameters_for_section(section) -> dict[str, list[dict[str, str]]]:
    label_map = assigner.core.build_label_map(section)
    parameters_by_id = {}
    for node in section.nodes:
        if not node.branch_options:
            continue
        parameters = []
        for option in node.branch_options:
            if option.label not in label_map:
                raise ValueError(
                    f"Missing branch target {option.label!r} in {section.filename}"
                )
            parameters.append(
                {
                    "ParameterStr": option.text,
                    "ParameterInt": str(label_map[option.label]),
                }
            )
        parameters_by_id[str(node.id)] = parameters
    return parameters_by_id


def goto_targets_for_section(section) -> dict[str, str]:
    label_map = assigner.core.build_label_map(section)
    targets_by_id = {}
    for node in section.nodes:
        if not node.goto:
            continue
        if node.goto not in label_map:
            raise ValueError(f"Missing goto target {node.goto!r} in {section.filename}")
        targets_by_id[str(node.id)] = str(label_map[node.goto])
    return targets_by_id


def apply_talk_flow_overrides(loops: list[int]) -> None:
    for loop in loops:
        for section in assigner.build_numbered_sections(loop):
            if section.kind != "Talk":
                continue
            parameters_by_id = branch_parameters_for_section(section)
            goto_targets_by_id = goto_targets_for_section(section)
            if not parameters_by_id and not goto_targets_by_id:
                continue

            path = AVG_DIR / EPISODE / "Talk" / f"loop{loop}" / f"{section.filename}.json"
            entries = json.loads(path.read_text(encoding="utf-8"))
            entries_by_id = {str(entry["id"]): entry for entry in entries}
            for talk_id, parameters in parameters_by_id.items():
                if talk_id not in entries_by_id:
                    raise ValueError(f"Missing Talk {talk_id} in {path}")
                entries_by_id[talk_id]["Parameters"] = parameters
            for talk_id, target_id in goto_targets_by_id.items():
                if talk_id not in entries_by_id:
                    raise ValueError(f"Missing Talk {talk_id} in {path}")
                entries_by_id[talk_id]["next"] = target_id
            path.write_text(
                json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def patch_entry(
    path: Path,
    predicate,
    *,
    next_id: str | None = None,
    scene_id: str,
) -> bool:
    entries = json.loads(path.read_text(encoding="utf-8"))
    matches = [entry for entry in entries if predicate(entry)]
    if len(matches) != 1:
        raise ValueError(f"Expected one transition anchor in {path}, found {len(matches)}")
    entry = matches[0]
    entry["script"] = "8"
    entry["ParameterStr0"] = scene_id
    if next_id is not None:
        entry["next"] = next_id
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def first_id(path: Path) -> str:
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not entries:
        raise ValueError(f"Empty dialogue JSON: {path}")
    return str(entries[0]["id"])


def apply_runtime_transitions() -> None:
    talk = AVG_DIR / EPISODE / "Talk"

    patch_entry(
        talk / "loop1" / "L1_opening_mickey.json",
        lambda entry: "到Zack 的侦探事务所了" in entry.get("cnWords", ""),
        scene_id="3018",
    )

    helen_room = talk / "loop3" / "L3_scene3008_helen_room.json"
    patch_entry(
        talk / "loop3" / "L3_scene3008_helen_encounter.json",
        lambda entry: entry.get("script") == "end",
        next_id=first_id(helen_room),
        scene_id="3308",
    )

    charles = talk / "loop5" / "L5_scene3009_charles.json"
    patch_entry(
        talk / "loop5" / "L5_opening.json",
        lambda entry: entry.get("script") == "end",
        next_id=first_id(charles),
        scene_id="3592",
    )
    patch_entry(
        charles,
        lambda entry: entry.get("script") == "end",
        scene_id="3514",
    )


def selected_loops(args: argparse.Namespace) -> list[int]:
    loops = args.loop or []
    if args.all or not loops:
        loops = list(range(1, 7))
    return sorted(set(loops))


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Unit3 numbered drafts to EPI03 JSON.")
    parser.add_argument("--loop", type=int, action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--purge", action="store_true")
    args = parser.parse_args()

    configure_core()
    loops = selected_loops(args)
    errors = [error for loop in loops for error in preflight(loop)]
    if errors:
        for error in errors:
            print(f"[ERR] {error}")
        return 1

    for loop in loops:
        mode = "WRITE" if args.write else "DRY"
        print(f"[{mode}] Unit3 Loop{loop} -> {EPISODE}")
        reconcile_loop(loop, dry_run=not args.write, purge=args.purge)

    if args.write:
        apply_talk_flow_overrides(loops)
        print("[WRITE] Applied Unit3 branch parameters and goto targets")
        if set(loops) == set(range(1, 7)):
            apply_runtime_transitions()
            print("[WRITE] Applied Unit3 scene transitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
