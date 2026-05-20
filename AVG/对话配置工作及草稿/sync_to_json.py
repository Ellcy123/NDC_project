#!/usr/bin/env python3
"""
MD ↔ JSON 同步 / 生成脚本
========================

三种模式：

1. **同步模式**（JSON 已存在）
   将 MD 草稿中修改过的中文对白回写到对应的 JSON 文件。
   只更新：
     - cnAction（情绪/表情）
     - cnWords（对白）
     - cnSpeaker（说话人，极少改动）
     - ParameterStr0-2（分支选项文本，仅 branches 类型）

2. **新建模式**（JSON 不存在）
   根据 MD 条目生成完整 JSON 骨架（含所有必填字段）。
   推断规则：
     - id：从 MD 的 ### xxx 标题取
     - step：按顺序递增
     - speakType：Zack=3 / 其他NPC=2 / 无说话人=4（旁白）
     - IdSpeaker：按中文名查 NPC_SPEAKER_MAP
     - cnSpeaker/cnAction/cnWords：从 MD 取
     - enSpeaker/enAction/enWords：留空
     - next：下一条 id；最后一条 ""
     - script：从 MD 条目的 `get`/`branches`/`expose`/`end` 标注识别
     - ParameterStr/Int：按 script 类型填写
     - videoEpisode/Loop/Id/Scene：从 MD 文件名和 ## Talk: 段落提取

3. **协调模式**（--reconcile）
   适用于 MD 拆分 / 合并 / 重命名场景。处理:
     - 跨文件 ID 迁移（同一 ID 从 emma_002.json 搬到 emma_smallroom_002.json）
     - 幽灵条目清理（JSON 里有但 MD 已删除——默认 warn，加 --purge 才删）
     - 空文件自动删除（迁移后变空的旧文件）
     - _manifest.json 自动重写
   保留已翻译字段（enWords / enAction / enSpeaker）不被清空。

用法:
  python sync_to_json.py Loop2_生成草稿.md              # 默认：自动判断（存在→同步，不存在→新建）
  python sync_to_json.py Loop2_生成草稿.md --dry-run    # 预览
  python sync_to_json.py Loop2_生成草稿.md --new-only   # 只新建，已有 JSON 跳过
  python sync_to_json.py Loop2_生成草稿.md --sync-only  # 只同步，不存在就跳过
  python sync_to_json.py Loop2_生成草稿.md --reconcile  # 协调模式（推荐用于 MD 拆分后）
  python sync_to_json.py Loop2_生成草稿.md --reconcile --purge  # 协调 + 删除幽灵条目
  python sync_to_json.py --all                           # 同步/新建所有 Loop
  python sync_to_json.py Loop2_生成草稿.md --episode EPI01  # 指定章节（默认 EPI01）
"""

import json
import re
import sys
import os
from pathlib import Path

# Windows 终端兼容：强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ============================================================
# 路径配置
# ============================================================

BASE = Path(__file__).parent.parent           # NDC_project/AVG/
MD_DIR = Path(__file__).parent                # 对话配置工作及草稿/
GEN_MD_DIR = MD_DIR / "生成草稿"              # 生成草稿/

# 默认 episode（可用 --episode 覆盖）
DEFAULT_EPISODE = "EPI01"

# ============================================================
# NPC 中文名 → IdSpeaker / enSpeaker 映射
# EPI01 使用 1XX 系列；Unit8（0417 重构版，EPI08）使用 8XX 系列
# 根据 --episode 参数选择映射表
# ============================================================

NPC_SPEAKER_MAP_EPI01 = {
    # 扎克 —— 主角
    "扎克·布伦南":      ("NPC101", "Zack Brennan"),
    "扎克":              ("NPC101", "Zack Brennan"),
    "Zack":              ("NPC101", "Zack Brennan"),
    "Zack Brennan":      ("NPC101", "Zack Brennan"),

    # Emma
    "艾玛·奥马利":       ("NPC102", "Emma O'Malley"),
    "艾玛":              ("NPC102", "Emma O'Malley"),
    "Emma":              ("NPC102", "Emma O'Malley"),
    "Emma O'Malley":     ("NPC102", "Emma O'Malley"),

    # Rosa
    "罗莎":              ("NPC103", "Rosa"),
    "Rosa":              ("NPC103", "Rosa"),

    # Morrison
    "莫里森":            ("NPC104", "Morrison"),
    "Morrison":          ("NPC104", "Morrison"),

    # Tommy
    "汤米":              ("NPC105", "Tommy"),
    "Tommy":             ("NPC105", "Tommy"),

    # Vivian
    "薇薇安":            ("NPC106", "Vivian"),
    "薇薇安·罗丝":       ("NPC106", "Vivian"),
    "薇薇安·罗斯":       ("NPC106", "Vivian"),
    "Vivian":            ("NPC106", "Vivian"),
    "Vivian Rose":       ("NPC106", "Vivian"),

    # Jimmy
    "吉米":              ("NPC107", "Jimmy"),
    "Jimmy":             ("NPC107", "Jimmy"),

    # Anna
    "安娜":              ("NPC108", "Anna"),
    "Anna":              ("NPC108", "Anna"),

    # Mrs. Morrison
    "莫里森太太":        ("NPC110", "Mrs. Morrison"),
    "Mrs. Morrison":     ("NPC110", "Mrs. Morrison"),

    # Whale
    "Whale":             ("NPC111", "Whale"),
    "鲸鱼":              ("NPC111", "Whale"),
}

# Unit8 = Unit1 0417 重构版，NPC 编码 801-811（与 Unit1 旧数据 101-111 隔离）
NPC_SPEAKER_MAP_EPI08 = {
    # Zack 801
    "扎克·布伦南":      ("NPC801", "Zack Brennan"),
    "扎克":              ("NPC801", "Zack Brennan"),
    "Zack":              ("NPC801", "Zack Brennan"),
    "Zack Brennan":      ("NPC801", "Zack Brennan"),

    # Emma 802
    "艾玛·奥马利":       ("NPC802", "Emma O'Malley"),
    "艾玛":              ("NPC802", "Emma O'Malley"),
    "Emma":              ("NPC802", "Emma O'Malley"),
    "Emma O'Malley":     ("NPC802", "Emma O'Malley"),

    # Rosa 803
    "罗莎":              ("NPC803", "Rosa"),
    "罗莎·马丁内斯":     ("NPC803", "Rosa"),
    "Rosa":              ("NPC803", "Rosa"),
    "Rosa Martinez":     ("NPC803", "Rosa"),

    # Morrison 804
    "莫里森":            ("NPC804", "Morrison"),
    "Morrison":          ("NPC804", "Morrison"),

    # Tommy 805
    "汤米":              ("NPC805", "Tommy"),
    "Tommy":             ("NPC805", "Tommy"),

    # Vivian 806
    "薇薇安":            ("NPC806", "Vivian"),
    "薇薇安·罗丝":       ("NPC806", "Vivian"),
    "薇薇安·罗斯":       ("NPC806", "Vivian"),
    "维维安":            ("NPC806", "Vivian"),
    "维维安·罗丝":       ("NPC806", "Vivian"),
    "维维安·罗斯":       ("NPC806", "Vivian"),
    "Vivian":            ("NPC806", "Vivian"),
    "Vivian Rose":       ("NPC806", "Vivian"),

    # James 807（Unit9：昵称 James / 全名 James O'Sullivan，与 EPI01 的 Jimmy 区分）
    "James":             ("NPC807", "James"),
    "James O'Sullivan":  ("NPC807", "James"),
    # MD 草稿中文 speaker 兼容（保留旧的中文称呼，避免 sync 失败）
    "吉米":              ("NPC807", "James"),
    "吉米·奥沙利文":    ("NPC807", "James"),
    "詹姆斯":            ("NPC807", "James"),
    "詹姆斯·奥沙利文":  ("NPC807", "James"),

    # Anna 808
    "安娜":              ("NPC808", "Anna"),
    "Anna":              ("NPC808", "Anna"),

    # Webb 809（死者，偶尔旁白引用）
    "Webb":              ("NPC809", "Webb"),
    "韦伯":              ("NPC809", "Webb"),

    # Mrs. Morrison 810
    "莫里森太太":        ("NPC810", "Mrs. Morrison"),
    "Mrs. Morrison":     ("NPC810", "Mrs. Morrison"),

    # Whale 811
    "Whale":             ("NPC811", "Whale"),
    "鲸鱼":              ("NPC811", "Whale"),
}

