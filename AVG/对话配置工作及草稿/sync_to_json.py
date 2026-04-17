#!/usr/bin/env python3
"""
MD → JSON 同步脚本
将 MD 草稿中修改过的中文对白回写到对应的 JSON 文件。

只更新以下字段（保留其他所有字段不变）：
  - cnAction（情绪/表情）
  - cnWords（对白）
  - cnSpeaker（说话人，极少改动）
  - ParameterStr0-2（分支选项文本，仅 branches 类型）

用法:
  python sync_to_json.py Loop2_对话草稿.md          # 同步单个 Loop
  python sync_to_json.py Loop2_对话草稿.md --dry-run # 预览变更，不写入
  python sync_to_json.py --all                       # 同步所有 Loop
  python sync_to_json.py --all --dry-run             # 预览所有变更
"""

import json
import re
import sys
import os
from pathlib import Path
from copy import deepcopy

# 路径配置
BASE = Path(__file__).parent.parent  # NDC_project/AVG/
TALK_DIR = BASE / "EPI02" / "Talk"
EXPOSE_DIR = BASE / "EPI02" / "Expose"
MD_DIR = Path(__file__).parent  # 对话配置工作及草稿/

# Expose 文件对应关系
EXPOSE_FILES = {
    1: "loop1_morrison.json",
    2: "loop2_leonard.json",
    3: "loop3_moore.json",
    4: "loop4_danny.json",
    5: "loop5_vinnie.json",
    6: "loop6_leonard.json",
}


class MDEntry:
    """从 MD 中解析出的单条对话"""
    def __init__(self):
        self.id = 0
        self.cn_speaker = ""
        self.cn_action = ""
        self.cn_words = ""
        self.script_tag = ""  # 原始标记，仅供参考
        self.branch_options = []  # [(text, target_id), ...]
        self.source_file = ""  # 对应的 JSON 文件名


