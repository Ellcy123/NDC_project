"""
更新 preview_new2 的 NPCLoopData.json 和 SceneConfig.json，
将 EPI02 NPC 条目的 TalkInfo.id / LoopTalkInfo.id 改为新对话 JSON 的实际首条 ID。
"""

import json
import os

PREVIEW_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'preview_new2', 'data', 'table')

# ============================================================
# 映射表：NPC 条目 ID → (新 TalkInfo.id, 新 LoopTalkInfo.id)
# ============================================================
NPC_ID_MAP = {
    # L1
    "2009": ("204001001", "204002001"),   # Emma → emma_foster / emma_foster_repeat
    # L2
    "2001": ("206001001", "206002001"),   # O'Hara → ohara_001 / ohara_001_repeat
    "2002": ("207001001", "207002001"),   # Tony → tony_001 / tony_001_repeat
    "2003": ("208001001", "208002001"),   # Moore → moore_001 / moore_001_repeat
    "2012": ("209001001", "209002001"),   # Leonard → leonard_001 / leonard_001_repeat (default L2)
    # L2 补充
    # vinnie_001 (207003001) 没有 NPC 配置条目
    # L3
    "2011": ("208002001", "208003001"),   # Moore → moore_002 / moore_002_repeat
    "2004": ("212001001", "212002001"),   # Danny → danny_001 / danny_001_repeat
    # 2010 O'Hara L3 — 新对话中已移除，不更新
    # L4
    "2006": ("201004001", "201005001"),   # Rose → rose_001 / rose_001_repeat
    "2013": ("206002001", "206003001"),   # O'Hara → ohara_002 / ohara_002_repeat
    "2014": ("209004001", "209005001"),   # Leonard → leonard_003 / leonard_003_repeat
    # L5
    "2008": ("201003001", "201004001"),   # Rose → rose_002 / rose_002_repeat
    "2007": ("207007001", "207008001"),   # Vinnie → vinnie_002 / vinnie_002_repeat
    # 2015 Danny L5 — 新对话中已移除，不更新
    # L6
    "2016": ("205002001", "205003001"),   # Morrison → morrison_002 / morrison_002_repeat
    "2020": ("209007001", "209008001"),   # Leonard → leonard_004 / leonard_004_repeat
    # 2005 Mickey, 2017 Tony L6, 2018 Moore L6, 2019 Danny L6 — 无对应新对话
}

# ============================================================
# SceneConfig 特殊覆盖：同一 NPC 条目在不同场景/Loop 需要不同 ID
# 格式：(sceneId, npcEntryId) → (TalkInfo.id, LoopTalkInfo.id)
# ============================================================
SCENE_OVERRIDES = {
    # #2012 Leonard 在 L2(scene 2209) 用 leonard_001，在 L3(scene 2309) 用 leonard_002
    ("2309", "2012"): ("209002001", "209003001"),  # leonard_002 / leonard_002_repeat
}


def update_npc_loop_data():
    """更新 NPCLoopData.json 中 EPI02 条目的 Talk ID"""
    filepath = os.path.join(PREVIEW_DIR, 'NPCLoopData.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    skipped = []
    for entry in data:
        eid = entry.get('id')
        if eid in NPC_ID_MAP:
            new_talk, new_loop_talk = NPC_ID_MAP[eid]
            old_talk = entry.get('TalkInfo', {}).get('id', '?')
            old_loop = entry.get('LoopTalkInfo', {}).get('id', '?')
            entry['TalkInfo']['id'] = new_talk
            entry['LoopTalkInfo']['id'] = new_loop_talk
            npc_name = entry.get('NPC', {}).get('Name', ['?'])[0]
            print(f"  #{eid} {npc_name}: Talk {old_talk} → {new_talk}, LoopTalk {old_loop} → {new_loop_talk}")
            updated += 1
        elif eid and eid.startswith('2') and len(eid) == 4:
            npc_name = entry.get('NPC', {}).get('Name', ['?'])[0]
            skipped.append(f"#{eid} {npc_name}")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent='\t')

    print(f"\nNPCLoopData: 更新 {updated} 条")
    if skipped:
        print(f"  跳过（无对应新对话）: {', '.join(skipped)}")


def update_scene_config():
    """更新 SceneConfig.json 中 EPI02 场景 NPC 条目的 Talk ID"""
    filepath = os.path.join(PREVIEW_DIR, 'SceneConfig.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for scene in data:
        scene_id = scene.get('sceneId', '')
        if not scene_id.startswith('2'):
            continue
        npc_infos = scene.get('NPCInfos', [])
        for npc in npc_infos:
            eid = npc.get('id')
            # 先检查场景级覆盖
            override_key = (scene_id, eid)
            if override_key in SCENE_OVERRIDES:
                new_talk, new_loop_talk = SCENE_OVERRIDES[override_key]
            elif eid in NPC_ID_MAP:
                new_talk, new_loop_talk = NPC_ID_MAP[eid]
            else:
                continue

            old_talk = npc.get('TalkInfo', {}).get('id', '?')
            old_loop = npc.get('LoopTalkInfo', {}).get('id', '?')
            npc['TalkInfo']['id'] = new_talk
            npc['LoopTalkInfo']['id'] = new_loop_talk
            npc_name = npc.get('NPC', {}).get('Name', ['?'])[0]
            print(f"  Scene {scene_id} #{eid} {npc_name}: Talk {old_talk} → {new_talk}, LoopTalk {old_loop} → {new_loop_talk}")
            updated += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent='\t')

    print(f"\nSceneConfig: 更新 {updated} 条")


if __name__ == '__main__':
    print("=== 更新 NPCLoopData.json ===")
    update_npc_loop_data()
    print()
    print("=== 更新 SceneConfig.json ===")
    update_scene_config()
    print()
    print("完成！")
