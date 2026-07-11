#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build a planning-level UnitFlow file from avg_editor_v2 table snapshots.

This is an editor-only interpretation layer. It does not replace formal tables.
"""

from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
TABLE_DIR = os.path.join(HERE, "data", "table")
OUT_DIR = os.path.join(HERE, "data", "formal")
OUT_PATH = os.path.join(OUT_DIR, "unit_flow.json")
CANON_MANIFEST_PATH = os.path.join(REPO_ROOT, "canon_manifest.json")
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from validate_canon_manifest import load_and_validate_manifest  # noqa: E402


def load_table(name: str, table_dir: str = TABLE_DIR):
    path = os.path.join(table_dir, f"{name}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cn(value, fallback: str = "") -> str:
    if isinstance(value, list):
        return str(value[0] if value else fallback)
    if value is None:
        return fallback
    return str(value)


def first_number(value) -> int:
    try:
        return int(str(value))
    except Exception:
        return 0


def normalize_id(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def unit_loop_from_chapter(chapter_id: str):
    s = normalize_id(chapter_id)
    if len(s) < 3:
        return None, None
    return s[0], int(s[-1])


def scene_name(scene: dict) -> str:
    loc = scene.get("location") or {}
    return cn(loc.get("Name"), f"Scene {scene.get('sceneId')}")


def scene_kind(scene: dict, art_by_id: dict) -> str:
    loc = scene.get("location") or {}
    bg = scene.get("backgroundImage") or loc.get("backgroundImage") or ""
    art = art_by_id.get(str(bg))
    return art.get("sceneKind") if art else ""


def condition_label(condition: dict, items_by_id: dict, testimony_by_id: dict) -> str:
    typ = normalize_id(condition.get("type"))
    param = normalize_id(condition.get("param"))
    if typ in ("3", "4"):
        t = testimony_by_id.get(param)
        kind = "时间线证词" if typ == "3" else "证词"
        return f"{kind} {param} · {cn(t.get('shortDesc') or t.get('testimony')) if t else '未找到'}"
    item = items_by_id.get(param)
    if item:
        return f"道具 {param} · {cn(item.get('Name'))}"
    return f"条件 {typ}:{param}"


def loop_from_encoded_id(value: str, mode: str, analyzed_source_by_id: dict[str, str] | None = None):
    s = normalize_id(value)
    if mode == "item" and analyzed_source_by_id and s in analyzed_source_by_id:
        s = analyzed_source_by_id[s]
    idx = 1 if mode == "item" else 3
    if len(s) <= idx:
        return None
    ch = s[idx]
    if ch >= "1" and ch <= "6":
        return int(ch)
    return None


def condition_dependency(condition: dict, current_loop: int, items_by_id: dict,
                         testimony_by_id: dict, analyzed_source_by_id: dict) -> dict:
    typ = normalize_id(condition.get("type"))
    param = normalize_id(condition.get("param"))

    exists = False
    name = ""
    kind = "未知"
    source_loop = None

    if typ == "1":
        kind = "道具"
        item = items_by_id.get(param)
        exists = item is not None
        name = cn(item.get("Name")) if item else ""
        source_loop = loop_from_encoded_id(param, "item", analyzed_source_by_id)
    elif typ in ("3", "4"):
        kind = "时间线证词" if typ == "3" else "证词"
        testimony = testimony_by_id.get(param)
        exists = testimony is not None
        name = cn(testimony.get("shortDesc") or testimony.get("testimony")) if testimony else ""
        source_loop = loop_from_encoded_id(param, "testimony")
    elif typ == "2":
        kind = "关系"
        exists = bool(param)
        name = f"关系连接 {param}" if param else ""

    if not exists:
        status = "missing"
        status_text = "未找到"
    elif source_loop is None:
        status = "unknown"
        status_text = "来源未知"
    elif source_loop > current_loop:
        status = "future"
        status_text = f"未来依赖 L{source_loop}"
    elif source_loop < current_loop:
        status = "previous"
        status_text = f"前置依赖 L{source_loop}"
    else:
        status = "current"
        status_text = f"当前 Loop L{source_loop}"

    return {
        "kind": kind,
        "name": name or "未找到",
        "label": condition_label(condition, items_by_id, testimony_by_id),
        "exists": exists,
        "sourceLoop": f"loop{source_loop}" if source_loop else "",
        "sourceLoopNum": source_loop or 0,
        "status": status,
        "statusText": status_text,
    }


def unit_labels_from_manifest(manifest: dict) -> dict[str, dict]:
    labels: dict[str, dict] = {}
    for chapter in manifest["chapters"]:
        if not chapter["tooling"]["buildUnitFlow"]:
            continue
        canonical_unit = chapter["canonicalUnit"]
        unit_number = canonical_unit.removeprefix("Unit")
        labels[unit_number] = {
            "key": canonical_unit,
            "title": chapter["playerTitle"],
            "chapter": chapter["unityEpisode"],
        }
    return labels


def apply_flow_aliases(units: dict[str, dict], manifest: dict) -> dict[str, dict]:
    for alias_config in manifest["flowAliases"]:
        if not alias_config["enabled"]:
            continue
        alias_name = alias_config["name"]
        target_name = alias_config["target"]
        if target_name not in units:
            raise ValueError(f"flow alias {alias_name} target {target_name} was not built")
        alias = deepcopy(units[target_name])
        alias["unit"] = alias_name
        alias["formalUnit"] = target_name
        alias["title"] = alias_config["title"]
        units[alias_name] = alias
    return units


def build(
    table_dir: str = TABLE_DIR,
    out_path: str = OUT_PATH,
    manifest_path: str = CANON_MANIFEST_PATH,
):
    manifest = load_and_validate_manifest(Path(manifest_path), Path(REPO_ROOT))
    unit_labels = unit_labels_from_manifest(manifest)
    chapters = load_table("ChapterConfig", table_dir)
    scenes = load_table("SceneConfig", table_dir)
    items = load_table("ItemStaticData", table_dir)
    testimonies = load_table("TestimonyItem", table_dir)
    art_assets = load_table("ArtAssetConfig", table_dir)

    items_by_id = {normalize_id(i.get("id")): i for i in items}
    testimony_by_id = {normalize_id(t.get("id")): t for t in testimonies}
    scenes_by_id = {normalize_id(s.get("sceneId")): s for s in scenes}
    art_by_id = {normalize_id(a.get("id")): a for a in art_assets}
    analyzed_source_by_id = {
        normalize_id(i.get("analysedEvidence")): normalize_id(i.get("id"))
        for i in items
        if normalize_id(i.get("analysedEvidence"))
    }

    units: dict[str, dict] = {}
    for unit_num, meta in unit_labels.items():
        units[meta["key"]] = {
            "unit": meta["key"],
            "formalUnit": meta["key"],
            "chapter": meta["chapter"],
            "title": meta["title"],
            "loops": [],
        }

    for ch in sorted(chapters, key=lambda c: first_number(c.get("id"))):
        unit_num, loop_num = unit_loop_from_chapter(ch.get("id"))
        if not unit_num or unit_num not in unit_labels:
            continue
        unit_key = unit_labels[unit_num]["key"]
        chapter_id = normalize_id(ch.get("id"))
        init_scene_id = normalize_id(ch.get("initScene"))

        open_scenes = [
            s for s in scenes
            if normalize_id(s.get("sceneId")).startswith(unit_num)
            and first_number(s.get("loop")) == loop_num
            and s.get("isOpen") is not False
        ]
        open_scenes.sort(key=lambda s: first_number(s.get("sceneId")))

        scene_nodes = []
        for s in open_scenes:
            sid = normalize_id(s.get("sceneId"))
            npc_count = len(s.get("NPCInfos") or [])
            item_ids = [normalize_id(x) for x in (s.get("ItemIDs") or [])]
            evidence_count = len([x for x in item_ids if x in items_by_id])
            scene_nodes.append({
                "id": sid,
                "name": scene_name(s),
                "kind": scene_kind(s, art_by_id) or "unknown",
                "isInit": sid == init_scene_id,
                "npcCount": npc_count,
                "itemCount": evidence_count,
                "itemIds": item_ids,
            })

        doubts = []
        for d in ch.get("doubts") or []:
            conditions = d.get("condition") or []
            doubts.append({
                "id": normalize_id(d.get("id")),
                "text": d.get("text") or "",
                "conditions": [
                    {
                        "type": normalize_id(c.get("type")),
                        "param": normalize_id(c.get("param")),
                        **condition_dependency(c, loop_num, items_by_id, testimony_by_id, analyzed_source_by_id),
                    }
                    for c in conditions
                ],
            })

        exposes = []
        for e in ch.get("exposes") or []:
            testimony_id = normalize_id(e.get("testimony"))
            evidence_ids = [normalize_id(x) for x in (e.get("item") or [])]
            exposes.append({
                "id": normalize_id(e.get("id")),
                "talkId": normalize_id(e.get("talkId")),
                "testimony": testimony_id,
                "testimonyLabel": condition_label({"type": "4", "param": testimony_id}, items_by_id, testimony_by_id) if testimony_id and testimony_id != "0" else "",
                "items": [
                    {
                        "id": item_id,
                        "name": cn(items_by_id.get(item_id, {}).get("Name"), "未找到"),
                    }
                    for item_id in evidence_ids
                ],
            })

        post_expose_segments = []
        for seg in ch.get("postExposeSegments") or []:
            scene_id = normalize_id(seg.get("sceneId"))
            scene = scenes_by_id.get(scene_id)
            post_expose_segments.append({
                "order": first_number(seg.get("order")) or len(post_expose_segments) + 1,
                "type": normalize_id(seg.get("type")) or "talk",
                "title": normalize_id(seg.get("title")),
                "brief": normalize_id(seg.get("brief")),
                "sceneId": scene_id,
                "sceneName": scene_name(scene) if scene else "",
                "sceneKind": scene_kind(scene, art_by_id) if scene else "",
                "videoEpisode": normalize_id(seg.get("videoEpisode")),
                "videoLoop": normalize_id(seg.get("videoLoop")),
                "videoScene": normalize_id(seg.get("videoScene")),
                "entryTalkId": normalize_id(seg.get("entryTalkId")),
                "transitionFrom": normalize_id(seg.get("transitionFrom")),
                "transitionLabel": normalize_id(seg.get("transitionLabel")),
            })
        post_expose_segments.sort(key=lambda s: s["order"])

        flow = []
        flow.append({
            "type": "opening",
            "title": "开篇",
            "summary": f"从 Talk {normalize_id(ch.get('initTalk')) or '未配置'} 进入本 Loop。",
            "refs": {"talkId": normalize_id(ch.get("initTalk")), "sceneId": init_scene_id},
        })
        flow.append({
            "type": "exploration",
            "title": "自由探索",
            "summary": f"{len(scene_nodes)} 个开放场景，其中 {sum(1 for s in scene_nodes if s['kind'] == 'explore')} 个探索底图、{sum(1 for s in scene_nodes if s['kind'] == 'dialogue')} 个对话底图。",
            "refs": {"sceneCount": len(scene_nodes)},
        })
        if doubts:
            flow.append({
                "type": "doubts",
                "title": "疑点推进",
                "summary": f"{len(doubts)} 个疑点需要在本 Loop 内满足。",
                "refs": {"doubtIds": [d["id"] for d in doubts]},
            })
        if exposes:
            flow.append({
                "type": "expose",
                "title": "指证",
                "summary": f"{len(exposes)} 轮指证，目标 NPC {normalize_id(ch.get('exposeNpcId')) or '未配置'}。",
                "refs": {"npcId": normalize_id(ch.get("exposeNpcId")), "roundCount": len(exposes)},
            })
        if post_expose_segments:
            titles = " / ".join(s["title"] or s["videoScene"] or f"段落{s['order']}" for s in post_expose_segments)
            flow.append({
                "type": "postExpose",
                "title": "指证后剧情",
                "summary": f"{len(post_expose_segments)} 段指证后剧情：{titles}",
                "refs": {
                    "segmentCount": len(post_expose_segments),
                    "sceneIds": [s["sceneId"] for s in post_expose_segments if s["sceneId"]],
                },
            })
        flow.append({
            "type": "summary",
            "title": "Loop 收束",
            "summary": cn(ch.get("summaryContent"), "未配置总结"),
            "refs": {"clearDoubts": ch.get("clearDoubts") or []},
        })

        units[unit_key]["loops"].append({
            "id": f"loop{loop_num}",
            "loop": loop_num,
            "chapterId": chapter_id,
            "title": cn(ch.get("chapterTitle"), f"Loop {loop_num}"),
            "brief": cn(ch.get("chapterBrief")),
            "openingBrief": cn(ch.get("openingBrief")),
            "goal": cn(ch.get("chapterGoal")),
            "initTalk": normalize_id(ch.get("initTalk")),
            "initScene": init_scene_id,
            "newDoubtTitle": cn(ch.get("newDoubtTitle")),
            "newDoubtContent": cn(ch.get("newDoubtContent")),
            "summaryTitle": cn(ch.get("summaryTitle")),
            "summaryContent": cn(ch.get("summaryContent")),
            "scenes": scene_nodes,
            "doubts": doubts,
            "exposes": exposes,
            "postExposeSegments": post_expose_segments,
            "flow": flow,
        })

    apply_flow_aliases(units, manifest)

    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "avg_editor_v2/data/table",
        "purpose": "planning-level flow overview for editor UI",
        "units": units,
    }

    output_dir = os.path.dirname(out_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


if __name__ == "__main__":
    data = build()
    print(f"wrote {OUT_PATH}")
    for unit, info in data["units"].items():
        print(f"  {unit}: {len(info['loops'])} loops")
