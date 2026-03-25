#!/usr/bin/env python3
"""
Unit3 State → Preview 数据转换脚本

读取 剧情设计/Unit3/state/loop{1-6}_state.yaml
生成 preview_new2/data/Unit3/ 下的 YAML 文件
追加 preview_new2/data/table/ 下的 JSON 条目
"""

import json
import os
import re
import yaml

# ============================================================
# 路径配置
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "剧情设计", "Unit3", "state")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "data", "Unit3")
TABLE_DIR = os.path.join(SCRIPT_DIR, "data", "table")

# ============================================================
# 硬编码数据（state注释中的信息，YAML解析器无法读取）
# ============================================================

# 每个Loop的元信息（从state文件注释提取）
LOOP_META = {
    1: {"title": "不是自杀", "time": "11/21 08:00 早晨"},
    2: {"title": "Mary的嫌疑", "time": "11/21 14:00 下午"},
    3: {"title": "杀妻骗保计划", "time": "11/22 10:00 上午"},
    4: {"title": "门把手上的油", "time": "11/22 16:00 下午"},
    5: {"title": "Bernard的\"标准服务\"", "time": "11/23 10:00 上午"},
    6: {"title": "辩论", "time": "11/23 18:00 傍晚"},
}

# 每个Loop的场景分类（从场景总览提取）
LOOP_SCENES = {
    1: {
        "unlocked": [3001, 3002, 3005],
        "locked": [
            {"id": 3003, "reason": "尚未发现Sullivan家线索"},
            {"id": 3007, "reason": "尚未发现Mary的宗教线索"},
            {"id": 3008, "reason": "尚未发现Helen线索"},
            {"id": 3009, "reason": "银行尚未出现在调查方向中"},
            {"id": 3010, "reason": "尚未发现Margaret线索"},
        ],
    },
    2: {
        "unlocked": [3003, 3012, 3007, 3001, 3002],
        "locked": [
            {"id": 3008, "reason": "尚未发现Helen线索"},
            {"id": 3009, "reason": "银行尚未出现在调查方向中"},
            {"id": 3010, "reason": "尚未发现Margaret线索"},
        ],
    },
    3: {
        "unlocked": [3008, 3002, 3009, 3006, 3001],
        "locked": [
            {"id": 3010, "reason": "尚未发现Margaret线索"},
        ],
    },
    4: {
        "unlocked": [3002, 3008, 3003, 3010],
        "locked": [],
    },
    5: {
        "unlocked": [3014],
        "locked": [],
    },
    6: {
        "unlocked": [3005, 3010, 3003, 3008, 3011],
        "locked": [],
    },
}

# 派生证据（state注释中，YAML解析不到）
DERIVED_EVIDENCE = {
    # L2 派生
    3212: {"name": "织物比对报告", "note": "系统层分析：Thomas袖扣织物(3206)+祈祷披肩(3205)→织物比对", "scene": "小玩法派生", "sources": [3206, 3205]},
    3213: {"name": "口红颜色比对报告", "note": "系统层分析：衬衫口红+Mary口红(3204)→颜色比对", "scene": "小玩法派生", "sources": [3203, 3204]},
    # L3 派生
    3311: {"name": "Foster地面油迹采样报告", "note": "派生中间产物：楼顶地面油迹现场采样→Foster出具采样报告", "scene": "SC3002", "sources": []},
    3312: {"name": "油样本化学比对报告", "note": "系统层分析：轮椅维护油(3301)+地面油迹采样(3311)→化学比对", "scene": "小玩法派生", "sources": [3301, 3311]},
    # L4 派生
    3405: {"name": "油迹二方比对报告", "note": "系统层分析：门把手油迹(3401)+地面油比对报告(3312)→二方比对", "scene": "小玩法派生", "sources": [3401, 3312]},
    # L5 派生
    3502: {"name": "笔迹比对报告", "note": "系统层分析：标注报纸(3501)→笔迹比对，确认批注非Thomas所写", "scene": "小玩法派生", "sources": [3501]},
    3505: {"name": "垫板压痕侧光分析报告", "note": "系统层分析：垫板(3504)+标注报纸(3501)→侧光分析，确认压痕=批注书写痕迹", "scene": "小玩法派生", "sources": [3504, 3501]},
    3506: {"name": "垫板压痕vs报纸批注对比照片", "note": "系统层分析：垫板(3504)压痕与报纸批注叠加对比", "scene": "小玩法派生", "sources": [3504, 3501]},
    3508: {"name": "Mary手链照片", "note": "L2回溯获取：Mary手链(原3207)的特写照片，用于花形压痕比对", "scene": "小玩法派生", "sources": [3207]},
    3509: {"name": "花形压痕比对报告", "note": "系统层分析：垫板花形压痕(3507)+Mary手链照片(3508)→比对，雏菊吊坠完全吻合", "scene": "小玩法派生", "sources": [3507, 3508]},
}

