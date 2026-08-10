#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit8 Expose JSON 清理脚本（一次性修复）

问题：
- Expose JSON 里 id / next / videoId 仍是 6 位 {1N}{序}（与 Unit1 冲突）
- ParameterStr 引用的证据 ID 是 EV1xxx（Unit1 格式）
- 部分文件同 id 有重复条目

修复规则：
1. 所有整数/字符串形式的 6 位 ID，若以 1[1-6] 开头（= Unit1 Expose 格式），改为 8[1-6]
   例：110001 → 810001（Loop1 Rosa Expose）
       160001 → 860001（Loop6 Morrison Expose）
2. ParameterStr 里 EV1xxx（4 位）→ EV8xxx（首位 1→8 保留 loop 号）
   例：EV1101 → EV8101（Loop1 证据 01，Vivian 手枪）
       EV1305 → EV8305（Loop3 证据 05，玻璃碎片）
3. 同 id 条目去重（保留第一条）
4. videoEpisode/videoLoop/videoScene/IdSpeaker 不改

备份：每个文件备份为 *.pre_prefix_fix
用法：
  python fix_expose_unit8_prefix.py --dry-run
  python fix_expose_unit8_prefix.py --apply
"""

import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EXPOSE_DIR = Path(r"d:\NDC_project\AVG\EPI08\Expose")

# 6 位 Expose ID 前缀映射：Unit1 → Unit8
# 11xxxx → 81xxxx / 12xxxx → 82xxxx / ... / 16xxxx → 86xxxx
EXPOSE_ID_PREFIX_MAP = {
    "11": "81", "12": "82", "13": "83",
    "14": "84", "15": "85", "16": "86",
}


def migrate_expose_id_str(s: str) -> str:
    """把 6 位纯数字字符串形式的 Expose ID 迁移。其他字符串原样返回。"""
    if not isinstance(s, str):
        return s
    m = re.fullmatch(r"(\d{6})", s)
    if not m:
        return s
    prefix2 = m.group(1)[:2]
    if prefix2 in EXPOSE_ID_PREFIX_MAP:
        return EXPOSE_ID_PREFIX_MAP[prefix2] + m.group(1)[2:]
    return s


def migrate_expose_id_int(n):
    """把 6 位整数形式的 Expose ID 迁移。"""
    if not isinstance(n, int):
        return n
    s = str(n)
    if len(s) != 6:
        return n
    prefix2 = s[:2]
    if prefix2 in EXPOSE_ID_PREFIX_MAP:
        return int(EXPOSE_ID_PREFIX_MAP[prefix2] + s[2:])
    return n


# EV1xxx → EV8xxx（证据 ID：首位 1→8 保留 loop 号）
# 证据 ID 格式 1N + 2 位序号；Unit8 为 8N + 序号
EV_PATTERN = re.compile(r"\bEV(1[1-6]\d{2})\b")
EV_PATTERN_6 = re.compile(r"\bEV(1[1-6]\d{4})\b")  # 偶尔 6 位


def migrate_ev_ref(s: str) -> str:
    """ParameterStr 里的 EV1xxx → EV8xxx（4 位 + 可能的 6 位）"""
    if not isinstance(s, str):
        return s
    s = EV_PATTERN_6.sub(lambda m: "EV8" + m.group(1)[1:], s)
    s = EV_PATTERN.sub(lambda m: "EV8" + m.group(1)[1:], s)
    return s


def process_entry(entry: dict) -> dict:
    """迁移单条 Expose 对话条目的所有相关字段。"""
    # id (int) / next (str) / videoId (str)
    if "id" in entry:
        entry["id"] = migrate_expose_id_int(entry["id"])
    if "next" in entry:
        entry["next"] = migrate_expose_id_str(entry["next"])
    if "videoId" in entry:
        entry["videoId"] = migrate_expose_id_str(entry["videoId"])

    # ParameterStr0/1/2 可能含 EV 引用和 next 跳转 id
    for k in ("ParameterStr0", "ParameterStr1", "ParameterStr2"):
        if k in entry and isinstance(entry[k], str):
            # 先处理 EV 引用
            entry[k] = migrate_ev_ref(entry[k])
            # ParameterStr 里也可能有 next 跳转 id（如分支选项的目标）
            # 匹配纯 6 位数字且以 1[1-6] 开头
            entry[k] = re.sub(
                r"\b(1[1-6]\d{4})\b",
                lambda m: EXPOSE_ID_PREFIX_MAP[m.group(1)[:2]] + m.group(1)[2:],
                entry[k],
            )

    # ParameterInt0/1/2 可能是跳转 id（整数形式）
    for k in ("ParameterInt0", "ParameterInt1", "ParameterInt2"):
        if k in entry:
            entry[k] = migrate_expose_id_int(entry[k])

    return entry


def deduplicate_entries(entries: list[dict]) -> tuple[list[dict], int]:
    """按 id 去重，保留第一次出现。返回 (去重后列表, 删除数量)"""
    seen = set()
    kept = []
    dup = 0
    for e in entries:
        eid = e.get("id")
        if eid in seen:
            dup += 1
            continue
        seen.add(eid)
        kept.append(e)
    return kept, dup


def process_file(filepath: Path, dry_run: bool = True) -> dict:
    """处理一个 Expose JSON 文件。"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return {"file": filepath.name, "error": "not a list"}

    before_count = len(data)

    # 1. 迁移每个条目的 ID/EV 引用
    for entry in data:
        process_entry(entry)

    # 2. 去重
    data, dup_count = deduplicate_entries(data)

    # 3. 备份 + 写入
    if not dry_run:
        backup = filepath.with_suffix(filepath.suffix + ".pre_prefix_fix")
        if not backup.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                backup.write_text(f.read(), encoding="utf-8")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 4. 统计新 ID 前缀分布
    prefix_dist = {}
    for e in data:
        iid = str(e.get("id", ""))
        if len(iid) >= 2:
            p = iid[:2]
            prefix_dist[p] = prefix_dist.get(p, 0) + 1

    return {
        "file": filepath.name,
        "before": before_count,
        "after": len(data),
        "duplicates_removed": dup_count,
        "new_prefix_dist": prefix_dist,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    dry_run = not args.apply

    print(f"模式: {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"目录: {EXPOSE_DIR}")
    print("=" * 60)

    if not EXPOSE_DIR.exists():
        print(f"[ERR] 目录不存在: {EXPOSE_DIR}")
        return

    files = sorted(EXPOSE_DIR.glob("loop*_*.json"))
    if not files:
        print("[WARN] 没找到 loop*_*.json 文件")
        return

    for f in files:
        stats = process_file(f, dry_run=dry_run)
        print(f"\n{stats['file']}:")
        print(f"  条目数：{stats['before']} → {stats['after']}（去重 {stats['duplicates_removed']}）")
        print(f"  新 ID 前缀分布：{stats['new_prefix_dist']}")

    print("\n" + "=" * 60)
    if dry_run:
        print("DRY-RUN 完成，未写入任何文件。用 --apply 执行。")
    else:
        print("APPLY 完成。备份文件：*.pre_prefix_fix")


if __name__ == "__main__":
    main()
