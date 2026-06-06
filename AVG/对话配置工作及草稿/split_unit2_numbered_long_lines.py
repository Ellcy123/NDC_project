#!/usr/bin/env python3
"""
Split overlong Unit2 numbered dialogue lines.

Input/output:
- Reads AVG/对话配置工作及草稿/Unit2/编号稿/LoopN_编号稿.md
- Rewrites the numbered drafts in place only with --write

Rules:
- Chinese characters and Chinese punctuation count toward the 35-char limit.
- English letters, numbers, spaces, and bracketed action notes do not count.
- One visible dialogue line becomes one dialogue ID.
- Mechanic tags such as Lie/branches/get stay on the final split chunk.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
NUMBERED_DIR = SCRIPT_DIR / "Unit2" / "编号稿"

SECTION_RE = re.compile(r"^##\s+(Talk|Expose):\s*(\S+)\.json\s*$")
ENTRY_RE = re.compile(r"^###\s+(\d+)(.*)$")
SPEAKER_RE = re.compile(r"^\*\*(.+?)\*\*(?:\s*\[(.*?)\])?\s*$")
COUNT_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff，。！？、；：“”‘’（）《》〈〉【】—…·]")
BRACKET_RE = re.compile(r"\[[^\]]*\]")


@dataclass
class Entry:
    old_id: str
    tail: str
    body: list[str]
    section_kind: str
    new_id: str = ""
    target_id: str = ""


@dataclass
class Part:
    raw: list[str] | None = None
    entry: Entry | None = None


def count_cn(text: str) -> int:
    return len(COUNT_RE.findall(BRACKET_RE.sub("", text)))


def split_visible_line(text: str, limit: int = 35) -> list[str]:
    text = text.strip()
    if count_cn(text) <= limit:
        return [text]

    chunks: list[str] = []
    rest = text
    strong = set("。！？；")
    soft = set("，、：")

    while count_cn(rest) > limit:
        counted = 0
        strong_cut = -1
        soft_cut = -1
        hard_cut = -1

        for idx, ch in enumerate(rest):
            if COUNT_RE.match(ch):
                counted += 1
                if counted <= limit:
                    hard_cut = idx + 1
                    if ch in strong:
                        strong_cut = idx + 1
                    elif ch in soft:
                        soft_cut = idx + 1
                else:
                    break

        cut = strong_cut if strong_cut > 0 else soft_cut if soft_cut > 0 else hard_cut
        if cut <= 0:
            break
        head = rest[:cut].strip()
        if head:
            chunks.append(head)
        rest = rest[cut:].strip()

    if rest:
        chunks.append(rest)
    return chunks


def is_dialogue_quote(line: str) -> bool:
    if not line.startswith(">"):
        return False
    content = line[1:].lstrip()
    if not content:
        return False
    if content.startswith(("- ", "📋 ", "🎯 ", "[WARN]", "**[", "[出示证据]", "→")):
        return False
    if content.startswith("场景") or content.startswith("场景："):
        return False
    if re.match(r"^\[(Loop|Scene|场景|循环|Phase|Round)\s", content):
        return False
    if re.match(r"^(Quiz|答案|Source|Note|注)[（(：:\s]", content):
        return False
    if re.match(r"^\*\*[^*\n]+\*\*\s*[:：]?\s*$", content):
        return False
    return True


def speaker_without_action(line: str) -> str:
    match = SPEAKER_RE.match(line.strip())
    if not match:
        return line
    return f"**{match.group(1).strip()}**"


def split_entry(entry: Entry) -> list[Entry]:
    word_indexes = [i for i, line in enumerate(entry.body) if is_dialogue_quote(line)]
    if not word_indexes:
        return [entry]

    chunks: list[str] = []
    for idx in word_indexes:
        content = entry.body[idx][1:].lstrip()
        chunks.extend(split_visible_line(content))

    if len(chunks) <= 1 and count_cn(chunks[0]) <= 35:
        return [entry]

    first_word = word_indexes[0]
    last_word = word_indexes[-1]
    prefix = entry.body[:first_word]
    trailer = [line for i, line in enumerate(entry.body[last_word + 1 :], last_word + 1) if i not in word_indexes]

    speaker_line = ""
    for line in prefix:
        if SPEAKER_RE.match(line.strip()):
            speaker_line = line
            break

    split_entries: list[Entry] = []
    tag_on_last = bool(entry.tail.strip())
    for idx, chunk in enumerate(chunks):
        body: list[str] = []
        if idx == 0:
            body.extend(prefix)
        elif speaker_line:
            body.append(speaker_without_action(speaker_line))
        body.append(f"> {chunk}")
        if idx == len(chunks) - 1:
            body.extend(trailer)
        tail = entry.tail if (idx == len(chunks) - 1 or not tag_on_last) else ""
        split_entries.append(Entry(entry.old_id, tail, body, entry.section_kind))
    return split_entries


def parse_section(lines: list[str], kind: str) -> list[Part]:
    parts: list[Part] = []
    raw: list[str] = []
    current: Entry | None = None

    def flush_raw() -> None:
        nonlocal raw
        if raw:
            parts.append(Part(raw=raw))
            raw = []

    def flush_entry() -> None:
        nonlocal current
        if current:
            parts.append(Part(entry=current))
            current = None

    for line in lines:
        match = ENTRY_RE.match(line)
        if match:
            flush_entry()
            flush_raw()
            current = Entry(match.group(1), match.group(2), [], kind)
            continue
        if current is not None:
            current.body.append(line)
        else:
            raw.append(line)

    flush_entry()
    flush_raw()
    return parts


def expose_seq(old_id: str) -> int:
    return int(old_id[2:]) if len(old_id) == 6 else 0


def assign_section_ids(entries: list[Entry]) -> dict[str, str]:
    old_to_new: dict[str, str] = {}
    if not entries:
        return old_to_new

    kind = entries[0].section_kind
    if kind == "Talk":
        base = entries[0].old_id[:6]
        for seq, entry in enumerate(entries, 1):
            entry.new_id = f"{base}{seq:03d}"
    else:
        prefix = entries[0].old_id[:2]
        main_seq = 1
        trap_next: dict[int, int] = {}
        for entry in entries:
            seq = expose_seq(entry.old_id)
            if seq >= 7000:
                trap_base = (seq // 100) * 100
                next_seq = trap_next.get(trap_base, trap_base + 1)
                entry.new_id = f"{prefix}{next_seq:04d}"
                trap_next[trap_base] = next_seq + 1
            else:
                entry.new_id = f"{prefix}{main_seq:04d}"
                main_seq += 1

    grouped: dict[str, list[Entry]] = {}
    for entry in entries:
        grouped.setdefault(entry.old_id, []).append(entry)
    for old_id, group in grouped.items():
        tagged = [entry for entry in group if "`Lie`" in entry.tail or "`branches`" in entry.tail]
        old_to_new[old_id] = (tagged[-1] if tagged else group[0]).new_id
    return old_to_new


def replace_refs(line: str, mapping: dict[str, str]) -> str:
    if not mapping:
        return line
    keys = sorted(mapping, key=len, reverse=True)
    pattern = re.compile(r"(?<!\d)(" + "|".join(re.escape(k) for k in keys) + r")(?!\d)")
    return pattern.sub(lambda m: mapping[m.group(1)], line)


def render_section(parts: list[Part]) -> tuple[list[str], int, dict[str, str]]:
    expanded_parts: list[Part] = []
    entries: list[Entry] = []
    split_count = 0

    for part in parts:
        if part.entry is None:
            expanded_parts.append(part)
            continue
        split_entries = split_entry(part.entry)
        split_count += max(0, len(split_entries) - 1)
        for entry in split_entries:
            expanded_parts.append(Part(entry=entry))
            entries.append(entry)

    mapping = assign_section_ids(entries)

    rendered: list[str] = []
    for part in expanded_parts:
        if part.raw is not None:
            rendered.extend(replace_refs(line, mapping) for line in part.raw)
            continue
        assert part.entry is not None
        entry = part.entry
        rendered.append(f"### {entry.new_id}{entry.tail}")
        rendered.extend(replace_refs(line, mapping) for line in entry.body)
        if rendered and rendered[-1] != "":
            rendered.append("")
    return rendered, split_count, mapping


def process_file(path: Path, write: bool) -> tuple[int, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    total_split = 0
    total_entries = 0
    idx = 0

    while idx < len(lines):
        section_match = SECTION_RE.match(lines[idx])
        if not section_match:
            output.append(lines[idx])
            idx += 1
            continue

        section_start = idx
        kind = section_match.group(1)
        idx += 1
        while idx < len(lines) and not SECTION_RE.match(lines[idx]):
            idx += 1
        section_lines = lines[section_start:idx]
        parts = parse_section(section_lines, kind)
        rendered, split_count, _ = render_section(parts)
        total_split += split_count
        total_entries += sum(1 for part in parts if part.entry is not None)
        output.extend(rendered)

    text = "\n".join(output).rstrip() + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    return total_entries, total_split


def selected_paths(args: argparse.Namespace) -> list[Path]:
    loops = args.loop or []
    if args.all or not loops:
        loops = list(range(1, 7))
    paths = [NUMBERED_DIR / f"Loop{loop}_编号稿.md" for loop in sorted(set(loops))]
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise SystemExit("Missing numbered drafts: " + ", ".join(str(path) for path in missing))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Split Unit2 numbered dialogue lines longer than 35 Chinese chars.")
    parser.add_argument("--loop", type=int, action="append", help="Loop number 1-6. Can be repeated.")
    parser.add_argument("--all", action="store_true", help="Process Loop1-6. Default when --loop is omitted.")
    parser.add_argument("--write", action="store_true", help="Rewrite numbered drafts in place.")
    args = parser.parse_args()

    mode = "WRITE" if args.write else "DRY"
    for path in selected_paths(args):
        entries, split_count = process_file(path, write=args.write)
        print(f"[{mode}] {path.relative_to(SCRIPT_DIR)} entries={entries} added={split_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
