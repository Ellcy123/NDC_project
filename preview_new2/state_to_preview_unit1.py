#!/usr/bin/env python3
"""
Unit1 State → Preview 数据转换脚本（0417 规范化版）

读取 剧情设计/Unit8/state/loop{1-6}_state.yaml
生成 preview_new2/data/Unit1/ 下的 YAML 文件
追加 preview_new2/data/table/ 下的 JSON 条目（Chapter="EPI01"）

与 Unit3 版本的关键差异：
1. 场景 ID 已规范化为 4 位整数 1001-1014（不做 loop 转换，直接作为 SceneConfig.sceneId）
2. ItemType 从 state.type 动态读取（item→3 / clue→1 / envir→2）
3. Doubt unlock_condition 解析简写 "item:xxxx + testimony:xxxxxxx + relation:xxx"
4. ART_CONFIG 全部留空（美术后补）
5. 处理自造字段（turn_cutscene / suspect_suicide_sequence / post_expose_dialogue /
   post_expose_scene / post_expose_romance / arrest_cutscene / ending_sequence /
   phone_call_event），作为 special_cutscenes 单独记录到 loop{N}.yaml
6. 无派生证据（DERIVED_EVIDENCE 留空）
"""

import glob
import json
import os
import re
import yaml

# ============================================================
# 路径配置
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "剧情设计", "Unit8", "state")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "data", "Unit1")
TABLE_DIR = os.path.join(SCRIPT_DIR, "data", "table")

# AVG 对话源目录
AVG_DIR = os.path.join(PROJECT_ROOT, "AVG", "EPI01")
AVG_TALK_DIR = os.path.join(AVG_DIR, "Talk")
AVG_EXPOSE_DIR = os.path.join(AVG_DIR, "Expose")

CHAPTER = "EPI01"

# ============================================================
# 硬编码元数据
# ============================================================

# 每个 Loop 的元信息（0417 重构版）
LOOP_META = {
    1: {"title": "枪响开场", "time": "1928-11 某夜 23:30"},
    2: {"title": "酒吧的秘密", "time": "当晚"},
    3: {"title": "虚假的目击", "time": "当晚"},
    4: {"title": "破碎的金丝雀", "time": "当晚"},
    5: {"title": "厨师的代价", "time": "凌晨"},
    6: {"title": "正义的重量", "time": "次日"},
}

# Unit1 物理场景 ID → 中英文名（14 个物理场景）
SCENES = [
    {"id": "1001", "name": "二楼会客室", "name_en": "MeetingRoom_2F"},
    {"id": "1002", "name": "Vivian 工作室", "name_en": "VivianStudio"},
    {"id": "1003", "name": "厨房", "name_en": "Kitchen"},
    {"id": "1004", "name": "Webb 办公室", "name_en": "WebbOffice"},
    {"id": "1005", "name": "Tommy 办公室", "name_en": "TommyOffice"},
    {"id": "1006", "name": "歌舞厅", "name_en": "Ballroom"},
    {"id": "1007", "name": "酒吧大厅", "name_en": "BarLobby"},
    {"id": "1008", "name": "清洁间", "name_en": "JanitorRoom"},
    {"id": "1009", "name": "一楼走廊", "name_en": "Corridor_1F"},
    {"id": "1010", "name": "Vivian 化妆间", "name_en": "VivianDressingRoom"},
    {"id": "1011", "name": "蓝月亮酒吧后门", "name_en": "BarBackDoor"},
    {"id": "1012", "name": "Jimmy 家", "name_en": "JimmyHome"},
    {"id": "1013", "name": "Morrison 家", "name_en": "MorrisonHome"},
    {"id": "1014", "name": "警局 Morrison 办公室", "name_en": "PoliceStation_MorrisonOffice"},
]

SCENE_NAME_MAP = {s["id"]: s["name"] for s in SCENES}
SCENE_EN_MAP = {s["id"]: s["name_en"] for s in SCENES}

# 每个 Loop 的场景分类
# unlocked = state 里 scenes.[*].id 出现的物理 ID（加上自造段的触发场景）
# locked / closed 由"14 全集减去 unlocked"自动计算（reason 留空，后补）
LOOP_SCENE_CONFIG = {
    1: {"unlocked": [1001]},
    2: {"unlocked": [1002, 1003, 1004, 1005, 1006]},
    3: {"unlocked": [1003, 1007, 1001, 1008]},
    4: {"unlocked": [1009, 1005, 1010, 1006, 1007]},
    5: {"unlocked": [1005, 1003, 1012, 1011]},  # 1011 来自 arrest_cutscene/suspect_suicide_sequence
    6: {"unlocked": [1013, 1014, 1001]},        # 1001 来自 ending_sequence 保险箱场景
}

# 派生证据（Unit1 当前无派生）
DERIVED_EVIDENCE = {}

# 证据类型数字映射（state.type → itemType 数字字符串）
TYPE_TO_ITEMTYPE = {
    "clue": "1",
    "envir": "2",
    "environment": "2",
    "item": "3",
    "note": "4",  # 已废弃，保留映射以防万一
}
ITEM_TYPE_NAME_MAP = {"1": "clue", "2": "environment", "3": "item", "4": "note"}

# ART 配置全部留空（后补）
ART_CONFIG = {}
NPC_ART_CONFIG = {}
SCENE_ART_CONFIG = {}

# NPC 列表（以 data/table/NPCStaticData.json 已存在的 EPI01 映射为准）
NPCS = [
    {"id": "101", "name_cn": "扎克·布伦南", "name_en": "Zack Brennan", "role": "4"},
    {"id": "102", "name_cn": "艾玛·奥马利", "name_en": "Emma O'Malley", "role": "3"},
    {"id": "103", "name_cn": "罗莎·马丁内斯", "name_en": "Rosa Martinez", "role": "5"},
    {"id": "104", "name_cn": "莫里森", "name_en": "Morrison", "role": "5"},
    {"id": "105", "name_cn": "汤米", "name_en": "Tommy", "role": "5"},
    {"id": "106", "name_cn": "薇薇安·罗斯", "name_en": "Vivian Rose", "role": "5"},
    {"id": "107", "name_cn": "吉米", "name_en": "Jimmy", "role": "5"},
    {"id": "108", "name_cn": "安娜", "name_en": "Anna", "role": "5"},
    {"id": "109", "name_cn": "韦布", "name_en": "Webb", "role": "1"},
    {"id": "110", "name_cn": "莫里森太太", "name_en": "Mrs. Morrison", "role": "5"},
    {"id": "111", "name_cn": "鲸鱼", "name_en": "Whale", "role": "5"},
]
NPC_ID_MAP = {npc["id"]: npc for npc in NPCS}

# talk_key 前缀 → NPC id
NPC_KEY_TO_ID = {
    "zack": "101",
    "emma": "102",
    "rosa": "103",
    "morrison": "104",
    "tommy": "105",
    "vivian": "106",
    "jimmy": "107",
    "anna": "108",
    "webb": "109",
    "whale": "111",
}

