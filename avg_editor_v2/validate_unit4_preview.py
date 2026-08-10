#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate the persisted Unit4 preview configuration and generated UnitFlow."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
TABLE_DIR = HERE / "data" / "table"
FLOW_PATH = HERE / "data" / "formal" / "unit_flow.json"

EXPECTED_COUNTS = {
    "ChapterConfig": 5,
    "SceneConfig": 27,
    "ItemStaticData": 56,
    "NPCStaticData": 16,
    "NPCLoopData": 14,
    "TestimonyItem": 20,
    "DoubtConfig": 12,
    "ArtAssetConfig": 28,
}


def load(name: str) -> list[dict]:
    return json.loads((TABLE_DIR / f"{name}.json").read_text(encoding="utf-8"))


def is_unit4(name: str, row: dict) -> bool:
    if row.get("Chapter") == "EPI04":
        return True
    key = row.get("sceneId") if name == "SceneConfig" else row.get("id")
    return str(key or "").startswith("4")


def validate() -> list[str]:
    errors: list[str] = []
    tables = {name: load(name) for name in EXPECTED_COUNTS}
    unit4 = {name: [row for row in rows if is_unit4(name, row)] for name, rows in tables.items()}

    for name, expected in EXPECTED_COUNTS.items():
        actual = len(unit4[name])
        if actual != expected:
            errors.append(f"{name}: expected {expected} Unit4 rows, found {actual}")

    for name, rows in tables.items():
        key = "sceneId" if name == "SceneConfig" else "id"
        ids = [str(row.get(key) or "") for row in rows]
        duplicates = sorted({value for value in ids if value and ids.count(value) > 1})
        if duplicates:
            errors.append(f"{name}: duplicate ids {duplicates}")

    item_ids = {str(row["id"]) for row in tables["ItemStaticData"]}
    testimony_ids = {str(row["id"]) for row in tables["TestimonyItem"]}
    npc_ids = {str(row["id"]) for row in tables["NPCStaticData"]}
    npc_loop_ids = {str(row["id"]) for row in tables["NPCLoopData"]}
    scene_ids = {str(row["sceneId"]) for row in tables["SceneConfig"]}
    material_ids = item_ids | testimony_ids

    for item in unit4["ItemStaticData"]:
        item_id = str(item["id"])
        for field in ("Name", "Describe", "ShortDescribe"):
            values = item.get(field)
            if not isinstance(values, list) or len(values) < 2 or not all(str(value).strip() for value in values[:2]):
                errors.append(f"Item {item_id}: {field} must contain non-empty Chinese and English text")
        if str((item.get("Name") or ["", ""])[1]).startswith("u4_item_"):
            errors.append(f"Item {item_id}: English name is still a preview placeholder")
        requirement = str(item.get("ArtRequirement") or "")
        if not requirement.startswith("【信息表达必不可少】\n") or "\n【风格参考】\n" not in requirement:
            errors.append(f"Item {item_id}: art requirement does not follow the Unit3 production-card style")
        if "Unit4 预览占位" in requirement:
            errors.append(f"Item {item_id}: art requirement is still a preview placeholder")

    spoiler_sensitive = {"4513", "4515", "4516"}
    for item in unit4["ItemStaticData"]:
        item_id = str(item["id"])
        if item_id not in spoiler_sensitive:
            continue
        visible_text = "\n".join(
            [
                *[str(value) for value in item.get("Name") or []],
                *[str(value) for value in item.get("Describe") or []],
                *[str(value) for value in item.get("ShortDescribe") or []],
            ]
        )
        if "Mickey" in visible_text or "Michael F. Donnelly" in visible_text:
            errors.append(f"Item {item_id}: pre-acknowledgment text reveals Mickey's identity")
        requirement = str(item.get("ArtRequirement") or "")
        if item_id == "4513" and (
            "接管人 Michael F. Donnelly" in requirement or "Mickey 正式接管" in requirement
        ):
            errors.append("Item 4513: art brief requires a direct Mickey / Whale identity mapping")

    item_map = {str(item["id"]): item for item in unit4["ItemStaticData"]}
    special_asset_ids = {"4516", "4704", "4705", "4706", "4707", "4708", "4709"}
    for item_id, item in item_map.items():
        if item_id in special_asset_ids:
            if any(item.get(field) for field in ("folderPath", "desSpritePath", "mapSpritePath", "iconPath")):
                errors.append(f"Item {item_id}: special evidence must not use standard item art paths")
            if not item.get("previewAssetMode") or not item.get("previewAssetNote"):
                errors.append(f"Item {item_id}: special evidence disposition is missing")
            continue
        if not str(item.get("folderPath") or "").startswith("EPI04\\u4_"):
            errors.append(f"Item {item_id}: resource folder is not preconfigured")
        if not item.get("desSpritePath") or not item.get("mapSpritePath") or not item.get("iconPath"):
            errors.append(f"Item {item_id}: detail/map/icon resource name is missing")

    item_4316 = item_map.get("4316") or {}
    if item_4316.get("previewEvidenceStates"):
        errors.append("Item 4316: must remain a single static pre-blast evidence record")

    item_4111 = item_map.get("4111") or {}
    if item_4111.get("sourceScene") != "4003" or item_4111.get("obtainMethod") != "minigame_output":
        errors.append("Item 4111: must be generated by the archive minigame in scene 4003")
    if "4122" in item_ids or "4123" in item_ids:
        errors.append("Items 4122/4123: minigame auxiliary pages must not enter ItemStaticData")

    resolved_sources = {
        "4315": ("clue", "4027"),
        "4418": ("key_item", "4034"),
        "4704": ("derived_memory", "4034"),
    }
    for item_id, (source_type, source_scene) in resolved_sources.items():
        item = item_map.get(item_id) or {}
        if item.get("sourceStateType") != source_type or item.get("sourceScene") != source_scene:
            errors.append(
                f"Item {item_id}: expected source {source_type}/{source_scene}, "
                f"found {item.get('sourceStateType')}/{item.get('sourceScene')}"
            )

    for item_id in ("4511", "4512", "4514", "4515"):
        item = item_map.get(item_id) or {}
        if item.get("canAnalyzed") != "false" or item.get("previewAnalysisRequired"):
            errors.append(f"Item {item_id}: identity-lock input must not use standard analysis")

    for item_id in ("4117", "4118", "4212", "4213", "4214", "4703"):
        if "SHC-28-B17" not in str((item_map.get(item_id) or {}).get("ArtRequirement") or ""):
            errors.append(f"Item {item_id}: Sacred Heart batch code SHC-28-B17 is missing")

    art_asset_ids = {str(row["id"]) for row in unit4["ArtAssetConfig"]}
    scene_map = {str(scene["sceneId"]): scene for scene in unit4["SceneConfig"]}
    for scene in unit4["SceneConfig"]:
        sid = str(scene["sceneId"])
        background = str((scene.get("location") or {}).get("backgroundImage") or "")
        if not background.startswith("Art\\Scene\\Backgrounds\\EPI04\\u4_"):
            errors.append(f"Scene {sid}: background resource is not preconfigured")
        for resource in scene.get("previewBackgroundImages") or [background]:
            if str(resource) not in art_asset_ids:
                errors.append(f"Scene {sid}: art asset row missing for {resource}")
        for item_id in scene.get("ItemIDs") or []:
            if str(item_id) not in item_ids:
                errors.append(f"Scene {sid}: missing item {item_id}")
        for info in scene.get("NPCInfos") or []:
            npc_loop_id = str(info.get("id") or "")
            npc_id = str((info.get("NPC") or {}).get("id") or "")
            if npc_loop_id and npc_loop_id not in npc_loop_ids:
                errors.append(f"Scene {sid}: missing NPCLoopData row {npc_loop_id}")
            if npc_id and npc_id not in npc_ids:
                errors.append(f"Scene {sid}: missing NPC {npc_id}")
            if not info.get("ResPath") or not info.get("ClickResPath"):
                errors.append(f"Scene {sid} NPC {npc_id}: art resource name is missing")
            for field in ("TalkInfo", "LoopTalkInfo"):
                entry = info.get(field) or {}
                if not entry.get("id") and not entry.get("videoScene") and not entry.get("pendingTalkKey"):
                    errors.append(f"Scene {sid} NPC {npc_id}: {field} has no explicit or pending entry")

    for chapter in unit4["ChapterConfig"]:
        cid = str(chapter["id"])
        if not chapter.get("pendingInitTalkKey") and not chapter.get("initTalk"):
            errors.append(f"Chapter {cid}: missing init talk and pending key")
        if str(chapter.get("initScene")) not in scene_ids:
            errors.append(f"Chapter {cid}: missing init scene {chapter.get('initScene')}")
        if str(chapter.get("explorationEntryScene")) not in scene_ids:
            errors.append(f"Chapter {cid}: missing exploration entry {chapter.get('explorationEntryScene')}")
        expose_scene = scene_map.get(str(chapter.get("exposeScene"))) or {}
        expected_top_bg = str((expose_scene.get("location") or {}).get("backgroundImage") or "")
        if chapter.get("topBg") != expected_top_bg or str(chapter.get("topBg")) not in art_asset_ids:
            errors.append(f"Chapter {cid}: expose background is not preconfigured")
        for doubt in chapter.get("doubts") or []:
            for condition in doubt.get("condition") or []:
                if str(condition.get("param")) not in material_ids:
                    errors.append(f"Doubt {doubt.get('id')}: missing material {condition.get('param')}")
        for expose in chapter.get("exposes") or []:
            if not expose.get("talkId") and not expose.get("pendingTalkKey"):
                errors.append(f"Expose {expose.get('id')}: missing talk and pending key")
            for material_id in expose.get("item") or []:
                if str(material_id) not in material_ids:
                    errors.append(f"Expose {expose.get('id')}: missing material {material_id}")

    testimony_types = {
        str(condition.get("param")): str(condition.get("type"))
        for chapter in unit4["ChapterConfig"]
        for doubt in chapter.get("doubts") or []
        for condition in doubt.get("condition") or []
        if str(condition.get("param")) in testimony_ids
    }
    for testimony_id, condition_type in testimony_types.items():
        expected = "3" if testimony_id == "4153001" else "4"
        if condition_type != expected:
            errors.append(f"Testimony {testimony_id}: expected condition type {expected}, found {condition_type}")

    for npc in unit4["NPCStaticData"]:
        if not npc.get("IconSmall") or not npc.get("IconLarge"):
            errors.append(f"NPC {npc.get('id')}: icon resource name is missing")

    flow = json.loads(FLOW_PATH.read_text(encoding="utf-8"))["units"].get("Unit4")
    if not flow:
        errors.append("UnitFlow: Unit4 missing")
        return errors
    loops = flow.get("loops") or []
    if [loop.get("id") for loop in loops] != [f"loop{n}" for n in range(1, 6)]:
        errors.append("UnitFlow: Unit4 must contain exactly loop1-loop5")
    if any(loop.get("id") == "loop6" for loop in loops):
        errors.append("UnitFlow: non-loop finale was incorrectly emitted as loop6")
    if loops:
        l5 = loops[-1]
        lock = (l5.get("specialMechanics") or {}).get("identityLock") or {}
        if len(lock.get("chains") or []) != 3 or not lock.get("replacesStandardDoubts"):
            errors.append("UnitFlow L5: three-chain identity lock missing")
        ending = l5.get("endingSequence") or {}
        if ending.get("countsAsLoop") is not False or len(ending.get("scenes") or []) != 3:
            errors.append("UnitFlow L5: non-loop three-scene finale missing")
        stage_types = [stage.get("type") for stage in l5.get("flow") or []]
        for required in ("identityLock", "nonLoopFinale"):
            if required not in stage_types:
                errors.append(f"UnitFlow L5: stage {required} missing")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Unit4 preview validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Unit4 preview validation PASS")
    for name, expected in EXPECTED_COUNTS.items():
        print(f"- {name}: {expected}")
    print("- UnitFlow: loop1-loop5 only; L5 identity lock + non-loop finale present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
