#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build Unit4 EPI04 AVG JSON and wire it into the preview tables.

The Unit4 Markdown drafts use the project's no-ID dialogue grammar.  This
builder assigns deterministic IDs, resolves branch labels, emits Talk/Expose
files, and replaces Unit4 preview-table pending keys with exact AVG entries.

Run without --write for a read-only validation/report.  Pass --write to update
AVG/EPI04 and the Unit4 slices of the preview tables.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DRAFT_DIR = REPO_ROOT / "AVG" / "对话配置工作及草稿" / "Unit4"
AVG_ROOT = REPO_ROOT / "AVG" / "EPI04"
TABLE_DIR = REPO_ROOT / "avg_editor_v2" / "data" / "table"

SECTION_RE = re.compile(r"^##\s+(Talk|Expose):\s+([^\s]+\.json)\s*$", re.M)
SPEAKER_RE = re.compile(r"^\*\*(.+?)\*\*(?:\s*\[(.*?)\])?\s*(.*)$")
OPT_RE = re.compile(r'^@opt\s+"([^"]+)"(?:\s+\[[^\]]+\])?\s*->\s*([^\s#]+)')
GET_RE = re.compile(r'^@get\s+(?:证词|证据)\s+(\d+)\s+"([^"]*)"', re.M)
EVIDENCE_RE = re.compile(r'^@evidence\s+"([^"]+)"\s*->\s*([^\s#]+)')


SPEAKERS: dict[str, tuple[str, str]] = {
    "扎克·布伦南": ("401", "Zack Brennan"),
    "艾玛·奥马利": ("402", "Emma O'Malley"),
    "米奇·唐纳利": ("403", "Mickey Donnelly"),
    "Whale": ("403", "Whale"),
    "Whale/米奇·唐纳利": ("403", "Whale / Mickey Donnelly"),
    "瓦茨": ("404", "Watts"),
    "哈罗德·莫里森": ("405", "Harold Morrison"),
    "多丽丝·莫里森": ("406", "Doris Morrison"),
    "罗莎·马丁内斯": ("407", "Rosa Martinez"),
    "福斯特医生": ("408", "Dr. Foster"),
    "惠特菲尔德": ("409", "Whitfield"),
    "玛格丽特·布伦南": ("410", "Margaret Brennan"),
    "奥哈拉太太": ("411", "Mrs. O'Hara"),
    "皮尔斯": ("412", "Inspector Pierce"),
    "莎拉·奥哈拉": ("414", "Sarah O'Hara"),
    "接线员": ("415", "Operator"),
    "夜班电话接线员": ("415", "Night Operator"),
    "档案管理员": ("416", "Archivist"),
    "社会服务部调档员": ("417", "Records Clerk"),
    "退休法官": ("418", "Retired Judge"),
    "记者A": ("419", "Reporter A"),
    "记者B": ("419", "Reporter B"),
    "记者C": ("419", "Reporter C"),
    "旁白": ("000", "Narrator"),
    "南区居民": ("000", "South Side Resident"),
    "辖区警员": ("000", "Precinct Officer"),
    "小女孩": ("000", "Little Girl"),
    "专线联络人": ("000", "Private-line Contact"),
    "Tidewater清道夫": ("000", "Tidewater Cleaner"),
}

OWNER_TOKENS = (
    ("records_clerk", 417),
    ("archivist", 416),
    ("operator", 415),
    ("sarah", 414),
    ("pierce", 412),
    ("ohara", 411),
    ("margaret", 410),
    ("whitfield", 409),
    ("foster", 408),
    ("rosa", 407),
    ("doris", 406),
    ("harold", 405),
    ("watts", 404),
    ("mickey", 403),
    ("survivors", 403),
)

OWNER_SPEAKERS = {
    403: "米奇·唐纳利",
    404: "瓦茨",
    406: "多丽丝·莫里森",
    409: "惠特菲尔德",
    410: "玛格丽特·布伦南",
}