# NPC 图标配置（命名规则: firstname_small / firstname_big）
NPC_ICON_CONFIG = {int(k): (f"{name}_small", f"{name}_big") for k, name in {
    "101": "zack", "102": "emma", "103": "rosa", "104": "morrison",
    "105": "tommy", "106": "vivian", "107": "jimmy", "108": "anna",
    "109": "webb", "110": "mrsmorrison", "111": "whale",
}.items()}

# 场景背景图路径（Art\Scene\Backgrounds\EPI01\SC{id}_bg_{EnName}）
SCENE_BG_CONFIG = {s["id"]: f"Art\\Scene\\Backgrounds\\EPI01\\SC{s['id']}_bg_{s['name_en']}" for s in SCENES}

# locations.yaml 数据（按"酒吧"主楼 + Morrison 家 + Jimmy 家 + 警局组织）
LOCATIONS = [
    {"name": "蓝月亮酒吧", "entry": "07", "children": ["01", "02", "03", "04", "05", "06", "08", "09", "10", "11"]},
    {"name": "Jimmy 家", "entry": "12", "children": []},
    {"name": "Morrison 家", "entry": "13", "children": []},
    {"name": "警局", "entry": "14", "children": []},
]

# 自造字段（在 loop.yaml 里独立记录）
SPECIAL_SECTIONS = [
    "turn_cutscene",
    "suspect_suicide_sequence",
    "arrest_cutscene",
    "post_expose_dialogue",
    "post_expose_romance",
    "post_expose_scene",
    "ending_sequence",
    "phone_call_event",
]


# ============================================================
# State 文件读取
# ============================================================

def preprocess_yaml(raw):
    """预处理 state YAML（Unit1 目前无已知 YAML 语法问题，保留接口备用）"""
    lines = raw.split('\n')
    result = []
    for line in lines:
        stripped = line.lstrip()
        # 兼容 Unit3 已知问题：列表外的"设计说明:"
        if stripped.startswith('设计说明:') and not stripped.startswith('- 设计说明:'):
            # 仅注释该行以避免 YAML 识别为 key
            result.append(re.sub(r'^(\s*)设计说明:', r'\1# 设计说明:', line))
            continue
        result.append(line)
    return '\n'.join(result)


def load_all_states():
    """读取 6 个 Unit1 state YAML 文件"""
    states = {}
    for i in range(1, 7):
        path = os.path.join(STATE_DIR, f"loop{i}_state.yaml")
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        raw = preprocess_yaml(raw)
        states[i] = yaml.safe_load(raw)
    return states


# ============================================================
# Doubt condition 解析
# ============================================================

def parse_unlock_condition(text):
    """将 'item:1101 + testimony:1021001 + relation:106-104' 解析为
       [{'type':'1','param':'1101'}, {'type':'3','param':'1021001'}, {'type':'2','param':'106-104'}]

       type_map:
         item → 1
         relation → 2
         testimony → 3

       对 locked_* / visible_in_* / unlocked_after_* / posed_loop* 等状态值直接跳过，返回空列表。
    """
    if not text or not isinstance(text, str):
        return []
    t = text.strip()
    # 状态标记值（不是真正的 condition，仅用于叙事追踪）
    state_prefixes = ("locked_", "visible_", "posed_", "unlocked_after_", "resolved_")
    if t.startswith(state_prefixes):
        return []
    parts = [p.strip() for p in t.split("+")]
    type_map = {"item": "1", "relation": "2", "testimony": "3"}
    result = []
    for p in parts:
        if ":" not in p:
            continue
        kind, val = p.split(":", 1)
        kind = kind.strip().lower()
        val = val.strip()
        if kind in type_map and val:
            result.append({"type": type_map[kind], "param": val})
    return result


# ============================================================
# JSON 工具
# ============================================================

def fix_json(text):
    """状态机修复非标准 JSON（与 index.html fixJson 一致）"""
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


# ============================================================
# State 扫描（构建场景 → 证据 / NPC 映射）
# ============================================================

def build_scene_item_ids(states):
    """构建 {loop_num: {scene_id_str: [item_id_str, ...]}} 映射"""
    result = {}
    for loop_num, state in states.items():
        loop_items = {}
        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            sid = str(scene.get("id", ""))
            if not sid:
                continue
            items = []
            for ev in scene.get("evidence", []) or []:
                if isinstance(ev, dict):
                    eid = str(ev.get("id", ""))
                    if eid and eid not in items:
                        items.append(eid)
            if items:
                loop_items[sid] = items
        result[loop_num] = loop_items
    return result


def build_scene_npc_infos(states):
    """构建 {loop_num: {scene_id_str: [npc_info, ...]}} 映射"""
    result = {}
    for loop_num, state in states.items():
        loop_npcs = {}
        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            sid = str(scene.get("id", ""))
            npcs_data = scene.get("npcs", {})
            if not isinstance(npcs_data, dict) or not npcs_data:
                continue
            infos = []
            for talk_key in npcs_data.keys():
                # 提取前缀（如 vivian_001 → vivian / morrison_expose → morrison）
                prefix = talk_key.split("_", 1)[0] if "_" in talk_key else talk_key
                npc_id = NPC_KEY_TO_ID.get(prefix, "")
                if not npc_id:
                    continue
                npc = NPC_ID_MAP.get(npc_id, {})
                infos.append({
                    "id": f"{npc_id}_{sid}_{loop_num}",
                    "NPC": {
                        "id": npc_id,
                        "Name": [npc.get("name_cn", ""), npc.get("name_en", "")],
                        "role": npc.get("role", "5"),
                        "Chapter": CHAPTER,
                    },
                    "TalkInfo": {
                        "id": talk_key,
                    },
                })
            if infos:
                loop_npcs[sid] = infos
        result[loop_num] = loop_npcs
    return result


