#!/usr/bin/env python3
"""Rebuild the canonical Unit1 AI-readable script from Unity runtime tables.

The Unity tables are JSON-like rather than strict JSON: they contain trailing
commas, raw newlines in strings, and unescaped Windows path separators.  This
tool normalizes those quirks in memory, never edits D:\\NDC, and writes a
reproducible Markdown corpus plus an audit report under the requested output
directory.

Runtime truth wins for IDs, speakers, words, routing, scripts, parameters,
scene names, and entry points. The archived pre-migration EPI09 authoring copy
is used only to enrich actions and key-info annotations when both the spoken
text and speaker identity still match. Reused IDs with revised content are
written to a conflict ledger.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_NAMES = {
    "": "none",
    "0": "none",
    "1": "branches",
    "2": "end",
    "3": "get",
    "4": "del",
    "5": "exhibit",
    "6": "comic",
    "7": "expose",
    "8": "change_scene",
    "9": "unlock_map",
    "10": "play_video",
    "11": "finalexpose",
    "12": "unlock_scene",
    "13": "new_npc_in",
    "14": "npc_out",
    "15": "loop_end",
    "16": "reverb",
    "17": "infoShowNode",
    "18": "itemShowNode",
}

OPTION_MARKERS = ["❶", "❷", "❸", "❹", "❺"]
LEGACY_ANNOTATION_ID = re.compile(
    r"(?<![A-Za-z0-9_])9(\d{8}|\d{6}|\d{5}|\d{3})(?!\d)"
)


@dataclass(frozen=True)
class RuntimePaths:
    table_dir: Path
    talk: Path
    scene: Path
    expose: Path
    chapter: Path
    item: Path
    testimony_item: Path


def normalize_unity_json(text: str) -> str:
    """Convert the project's permissive table syntax to strict JSON."""
    out: list[str] = []
    in_string = False
    i = 0
    valid_escapes = {'"', "\\", "/", "b", "f", "n", "r", "t", "u"}

    while i < len(text):
        ch = text[i]
        if not in_string:
            out.append(ch)
            if ch == '"':
                in_string = True
            i += 1
            continue

        if ch == '"':
            # Unity tables occasionally contain raw ASCII quotes inside a
            # localized sentence, e.g. `the "special business"`.  A genuine
            # JSON closing quote is followed (ignoring whitespace) by a JSON
            # delimiter; otherwise keep the quote as escaped string content.
            lookahead = i + 1
            while lookahead < len(text) and text[lookahead] in " \t\r\n":
                lookahead += 1
            following = text[lookahead] if lookahead < len(text) else ""
            if following in ",]}:":
                out.append(ch)
                in_string = False
            else:
                out.append('\\"')
            i += 1
            continue

        if ch == "\\":
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if nxt in valid_escapes:
                out.append(ch)
            else:
                out.append("\\\\")
            i += 1
            continue

        if ch == "\r":
            if i + 1 < len(text) and text[i + 1] == "\n":
                i += 1
            out.append("\\n")
            i += 1
            continue
        if ch == "\n":
            out.append("\\n")
            i += 1
            continue
        if ch == "\t":
            out.append("\\t")
            i += 1
            continue
        if ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
            i += 1
            continue

        out.append(ch)
        i += 1

    normalized = "".join(out)
    return re.sub(r",(?=\s*[}\]])", "", normalized)


