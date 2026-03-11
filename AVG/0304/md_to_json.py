#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
MD → JSON 对话转换脚本
将 0304/对话草稿/ 目录下的 MD 文件转换为 EPI02 格式的 JSON 文件。

功能:
1. 解析 MD 对话格式（headers, speakers, branches, get, Lie, end）
2. 重编号带字母后缀的 ID（如 038a → 纯数字），同步更新 MD 源文件
3. 计算 next 字段链
4. 输出简化 JSON（与 EPI02 现有格式一致）
5. 更新 _manifest.json

用法:
  python md_to_json.py                # 转换全部
  python md_to_json.py --dry-run      # 预览，不写文件
  python md_to_json.py --loop 1       # 只转换 Loop1
"""

import json
import re
import sys
from pathlib import Path
from collections import OrderedDict

# ─── 路径配置 ───
BASE = Path(__file__).parent.parent  # AVG/
DRAFT_DIR = Path(__file__).parent / "对话草稿"
TALK_DIR = BASE / "EPI02" / "Talk"
EXPOSE_DIR = BASE / "EPI02" / "Expose"

# ─── Speaker 名称映射 ───
SPEAKER_MAP = {
    "扎克": "扎克·布伦南",
    "艾玛": "艾玛·奥马利",
    "莫里森": "莫里森",
    "莱昂纳德": "莱昂纳德·罗斯",
    "摩尔": "哈罗德·摩尔",
    "丹尼": "丹尼·科瓦尔斯基",
    "文尼": "维尼·莫雷蒂",
    "维尼": "维尼·莫雷蒂",
    "罗丝": "罗斯·马丁内斯",
    "罗斯": "罗斯·马丁内斯",
    "托尼": "托尼",
    "奥哈拉太太": "莎拉·奥哈拉",
    "米基": "米奇·麦克奈尔",
    "米奇": "米奇·麦克奈尔",
    "玛格丽特": "玛格丽特",
    "旁白": "旁白",
    "医生": "医生",
}


class DialogueEntry:
    """一条对话数据"""
    def __init__(self):
        self.id_raw = ""        # "210001038a" — 原始 ID（含字母后缀）
        self.id_num = 0         # 最终纯数字 ID
        self.speaker_short = "" # "扎克"
        self.speaker_full = ""  # "扎克·布伦南"
        self.emotion = ""       # "冷静"
        self.words = ""         # 对白文本
        self.script = ""        # branches / get / end / Lie / ""
        self.get_target = 0     # get 的 item/testimony ID
        self.lie_target_raw = ""  # Lie 成功跳转目标（原始）
        self.lie_evidences = ""   # Lie 可用证据列表 "2101,2102"
        self.branch_options = []  # [(text, target_raw), ...]
        self.convergence_raw = "" # 汇合目标（原始）
        self.line_num = 0       # MD 文件中的行号


def parse_md_file(filepath):
    """解析 MD 文件，返回 {json_filename: [DialogueEntry]}"""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    sections = OrderedDict()  # filename → [DialogueEntry]
    current_file = None
    current_entry = None
    in_words = False
    in_comment = False

    for i, line in enumerate(lines, 1):
        # 跳过 HTML 注释
        if "<!--" in line and "-->" in line:
            continue
        if "<!--" in line:
            in_comment = True
            continue
        if "-->" in line:
            in_comment = False
            continue
        if in_comment:
            continue

        # 文件段落: ## Talk: xxx.json 或 ## Expose: xxx.json
        file_match = re.match(r"^## (?:Talk|Expose):\s*(.+\.json)", line)
        if file_match:
            if current_entry and current_file:
                sections.setdefault(current_file, []).append(current_entry)
            current_file = file_match.group(1)
            current_entry = None
            in_words = False
            continue

        # Phase/section 标题（如 "## Phase 1：..." — 非文件标题）
        if re.match(r"^## ", line) and not file_match:
            continue

        # 小标题（如 "#### ❶ 正确路径"）、分隔线、标签行
        if re.match(r"^#{3,4}\s+[^0-9]", line) or line.strip() == "---":
            in_words = False
            continue
        if re.match(r"^\*\*[❶❷❸]", line):
            in_words = False
            continue

        # 对话条目: ### 209001001 [optional tags]
        entry_match = re.match(r"^### (\d+[a-z]?)\s*(.*)", line)
        if entry_match:
            if current_entry and current_file:
                sections.setdefault(current_file, []).append(current_entry)

            current_entry = DialogueEntry()
            current_entry.id_raw = entry_match.group(1)
            current_entry.line_num = i
            tag_str = entry_match.group(2).strip()

            # 解析标签
            if "`branches`" in tag_str:
                current_entry.script = "branches"
            elif "`end`" in tag_str:
                current_entry.script = "end"
            elif "`get`" in tag_str:
                current_entry.script = "get"
                get_match = re.search(r"`get`\s*→\s*(\d+)", tag_str)
                if get_match:
                    current_entry.get_target = int(get_match.group(1))
            elif "`Lie`" in tag_str:
                current_entry.script = "Lie"
                lie_match = re.search(r"`(\d+[a-z]?)`", tag_str)
                if lie_match:
                    current_entry.lie_target_raw = lie_match.group(1)

            in_words = False
            continue

        if current_entry is None:
            continue

        # 说话人: **Name** [emotion]
        speaker_match = re.match(r"^\*\*(.+?)\*\*\s*(?:\[(.+?)\])?", line)
        if speaker_match:
            name = speaker_match.group(1).strip()
            current_entry.speaker_short = name
            current_entry.speaker_full = SPEAKER_MAP.get(name, name)
            current_entry.emotion = (speaker_match.group(2) or "").strip()
            in_words = False
            continue

        # 对白行: > xxx
        if line.startswith("> "):
            content = line[2:]

            # 跳过标记行
            if content.startswith("📋 ") or content.startswith("🎯 "):
                # 但从 🎯 行提取 Lie 证据列表
                if content.startswith("🎯 ") and current_entry.script == "Lie":
                    # 提取所有4-7位数字ID
                    ids = re.findall(r'\b(\d{4,7})\b', content)
                    current_entry.lie_evidences = ",".join(ids)
                continue
            if content.startswith("场景：") or content.startswith("Scene:"):
                continue

            # 分支选项: > - ❶ text → `target`
            branch_match = re.match(
                r"^- [❶❷❸④⑤\d\.]\s*(.+?)\s*→\s*`(\d+[a-z]?)`", content
            )
            if branch_match:
                opt_text = branch_match.group(1).strip()
                opt_target = branch_match.group(2)
                current_entry.branch_options.append((opt_text, opt_target))
                continue

            # 普通对白（跳过仅有 "——" 或 "……" 的占位行在 branches 中）
            if current_entry.script == "branches" and content.strip() in ("——", "……", "…"):
                continue

            if in_words:
                current_entry.words += "\n" + content
            else:
                current_entry.words = content
                in_words = True
            continue

        # 汇合标记: → 汇合到/汇合至 `target`
        conv_match = re.match(r"^→\s*汇合[到至]\s*`?(\d+[a-z]?)`?", line)
        if conv_match and current_entry:
            current_entry.convergence_raw = conv_match.group(1)
            in_words = False
            continue

        # 空行结束对白
        if line.strip() == "":
            in_words = False

    # 保存最后一个条目
    if current_entry and current_file:
        sections.setdefault(current_file, []).append(current_entry)

    return sections


def renumber_letter_ids(entries):
    """重编号带字母后缀的 ID。返回 {old_raw: new_num_id} 映射表。"""
    id_map = {}  # old_raw → new_num

    # 第一遍：找出所有 ID（含后缀的和纯数字的）
    has_suffix = any(re.search(r"[a-z]$", e.id_raw) for e in entries)
    if not has_suffix:
        # 无字母后缀，直接用原始数字
        for e in entries:
            num = int(e.id_raw)
            id_map[e.id_raw] = num
            e.id_num = num
        return id_map

    # 有字母后缀 → 需要重编号
    # 策略：按文件顺序遍历，为每个条目分配连续 ID
    # 基准：使用第一个条目的数字部分作为起始前缀

    # 提取所有条目的数字基准（去掉字母后缀）
    first_id = entries[0].id_raw
    prefix = first_id[:6]  # 前6位（如 210001）

    # 按文件顺序分配，保持原始纯数字条目的序号尽量不变
    # 但如果有字母后缀导致冲突，后续条目向后推移
    next_seq = int(entries[0].id_raw.rstrip("abcdefghijklmnopqrstuvwxyz")[-3:])

    for e in entries:
        raw_digits = e.id_raw.rstrip("abcdefghijklmnopqrstuvwxyz")
        raw_prefix = raw_digits[:-3]  # 如 "210001"
        raw_seq = int(raw_digits[-3:])  # 如 38

        if re.search(r"[a-z]$", e.id_raw):
            # 有字母后缀 → 分配新序号
            new_seq = max(next_seq, raw_seq)
            new_id = int(raw_prefix + f"{new_seq:03d}")
            id_map[e.id_raw] = new_id
            e.id_num = new_id
            next_seq = new_seq + 1
        else:
            # 纯数字 → 尽量保持，但不能比 next_seq 小
            if raw_seq < next_seq:
                new_id = int(raw_prefix + f"{next_seq:03d}")
            else:
                new_id = int(e.id_raw)
                next_seq = raw_seq
            id_map[e.id_raw] = new_id
            e.id_num = new_id
            next_seq = new_id % 1000 + 1

    return id_map


def resolve_id(raw_id, id_map):
    """将原始 ID（可能含字母后缀）解析为最终数字 ID。"""
    if raw_id in id_map:
        return id_map[raw_id]
    # 可能是纯数字但不在当前文件的 map 中（跨文件引用）
    try:
        return int(raw_id)
    except ValueError:
        print(f"  ⚠️ 无法解析 ID: {raw_id}")
        return 0


def compute_next_and_params(entries, id_map):
    """计算每条 entry 的 next 字段和 Parameter 字段。"""
    for i, e in enumerate(entries):
        next_entry = entries[i + 1] if i + 1 < len(entries) else None

        if e.script == "end":
            # end → 无 next
            e._next = None
            continue

        if e.script == "Lie":
            # Lie → next 为空（玩家需出示证据）
            e._next = None
            e._param_str0 = e.lie_evidences
            e._param_int0 = resolve_id(e.lie_target_raw, id_map)
            e._param_int1 = 1
            continue

        if e.script == "branches":
            # branches → ParameterStr/Int 存分支选项
            targets = []
            for j, (text, target_raw) in enumerate(e.branch_options):
                target_id = resolve_id(target_raw, id_map)
                setattr(e, f"_param_str{j}", text)
                setattr(e, f"_param_int{j}", target_id)
                targets.append(str(target_id))
            e._next = "/".join(targets) if targets else None
            continue

        if e.script == "get":
            e._param_int0 = e.get_target
            # get → next = 下一条或汇合目标
            if e.convergence_raw:
                e._next = str(resolve_id(e.convergence_raw, id_map))
            elif next_entry:
                e._next = str(next_entry.id_num)
            else:
                e._next = None
            continue

        # 普通对话
        if e.convergence_raw:
            e._next = str(resolve_id(e.convergence_raw, id_map))
        elif next_entry:
            e._next = str(next_entry.id_num)
        else:
            # 最后一条无 next → 标记为 end
            e.script = "end"
            e._next = None


def entry_to_json(e):
    """将 DialogueEntry 转换为 JSON dict（简化格式）。"""
    d = OrderedDict()
    d["id"] = e.id_num
    d["cnSpeaker"] = e.speaker_full
    d["cnWords"] = e.words

    # next
    next_val = getattr(e, "_next", None)
    if next_val:
        d["next"] = next_val

    # script
    if e.script:
        d["script"] = e.script

    # Parameters
    for j in range(3):
        str_key = f"ParameterStr{j}"
        int_key = f"ParameterInt{j}"
        str_val = getattr(e, f"_param_str{j}", "")
        int_val = getattr(e, f"_param_int{j}", 0)
        if str_val:
            d[str_key] = str_val
        if int_val:
            d[int_key] = int_val

    return d


def write_json_file(data, filepath, dry_run=False):
    """写入 JSON 文件。"""
    if dry_run:
        print(f"  [DRY] Would write {filepath.name} ({len(data)} entries)")
        return

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_md_ids(filepath, all_id_maps):
    """更新 MD 文件中的字母后缀 ID 为纯数字。"""
    text = filepath.read_text(encoding="utf-8")

    # 合并所有段的 id_map
    combined = {}
    for id_map in all_id_maps:
        for raw, num in id_map.items():
            if re.search(r"[a-z]$", raw):
                combined[raw] = str(num)
            elif str(num) != raw:
                combined[raw] = str(num)

    if not combined:
        return False  # 无需修改

    # 使用 re.sub 单次替换，避免级联替换问题
    # 按长度降序排列 key，确保 "038a" 在 "038" 之前匹配
    sorted_keys = sorted(combined.keys(), key=len, reverse=True)

    # 构建正则：匹配 ### ID 行或 `ID` 引用中的 ID
    def make_pattern(keys):
        escaped = [re.escape(k) for k in keys]
        return re.compile(
            r"(###\s+)(" + "|".join(escaped) + r")(\s|$)"
            r"|"
            r"(`)("+  "|".join(escaped) + r")(`)"
        )

    pattern = make_pattern(sorted_keys)

    def replacer(m):
        if m.group(1) is not None:
            # ### ID 行
            old_id = m.group(2)
            return m.group(1) + combined[old_id] + m.group(3)
        else:
            # `ID` 引用
            old_id = m.group(5)
            return m.group(4) + combined[old_id] + m.group(6)

    text = pattern.sub(replacer, text)

    filepath.write_text(text, encoding="utf-8")
    return True


def update_manifest(directory, filenames, dry_run=False):
    """更新 _manifest.json。"""
    manifest_path = directory / "_manifest.json"
    data = sorted([f"{fn}" for fn in filenames])
    if dry_run:
        print(f"  [DRY] Would update {manifest_path}: {data}")
        return
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def process_loop(loop_num, dry_run=False):
    """处理一个 Loop 的全部 MD 文件。"""
    loop_dir = DRAFT_DIR / f"Loop{loop_num}"
    if not loop_dir.exists():
        print(f"  [SKIP] Loop{loop_num} 目录不存在")
        return

    md_files = sorted(loop_dir.glob("*.md"))
    if not md_files:
        print(f"  [SKIP] Loop{loop_num} 无 MD 文件")
        return

    talk_files = []  # 生成的 Talk JSON 文件名
    expose_files = []  # 生成的 Expose JSON 文件名
    total_entries = 0

    for md_file in md_files:
        print(f"\n  📄 {md_file.name}")
        sections = parse_md_file(md_file)

        if not sections:
            print(f"     ⚠️ 未解析到任何对话段落")
            continue

        all_id_maps = []

        for json_filename, entries in sections.items():
            if not entries:
                continue

            # 重编号字母后缀 ID
            id_map = renumber_letter_ids(entries)
            all_id_maps.append(id_map)

            # 计算 next 和 parameters
            compute_next_and_params(entries, id_map)

            # 转换为 JSON
            json_data = [entry_to_json(e) for e in entries]
            total_entries += len(json_data)

            # 确定输出路径
            is_expose = json_filename.startswith("loop") and "expose" in json_filename.lower()
            # 也检查 MD 中的 ## Expose: 标记
            if not is_expose:
                # 检查文件名是否在 Expose 目录的命名模式中
                is_expose = any(
                    json_filename == f"loop{loop_num}_{name}.json"
                    for name in ["morrison", "leonard", "moore", "danny", "vinnie"]
                )

            if is_expose:
                out_path = EXPOSE_DIR / json_filename
                expose_files.append(json_filename)
            else:
                out_path = TALK_DIR / f"loop{loop_num}" / json_filename
                talk_files.append(json_filename)

            print(f"     → {out_path.relative_to(BASE)} ({len(json_data)} entries)")
            write_json_file(json_data, out_path, dry_run)

        # 注意：不更新 MD 源文件中的字母后缀 ID
        # 字母后缀在 MD 中保留用于可读性，仅在 JSON 输出时重编号

    # 更新 manifest
    if talk_files:
        print(f"\n  📋 Talk manifest: {talk_files}")
        update_manifest(TALK_DIR / f"loop{loop_num}", talk_files, dry_run)

    # Expose manifest 在所有 loop 处理完后统一更新
    return {
        "talk_files": talk_files,
        "expose_files": expose_files,
        "total_entries": total_entries,
    }


def main():
    dry_run = "--dry-run" in sys.argv
    target_loop = None

    for arg in sys.argv[1:]:
        if arg.startswith("--loop"):
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                target_loop = int(sys.argv[idx + 1])

    if dry_run:
        print("🔍 预览模式（不写文件）\n")
    else:
        print("🚀 开始转换\n")

    all_expose_files = []
    grand_total = 0

    loops = [target_loop] if target_loop else range(1, 7)

    for loop_num in loops:
        print(f"═══ Loop {loop_num} ═══")
        result = process_loop(loop_num, dry_run)
        if result:
            all_expose_files.extend(result["expose_files"])
            grand_total += result["total_entries"]

    # 更新 Expose manifest
    if all_expose_files:
        print(f"\n📋 Expose manifest: {all_expose_files}")
        update_manifest(EXPOSE_DIR, all_expose_files, dry_run)

    print(f"\n✅ 完成！共处理 {grand_total} 条对话。")


if __name__ == "__main__":
    main()