@dataclass
class Node:
    speaker: str
    action: str
    words: str
    synthetic: bool = False
    script: str = ""
    next_label: str | None = None
    parameter_str: list[str] = field(default_factory=lambda: ["", "", ""])
    parameter_int: list[int] = field(default_factory=lambda: [0, 0, 0])
    options: list[tuple[str, str]] = field(default_factory=list)
    id: int = 0


@dataclass
class Section:
    kind: str
    name: str
    loop: int
    source: Path
    body: str
    nodes: list[Node] = field(default_factory=list)
    labels: dict[str, int] = field(default_factory=dict)
    branch_names: dict[str, int] = field(default_factory=dict)
    lie_indices: dict[int, int] = field(default_factory=dict)

    @property
    def stem(self) -> str:
        return self.name.removesuffix(".json")

    @property
    def is_repeat(self) -> bool:
        return self.kind == "Talk" and self.stem.endswith("_repeat")

    @property
    def start_id(self) -> int:
        return self.nodes[0].id


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def split_words(text: str, limit: int = 38) -> list[str]:
    """Split a long draft line at natural punctuation without changing text."""
    text = text.strip().replace("  ", " ")
    if len(text) <= limit:
        return [text]
    pieces: list[str] = []
    rest = text
    while len(rest) > limit:
        window = rest[: limit + 1]
        cut = max((window.rfind(mark) + 1 for mark in "。！？；…"), default=0)
        if cut < limit // 2:
            cut = max((window.rfind(mark) + 1 for mark in "，、：,.!?;"), default=0)
        if cut < limit // 2:
            cut = limit
        pieces.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    if rest:
        pieces.append(rest)
    return [piece for piece in pieces if piece]


def load_sections() -> list[Section]:
    sections: list[Section] = []
    for loop in range(1, 6):
        path = DRAFT_DIR / f"Loop{loop}_生成草稿.md"
        text = strip_comments(path.read_text(encoding="utf-8"))
        matches = list(SECTION_RE.finditer(text))
        if not matches:
            raise ValueError(f"No dialogue sections found in {path}")
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections.append(
                Section(
                    kind=match.group(1),
                    name=match.group(2),
                    loop=loop,
                    source=path,
                    body=text[match.end() : end],
                )
            )
    names = [section.stem for section in sections]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate Unit4 section names: {duplicates}")
    return sections


def add_speaker_block(section: Section, speaker: str, action: str, quote_lines: list[str]) -> tuple[int, int]:
    start = len(section.nodes)
    expanded: list[str] = []
    for line in quote_lines:
        expanded.extend(split_words(line))
    if not expanded:
        # A few drafts intentionally use an action-only speaker block as the
        # carrier for the immediately following branch menu.
        expanded = ["……"]
    for index, words in enumerate(expanded):
        section.nodes.append(
            Node(
                speaker=speaker,
                action=action if index == 0 else "",
                words=words,
                synthetic=not quote_lines,
            )
        )
    return start, len(section.nodes) - 1