def load_unity_table(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = json.loads(normalize_unity_json(text))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a top-level array: {path}")
    return [row for row in payload if isinstance(row, dict)]


def scalar(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def localized(value: Any, index: int = 0) -> str:
    if isinstance(value, list):
        if not value:
            return ""
        if index < len(value):
            return scalar(value[index])
        return scalar(value[0])
    return scalar(value)


def formalize_unit1_id(value: Any) -> str:
    text = scalar(value)
    if text.startswith("9") and text.isdigit() and len(text) in {4, 6, 7, 9}:
        return "1" + text[1:]
    return text


def formalize_annotation_ids(value: Any) -> tuple[str, int]:
    """Migrate standalone EPI09 business IDs inside trusted prose annotations.

    Asset keys such as ``SC9003_item_01`` and source paths remain untouched
    because the leading 9 is adjacent to an identifier character.
    """
    return LEGACY_ANNOTATION_ID.subn(lambda match: "1" + match.group(1), scalar(value))


def source_rows(repo_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    by_formal_id: dict[str, dict[str, Any]] = {}
    scene_files: dict[str, Path] = {}
    epi09 = (
        repo_root
        / "旧文档"
        / "Unit1_EPI命名迁移前_20260810"
        / "AVG"
        / "EPI09_9xxx作者版"
    )
    for kind in ("Talk", "Expose"):
        root = epi09 / kind
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.json")):
            if path.name == "_manifest.json":
                continue
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(payload, list):
                continue
            scene_files.setdefault(path.stem, path)
            for row in payload:
                if not isinstance(row, dict) or "id" not in row:
                    continue
                formal_id = formalize_unit1_id(row["id"])
                enriched = dict(row)
                enriched["_source_path"] = str(path.relative_to(repo_root))
                by_formal_id.setdefault(formal_id, enriched)
    return by_formal_id, scene_files


def belongs_to_epi01(row: dict[str, Any]) -> bool:
    if scalar(row.get("videoEpisode")).upper() == "EPI01":
        return True
    speaker = row.get("Speaker")
    return isinstance(speaker, dict) and scalar(speaker.get("Chapter")).upper() == "EPI01"


def split_dialogue_refs(value: Any) -> list[str]:
    return [part.strip() for part in scalar(value).split("/") if part.strip()]


def dialogue_targets(row: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for nxt in split_dialogue_refs(row.get("next")):
        if nxt.isdigit() and len(nxt) in {6, 9}:
            targets.append(nxt)
    if scalar(row.get("script")) == "1":
        for param in row.get("Parameters") or []:
            if not isinstance(param, dict):
                continue
            target = scalar(param.get("ParameterInt"))
            if target.isdigit() and len(target) in {6, 9}:
                targets.append(target)
    return targets


def propagate_video_metadata(rows: list[dict[str, Any]]) -> None:
    """Fill rare system nodes that omit loop/scene metadata from neighbors."""
    by_id = {scalar(row.get("id")): row for row in rows}
    predecessors: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for target in dialogue_targets(row):
            predecessors[target].append(row)

    for _ in range(4):
        changed = False
        for row in rows:
            if row.get("videoLoop") and row.get("videoScene"):
                continue
            candidates: list[dict[str, Any]] = []
            for nxt in split_dialogue_refs(row.get("next")):
                if nxt in by_id:
                    candidates.append(by_id[nxt])
            candidates.extend(predecessors.get(scalar(row.get("id")), []))
            for candidate in candidates:
                if not row.get("videoLoop") and candidate.get("videoLoop"):
                    row["videoLoop"] = candidate["videoLoop"]
                    changed = True
                if not row.get("videoScene") and candidate.get("videoScene"):
                    row["videoScene"] = candidate["videoScene"]
                    changed = True
                if row.get("videoLoop") and row.get("videoScene"):
                    break
        if not changed:
            break


def normalize_legacy_location_ids(
    rows: list[dict[str, Any]], scene_rows: list[dict[str, Any]]
) -> list[dict[str, str]]:
    """Normalize only Location prefixes whose formal 1xxx scene exists.

    Unity Talk still contains a small number of pre-migration Location labels
    such as ``9016 书房`` while Unity SceneConfig already identifies that scene
    as ``1016``. Other 9-prefixed values (events, colors, steps) stay untouched.
    """
    formal_scene_ids = {
        scalar(row.get("sceneId") or row.get("id"))
        for row in scene_rows
        if scalar(row.get("sceneId") or row.get("id")).startswith("1")
    }
    pattern = re.compile(r"^(?P<prefix>\s*)9(?P<tail>\d{3})(?P<suffix>(?:\s.*)?)$")
    changes: list[dict[str, str]] = []
    for row in rows:
        location = row.get("Location")
        values = location if isinstance(location, list) else [location]
        normalized: list[Any] = []
        changed = False
        for value in values:
            if not isinstance(value, str):
                normalized.append(value)
                continue
            match = pattern.match(value)
            candidate = "1" + match.group("tail") if match else ""
            if not match or candidate not in formal_scene_ids:
                normalized.append(value)
                continue
            replacement = match.group("prefix") + candidate + match.group("suffix")
            normalized.append(replacement)
            changed = True
            changes.append(
                {"talkId": scalar(row.get("id")), "from": value, "to": replacement}
            )
        if changed:
            row["Location"] = normalized if isinstance(location, list) else normalized[0]
    return changes


def iter_nested(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_nested(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_nested(child)


def label_for(row: dict[str, Any]) -> str:
    for key in ("Name", "shortDesc", "ShortDescribe", "testimony", "Describe", "text"):
        value = row.get(key)
        label = localized(value, 0).replace("\n", " ").strip()
        if label:
            return label
    return ""


def build_id_labels(*tables: list[dict[str, Any]]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for table in tables:
        for row in table:
            row_id = scalar(row.get("id"))
            if row_id:
                labels[row_id] = label_for(row)
    return labels


def source_speaker_names(source: dict[str, dict[str, Any]]) -> dict[str, str]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in source.values():
        speaker_id = scalar(row.get("IdSpeaker"))
        if speaker_id.startswith("NPC9"):
            speaker_id = "1" + speaker_id[4:]
        elif speaker_id.startswith("NPC"):
            speaker_id = speaker_id[3:]
        name = scalar(row.get("cnSpeaker")).strip()
        if speaker_id and name:
            counts[speaker_id][name] += 1
    return {speaker_id: names.most_common(1)[0][0] for speaker_id, names in counts.items()}


def formal_source_speaker_id(row: dict[str, Any]) -> str:
    speaker_id = scalar(row.get("IdSpeaker"))
    if speaker_id.startswith("NPC9"):
        return "1" + speaker_id[4:]
    if speaker_id.startswith("NPC"):
        return speaker_id[3:]
    return speaker_id


def normalized_words(value: Any) -> str:
    text = scalar(value).replace("…", "...")
    return re.sub(r"\s+", "", text)


def select_trusted_enrichment(
    rows: list[dict[str, Any]],
    source: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    """Keep source annotations only when an ID still represents the same line."""
    trusted: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, str]] = []
    stats = Counter({
        "direct_id_matches": 0,
        "trusted": 0,
        "text_changed": 0,
        "speaker_changed": 0,
        "annotation_ids_normalized": 0,
    })

    for row in rows:
        entry_id = scalar(row.get("id"))
        src = source.get(entry_id)
        if not src:
            continue
        stats["direct_id_matches"] += 1
        runtime_words = localized(row.get("Words"), 0)
        source_words = scalar(src.get("cnWords"))
        speaker = row.get("Speaker") if isinstance(row.get("Speaker"), dict) else {}
        runtime_speaker_id = scalar(speaker.get("id"))
        source_speaker_id = formal_source_speaker_id(src)
        text_matches = normalized_words(runtime_words) == normalized_words(source_words)
        speaker_matches = (
            not runtime_speaker_id
            or not source_speaker_id
            or runtime_speaker_id == source_speaker_id
        )

        reasons: list[str] = []
        if not text_matches:
            stats["text_changed"] += 1
            reasons.append("text_changed")
        if not speaker_matches:
            stats["speaker_changed"] += 1
            reasons.append("speaker_changed")

        if text_matches and speaker_matches:
            enriched = dict(src)
            for field in ("cnAction", "keyInfoContent"):
                enriched[field], count = formalize_annotation_ids(enriched.get(field))
                stats["annotation_ids_normalized"] += count
            trusted[entry_id] = enriched
            stats["trusted"] += 1
            continue

        conflicts.append({
            "id": entry_id,
            "reason": ",".join(reasons),
            "runtimeSpeakerId": runtime_speaker_id,
            "runtimeSpeaker": localized(speaker.get("Name"), 0),
            "sourceSpeakerId": source_speaker_id,
            "sourceSpeaker": scalar(src.get("cnSpeaker")),
            "runtimeWords": runtime_words,
            "sourceWords": source_words,
            "sourcePath": scalar(src.get("_source_path")),
        })
    return trusted, conflicts, dict(stats)


def parameter_text(param: dict[str, Any]) -> str:
    cn = scalar(param.get("ParameterStr"))
    en = scalar(param.get("ParameterEn"))
    target = scalar(param.get("ParameterInt"))
    parts = []
    if cn:
        parts.append(cn)
    if en and en != cn:
        parts.append(f"EN: {en}")
    if target:
        parts.append(f"→ `{target}`")
    return " / ".join(parts) if parts else "（空参数）"


def resolve_parameter(target: str, labels: dict[str, str]) -> str:
    label = labels.get(target, "")
    return f"`{target}`「{label}」" if label else f"`{target}`"


def render_entry(
    row: dict[str, Any],
    source: dict[str, dict[str, Any]],
    speaker_names: dict[str, str],
    labels: dict[str, str],
    expose_by_talk: dict[str, list[dict[str, Any]]],
) -> list[str]:
    entry_id = scalar(row.get("id"))
    script_code = scalar(row.get("script"))
    script_name = SCRIPT_NAMES.get(script_code, f"unknown_{script_code}")
    title = f"### {entry_id}"
    if script_name != "none":
        title += f" `{script_name}`"
    lines = [title]

    src = source.get(entry_id, {})
    speaker = row.get("Speaker") if isinstance(row.get("Speaker"), dict) else {}
    speaker_id = scalar(speaker.get("id"))
    runtime_name = localized(speaker.get("Name"), 0)
    # Runtime speaker metadata is authoritative. The old source is deliberately
    # excluded here because reused IDs can point at a different character.
    cn_speaker = speaker_names.get(speaker_id) or runtime_name or "系统节点"
    en_speaker = localized(speaker.get("Name"), 1)
    action = scalar(src.get("cnAction")).replace("\n", " ").strip()
    speaker_line = f"**{cn_speaker}**"
    if en_speaker and en_speaker != cn_speaker:
        speaker_line += f" / {en_speaker}"
    if action:
        speaker_line += f" [{action}]"
    lines.append(speaker_line)

    words = row.get("Words")
    cn_words = localized(words, 0)
    en_words = localized(words, 1)
    if cn_words:
        for part in cn_words.splitlines() or [cn_words]:
            lines.append(f"> {part}")
    elif script_name == "none":
        lines.append("> （无台词）")
    if en_words:
        for index, part in enumerate(en_words.splitlines() or [en_words]):
            prefix = "> EN: " if index == 0 else "> EN· "
            lines.append(prefix + part)

    params = [p for p in (row.get("Parameters") or []) if isinstance(p, dict)]
    if script_name == "branches":
        for index, param in enumerate(params):
            marker = OPTION_MARKERS[index] if index < len(OPTION_MARKERS) else f"({index + 1})"
            lines.append(f"> - {marker} {parameter_text(param)}")
    elif script_name == "get":
        targets = [scalar(p.get("ParameterInt")) for p in params if scalar(p.get("ParameterInt")) not in {"", "0"}]
        if targets:
            lines.append("> 系统：获取 " + "、".join(resolve_parameter(t, labels) for t in targets))
    elif script_name in {"change_scene", "unlock_map", "unlock_scene", "exhibit", "play_video", "new_npc_in", "npc_out", "infoShowNode", "itemShowNode", "comic", "reverb"}:
        for param in params:
            lines.append(f"> 系统参数：{parameter_text(param)}")

    for expose in expose_by_talk.get(entry_id, []):
        testimony = scalar(expose.get("testimony"))
        items = [scalar(item) for item in (expose.get("item") or [])]
        accepted: list[str] = []
        if testimony and testimony != "0":
            accepted.append(resolve_parameter(testimony, labels))
        accepted.extend(resolve_parameter(item, labels) for item in items if item and item != "0")
        if accepted:
            lines.append("> 指证可用材料：" + "、".join(accepted))

    nxt = scalar(row.get("next"))
    if nxt:
        lines.append(f"→ 下一节点 `{nxt}`")

    key_info_type = scalar(src.get("keyInfoType"))
    key_info = scalar(src.get("keyInfoContent"))
    if key_info_type or key_info:
        lines.append(f"> 设计标注：{key_info_type or 'keyInfo'} — {key_info}")

    metadata = [
        f"step={scalar(row.get('step'))}",
        f"script={script_code or '0'}:{script_name}",
        f"isRight={scalar(row.get('isRight'))}",
        f"waitTime={scalar(row.get('waitTime'))}",
    ]
    static_path = scalar(row.get("staticImagePath"))
    bgm = scalar(row.get("bgm"))
    if static_path:
        metadata.append(f"staticImagePath={static_path}")
    if bgm:
        metadata.append(f"bgm={bgm}")
    if src.get("_source_path"):
        metadata.append(f"actionSource={src['_source_path']}")
    lines.append("<!-- runtime: " + "; ".join(metadata) + " -->")
    lines.append("")
    return lines


def scene_kind(scene: str, expose_scenes: set[str]) -> str:
    if scene in expose_scenes:
        return "Expose"
    if scene.endswith("_repeat"):
        return "Repeat Talk"
    if scene.startswith("ending_"):
        return "Ending"
    return "Talk"


def collect_scene_entry_refs(scene_table: list[dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for node in iter_nested(scene_table):
        for key in ("TalkInfo", "LoopTalkInfo"):
            info = node.get(key)
            if isinstance(info, dict):
                ref = scalar(info.get("id"))
                if ref:
                    refs.append(ref)
    return refs


def collect_scene_entry_map(
    scene_table: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    expose_rows: list[dict[str, Any]],
) -> dict[str, list[tuple[str, str]]]:
    by_scene: dict[str, list[tuple[str, str]]] = defaultdict(list)
    by_id = {scalar(row.get("id")): row for row in rows}
    for node in iter_nested(scene_table):
        for key in ("TalkInfo", "LoopTalkInfo"):
            info = node.get(key)
            if not isinstance(info, dict):
                continue
            entry_id = scalar(info.get("id"))
            row = by_id.get(entry_id, info)
            scene = scalar(row.get("videoScene"))
            if entry_id in by_id and scene:
                pair = (key, entry_id)
                if pair not in by_scene[scene]:
                    by_scene[scene].append(pair)
    for expose in expose_rows:
        entry_id = scalar(expose.get("talkId"))
        row = by_id.get(entry_id)
        if not row:
            continue
        scene = scalar(row.get("videoScene"))
        pair = ("ExposeData", entry_id)
        if scene and pair not in by_scene[scene]:
            by_scene[scene].append(pair)
    return dict(by_scene)


def validate(
    rows: list[dict[str, Any]],
    scene_refs: list[str],
    expose_rows: list[dict[str, Any]],
    labels: dict[str, str],
) -> dict[str, Any]:
    ids = [scalar(row.get("id")) for row in rows]
    id_set = set(ids)
    duplicates = sorted(entry_id for entry_id, count in Counter(ids).items() if count > 1)
    next_refs = [
        ref
        for row in rows
        for ref in split_dialogue_refs(row.get("next"))
        if ref
    ]
    branch_refs = []
    get_refs = []
    for row in rows:
        script = scalar(row.get("script"))
        for param in row.get("Parameters") or []:
            if not isinstance(param, dict):
                continue
            target = scalar(param.get("ParameterInt"))
            if not target or target == "0":
                continue
            if script == "1" and len(target) in {6, 9}:
                branch_refs.append(target)
            if script == "3":
                get_refs.append(target)

    expose_refs = [
        scalar(row.get("talkId"))
        for row in expose_rows
        if scalar(row.get("talkId")).startswith("1")
    ]
    expose_materials: list[str] = []
    for row in expose_rows:
        talk_id = scalar(row.get("talkId"))
        if not talk_id.startswith("1"):
            continue
        testimony = scalar(row.get("testimony"))
        if testimony and testimony != "0":
            expose_materials.append(testimony)
        expose_materials.extend(scalar(item) for item in (row.get("item") or []) if scalar(item) not in {"", "0"})

    return {
        "row_count": len(rows),
        "unique_count": len(id_set),
        "duplicates": duplicates,
        "missing_next": sorted(set(next_refs) - id_set),
        "missing_branch": sorted(set(branch_refs) - id_set),
        "missing_scene_entry": sorted({ref for ref in scene_refs if ref.startswith("1")} - id_set),
        "missing_expose_entry": sorted(set(expose_refs) - id_set),
        "missing_get_material": sorted({ref for ref in get_refs if ref not in labels}),
        "missing_expose_material": sorted({ref for ref in expose_materials if ref not in labels}),
        "script_counts": dict(sorted(Counter(scalar(row.get("script")) or "0" for row in rows).items())),
    }


def write_loop_files(
    output_dir: Path,
    rows: list[dict[str, Any]],
    chapter_rows: list[dict[str, Any]],
    source: dict[str, dict[str, Any]],
    speaker_names: dict[str, str],
    labels: dict[str, str],
    expose_rows: list[dict[str, Any]],
    expose_scenes: set[str],
    scene_entry_map: dict[str, list[tuple[str, str]]],
) -> list[dict[str, Any]]:
    expose_by_talk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for expose in expose_rows:
        expose_by_talk[scalar(expose.get("talkId"))].append(expose)

    chapter_by_loop = {scalar(row.get("id"))[-1:]: row for row in chapter_rows if scalar(row.get("id")).startswith("10")}
    output_summary: list[dict[str, Any]] = []

    for loop_number in range(1, 7):
        loop_name = f"loop{loop_number}"
        loop_rows = [row for row in rows if scalar(row.get("videoLoop")).lower() == loop_name]
        scene_groups: dict[str, list[dict[str, Any]]] = {}
        for row in loop_rows:
            scene = scalar(row.get("videoScene")) or "_unassigned"
            scene_groups.setdefault(scene, []).append(row)

        chapter = chapter_by_loop.get(str(loop_number), {})
        title = localized(chapter.get("chapterTitle"), 0) or f"Loop {loop_number}"
        goal = localized(chapter.get("chapterGoal"), 0)
        lines = [
            f"# Unit1 Loop{loop_number} 完整台本｜{title}",
            "",
            "> 正式命名空间：EPI01 / 1xxx。",
            "> 台词、ID、跳转、脚本和参数以 Unity `Assets/table/Talk.json` 为准；动作与设计标注仅从迁移归档中的 EPI09 同 ID 内容补充。",
            f"> 本文件共 {len(loop_rows)} 个运行时节点，{len(scene_groups)} 个场景。",
        ]
        if goal:
            lines.append(f"> Loop 目标：{goal}")
        lines.append("")

        scene_summaries = []
        for scene, scene_rows in scene_groups.items():
            first = scene_rows[0]
            kind = scene_kind(scene, expose_scenes)
            location_cn = localized(first.get("Location"), 0)
            location_en = localized(first.get("Location"), 1)
            lines.extend([f"## {kind}: {scene}", ""])
            if location_cn:
                location_line = f"> 场景：{location_cn}"
                if location_en and location_en != location_cn:
                    location_line += f" / {location_en}"
                lines.append(location_line)
            configured_entries = scene_entry_map.get(scene, [])
            if configured_entries:
                rendered_entries = "；".join(
                    f"{entry_type}=`{entry_id}`" for entry_type, entry_id in configured_entries
                )
                lines.append(f"> 节点数：{len(scene_rows)}｜正式入口：{rendered_entries}")
            else:
                lines.append(
                    f"> 节点数：{len(scene_rows)}｜未配置独立入口；本文件链首：`{scalar(first.get('id'))}`"
                )
            lines.append("")
            for row in scene_rows:
                lines.extend(render_entry(row, source, speaker_names, labels, expose_by_talk))
            scene_summaries.append({
                "scene": scene,
                "kind": kind,
                "entries": len(scene_rows),
                "first_id": scalar(first.get("id")),
                "last_id": scalar(scene_rows[-1].get("id")),
            })

        path = output_dir / f"Loop{loop_number}_完整台本.md"
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        output_summary.append({
            "loop": loop_number,
            "title": title,
            "entries": len(loop_rows),
            "scenes": scene_summaries,
            "path": path.name,
        })
    return output_summary


def write_index(
    output_dir: Path,
    summary: list[dict[str, Any]],
    enrichment_stats: dict[str, int],
) -> None:
    total_entries = sum(loop["entries"] for loop in summary)
    total_scenes = sum(len(loop["scenes"]) for loop in summary)
    lines = [
        "# Unit1 完整台本索引（EPI01 正式运行版）",
        "",
        "## AI 使用说明",
        "",
        "- 本目录是 Unit1《黑哨之夜》的正式可读台本，按 Loop 分文件。",
        "- 台词、英文、正式 ID、分支、next、脚本参数来自 Unity 运行表。",
        "- 方括号动作与“设计标注”来自迁移归档中的 EPI09 同 ID 内容；没有来源时不会补写或猜测。",
        "- Repeat、系统展示节点、场景切换和指证入口均保留，不能只读取普通 Talk。",
        "- 需要推理语义时，同时读取 `剧情设计/Unit1/state/loopX_state.yaml` 和本目录对应 Loop。",
        "- 若台本与策划说明冲突，优先级为：本目录正式台本 / Unity 运行表 > 当前 state > 迁移归档。",
        "- 正式结局止于 11 月 6 日的 `loop_end`；Talk 未执行 `get 1602`，飞车与鞋坊火场不属于当前台本。",
        "",
        "## 数据规模",
        "",
        f"- 正式运行节点：{total_entries}",
        f"- 场景/视频段：{total_scenes}",
        f"- 迁移归档 EPI09 同 ID 节点：{enrichment_stats['direct_id_matches']}",
        f"- 经台词与角色双重校验后可信、可补充动作/标注的节点：{enrichment_stats['trusted']}",
        f"- 同 ID 但台词已改写的节点：{enrichment_stats['text_changed']}（不采用旧动作）",
        f"- 同 ID 但角色身份已变化的节点：{enrichment_stats['speaker_changed']}（不采用旧署名/动作）",
        f"- 可信旧注释内完成 EPI09 → EPI01 业务 ID 转换：{enrichment_stats['annotation_ids_normalized']}",
        "",
        "## Loop 文件",
        "",
        "| Loop | 标题 | 节点 | 场景 | 文件 |",
        "|---|---|---:|---:|---|",
    ]
    for loop in summary:
        lines.append(
            f"| Loop{loop['loop']} | {loop['title']} | {loop['entries']} | {len(loop['scenes'])} | [{loop['path']}]({loop['path']}) |"
        )

    for loop in summary:
        lines.extend(["", f"## Loop{loop['loop']} 场景清单", "", "| 类型 | 场景 | 节点数 | ID 范围 |", "|---|---|---:|---|"])
        for scene in loop["scenes"]:
            lines.append(
                f"| {scene['kind']} | `{scene['scene']}` | {scene['entries']} | `{scene['first_id']}` → `{scene['last_id']}` |"
            )

    (output_dir / "Unit1_完整台本索引.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_audit(
    output_dir: Path,
    audit: dict[str, Any],
    paths: RuntimePaths,
    rows: list[dict[str, Any]],
    enrichment_stats: dict[str, int],
) -> None:
    issue_keys = [
        "duplicates",
        "missing_next",
        "missing_branch",
        "missing_scene_entry",
        "missing_expose_entry",
        "missing_get_material",
        "missing_expose_material",
    ]
    lines = [
        "# Unit1 EPI01 台本重构审查报告",
        "",
        "## 来源",
        "",
        f"- Talk：`{paths.talk}`",
        f"- SceneConfig：`{paths.scene}`",
        f"- ExposeData：`{paths.expose}`",
        f"- ChapterConfig：`{paths.chapter}`",
        f"- ItemStaticData：`{paths.item}`",
        f"- TestimonyItem：`{paths.testimony_item}`",
        "",
        "## 核心校验",
        "",
        "| 项目 | 结果 | 详情 |",
        "|---|---|---|",
        f"| 运行节点数 | PASS | {audit['row_count']} |",
        f"| ID 唯一性 | {'PASS' if not audit['duplicates'] else 'FAIL'} | 唯一 {audit['unique_count']} |",
        f"| next 闭环 | {'PASS' if not audit['missing_next'] else 'FAIL'} | 缺失 {len(audit['missing_next'])} |",
        f"| branches 闭环 | {'PASS' if not audit['missing_branch'] else 'FAIL'} | 缺失 {len(audit['missing_branch'])} |",
        f"| SceneConfig 入口 | {'PASS' if not audit['missing_scene_entry'] else 'FAIL'} | 缺失 {len(audit['missing_scene_entry'])} |",
        f"| ExposeData 入口 | {'PASS' if not audit['missing_expose_entry'] else 'FAIL'} | 缺失 {len(audit['missing_expose_entry'])} |",
        f"| get 材料引用 | {'PASS' if not audit['missing_get_material'] else 'WARN'} | 未解析 {len(audit['missing_get_material'])} |",
        f"| 指证材料引用 | {'PASS' if not audit['missing_expose_material'] else 'FAIL'} | 未解析 {len(audit['missing_expose_material'])} |",
        f"| Location 旧场景号归一化 | PASS | {len(audit.get('normalized_legacy_locations', []))} 个字段；仅在 SceneConfig 存在对应 1xxx 时转换 |",
        f"| 旧稿动作可信补充 | PASS | {enrichment_stats['trusted']} / {enrichment_stats['direct_id_matches']}；其余不采用 |",
        f"| 旧注释业务 ID 归一化 | PASS | {enrichment_stats['annotation_ids_normalized']} 处 EPI09 ID 已转换为 EPI01 |",
        "",
        "## Script 分布",
        "",
        "| script | 语义 | 数量 |",
        "|---:|---|---:|",
    ]
    for code, count in audit["script_counts"].items():
        lines.append(f"| {code} | {SCRIPT_NAMES.get(code, 'unknown')} | {count} |")

    for key in issue_keys:
        if not audit[key]:
            continue
        lines.extend(["", f"## {key}", ""])
        lines.extend(f"- `{value}`" for value in audit[key])

    missing_metadata = [
        scalar(row.get("id"))
        for row in rows
        if not row.get("videoLoop") or not row.get("videoScene")
    ]
    lines.extend([
        "",
        "## 元数据补全",
        "",
        f"- 传播后仍缺少 Loop/Scene 的节点：{len(missing_metadata)}",
    ])
    lines.extend(f"- `{entry_id}`" for entry_id in missing_metadata)
    if audit.get("normalized_legacy_locations"):
        lines.extend(["", "## Unity Talk Location 残留归一化", ""])
        lines.append(
            "Unity Talk 原表保持只读；项目输出按 Unity SceneConfig 的正式场景号修正如下："
        )
        for change in audit["normalized_legacy_locations"]:
            lines.append(
                f"- `{change['talkId']}`：`{change['from']}` → `{change['to']}`"
            )
    (output_dir / "Unit1_重构审查报告.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_conflict_ledger(output_dir: Path, conflicts: list[dict[str, str]]) -> None:
    payload = {
        "description": "迁移归档的 EPI09 与当前 EPI01 使用同一映射 ID，但台词或说话人已变化；这些旧稿动作和标注未进入正式台本。",
        "count": len(conflicts),
        "rows": conflicts,
    }
    (output_dir / "Unit1_EPI09来源差异清单.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_avg_scene_files(
    avg_output_dir: Path,
    rows: list[dict[str, Any]],
    expose_scenes: set[str],
) -> dict[str, Any]:
    """Write strict-JSON EPI01 scene files from the verified runtime rows."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        loop_name = scalar(row.get("videoLoop")).lower()
        scene_name = scalar(row.get("videoScene"))
        grouped.setdefault((loop_name, scene_name), []).append(row)

    file_rows: list[dict[str, Any]] = []
    for (loop_name, scene_name), scene_rows in grouped.items():
        is_expose = scene_name in expose_scenes and not scene_name.endswith("_repeat")
        if is_expose:
            relative = Path("Expose") / f"{scene_name}.json"
            kind = "Expose"
        else:
            relative = Path("Talk") / loop_name / f"{scene_name}.json"
            kind = "Talk"
        path = avg_output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(scene_rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        file_rows.append({
            "path": relative.as_posix(),
            "kind": kind,
            "loop": loop_name,
            "scene": scene_name,
            "rows": len(scene_rows),
            "firstId": scalar(scene_rows[0].get("id")),
            "lastId": scalar(scene_rows[-1].get("id")),
        })

    manifest = {
        "episode": "EPI01",
        "canonicalUnit": "Unit1",
        "source": r"D:\NDC\Assets\table\Talk.json",
        "sourceRole": "Unity formal runtime truth",
        "generatedBy": "AVG/Tools/rebuild_unit1_runtime_script.py",
        "rowCount": len(rows),
        "uniqueIdCount": len({scalar(row.get('id')) for row in rows}),
        "fileCount": len(file_rows),
        "files": file_rows,
    }
    (avg_output_dir / "_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def write_preview_talk_mirror(path: Path, unit1_rows: list[dict[str, Any]]) -> dict[str, int]:
    """Replace only Unit1 rows in the preview table, preserving other chapters."""
    existing = load_unity_table(path)
    preserved = [row for row in existing if not belongs_to_epi01(row)]
    merged = unit1_rows + preserved
    path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "removedUnit1": len(existing) - len(preserved),
        "insertedUnit1": len(unit1_rows),
        "preservedOther": len(preserved),
        "total": len(merged),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--unity-root", type=Path, default=Path(r"D:\NDC"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Defaults to AVG/对话配置工作及草稿/Unit1",
    )
    parser.add_argument("--check-only", action="store_true", help="Audit inputs without writing Markdown")
    parser.add_argument(
        "--avg-output-dir",
        type=Path,
        default=None,
        help="Also write strict-JSON EPI01 Talk/Expose scene files to this directory",
    )
    parser.add_argument(
        "--preview-talk-path",
        type=Path,
        default=None,
        help="Replace Unit1 rows in a project preview Talk.json while preserving other chapters",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_dir = (args.output_dir or (repo_root / "AVG" / "对话配置工作及草稿" / "Unit1")).resolve()
    table_dir = args.unity_root.resolve() / "Assets" / "table"
    paths = RuntimePaths(
        table_dir=table_dir,
        talk=table_dir / "Talk.json",
        scene=table_dir / "SceneConfig.json",
        expose=table_dir / "ExposeData.json",
        chapter=table_dir / "ChapterConfig.json",
        item=table_dir / "ItemStaticData.json",
        testimony_item=table_dir / "TestimonyItem.json",
    )

    for path in paths.__dict__.values():
        if isinstance(path, Path) and not path.exists():
            raise FileNotFoundError(path)

    talk_rows = load_unity_table(paths.talk)
    scene_rows = load_unity_table(paths.scene)
    expose_rows = load_unity_table(paths.expose)
    chapter_rows = load_unity_table(paths.chapter)
    item_rows = load_unity_table(paths.item)
    testimony_rows = load_unity_table(paths.testimony_item)

    unit1_rows = [dict(row) for row in talk_rows if belongs_to_epi01(row)]
    normalized_locations = normalize_legacy_location_ids(unit1_rows, scene_rows)
    propagate_video_metadata(unit1_rows)

    source, _ = source_rows(repo_root)
    trusted_source, source_conflicts, enrichment_stats = select_trusted_enrichment(unit1_rows, source)
    speaker_names = source_speaker_names(source)
    labels = build_id_labels(item_rows, testimony_rows, scene_rows)
    scene_refs = collect_scene_entry_refs(scene_rows)
    audit = validate(unit1_rows, scene_refs, expose_rows, labels)
    audit["normalized_legacy_locations"] = normalized_locations

    print(f"Unit1 runtime rows: {audit['row_count']}")
    print(f"Unique IDs: {audit['unique_count']}")
    print(f"Archived EPI09 direct ID matches: {enrichment_stats['direct_id_matches']}")
    print(f"Trusted archived EPI09 enrichments: {enrichment_stats['trusted']}")
    print(f"Archived EPI09 source conflicts: {len(source_conflicts)}")
    print(f"Normalized IDs inside trusted annotations: {enrichment_stats['annotation_ids_normalized']}")
    print(f"Normalized legacy Location fields: {len(normalized_locations)}")
    for key in ("duplicates", "missing_next", "missing_branch", "missing_scene_entry", "missing_expose_entry", "missing_expose_material"):
        print(f"{key}: {len(audit[key])}")
        if audit[key]:
            print("  " + ", ".join(audit[key]))

    if args.check_only:
        return 1 if any(audit[key] for key in ("duplicates", "missing_next", "missing_branch", "missing_scene_entry", "missing_expose_entry", "missing_expose_material")) else 0

    output_dir.mkdir(parents=True, exist_ok=True)
    expose_scenes = {
        scalar(row.get("videoScene"))
        for row in unit1_rows
        if scalar(row.get("script")) in {"7", "11"}
    }
    expose_scenes.update({f"Loop{loop}_{name}" for loop, name in [(1, "rosa"), (2, "tommy"), (3, "rosa"), (4, "vivian"), (5, "james"), (6, "morrison")]})
    scene_entry_map = collect_scene_entry_map(scene_rows, unit1_rows, expose_rows)
    summary = write_loop_files(
        output_dir,
        unit1_rows,
        chapter_rows,
        trusted_source,
        speaker_names,
        labels,
        expose_rows,
        expose_scenes,
        scene_entry_map,
    )
    write_index(output_dir, summary, enrichment_stats)
    write_audit(output_dir, audit, paths, unit1_rows, enrichment_stats)
    write_conflict_ledger(output_dir, source_conflicts)
    if args.avg_output_dir is not None:
        avg_manifest = write_avg_scene_files(args.avg_output_dir.resolve(), unit1_rows, expose_scenes)
        print(
            "Wrote AVG scene files: "
            f"{avg_manifest['fileCount']} files / {avg_manifest['rowCount']} rows -> "
            f"{args.avg_output_dir.resolve()}"
        )
    if args.preview_talk_path is not None:
        preview_stats = write_preview_talk_mirror(args.preview_talk_path.resolve(), unit1_rows)
        print(
            "Updated preview Talk mirror: "
            f"removed {preview_stats['removedUnit1']} old Unit1 / "
            f"inserted {preview_stats['insertedUnit1']} formal Unit1 / "
            f"preserved {preview_stats['preservedOther']} other rows / "
            f"total {preview_stats['total']}"
        )
    print(f"Wrote Unit1 corpus to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
