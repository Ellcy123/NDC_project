#!/usr/bin/env python3
"""
Unit2 MD -> AVG JSON wrapper.

This script is intentionally small: it reuses sync_to_json.py for parsing and
JSON writing, while adding Unit2/EPI02 defaults, speaker mapping, and state-vs-MD
preflight checks.

Default mode is dry-run. Use --write to actually create/update AVG/EPI02 JSON.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import sync_to_json as core


EPISODE = "EPI02"
UNIT_NAME = "Unit2"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
UNIT_MD_DIR = SCRIPT_DIR / UNIT_NAME
STATE_DIR = REPO_ROOT / "剧情设计" / UNIT_NAME / "state"


EPI02_SPEAKER_MAP = {
    # Main cast
    "扎克·布伦南": ("NPC201", "Zack Brennan"),
    "扎克": ("NPC201", "Zack Brennan"),
    "Zack": ("NPC201", "Zack Brennan"),
    "Zack Brennan": ("NPC201", "Zack Brennan"),

    "艾玛·奥马利": ("NPC202", "Emma O'Malley"),
    "艾玛": ("NPC202", "Emma O'Malley"),
    "Emma": ("NPC202", "Emma O'Malley"),
    "Emma O'Malley": ("NPC202", "Emma O'Malley"),

    "莫里森": ("NPC203", "Morrison"),
    "莫里森侦探": ("NPC203", "Morrison"),
    "Morrison": ("NPC203", "Morrison"),

    "Frank": ("NPC204", "Frank Kowalski"),
    "Frank Kowalski": ("NPC204", "Frank Kowalski"),
    "弗兰克": ("NPC204", "Frank Kowalski"),

    "米奇": ("NPC205", "Mickey Donnelly"),
    "米奇·唐纳利": ("NPC205", "Mickey Donnelly"),
    "Mickey": ("NPC205", "Mickey Donnelly"),
    "Mickey Donnelly": ("NPC205", "Mickey Donnelly"),

    "奥哈拉太太": ("NPC206", "Mrs. O'Hara"),
    "O'Hara": ("NPC206", "Mrs. O'Hara"),
    "Mrs. O'Hara": ("NPC206", "Mrs. O'Hara"),
    "Mrs. O’Hara": ("NPC206", "Mrs. O'Hara"),

    "伦纳德": ("NPC207", "Leonard Ross"),
    "伦纳德·罗斯": ("NPC207", "Leonard Ross"),
    "Leonard": ("NPC207", "Leonard Ross"),
    "Leonard Ross": ("NPC207", "Leonard Ross"),
    "Leonard Russo": ("NPC207", "Leonard Ross"),
    "Leon Russo": ("NPC207", "Leonard Ross"),

    "摩尔": ("NPC208", "Harold Moore"),
    "Harold Moore": ("NPC208", "Harold Moore"),
    "Moore": ("NPC208", "Harold Moore"),

    "托尼": ("NPC209", "Tony"),
    "Tony": ("NPC209", "Tony"),

    "维尼": ("NPC210", "Vinnie Moretti"),
    "Vinnie": ("NPC210", "Vinnie Moretti"),
    "Vinnie Moretti": ("NPC210", "Vinnie Moretti"),

    "丹尼": ("NPC211", "Danny Kowalski"),
    "丹尼·科瓦尔斯基": ("NPC211", "Danny Kowalski"),
    "Danny": ("NPC211", "Danny Kowalski"),
    "Danny Kowalski": ("NPC211", "Danny Kowalski"),

    "露拉": ("NPC212", "Lula Washington"),
    "Lula": ("NPC212", "Lula Washington"),
    "Lula Washington": ("NPC212", "Lula Washington"),

    "玛格丽特": ("NPC213", "Margaret Brennan"),
    "Margaret": ("NPC213", "Margaret Brennan"),
    "Margaret Brennan": ("NPC213", "Margaret Brennan"),

    "伊迪丝": ("NPC214", "Edith Ross"),
    "Edith": ("NPC214", "Edith Ross"),
    "Edith Ross": ("NPC214", "Edith Ross"),

    "福斯特": ("NPC215", "Foster"),
    "福斯特（电话中）": ("NPC215", "Foster"),
    "Foster": ("NPC215", "Foster"),
    "Dr. Foster": ("NPC215", "Foster"),

    # One-off display speakers. Empty IdSpeaker is intentional.
    "门卫": ("", "Guard"),
    "举报信": ("", "Report Letter"),
    "Frank写给Lula的情书": ("", "Frank's Letter"),
}


FIELD_REF_RE = re.compile(
    r"^\s*(?:talk|target_talk|next_talk|pre_expose_talk|prerequisite_talk):\s*([A-Za-z][A-Za-z0-9_]*)"
)
SECTION_RE = re.compile(r"^##\s+(Talk|Expose):\s*(\S+)\.json\s*$")
ENTRY_ID_RE = re.compile(r"^###\s+(\d+)\b")
SPEAKER_RE = re.compile(r"^\*\*(.+?)\*\*")


def configure_core() -> None:
    core.NPC_SPEAKER_MAP = EPI02_SPEAKER_MAP


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync Unit2 dialogue MD drafts to AVG/EPI02 JSON. Default is dry-run."
    )
    parser.add_argument("--loop", type=int, action="append", help="Loop number 1-6. Can be repeated.")
    parser.add_argument("--all", action="store_true", help="Process Loop1-6. Default when --loop is omitted.")
    parser.add_argument("--write", action="store_true", help="Actually write JSON. Omit for dry-run.")
    parser.add_argument("--numbered", action="store_true", help="Read Unit2/编号稿/LoopN_编号稿.md instead of original drafts.")
    parser.add_argument("--purge", action="store_true", help="In reconcile mode, delete stale JSON entries/files.")
    parser.add_argument("--skip-state-check", action="store_true", help="Skip state-vs-MD talk section check.")
    parser.add_argument("--skip-id-check", action="store_true", help="Allow MD without ### numeric IDs.")
    parser.add_argument("--no-reconcile", action="store_true", help="Use sync_to_json auto/new/sync mode instead of reconcile.")
    parser.add_argument("--mode", choices=["auto", "new-only", "sync-only"], default="auto",
                        help="Mode passed to sync_to_json.py when --no-reconcile is used.")
    return parser.parse_args()


def selected_loops(args: argparse.Namespace) -> list[int]:
    loops = args.loop or []
    if args.all or not loops:
        loops = list(range(1, 7))
    bad = [n for n in loops if n < 1 or n > 6]
    if bad:
        raise SystemExit(f"[ERR] Invalid loop number(s): {bad}. Expected 1-6.")
    return sorted(set(loops))


def md_path_for(loop_num: int, numbered: bool = False) -> Path:
    if numbered:
        return UNIT_MD_DIR / "编号稿" / f"Loop{loop_num}_编号稿.md"
    return UNIT_MD_DIR / f"Loop{loop_num}_生成草稿.md"


def state_path_for(loop_num: int) -> Path:
    return STATE_DIR / f"loop{loop_num}_state.yaml"


def md_sections(md_path: Path) -> set[str]:
    sections: set[str] = set()
    for line in md_path.read_text(encoding="utf-8").splitlines():
        match = SECTION_RE.match(line.strip())
        if match:
            sections.add(Path(match.group(2)).stem)
    return sections


def md_entry_count(md_path: Path) -> int:
    return sum(1 for line in md_path.read_text(encoding="utf-8").splitlines() if ENTRY_ID_RE.match(line))


def state_talk_refs(state_path: Path) -> set[str]:
    refs: set[str] = set()
    in_talk_sequence = False
    talk_sequence_indent = 0

    for raw_line in state_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        seq_match = re.match(r"^\s*talk_sequence:\s*$", line)
        if seq_match:
            in_talk_sequence = True
            talk_sequence_indent = indent
            continue

        if in_talk_sequence:
            if stripped and indent <= talk_sequence_indent:
                in_talk_sequence = False
            else:
                item_match = re.match(r"^\s*-\s*([A-Za-z][A-Za-z0-9_]*)\s*(?:#.*)?$", line)
                if item_match:
                    refs.add(item_match.group(1))
                continue

        field_match = FIELD_REF_RE.match(line)
        if field_match:
            ref = Path(field_match.group(1)).stem
            if ref != "null":
                refs.add(ref)

    return refs


def raw_speakers(md_path: Path) -> set[str]:
    speakers: set[str] = set()
    for line in md_path.read_text(encoding="utf-8").splitlines():
        match = SPEAKER_RE.match(line.strip())
        if match:
            speakers.add(match.group(1).strip())
    return speakers


def preflight(loop_num: int, args: argparse.Namespace) -> bool:
    md_path = md_path_for(loop_num, args.numbered)
    state_path = state_path_for(loop_num)
    ok = True

    print(f"\n[CHECK] Unit2 Loop{loop_num}")

    if not md_path.exists():
        print(f"  [ERR] Missing MD: {md_path}")
        return False

    sections = md_sections(md_path)
    entries = md_entry_count(md_path)
    print(f"  MD sections: {len(sections)}")
    print(f"  Numbered entries: {entries}")

    if entries == 0 and not args.skip_id_check:
        print("  [ERR] MD has no '### numeric id' dialogue entries.")
        print("        This script will not write JSON until IDs are assigned.")
        print("        Use --skip-id-check only for parser diagnostics; generated JSON would be empty.")
        ok = False

    if not args.skip_state_check:
        if not state_path.exists():
            print(f"  [ERR] Missing state: {state_path}")
            ok = False
        else:
            refs = state_talk_refs(state_path)
            missing = sorted(refs - sections)
            print(f"  State talk refs: {len(refs)}")
            if missing:
                print("  [ERR] State references not found in MD sections:")
                for ref in missing:
                    print(f"        - {ref}")
                ok = False
            else:
                print("  State refs: OK")

    unknown_speakers = sorted(sp for sp in raw_speakers(md_path) if core._lookup_speaker(sp) is None)
    if unknown_speakers:
        print("  [WARN] Unknown speakers; IdSpeaker will be blank if they become entries:")
        for sp in unknown_speakers:
            print(f"        - {sp}")

    return ok


def process_loop(loop_num: int, args: argparse.Namespace) -> bool:
    md_path = md_path_for(loop_num, args.numbered)
    if not preflight(loop_num, args):
        return False

    dry_run = not args.write
    if dry_run:
        print("  Mode: dry-run")
    else:
        print("  Mode: WRITE")

    if args.no_reconcile:
        core.process_single_md(md_path, EPISODE, dry_run=dry_run, mode=args.mode)
    else:
        core.reconcile_md_to_loop_dir(md_path, EPISODE, dry_run=dry_run, purge=args.purge)

    return True


def main() -> int:
    args = parse_args()
    configure_core()
    loops = selected_loops(args)

    print(f"[INFO] Unit2 -> {EPISODE}")
    print(f"[INFO] MD dir: {UNIT_MD_DIR / '编号稿' if args.numbered else UNIT_MD_DIR}")
    print(f"[INFO] Output: {SCRIPT_DIR.parent / EPISODE}")
    if not args.write:
        print("[INFO] Default dry-run. Add --write to create/update JSON.")

    results = [process_loop(loop_num, args) for loop_num in loops]
    if not all(results):
        print("\n[STOP] Preflight failed. No JSON was written.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