# 指证数据（从state的expose部分完整提取）
EXPOSE_DATA = {
    1: {
        "scene": 3004,
        "target_name": "Morrison（腐败警察）",
        "npc_id": "301",
        "rounds": [
            {"lie": "现场干干净净，只有死者一个人的痕迹", "evidences": [3104]},
            {"lie": "这人明显是自己跳下去的。护栏那么矮，喝多了站不稳，一脚踩空就掉了", "evidences": [3106, 3101]},
        ],
    },
    2: {
        "scene": 3003,
        "target_name": "Mary Sullivan",
        "npc_id": "303",
        "rounds": [
            {"lie": "那晚我在教堂祈祷了很久，读到第23章，蜡烛烧了很久才走", "evidences": [3202, 3201]},
            {"lie": "蜡烛断了、蜡油在第5章——那是我离开之后的事，跟我没关系", "evidences": [3210]},
            {"lie": "我也是最近才听说Thomas和Helen的事……大概一周前吧", "evidences": [3213, 3204]},
            {"lie": "我上去看了一圈，没找到他，就回来了。我那天晚上根本没见到Thomas", "evidences": [3212]},
        ],
    },
    3: {
        "scene": 3008,
        "target_name": "Helen",
        "npc_id": "304",
        "rounds": [
            {"lie": "Thomas只是来找我聊天诉苦。那晚他自己上楼顶喝酒，掉了。跟我没关系", "evidences": [3206, 3303]},
            {"lie": "我只是帮Thomas配了把钥匙。天台我自己从来没上去过。楼顶发生的事跟我没关系", "evidences": [3312, 3308]},
            {"lie": "Thomas说他想在楼顶吓唬Mary，让她害怕不敢再反抗他。油是为了万一……我真的以为只是'吓唬'", "evidences": [3304]},
        ],
    },
    4: {
        "scene": 3008,
        "target_name": "Helen（补充指证）",
        "npc_id": "304",
        "rounds": [
            {"lie": "我把东西都准备好了，但那天晚上我一直待在家里", "evidences": [3405, 3401]},
            {"lie": "Thomas叫我上去检查，我看了一眼就回去了。他自己在那喝酒，自己带的酒", "evidences": [3408, 3217]},
            {"lie": "我给Thomas倒了很多酒。后来Mary到了。Thomas太醉了，站都站不稳，自己滑倒摔下去的。谁都没碰他", "evidences": []},
        ],
    },
    5: {
        "scene": 3014,
        "target_name": "Bernard Wells",
        "npc_id": "305",
        "rounds": [
            {"lie": "Thomas来买了一份标准保单，很正常的业务。我没有做任何不恰当的事", "evidences": [3502, 3304]},
            {"lie": "我只是用报纸上的文章给Thomas解释保单条款，这是正常的客户服务", "evidences": [3505]},
            {"lie": "我的工作就是回答客户的问题。Thomas问了，我回答了。之后没有其他人来找过我", "evidences": [3509]},
        ],
    },
    6: {
        "scene": 3011,
        "target_name": "Mickey Brennan（控辩辩论）",
        "npc_id": "308",
        "rounds": [
            {"lie": "Thomas打了Mary多少年？酗酒者的暴力是肌肉记忆。Margaret亲眼看到他在推Mary。正当防卫", "evidences": [3601]},
            {"lie": "Helen心软了——她涂了油，但最后没推Thomas。地面油是准备阶段的残留", "evidences": [3308, 3309]},
            {"lie": "Mary的45分钟空白是恐惧冻结反应。一个被家暴十年的女人——她是吓呆了", "evidences": [3201]},
            {"lie": "就算有预谋，那也是被家暴者的求生。Mary去银行不是为了钱——是为了确认生存手段", "evidences": [3507, 3509]},
            {"lie": "Mickey主动出示实地勘查记录，质疑Margaret证词的物理可能性", "evidences": [3610]},
        ],
    },
}

