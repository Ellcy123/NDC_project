#!/usr/bin/env python3
"""Migrate current Unit1 authoring text from the old 9xxx namespace to 1xxx.

The replacement is deliberately structural. It changes standalone business IDs
with known ID lengths, EPI09, NPC9xx, and the Unit9 authoring alias. It does not
touch embedded asset identifiers such as SC9003_item_01, because those are real
Unity resource names rather than business IDs. Generated AI scripts under
``AVG/对话配置工作及草稿/Unit1`` are rebuilt from runtime truth and are skipped;
their EPI09 strings are intentional provenance paths, not current IDs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}
ALLOWED_ROOT_PREFIXES = (
    ("剧情设计", "Unit1"),
    ("avg_editor_v2", "data", "_table_drafts", "Unit1"),
    ("AVG", "对话配置工作及草稿", "Unit1"),
)
BUSINESS_ID = re.compile(r"(?<![A-Za-z0-9_])9(?:\d{8}|\d{6}|\d{5}|\d{3})(?!\d)")
NPC_ID = re.compile(r"(?<![A-Za-z0-9_])NPC9(?=\d{2}(?!\d))")
EVENT_ID = re.compile(r"(?<![A-Za-z0-9_])U9(?=-L[1-6]-INT-\d{2}(?!\d))")
ID_RANGE = re.compile(r"(?<![A-Za-z0-9_])9([1-7])xx(?![A-Za-z0-9_])", re.IGNORECASE)
GENERIC_RANGE = re.compile(r"(?<![A-Za-z0-9_])9xxx(?![A-Za-z0-9_])", re.IGNORECASE)

# Three-digit values are context-sensitive: ``901`` can be an old doubt ID,
# an NPC/chapter ID, or an unrelated step/coordinate.  Never feed them into
# BUSINESS_ID.  These explicit conversions cover only known Unit1 schemas.
DOUBT_ID_MAP = {
    "901": "1101",
    "902": "1201",
    "903": "1202",
    "904": "1203",
    "905": "1301",
    "906": "1302",
    "907": "1303",
    "908": "1401",
    "909": "1402",
    "910": "1501",
    "911": "1502",
    "912": "1503",
    "913": "1504",
    "914": "1601",
    "915": "1602",
}
NPC_ID_MAP = {str(value): str(value - 800) for value in range(902, 911)}
CHAPTER_ID_MAP = {str(value): str(value - 800) for value in range(901, 907)}
GENERATED_CORPUS_PREFIX = ("AVG", "对话配置工作及草稿", "Unit1")


def replace_known_ids(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    pattern = re.compile(
        r"(?<![A-Za-z0-9_])(?:" + "|".join(map(re.escape, mapping)) + r")(?!\d)"
    )
    return pattern.subn(lambda match: mapping[match.group(0)], text)


def migrate_contextual_three_digit_ids(
    text: str, relative_path: Path
) -> tuple[str, Counter[str]]:
    counts: Counter[str] = Counter()
    normalized = relative_path.as_posix()

    if normalized == "剧情设计/Unit1/Unit1_大纲.md":
        text, count = replace_known_ids(text, DOUBT_ID_MAP)
        counts["doubt_id"] += count

    if normalized.startswith("avg_editor_v2/data/_table_drafts/Unit1/"):
        lines: list[str] = []
        for line in text.splitlines(keepends=True):
            if re.match(r"^###\s+9\d{2}(?:\s|$)", line):
                line, count = replace_known_ids(line, NPC_ID_MAP | CHAPTER_ID_MAP)
                counts["table_heading_id"] += count
            elif re.match(r"^\s*-?\s*(?:npc_ref|triggerParam):", line):
                line, count = replace_known_ids(line, NPC_ID_MAP)
                counts["npc_id"] += count
            elif re.match(r"^\s*-?\s*chapter:", line):
                line, count = replace_known_ids(line, CHAPTER_ID_MAP)
                counts["chapter_id"] += count
            lines.append(line)
        text = "".join(lines)

    if normalized.startswith("剧情设计/Unit1/state/"):
        lines = []
        for line in text.splitlines(keepends=True):
            if re.match(r"^\s*#.*(?:Emma=902|Rosa=903|Morrison=904)", line):
                line, count = replace_known_ids(line, NPC_ID_MAP)
                counts["npc_id_comment"] += count
            elif re.match(r"^\s*(?:id|target_npc_id):\s+9\d{2}(?:\s|$)", line):
                line, count = replace_known_ids(line, NPC_ID_MAP)
                counts["npc_id"] += count
            lines.append(line)
        text = "".join(lines)

    return text, counts


def migrate_text(text: str, relative_path: Path | None = None) -> tuple[str, Counter[str]]:
    counts: Counter[str] = Counter()

    def replace_business_id(match: re.Match[str]) -> str:
        counts["business_id"] += 1
        return "1" + match.group(0)[1:]

    def replace_id_range(match: re.Match[str]) -> str:
        counts["id_range"] += 1
        return "1" + match.group(1) + "xx"

    migrated = BUSINESS_ID.sub(replace_business_id, text)
    migrated, count = NPC_ID.subn("NPC1", migrated)
    counts["npc_id"] += count
    migrated, count = EVENT_ID.subn("U1", migrated)
    counts["event_id"] += count
    migrated = ID_RANGE.sub(replace_id_range, migrated)
    migrated, count = GENERIC_RANGE.subn("1xxx", migrated)
    counts["id_range"] += count
    migrated, count = re.subn(r"EPI09", "EPI01", migrated, flags=re.IGNORECASE)
    counts["episode"] += count
    migrated, count = re.subn(r"Unit9", "Unit1", migrated, flags=re.IGNORECASE)
    counts["unit_alias"] += count
    if relative_path is not None:
        migrated, contextual_counts = migrate_contextual_three_digit_ids(migrated, relative_path)
        counts.update(contextual_counts)
    return migrated, counts


def iter_text_files(roots: list[Path]):
    for root in roots:
        if root.is_file():
            if root.suffix.lower() in TEXT_SUFFIXES:
                yield root
            continue
        for path in sorted(root.rglob("*")):
            if "备份" in path.parts:
                continue
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                yield path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        help="Repo-relative file or directory; defaults to 剧情设计/Unit1",
    )
    parser.add_argument("--write", action="store_true", help="Apply replacements; default is dry-run")
    parser.add_argument("--report", type=Path, default=None, help="Optional JSON report path")
    return parser.parse_args()


def validate_root_scope(repo_root: Path, roots: list[Path]) -> None:
    """Reject broad roots so ordinary numbers cannot be mistaken for Unit1 IDs."""
    invalid: list[str] = []
    for root in roots:
        try:
            relative_parts = root.resolve().relative_to(repo_root).parts
        except ValueError:
            invalid.append(str(root))
            continue
        if not any(
            relative_parts[: len(prefix)] == prefix for prefix in ALLOWED_ROOT_PREFIXES
        ):
            invalid.append(Path(*relative_parts).as_posix())
    if invalid:
        allowed = ", ".join("/".join(prefix) for prefix in ALLOWED_ROOT_PREFIXES)
        raise ValueError(
            "Refusing out-of-scope migration root(s): "
            + ", ".join(invalid)
            + ". Allowed Unit1 roots: "
            + allowed
        )


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    roots = [repo_root / value for value in (args.roots or ["剧情设计/Unit1"])]
    validate_root_scope(repo_root, roots)
    missing = [str(path) for path in roots if not path.exists()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    file_changes: list[dict[str, object]] = []
    totals: Counter[str] = Counter()
    for path in iter_text_files(roots):
        original = path.read_text(encoding="utf-8-sig")
        relative_path = path.relative_to(repo_root)
        if relative_path.parts[:3] == GENERATED_CORPUS_PREFIX:
            continue
        migrated, counts = migrate_text(original, relative_path)
        if migrated == original:
            continue
        relative = relative_path.as_posix()
        file_changes.append({"path": relative, "replacements": dict(counts)})
        totals.update(counts)
        if args.write:
            path.write_text(migrated, encoding="utf-8")

    report = {
        "mode": "write" if args.write else "dry-run",
        "roots": [path.relative_to(repo_root).as_posix() for path in roots],
        "changedFileCount": len(file_changes),
        "replacementTotals": dict(totals),
        "files": file_changes,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report:
        report_path = args.report if args.report.is_absolute() else repo_root / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
