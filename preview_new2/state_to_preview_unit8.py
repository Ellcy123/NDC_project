#!/usr/bin/env python3
"""
Unit8 State → Preview 数据转换脚本（Unit1 重构版的 8-prefix 版本）

读取 剧情设计/Unit8/state/loop{1-6}_state.yaml（state 文件保持 1-prefix ID 不动）
生成 preview_new2/data/Unit8/ 下的 YAML 文件
追加 preview_new2/data/table/ 下的 JSON 条目（Chapter="EPI08"）

所有 state 里以 '1' 开头的纯数字 ID 在输出时首位换成 '8'：
  场景 1001-1014 → 8001-8014
  证据 1101/1201... → 8101/8201...
  NPC 101-111 → 801-811
  Doubt 1xxx → 8xxx
  Testimony 1xxxxxx → 8xxxxxx
  Dialogue 9 位 → 8xxxxxxxx

美术资源路径保持原名（SC1001_bg_*、NPC icon "zack_small" 等），
因为资产文件名未变——只在 preview/table 的 ID 层面做 8-prefix 隔离。

AVG 对话读自 AVG/EPI08/ （用户新写的 MD 同步产物，8-prefix）。
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
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "data", "Unit8")
TABLE_DIR = os.path.join(SCRIPT_DIR, "data", "table")

# AVG 对话源目录（Unit8 专用）
AVG_DIR = os.path.join(PROJECT_ROOT, "AVG", "EPI08")
AVG_TALK_DIR = os.path.join(AVG_DIR, "Talk")
AVG_EXPOSE_DIR = os.path.join(AVG_DIR, "Expose")

CHAPTER = "EPI08"


# ============================================================
# ID 映射工具：state(1-prefix) → unit8(8-prefix)
# ============================================================

def map_id(raw):
    """仅对纯数字且首位为 '1' 的字符串换首位为 '8'；其他保持原样。"""
    if raw is None:
        return raw
    s = str(raw).strip()
    if s.isdigit() and s.startswith("1"):
        return "8" + s[1:]
    return s


def map_condition_param(kind, val):
    """DoubtConfig condition param 映射。
    kind: '1' item, '2' relation (形如 '106-104'), '3' testimony。
    relation 按 '-' 切分后逐段映射，其他直接 map_id。
    """
    if kind == "2":
        parts = val.split("-")
        return "-".join(map_id(p) for p in parts)
    return map_id(val)

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

# Unit8 物理场景 ID → 中英文名（14 个物理场景，8-prefix）
SCENES = [
    {"id": "8001", "name": "一楼会客室", "name_en": "MeetingRoom_1F"},
    {"id": "8002", "name": "Vivian 工作室", "name_en": "VivianStudio"},
    {"id": "8003", "name": "二楼厨房", "name_en": "Kitchen_2F"},
    {"id": "8004", "name": "Webb 办公室", "name_en": "WebbOffice"},
    {"id": "8005", "name": "Tommy 办公室", "name_en": "TommyOffice"},
    {"id": "8006", "name": "歌舞厅", "name_en": "Ballroom"},
    {"id": "8007", "name": "酒吧大厅", "name_en": "BarLobby"},
    {"id": "8008", "name": "清洁间", "name_en": "JanitorRoom"},
    {"id": "8009", "name": "一楼走廊", "name_en": "Corridor_1F"},
    {"id": "8010", "name": "Vivian 化妆间", "name_en": "VivianDressingRoom"},
    {"id": "8011", "name": "蓝月亮酒吧后门", "name_en": "BarBackDoor"},
    {"id": "8012", "name": "James 家", "name_en": "JamesHome"},
    {"id": "8013", "name": "Morrison 家", "name_en": "MorrisonHome"},
    {"id": "8014", "name": "警局 Morrison 办公室", "name_en": "PoliceStation_MorrisonOffice"},
]

SCENE_NAME_MAP = {s["id"]: s["name"] for s in SCENES}
SCENE_EN_MAP = {s["id"]: s["name_en"] for s in SCENES}

# 每个 Loop 的场景分类（unlocked 用 Unit8 的 8-prefix ID）
LOOP_SCENE_CONFIG = {
    1: {"unlocked": [8001]},
    2: {"unlocked": [8002, 8003, 8004, 8005, 8006]},
    3: {"unlocked": [8003, 8007, 8001, 8008]},
    4: {"unlocked": [8009, 8005, 8010, 8006, 8007]},
    5: {"unlocked": [8005, 8003, 8012, 8011]},
    6: {"unlocked": [8013, 8014, 8001]},
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

# NPC 列表（Unit8 = 101-111 映射到 801-811；美术资源名称保持原样）
NPCS = [
    {"id": "801", "name_cn": "扎克·布伦南", "name_en": "Zack Brennan", "role": "4"},
    {"id": "802", "name_cn": "艾玛·奥马利", "name_en": "Emma O'Malley", "role": "3"},
    {"id": "803", "name_cn": "罗莎·马丁内斯", "name_en": "Rosa Martinez", "role": "5"},
    {"id": "804", "name_cn": "莫里森", "name_en": "Morrison", "role": "5"},
    {"id": "805", "name_cn": "汤米", "name_en": "Tommy", "role": "5"},
    {"id": "806", "name_cn": "薇薇安·罗斯", "name_en": "Vivian Rose", "role": "5"},
    {"id": "807", "name_cn": "詹姆斯", "name_en": "James", "role": "5"},
    {"id": "808", "name_cn": "安娜", "name_en": "Anna", "role": "5"},
    {"id": "809", "name_cn": "韦布", "name_en": "Webb", "role": "1"},
    {"id": "810", "name_cn": "莫里森太太", "name_en": "Mrs. Morrison", "role": "5"},
    {"id": "811", "name_cn": "鲸鱼", "name_en": "Whale", "role": "5"},
]
NPC_ID_MAP = {npc["id"]: npc for npc in NPCS}

# talk_key 前缀 → NPC id（Unit8 的 8-prefix）
NPC_KEY_TO_ID = {
    "zack": "801",
    "emma": "802",
    "rosa": "803",
    "morrison": "804",
    "tommy": "805",
    "vivian": "806",
    "james": "807",
    "anna": "808",
    "webb": "809",
    "whale": "811",
}

# NPC 图标配置（命名规则: firstname_small / firstname_big，美术文件名未变）
NPC_ICON_CONFIG = {int(k): (f"{name}_small", f"{name}_big") for k, name in {
    "801": "zack", "802": "emma", "803": "rosa", "804": "morrison",
    "805": "tommy", "806": "vivian", "807": "james", "808": "anna",
    "809": "webb", "810": "mrsmorrison", "811": "whale",
}.items()}


def _art_scene_id(scene_id):
    """把 Unit8 的场景 ID 映回原 Unit1 的 SC{id} 文件名（8xxx → 1xxx）。"""
    s = str(scene_id)
    if s.startswith("8") and s[1:].isdigit():
        return "1" + s[1:]
    return s


def _art_item_id(item_id):
    """把 Unit8 证据 ID 映回原 1-prefix，用于 sprite/icon 文件名复用。"""
    s = str(item_id)
    if s.isdigit() and s.startswith("8"):
        return "1" + s[1:]
    return s


# 场景背景图路径：sceneId 是 8xxx，但文件名仍指向原 SC1xxx_bg_* 资产
SCENE_BG_CONFIG = {
    s["id"]: f"Art\\Scene\\Backgrounds\\EPI01\\SC{_art_scene_id(s['id'])}_bg_{s['name_en']}"
    for s in SCENES
}

# locations.yaml 数据（按"酒吧"主楼 + Morrison 家 + James 家 + 警局组织）
LOCATIONS = [
    {"name": "蓝月亮酒吧", "entry": "07", "children": ["01", "02", "03", "04", "05", "06", "08", "09", "10", "11"]},
    {"name": "James 家", "entry": "12", "children": []},
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
# Testimony 抽取：扫 state 原文 testimony_ids 块里的 "- 7位数字 # 文本" 行
# ============================================================

_TESTIMONY_LINE = re.compile(r'^\s*-\s+(\d{7})\s*#\s*(.+?)\s*$')
_TESTIMONY_HEADER = re.compile(r'^\s*testimony_ids:\s*$')


def extract_testimonies_from_state():
    """返回 {tid(8-prefix): {'text':..., 'loop':N, 'npc_id':'80X'}}。
    tid 第 2-3 位是 NPC code（Unit8 NPC id = '8' + code）。
    tid 第 4 位是 loop。
    """
    collected = {}
    for loop_num in range(1, 7):
        path = os.path.join(STATE_DIR, f"loop{loop_num}_state.yaml")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_block = False
        header_indent = -1
        for line in lines:
            if _TESTIMONY_HEADER.match(line):
                in_block = True
                header_indent = len(line) - len(line.lstrip())
                continue
            if in_block:
                stripped = line.rstrip("\n")
                # 空行跳过不退出
                if not stripped.strip():
                    continue
                cur_indent = len(line) - len(line.lstrip())
                # 缩进回到 header 同级或更浅 → 退出块
                if cur_indent <= header_indent:
                    in_block = False
                    continue
                m = _TESTIMONY_LINE.match(stripped)
                if not m:
                    continue
                raw_id = m.group(1)
                text = m.group(2).strip()
                # 去掉 ⚠谎言:/⚠偏见: 前缀（策划内部标签）
                text = re.sub(r"^⚠?\s*(谎言|偏见)\s*[:：]\s*", "", text)
                tid = map_id(raw_id)  # 1-prefix → 8-prefix
                if tid in collected:
                    continue  # 首次出现为准
                # NPC code（ID 第 2-3 位）+ Unit8 前缀 8
                npc_code = raw_id[1:3]
                npc_id = "8" + npc_code
                collected[tid] = {
                    "text": text,
                    "loop": loop_num,
                    "npc_id": npc_id,
                    "raw_id": raw_id,
                }
    return collected


def append_testimonies_to_json(testimonies):
    """写入 Testimony.json（按 NPC 聚合，带 evidenceItem 列表）
       和 TestimonyItem.json（扁平列表，供其他模块用）。
    """
    # --- Testimony.json ---
    try:
        tdata = load_json("Testimony.json")
    except Exception:
        tdata = []
    # 清理旧 Unit8 条目（chapter 或 npc.Chapter 为 EPI08；或 id 以 '80' 开头的 9 位）
    tdata_kept = [
        it for it in tdata
        if not (
            (it.get("npc", {}).get("Chapter") == CHAPTER) or
            (it.get("chapter") in {"801", "802", "803", "804", "805", "806"})
        )
    ]

    # 按 NPC 聚合（一个 NPC 一条 top-level Testimony，evidenceItem 汇总所有 loop 的证词）
    by_npc = {}
    for tid, info in testimonies.items():
        npc_id = info["npc_id"]
        if npc_id not in NPC_ID_MAP:
            continue
        by_npc.setdefault(npc_id, []).append((tid, info))

    for npc_id, items in by_npc.items():
        npc = NPC_ID_MAP[npc_id]
        evidence_items = []
        for tid, info in sorted(items, key=lambda x: x[0]):
            evidence_items.append({
                "id": tid,
                "testimonyType": "1",
                "testimony": [info["text"], ""],
                "triggerType": "2",
                "triggerParam": f"{npc_id},801",  # NPC,Zack
            })
        # 合成 trigger id：{npc}{seq=001}{000} → npc_id + "001000"（占位）
        trigger_id = f"{npc_id}001000"
        entry = {
            "id": trigger_id,
            "npc": {
                "id": npc_id,
                "Name": [npc.get("name_cn", ""), npc.get("name_en", "")],
                "role": npc.get("role", "5"),
                "Chapter": CHAPTER,
            },
            "chapter": f"80{items[0][1]['loop']}",  # 取第一条 loop
            "words": ["", ""],
            "evidenceItem": evidence_items,
        }
        # NPC icon（有的话）
        icons = NPC_ICON_CONFIG.get(int(npc_id))
        if icons:
            entry["npc"]["IconSmall"] = icons[0]
            entry["npc"]["IconLarge"] = icons[1]
        tdata_kept.append(entry)

    save_json("Testimony.json", tdata_kept)
    print(f"    -> Testimony.json 追加 {len(by_npc)} 个 Unit8 NPC 聚合条目")

    # --- TestimonyItem.json ---
    try:
        tidata = load_json("TestimonyItem.json")
    except Exception:
        tidata = []
    # 清理旧 Unit8（id 以 '8' 开头）
    tidata_kept = [it for it in tidata if not str(it.get("id", "")).startswith("8")]
    added = 0
    for tid, info in sorted(testimonies.items()):
        tidata_kept.append({
            "id": tid,
            "testimonyType": "1",
            "testimony": [info["text"], ""],
            "triggerType": "2",
            "triggerParam": f"{info['npc_id']},801",
        })
        added += 1
    save_json("TestimonyItem.json", tidata_kept)
    print(f"    -> TestimonyItem.json 追加 {added} 条 Unit8 证词条目")


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
            tcode = type_map[kind]
            result.append({"type": tcode, "param": map_condition_param(tcode, val)})
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
    """构建 {loop_num: {scene_id_str: [item_id_str, ...]}} 映射（ID 均为 8-prefix）。
    来源：scenes.[*].evidence + evidence_registry（首次登记且 first_scene 为数字场景 ID）。
    """
    result = {}
    for loop_num, state in states.items():
        loop_items = {}

        def _append(sid, eid):
            if not sid or not eid:
                return
            loop_items.setdefault(sid, [])
            if eid not in loop_items[sid]:
                loop_items[sid].append(eid)

        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            sid = map_id(scene.get("id", ""))
            for ev in scene.get("evidence", []) or []:
                if isinstance(ev, dict):
                    _append(sid, map_id(ev.get("id", "")))

        # evidence_registry 里的首次登记（补 scenes.evidence 未覆盖的条目）
        for ev in state.get("evidence_registry", []) or []:
            if not isinstance(ev, dict):
                continue
            fs = ev.get("first_scene")
            if fs is None:
                continue
            fs_str = str(fs)
            if not fs_str.isdigit():
                continue
            _append(map_id(fs_str), map_id(ev.get("id", "")))

        result[loop_num] = loop_items
    return result


def build_scene_npc_infos(states):
    """构建 {loop_num: {scene_id_str: [npc_info, ...]}} 映射（场景/NPC ID 均为 8-prefix）"""
    result = {}
    for loop_num, state in states.items():
        loop_npcs = {}
        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            sid = map_id(scene.get("id", ""))
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
    """收集所有 state 中出现的证据。返回 [(loop_num, scene_id_or_None, ev), ...]。
    scene_id 和证据 id 在此已映射为 8-prefix；ev 本身保持原 state dict。
    """
    collected = []
    seen_ids = set()

    def _add(loop_num, scene_id, ev):
        if not isinstance(ev, dict):
            return
        raw_eid = ev.get("id")
        if raw_eid is None:
            return
        eid = map_id(raw_eid)
        if eid in seen_ids:
            return
        seen_ids.add(eid)
        collected.append((loop_num, scene_id, ev))

    for loop_num, state in states.items():
        # 1. scenes.[*].evidence
        for scene in state.get("scenes", []) or []:
            if not isinstance(scene, dict):
                continue
            sid = map_id(scene.get("id", ""))
            for ev in scene.get("evidence", []) or []:
                _add(loop_num, sid, ev)
            bs = scene.get("body_search", {})
            if isinstance(bs, dict):
                for ev in bs.get("evidence", []) or []:
                    _add(loop_num, sid, ev)

        # 2. evidence_registry
        for ev in state.get("evidence_registry", []) or []:
            if not isinstance(ev, dict):
                continue
            first_scene = ev.get("first_scene")
            fs_str = str(first_scene) if first_scene is not None else None
            if fs_str and fs_str.isdigit():
                _add(loop_num, map_id(fs_str), ev)
            else:
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


SECTION_TITLE_MAP = {
    "turn_cutscene": "情节转折",
    "suspect_suicide_sequence": "嫌疑人自尽",
    "arrest_cutscene": "逮捕现场",
    "post_expose_dialogue": "指证后对话",
    "post_expose_romance": "指证后·情感戏",
    "post_expose_scene": "指证后剧情",
    "ending_sequence": "终章",
    "phone_call_event": "电话事件",
}


def collect_special_cutscenes(state):
    """收集 state 中的自造剧情段。返回 [{type, title, subtype, location, summary, description}]。
    description 输出完整文本，供 pipeline 显示成剧情卡。
    """
    out = []
    for field in SPECIAL_SECTIONS:
        section = state.get(field)
        if not isinstance(section, dict):
            continue
        entry = {"type": field, "title": SECTION_TITLE_MAP.get(field, field)}
        if section.get("type"):
            entry["subtype"] = section.get("type")
        if section.get("location"):
            entry["location"] = section.get("location")
        desc = section.get("description", "")
        if isinstance(desc, str) and desc.strip():
            text = desc.strip()
            entry["summary"] = text.split("\n")[0][:80]
            entry["description"] = text
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

    # expose 场景（Unit8 = 8-prefix）
    expose_scene_map = {
        1: 8001, 2: 8005, 3: 8008, 4: 8007, 5: 8011, 6: 8014,
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
                evs.append(map_id(e.get("id")))
        rounds.append({"lie": lie, "evidences": evs})

    # scenes 分类
    locked, closed = build_locked_closed(loop_num)
    free_phase = list(build_free_phase(loop_num))  # 新列表副本

    # opening（参考 Unit1 旧版 loop.yaml 用 opening_talks 列表）
    opening_scenes = []
    if opening_data.get("scene_id"):
        opening_scenes.append(map_id(opening_data["scene_id"]))

    # target_name：把 expose.target 标识符转为 NPC 中文名
    expose_target_display_map = {
        "rosa": "Rosa",
        "tommy": "Tommy",
        "vivian": "Vivian",
        "james": "James",
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

        # post_expose_scene / post_expose_romance 的 NPC 对白
        # （emma_002/004/006/008/010 等承接/收尾/感情戏对白）
        for post_key in ("post_expose_scene", "post_expose_romance"):
            post_block = state.get(post_key, {}) or {}
            if not isinstance(post_block, dict):
                continue
            label = "收尾/承接" if post_key == "post_expose_scene" else "感情戏/收尾"
            for npc_key, npc_data in post_block.items():
                if not isinstance(npc_data, dict):
                    continue
                talk_id = npc_data.get("talk", "")
                motive = npc_data.get("motive", "")
                if talk_id and motive:
                    summaries[talk_id] = f"L{loop_num} {label}：{motive[:60]}"

        # turn_cutscene 的 NPC 对白（如 loop4 morrison_003_turn · Part1 情节转折）
        turn_cut = state.get("turn_cutscene", {}) or {}
        if isinstance(turn_cut, dict):
            for npc_key, npc_data in turn_cut.items():
                if not isinstance(npc_data, dict):
                    continue
                talk_id = npc_data.get("talk", "")
                motive = npc_data.get("motive", "")
                if talk_id and motive:
                    summaries[talk_id] = f"L{loop_num} 情节转折：{motive[:60]}"

        # expose 的 target_talk
        expose = state.get("expose", {}) or {}
        target_talk = expose.get("target_talk", "")
        expose_target = expose.get("target", "")
        if target_talk and expose_target:
            summaries[target_talk] = f"L{loop_num} 指证：{expose_target}"

        # Expose 每轮 talkId 摘要（从 Expose JSON 追 Lie 链算 talkId）
        npc_name_map = {1:"rosa",2:"tommy",3:"rosa",4:"vivian",5:"james",6:"morrison"}
        expose_file = os.path.join(AVG_EXPOSE_DIR, f"loop{loop_num}_{npc_name_map[loop_num]}.json")
        if os.path.isfile(expose_file):
            try:
                with open(expose_file, "r", encoding="utf-8") as f:
                    ex_entries = json.loads(fix_json(f.read()))
                if isinstance(ex_entries, dict):
                    ex_entries = [ex_entries]
                first_id = str(ex_entries[0].get("id", "")) if ex_entries else ""
                lies = [e for e in ex_entries if (e.get("script","") or "") == "Lie"]
                round_keys = ("round_1","round_2","round_3","round_4","round_5")
                rounds_data = [expose.get(k) for k in round_keys if isinstance(expose.get(k), dict)]
                prev_break = None
                for idx, lie in enumerate(lies):
                    tid = first_id if idx == 0 else (str(prev_break) if prev_break else first_id)
                    rd = rounds_data[idx] if idx < len(rounds_data) else {}
                    lie_text = (rd.get("lie") or "").strip()[:40]
                    evs = []
                    for e in rd.get("usable_evidence", []) or []:
                        if isinstance(e, dict):
                            nm = e.get("name", "") or f"证据{e.get('id','')}"
                            evs.append(nm)
                    ev_str = "+".join(evs[:3])
                    if ev_str and lie_text:
                        summaries[tid] = f"L{loop_num} R{idx+1}：{ev_str} → 击穿'{lie_text}'"
                    elif lie_text:
                        summaries[tid] = f"L{loop_num} R{idx+1}：击穿'{lie_text}'"
                    pi0 = lie.get("ParameterInt0", 0)
                    prev_break = pi0 if pi0 else None
            except Exception as e:
                print(f"    [WARN] talk_summary Expose 摘要失败 loop{loop_num}: {e}")

    # 补充：loop{N}.yaml 手工维护的场景级 cutscene 对白（不在 state NPC 结构中）
    scene_cutscene_talks = {
        "morrison_house": "L6 Morrison 家：Zack/Emma 伪装记者+助理搜证；中段 Whale 来电（首次声音登场）",
    }
    for k, v in scene_cutscene_talks.items():
        if k not in summaries:
            summaries[k] = v

    doc = {**summaries, "scene_talks": {}}
    path = os.path.join(OUTPUT_DIR, "talk_summary.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


# ============================================================
# JSON 追加（全部处理 Chapter=EPI08）
# ============================================================

def loop_scene_id(loop_num, phys_id):
    """Unit2 风格：{8}{loop}{seq2}——seq2 来自物理 ID 末 2 位（8001→01）"""
    phys_sid = str(phys_id)
    seq2 = phys_sid[-2:] if len(phys_sid) >= 2 else phys_sid.zfill(2)
    return f"8{loop_num}{seq2}"


def append_scenes_to_json(states):
    """追加 SceneConfig.json —— Unit2 风格：每条 = 单一 loop-scene 组合，4 位 ID"""
    data = load_json("SceneConfig.json")
    data = [item for item in data if item.get("Chapter") != CHAPTER]

    per_loop_items = build_scene_item_ids(states)
    per_loop_npcs = build_scene_npc_infos(states)

    # 按 Loop × 物理场景 生成条目（无独立静态条目）
    # sceneId = 8{loop}{seq2}，如 L1 会客室=8101, L3 厨房=8303
    for loop_num in range(1, 7):
        cfg = LOOP_SCENE_CONFIG[loop_num]
        state = states[loop_num]

        active_scenes = list(cfg["unlocked"])
        expose_scene_map = {1: 8001, 2: 8005, 3: 8008, 4: 8007, 5: 8011, 6: 8014}
        esid = expose_scene_map.get(loop_num)
        if esid and esid not in active_scenes:
            active_scenes.append(esid)
        opening_sid = state.get("opening", {}).get("scene_id")
        if opening_sid:
            try:
                mapped = int(map_id(opening_sid))
                if mapped not in active_scenes:
                    active_scenes.append(mapped)
            except (TypeError, ValueError):
                pass

        for phys_id in active_scenes:
            phys_sid = str(phys_id)
            scene_name = SCENE_NAME_MAP.get(phys_sid, f"场景{phys_sid}")
            scene_en = SCENE_EN_MAP.get(phys_sid, "")
            new_sid = loop_scene_id(loop_num, phys_sid)

            entry = {
                "sceneId": new_sid,
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
    # 粗估条目数：每 Loop 平均 4 个场景 × 6 Loop ≈ 24
    print(f"    -> EPI08 单条目模式：每 Loop × 物理场景 一条，共约 {sum(len(cfg['unlocked']) for cfg in LOOP_SCENE_CONFIG.values())} 条")


def append_items_to_json(states):
    """追加 ItemStaticData.json。itemType 动态来自 state.type（item/clue/envir）。"""
    data = load_json("ItemStaticData.json")
    data = [item for item in data if item.get("Chapter") != CHAPTER]

    collected = collect_all_evidence(states)
    items_to_add = []

    for loop_num, scene_id, ev in collected:
        eid = map_id(ev.get("id"))
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

        # 美术资源复用原 1-prefix 命名
        art_eid = _art_item_id(eid)
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
            "folderPath": f"EPI01\\{scene_en}" if scene_en else "EPI01",
            "desSpritePath": f"{type_name}_{art_eid}_big",
            "mapSpritePath": f"{type_name}_{art_eid}",
            "iconPath": f"{type_name}_{art_eid}_icon",
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
    print(f"    -> 添加了 {len(items_to_add)} 个 EPI08 证据条目")


def append_npcs_to_json():
    """追加 NPCStaticData.json（EPI08 部分）"""
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
            did = map_id(doubt.get("id", "") or "")
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
    print(f"    -> 写入 {len(aggregated)} 个 EPI08 疑点条目")


def append_chapter_config(states):
    """追加 ChapterConfig.json（Unit8 loops 用 id '801'-'806'）"""
    data = load_json("ChapterConfig.json")
    # 只清理旧的 Unit8 条目（id 以 '8' 开头且长度为 3），不动 Unit1 的 101-106
    data = [item for item in data if not (
        str(item.get("id", "")).startswith("8") and len(str(item.get("id", ""))) == 3
    )]

    expose_scene_map = {1: 8001, 2: 8005, 3: 8008, 4: 8007, 5: 8011, 6: 8014}
    # Unit8 Expose 对象 NPC ID 映射（8-prefix）
    expose_target_npc_map = {
        1: "803",  # Rosa
        2: "805",  # Tommy
        3: "803",  # Rosa（真击破）
        4: "806",  # Vivian
        5: "807",  # James
        6: "804",  # Morrison
    }

    for loop_num in range(1, 7):
        state = states[loop_num]
        expose = state.get("expose", {}) or {}

        doubts = []
        seen_local = set()
        for doubt in state.get("doubts", []) or []:
            if not isinstance(doubt, dict):
                continue
            did = map_id(doubt.get("id", "") or "")
            if not did or did in seen_local:
                continue
            seen_local.add(did)
            text = doubt.get("text", "") or ""
            condition_str = doubt.get("unlock_condition", "")
            conditions = parse_unlock_condition(condition_str)
            doubts.append({"id": did, "condition": conditions, "text": text})

        # 读对应 loop 的 Expose JSON，按 Lie 顺序算 talkId：
        # R1 talkId = 首条 id；R(N+1) talkId = 前一条 Lie 的 ParameterInt0（break_next）
        per_round_talk_ids = []
        npc_name_map = {1:"rosa",2:"tommy",3:"rosa",4:"vivian",5:"james",6:"morrison"}
        expose_file = os.path.join(AVG_EXPOSE_DIR, f"loop{loop_num}_{npc_name_map[loop_num]}.json")
        if os.path.isfile(expose_file):
            try:
                with open(expose_file, "r", encoding="utf-8") as f:
                    ex_raw = f.read()
                ex_entries = json.loads(fix_json(ex_raw))
                if isinstance(ex_entries, dict):
                    ex_entries = [ex_entries]
                first_id = str(ex_entries[0].get("id", "")) if ex_entries else ""
                lie_list = [e for e in ex_entries if (e.get("script","") or "") == "Lie"]
                prev_break = None
                for li, lie in enumerate(lie_list):
                    if li == 0:
                        per_round_talk_ids.append(first_id)
                    else:
                        per_round_talk_ids.append(str(prev_break) if prev_break else first_id)
                    pi0 = lie.get("ParameterInt0", 0)
                    prev_break = pi0 if pi0 else None
            except Exception as e:
                print(f"    [WARN] 读 {expose_file} 失败，talkId 留空: {e}")

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
                    items.append(map_id(e.get("id")))
            talk_id = per_round_talk_ids[idx-1] if idx-1 < len(per_round_talk_ids) else ""
            exposes.append({
                "id": str(idx),
                "testimony": "",
                "item": items,
                "talkId": talk_id,
            })

        config_id = f"80{loop_num}"  # 801..806
        init_scene_phys = expose_scene_map.get(loop_num, 8001)
        init_scene = loop_scene_id(loop_num, init_scene_phys)  # Unit2 风格：8{loop}{seq2}
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

# 哪些 NPC 有 icon（Unit8 8-prefix）
NPC_HAS_ICON = {"803", "804", "805", "806", "807", "808", "810"}

# Expose 每个 loop 对应的 testimony ID（8-prefix）
# ⚠ 0417 重构版：Rosa/Tommy/Rosa/Vivian/James/Morrison（与旧 Unit1 顺序不同）
LOOP_EXPOSE_TESTIMONY = {
    1: "8031001",  # Rosa (loop1 Expose)
    2: "8052001",  # Tommy (loop2 Expose)
    3: "8033001",  # Rosa (loop3 Expose 真击穿)
    4: "8064001",  # Vivian (loop4 Expose)
    5: "8075002",  # James (loop5 Expose)
    6: "8046001",  # Morrison (loop6 Expose)
}

# Expose sceneId = "8{loop}" (81/82/83/84/85/86)
LOOP_EXPOSE_SCENE_ID = {i: f"8{i}" for i in range(1, 7)}

# Expose 目标 NPC id（8-prefix, 0417 重构版顺序）
LOOP_EXPOSE_NPC = {
    1: "803",  # Rosa
    2: "805",  # Tommy
    3: "803",  # Rosa (第二次指证，真击穿)
    4: "806",  # Vivian
    5: "807",  # James
    6: "804",  # Morrison
}

LOOP_EXPOSE_NPC_INFO_ID = {
    1: "2", 2: "2", 3: "2", 4: "2", 5: "2", 6: "2",
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
        "talkDisplayIndex": str(src.get("talkDisplayIndex", 1 if npc_id == "801" else 2)),
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
    """从 AVG/EPI08/Talk/loop{1-6}/*.json 读取所有 Unit1 对话。

    跳过 _manifest.json；每个文件可能是单条（dict）或数组（list）。
    可选 include_expose=True：同时把 AVG/EPI08/Expose/*.json 也转成 Talk.json 目标格式
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
    """从 AVG/EPI08/Expose/loop{N}_{npc}.json 读取所有指证对话。

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
        # 按 0417 重构版 Expose 对象顺序
        npc_name_map = {
            1: "rosa", 2: "tommy", 3: "rosa",
            4: "vivian", 5: "james", 6: "morrison",
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

    清理策略：删除所有 id 以 8[0-6] 开头的 Unit8 旧条目。
    Unit1/Unit2/Unit3 条目（前缀 1x/2x/3x）保持不动。
    """
    data = load_json("Talk.json")
    before_count = len(data)

    unit8_prefixes = {"80", "81", "82", "83", "84", "85", "86"}
    kept = []
    removed = 0
    for it in data:
        iid = str(it.get("id", ""))
        if iid[:2] in unit8_prefixes:
            removed += 1
        else:
            kept.append(it)

    keep_prefix = {}
    for it in kept:
        p = str(it.get("id", ""))[:2]
        keep_prefix[p] = keep_prefix.get(p, 0) + 1

    print(f"    [Talk.json] 原 {before_count} 条；清理 Unit8 旧 {removed} 条；"
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

    清理策略（仅清理 Unit8 旧条目，不动 Unit1/2/3）：
      - ExposeTalk.json: 删除 id 前缀 8[1-6] 的 Unit8 条目
      - ExposeConfig.json: 删除 sceneId 前缀 "8" 的 Unit8 条目
      - ExposeData.json: 删除 testimony 前缀 "8" 的 Unit8 条目
    """
    # --- ExposeTalk.json ---
    etalk = load_json("ExposeTalk.json")
    before_etalk = len(etalk)
    u8_prefixes = {"81", "82", "83", "84", "85", "86"}
    etalk_kept = [it for it in etalk if str(it.get("id", ""))[:2] not in u8_prefixes]
    print(f"    [ExposeTalk.json] 原 {before_etalk} 条；清理 {before_etalk - len(etalk_kept)} 条；"
          f"追加 {len(expose_talks)} 条")

    # --- ExposeConfig.json ---
    econf = load_json("ExposeConfig.json")
    before_econf = len(econf)
    econf_kept = [it for it in econf if not str(it.get("sceneId", "")).startswith("8")]
    print(f"    [ExposeConfig.json] 原 {before_econf} 条；清理 {before_econf - len(econf_kept)} 条；"
          f"追加 {len(expose_configs)} 条")

    # --- ExposeData.json ---
    edata = load_json("ExposeData.json")
    before_edata = len(edata)
    edata_kept = [it for it in edata if not str(it.get("testimony", "")).startswith("8")]
    others_remaining = len(edata_kept)
    print(f"    [ExposeData.json] 原 {before_edata} 条；清理 {before_edata - len(edata_kept)} 条；"
          f"追加 {len(expose_data)} 条 (其他 Unit 保留 {others_remaining})")

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
    print("Unit8 State -> Preview 数据转换（0417 重构版 8-prefix）")
    print("=" * 50)

    print("\n[1/3] 读取 State 文件...")
    states = load_all_states()
    print(f"  [OK] 已读取 {len(states)} 个 state 文件")

    print("\n[2/3] 生成 Preview YAML 文件...")
    # loop{N}.yaml 手工维护（参考 Unit2 风格：opening 结构化 / scenes 注释 / locked.reason / events）
    # 脚本不再覆盖，除非环境变量 REGEN_LOOP_YAML=1 明确要求重建
    if os.environ.get("REGEN_LOOP_YAML", "").lower() in ("1","true","yes"):
        print("  [!] REGEN_LOOP_YAML=1 —— 重建 loop{N}.yaml（会覆盖手工编辑）")
        for i in range(1, 7):
            generate_loop_yaml(i, states[i])
    else:
        print("  [skip] loop{N}.yaml 不覆盖（手工维护，REGEN_LOOP_YAML=1 可强制重建）")
    generate_locations_yaml()
    generate_talk_summary(states)

    print("\n[3/4] 追加 JSON 数据表（仅处理 Chapter=EPI08）...")
    append_scenes_to_json(states)
    append_items_to_json(states)
    append_npcs_to_json()
    append_doubts_to_json(states)
    append_chapter_config(states)
    testimonies = extract_testimonies_from_state()
    print(f"    -> 从 state 抽取到 {len(testimonies)} 条 Unit8 证词")
    append_testimonies_to_json(testimonies)

    print("\n[4/4] 合并 AVG 对话 JSON (Talk / Expose)...")
    dry_run = os.environ.get("AVG_DRY_RUN", "").lower() in ("1", "true", "yes")
    talks = load_avg_talks()
    e_talks, e_configs, e_data = load_avg_exposes()
    append_avg_talks_to_table(talks, dry_run=dry_run)
    append_avg_exposes_to_table(e_talks, e_configs, e_data, dry_run=dry_run)

    print("\n" + "=" * 50)
    print("Unit8 preview 数据生成完成")
    print(f"YAML 输出: {OUTPUT_DIR}")
    print(f"JSON 更新: {TABLE_DIR}")
    if dry_run:
        print("(AVG_DRY_RUN=1 — AVG 对话部分为预览模式，未写入文件)")
    print("=" * 50)


if __name__ == "__main__":
    main()
