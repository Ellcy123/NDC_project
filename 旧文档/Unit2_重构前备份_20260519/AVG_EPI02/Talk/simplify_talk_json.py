"""
简化 AVG/EPI02/Talk 下所有对话 JSON 文件。
保留预览必要字段，省略空值/零值字段。

保留字段：
  必填: id, cnSpeaker, cnWords
  条件: next, script, ParameterStr0/1/2, ParameterInt0/1/2

用法: python simplify_talk_json.py
"""

import json
import os
from pathlib import Path

KEEP_ALWAYS = {"id", "cnSpeaker", "cnWords"}
KEEP_IF_TRUTHY = {"next", "script", "ParameterStr0", "ParameterStr1", "ParameterStr2"}
KEEP_IF_NONZERO = {"ParameterInt0", "ParameterInt1", "ParameterInt2"}


def simplify_entry(entry):
    out = {}
    for key in KEEP_ALWAYS:
        if key in entry:
            out[key] = entry[key]
    for key in KEEP_IF_TRUTHY:
        val = entry.get(key)
        if val:  # non-empty string
            out[key] = val
    for key in KEEP_IF_NONZERO:
        val = entry.get(key)
        if val and val != 0:
            out[key] = val
    return out


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"  跳过（非数组）: {filepath}")
        return 0

    simplified = [simplify_entry(e) for e in data]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

    return len(simplified)


def main():
    base = Path(__file__).parent
    total_files = 0
    total_entries = 0

    for loop_dir in sorted(base.glob("loop*")):
        if not loop_dir.is_dir():
            continue
        for json_file in sorted(loop_dir.glob("*.json")):
            if json_file.name == "_manifest.json":
                continue
            count = process_file(json_file)
            if count > 0:
                total_files += 1
                total_entries += count
                print(f"  OK {loop_dir.name}/{json_file.name} ({count} entries)")

    print(f"\n完成: {total_files} 文件, {total_entries} 条对话已简化")


if __name__ == "__main__":
    main()