def parse_section(section: Section, testimony_summaries: dict[str, str]) -> None:
    lines = section.body.splitlines()
    index = 0
    pending_labels: list[str] = []
    pending_lie_round: int | None = None
    pending_lie_anchor: str | None = None
    current_round = 0
    current_lie_index: int | None = None
    last_block_end: int | None = None
    control_boundary = True

    def bind_pending(node_index: int) -> None:
        nonlocal pending_labels
        for label in pending_labels:
            if label in section.labels:
                raise ValueError(f"{section.name}: duplicate label {label}")
            section.labels[label] = node_index
        pending_labels = []

    while index < len(lines):
        raw = lines[index].strip()
        if not raw or raw == "---" or raw.startswith("#"):
            index += 1
            continue

        speaker_match = SPEAKER_RE.match(raw)
        if speaker_match:
            speaker = speaker_match.group(1).strip()
            action = (speaker_match.group(2) or "").strip()
            tail = (speaker_match.group(3) or "").strip()
            if tail:
                action = f"{action} {tail}".strip()
            quote_lines: list[str] = []
            index += 1
            while index < len(lines):
                candidate = lines[index].strip()
                if candidate.startswith(">"):
                    quote_lines.append(candidate[1:].strip())
                    index += 1
                    continue
                if not candidate:
                    index += 1
                    continue
                break
            start, end = add_speaker_block(section, speaker, action, quote_lines)
            bind_pending(start)
            last_block_end = end
            control_boundary = False
            if pending_lie_round is not None:
                section.nodes[end].script = "Lie"
                section.nodes[end].parameter_int[1] = pending_lie_round
                section.lie_indices[pending_lie_round] = end
                current_lie_index = end
                pending_lie_round = None
                pending_lie_anchor = None
            continue

        if raw.startswith("@label ") or raw.startswith("@path "):
            pending_labels.append(raw.split(maxsplit=1)[1].strip())
            control_boundary = True
        elif raw.startswith("@round "):
            current_round = int(raw.split(maxsplit=1)[1])
            control_boundary = True
        elif raw.startswith("@lie "):
            if not current_round:
                raise ValueError(f"{section.name}: @lie appears before @round")
            pending_lie_round = current_round
            anchor_match = re.search(r"anchor=([^\s]+)", raw)
            pending_lie_anchor = anchor_match.group(1) if anchor_match else "null"
            control_boundary = True
        elif raw.startswith("@evidence "):
            match = EVIDENCE_RE.match(raw)
            if current_lie_index is None and pending_lie_round is not None:
                owner = section_owner(section)
                anchor_text = testimony_summaries.get(str(pending_lie_anchor or ""))
                words = anchor_text or f"（证词 {pending_lie_anchor}）"
                current_lie_index = len(section.nodes)
                section.nodes.append(
                    Node(
                        speaker=OWNER_SPEAKERS.get(owner, "对方"),
                        action="",
                        words=words,
                        synthetic=True,
                        script="Lie",
                    )
                )
                section.nodes[current_lie_index].parameter_int[1] = pending_lie_round
                section.lie_indices[pending_lie_round] = current_lie_index
                bind_pending(current_lie_index)
                last_block_end = current_lie_index
                pending_lie_round = None
                pending_lie_anchor = None
            if not match or current_lie_index is None:
                raise ValueError(f"{section.name}: invalid or unattached evidence directive: {raw}")
            target = match.group(2)
            lie_node = section.nodes[current_lie_index]
            if lie_node.next_label and lie_node.next_label != target:
                raise ValueError(f"{section.name}: round {current_round} evidence targets disagree")
            lie_node.next_label = target
            control_boundary = True
        elif raw.startswith("@branch "):
            branch_name = raw.split(maxsplit=1)[1].strip()
            if last_block_end is None or control_boundary:
                carrier = len(section.nodes)
                section.nodes.append(
                    Node(speaker="扎克·布伦南", action="", words=f"（{branch_name}）", synthetic=True)
                )
                bind_pending(carrier)
            else:
                carrier = last_block_end
                bind_pending(carrier)
            section.nodes[carrier].script = "branches"
            section.branch_names[branch_name] = carrier
            options: list[tuple[str, str]] = []
            index += 1
            while index < len(lines):
                candidate = lines[index].strip()
                if not candidate:
                    index += 1
                    continue
                match = OPT_RE.match(candidate)
                if not match:
                    break
                options.append((match.group(1), match.group(2)))
                index += 1
            if not options:
                raise ValueError(f"{section.name}: branch {branch_name!r} has no options")
            section.nodes[carrier].options = options
            last_block_end = carrier
            control_boundary = True
            continue
        elif raw.startswith("@goto "):
            if last_block_end is None:
                raise ValueError(f"{section.name}: @goto has no previous dialogue node")
            section.nodes[last_block_end].next_label = raw.split(maxsplit=1)[1].strip()
            control_boundary = True
        elif raw.startswith("@get "):
            match = GET_RE.match(raw)
            if not match or last_block_end is None:
                raise ValueError(f"{section.name}: invalid or unattached get directive: {raw}")
            node = section.nodes[last_block_end]
            node.script = "get"
            node.parameter_str[0] = match.group(1)
            control_boundary = True
        elif raw.startswith("@change_scene "):
            if last_block_end is None:
                raise ValueError(f"{section.name}: @change_scene has no previous dialogue node")
            node = section.nodes[last_block_end]
            node.script = "8"
            node.parameter_str[0] = raw.split(maxsplit=1)[1].strip()
            control_boundary = True
        elif raw.startswith("@"):
            raise ValueError(f"{section.name}: unsupported directive {raw}")
        index += 1

    if pending_labels:
        raise ValueError(f"{section.name}: labels without a following node: {pending_labels}")
    if pending_lie_round is not None:
        raise ValueError(f"{section.name}: @lie has no following speaker block")
    if not section.nodes:
        raise ValueError(f"{section.name}: no dialogue nodes generated")