# NPC列表
NPCS = [
    {"id": "301", "name_cn": "Morrison", "name_en": "Morrison", "role": "5"},
    {"id": "302", "name_cn": "Emma O'Malley", "name_en": "Emma O'Malley", "role": "3"},
    {"id": "303", "name_cn": "Mary Sullivan", "name_en": "Mary Sullivan", "role": "5"},
    {"id": "304", "name_cn": "Helen", "name_en": "Helen", "role": "5"},
    {"id": "305", "name_cn": "Bernard Wells", "name_en": "Bernard Wells", "role": "5"},
    {"id": "306", "name_cn": "Liam Byrne", "name_en": "Liam Byrne", "role": "5"},
    {"id": "307", "name_cn": "Margaret Brennan", "name_en": "Margaret Brennan", "role": "5"},
    {"id": "308", "name_cn": "Mickey Brennan", "name_en": "Mickey Brennan", "role": "5"},
    {"id": "309", "name_cn": "Foster", "name_en": "Foster", "role": "5"},
    {"id": "310", "name_cn": "Emily Sullivan", "name_en": "Emily Sullivan", "role": "7"},
]

# 场景列表
SCENES = [
    {"id": "3001", "name": "Thomas公寓楼下现场", "name_en": "CrimeScene_Ground"},
    {"id": "3002", "name": "Thomas公寓楼顶", "name_en": "Rooftop"},
    {"id": "3003", "name": "Sullivan家客厅", "name_en": "SullivanHome_LivingRoom"},
    {"id": "3004", "name": "警局", "name_en": "PoliceStation"},
    {"id": "3005", "name": "法医办公室", "name_en": "ForensicOffice"},
    {"id": "3006", "name": "公寓二楼走廊", "name_en": "ApartmentCorridor_2F"},
    {"id": "3007", "name": "St. Patrick教堂", "name_en": "StPatrickChurch"},
    {"id": "3008", "name": "Helen家", "name_en": "HelenHome"},
    {"id": "3009", "name": "Continental银行公共区域", "name_en": "ContinentalBank_Lobby"},
    {"id": "3010", "name": "Margaret鞋坊", "name_en": "MargaretShoeShop"},
    {"id": "3011", "name": "街角", "name_en": "StreetCorner"},
    {"id": "3012", "name": "Sullivan家卧室", "name_en": "SullivanHome_Bedroom"},
    {"id": "3014", "name": "Continental银行Bernard办公室", "name_en": "ContinentalBank_BernardOffice"},
]

SCENE_NAME_MAP = {s["id"]: s["name"] for s in SCENES}
SCENE_EN_MAP = {s["id"]: s["name_en"] for s in SCENES}

# locations.yaml 数据
LOCATIONS = [
    {"name": "Thomas公寓楼", "entry": "01", "children": ["02", "03", "06", "12"]},
    {"name": "警局", "entry": "04", "children": []},
    {"name": "法医办公室", "entry": "05", "children": []},
    {"name": "St. Patrick教堂", "entry": "07", "children": []},
    {"name": "Helen家", "entry": "08", "children": []},
    {"name": "Continental银行", "entry": "09", "children": ["14"]},
    {"name": "Margaret鞋坊", "entry": "10", "children": []},
    {"name": "街角", "entry": "11", "children": []},
]


# ============================================================
# State文件读取
# ============================================================

def preprocess_yaml(raw):
    """预处理state YAML，修复已知语法问题（不修改原文件）"""
    import re
    lines = raw.split('\n')
    result = []
    for line in lines:
        stripped = line.lstrip()
        # 跳过列表内非列表项的 设计说明: （loop3语法问题）
        if stripped.startswith('设计说明:'):
            result.append(re.sub(r'^(\s*)设计说明:', r'\1# 设计说明:', line))
            continue
        # 修复reward字段中嵌套双引号的问题（如 "..."自杀"..." ）
        if stripped.startswith('reward:') and stripped.count('"') > 2:
            indent = line[:len(line) - len(stripped)]
            # 提取key和value，将value改用单引号包裹
            val_start = stripped.index('"') + 1
            val = stripped[len('reward: "'):].rstrip('"')
            val = val.replace("'", "''")  # 转义单引号（YAML单引号字符串规则）
            result.append(f"{indent}reward: '{val}'")
            continue
        result.append(line)
    return '\n'.join(result)