# EPI09 = Unit9 正式输出目录（NPC 编码 9XX，与 NPCStaticData EPI09 entries 一致）
NPC_SPEAKER_MAP_EPI09 = {
    # Zack 901
    "扎克·布伦南":      ("NPC901", "Zack"),
    "扎克":              ("NPC901", "Zack"),
    "Zack":              ("NPC901", "Zack"),
    "Zack Brennan":      ("NPC901", "Zack"),

    # Emma 902
    "艾玛·奥马利":       ("NPC902", "Emma"),
    "艾玛":              ("NPC902", "Emma"),
    "Emma":              ("NPC902", "Emma"),
    "Emma O'Malley":     ("NPC902", "Emma"),

    # Rosa 903
    "罗莎":              ("NPC903", "Rosa"),
    "罗莎·马丁内斯":     ("NPC903", "Rosa"),
    "Rosa":              ("NPC903", "Rosa"),
    "Rosa Martinez":     ("NPC903", "Rosa"),

    # Morrison 904
    "莫里森":            ("NPC904", "Morrison"),
    "莫里森侦探":        ("NPC904", "Morrison"),
    "Morrison":          ("NPC904", "Morrison"),

    # Tommy 905
    "汤米":              ("NPC905", "Tommy"),
    "汤米·康纳利":       ("NPC905", "Tommy"),
    "Tommy":             ("NPC905", "Tommy"),

    # Vivian 906
    "薇薇安":            ("NPC906", "Vivian"),
    "薇薇安·罗丝":       ("NPC906", "Vivian"),
    "薇薇安·罗斯":       ("NPC906", "Vivian"),
    "维维安":            ("NPC906", "Vivian"),
    "维维安·罗丝":       ("NPC906", "Vivian"),
    "维维安·罗斯":       ("NPC906", "Vivian"),
    "Vivian":            ("NPC906", "Vivian"),
    "Vivian Rose":       ("NPC906", "Vivian"),

    # James 907
    "James":             ("NPC907", "James"),
    "James O'Sullivan":  ("NPC907", "James"),
    "詹姆斯·奥沙利文":   ("NPC907", "James"),
    "吉米":              ("NPC907", "James"),
    "吉米·奥沙利文":    ("NPC907", "James"),
    "詹姆斯":            ("NPC907", "James"),

    # Anna 908
    "安娜":              ("NPC908", "Anna"),
    "安娜·奥沙利文":     ("NPC908", "Anna"),
    "Anna":              ("NPC908", "Anna"),

    # Whale 909
    "Whale":             ("NPC909", "Whale"),
    "鲸鱼":              ("NPC909", "Whale"),

    # Mrs. Morrison 910
    "莫里森太太":        ("NPC910", "Mrs. Morrison"),
    "Mrs. Morrison":     ("NPC910", "Mrs. Morrison"),
    "莫里森夫人":        ("NPC910", "Mrs. Morrison"),
}

# 当前 episode 激活的映射表——入口函数根据 --episode 设置
NPC_SPEAKER_MAP = NPC_SPEAKER_MAP_EPI01

# Expose 文件对应关系（loop_num → filename）
# 注：新 0417 体系按章节重构，Expose 对象不同；此表是回退默认值
EXPOSE_FILES_EPI01 = {
    1: "loop1_rosa.json",
    2: "loop2_tommy.json",   # 0417 重构后 loop2 指证对象是 Tommy
    3: "loop3_morrison.json",
    4: "loop4_jimmy.json",
    5: "loop5_vivian.json",
    6: "loop6_jimmy.json",
}

EXPOSE_FILES_EPI02 = {
    1: "loop1_morrison.json",
    2: "loop2_leonard.json",
    3: "loop3_moore.json",
    4: "loop4_danny.json",
    5: "loop5_vinnie.json",
    6: "loop6_leonard.json",
}


# ============================================================
# MD 解析
# ============================================================

class MDEntry:
    """从 MD 中解析出的单条对话"""
    def __init__(self):
        self.id = 0
        self.cn_speaker = ""
        self.cn_action = ""
        self.cn_words = ""
        self.script_tag = ""       # 从 ### 行提取的 tag（get/branches/end/Lie/expose 等）
        self.script_tag_target = ""  # 如 `get` → 2001001 中的 2001001
        self.branch_options = []    # [(text, target_id_str), ...]
        self.lie_correct_evidence = []  # Expose Lie 的正确证据列表（EV 前缀）
        self.lie_correct_next = ""      # Expose Lie 正确路径 next
        self.lie_round = 0              # Expose Lie 轮次
        self.source_file = ""       # 对应的 JSON 文件名
        self.location = ""          # 从段落 > 场景：xxx 注释提取
        self.order = 0              # 在文件内的顺序（用于 step）


def _parse_tag_line(tag_str):
    """解析 ### 行的标记部分。
    支持形式：
      `get` → 2001001
      `branches`
      `end`
      `Lie` → 正确证据：2011002 / 陷阱证据：1202 或 1203
    返回 (tag_name, target_str, lie_info_dict)
    """
    tag_str = tag_str.strip()
    tag_name = ""
    target = ""
    lie_info = {}

    # 提取反引号中的 tag 名
    backtick = re.search(r"`([^`]+)`", tag_str)
    if backtick:
        tag_name = backtick.group(1).strip().lower()

    # 提取 → 后的目标（简单情况：get → 1234）
    arrow = re.search(r"→\s*(\d+)", tag_str)
    if arrow:
        target = arrow.group(1)

    # Lie 特殊解析：从 "正确证据：..." 提取
    if tag_name == "lie":
        m_correct = re.search(r"正确证据[:：]\s*([0-9A-Za-z,+\s]+)", tag_str)
        if m_correct:
            evs = re.findall(r"[0-9]+", m_correct.group(1))
            lie_info["correct_evidence"] = evs

    return tag_name, target, lie_info