def parse_md_file(md_path):
    """解析 MD 文件，返回 {json_filename: [MDEntry, ...]}"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    result = {}  # filename → [MDEntry]
    current_file = None
    current_entry = None
    in_words = False  # 是否在读取 > 对白行

    for line in lines:
        # 检测文件段落标题: ## Talk: xxx.json 或 ## Expose: xxx.json
        file_match = re.match(r"^## (?:Talk|Expose): (.+\.json)", line)
        if file_match:
            # 保存前一个 entry
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
            current_file = file_match.group(1)
            current_entry = None
            in_words = False
            continue

        # 检测对话条目标题: ### 209001001 [可选标记]
        entry_match = re.match(r"^### (\d+)", line)
        if entry_match:
            # 保存前一个 entry
            if current_entry and current_file:
                result.setdefault(current_file, []).append(current_entry)
            current_entry = MDEntry()
            current_entry.id = int(entry_match.group(1))
            current_entry.source_file = current_file or ""
            in_words = False
            continue

        if current_entry is None:
            continue

        # 检测说话人 + 情绪: **扎克·布伦南** [情绪描述]
        speaker_match = re.match(r"^\*\*(.+?)\*\*\s*(?:\[(.+?)\])?", line)
        if speaker_match:
            current_entry.cn_speaker = speaker_match.group(1).strip()
            current_entry.cn_action = (speaker_match.group(2) or "").strip()
            in_words = False
            continue

        # 检测对白行: > xxx
        if line.startswith("> "):
            content = line[2:]

            # 跳过特殊标记行
            if content.startswith("📋 ") or content.startswith("🎯 "):
                continue
            if content.startswith("场景："):
                continue

            # 检测分支选项: > - ❶ 文本 → `target`
            branch_match = re.match(
                r"^- [❶❷❸\(\d+\)]\s+(.+?)\s+→\s+`(\d+)`", content
            )
            if branch_match:
                opt_text = branch_match.group(1).strip()
                opt_target = int(branch_match.group(2))
                current_entry.branch_options.append((opt_text, opt_target))
                continue

            # 普通对白
            if in_words:
                current_entry.cn_words += "\n" + content
            else:
                current_entry.cn_words = content
                in_words = True
            continue

        # 非 > 开头的行 → 对白段落结束
        if in_words and line.strip() == "":
            in_words = False

    # 保存最后一个 entry
    if current_entry and current_file:
        result.setdefault(current_file, []).append(current_entry)

    return result


def resolve_json_path(filename, loop_num):
    """根据文件名和 Loop 号找到对应的 JSON 文件路径"""
    # Expose 文件
    if filename.startswith("loop") and "_" in filename:
        path = EXPOSE_DIR / filename
        if path.exists():
            return path

    # Talk 文件
    path = TALK_DIR / f"loop{loop_num}" / filename
    if path.exists():
        return path

    return None


def sync_entries(json_path, md_entries, dry_run=False):
    """将 MD 中的对白同步到 JSON 文件。返回变更摘要。"""
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 建立 ID 索引
    id_to_idx = {}
    for idx, entry in enumerate(json_data):
        id_to_idx[entry["id"]] = idx

    changes = []
    modified = False

    for md_entry in md_entries:
        idx = id_to_idx.get(md_entry.id)
        if idx is None:
            changes.append(f"  ⚠️  ID {md_entry.id} 在 JSON 中不存在，跳过")
            continue

        je = json_data[idx]
        entry_changes = []

        # 同步 cnWords
        if md_entry.cn_words and md_entry.cn_words != je.get("cnWords", ""):
            old = je.get("cnWords", "")
            entry_changes.append(f"    cnWords: {_truncate(old)} → {_truncate(md_entry.cn_words)}")
            if not dry_run:
                je["cnWords"] = md_entry.cn_words

        # 同步 cnAction
        if md_entry.cn_action != je.get("cnAction", ""):
            old = je.get("cnAction", "")
            entry_changes.append(f"    cnAction: {_truncate(old)} → {_truncate(md_entry.cn_action)}")
            if not dry_run:
                je["cnAction"] = md_entry.cn_action

        # 同步 cnSpeaker（极少改动，但支持）
        if md_entry.cn_speaker and md_entry.cn_speaker != je.get("cnSpeaker", ""):
            old = je.get("cnSpeaker", "")
            entry_changes.append(f"    cnSpeaker: {old} → {md_entry.cn_speaker}")
            if not dry_run:
                je["cnSpeaker"] = md_entry.cn_speaker

        # 同步分支选项文本（仅文本，不动 ParameterInt）
        if md_entry.branch_options:
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

    # 写回 JSON
    if modified and not dry_run:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    return changes, modified


def _truncate(s, maxlen=50):
    """截断长字符串用于显示"""
    s = s.replace("\n", "\\n")
    if len(s) > maxlen:
        return s[:maxlen] + "..."
    return s


def get_loop_num_from_md(md_filename):
    """从 MD 文件名提取 Loop 号"""
    m = re.match(r"Loop(\d+)", md_filename)
    return int(m.group(1)) if m else None


def process_single_md(md_path, dry_run=False):
    """处理单个 MD 文件的同步"""
    md_filename = os.path.basename(md_path)
    loop_num = get_loop_num_from_md(md_filename)
    if loop_num is None:
        print(f"❌ 无法从文件名 {md_filename} 提取 Loop 号")
        return

    print(f"\n{'[预览模式] ' if dry_run else ''}同步 {md_filename} (Loop {loop_num})")
    print("=" * 60)

    parsed = parse_md_file(md_path)
    if not parsed:
        print("  没有解析到任何对话条目")
        return

    total_changes = 0
    total_files = 0

    for filename, md_entries in parsed.items():
        json_path = resolve_json_path(filename, loop_num)
        if json_path is None:
            print(f"\n📄 {filename} — ⚠️ JSON 文件未找到，跳过")
            continue

        changes, modified = sync_entries(json_path, md_entries, dry_run)

        if changes:
            print(f"\n📄 {filename}")
            for line in changes:
                print(line)
            total_changes += len([c for c in changes if c.startswith("  [")])
            if modified:
                total_files += 1
        else:
            print(f"\n📄 {filename} — 无变更")

    print(f"\n{'─' * 40}")
    if dry_run:
        print(f"预览完成: {total_changes} 条记录有变更，涉及 {total_files} 个文件")
    else:
        print(f"同步完成: 更新了 {total_changes} 条记录，写入 {total_files} 个文件")


def main():
    args = sys.argv[1:]

    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if "--all" in args:
        # 同步所有 Loop
        for loop_num in range(1, 7):
            md_path = MD_DIR / f"Loop{loop_num}_对话草稿.md"
            if md_path.exists():
                process_single_md(md_path, dry_run)
            else:
                print(f"⚠️ {md_path.name} 不存在，跳过")
    elif args:
        # 同步指定文件
        for arg in args:
            md_path = Path(arg)
            if not md_path.is_absolute():
                md_path = MD_DIR / arg
            if md_path.exists():
                process_single_md(md_path, dry_run)
            else:
                print(f"❌ 文件不存在: {md_path}")
    else:
        print("用法:")
        print("  python sync_to_json.py Loop2_对话草稿.md          # 同步单个文件")
        print("  python sync_to_json.py Loop2_对话草稿.md --dry-run # 预览变更")
        print("  python sync_to_json.py --all                       # 同步所有")
        print("  python sync_to_json.py --all --dry-run             # 预览所有")


if __name__ == "__main__":
    main()