def section_owner(section: Section) -> int:
    lowered = section.stem.lower()
    for token, owner in OWNER_TOKENS:
        if token in lowered:
            return owner
    return 401


def allocate_ids(sections: list[Section]) -> None:
    groups: defaultdict[int, int] = defaultdict(int)
    expose_seq: defaultdict[int, int] = defaultdict(int)
    for section in sections:
        owner = section_owner(section)
        if section.kind == "Expose":
            start = 400000 + section.loop * 10000 + expose_seq[section.loop] + 1
            for offset, node in enumerate(section.nodes):
                node.id = start + offset
            expose_seq[section.loop] += len(section.nodes)
        elif section.is_repeat:
            start = owner * 1_000_000 + (800 + section.loop) * 1000 + 1
            for offset, node in enumerate(section.nodes):
                node.id = start + offset
        else:
            groups[owner] += 1
            group = groups[owner]
            if group >= 800:
                raise ValueError(f"NPC {owner}: normal Talk group collides with repeat namespace")
            start = owner * 1_000_000 + group * 1000 + 1
            for offset, node in enumerate(section.nodes):
                node.id = start + offset


def resolve_label(section: Section, label: str) -> int:
    index = section.labels.get(label)
    if index is None:
        index = section.branch_names.get(label)
    if index is None:
        raise ValueError(f"{section.name}: unresolved jump label {label!r}")
    return section.nodes[index].id


def finalize_links(sections: list[Section]) -> None:
    by_stem = {section.stem: section for section in sections}
    for section in sections:
        for index, node in enumerate(section.nodes):
            if node.options:
                # Legacy fields retain the first three branches; Parameters keeps all.
                for option_index, (_, target) in enumerate(node.options[:3]):
                    node.parameter_int[option_index] = resolve_label(section, target)
            if node.next_label:
                target_id = resolve_label(section, node.next_label)
                if node.script == "Lie":
                    node.parameter_int[0] = target_id
                else:
                    node.parameter_int[0] = node.parameter_int[0] or 0
            if section.is_repeat:
                continue
            if node.script == "branches":
                continue
            if node.next_label:
                continue
            if node.script == "8":
                continue

        if section.is_repeat:
            source_name = section.stem.removesuffix("_repeat")
            source = by_stem.get(source_name)
            if source is None:
                raise ValueError(f"{section.name}: repeat source {source_name}.json not found")
            if source.branch_names:
                target_index = next(iter(source.branch_names.values()))
                section.nodes[-1].next_label = f"__external__:{source.nodes[target_index].id}"