def _normalize_md_text(text):
    """归一化处理——把 fenced 代码块风格转换为标准 ### xxx / **speaker** [...] / > words 格式。

    支持两种变体：
    1. tommy_001 风格（纯 id+speaker）：
       ```
       id: 205104001
       speaker: Zack（内心观察）
       ```
    2. Loop6 Morrison Expose 风格（ID+speaker+text 等多字段）：
       ```
       ID: 160001
       speaker: Morrison
       text: "台词"
       action: 动作描述（可选）
       keyInfoType: ...  # 忽略
       keyInfoContent: ... # 忽略
       ```
    """

    # ── 变体 2（Loop6 Morrison Expose）：完整 fenced block 带 text/action 字段 ──
    # 注意：先处理变体 2（更具体），再处理变体 1（更宽松）
    pattern_v2 = re.compile(
        r"```\s*\n"
        r"\s*ID:\s*(\d+)\s*\n"              # ID: 160001
        r"\s*speaker:\s*([^\n]+?)\n"        # speaker: Morrison
        r"(?:\s*text:\s*\"?([^\n]*?)\"?\s*\n)?"  # text: "..." (可选)
        r"(?:\s*action:\s*([^\n]*?)\n)?"    # action: ... (可选)
        r"(?:\s*keyInfoType:[^\n]*\n)?"     # keyInfoType: ... (忽略)
        r"(?:\s*keyInfoContent:[^\n]*\n)?"  # keyInfoContent: ... (忽略)
        r"\s*```",
        re.MULTILINE,
    )

    def replace_v2(m):
        entry_id = m.group(1).strip()
        speaker = m.group(2).strip()
        text_line = (m.group(3) or "").strip()
        action = (m.group(4) or "").strip()
        # 清理 text 两端可能残留的引号
        text_line = text_line.strip('"').strip("'")
        result = f"### {entry_id}\n**{speaker}**"
        if action:
            result += f" [{action}]"
        result += "\n"
        if text_line:
            result += f"> {text_line}\n"
        return result

    text = pattern_v2.sub(replace_v2, text)

    # ── 变体 1（tommy_001 风格）：纯 id+speaker（无 text 行） ──
    pattern_v1 = re.compile(
        r"```\s*\n\s*id:\s*(\d+)\s*\n\s*speaker:\s*([^\n]+?)\n\s*```",
        re.MULTILINE,
    )

    def replace_v1(m):
        entry_id = m.group(1).strip()
        speaker_raw = m.group(2).strip()
        action = ""
        speaker = speaker_raw
        pm = re.match(r"^([^（(]+)\s*[（(](.+?)[)）]\s*$", speaker_raw)
        if pm:
            speaker = pm.group(1).strip()
            action = pm.group(2).strip()
        return f"### {entry_id}\n**{speaker}** [{action}]"

    return pattern_v1.sub(replace_v1, text)


