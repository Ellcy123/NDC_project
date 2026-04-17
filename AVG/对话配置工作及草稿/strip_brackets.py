#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量清理对话台词里嵌入的方括号动作描述 [...]

范围：
- AVG/对话配置工作及草稿/生成草稿/Loop{1-6}_生成草稿.md 里 `> ` 开头的台词行
- AVG/EPI08/Talk/loop*/*.json 的 cnWords 字段
- AVG/EPI08/Expose/*.json 的 cnWords 字段
- preview_new2/data/table/Talk.json 和 ExposeTalk.json 里 EPI08 条目的 cnWords

规则：
- 移除台词里所有 [...] 段（含半角 [] 和全角 ［］）
- 保留 cnAction 字段（动作描述本来就放这里，不动）
- 清理移除后残留的多余空格/连续标点

用法：
  python strip_brackets.py --dry-run
  python strip_brackets.py --apply
"""

import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r"d:\NDC_project")
MD_DIR = ROOT / "AVG/对话配置工作及草稿/生成草稿"
TALK_DIR = ROOT / "AVG/EPI08/Talk"
EXPOSE_DIR = ROOT / "AVG/EPI08/Expose"
TABLE_DIR = ROOT / "preview_new2/data/table"

# 方括号模式：半角 [] + 全角 ［］
# 非贪婪匹配避免跨越多个 [...]
BRACKET_PATTERN = re.compile(r"[\[［][^\[\]［］]*?[\]］]")


def strip_brackets_in_text(text: str) -> tuple[str, int]:
    """从文本里移除所有 [...] 段。返回 (清理后文本, 移除数量)。"""
    if not isinstance(text, str) or ('[' not in text and '［' not in text):
        return text, 0

    count = len(BRACKET_PATTERN.findall(text))
    if count == 0:
        return text, 0

    result = BRACKET_PATTERN.sub("", text)
    # 清理：连续空格合并为一个 / 首尾空格去掉
    result = re.sub(r"\s{2,}", " ", result).strip()
    # 清理遗留的孤立标点（如" ，"、连续标点）
    result = re.sub(r"\s+([，。；？！,.])", r"\1", result)
    return result, count


def process_md_file(path: Path, dry_run: bool) -> dict:
    """处理 MD 文件：只清理 `> ` 开头的台词行（保留 speaker 行 `**xxx** [action]` 格式不动）。"""
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')
    total_removed = 0
    changed_lines = 0

    for i, line in enumerate(lines):
        if line.startswith('> '):
            body = line[2:]
            new_body, n = strip_brackets_in_text(body)
            if n > 0:
                lines[i] = '> ' + new_body
                total_removed += n
                changed_lines += 1

    if not dry_run and changed_lines > 0:
        backup = path.with_suffix(path.suffix + '.pre_strip_brackets')
        if not backup.exists():
            backup.write_text(content, encoding='utf-8')
        path.write_text('\n'.join(lines), encoding='utf-8')

    return {"file": str(path.relative_to(ROOT)), "changed_lines": changed_lines, "removed": total_removed}


def process_json_file(path: Path, dry_run: bool, only_epi08: bool = False) -> dict:
    """处理 JSON 文件：清理每个条目的 cnWords 字段。"""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        return {"file": str(path.relative_to(ROOT)), "error": "not a list"}

    total_removed = 0
    changed_entries = 0

    for entry in data:
        if not isinstance(entry, dict):
            continue
        # 只处理 EPI08 条目（如果要求）
        if only_epi08 and entry.get('videoEpisode') != 'EPI08':
            continue
        entry_changed = False
        # AVG JSON 格式：cnWords 是字符串
        if 'cnWords' in entry and isinstance(entry['cnWords'], str):
            new_text, n = strip_brackets_in_text(entry['cnWords'])
            if n > 0:
                entry['cnWords'] = new_text
                total_removed += n
                entry_changed = True
        # Table JSON 格式：Words 是 [中文, 英文] 数组
        if 'Words' in entry and isinstance(entry['Words'], list):
            words = entry['Words']
            if len(words) >= 1 and isinstance(words[0], str):
                new_text, n = strip_brackets_in_text(words[0])
                if n > 0:
                    words[0] = new_text
                    total_removed += n
                    entry_changed = True
        if entry_changed:
            changed_entries += 1

    if not dry_run and changed_entries > 0:
        backup = path.with_suffix(path.suffix + '.pre_strip_brackets')
        if not backup.exists():
            with open(path, encoding='utf-8') as f:
                backup.write_text(f.read(), encoding='utf-8')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return {"file": str(path.relative_to(ROOT)), "changed_entries": changed_entries, "removed": total_removed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', default=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--skip-md', action='store_true', help='跳过 MD 文件')
    parser.add_argument('--skip-avg-json', action='store_true', help='跳过 AVG/EPI08 JSON')
    parser.add_argument('--skip-table', action='store_true', help='跳过 table JSON')
    args = parser.parse_args()
    dry_run = not args.apply

    print(f"模式: {'DRY-RUN' if dry_run else 'APPLY'}")
    print("=" * 60)

    total_removed = 0
    total_files_changed = 0

    # 1. MD 草稿
    if not args.skip_md:
        print("\n── MD 草稿 ──")
        for path in sorted(MD_DIR.glob("Loop*_生成草稿.md")):
            stats = process_md_file(path, dry_run)
            total_removed += stats["removed"]
            if stats["changed_lines"] > 0:
                total_files_changed += 1
            print(f"  {path.name}: {stats['changed_lines']} 行改动，移除 {stats['removed']} 个方括号")

    # 2. AVG Talk JSON
    if not args.skip_avg_json:
        print("\n── AVG/EPI08/Talk/ JSON ──")
        for path in sorted(TALK_DIR.glob("loop*/*.json")):
            if path.name.startswith("_manifest"):
                continue
            stats = process_json_file(path, dry_run)
            total_removed += stats.get("removed", 0)
            if stats.get("changed_entries", 0) > 0:
                total_files_changed += 1
                print(f"  {path.relative_to(TALK_DIR)}: {stats['changed_entries']} 条改动，移除 {stats['removed']} 个")

        print("\n── AVG/EPI08/Expose/ JSON ──")
        for path in sorted(EXPOSE_DIR.glob("*.json")):
            if path.name.startswith("_manifest"):
                continue
            stats = process_json_file(path, dry_run)
            total_removed += stats.get("removed", 0)
            if stats.get("changed_entries", 0) > 0:
                total_files_changed += 1
                print(f"  {path.name}: {stats['changed_entries']} 条改动，移除 {stats['removed']} 个")

    # 3. Table JSON（只处理 EPI08 条目）
    if not args.skip_table:
        print("\n── preview_new2/data/table/ JSON （仅 EPI08 条目）──")
        for fname in ("Talk.json", "ExposeTalk.json"):
            path = TABLE_DIR / fname
            if not path.exists():
                continue
            stats = process_json_file(path, dry_run, only_epi08=True)
            total_removed += stats.get("removed", 0)
            if stats.get("changed_entries", 0) > 0:
                total_files_changed += 1
            print(f"  {fname}: {stats.get('changed_entries', 0)} 条改动（仅 EPI08），移除 {stats.get('removed', 0)} 个")

    print("\n" + "=" * 60)
    print(f"合计：{total_files_changed} 个文件改动，移除 {total_removed} 个方括号")
    if dry_run:
        print("DRY-RUN 完成，未写入。用 --apply 执行。")
    else:
        print("APPLY 完成。备份后缀：*.pre_strip_brackets")


if __name__ == '__main__':
    main()