def collect_all_evidence(states):
    """收集所有 state 中出现的证据（scenes.[*].evidence + arrest/suspect_suicide 等自造段落内 new_evidence_gained + ending_sequence 的 evidence_obtained）

    返回: [ (loop_num, scene_id_or_None, evidence_dict), ... ] 去重按 id
    """
    collected = []
    seen_ids = set()

    def _add(loop_num, scene_id, ev):
        if not isinstance(ev, dict):
            return
        eid = ev.get("id")
        if eid is None:
            return
        eid = str(eid)
        if eid in seen_ids:
            return
        seen_ids.add(eid)
        collected.append((loop_num, scene_id, ev))

    for loop_num, state in states.items():
        # 1. scenes.[*].evidence
        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            sid = str(scene.get("id", ""))
            for ev in scene.get("evidence", []) or []:
                _add(loop_num, sid, ev)
            # body_search（Unit3 沿用字段，Unit1 目前未使用但保留以防）
            bs = scene.get("body_search", {})
            if isinstance(bs, dict):
                for ev in bs.get("evidence", []) or []:
                    _add(loop_num, sid, ev)
            # phone_call_event 等嵌套在场景内的自造段（无 evidence）

        # 2. evidence_registry（新增证据的规范化登记）
        for ev in state.get("evidence_registry", []) or []:
            if not isinstance(ev, dict):
                continue
            first_scene = ev.get("first_scene")
            fs_str = str(first_scene) if first_scene is not None else None
            if fs_str and fs_str.isdigit():
                _add(loop_num, fs_str, ev)
            else:
                # first_scene 是自造名称（如 suspect_suicide_sequence），记为 None
                _add(loop_num, None, ev)

        # 3. suspect_suicide_sequence.new_evidence_gained（loop5）
        sss = state.get("suspect_suicide_sequence", {})
        if isinstance(sss, dict):
            for ev in sss.get("new_evidence_gained", []) or []:
                _add(loop_num, None, ev)

        # 4. ending_sequence.sequence.act_3_safe_box.evidence_obtained（loop6）
        es = state.get("ending_sequence", {})
        if isinstance(es, dict):
            seq = es.get("sequence", {})
            if isinstance(seq, dict):
                for act_key, act in seq.items():
                    if not isinstance(act, dict):
                        continue
                    for ev in act.get("evidence_obtained", []) or []:
                        _add(loop_num, None, ev)

        # 5. turn_cutscene 内的 evidence_status_changes（不是新证据，跳过）

    return collected


# ============================================================
# YAML 生成
# ============================================================

def extract_opening_talks(opening_data):
    """从 opening 块里提取 emma_XXX / 等以 NPC 前缀命名的 talk key"""
    if not isinstance(opening_data, dict):
        return []
    talks = []
    for key in opening_data.keys():
        if key in ("type", "description", "location", "time", "scene_id", "characters", "purpose", "talk"):
            continue
        # 形如 emma_003 / zack_xxx 等
        if "_" in key:
            prefix = key.split("_", 1)[0]
            if prefix in NPC_KEY_TO_ID:
                talks.append(key)
    return talks


def collect_special_cutscenes(state):
    """收集 state 中的自造剧情段，返回 [{type, name, location}] 列表"""
    out = []
    for field in SPECIAL_SECTIONS:
        section = state.get(field)
        if not isinstance(section, dict):
            continue
        entry = {"type": field}
        if section.get("type"):
            entry["subtype"] = section.get("type")
        if section.get("location"):
            entry["location"] = section.get("location")
        # 摘要（description 的首行）
        desc = section.get("description", "")
        if isinstance(desc, str) and desc.strip():
            first_line = desc.strip().split("\n")[0][:80]
            entry["summary"] = first_line
        out.append(entry)
    return out


def build_free_phase(loop_num):
    """返回 loop 的 free_phase 场景 ID 列表（物理 ID，整数）"""
    cfg = LOOP_SCENE_CONFIG[loop_num]
    return list(cfg["unlocked"])


def build_locked_closed(loop_num):
    """返回 (locked_items, closed_ids)。locked_items 是 [{'id':..,'reason':''}]。"""
    cfg = LOOP_SCENE_CONFIG[loop_num]
    all_ids = [int(s["id"]) for s in SCENES]
    unlocked = set(cfg["unlocked"])
    locked = []
    for sid in all_ids:
        if sid not in unlocked:
            locked.append({"id": sid, "reason": ""})  # reason 由美术/策划后补
    return locked, []