def parse_md_file(md_path):
    """解析 MD 文件，返回 {json_filename: [MDEntry, ...]}"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 归一化 tommy 风格的代码块
    text = _normalize_md_text(text)

    lines = text.split("\n")
    result = {}                      # filename → [MDEntry]
    current_file = None
    current_entry = None
    current_location = ""            # 从文件级别的 > 场景：xxx 提取
    in_words = False                 # 是否在读取 > 对白行

    loop_num_hint = None
    m_loop = re.search(r"Loop\s*(\d+)", str(md_path))
    if m_loop:
        loop_num_hint = int(m_loop.group(1))

    # 多行 HTML 注释状态
    in_html_comment = False

    for line in lines:
        # HTML 注释跨行处理：<!-- ... -->
        # 用计数法防嵌套行内注释干扰: 每行 <!-- 增加 depth, --> 减少
        if in_html_comment:
            opens = line.count("<!--")
            closes = line.count("-->")
            # 行内对 (<!--...-->) = opens==closes 不改变深度
            # 行尾真正的关闭: closes > opens
            if closes > opens:
                in_html_comment = False
            continue
        # 单行注释直接跳过；多行注释开启状态
        stripped_line = line.strip()
        if stripped_line.startswith("<!--"):
            opens = line.count("<!--")
            closes = line.count("-->")
            if opens > closes:
                in_html_comment = True
            continue

        # 任何新的 ## 或 # 标题都应关闭当前条目
        if re.match(r"^#{1,3}\s+", line) and not re.match(r"^###\s+\d+", line):
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
                current_entry = None
                in_words = False

        # 检测文件段落标题: ## Talk: xxx.json 或 ## Expose: xxx.json
        file_match = re.match(r"^## (?:Talk|Expose):\s*(\S+\.json)", line)
        if file_match:
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
            current_file = file_match.group(1).strip()
            current_entry = None
            current_location = ""
            in_words = False
            continue

        # 备用形式: ## <scene_name> · Talk · ... → 推断 filename = <scene_name>.json
        alt_talk_match = re.match(r"^##\s+([a-zA-Z][\w]*)\s*[·・]\s*Talk\b", line)
        if alt_talk_match:
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
            current_file = alt_talk_match.group(1).strip() + ".json"
            current_entry = None
            current_location = ""
            in_words = False
            continue

        # 备用形式: ## §N. Expose — <嫌疑人> 指证 ... → 推断 loopN_<嫌疑人>.json
        alt_expose_match = re.match(r"^##\s+(?:§\d+\.?\s*)?Expose\s*[—\-–]+\s*(\S+?)\s*指证", line)
        if alt_expose_match:
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
            suspect = alt_expose_match.group(1).strip()
            # 查映射表把中文名转成英文 key
            speaker_info = _lookup_speaker(suspect)
            if speaker_info:
                _, en_name = speaker_info
                en_key = en_name.split()[0].lower().replace("'", "").replace(".", "")
            else:
                en_key = suspect.lower()
            loop_prefix = f"loop{loop_num_hint}" if loop_num_hint else "loop"
            current_file = f"{loop_prefix}_{en_key}.json"
            current_entry = None
            current_location = ""
            in_words = False
            continue

        # 检测场景注释: > 场景：xxx
        if line.startswith("> 场景"):
            m = re.match(r"^>\s*场景[:：]\s*(.+)", line)
            if m:
                current_location = m.group(1).strip().split("（")[0].split("(")[0].strip()
            continue

        # 检测对话条目标题: ### 209001001 [可选反引号标记]
        entry_match = re.match(r"^###\s+(\d+)(.*)", line)
        if entry_match:
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
            current_entry = MDEntry()
            current_entry.id = int(entry_match.group(1))
            current_entry.source_file = current_file or ""
            current_entry.location = current_location
            current_entry.order = len(result.get(current_file, []))
            # 解析 tag
            tag_tail = entry_match.group(2).strip()
            if tag_tail:
                tag_name, target, lie_info = _parse_tag_line(tag_tail)
                current_entry.script_tag = tag_name
                current_entry.script_tag_target = target
                if tag_name == "lie" and "correct_evidence" in lie_info:
                    current_entry.lie_correct_evidence = lie_info["correct_evidence"]
            in_words = False
            continue

        if current_entry is None:
            continue

        # 检测说话人 + 情绪 —— 支持两种格式：
        # 格式 A: **扎克·布伦南** [情绪描述]   （Loop1-5 主流格式，action 在 ** 外部）
        # 格式 B: **Zack [情绪描述]**            （Loop6 混合格式，action 在 ** 内部）
        # 注意：格式 B 必须优先匹配，否则格式 A 的 non-greedy 会错误地把 "Zack [情绪描述]" 整体当 speaker
        speaker_inline_match = re.match(r"^\*\*([^\[\]]+?)\s*\[(.+?)\]\*\*\s*$", line)
        if speaker_inline_match:
            speaker_name = speaker_inline_match.group(1).strip()
            action = speaker_inline_match.group(2).strip()
            if not current_entry.cn_speaker:
                current_entry.cn_speaker = speaker_name
                current_entry.cn_action = action
            in_words = False
            continue

        # 格式 A（原有）
        speaker_match = re.match(r"^\*\*(.+?)\*\*\s*(?:\[(.*?)\])?\s*$", line)
        if speaker_match:
            speaker_name = speaker_match.group(1).strip()
            action = (speaker_match.group(2) or "").strip()
            # 如果同一条目已有 speaker（多 speaker 合并行场景），忽略
            if not current_entry.cn_speaker:
                current_entry.cn_speaker = speaker_name
                current_entry.cn_action = action
            in_words = False
            continue

        # 检测对白行: > xxx
        if line.startswith(">") :
            content = line[1:].lstrip()

            # 跳过特殊标记行
            if content.startswith("📋 ") or content.startswith("🎯 "):
                continue
            if content.startswith("场景") or content.startswith("场景："):
                continue
            if content.startswith("[WARN]"):
                continue
            # 跳过 > [Loop N...] / > [Scene xxx] 等转场 meta
            if re.match(r"^\[(Loop|Scene|场景|循环|Phase|Round)\s", content):
                continue
            # 跳过 >  / > Quiz / > 答案 / > Source 等标注
            if re.match(r"^(Quiz|答案|Source|Note|注)[（(：:\s]", content):
                continue

            # Expose Lie 出示证据选项（优先于普通 branches）: - ❶ 出示 XXX → `target`（正确：...）
            if current_entry.script_tag == "lie":
                lie_opt_match = re.match(
                    r"^-\s*[❶❷❸]\s*(?:出示|同时出示|仅出示)?\s*(.+?)\s*→\s*`?(\d+)`?\s*(?:[(（](.+?)[)）])?",
                    content,
                )
                if lie_opt_match:
                    opt_text = lie_opt_match.group(1).strip()
                    opt_target = lie_opt_match.group(2).strip()
                    opt_note = (lie_opt_match.group(3) or "").strip()
                    # 正确分支判断：备注含"正确"
                    if "正确" in opt_note:
                        current_entry.lie_correct_next = opt_target
                    current_entry.branch_options.append((opt_text, opt_target))
                    continue

            # 检测分支选项: - ❶ 文本 → `target`
            branch_match = re.match(
                r"^-\s*[❶❷❸➊➋➌①②③\d()()\[\]]+\s*(.+?)\s*→\s*`?(\d+)`?",
                content,
            )
            if branch_match:
                opt_text = branch_match.group(1).strip()
                opt_target = branch_match.group(2).strip()
                current_entry.branch_options.append((opt_text, opt_target))
                continue

            # 跳过 > 开头但是 [出示证据] 等标记行
            if content.startswith("**[") or content.startswith("[出示证据]"):
                in_words = False
                continue

            # 跳过 → 汇合至 xxx 形式的 > 行
            if content.startswith("→"):
                continue

            # 跳过纯标签行: > **出示证据：** / > **核心信息** / > **证据/证词清单** 等
            if re.match(r"^\*\*[^*\n]+\*\*\s*[:：]?\s*$", content):
                in_words = False
                continue

            # 剥 <special>...</special> 包装但保留内部对白
            content = re.sub(r"</?special>", "", content)
            # 剥行内 HTML 注释 <!-- ... -->
            content = re.sub(r"<!--.*?-->", "", content).strip()
            if not content:
                continue

            # 普通对白
            if in_words:
                current_entry.cn_words += "\n" + content
            else:
                current_entry.cn_words = content
                in_words = True
            continue

        # 非 > 开头且非 ### 开头——可能是未加 > 的对白（tommy 代码块展开后的情况）
        stripped = line.strip()
        # 跳过孤立 --> 行（嵌套 html 注释场景：外层多行注释 + 行内注释干扰了 in_html_comment 状态）
        if stripped == "-->" or stripped.startswith("-->"):
            continue
        # 跳过策划标注行: `get: xxx` / `show: xxx` / 📋 ... / 🎯 ... / 信息点统计 / 节拍注释 / keyInfoType
        if stripped.startswith("`") and re.match(r"^`(get|show)[:\s_]", stripped):
            continue
        if stripped.startswith("📋") or stripped.startswith("🎯"):
            continue
        if "信息点统计" in stripped or "核心信息获取小结" in stripped or "节拍注释" in stripped:
            continue
        if "keyInfoType" in stripped or "keyInfoContent" in stripped:
            continue
        if stripped.startswith("<special>") or stripped.startswith("</special>") or stripped == "</special>":
            continue
        # 跳过任意非对白的设计师笔记行 (含明显设计标记词)
        designer_keywords = ["分支汇合节点", "信息隔离", "禁忌检查", "Source / Quiz 标记",
                             "节拍分布", "证词分配", "证据 get 顺序", "get 间隔检查",
                             "post_dialogue_lock", "lie_source", "talkDisplayIndex"]
        if any(kw in stripped for kw in designer_keywords):
            continue
        if current_entry is not None and stripped and not stripped.startswith("<!--") \
                and not stripped.startswith("```") and not stripped.startswith("---") \
                and not stripped.startswith("→") and not stripped.startswith("##") \
                and not stripped.startswith("|") and not stripped.startswith("- ") \
                and not stripped.startswith("**") and not stripped.startswith("> "):
            # 剥 <special>...</special> 包装但保留内部对白
            stripped = re.sub(r"</?special>", "", stripped)
            stripped = re.sub(r"<!--.*?-->", "", stripped).strip()
            if not stripped:
                continue
            # 视为对白的延续（tommy 代码块风格）
            if current_entry.cn_words:
                current_entry.cn_words += "\n" + stripped
            else:
                current_entry.cn_words = stripped
            in_words = True
            continue

        # 空行或其他——关闭当前对白段
        if in_words and stripped == "":
            in_words = False

    # 保存最后一个 entry
    if current_entry and current_file:
        result.setdefault(current_file, []).append(current_entry)

    # 重新编号 order
    for fname, entries in result.items():
        for i, e in enumerate(entries):
            e.order = i

    return result


# ============================================================
# 新建模式：生成 JSON 骨架
# ============================================================

def _lookup_speaker(cn_name):
    """查 NPC 映射。返回 (IdSpeaker, enSpeaker) 或 None。"""
    if not cn_name:
        return None
    # 原名
    if cn_name in NPC_SPEAKER_MAP:
        return NPC_SPEAKER_MAP[cn_name]
    # 去掉空格/标点再试
    clean = cn_name.strip().replace(" ", "")
    if clean in NPC_SPEAKER_MAP:
        return NPC_SPEAKER_MAP[clean]
    # 模糊匹配：主姓氏包含
    for key, val in NPC_SPEAKER_MAP.items():
        if key in cn_name or cn_name in key:
            return val
    return None


def _infer_speak_type(cn_speaker):
    """speakType: 1=NPC独白 / 2=NPC对Zack / 3=Zack对NPC / 4=旁白"""
    if not cn_speaker:
        return 4
    # Zack 说话 → 3
    if _lookup_speaker(cn_speaker) == NPC_SPEAKER_MAP.get("扎克·布伦南"):
        return 3
    # 其他 NPC → 2
    return 2


def _build_entry(md_entry, entries, idx, episode, loop_num, scene_name, is_expose=False, warnings=None):
    """根据 MDEntry 生成 JSON 条目 dict。"""
    if warnings is None:
        warnings = []

    entry_id = md_entry.id
    entry_id_str = str(entry_id)

    # speaker
    cn_speaker = md_entry.cn_speaker or ""
    speaker_info = _lookup_speaker(cn_speaker)
    if speaker_info:
        id_speaker, en_speaker = speaker_info
    else:
        if cn_speaker:
            warnings.append(f"  [WARN][{entry_id}] 未知说话人 '{cn_speaker}'，IdSpeaker 留空")
            id_speaker, en_speaker = "", ""
        else:
            id_speaker, en_speaker = "", ""

    # speakType
    speak_type = _infer_speak_type(cn_speaker) if cn_speaker else 4

    # next
    next_id = ""
    if idx + 1 < len(entries):
        next_id = str(entries[idx + 1].id)
    # 最后一个或 end 标记 → next = ""
    tag = (md_entry.script_tag or "").lower()
    if tag == "end":
        next_id = ""

    # script 归一化
    script = ""
    if tag in ("get", "branches", "end", "expose", "lie"):
        # JSON 里的 script 字段值（小写约定，Lie 在 Expose 里保持首字母大写）
        if is_expose and tag == "lie":
            script = "Lie"
        else:
            script = tag
    elif tag and tag not in ("",):
        # 未知标记也保留
        script = tag

    # ParameterStr / ParameterInt 默认
    p_str = ["", "", ""]
    p_int = [0, 0, 0]

    if tag == "get":
        # 证据 ID：放 ParameterStr0（带 EV 前缀用于证据；证词直接数字）
        target = md_entry.script_tag_target
        if target:
            # 证词 ID 是 7 位数字，证据 ID 是 4 位（1xxx）
            # 按长度推断：7 位证词直接写；4 位证据加 EV 前缀
            if len(target) == 4:
                p_str[0] = f"EV{target}"
            else:
                p_str[0] = target

    elif tag == "branches":
        # 分支选项文本 → ParameterStr；目标 id → ParameterInt
        for i, (opt_text, opt_target) in enumerate(md_entry.branch_options[:3]):
            p_str[i] = opt_text
            try:
                p_int[i] = int(opt_target)
            except (ValueError, TypeError):
                warnings.append(f"  [WARN][{entry_id}] branches 选项 {i} target 非数字: {opt_target}")

    elif is_expose and tag == "lie":
        # Expose Lie 结构
        # ParameterStr0 = 正确证据 EV 列表（逗号分隔）
        if md_entry.lie_correct_evidence:
            p_str[0] = ",".join(f"EV{ev}" for ev in md_entry.lie_correct_evidence)
        # ParameterInt0 = 正确路径 next（整数）
        if md_entry.lie_correct_next:
            try:
                p_int[0] = int(md_entry.lie_correct_next)
            except (ValueError, TypeError):
                pass
        # ParameterInt1 = 轮次（从文件内 Lie 计数推断）
        if md_entry.lie_round:
            p_int[1] = md_entry.lie_round

    # Location
    location = md_entry.location or ""

    # 构造 entry（Expose 和 Talk 略有字段差异）
    entry = {
        "id": entry_id,
        "step": idx + 1,
        "speakType": speak_type,
        "waitTime": 0,
        "IdSpeaker": id_speaker,
        "cnSpeaker": cn_speaker,
        "enSpeaker": en_speaker,
    }

    # Expose 特有：talkDisplayIndex (1=Zack/左 / 2=NPC/右)
    if is_expose:
        if id_speaker == "NPC101":
            entry["talkDisplayIndex"] = 1
        elif id_speaker:
            entry["talkDisplayIndex"] = 2
        else:
            entry["talkDisplayIndex"] = 1

    entry.update({
        "Location": location,
        "cnAction": md_entry.cn_action or "",
        "cnWords": md_entry.cn_words or "",
        "enAction": "",
        "enWords": "",
        "next": next_id,
        "script": script,
        "ParameterStr0": p_str[0],
        "ParameterStr1": p_str[1],
        "ParameterStr2": p_str[2],
        "ParameterInt0": p_int[0],
        "ParameterInt1": p_int[1],
        "ParameterInt2": p_int[2],
        "videoEpisode": episode,
        "videoLoop": f"loop{loop_num}",
        "videoId": entry_id_str,
        "videoScene": scene_name,
    })

    return entry


def new_json(json_path, md_entries, episode, loop_num, is_expose=False, dry_run=False):
    """当 json_path 不存在时，根据 MD 条目生成完整 JSON 骨架。"""
    scene_name = json_path.stem  # 文件名去掉 .json
    warnings = []

    # Expose Lie 轮次计数
    if is_expose:
        lie_count = 0
        for e in md_entries:
            if (e.script_tag or "").lower() == "lie":
                lie_count += 1
                e.lie_round = lie_count

    json_list = []
    for idx, md_entry in enumerate(md_entries):
        entry = _build_entry(
            md_entry, md_entries, idx,
            episode=episode,
            loop_num=loop_num,
            scene_name=scene_name,
            is_expose=is_expose,
            warnings=warnings,
        )
        json_list.append(entry)

    # Post-process: 把 branches 中 next 清空（branches 的走向由 ParameterInt0-2 决定）
    for entry in json_list:
        if entry["script"] == "branches":
            entry["next"] = ""
        if entry["script"] == "Lie":
            # Lie 的 next 留给 ParameterInt0（正确路径）；主 next 字段保留为下一条 id 以供默认流转
            pass

    if not dry_run:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_list, f, ensure_ascii=False, indent=2)

    return json_list, warnings


# ============================================================
# 同步模式：回写 MD 修改到 JSON
# ============================================================

def sync_entries(json_path, md_entries, dry_run=False, force_clear=False):
    """将 MD 中的对白同步到 JSON 文件。返回 (changes_list, modified_bool)
    force_clear=True 时：若 MD 中 cn_words 为空而 JSON 中非空，也会清空 JSON（危险，慎用）。"""
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    id_to_idx = {}
    for idx, entry in enumerate(json_data):
        id_to_idx[entry["id"]] = idx

    changes = []
    modified = False

    for md_entry in md_entries:
        idx = id_to_idx.get(md_entry.id)
        if idx is None:
            changes.append(f"  [WARN]ID {md_entry.id} 在 JSON 中不存在，跳过")
            continue

        je = json_data[idx]
        entry_changes = []

        cn_words_diff = md_entry.cn_words != je.get("cnWords", "")
        if cn_words_diff and (md_entry.cn_words or force_clear):
            old = je.get("cnWords", "")
            entry_changes.append(f"    cnWords: {_truncate(old)} → {_truncate(md_entry.cn_words) if md_entry.cn_words else '(清空)'}")
            if not dry_run:
                je["cnWords"] = md_entry.cn_words

        if md_entry.cn_action != je.get("cnAction", ""):
            old = je.get("cnAction", "")
            entry_changes.append(f"    cnAction: {_truncate(old)} → {_truncate(md_entry.cn_action)}")
            if not dry_run:
                je["cnAction"] = md_entry.cn_action

        if md_entry.cn_speaker and md_entry.cn_speaker != je.get("cnSpeaker", ""):
            old = je.get("cnSpeaker", "")
            entry_changes.append(f"    cnSpeaker: {old} → {md_entry.cn_speaker}")
            if not dry_run:
                je["cnSpeaker"] = md_entry.cn_speaker

        # Lie 节点的 ParameterStr0 由 lie_correct_evidence 控制（EV{id} 格式），
        # 不应被 branch_options 的 opt_text 覆盖（sync 一致性 bug 修复）
        if md_entry.branch_options and (md_entry.script_tag or "").lower() != "lie":
            for i, (opt_text, _) in enumerate(md_entry.branch_options):
                if i > 2:
                    break
                key = f"ParameterStr{i}"
                if opt_text != je.get(key, ""):
                    old = je.get(key, "")
                    entry_changes.append(f"    {key}: {old} → {opt_text}")
                    if not dry_run:
                        je[key] = opt_text

        if entry_changes:
            changes.append(f"  [{md_entry.id}]")
            changes.extend(entry_changes)
            modified = True

    if modified and not dry_run:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    return changes, modified


def _truncate(s, maxlen=50):
    s = s.replace("\n", "\\n")
    if len(s) > maxlen:
        return s[:maxlen] + "..."
    return s


# ============================================================
# 协调模式：跨文件迁移 + 幽灵清理 + manifest 重写
# ============================================================

def _merge_md_into_json_entry(existing, md_entry, all_entries_in_bucket, idx_in_bucket,
                              fname, episode, loop_num, is_expose):
    """以现有 JSON 条目为底，把 MD 的最新内容覆盖进去。

    保留：enWords / enAction / enSpeaker（人工译文）
    覆盖：cnSpeaker / cnAction / cnWords / step / next / videoScene / videoLoop / videoEpisode /
          script / IdSpeaker / speakType / branches Param* / Lie Param* / get Param*
    """
    ent = dict(existing)
    md_e = md_entry

    if md_e.cn_speaker:
        ent["cnSpeaker"] = md_e.cn_speaker
        speaker_info = _lookup_speaker(md_e.cn_speaker)
        if speaker_info:
            ent["IdSpeaker"], ent["enSpeaker"] = speaker_info
        ent["speakType"] = _infer_speak_type(md_e.cn_speaker)
    ent["cnAction"] = md_e.cn_action or ""
    ent["cnWords"] = md_e.cn_words or ""

    # step / next
    ent["step"] = idx_in_bucket + 1
    if idx_in_bucket + 1 < len(all_entries_in_bucket):
        ent["next"] = str(all_entries_in_bucket[idx_in_bucket + 1].id)
    else:
        ent["next"] = ""

    tag = (md_e.script_tag or "").lower()
    if tag == "end":
        ent["next"] = ""

    # script 字段
    if tag in ("get", "branches", "end", "expose", "lie"):
        ent["script"] = "Lie" if (is_expose and tag == "lie") else tag
    elif tag:
        ent["script"] = tag
    else:
        ent["script"] = ""

    # video* 字段（迁移后跟新文件名走）
    ent["videoEpisode"] = episode
    ent["videoLoop"] = f"loop{loop_num}"
    ent["videoScene"] = Path(fname).stem
    ent["videoId"] = str(md_e.id)

    # Location（如果 MD 有给）
    if md_e.location:
        ent["Location"] = md_e.location

    # 重置 Parameter 字段（避免老的 branches 数据残留），再按 tag 填新值
    p_str = ["", "", ""]
    p_int = [0, 0, 0]

    if tag == "get":
        target = md_e.script_tag_target
        if target:
            if len(target) == 4:
                p_str[0] = f"EV{target}"
            else:
                p_str[0] = target
    elif tag == "branches":
        for i, (opt_text, opt_target) in enumerate(md_e.branch_options[:3]):
            p_str[i] = opt_text
            try:
                p_int[i] = int(opt_target)
            except (ValueError, TypeError):
                pass
        # branches 主 next 由 ParameterInt 决定，主字段清空
        ent["next"] = ""
    elif is_expose and tag == "lie":
        if md_e.lie_correct_evidence:
            p_str[0] = ",".join(f"EV{ev}" for ev in md_e.lie_correct_evidence)
        if md_e.lie_correct_next:
            try:
                p_int[0] = int(md_e.lie_correct_next)
            except (ValueError, TypeError):
                pass
        if md_e.lie_round:
            p_int[1] = md_e.lie_round

    ent["ParameterStr0"] = p_str[0]
    ent["ParameterStr1"] = p_str[1]
    ent["ParameterStr2"] = p_str[2]
    ent["ParameterInt0"] = p_int[0]
    ent["ParameterInt1"] = p_int[1]
    ent["ParameterInt2"] = p_int[2]

    return ent


def _reconcile_dir(loop_dir, buckets, episode, loop_num, dry_run, purge, is_expose,
                   scope_filter=None):
    """协调一个目录（loopN/ 或 Expose/）的 JSON 与 MD bucket。

    scope_filter: 可选 callable(filename)->bool，控制扫描时哪些文件算"在作用域内"。
                  Talk 默认 None（loopN/ 目录本身已天然按 Loop 隔离）。
                  Expose 应传 lambda f: f.lower().startswith(f"loop{loop_num}_")
                  避免误把别的 Loop 的 Expose 文件标成 stale。
    """

    # ── Step 1: MD 期望的 ID → 文件 / Entry 映射 ──
    md_id_to_file = {}
    md_id_to_entry = {}
    md_file_to_entries = {}
    for fname, entries in buckets.items():
        md_file_to_entries[fname] = entries
        for e in entries:
            md_id_to_file[e.id] = fname
            md_id_to_entry[e.id] = e

    # ── Step 2: 扫描目录里所有现存 JSON（按作用域过滤）──
    json_id_to_file = {}
    json_id_to_entry = {}
    json_file_entries = {}

    if loop_dir.exists():
        for jf in sorted(loop_dir.glob("*.json")):
            if jf.name == "_manifest.json":
                continue
            if scope_filter and not scope_filter(jf.name):
                continue
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            except Exception as ex:
                print(f"  [WARN] 无法读取 {jf.name}: {ex}")
                continue
            json_file_entries[jf.name] = entries
            for ent in entries:
                eid = ent.get("id")
                if eid is None:
                    continue
                json_id_to_file[eid] = jf.name
                json_id_to_entry[eid] = ent

    # ── Step 3: 行动分类 ──
    new_count = 0
    update_count = 0
    migrate_count = 0
    migrations = []  # (id, from, to)
    for md_id, target_file in md_id_to_file.items():
        current_file = json_id_to_file.get(md_id)
        if current_file is None:
            new_count += 1
        elif current_file == target_file:
            update_count += 1
        else:
            migrate_count += 1
            migrations.append((md_id, current_file, target_file))

    stale_actions = [(jid, jfile) for jid, jfile in json_id_to_file.items()
                     if jid not in md_id_to_file]

    print(f"\n[Plan · {loop_dir.name}] new={new_count}, update={update_count}, "
          f"migrate={migrate_count}, stale={len(stale_actions)}")

    if migrations:
        print(f"\n[Migrate]")
        for mid, mfrom, mto in sorted(migrations)[:30]:
            print(f"  {mid}: {mfrom} → {mto}")
        if len(migrations) > 30:
            print(f"  ... +{len(migrations) - 30} more")

    if stale_actions:
        marker = "(--purge 已开启，将删除)" if purge else "(默认保留，加 --purge 才删)"
        print(f"\n[Stale] {marker}")
        for sid, sfile in stale_actions[:20]:
            print(f"  {sid} in {sfile}")
        if len(stale_actions) > 20:
            print(f"  ... +{len(stale_actions) - 20} more")

    # ── Step 4: 构建输出 ──
    output_files = {}

    for fname, entries in md_file_to_entries.items():
        # Expose Lie 轮次
        if is_expose:
            lie_count = 0
            for e in entries:
                if (e.script_tag or "").lower() == "lie":
                    lie_count += 1
                    e.lie_round = lie_count

        out_list = []
        warnings = []
        for idx, md_e in enumerate(entries):
            existing = json_id_to_entry.get(md_e.id)
            if existing:
                ent = _merge_md_into_json_entry(
                    existing, md_e, entries, idx, fname,
                    episode, loop_num, is_expose,
                )
            else:
                ent = _build_entry(
                    md_e, entries, idx,
                    episode=episode,
                    loop_num=loop_num,
                    scene_name=Path(fname).stem,
                    is_expose=is_expose,
                    warnings=warnings,
                )
                if ent.get("script") == "branches":
                    ent["next"] = ""
            out_list.append(ent)
        output_files[fname] = out_list
        for w in warnings:
            print(w)

    # ── Step 5: 处理幽灵条目 ──
    if not purge and stale_actions:
        # 按原文件保留幽灵条目
        for jfile, original_entries in json_file_entries.items():
            for orig in original_entries:
                eid = orig.get("id")
                if eid in md_id_to_file:
                    continue
                output_files.setdefault(jfile, []).append(orig)

    # ── Step 6: 写文件 ──
    for fname, entries in sorted(output_files.items()):
        if not entries:
            continue
        json_path = loop_dir / fname
        if not dry_run:
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
        tag = "WRITE" if not dry_run else "PLAN"
        print(f"  [{tag}] {fname}: {len(entries)} 条")

    # ── Step 7: 删除空文件（迁移后变空的旧文件）──
    # 仅考虑作用域内的文件——避免误删别的 Loop 的文件（如 Expose 共享目录）
    if loop_dir.exists():
        for jf in sorted(loop_dir.glob("*.json")):
            if jf.name == "_manifest.json":
                continue
            if scope_filter and not scope_filter(jf.name):
                continue
            still_has_content = jf.name in output_files and output_files[jf.name]
            if not still_has_content:
                if not dry_run:
                    jf.unlink()
                tag = "DELETE" if not dry_run else "PLAN-DELETE"
                print(f"  [{tag}] {jf.name}（已迁空 / 已废弃）")

    # ── Step 8: 重写 manifest ──
    # 写入后扫描目录得到真实最终列表；干跑下手工模拟一次"写入后的目录状态"
    if dry_run:
        final_files_set = set()
        if loop_dir.exists():
            for jf in loop_dir.glob("*.json"):
                if jf.name == "_manifest.json":
                    continue
                in_scope = (scope_filter is None) or scope_filter(jf.name)
                if in_scope:
                    # 作用域内：是否会被删/留要看 output_files
                    if jf.name in output_files and output_files[jf.name]:
                        final_files_set.add(jf.name)
                else:
                    # 作用域外：不动
                    final_files_set.add(jf.name)
        # 新写入的文件
        for fname, entries in output_files.items():
            if entries:
                final_files_set.add(fname)
        final_files = sorted(final_files_set)
    else:
        final_files = sorted(
            jf.name for jf in loop_dir.glob("*.json")
            if jf.name != "_manifest.json"
        )
    manifest_path = loop_dir / "_manifest.json"
    if not dry_run:
        loop_dir.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(final_files, f, ensure_ascii=False, indent=2)
    tag = "WRITE" if not dry_run else "PLAN"
    print(f"  [{tag}] _manifest.json: {len(final_files)} 个文件")


def reconcile_md_to_loop_dir(md_path, episode, dry_run=False, purge=False):
    """协调模式入口：处理跨文件迁移、幽灵清理、manifest 重写。"""
    md_filename = os.path.basename(md_path)
    loop_num = get_loop_num_from_md(md_filename)
    if loop_num is None:
        print(f"[ERR] 无法从文件名 {md_filename} 提取 Loop 号")
        return

    parsed = parse_md_file(md_path)
    if not parsed:
        print("  没有解析到任何对话条目")
        return

    prefix = "[预览] " if dry_run else ""
    print(f"\n{prefix}Reconcile {md_filename} (Loop {loop_num}, Episode {episode})"
          f"{' --purge' if purge else ''}")
    print("=" * 70)

    # 分离 Talk 和 Expose
    talk_buckets = {}
    expose_buckets = {}
    for fname, entries in parsed.items():
        _, is_expose = resolve_json_path(fname, loop_num, episode)
        if is_expose:
            expose_buckets[fname] = entries
        else:
            talk_buckets[fname] = entries

    if talk_buckets:
        talk_dir = BASE / episode / "Talk" / f"loop{loop_num}"
        _reconcile_dir(talk_dir, talk_buckets, episode, loop_num,
                       dry_run, purge, is_expose=False)

    if expose_buckets:
        expose_dir = BASE / episode / "Expose"
        # Expose/ 是共享目录，按 LoopN_ 前缀过滤
        scope = lambda n: n.lower().startswith(f"loop{loop_num}_")
        _reconcile_dir(expose_dir, expose_buckets, episode, loop_num,
                       dry_run, purge, is_expose=True, scope_filter=scope)


# ============================================================
# 路径解析
# ============================================================

def get_loop_num_from_md(md_filename):
    """从 MD 文件名提取 Loop 号，支持 Loop2_对话草稿.md / Loop2_生成草稿.md 等。"""
    m = re.match(r"Loop(\d+)", md_filename)
    return int(m.group(1)) if m else None


def resolve_md_path(arg):
    """支持相对/绝对/只给文件名三种形式，自动在 MD_DIR 和 GEN_MD_DIR 搜索。"""
    p = Path(arg)
    if p.is_absolute() and p.exists():
        return p
    # 命令行给的 "生成草稿/Loop2_..." 相对路径
    rel1 = MD_DIR / arg
    if rel1.exists():
        return rel1
    # 只给文件名
    base = os.path.basename(arg)
    candidates = [
        MD_DIR / base,
        GEN_MD_DIR / base,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def resolve_json_path(filename, loop_num, episode):
    """根据 JSON 文件名、loop、episode 定位绝对路径（无论是否存在）。"""
    talk_dir = BASE / episode / "Talk"
    expose_dir = BASE / episode / "Expose"

    # Expose 文件：开头 loopN_ 或 _expose 结尾（大小写不敏感，兼容 Loop1_rosa.json）
    fn_lower = filename.lower()
    is_expose = (
        fn_lower.startswith("loop") and "_" in filename
    ) or fn_lower.endswith("_expose.json")

    if is_expose:
        return expose_dir / filename, True

    return talk_dir / f"loop{loop_num}" / filename, False


# ============================================================
# 主流程
# ============================================================

def process_single_md(md_path, episode, dry_run=False, mode="auto", force_clear=False):
    """处理单个 MD 文件。mode: auto / new-only / sync-only"""
    md_filename = os.path.basename(md_path)
    loop_num = get_loop_num_from_md(md_filename)
    if loop_num is None:
        print(f"[ERR] 无法从文件名 {md_filename} 提取 Loop 号")
        return

    prefix = "[预览] " if dry_run else ""
    mode_tag = {"auto": "AUTO", "new-only": "NEW-ONLY", "sync-only": "SYNC-ONLY"}[mode]
    print(f"\n{prefix}处理 {md_filename} (Loop {loop_num}, Episode {episode}, mode={mode_tag})")
    print("=" * 70)

    parsed = parse_md_file(md_path)
    if not parsed:
        print("  没有解析到任何对话条目")
        return

    total_synced = 0
    total_created = 0
    total_skipped = 0
    total_warnings = 0

    for filename, md_entries in parsed.items():
        if not md_entries:
            continue

        json_path, is_expose = resolve_json_path(filename, loop_num, episode)
        exists = json_path.exists()

        # 模式策略
        action = None
        if exists:
            if mode == "new-only":
                action = "skip-exists"
            else:
                action = "sync"
        else:
            if mode == "sync-only":
                action = "skip-missing"
            else:
                action = "new"

        print(f"\n[File] {filename}  [{len(md_entries)} 条]")
        print(f"   → {json_path.relative_to(BASE.parent)}" if json_path.is_relative_to(BASE.parent) else f"   → {json_path}")

        if action == "skip-exists":
            print(f"   [SKIP] 已存在，--new-only 跳过")
            total_skipped += 1
            continue

        if action == "skip-missing":
            print(f"   [SKIP] 不存在，--sync-only 跳过")
            total_skipped += 1
            continue

        if action == "sync":
            changes, modified = sync_entries(json_path, md_entries, dry_run, force_clear=force_clear)
            if changes:
                for line in changes:
                    print(line)
                if modified:
                    total_synced += 1
            else:
                print("   [OK] 无变更")
            continue

        if action == "new":
            # 新建模式
            json_list, warnings = new_json(
                json_path, md_entries,
                episode=episode,
                loop_num=loop_num,
                is_expose=is_expose,
                dry_run=dry_run,
            )
            if dry_run:
                print(f"   [NEW] [预览] 将生成 {len(json_list)} 条 JSON 记录")
            else:
                print(f"   [NEW] 已生成 {len(json_list)} 条 JSON 记录")
            for w in warnings:
                print(w)
            total_warnings += len(warnings)
            total_created += 1
            continue

    print(f"\n{'─' * 40}")
    verb = "预览" if dry_run else "执行"
    print(f"{verb}完成: 同步 {total_synced} 个文件 · 新建 {total_created} 个文件 · 跳过 {total_skipped} 个文件 · 警告 {total_warnings}")


def main():
    args = sys.argv[1:]

    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    force_clear = "--force-clear" in args
    args = [a for a in args if a != "--force-clear"]

    reconcile = "--reconcile" in args
    args = [a for a in args if a != "--reconcile"]

    purge = "--purge" in args
    args = [a for a in args if a != "--purge"]

    mode = "auto"
    if "--new-only" in args:
        mode = "new-only"
        args = [a for a in args if a != "--new-only"]
    if "--sync-only" in args:
        mode = "sync-only"
        args = [a for a in args if a != "--sync-only"]

    # --episode EPIxx
    episode = DEFAULT_EPISODE
    if "--episode" in args:
        idx = args.index("--episode")
        if idx + 1 < len(args):
            episode = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    # 根据 episode 切换 NPC 映射表
    # EPI08 = Unit1 0417 重构版（8XX 编码，已废弃但保留）
    # EPI09 = Unit9 正式输出目录（沿用 8XX 编码，复用 EPI08 映射）
    global NPC_SPEAKER_MAP
    ep_upper = episode.upper()
    if ep_upper == "EPI08":
        NPC_SPEAKER_MAP = NPC_SPEAKER_MAP_EPI08
        print(f"[INFO] 使用 EPI08 NPC 映射表（8XX 编码）")
    elif ep_upper == "EPI09":
        NPC_SPEAKER_MAP = NPC_SPEAKER_MAP_EPI09
        print(f"[INFO] 使用 EPI09 NPC 映射表（Unit9，沿用 8XX 编码）")
    else:
        NPC_SPEAKER_MAP = NPC_SPEAKER_MAP_EPI01

    if "--all" in args:
        # 依次处理两个目录下的 Loop{1-6}_*.md
        any_found = False
        for loop_num in range(1, 7):
            for candidates in [
                MD_DIR / f"Loop{loop_num}_对话草稿.md",
                GEN_MD_DIR / f"Loop{loop_num}_生成草稿.md",
            ]:
                if candidates.exists():
                    if reconcile:
                        reconcile_md_to_loop_dir(candidates, episode, dry_run=dry_run, purge=purge)
                    else:
                        process_single_md(candidates, episode, dry_run, mode, force_clear=force_clear)
                    any_found = True
        if not any_found:
            print("[WARN]未找到任何 Loop{1-6}_*.md 文件")
        return

    if not args:
        print(__doc__)
        return

    for arg in args:
        md_path = resolve_md_path(arg)
        if md_path is None:
            print(f"[ERR] 文件不存在: {arg}（已搜索 {MD_DIR} 和 {GEN_MD_DIR}）")
            continue
        if reconcile:
            reconcile_md_to_loop_dir(md_path, episode, dry_run=dry_run, purge=purge)
        else:
            process_single_md(md_path, episode, dry_run, mode, force_clear=force_clear)


if __name__ == "__main__":
    main()