def load_all_states():
    """读取6个state YAML文件"""
    states = {}
    for i in range(1, 7):
        path = os.path.join(STATE_DIR, f"loop{i}_state.yaml")
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        raw = preprocess_yaml(raw)
        states[i] = yaml.safe_load(raw)
    return states


# ============================================================
# YAML生成
# ============================================================

def generate_loop_yaml(loop_num, state_data):
    """生成 data/Unit3/loop{N}.yaml"""
    meta = LOOP_META[loop_num]
    scenes = LOOP_SCENES[loop_num]
    expose = EXPOSE_DATA[loop_num]

    opening_data = state_data.get("opening", {})

    doc = {
        "title": meta["title"],
        "target": state_data.get("player_context", {}).get("goals", {}).get("primary", ""),
        "time": meta["time"],
        "opening": [{
            "id": opening_data.get("scene_id", 0),
            "characters": opening_data.get("characters", []),
            "purpose": opening_data.get("purpose", ""),
            "talk": opening_data.get("talk", ""),
        }],
        "scenes": {
            "unlocked": scenes["unlocked"],
            "locked": scenes["locked"],
            "closed": [],
        },
        "expose": {
            "scene": expose["scene"],
            "target_name": expose["target_name"],
            "rounds": expose["rounds"],
        },
    }

    path = os.path.join(OUTPUT_DIR, f"loop{loop_num}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def generate_locations_yaml():
    """生成 data/Unit3/locations.yaml"""
    # 手写YAML以确保所有数字字符串带引号（js-yaml兼容）
    path = os.path.join(OUTPUT_DIR, "locations.yaml")
    with open(path, "w", encoding="utf-8") as f:
        f.write("locations:\n")
        for loc in LOCATIONS:
            f.write(f"- name: {loc['name']}\n")
            f.write(f"  entry: \"{loc['entry']}\"\n")
            if loc['children']:
                f.write("  children:\n")
                for ch in loc['children']:
                    f.write(f"  - \"{ch}\"\n")
            else:
                f.write("  children: []\n")
    print(f"  [OK] {path}")


def generate_talk_summary(states):
    """生成 data/Unit3/talk_summary.yaml（精简版）"""
    summaries = {}

    for loop_num, state in states.items():
        opening = state.get("opening", {})
        talk_key = opening.get("talk", "")
        purpose = opening.get("purpose", "")
        if talk_key and purpose:
            summaries[talk_key] = f"L{loop_num}开篇：{purpose}"

        # NPC talks from scenes
        for scene in state.get("scenes", []):
            if not isinstance(scene, dict):
                continue
            npcs = scene.get("npcs", {})
            if not isinstance(npcs, dict):
                continue
            for npc_key, npc_data in npcs.items():
                if not isinstance(npc_data, dict):
                    continue
                talk_id = npc_data.get("talk", "")
                motive = npc_data.get("motive", "")
                if talk_id and motive:
                    scene_name = scene.get("name", "")
                    summaries[talk_id] = f"L{loop_num} {scene_name}：{motive[:60]}"

    doc = {**summaries, "scene_talks": {}}
    path = os.path.join(OUTPUT_DIR, "talk_summary.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


# ============================================================
# JSON追加
# ============================================================

def fix_json(text):
    """状态机修复非标准JSON（与index.html fixJson一致）:
    1. 字符串内字面换行符 -> \\n
    2. 未转义反斜杠 -> \\\\
    3. 字符串内裸双引号 -> \\"
    """
    out = []
    in_str = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if not in_str:
            out.append(c)
            if c == '"':
                in_str = True
            i += 1
            continue
        # 以下在字符串内部
        if c == '\\':
            nx = text[i + 1] if i + 1 < n else ''
            if nx in '"\\\/bfnrt':
                out.append(c + nx)
                i += 2
            elif nx == 'u' and i + 5 < n and all(ch in '0123456789abcdefABCDEF' for ch in text[i+2:i+6]):
                out.append(text[i:i+6])
                i += 6
            else:
                out.append('\\\\')
                i += 1
        elif c == '"':
            nx = text[i + 1] if i + 1 < n else ''
            if nx == '' or nx in ',:]}':
                out.append(c)
                in_str = False
                i += 1
            elif nx in ' \t\r\n':
                # 引号后是空白/换行 -> 向前看跳过空白
                j = i + 1
                while j < n and text[j] in ' \t\r\n':
                    j += 1
                after = text[j] if j < n else ''
                if after == '' or after in ',:]}':
                    out.append(c)
                    in_str = False
                    i += 1
                else:
                    out.append('\\"')
                    i += 1
            else:
                out.append('\\"')
                i += 1
        elif c == '\n':
            out.append('\\n')
            i += 1
        elif c == '\r':
            i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def load_json(filename):
    path = os.path.join(TABLE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    return json.loads(fix_json(raw))


def save_json(filename, data):
    path = os.path.join(TABLE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] {path}")


def has_epi03(data, chapter_field="Chapter"):
    """检查JSON数组中是否已有EPI03条目"""
    return any(item.get(chapter_field) == "EPI03" for item in data)


def append_scenes_to_json():
    """追加SceneConfig.json"""
    data = load_json("SceneConfig.json")
    if any(item.get("Chapter") == "EPI03" for item in data):
        print("  [SKIP] SceneConfig.json 已有EPI03场景，跳过")
        return

    for scene in SCENES:
        data.append({
            "sceneId": scene["id"],
            "sceneName": scene["name"],
            "sceneNameEn": scene["name_en"],
            "sceneType": "1",
            "backgroundImage": "",
            "backgroundMusic": "test",
            "Chapter": "EPI03",
        })
    save_json("SceneConfig.json", data)


def append_items_to_json(states):
    """追加ItemStaticData.json"""
    data = load_json("ItemStaticData.json")
    if has_epi03(data):
        print("  [SKIP] ItemStaticData.json 已有EPI03条目，跳过")
        return

    existing_ids = set()
    items_to_add = []

    # 从state的scenes.evidence中提取
    for loop_num, state in states.items():
        for scene in state.get("scenes", []):
            if not isinstance(scene, dict):
                continue
            scene_id = str(scene.get("id", ""))
            scene_name = scene.get("name", "")
            for ev in scene.get("evidence", []):
                if not isinstance(ev, dict):
                    continue
                eid = str(ev.get("id", ""))
                if eid in existing_ids:
                    continue
                existing_ids.add(eid)
                items_to_add.append({
                    "id": eid,
                    "Name": [ev.get("name", ""), f"Evidence_{eid}"],
                    "itemType": "2",
                    "canAnalyzed": "false",
                    "canCombined": "false",
                    "Describe": [ev.get("note", "")],
                    "ShortDescribe": [ev.get("name", "")],
                    "location": [scene_name, SCENE_EN_MAP.get(scene_id, "")],
                    "Chapter": "EPI03",
                    "folderPath": "",
                    "desSpritePath": "",
                    "mapSpritePath": "",
                    "Position": ["0", "0"],
                    "ArtRequirement": "",
                })

    # 追加派生证据
    for eid, info in DERIVED_EVIDENCE.items():
        eid_str = str(eid)
        if eid_str in existing_ids:
            continue
        existing_ids.add(eid_str)
        scene_label = info.get("scene", "小玩法派生")
        items_to_add.append({
            "id": eid_str,
            "Name": [info["name"], f"Evidence_{eid_str}"],
            "itemType": "2",
            "canAnalyzed": "false",
            "canCombined": "false",
            "Describe": [info["note"]],
            "ShortDescribe": [info["name"]],
            "location": [scene_label, ""],
            "Chapter": "EPI03",
            "folderPath": "",
            "desSpritePath": "",
            "mapSpritePath": "",
            "Position": ["0", "0"],
            "ArtRequirement": "",
        })

    # 设置 canAnalyzed（如果该物证是某个派生的源）
    source_to_product = {}
    for pid, info in DERIVED_EVIDENCE.items():
        for src in info.get("sources", []):
            source_to_product[str(src)] = str(pid)

    for item in items_to_add:
        if item["id"] in source_to_product:
            item["canAnalyzed"] = "true"
            item["analysedEvidence"] = source_to_product[item["id"]]

    # 排序
    items_to_add.sort(key=lambda x: int(x["id"]))
    data.extend(items_to_add)
    save_json("ItemStaticData.json", data)
    print(f"    -> 添加了 {len(items_to_add)} 个证据条目")


def append_npcs_to_json():
    """追加NPCStaticData.json"""
    data = load_json("NPCStaticData.json")
    if has_epi03(data):
        print("  [SKIP] NPCStaticData.json 已有EPI03条目，跳过")
        return

    for npc in NPCS:
        data.append({
            "id": npc["id"],
            "Name": [npc["name_cn"], npc["name_en"]],
            "role": npc["role"],
            "Chapter": "EPI03",
        })
    save_json("NPCStaticData.json", data)


def append_doubts_to_json(states):
    """追加DoubtConfig.json"""
    data = load_json("DoubtConfig.json")
    if any(item.get("Chapter") == "EPI03" for item in data):
        print("  [SKIP] DoubtConfig.json 已有EPI03条目，跳过")
        return

    for loop_num, state in states.items():
        for doubt in state.get("doubts", []):
            if not isinstance(doubt, dict):
                continue
            did = str(doubt.get("id", ""))
            text = doubt.get("text", "")
            condition_str = doubt.get("unlock_condition", "")

            # 解析 "item:3104 + testimony:3101001" → JSON条件数组
            conditions = []
            if condition_str:
                parts = [p.strip() for p in condition_str.split("+")]
                for part in parts:
                    part = part.strip()
                    if part.startswith("item:"):
                        conditions.append({"type": "1", "param": part.replace("item:", "").strip()})
                    elif part.startswith("testimony:"):
                        conditions.append({"type": "3", "param": part.replace("testimony:", "").strip()})

            data.append({
                "id": did,
                "condition": conditions,
                "text": text,
                "Chapter": "EPI03",
            })

    save_json("DoubtConfig.json", data)


def append_chapter_config(states):
    """追加ChapterConfig.json"""
    data = load_json("ChapterConfig.json")
    if any(str(item.get("id", "")).startswith("3") for item in data):
        print("  [SKIP] ChapterConfig.json 已有EPI03条目，跳过")
        return

    for loop_num in range(1, 7):
        state = states[loop_num]
        expose = EXPOSE_DATA[loop_num]

        # 收集该loop的疑点
        doubts = []
        for doubt in state.get("doubts", []):
            if not isinstance(doubt, dict):
                continue
            did = str(doubt.get("id", ""))
            text = doubt.get("text", "")
            condition_str = doubt.get("unlock_condition", "")
            conditions = []
            if condition_str:
                parts = [p.strip() for p in condition_str.split("+")]
                for part in parts:
                    part = part.strip()
                    if part.startswith("item:"):
                        conditions.append({"type": "1", "param": part.replace("item:", "").strip()})
                    elif part.startswith("testimony:"):
                        conditions.append({"type": "3", "param": part.replace("testimony:", "").strip()})
            doubts.append({"id": did, "condition": conditions, "text": text})

        # 构建exposes数组
        exposes = []
        for i, rnd in enumerate(expose["rounds"]):
            exposes.append({
                "id": str(i + 1),
                "testimony": "",
                "item": [str(e) for e in rnd.get("evidences", [])],
                "talkId": "",
            })

        config_id = str(300 + loop_num)
        data.append({
            "id": config_id,
            "initTalk": "",
            "initScene": str(expose["scene"]),
            "doubts": doubts,
            "exposeNpcId": expose["npc_id"],
            "exposes": exposes,
        })

    save_json("ChapterConfig.json", data)


# ============================================================
# 主流程
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("Unit3 State -> Preview 数据转换")
    print("=" * 50)

    print("\n[1/3] 读取State文件...")
    states = load_all_states()
    print(f"  [OK] 已读取 {len(states)} 个state文件")

    print("\n[2/3] 生成Preview YAML文件...")
    for i in range(1, 7):
        generate_loop_yaml(i, states[i])
    generate_locations_yaml()
    generate_talk_summary(states)

    print("\n[3/3] 追加JSON数据表...")
    append_scenes_to_json()
    append_items_to_json(states)
    append_npcs_to_json()
    append_doubts_to_json(states)
    append_chapter_config(states)

    print("\n" + "=" * 50)
    print("转换完成！")
    print(f"YAML输出: {OUTPUT_DIR}")
    print(f"JSON更新: {TABLE_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
