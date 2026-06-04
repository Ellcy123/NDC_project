#!/usr/bin/env python3
"""
Assign Unit2 dialogue IDs.

Reads Unit2 no-ID MD drafts and writes derived numbered drafts under
Unit2/编号稿/. Original drafts are not modified.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
UNIT_DIR = SCRIPT_DIR / "Unit2"
OUT_DIR = UNIT_DIR / "编号稿"

NPC_CODES = {
    "zack": 201,
    "opening": 201,
    "office": 201,
    "ending": 201,
    "emma": 202,
    "morrison": 203,
    "frank": 204,
    "mickey": 205,
    "ohara": 206,
    "leonard": 207,
    "moore": 208,
    "tony": 209,
    "vinnie": 210,
    "danny": 211,
    "lula": 212,
    "margaret": 213,
    "edith": 214,
    "foster": 215,
}

SPECIAL_BASE = {
    "office_l1_telegram": (201, 101),
    "vinnie_l5_postexpose_phone": (215, 5),
    "ending_l6_cemetery": (201, 106),
}

SECTION_RE = re.compile(r"^##\s+(Talk|Expose):\s*(\S+)\.json\s*$")
SPEAKER_RE = re.compile(r"^\*\*(.+?)\*\*\s*(?:\[(.*?)\])?\s*$")
GET_RE = re.compile(r"^@get\s+(证词|证据)\s+([0-9A-Za-z]+)\s+[\"“](.*?)[\"”]\s*#?(\w+)?")
OPT_RE = re.compile(r"^@opt\s+[\"“](.*?)[\"”]\s*->\s*([A-Za-z0-9_]+)")
EVIDENCE_RE = re.compile(
    r"^@evidence\s+[\"“](.*?)[\"”]\s*"
    r"(?:[（(]([0-9A-Za-z]+)[）)])?\s*->\s*([A-Za-z0-9_]+)\s*#(correct|trap)"
    r"(?:\s+[\"“](.*?)[\"”])?"
)
LIE_RE = re.compile(r"^@lie\s+anchor=([0-9A-Za-z]+|null)")


@dataclass
class GetTag:
    kind: str
    target: str
    summary: str
    key_type: str = ""


@dataclass
class Option:
    text: str
    label: str
    kind: str = ""
    reason: str = ""
    target_id: int | None = None


@dataclass
class Node:
    speaker: str = ""
    action: str = ""
    words: list[str] = field(default_factory=list)
    tags: list[GetTag] = field(default_factory=list)
    branch_options: list[Option] = field(default_factory=list)
    evidence_options: list[Option] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    goto: str = ""
    is_lie: bool = False
    lie_anchor: str = ""
    source_line: int = 0
    id: int | None = None
    section_kind: str = ""


@dataclass
class Section:
    kind: str
    filename: str
    prelude: list[str] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    loop: int = 0


def normalize_quote_line(line: str) -> str:
    content = line[1:].lstrip()
    if not content:
        return ""
    return content


def file_stem(filename: str) -> str:
    return Path(filename).stem


def loop_from_path(path: Path) -> int:
    match = re.search(r"Loop(\d+)_", path.name)
    if not match:
        raise ValueError(f"Cannot infer loop from {path}")
    return int(match.group(1))


def base_for_section(section: Section, used_conv: dict[int, set[int]]) -> tuple[int, int]:
    stem = file_stem(section.filename)
    if section.kind == "Expose":
        return (0, 0)
    if stem in SPECIAL_BASE:
        npc, conv = SPECIAL_BASE[stem]
    else:
        prefix = stem.split("_")[0].lower()
        npc = NPC_CODES.get(prefix, 201)
        conv = section.loop
    if stem.startswith(f"opening_l{section.loop}_"):
        npc, conv = 201, section.loop
    used = used_conv.setdefault(npc, set())
    if conv in used:
        conv = max(max(used) + 1, section.loop + 1)
    used.add(conv)
    return npc, conv


def make_talk_id(npc: int, conv: int, seq: int) -> int:
    return int(f"{npc:03d}{conv:03d}{seq:03d}")


def make_expose_id(loop: int, seq: int) -> int:
    return int(f"2{loop}{seq:04d}")


def clean_option_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_sections(path: Path) -> list[Section]:
    loop = loop_from_path(path)
    sections: list[Section] = []
    current: Section | None = None
    node: Node | None = None
    pending_labels: list[str] = []
    pending_lie_anchor = ""
    active_lie: Node | None = None

    def flush_node() -> None:
        nonlocal node, active_lie
        if node is not None and current is not None:
            current.nodes.append(node)
            if node.is_lie:
                active_lie = node
            node = None

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        section_match = SECTION_RE.match(line.strip())
        if section_match:
            flush_node()
            current = Section(section_match.group(1), section_match.group(2), [line], [], loop)
            sections.append(current)
            pending_labels = []
            pending_lie_anchor = ""
            active_lie = None
            continue

        if current is None:
            continue

        # Preserve human-readable headings and comments.
        if line.startswith("<!--"):
            flush_node()
            if "-->" in line:
                current.prelude.append(line)
            else:
                current.prelude.append("<!-- source multi-line comment omitted -->")
            continue

        if line.startswith("## ") or line.startswith("# ") or line.startswith("---"):
            flush_node()
            current.prelude.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("@round"):
            flush_node()
            match = re.search(r"@round\s+(\d+)", stripped)
            if match:
                pending_labels.append(f"round{match.group(1)}")
            current.prelude.append(f"<!-- {stripped} -->")
            continue

        lie_match = LIE_RE.match(stripped)
        if lie_match:
            flush_node()
            pending_lie_anchor = lie_match.group(1)
            current.prelude.append(f"<!-- {stripped} -->")
            continue

        if stripped.startswith("@label"):
            flush_node()
            label = stripped.split(maxsplit=1)[1].strip()
            if active_lie is not None and re.search(r"_?(present|evidence|evidence_select)$", label):
                active_lie.labels.append(label)
            else:
                pending_labels.append(label)
            current.prelude.append(f"<!-- {stripped} -->")
            continue

        if stripped.startswith("@path"):
            flush_node()
            label = stripped.split(maxsplit=1)[1].strip()
            pending_labels.append(label)
            current.prelude.append(f"<!-- {stripped} -->")
            continue

        if stripped.startswith("@goto"):
            target = stripped.split(maxsplit=1)[1].strip()
            if node is not None:
                node.goto = target
            elif current.nodes:
                current.nodes[-1].goto = target
            current.prelude.append(f"<!-- {stripped} -->")
            continue

        if stripped.startswith("@branch"):
            if node is None and current.nodes:
                node = current.nodes.pop()
            if node is None:
                node = Node(source_line=lineno)
            current.prelude.append(f"<!-- {stripped} -->")
            continue

        opt_match = OPT_RE.match(stripped)
        if opt_match:
            if node is None and current.nodes:
                node = current.nodes.pop()
            if node is None:
                node = Node(source_line=lineno)
            node.branch_options.append(Option(clean_option_text(opt_match.group(1)), opt_match.group(2)))
            continue

        get_match = GET_RE.match(stripped)
        if get_match:
            if node is None and current.nodes:
                node = current.nodes.pop()
            if node is None:
                node = Node(source_line=lineno)
            node.tags.append(GetTag(get_match.group(1), get_match.group(2), get_match.group(3), get_match.group(4) or ""))
            continue

        evidence_match = EVIDENCE_RE.match(stripped)
        if evidence_match:
            if active_lie is None and node is not None and node.is_lie:
                active_lie = node
            if active_lie is None:
                continue
            text, inline_id, target, kind, reason = evidence_match.groups()
            ev_text = clean_option_text(text)
            if inline_id and inline_id not in ev_text:
                ev_text = f"{ev_text}（{inline_id}）"
            active_lie.evidence_options.append(Option(ev_text, target, kind, reason or ""))
            continue

        speaker_match = SPEAKER_RE.match(stripped)
        if speaker_match:
            flush_node()
            node = Node(
                speaker=speaker_match.group(1).strip(),
                action=(speaker_match.group(2) or "").strip(),
                labels=pending_labels,
                is_lie=bool(pending_lie_anchor),
                lie_anchor=pending_lie_anchor,
                source_line=lineno,
                section_kind=current.kind,
            )
            pending_labels = []
            pending_lie_anchor = ""
            continue

        if line.startswith(">"):
            if node is None:
                node = Node(labels=pending_labels, source_line=lineno, section_kind=current.kind)
                pending_labels = []
            content = normalize_quote_line(line)
            if content:
                node.words.append(content)
            continue

        # Ignore non-dialogue prose inside sections. It remains in the original draft.

    flush_node()
    return sections


def assign_ids(sections: list[Section]) -> None:
    used_conv: dict[int, set[int]] = {}
    for section in sections:
        if section.kind == "Expose":
            main_seq = 1
            trap_seq_by_label: dict[str, int] = {}
            next_trap_base = 7000
            current_trap_base: int | None = None
            for node in section.nodes:
                trap_label = next((label for label in node.labels if "trap" in label), "")
                if trap_label:
                    if trap_label not in trap_seq_by_label:
                        trap_seq_by_label[trap_label] = next_trap_base
                        next_trap_base += 100
                    current_trap_base = trap_seq_by_label[trap_label]
                    seq = current_trap_base + 1
                    trap_seq_by_label[trap_label] = seq
                    node.id = make_expose_id(section.loop, seq)
                    continue
                current_trap_base = None
                node.id = make_expose_id(section.loop, main_seq)
                main_seq += 1
        else:
            npc, conv = base_for_section(section, used_conv)
            for seq, node in enumerate(section.nodes, 1):
                node.id = make_talk_id(npc, conv, seq)


def build_label_map(section: Section) -> dict[str, int]:
    labels: dict[str, int] = {}
    for node in section.nodes:
        assert node.id is not None
        for label in node.labels:
            labels[label] = node.id
    # If a goto targets roundN and no explicit node label exists, map to first node after that round comment.
    return labels


def evidence_id_from_text(text: str) -> str:
    ids = re.findall(r"\b(?:\d{4}|\d{7}[A-Za-z]?)\b", text)
    return ids[-1] if ids else ""


def split_line_nodes(sections: list[Section]) -> None:
    for section in sections:
        expanded: list[Node] = []
        for node in section.nodes:
            if node.branch_options or node.evidence_options or node.is_lie:
                expanded.append(node)
                continue

            words = node.words or [""]
            if len(words) <= 1 and len(node.tags) <= 1:
                expanded.append(node)
                continue

            tag_by_word: dict[int, GetTag] = {}
            extra_tags: list[GetTag] = []
            if node.tags:
                if len(node.tags) == 1:
                    tag_by_word[len(words) - 1] = node.tags[0]
                elif len(words) >= len(node.tags):
                    start = len(words) - len(node.tags)
                    for idx, tag in enumerate(node.tags):
                        tag_by_word[start + idx] = tag
                else:
                    for idx, tag in enumerate(node.tags):
                        if idx < len(words):
                            tag_by_word[idx] = tag
                        else:
                            extra_tags.append(tag)

            total = len(words) + len(extra_tags)
            for idx, word in enumerate(words):
                clone = Node(
                    speaker=node.speaker,
                    action=node.action if idx == 0 else "",
                    words=[word] if word else [],
                    tags=[tag_by_word[idx]] if idx in tag_by_word else [],
                    branch_options=[],
                    evidence_options=[],
                    labels=node.labels if idx == 0 else [],
                    goto=node.goto if idx == total - 1 else "",
                    is_lie=False,
                    source_line=node.source_line,
                    section_kind=node.section_kind,
                )
                expanded.append(clone)

            for extra_idx, tag in enumerate(extra_tags):
                idx = len(words) + extra_idx
                clone = Node(
                    speaker=node.speaker,
                    action="",
                    words=[words[-1]] if words and words[-1] else [],
                    tags=[tag],
                    branch_options=[],
                    evidence_options=[],
                    labels=[],
                    goto=node.goto if idx == total - 1 else "",
                    is_lie=False,
                    source_line=node.source_line,
                    section_kind=node.section_kind,
                )
                expanded.append(clone)

        section.nodes = expanded


def render_node(node: Node, section: Section, label_map: dict[str, int], is_last: bool) -> list[str]:
    assert node.id is not None
    rendered: list[str] = []
    tag_tail = ""
    if node.is_lie:
        correct = []
        for opt in node.evidence_options:
            if opt.kind == "correct":
                ev_id = evidence_id_from_text(opt.text)
                if ev_id:
                    correct.append(ev_id)
        tag_tail = " `Lie`"
        if correct:
            tag_tail += " 正确证据：" + ",".join(dict.fromkeys(correct))
    elif node.branch_options:
        tag_tail = " `branches`"
    elif node.tags:
        tag_tail = f" `get` → {node.tags[0].target}"
    elif is_last:
        tag_tail = " `end`"

    rendered.append(f"### {node.id}{tag_tail}")
    if node.speaker:
        speaker = f"**{node.speaker}**"
        if node.action:
            speaker += f" [{node.action}]"
        rendered.append(speaker)
    for word in node.words:
        rendered.append(f"> {word}")

    if node.branch_options:
        for idx, opt in enumerate(node.branch_options, 1):
            target = label_map.get(opt.label, 0)
            arrow = f"`{target}`" if target else f"`{opt.label}`"
            rendered.append(f"> - {idx}. {opt.text} → {arrow}")

    if node.evidence_options:
        for idx, opt in enumerate(node.evidence_options, 1):
            target = label_map.get(opt.label, 0)
            arrow = f"`{target}`" if target else f"`{opt.label}`"
            note = "正确" if opt.kind == "correct" else f"陷阱：{opt.reason}"
            rendered.append(f"> - {idx}. 出示{opt.text} → {arrow}（{note}）")

    if node.goto:
        target = label_map.get(node.goto, 0)
        suffix = f" -> {target}" if target else ""
        rendered.append(f"<!-- @goto {node.goto}{suffix} -->")
    return rendered


def render(sections: list[Section], source: Path) -> str:
    out: list[str] = [
        f"# Unit2 Loop{loop_from_path(source)} 对白编号稿",
        "",
        f"> 来源：`../{source.name}`",
        "> 用途：派生编号稿，给 Unit2 对话 JSON 同步流程读取。",
        "> 注意：原无 ID 草稿不修改。",
        "",
    ]
    for section in sections:
        label_map = build_label_map(section)
        if out and out[-1] != "":
            out.append("")
        for line in section.prelude:
            out.append(line)
        if section.prelude and out[-1] != "":
            out.append("")
        for idx, node in enumerate(section.nodes):
            out.extend(render_node(node, section, label_map, idx == len(section.nodes) - 1))
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def process_loop(loop: int, write: bool) -> tuple[Path, str]:
    src = UNIT_DIR / f"Loop{loop}_生成草稿.md"
    if not src.exists():
        raise FileNotFoundError(src)
    sections = parse_sections(src)
    split_line_nodes(sections)
    assign_ids(sections)
    text = render(sections, src)
    out = OUT_DIR / f"Loop{loop}_编号稿.md"
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return out, text


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign Unit2 no-ID dialogue drafts to numbered MD.")
    parser.add_argument("--loop", type=int, action="append", help="Loop number 1-6. Can be repeated.")
    parser.add_argument("--all", action="store_true", help="Process all loops.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files.")
    args = parser.parse_args()

    loops = args.loop or []
    if args.all or not loops:
        loops = list(range(1, 7))

    for loop in sorted(set(loops)):
        out, text = process_loop(loop, write=not args.dry_run)
        ids = re.findall(r"^###\s+(\d+)", text, flags=re.M)
        duplicates = sorted({x for x in ids if ids.count(x) > 1})
        status = "DRY" if args.dry_run else "WRITE"
        print(f"[{status}] Loop{loop}: {out} sections={text.count('## Talk:') + text.count('## Expose:')} ids={len(ids)}")
        if duplicates:
            print(f"  [WARN] duplicate IDs: {', '.join(duplicates)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