def node_to_json(section: Section, node: Node, step: int) -> dict[str, Any]:
    speaker_id, english_name = SPEAKERS.get(node.speaker, ("000", node.speaker))
    if node.next_label:
        if node.next_label.startswith("__external__:"):
            next_id = node.next_label.split(":", 1)[1]
        elif node.script == "Lie":
            next_id = str(section.nodes[step].id) if step < len(section.nodes) else ""
        else:
            next_id = str(resolve_label(section, node.next_label))
    elif node.script not in {"branches", "8"} and step < len(section.nodes):
        next_id = str(section.nodes[step].id)
    else:
        next_id = ""

    script = node.script
    if not next_id and not script:
        script = "end"

    result: dict[str, Any] = {
        "id": node.id,
        "step": step,
        "speakType": 3 if speaker_id == "401" else 2,
        "waitTime": 0,
        "IdSpeaker": f"NPC{speaker_id}",
        "cnSpeaker": node.speaker,
        "enSpeaker": english_name,
        "Location": "",
        "cnAction": node.action,
        "cnWords": node.words,
        "enAction": "",
        "enWords": "",
        "next": next_id,
        "script": script,
        "ParameterStr0": node.parameter_str[0],
        "ParameterStr1": node.parameter_str[1],
        "ParameterStr2": node.parameter_str[2],
        "ParameterInt0": node.parameter_int[0],
        "ParameterInt1": node.parameter_int[1],
        "ParameterInt2": node.parameter_int[2],
        "videoEpisode": "EPI04",
        "videoLoop": f"loop{section.loop}",
        "videoId": str(node.id),
        "videoScene": section.stem,
    }
    if node.options:
        result["ParameterStr0"] = node.options[0][0] if len(node.options) > 0 else ""
        result["ParameterStr1"] = node.options[1][0] if len(node.options) > 1 else ""
        result["ParameterStr2"] = node.options[2][0] if len(node.options) > 2 else ""
        result["Parameters"] = [
            {"ParameterStr": text, "ParameterInt": str(resolve_label(section, target))}
            for text, target in node.options
        ]
    return result


def render_section(section: Section) -> list[dict[str, Any]]:
    return [node_to_json(section, node, step) for step, node in enumerate(section.nodes, start=1)]


def section_reference(section: Section) -> dict[str, Any]:
    return {
        "id": str(section.start_id),
        "videoEpisode": "EPI04",
        "videoLoop": f"loop{section.loop}",
        "videoScene": section.stem,
    }


def update_entry(entry: dict[str, Any], section_map: dict[str, Section], *, id_key: str = "talkId") -> bool:
    pending = str(entry.get("pendingTalkKey") or "")
    if not pending:
        return False
    round_match = re.fullmatch(r"(.+)\.round_(\d+)", pending)
    if round_match:
        stem, round_text = round_match.groups()
        section = section_map.get(stem)
        round_number = int(round_text)
        if section is None or round_number not in section.lie_indices:
            raise ValueError(f"Cannot resolve expose pending key {pending}")
        node = section.nodes[section.lie_indices[round_number]]
        entry[id_key] = str(node.id)
        entry["videoEpisode"] = "EPI04"
        entry["videoLoop"] = f"loop{section.loop}"
        entry["videoScene"] = section.stem
    else:
        section = section_map.get(pending)
        if section is None:
            raise ValueError(f"Cannot resolve pending key {pending}")
        entry[id_key] = str(section.start_id)
        entry.update({key: value for key, value in section_reference(section).items() if key != "id"})
    entry.pop("pendingTalkKey", None)
    if "previewStatus" in entry:
        entry["previewStatus"] = "avg_ready"
    return True


def update_npc_row(row: dict[str, Any], section_map: dict[str, Section]) -> int:
    count = 0
    for field in ("TalkInfo", "LoopTalkInfo"):
        entry = row.get(field)
        if isinstance(entry, dict) and entry.get("pendingTalkKey"):
            pending = str(entry["pendingTalkKey"])
            section = section_map.get(pending)
            if section is None:
                raise ValueError(f"NPC row {row.get('id')}: missing section {pending}")
            entry.update(section_reference(section))
            entry.pop("pendingTalkKey", None)
            entry["previewStatus"] = "avg_ready"
            count += 1
    if count and "previewStatus" in row:
        row["previewStatus"] = "avg_ready_art_pending"
    return count


