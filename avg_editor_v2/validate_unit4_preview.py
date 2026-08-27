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
AVG_ROOT = HERE.parent / "AVG" / "EPI04"

EXPECTED_COUNTS = {
    "ChapterConfig": 5,
    "SceneConfig": 28,
    "ItemStaticData": 59,
    "NPCStaticData": 19,
    "NPCLoopData": 15,
    "TestimonyItem": 19,
    "DoubtConfig": 12,
    "ArtAssetConfig": 29,
}


def load(name: str) -> list[dict]:
    return json.loads((TABLE_DIR / f"{name}.json").read_text(encoding="utf-8"))


def is_unit4(name: str, row: dict) -> bool:
    if row.get("Chapter") == "EPI04":
        return True
    key = row.get("sceneId") if name == "SceneConfig" else row.get("id")
    return str(key or "").startswith("4")


def scene_open_in_loop(scene: dict, loop: int) -> bool:
    explicit_loops = scene.get("openInLoops")
    if isinstance(explicit_loops, list):
        normalized = {int(value) for value in explicit_loops if str(value).isdigit()}
        if normalized:
            return loop in normalized
    return int(scene.get("loop") or 0) == loop


def nonempty_pending_keys(value) -> list[str]:
    pending: list[str] = []
    if isinstance(value, list):
        for item in value:
            pending.extend(nonempty_pending_keys(item))
    elif isinstance(value, dict):
        key = value.get("pendingTalkKey") or value.get("pendingInitTalkKey")
        if key:
            pending.append(str(key))
        for nested in value.values():
            pending.extend(nonempty_pending_keys(nested))
    return pending


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

    talk_files = sorted((AVG_ROOT / "Talk").glob("loop*/*.json")) if AVG_ROOT.exists() else []
    talk_files = [path for path in talk_files if path.name != "_manifest.json"]
    expose_files = sorted((AVG_ROOT / "Expose").glob("*.json")) if AVG_ROOT.exists() else []
    expose_files = [path for path in expose_files if path.name != "_manifest.json"]
    if len(talk_files) != 48 or len(expose_files) != 5:
        errors.append(f"EPI04 AVG: expected 48 Talk and 5 Expose files, found {len(talk_files)} and {len(expose_files)}")
    avg_rows = []
    ids_by_scene: dict[str, set[str]] = {}
    for path in talk_files + expose_files:
        rows = json.loads(path.read_text(encoding="utf-8"))
        avg_rows.extend(rows)
        ids_by_scene[path.stem] = {str(row.get("id") or "") for row in rows}
    avg_ids = [str(row.get("id") or "") for row in avg_rows]
    duplicate_avg_ids = sorted({talk_id for talk_id in avg_ids if talk_id and avg_ids.count(talk_id) > 1})
    if duplicate_avg_ids:
        errors.append(f"EPI04 AVG: duplicate Talk IDs {duplicate_avg_ids[:10]}")
    avg_id_set = set(avg_ids)
    for row in avg_rows:
        talk_id = str(row.get("id") or "")
        next_id = str(row.get("next") or "")
        if next_id and next_id not in avg_id_set:
            errors.append(f"EPI04 AVG {talk_id}: missing next target {next_id}")
        if row.get("script") in {"branches", "1"}:
            for parameter in row.get("Parameters") or []:
                target = str(parameter.get("ParameterInt") or "")
                if target and target not in avg_id_set:
                    errors.append(f"EPI04 AVG {talk_id}: missing branch target {target}")
        if row.get("script") == "Lie" and str(row.get("ParameterInt0") or "") not in avg_id_set:
            errors.append(f"EPI04 AVG {talk_id}: missing Lie success target")

    pending = nonempty_pending_keys(unit4["SceneConfig"]) + nonempty_pending_keys(unit4["ChapterConfig"])
    pending += nonempty_pending_keys(unit4["NPCLoopData"])
    if pending:
        errors.append(f"Unit4 AVG: unresolved pending Talk keys {sorted(set(pending))}")

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

    for item_id in ("4118", "4212", "4214", "4703"):
        if "SHC-28-B17" not in str((item_map.get(item_id) or {}).get("ArtRequirement") or ""):
            errors.append(f"Item {item_id}: Sacred Heart batch code SHC-28-B17 is missing")

    item_4213_requirement = str((item_map.get("4213") or {}).get("ArtRequirement") or "")
    if (
        "不得把它们画成与 4118、4212 共享 SHC-28-B17 生产批号" not in item_4213_requirement
        or "不在瓶签上写“同配方”“同批次”" not in item_4213_requirement
    ):
        errors.append("Item 4213: must explicitly avoid presenting the old samples as SHC-28-B17 / same production batch")

    for item_id in ("4217", "4218", "4219"):
        if item_id not in item_map:
            errors.append(f"Item {item_id}: approved Loop2 evidence is missing")

    art_asset_ids = {str(row["id"]) for row in unit4["ArtAssetConfig"]}
    scene_map = {str(scene["sceneId"]): scene for scene in unit4["SceneConfig"]}
    expected_canonical_scenes_by_loop = {
        1: {"4001", "4002", "4003"},
        2: {"4011", "4012", "4013", "4014", "4015", "4016"},
        3: {"4021", "4022", "4023", "4024", "4025", "4026", "4027", "4028", "4029"},
        4: {"4031", "4032", "4033", "4034", "4035"},
        5: {"4041", "4042", "4043", "4044", "4045"},
    }
    for loop, expected_scene_ids in expected_canonical_scenes_by_loop.items():
        actual_scene_ids = {
            str(scene["sceneId"])
            for scene in unit4["SceneConfig"]
            if int(scene.get("loop") or 0) == loop
        }
        if actual_scene_ids != expected_scene_ids:
            errors.append(
                f"Loop {loop}: expected scenes {sorted(expected_scene_ids)}, found {sorted(actual_scene_ids)}"
            )

    expected_open_scene_ids_by_loop = {
        1: {"4002", "4003"},
        2: {"4011", "4012", "4013", "4014", "4015"},
        3: {"4022", "4023", "4024", "4025", "4026", "4027", "4028"},
        4: {"4032", "4033", "4034"},
        5: {"4042"},
    }
    for loop, expected_scene_ids in expected_open_scene_ids_by_loop.items():
        actual_scene_ids = {
            str(scene["sceneId"])
            for scene in unit4["SceneConfig"]
            if scene.get("isOpen") is not False and scene_open_in_loop(scene, loop)
        }
        if actual_scene_ids != expected_scene_ids:
            errors.append(
                f"Loop {loop}: expected open scenes {sorted(expected_scene_ids)}, found {sorted(actual_scene_ids)}"
            )

    l5_chapter = next((chapter for chapter in unit4["ChapterConfig"] if str(chapter.get("id")) == "405"), {})
    l5_opening = (l5_chapter.get("openingSequence") or [{}])[0]
    if (
        not str(l5_chapter.get("initTalk") or "")
        or l5_chapter.get("pendingInitTalkKey")
        or str(l5_chapter.get("initScene")) != "4034"
        or str(l5_chapter.get("openingScene")) != "4034"
        or l5_opening.get("talkId") != l5_chapter.get("initTalk")
        or l5_opening.get("videoScene") != "L5_opening_unanswered_calls"
        or l5_opening.get("draftSourceTalk")
        or l5_opening.get("embeddedVisualSceneIds") != ["4041"]
    ):
        errors.append("Loop 5: ChapterConfig must use the 4034 unanswered-calls opening")
    scene_4034 = scene_map.get("4034") or {}
    if scene_4034.get("openInLoops") != [4]:
        errors.append("Scene 4034: must remain a Loop4 exploration scene only")
    scene_4041 = scene_map.get("4041") or {}
    embedded_opening = scene_4041.get("embeddedInOpening") or {}
    if (
        scene_4041.get("isOpeningScene") is not False
        or embedded_opening.get("hostSceneId") != "4034"
        or embedded_opening.get("hostTalkKey") != "L5_opening_unanswered_calls"
    ):
        errors.append("Scene 4041: must remain an embedded visual of the 4034 opening")

    clerk = next((npc for npc in unit4["NPCLoopData"] if str(npc.get("id")) == "4172"), {})
    clerk_branch = ((clerk.get("TalkInfo") or {}).get("branchEvents") or [{}])[0]
    if (
        clerk_branch.get("id") != "records_clerk_submit_seven_numbers"
        or clerk_branch.get("branchPath") != "clerk_submit_permit"
        or clerk_branch.get("grantsItemIds") != ["4219"]
    ):
        errors.append("Records clerk: seven-number submission must remain an NPC branch")

    survivors = [npc for npc in unit4["NPCLoopData"] if str(npc.get("id")) in {"4033", "40631"}]
    if len(survivors) != 2 or any(
        not (npc.get("TalkInfo") or {}).get("id")
        or (npc.get("TalkInfo") or {}).get("videoScene") != "L3_scene4023_survivors"
        or (npc.get("TalkInfo") or {}).get("sharedTalkGroup") != "l3_survivors_debrief"
        or (npc.get("LoopTalkInfo") or {}).get("repeatPolicy") != "disabled_after_shared_first_click"
        for npc in survivors
    ):
        errors.append("Scene 4023: Mickey and Doris must use one once-per-loop shared dialogue")
    scene_4023 = scene_map.get("4023") or {}
    exterior_event = next(
        (event for event in scene_4023.get("previewEvents") or [] if event.get("id") == "mansion_exterior_escape"),
        {},
    )
    if exterior_event.get("previousTalkKey") != "L3_event_mansion_evacuation":
        errors.append("Scene 4023: exterior escape must chain from the evacuation event")

    expected_art_split = {"explore": 18, "dialogue": 11}
    for kind, expected in expected_art_split.items():
        actual = sum(1 for row in unit4["ArtAssetConfig"] if row.get("sceneKind") == kind)
        if actual != expected:
            errors.append(f"ArtAssetConfig: expected {expected} {kind} rows, found {actual}")

    required_scene_assets = {
        "4012": "u4_exp_hospital_social_service_day",
        "4016": "u4_avg_pretrial_courtroom_afternoon",
        "4043": "u4_l5_end_building_stairs_pickup_night",
        "4044": "u4_l5_end_moving_archive_van_review",
    }
    for scene_id, resource_name in required_scene_assets.items():
        scene = scene_map.get(scene_id) or {}
        resources = [
            str(path).split("\\")[-1]
            for path in scene.get("previewBackgroundImages")
            or [(scene.get("location") or {}).get("backgroundImage") or ""]
        ]
        if resource_name not in resources:
            errors.append(f"Scene {scene_id}: expected art resource {resource_name}, found {resources}")

    forbidden_resource_tokens = ("u4_exp_miller_ward_day", "u4_l5_end_safehouse_archive_0420", "u4_l5_end_stairs_pickup_night")
    if any(token in asset_id for asset_id in art_asset_ids for token in forbidden_resource_tokens):
        errors.append("ArtAssetConfig: obsolete Unit4 ward/safehouse/stairs resource remains")

    art_asset_map = {str(row["id"]): row for row in unit4["ArtAssetConfig"]}
    required_action_layers = {
        "Art\\Scene\\Backgrounds\\EPI04\\u4_exp_harrison_outer_office_day": "u4_avg_harrison_outer_office_post_expose",
        "Art\\Scene\\Backgrounds\\EPI04\\u4_exp_morrison_aftermath_night": "u4_avg_morrison_door_post_expose",
        "Art\\Scene\\Backgrounds\\EPI04\\u4_exp_mickey_office_night": "u4_l5_climax_mickey_fall_night",
    }
    for asset_id, action_asset_name in required_action_layers.items():
        action_names = {
            str(action.get("assetName") or "")
            for action in (art_asset_map.get(asset_id) or {}).get("characterActionRequirements") or []
        }
        if action_asset_name not in action_names:
            errors.append(f"ArtAsset {asset_id}: missing same-scene AVG action layer {action_asset_name}")
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
                disabled_shared_repeat = (
                    field == "LoopTalkInfo"
                    and entry.get("repeatPolicy") == "disabled_after_shared_first_click"
                    and entry.get("sharedTalkGroup")
                )
                if (
                    not disabled_shared_repeat
                    and not entry.get("id")
                    and not entry.get("videoScene")
                    and not entry.get("pendingTalkKey")
                ):
                    errors.append(f"Scene {sid} NPC {npc_id}: {field} has no explicit or pending entry")
                talk_id = str(entry.get("id") or "")
                video_scene = str(entry.get("videoScene") or "")
                if talk_id and video_scene and talk_id not in ids_by_scene.get(video_scene, set()):
                    errors.append(
                        f"Scene {sid} NPC {npc_id}: {field} Talk {talk_id} is not in {video_scene}.json"
                    )

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
            expose_talk_id = str(expose.get("talkId") or "")
            expose_scene = str(expose.get("videoScene") or "")
            if expose_talk_id and expose_scene and expose_talk_id not in ids_by_scene.get(expose_scene, set()):
                errors.append(
                    f"Chapter {cid} expose {expose.get('id')}: Talk {expose_talk_id} is not in {expose_scene}.json"
                )

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
    for npc_id in ("417", "418", "419"):
        if npc_id not in npc_ids:
            errors.append(f"NPC {npc_id}: approved Unit4 art profile is missing")
    npc_map = {str(npc["id"]): npc for npc in unit4["NPCStaticData"]}
    for npc_id in ("417", "418", "419"):
        requirement = str((npc_map.get(npc_id) or {}).get("ArtRequirement") or "")
        if not requirement.startswith("【Unit4 人物美术需求】") or "人物事实与美术边界见" in requirement:
            errors.append(f"NPC {npc_id}: detailed art requirements were not imported")

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