def generate_loop_yaml(loop_num, state):
    """生成 data/Unit1/loop{N}.yaml"""
    meta = LOOP_META[loop_num]
    opening_data = state.get("opening", {}) or {}
    opening_talks = extract_opening_talks(opening_data)

    # target 优先从 player_context.goals.primary 取
    target = ""
    pc = state.get("player_context", {})
    if isinstance(pc, dict):
        goals = pc.get("goals", {})
        if isinstance(goals, dict):
            target = goals.get("primary", "") or ""

    # expose
    expose = state.get("expose", {}) or {}
    expose_target = expose.get("target", "") or ""
    target_name = expose_target if isinstance(expose_target, str) else ""

    # expose 场景：优先从 expose 里抓 scene_id（Unit1 规范化后可能没有 scene_id），
    # 否则按设计文档的"指证发生在哪个场景"推断。
    expose_scene_map = {
        1: 1001,   # 会客室
        2: 1005,   # Tommy 办公室（指证 Tommy）
        3: 1008,   # 清洁间（指证 Rosa 真击破）
        4: 1007,   # 大厅（指证 Vivian 让她放弃认罪）→ 按 turn_cutscene 前推断
        5: 1011,   # 后门（指证 Jimmy）
        6: 1014,   # 警局 Morrison 办公室
    }
    expose_scene = expose_scene_map.get(loop_num)

    # 指证轮次
    rounds = []
    for round_key in ("round_1", "round_2", "round_3", "round_4", "round_5"):
        rnd = expose.get(round_key)
        if not isinstance(rnd, dict):
            continue
        lie = rnd.get("lie", "") or ""
        evs = []
        for e in rnd.get("usable_evidence", []) or []:
            if isinstance(e, dict) and e.get("id") is not None:
                evs.append(str(e.get("id")))
        rounds.append({"lie": lie, "evidences": evs})

    # scenes 分类
    locked, closed = build_locked_closed(loop_num)
    free_phase = list(build_free_phase(loop_num))  # 新列表副本

    # opening（参考 Unit1 旧版 loop.yaml 用 opening_talks 列表）
    opening_scenes = []
    if opening_data.get("scene_id"):
        opening_scenes.append(opening_data["scene_id"])

    # target_name：把 expose.target 标识符转为 NPC 中文名
    expose_target_display_map = {
        "rosa": "Rosa",
        "tommy": "Tommy",
        "vivian": "Vivian",
        "jimmy": "Jimmy",
        "morrison": "Morrison",
    }
    target_display = expose_target_display_map.get(target_name, target_name)

    doc = {
        "title": meta["title"],
        "target": target,
        "time": meta["time"],
        "opening": opening_scenes,
        "opening_talks": opening_talks,
        "free_phase": list(free_phase),  # 独立副本避免 YAML anchor
        "scenes": {
            "unlocked": list(free_phase),  # 独立副本避免 YAML anchor
            "locked": locked,
            "closed": closed,
        },
        "expose": {
            "scene": expose_scene,
            "target_name": target_display,
            "rounds": rounds,
        },
    }

    # 自造剧情段
    specials = collect_special_cutscenes(state)
    if specials:
        doc["special_cutscenes"] = specials

    path = os.path.join(OUTPUT_DIR, f"loop{loop_num}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def generate_locations_yaml():
    """生成 data/Unit1/locations.yaml"""
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
    """生成 data/Unit1/talk_summary.yaml（精简摘要）"""
    summaries = {}
    for loop_num, state in states.items():
        # opening 的 emma_XXX
        opening = state.get("opening", {}) or {}
        for key in opening.keys():
            if not isinstance(opening.get(key), dict):
                continue
            npc_block = opening[key]
            if not isinstance(npc_block, dict):
                continue
            talk_id = npc_block.get("talk", "")
            motive = npc_block.get("motive", "")
            if talk_id and motive:
                summaries[talk_id] = f"L{loop_num} 开篇：{motive[:60]}"

        # scenes NPC talks
        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            npcs = scene.get("npcs", {})
            if not isinstance(npcs, dict):
                continue
            scene_name = scene.get("name", "")
            for npc_key, npc_data in npcs.items():
                if not isinstance(npc_data, dict):
                    continue
                talk_id = npc_data.get("talk", "")
                motive = npc_data.get("motive", "")
                if talk_id and motive:
                    summaries[talk_id] = f"L{loop_num} {scene_name}：{motive[:60]}"

        # expose 的 target_talk
        expose = state.get("expose", {}) or {}
        target_talk = expose.get("target_talk", "")
        expose_target = expose.get("target", "")
        if target_talk and expose_target:
            summaries[target_talk] = f"L{loop_num} 指证：{expose_target}"

    doc = {**summaries, "scene_talks": {}}
    path = os.path.join(OUTPUT_DIR, "talk_summary.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


# ============================================================
# JSON 追加（全部处理 Chapter=EPI01）
# ============================================================

def append_scenes_to_json(states):
    """追加 SceneConfig.json"""
    data = load_json("SceneConfig.json")
    data = [item for item in data if item.get("Chapter") != CHAPTER]

    per_loop_items = build_scene_item_ids(states)
    per_loop_npcs = build_scene_npc_infos(states)

    # 1. 静态条目（14 个物理场景）
    for scene in SCENES:
        entry = {
            "sceneId": scene["id"],
            "sceneName": scene["name"],
            "sceneNameEn": scene["name_en"],
            "sceneType": "1",
            "backgroundImage": SCENE_BG_CONFIG.get(scene["id"], ""),
            "backgroundMusic": "test",
            "Chapter": CHAPTER,
        }
        art = SCENE_ART_CONFIG.get(int(scene["id"]), "")
        if art:
            entry["ArtRequirement"] = art
        data.append(entry)

    # 2. 按 Loop × 场景的条目（含 ItemIDs / NPCInfos）
    # Unit1 不做 loop 场景 ID 转换（物理 ID 直接作为 sceneId），但每个 (loop, scene) 组合生成独立条目
    # 使用复合 id 避免和静态条目冲突：loopScene_{loop}_{scene}
    for loop_num in range(1, 7):
        cfg = LOOP_SCENE_CONFIG[loop_num]
        state = states[loop_num]
        expose = state.get("expose", {}) or {}

        active_scenes = list(cfg["unlocked"])
        # 加入 expose scene 若未包含
        expose_scene_map = {1: 1001, 2: 1005, 3: 1008, 4: 1007, 5: 1011, 6: 1014}
        esid = expose_scene_map.get(loop_num)
        if esid and esid not in active_scenes:
            active_scenes.append(esid)
        # opening scene_id（若存在）
        opening_sid = state.get("opening", {}).get("scene_id")
        if opening_sid:
            try:
                opening_sid = int(opening_sid)
                if opening_sid not in active_scenes:
                    active_scenes.append(opening_sid)
            except (TypeError, ValueError):
                pass

        for phys_id in active_scenes:
            phys_sid = str(phys_id)
            scene_name = SCENE_NAME_MAP.get(phys_sid, f"场景{phys_sid}")
            scene_en = SCENE_EN_MAP.get(phys_sid, "")
            loop_scene_id = f"loop{loop_num}_{phys_sid}"

            entry = {
                "sceneId": loop_scene_id,
                "sceneName": scene_name,
                "sceneNameEn": scene_en,
                "sceneType": "1",
                "backgroundImage": SCENE_BG_CONFIG.get(phys_sid, ""),
                "backgroundMusic": "test",
                "Chapter": CHAPTER,
            }

            art = SCENE_ART_CONFIG.get(phys_id, "")
            if art:
                entry["ArtRequirement"] = art

            item_ids = per_loop_items.get(loop_num, {}).get(phys_sid, [])
            if item_ids:
                entry["ItemIDs"] = item_ids

            npc_infos = per_loop_npcs.get(loop_num, {}).get(phys_sid, [])
            if npc_infos:
                entry["NPCInfos"] = npc_infos

            data.append(entry)

    save_json("SceneConfig.json", data)
    print(f"    -> 静态场景 {len(SCENES)} 个 + Loop 条目若干")


def append_items_to_json(states):
    """追加 ItemStaticData.json。itemType 动态来自 state.type（item/clue/envir）。"""
    data = load_json("ItemStaticData.json")
    data = [item for item in data if item.get("Chapter") != CHAPTER]

    collected = collect_all_evidence(states)
    items_to_add = []

    for loop_num, scene_id, ev in collected:
        eid = str(ev.get("id"))
        eid_int = int(eid) if eid.isdigit() else 0
        state_type = (ev.get("type") or "item").strip().lower()
        item_type = TYPE_TO_ITEMTYPE.get(state_type, "3")
        type_name = ITEM_TYPE_NAME_MAP.get(item_type, "item")

        scene_name = SCENE_NAME_MAP.get(scene_id, "") if scene_id else ""
        scene_en = SCENE_EN_MAP.get(scene_id, "") if scene_id else ""

        name_cn = ev.get("name", "") or ""
        name_en = f"Evidence_{eid}"
        note_text = ev.get("note", "") or ""
        desc_text = ev.get("description", "") or note_text

        entry = {
            "id": eid,
            "Name": [name_cn, name_en],
            "itemType": item_type,
            "canAnalyzed": "false",
            "canCombined": "false",
            "Describe": [desc_text],
            "ShortDescribe": [name_cn],
            "location": [scene_name, scene_en],
            "Chapter": CHAPTER,
            "folderPath": f"{CHAPTER}\\{scene_en}" if scene_en else CHAPTER,
            "desSpritePath": f"{type_name}_{eid}_big",
            "mapSpritePath": f"{type_name}_{eid}",
            "iconPath": f"{type_name}_{eid}_icon",
            "Position": ["0", "0"],
        }
        art = ART_CONFIG.get(eid_int, "")
        if art:
            entry["ArtRequirement"] = art

        items_to_add.append(entry)

    # 派生证据（Unit1 目前为空）
    for eid, info in DERIVED_EVIDENCE.items():
        eid_str = str(eid)
        # (保留接口，当前 DERIVED_EVIDENCE={} 不会进入)
        scene_label = info.get("scene", "")
        scene_label_en = info.get("scene_en", "")
        item_type = info.get("itemType", "1")
        type_name = ITEM_TYPE_NAME_MAP.get(item_type, "clue")
        items_to_add.append({
            "id": eid_str,
            "Name": [info["name"], f"Evidence_{eid_str}"],
            "itemType": item_type,
            "canAnalyzed": "false",
            "canCombined": "false",
            "Describe": [info.get("note", "")],
            "ShortDescribe": [info["name"]],
            "location": [scene_label, scene_label_en],
            "Chapter": CHAPTER,
            "folderPath": f"{CHAPTER}\\Derived",
            "desSpritePath": f"{type_name}_{eid_str}_big",
            "mapSpritePath": f"{type_name}_{eid_str}",
            "iconPath": f"{type_name}_{eid_str}_icon",
            "Position": ["0", "0"],
        })

    # 按 id 排序
    def _sort_key(x):
        try:
            return int(x["id"])
        except (TypeError, ValueError):
            return 0
    items_to_add.sort(key=_sort_key)

    data.extend(items_to_add)
    save_json("ItemStaticData.json", data)
    print(f"    -> 添加了 {len(items_to_add)} 个 EPI01 证据条目")


def append_npcs_to_json():
    """追加 NPCStaticData.json（EPI01 部分）"""
    data = load_json("NPCStaticData.json")
    data = [item for item in data if item.get("Chapter") != CHAPTER]

    for npc in NPCS:
        entry = {
            "id": npc["id"],
            "Name": [npc["name_cn"], npc["name_en"]],
            "role": npc["role"],
            "Chapter": CHAPTER,
        }
        icons = NPC_ICON_CONFIG.get(int(npc["id"]))
        if icons:
            entry["IconSmall"] = icons[0]
            entry["IconLarge"] = icons[1]
        art = NPC_ART_CONFIG.get(int(npc["id"]), "")
        if art:
            entry["ArtRequirement"] = art
        data.append(entry)
    save_json("NPCStaticData.json", data)


def append_doubts_to_json(states):
    """追加 DoubtConfig.json

    去重策略：同一 doubt id 可能在多个 loop 的 doubts 里继承出现。
    优先选择"有真实 condition"的版本（parsed 非空），其次取首次出现版本。
    """
    data = load_json("DoubtConfig.json")
    data = [item for item in data if item.get("Chapter") != CHAPTER]

    # 聚合每个 doubt id 的候选版本
    aggregated = {}  # did -> (text, conditions)
    for loop_num, state in states.items():
        for doubt in state.get("doubts", []) or []:
            if not isinstance(doubt, dict):
                continue
            did = str(doubt.get("id", "") or "")
            if not did:
                continue
            text = doubt.get("text", "") or ""
            condition_str = doubt.get("unlock_condition", "")
            conditions = parse_unlock_condition(condition_str)

            if did not in aggregated:
                aggregated[did] = (text, conditions)
            else:
                old_text, old_conds = aggregated[did]
                # 优先非空 condition
                if not old_conds and conditions:
                    aggregated[did] = (text or old_text, conditions)

    # 按 id 排序后写入
    for did in sorted(aggregated.keys(), key=lambda x: (len(x), x)):
        text, conditions = aggregated[did]
        data.append({
            "id": did,
            "condition": conditions,
            "text": text,
            "Chapter": CHAPTER,
        })
    save_json("DoubtConfig.json", data)
    print(f"    -> 写入 {len(aggregated)} 个 EPI01 疑点条目")


def append_chapter_config(states):
    """追加 ChapterConfig.json（Unit1 loops 用 id '101'-'106'）"""
    data = load_json("ChapterConfig.json")
    # 过滤旧 EPI01 loop 配置（id 以 '1' 开头且长度为 3）
    data = [item for item in data if not (
        str(item.get("id", "")).startswith("1") and len(str(item.get("id", ""))) == 3
    )]

    expose_scene_map = {1: 1001, 2: 1005, 3: 1008, 4: 1007, 5: 1011, 6: 1014}
    # Unit1 Expose 对象 NPC ID 映射
    expose_target_npc_map = {
        1: "103",  # Rosa
        2: "105",  # Tommy
        3: "103",  # Rosa（真击破）
        4: "106",  # Vivian
        5: "107",  # Jimmy
        6: "104",  # Morrison
    }

    for loop_num in range(1, 7):
        state = states[loop_num]
        expose = state.get("expose", {}) or {}

        # 收集该 loop 的疑点（仅该 loop 首次解锁的——简化处理为全部列出）
        doubts = []
        seen_local = set()
        for doubt in state.get("doubts", []) or []:
            if not isinstance(doubt, dict):
                continue
            did = str(doubt.get("id", "") or "")
            if not did or did in seen_local:
                continue
            seen_local.add(did)
            text = doubt.get("text", "") or ""
            condition_str = doubt.get("unlock_condition", "")
            conditions = parse_unlock_condition(condition_str)
            doubts.append({"id": did, "condition": conditions, "text": text})

        # 构建 exposes 数组
        exposes = []
        idx = 0
        for round_key in ("round_1", "round_2", "round_3", "round_4", "round_5"):
            rnd = expose.get(round_key)
            if not isinstance(rnd, dict):
                continue
            idx += 1
            items = []
            for e in rnd.get("usable_evidence", []) or []:
                if isinstance(e, dict) and e.get("id") is not None:
                    items.append(str(e.get("id")))
            exposes.append({
                "id": str(idx),
                "testimony": "",
                "item": items,
                "talkId": "",
            })

        config_id = f"10{loop_num}"  # 101..106
        init_scene = expose_scene_map.get(loop_num, 1001)
        data.append({
            "id": config_id,
            "initTalk": "",
            "initScene": str(init_scene),
            "doubts": doubts,
            "exposeNpcId": expose_target_npc_map.get(loop_num, ""),
            "exposes": exposes,
        })

    save_json("ChapterConfig.json", data)


# ============================================================
# AVG 对话导入（Talk / Expose → Talk.json / ExposeTalk.json / ExposeConfig.json / ExposeData.json）
# ============================================================

# 源 script → 目标 script 数字代码（见 0415 历史数据分析）
SCRIPT_CODE_MAP = {
    "": "",                       # 无 script → 不写入
    "end": "2",                   # 对话结束
    "branches": "1",              # 分支选项（带 Parameter 数组）
    "get": "3",                   # 获取证据/证词/事件
    "get_Evidence_Box": "4",      # 特殊：获取证物箱
    "interrupt": "5",             # 中断（loop6 录音打断）
    "Unlock_Cabaret_Hall": "6",   # 特殊：解锁歌舞厅
    "Lie": "7",                   # 指证谎言
}

# NPC IdSpeaker (源格式 "NPC101") → 数字 ID
# 特殊: NPC_RECORDER 作为录音机旁白
NPC_IDSPEAKER_MAP = {f"NPC{npc['id']}": npc["id"] for npc in NPCS}
NPC_IDSPEAKER_MAP["NPC_RECORDER"] = "RECORDER"  # 保留原标签，不做转换

# 哪些 NPC 有 icon（和 Talk.json 现有格式一致）
NPC_HAS_ICON = {"103", "104", "105", "106", "107", "108", "110"}

# Expose 每个 loop 对应的 testimony ID（与现有 ExposeData.json 一致）
LOOP_EXPOSE_TESTIMONY = {
    1: "1031002",  # Rosa
    2: "1041003",  # Morrison
    3: "1053001",  # Tommy
    4: "1071006",  # Jimmy (loop4)
    5: "1063002",  # Vivian
    6: "1072003",  # Jimmy (loop6)
}

# Expose sceneId = "1{loop}" (11/12/13/14/15/16)
LOOP_EXPOSE_SCENE_ID = {i: f"1{i}" for i in range(1, 7)}

# Expose 目标 NPC id (1-indexed loop → npc_id)
LOOP_EXPOSE_NPC = {
    1: "103",  # Rosa
    2: "104",  # Morrison
    3: "105",  # Tommy
    4: "107",  # Jimmy
    5: "106",  # Vivian
    6: "107",  # Jimmy
}

LOOP_EXPOSE_NPC_INFO_ID = {
    1: "2", 2: "2", 3: "2", 4: "1", 5: "2", 6: "3",
}


def _load_avg_json_file(path):
    """加载单个 AVG JSON 文件。返回条目列表（dict 会被包进单元素列表）。"""
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    if isinstance(d, dict):
        return [d]
    elif isinstance(d, list):
        return d
    else:
        return []


def _normalize_avg_talk_entry(src, source_file_hint=None):
    """将 AVG 源对话条目转换为 Talk.json 目标格式。

    返回目标格式 dict，或 None（若 IdSpeaker 不识别）。
    """
    src_speaker = src.get("IdSpeaker", "")
    npc_id = NPC_IDSPEAKER_MAP.get(src_speaker)

    # Speaker 块
    if npc_id and npc_id != "RECORDER":
        npc = NPC_ID_MAP.get(npc_id, {})
        speaker = {
            "id": npc_id,
            "Name": [npc.get("name_cn", src.get("cnSpeaker", "")),
                     npc.get("name_en", src.get("enSpeaker", ""))],
            "role": npc.get("role", "5"),
            "Chapter": CHAPTER,
        }
        if npc_id in NPC_HAS_ICON:
            icons = NPC_ICON_CONFIG.get(int(npc_id))
            if icons:
                speaker["IconSmall"] = icons[0]
                speaker["IconLarge"] = icons[1]
    else:
        # 未识别或 RECORDER：保留名称但不设 id（或用原前缀）
        speaker = {
            "id": npc_id if npc_id else src_speaker,
            "Name": [src.get("cnSpeaker", ""), src.get("enSpeaker", "")],
            "role": "5",
            "Chapter": CHAPTER,
        }

    # 基础字段
    entry = {
        "id": str(src.get("id", "")),
        "step": str(src.get("step", "")),
        "isRight": "false",
        "waitTime": str(src.get("waitTime", 0)),
        "Speaker": speaker,
    }

    # Location: 优先 cnLocation/enLocation（数组），否则 Location（单字符串）也生成数组
    cn_loc = src.get("cnLocation", "") or ""
    en_loc = src.get("enLocation", "") or ""
    single_loc = src.get("Location", "") or ""
    if cn_loc or en_loc:
        entry["Location"] = [cn_loc, en_loc]
    elif single_loc:
        entry["Location"] = [single_loc, single_loc]

    # Words
    entry["Words"] = [src.get("cnWords", "") or "", src.get("enWords", "") or ""]

    # next 字段：源 next 可能是数字、字符串、空串或 "-1" 或 ""
    src_next = src.get("next", "")
    # 规范化：空串、null、"-1" 等 ending 标记 → 不写 next
    src_script = src.get("script", "") or ""
    if src_script in ("end", "Lie"):
        # end/Lie 的 next 一般被吞掉（target 中不存在）
        if src_script == "Lie":
            # Lie 的 break_next 放在 ParameterInt0，target 里 next 保留为该值
            pi0 = src.get("ParameterInt0", 0)
            if pi0 and str(pi0) not in ("0",):
                entry["next"] = str(pi0)
        # end: 不设 next
    else:
        if src_next not in (None, "", "-1"):
            entry["next"] = str(src_next)

    # script 映射
    target_script = SCRIPT_CODE_MAP.get(src_script, "")
    if target_script:
        entry["script"] = target_script

    # Parameters 构建
    # 默认：[{"ParameterInt": "0"}]
    # branches: 每个非空 ParameterStrN + ParameterIntN 作为一对
    # get: 有 Str 的 → {ParameterStr, ParameterInt:"0"}
    # Lie: 强制 default（[{ParameterInt:"0"}]）—— 与现有 Talk.json 一致
    params = []
    if src_script == "branches":
        for i in range(4):  # 0..3
            ps = src.get(f"ParameterStr{i}", "") or ""
            pi = src.get(f"ParameterInt{i}", 0)
            if ps or (pi and str(pi) not in ("0",)):
                params.append({
                    "ParameterStr": ps,
                    "ParameterInt": str(pi) if pi else "0",
                })
        if not params:
            params = [{"ParameterInt": "0"}]
    elif src_script == "get":
        # 选用第一个非空 Str（源同时有 ParameterStr0 和 ParameterStr1 的情况：通常只有一个非空）
        combined_str = ""
        for i in range(4):
            ps = src.get(f"ParameterStr{i}", "") or ""
            if ps:
                combined_str = ps
                break
        if combined_str:
            params.append({"ParameterStr": combined_str, "ParameterInt": "0"})
        else:
            params = [{"ParameterInt": "0"}]
    elif src_script == "interrupt":
        # interrupt: ParameterInt0 = 1（标记）
        pi0 = src.get("ParameterInt0", 0)
        if pi0 is not None:
            params = [{"ParameterInt": str(pi0) if pi0 else "0"}]
        else:
            params = [{"ParameterInt": "0"}]
    else:
        params = [{"ParameterInt": "0"}]
    entry["Parameters"] = params

    # videoEpisode / videoLoop / videoScene / videoId
    entry["videoEpisode"] = src.get("videoEpisode", CHAPTER)
    entry["videoLoop"] = src.get("videoLoop", "")
    entry["videoScene"] = src.get("videoScene", "") or (source_file_hint or "")
    entry["videoId"] = str(src.get("videoId", "") or entry["id"])

    return entry


def _normalize_expose_talk_entry(src):
    """将 AVG Expose 源条目转换为 ExposeTalk.json 目标格式。"""
    src_speaker = src.get("IdSpeaker", "")
    npc_id = NPC_IDSPEAKER_MAP.get(src_speaker, src_speaker.replace("NPC", ""))

    npc = NPC_ID_MAP.get(npc_id, {})
    cn_speaker = npc.get("name_cn", src.get("cnSpeaker", ""))
    en_speaker = npc.get("name_en", src.get("enSpeaker", ""))

    entry = {
        "id": str(src.get("id", "")),
        "step": str(src.get("step", "")),
        "speakType": f"E_{src.get('speakType', 2)}",
        "waitTime": str(src.get("waitTime", 0)),
        "IdSpeaker": npc_id,
        "cnSpeaker": cn_speaker,
        "enSpeaker": en_speaker,
        "talkDisplayIndex": str(src.get("talkDisplayIndex", 1 if npc_id == "101" else 2)),
        "cnWords": src.get("cnWords", "") or "",
        "enWords": src.get("enWords", "") or "",
    }

    src_next = src.get("next", "")
    if src_next not in (None, "", "-1"):
        entry["next"] = str(src_next)

    # script：Lie / end 等原文保留，空则不写
    src_script = src.get("script", "") or ""
    if src_script:
        entry["script"] = src_script

    # 对 Lie 保留 ParameterStr0 中的证据串（去除 EV 前缀）
    if src_script == "Lie":
        ps0 = src.get("ParameterStr0", "") or ""
        # 去掉 "EV" 前缀并转为逗号分隔数字
        items = [x.strip().removeprefix("EV") for x in ps0.split(",") if x.strip()]
        entry["ParameterStr0"] = ",".join(items)

    pi0 = src.get("ParameterInt0", 0)
    pi1 = src.get("ParameterInt1", 0)
    pi2 = src.get("ParameterInt2", 0)
    entry["ParameterInt0"] = str(pi0 if pi0 is not None else 0)
    entry["ParameterInt1"] = str(pi1 if pi1 is not None else 0)
    entry["ParameterInt2"] = str(pi2 if pi2 is not None else 0)

    entry["videoEpisode"] = src.get("videoEpisode", CHAPTER)
    entry["videoLoop"] = src.get("videoLoop", "")
    entry["videoScene"] = src.get("videoScene", "")
    entry["videoId"] = str(src.get("videoId", "") or entry["id"])

    return entry


def load_avg_talks(include_expose=True):
    """从 AVG/EPI01/Talk/loop{1-6}/*.json 读取所有 Unit1 对话。

    跳过 _manifest.json；每个文件可能是单条（dict）或数组（list）。
    可选 include_expose=True：同时把 AVG/EPI01/Expose/*.json 也转成 Talk.json 目标格式
    （保持历史 Talk.json 同时收纳 Talk+Expose 条目的行为）。
    返回扁平化的 Talk.json 目标格式条目列表。
    """
    talks = []
    files_loaded = 0
    for loop_num in range(1, 7):
        loop_dir = os.path.join(AVG_TALK_DIR, f"loop{loop_num}")
        if not os.path.isdir(loop_dir):
            continue
        for fname in sorted(os.listdir(loop_dir)):
            if not fname.endswith(".json") or fname.startswith("_manifest"):
                continue
            path = os.path.join(loop_dir, fname)
            scene_hint = fname.removesuffix(".json")
            entries = _load_avg_json_file(path)
            for src in entries:
                tgt = _normalize_avg_talk_entry(src, source_file_hint=scene_hint)
                if tgt is not None:
                    talks.append(tgt)
            files_loaded += 1

    expose_files = 0
    expose_entries_added = 0
    if include_expose and os.path.isdir(AVG_EXPOSE_DIR):
        for fname in sorted(os.listdir(AVG_EXPOSE_DIR)):
            if not fname.endswith(".json") or fname.startswith("_manifest"):
                continue
            path = os.path.join(AVG_EXPOSE_DIR, fname)
            scene_hint = fname.removesuffix(".json")
            entries = _load_avg_json_file(path)
            for src in entries:
                tgt = _normalize_avg_talk_entry(src, source_file_hint=scene_hint)
                if tgt is not None:
                    talks.append(tgt)
                    expose_entries_added += 1
            expose_files += 1

    print(f"    [AVG] 读取 {files_loaded} 个 Talk 文件 + {expose_files} 个 Expose 文件，"
          f"共 {len(talks)} 条对话（其中 Expose {expose_entries_added} 条）")
    return talks


def load_avg_exposes():
    """从 AVG/EPI01/Expose/loop{N}_{npc}.json 读取所有指证对话。

    返回 (expose_talks, expose_configs, expose_data) 三元组：
      expose_talks: ExposeTalk.json 条目列表
      expose_configs: ExposeConfig.json 条目列表（每个 loop 一个）
      expose_data: ExposeData.json 条目列表（每个 Lie 一条）
    """
    expose_talks = []
    expose_configs = []
    expose_data = []

    # 从 ExposeData.json 现存的最大 id 继续编号（避免与 Unit2 id 冲突）
    existing_data = []
    try:
        existing_data = load_json("ExposeData.json")
    except Exception:
        existing_data = []
    # 计算 Unit1 最大 id（用于分配新 id）
    u1_ids = []
    for it in existing_data:
        # Unit1 的 testimony 以 1 开头
        if str(it.get("testimony", "")).startswith("1"):
            try:
                u1_ids.append(int(it["id"]))
            except (TypeError, ValueError):
                pass
    next_data_id = max(u1_ids) + 1 if u1_ids else 1
    # 为保持与现有数据一致，从 1 开始重新分配
    next_data_id = 1

    for loop_num in range(1, 7):
        expose_npc = LOOP_EXPOSE_NPC[loop_num]
        # 按现有文件名规则
        npc_name_map = {
            1: "rosa", 2: "morrison", 3: "tommy",
            4: "jimmy", 5: "vivian", 6: "jimmy",
        }
        fname = f"loop{loop_num}_{npc_name_map[loop_num]}.json"
        path = os.path.join(AVG_EXPOSE_DIR, fname)
        if not os.path.isfile(path):
            print(f"    [WARN] Expose file not found: {path}")
            continue
        entries = _load_avg_json_file(path)
        if not entries:
            continue

        # 1. ExposeTalk 格式转换
        for src in entries:
            expose_talks.append(_normalize_expose_talk_entry(src))

        # 2. ExposeConfig：聚合所有 Lie 的证据到 ExposeItemID
        lie_entries = [e for e in entries if (e.get("script", "") or "") == "Lie"]
        all_items = []
        for lie in lie_entries:
            ps0 = lie.get("ParameterStr0", "") or ""
            for x in ps0.split(","):
                x = x.strip().removeprefix("EV")
                if x and x not in all_items:
                    all_items.append(x)
        expose_configs.append({
            "sceneId": LOOP_EXPOSE_SCENE_ID[loop_num],
            "ExposeNPCID": LOOP_EXPOSE_NPC[loop_num],
            "ExposeNPCInfoID": LOOP_EXPOSE_NPC_INFO_ID[loop_num],
            "ExposeItemIDCount": "1",
            "ExposeItemID": [",".join(all_items) if all_items else ""],
            "ExposeTalkID": str(entries[0].get("id", "")),
        })

        # 3. ExposeData：每个 Lie 一条
        #    talkId 策略：round 1 = 首个对话 id；round N>1 = 前一个 Lie 的 ParameterInt0
        first_entry_id = str(entries[0].get("id", ""))
        testimony_id = LOOP_EXPOSE_TESTIMONY[loop_num]

        prev_break_next = None
        for idx, lie in enumerate(lie_entries):
            ps0 = lie.get("ParameterStr0", "") or ""
            items = [x.strip().removeprefix("EV") for x in ps0.split(",") if x.strip()]
            if idx == 0:
                talk_id = first_entry_id
            else:
                talk_id = str(prev_break_next) if prev_break_next else first_entry_id
            expose_data.append({
                "id": str(next_data_id),
                "testimony": testimony_id,
                "item": items,
                "talkId": talk_id,
            })
            next_data_id += 1
            # 记录本 Lie 的 break_next（下个 round 的 talkId 候选）
            pi0 = lie.get("ParameterInt0", 0)
            prev_break_next = pi0 if pi0 else None

    print(f"    [AVG] 读取 {len(expose_talks)} 条 Expose 对话，"
          f"{len(expose_configs)} 个 ExposeConfig，{len(expose_data)} 条 ExposeData")
    return expose_talks, expose_configs, expose_data


def append_avg_talks_to_table(talks, dry_run=False):
    """合并 AVG Talk 到 data/table/Talk.json

    清理策略：删除所有 id 以 1[0-6] 开头的 Unit1 旧条目（6 位或 9 位）。
    保留：id 前缀 2x 的 Unit2 条目 + Chapter != EPI01 的其他条目。
    """
    data = load_json("Talk.json")
    before_count = len(data)

    unit1_prefixes = {"10", "11", "12", "13", "14", "15", "16"}
    kept = []
    removed = 0
    for it in data:
        iid = str(it.get("id", ""))
        if iid[:2] in unit1_prefixes:
            removed += 1
        else:
            kept.append(it)

    # 统计保留项的 Chapter 分布（验证 Unit2 未被动）
    keep_prefix = {}
    for it in kept:
        p = str(it.get("id", ""))[:2]
        keep_prefix[p] = keep_prefix.get(p, 0) + 1

    print(f"    [Talk.json] 原 {before_count} 条；清理 Unit1 旧 {removed} 条；"
          f"保留 {len(kept)} 条（前缀分布：{keep_prefix}）")
    print(f"    [Talk.json] 将追加 {len(talks)} 条 AVG 新对话")

    if dry_run:
        print("    [DRY-RUN] 不写入文件")
        return

    # 追加
    kept.extend(talks)
    save_json("Talk.json", kept)
    print(f"    [Talk.json] 最终 {len(kept)} 条")


def append_avg_exposes_to_table(expose_talks, expose_configs, expose_data, dry_run=False):
    """合并 AVG Expose 数据到 ExposeTalk.json / ExposeConfig.json / ExposeData.json。

    清理策略：
      - ExposeTalk.json: 删除 id 前缀 1[1-6] 的 Unit1 条目（全是 Unit1，按需清理）
      - ExposeConfig.json: 删除 sceneId 前缀 "1" 的 Unit1 条目
      - ExposeData.json: 删除 testimony 前缀 "1" 的 Unit1 条目
    """
    # --- ExposeTalk.json ---
    etalk = load_json("ExposeTalk.json")
    before_etalk = len(etalk)
    u1_prefixes = {"11", "12", "13", "14", "15", "16"}
    etalk_kept = [it for it in etalk if str(it.get("id", ""))[:2] not in u1_prefixes]
    print(f"    [ExposeTalk.json] 原 {before_etalk} 条；清理 {before_etalk - len(etalk_kept)} 条；"
          f"追加 {len(expose_talks)} 条")

    # --- ExposeConfig.json ---
    econf = load_json("ExposeConfig.json")
    before_econf = len(econf)
    # Unit1 sceneId 是 "11"-"16"
    econf_kept = [it for it in econf if not str(it.get("sceneId", "")).startswith("1")]
    print(f"    [ExposeConfig.json] 原 {before_econf} 条；清理 {before_econf - len(econf_kept)} 条；"
          f"追加 {len(expose_configs)} 条")

    # --- ExposeData.json ---
    edata = load_json("ExposeData.json")
    before_edata = len(edata)
    # Unit1 testimony 以 "1" 开头
    edata_kept = [it for it in edata if not str(it.get("testimony", "")).startswith("1")]
    unit2_remaining = len(edata_kept)
    print(f"    [ExposeData.json] 原 {before_edata} 条；清理 {before_edata - len(edata_kept)} 条；"
          f"追加 {len(expose_data)} 条 (Unit2 保留 {unit2_remaining})")

    if dry_run:
        print("    [DRY-RUN] 不写入文件")
        return

    etalk_kept.extend(expose_talks)
    econf_kept.extend(expose_configs)
    edata_kept.extend(expose_data)

    save_json("ExposeTalk.json", etalk_kept)
    save_json("ExposeConfig.json", econf_kept)
    save_json("ExposeData.json", edata_kept)
    print(f"    [写入] ExposeTalk={len(etalk_kept)}, "
          f"ExposeConfig={len(econf_kept)}, ExposeData={len(edata_kept)}")


# ============================================================
# 主流程
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("Unit1 State -> Preview 数据转换（0417 规范化版）")
    print("=" * 50)

    print("\n[1/3] 读取 State 文件...")
    states = load_all_states()
    print(f"  [OK] 已读取 {len(states)} 个 state 文件")

    print("\n[2/3] 生成 Preview YAML 文件...")
    for i in range(1, 7):
        generate_loop_yaml(i, states[i])
    generate_locations_yaml()
    generate_talk_summary(states)

    print("\n[3/4] 追加 JSON 数据表（仅处理 Chapter=EPI01）...")
    append_scenes_to_json(states)
    append_items_to_json(states)
    append_npcs_to_json()
    append_doubts_to_json(states)
    append_chapter_config(states)

    print("\n[4/4] 合并 AVG 对话 JSON (Talk / Expose)...")
    dry_run = os.environ.get("AVG_DRY_RUN", "").lower() in ("1", "true", "yes")
    talks = load_avg_talks()
    e_talks, e_configs, e_data = load_avg_exposes()
    append_avg_talks_to_table(talks, dry_run=dry_run)
    append_avg_exposes_to_table(e_talks, e_configs, e_data, dry_run=dry_run)

    print("\n" + "=" * 50)
    print("Unit1 preview 数据生成完成")
    print(f"YAML 输出: {OUTPUT_DIR}")
    print(f"JSON 更新: {TABLE_DIR}")
    if dry_run:
        print("(AVG_DRY_RUN=1 — AVG 对话部分为预览模式，未写入文件)")
    print("=" * 50)


if __name__ == "__main__":
    main()