def walk_pending(value: Any, section_map: dict[str, Section]) -> int:
    """Resolve non-NPC pending Talk keys in preview event dictionaries."""
    count = 0
    if isinstance(value, list):
        return sum(walk_pending(item, section_map) for item in value)
    if not isinstance(value, dict):
        return 0
    pending = str(value.get("pendingTalkKey") or "")
    if pending:
        id_key = "entryTalkId" if "entryTalkId" in value or value.get("type") == "post_expose" else "talkId"
        if update_entry(value, section_map, id_key=id_key):
            count += 1
    for nested in value.values():
        count += walk_pending(nested, section_map)
    return count


def update_preview_tables(sections: list[Section], *, write: bool) -> tuple[int, int, int]:
    section_map = {section.stem: section for section in sections}
    scene_path = TABLE_DIR / "SceneConfig.json"
    npc_loop_path = TABLE_DIR / "NPCLoopData.json"
    chapter_path = TABLE_DIR / "ChapterConfig.json"
    scenes = json.loads(scene_path.read_text(encoding="utf-8"))
    npc_rows = json.loads(npc_loop_path.read_text(encoding="utf-8"))
    chapters = json.loads(chapter_path.read_text(encoding="utf-8"))

    npc_count = 0
    event_count = 0
    for scene in scenes:
        if scene.get("Chapter") != "EPI04":
            continue
        for npc in scene.get("NPCInfos") or []:
            npc_count += update_npc_row(npc, section_map)
        scene_event_count = 0
        if scene.get("pendingTalkKey"):
            scene_event_count += int(update_entry(scene, section_map, id_key="entryTalkId"))
        for key, value in scene.items():
            if key != "NPCInfos":
                scene_event_count += walk_pending(value, section_map)
        event_count += scene_event_count
        if scene_event_count and scene.get("previewStatus") == "avg_pending":
            scene["previewStatus"] = "avg_ready_art_pending"

    npc_table_count = 0
    for row in npc_rows:
        npc = row.get("NPC") or {}
        if npc.get("Chapter") == "EPI04":
            npc_table_count += update_npc_row(row, section_map)

    chapter_count = 0
    for chapter in chapters:
        if not str(chapter.get("id") or "").startswith("4"):
            continue
        pending_init = str(chapter.get("pendingInitTalkKey") or "")
        if pending_init:
            section = section_map.get(pending_init)
            if section is None:
                raise ValueError(f"Chapter {chapter.get('id')}: missing init section {pending_init}")
            chapter["initTalk"] = str(section.start_id)
            chapter.pop("pendingInitTalkKey", None)
            chapter_count += 1
        chapter_count += walk_pending(chapter.get("openingSequence") or [], section_map)
        for expose in chapter.get("exposes") or []:
            if expose.get("pendingTalkKey"):
                chapter_count += int(update_entry(expose, section_map, id_key="talkId"))
        chapter_count += walk_pending(chapter.get("postExposeSegments") or [], section_map)
        chapter_count += walk_pending(chapter.get("endingSequence") or {}, section_map)
        chapter["previewStatus"] = "avg_ready_art_pending"
        if str(chapter.get("id")) == "405":
            opening = (chapter.get("openingSequence") or [{}])[0]
            opening.pop("draftSourceTalk", None)

    # References to the old L5 draft filename were planning aliases only.
    def replace_old_l5_name(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                replace_old_l5_name(item)
        elif isinstance(value, dict):
            for key, nested in list(value.items()):
                if nested == "L5_opening_call_to_emma":
                    value[key] = "L5_opening_unanswered_calls"
                else:
                    replace_old_l5_name(nested)

    replace_old_l5_name(scenes)
    replace_old_l5_name(chapters)

    if write:
        scene_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        npc_loop_path.write_text(json.dumps(npc_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        chapter_path.write_text(json.dumps(chapters, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return npc_count + npc_table_count, event_count, chapter_count


def write_avg(sections: list[Section]) -> tuple[int, int]:
    if AVG_ROOT.exists():
        shutil.rmtree(AVG_ROOT)
    talk_count = 0
    expose_count = 0
    expose_files: list[str] = []
    for loop in range(1, 6):
        loop_dir = AVG_ROOT / "Talk" / f"loop{loop}"
        loop_dir.mkdir(parents=True, exist_ok=True)
        filenames: list[str] = []
        for section in sections:
            if section.loop != loop or section.kind != "Talk":
                continue
            payload = render_section(section)
            (loop_dir / section.name).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            filenames.append(section.name)
            talk_count += len(payload)
        (loop_dir / "_manifest.json").write_text(
            json.dumps(filenames, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    expose_dir = AVG_ROOT / "Expose"
    expose_dir.mkdir(parents=True, exist_ok=True)
    for section in sections:
        if section.kind != "Expose":
            continue
        payload = render_section(section)
        (expose_dir / section.name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        expose_files.append(section.name)
        expose_count += len(payload)
    (expose_dir / "_manifest.json").write_text(
        json.dumps(expose_files, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return talk_count, expose_count


def validate_generated(sections: list[Section]) -> list[str]:
    errors: list[str] = []
    all_ids = [node.id for section in sections for node in section.nodes]
    duplicates = sorted({value for value in all_ids if all_ids.count(value) > 1})
    if duplicates:
        errors.append(f"duplicate Talk IDs: {duplicates[:10]}")
    all_id_set = {str(value) for value in all_ids}
    for section in sections:
        rows = render_section(section)
        for row in rows:
            next_id = str(row.get("next") or "")
            if next_id and next_id not in all_id_set:
                errors.append(f"{section.name} #{row['id']}: next target {next_id} not found")
            if row["script"] == "branches":
                for parameter in row.get("Parameters") or []:
                    if str(parameter["ParameterInt"]) not in all_id_set:
                        errors.append(f"{section.name} #{row['id']}: branch target missing")
            if row["script"] == "Lie" and str(row["ParameterInt0"]) not in all_id_set:
                errors.append(f"{section.name} #{row['id']}: Lie success target missing")
        if section.kind == "Expose" and set(section.lie_indices) != {1, 2, 3}:
            errors.append(f"{section.name}: expected rounds 1-3, found {sorted(section.lie_indices)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write AVG/EPI04 and preview-table updates")
    args = parser.parse_args()

    sections = load_sections()
    testimony_summaries = {
        match.group(1): match.group(2)
        for section in sections
        for match in GET_RE.finditer(section.body)
    }
    for section in sections:
        parse_section(section, testimony_summaries)
    allocate_ids(sections)
    finalize_links(sections)
    errors = validate_generated(sections)
    if errors:
        print("Unit4 AVG build FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    npc_refs, scene_events, chapter_refs = update_preview_tables(sections, write=args.write)
    talk_nodes = sum(len(section.nodes) for section in sections if section.kind == "Talk")
    expose_nodes = sum(len(section.nodes) for section in sections if section.kind == "Expose")
    if args.write:
        talk_nodes, expose_nodes = write_avg(sections)

    mode = "WRITE" if args.write else "CHECK"
    print(f"Unit4 AVG build {mode} PASS")
    print(f"- sections: {len(sections)} ({sum(s.kind == 'Talk' for s in sections)} Talk, {sum(s.kind == 'Expose' for s in sections)} Expose)")
    print(f"- nodes: {talk_nodes} Talk, {expose_nodes} Expose")
    print(f"- preview refs: {npc_refs} NPC entries, {scene_events} scene events, {chapter_refs} chapter entries")
    for loop in range(1, 6):
        loop_sections = [section for section in sections if section.loop == loop]
        print(f"- loop{loop}: {len(loop_sections)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
