#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit1 重构版 0417 · 对话草稿 ID 迁移脚本

把 Loop1-6 对话草稿里"临时/ad-hoc"的 9 位对话 ID 统一迁移到配置表详解（docs/配置表详解.md）
规定的 重构版 8XX 命名规范。

## 规范

- 普通对话 ID（9 位）：`{NPC3}{对话组3}{句序3}`，NPC 以 8XX 开头（重构版）
- 指证对话 ID（6 位）：`{轮次2}{序号4}`（例如 Loop1 Rosa Expose = 11xxxx）
- 证词 ID（7 位）：`{NPC3}{轮次1}{序号3}`，8XX 开头

## NPC 编码（重构版）

| 旧 | 新 | 角色 |
|----|----|----|
| 101 | 801 | Zack |
| 102 | 802 | Emma |
| 103 | 803 | Rosa |
| 104 | 804 | Morrison |
| 105 | 805 | Tommy |
| 106 | 806 | Vivian |
| 107 | 807 | Jimmy |
| 108 | 808 | Anna |
| 109 | 809 | Webb（死者） |
| 110 | 810 | Mrs. Morrison |
| 111 | 811 | Whale |

## 用法

```
python id_migration_0417.py --dry-run    # 预览（不写文件）
python id_migration_0417.py --apply      # 实际应用
```
"""

import argparse
import io
import json
import os
import re
import sys
from collections import OrderedDict
from pathlib import Path

# 强制 stdout 使用 utf-8 输出（Windows GBK 默认不支持中文/emoji）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ──────────────────────────────────────────────────────────
# 路径
# ──────────────────────────────────────────────────────────
ROOT = Path(r"d:\NDC_project")
DRAFT_DIR = ROOT / "AVG/对话配置工作及草稿/生成草稿"
STATE_DIR = ROOT / "剧情设计/unit1重构版0417/state"
MAPPING_OUT = DRAFT_DIR / "id_mapping_0417.json"

LOOP_FILES = {i: DRAFT_DIR / f"Loop{i}_生成草稿.md" for i in range(1, 7)}
STATE_FILES = {i: STATE_DIR / f"loop{i}_state.yaml" for i in range(1, 7)}

# ──────────────────────────────────────────────────────────
# 对话段 → 新前缀映射
# ──────────────────────────────────────────────────────────
# 格式：旧 6 位前缀 → (新 NPC 8XX, 对话组 3 位)
# 对话组计数规则：每个 NPC 从 001 开始，按 loop 顺序累加（跨 loop 累加）
#
# Emma 跨 loop 出场（opening + post_expose）=> 002 × 6 = group 001..012
# 每个其他 NPC 按 loop 出场累加
#
# 非 NPC 段（如 arrest_cutscene / whale phone / morrison_house 搜证）
# 暂定归 Zack（801）名下作为"Zack 主导场景"，组号继续累加

DIALOGUE_PREFIX_MAP = {
    # ── Loop1 ────────────────────────────────
    "105001": ("802", "001"),  # emma_001 (loop1 opening)
    "105002": ("802", "002"),  # emma_002 (loop1 post_expose)
    "101101": ("806", "001"),  # vivian_001 (loop1 s101)
    "102101": ("803", "001"),  # rosa_001 (loop1 s101)
    "103101": ("804", "001"),  # morrison_001 (loop1 s101)

    # ── Loop2 ────────────────────────────────
    "205001": ("802", "003"),  # emma_003 (loop2 opening)
    "205002": ("802", "004"),  # emma_004 (loop2 post_expose)
    "202101": ("806", "002"),  # vivian_002 (loop2 workshop)
    "204103": ("807", "001"),  # jimmy_001 (loop2 kitchen)
    "205104": ("805", "001"),  # tommy_001 (loop2 office)

    # ── Loop3 ────────────────────────────────
    "305001": ("802", "005"),  # emma_005 (loop3 opening)
    "305002": ("802", "006"),  # emma_006 (loop3 post_expose)
    "304103": ("807", "002"),  # jimmy_002 (loop3 kitchen)
    "303102": ("804", "002"),  # morrison_002 (loop3 hall)
    "302108": ("803", "002"),  # rosa_002 (loop3 cleaning)

    # ── Loop4 ────────────────────────────────
    "405001": ("802", "007"),  # emma_007 (loop4 opening)
    "405002": ("802", "008"),  # emma_008 (loop4 post_turn)
    "404105": ("804", "003"),  # morrison_s405 (loop4 hall, stage A/B)
    "404180": ("804", "004"),  # morrison_003_turn (loop4 turn_cutscene)
    "405104": ("805", "002"),  # tommy_002 (loop4 office)
    "406104": ("806", "003"),  # vivian_003 (loop4 cabaret)

    # ── Loop5 ────────────────────────────────
    "505001": ("802", "009"),  # emma_009 (loop5 opening)
    "505002": ("802", "010"),  # emma_010 (loop5 post_romance)
    "504103": ("807", "003"),  # jimmy_001 (loop5 kitchen; renumbered)
    "504180": ("807", "004"),  # arrest_cutscene (Zack+Emma+Jimmy, 归 Jimmy 名下作过场)
    "504181": ("807", "005"),  # suspect_suicide_sequence (Jimmy 自杀)
    "505105": ("805", "003"),  # tommy_003 (loop5 office)
    "508112": ("808", "001"),  # anna_001 (loop5 jimmy home)

    # ── Loop6 ────────────────────────────────
    "605001": ("802", "011"),  # emma_011 (loop6 opening)
    "606002": ("801", "001"),  # morrison_house 搜证对话（Zack+Emma，归 Zack）
    "606082": ("811", "001"),  # Whale phone call（Whale 声音唯一登场）
    "606103": ("806", "004"),  # vivian_004 Act 2 (获释走廊)
    "606104": ("806", "005"),  # vivian_004 Act 3 (保险箱)
    "606205": ("808", "002"),  # anna_epilogue + Zack 独白 (归 Anna 名下 Act 4 因 anna 短暂登场)
}

# Expose 段 6 位 ID 映射：旧 6 位前缀 → 新 6 位前缀
EXPOSE_PREFIX_MAP = {
    # Loop1 Rosa Expose: 190001xxx (9 位) → 11xxxx (6 位)
    # 注意位数变化 —— 9 位 → 6 位
    "190001": "11",  # 截断到 6 位新前缀的前 2 位（指证编码 {轮次2}{序号4}）
    "290001": "12",  # Loop2 Tommy Expose
    "390001": "13",  # Loop3 Rosa Expose (真击穿)
    "490001": "14",  # Loop4 Vivian Expose
    "590001": "15",  # Loop5 Jimmy Expose
    "690001": "16",  # Loop6 Morrison Expose
}

# Testimony ID 映射（7 位：{NPC3}{轮次1}{序号3}）
# 旧格式在不同 loop 有不同 ad-hoc 约定，新格式统一为规范 {NPC 801-811}{loop}{seq}。
# 映射表：旧 4 位前缀 → (新 4 位前缀, seq_offset)
# seq_offset 用于同一 NPC 同一 loop 的多个对话组避免冲突（如 Emma 的 _001/_002）
#
# 新前缀计算：NPC(3) + loop(1) = 4 位
# 示例：
#   1001 (Loop1 emma_001) → 8021 + seq offset 0  → 8021001, 8021002, ...
#   1002 (Loop1 emma_002) → 8021 + seq offset 100 → 8021101, 8021102, ...
#   1011 (Loop1 vivian_001) → 8061 + seq offset 0
OLD_TESTIMONY_PREFIX_MAP = {
    # ── Loop1 ──
    "1001": ("8021", 0),    # emma_001 (Emma + loop1, group 1)
    "1002": ("8021", 100),  # emma_002 (Emma + loop1, group 2)
    "1011": ("8061", 0),    # vivian_001
    "1021": ("8031", 0),    # rosa_001
    "1031": ("8041", 0),    # morrison_001

    # ── Loop2 ──
    "2001": ("8022", 0),    # emma_003
    "2002": ("8022", 100),  # emma_004
    "2011": ("8062", 0),    # vivian_002
    "2041": ("8072", 0),    # jimmy_001 (loop2)
    "2051": ("8052", 0),    # tommy_001

    # ── Loop3 ──
    "3001": ("8023", 0),    # emma_005
    "3002": ("8023", 100),  # emma_006
    "3021": ("8033", 0),    # rosa_002
    "3031": ("8043", 0),    # morrison_002
    "3041": ("8073", 0),    # jimmy_002

    # ── Loop4 ──
    "4001": ("8024", 0),    # emma_007
    "4002": ("8024", 100),  # emma_008
    "4011": ("8064", 0),    # vivian_003 / vivian_expose_001 (跨 loop5 引用时也用)
    "4031": ("8044", 0),    # morrison_s405 / morrison_003
    "4051": ("8054", 0),    # tommy_002

    # ── Loop5 ──
    "5001": ("8025", 0),    # emma_009
    "5002": ("8025", 100),  # emma_010
    "5041": ("8075", 0),    # jimmy_001 (loop5)
    "5051": ("8055", 0),    # tommy_003
    "5061": ("8085", 0),    # anna_001

    # ── Loop6 ──
    "6001": ("8026", 0),    # emma_011
    "6011": ("8066", 0),    # vivian_004
    "6031": ("8046", 0),    # morrison_expose
    "6061": ("8086", 0),    # anna_epilogue
}

# ──────────────────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────────────────

def collect_dialogue_ids(content: str) -> list[str]:
    """提取所有 9 位对话 ID（含字母后缀变体）。"""
    # 匹配：9 位数字（可选后跟 -A / -B / -C 或小写字母 / _bridge）
    pattern = re.compile(r'\b(\d{9}(?:[-_][A-Za-z_]+|[a-z])?)\b')
    return pattern.findall(content)


def migrate_dialogue_id(old_id: str, mapping: dict, seq_counter: dict) -> str | None:
    """
    把一个旧 9 位对话 ID（可带后缀）迁移到新 9 位 ID。
    返回新 ID；如果前缀未在 mapping 中则返回 None（保留原 ID）。

    后缀处理（避免冲突）：
    - 无后缀：seq 保持原样（e.g. 010 → 010 → new_prefix + 010）
    - -A / -a：seq 变为 1XX（首位 1 + 原 seq 后 2 位），范围 100-199
    - -B / -b：seq 变为 2XX，范围 200-299
    - -C / -c：seq 变为 3XX
    - 其他小写字母 d-n（用于 Rosa Expose 崩溃段的 039b-039n 类）：
        按 ord(letter)-'a'+1 映射到 {code}XX 范围
        d=4XX, e=5XX, f=6XX, ..., n=14XX (溢出处理)
    - _bridge：seq 变为 9XX
    """
    match = re.match(r'^(\d{9})([-_][A-Za-z_]+|[a-z])?$', old_id)
    if not match:
        return None
    base, suffix = match.group(1), match.group(2)
    old_prefix = base[:6]

    if old_prefix not in mapping:
        return None

    new_npc, new_group = mapping[old_prefix]
    old_seq = base[6:9]  # 原 3 位 seq

    # 无后缀：直接使用原 seq
    if not suffix:
        return f"{new_npc}{new_group}{old_seq}"

    # 计算后缀代码（决定百位数）
    suffix_code = None

    # 归一化：去除 -_ 前缀
    suffix_clean = suffix.lstrip('-_').lower()

    if suffix_clean == 'bridge':
        suffix_code = 9
    elif len(suffix_clean) == 1 and suffix_clean.isalpha():
        # 单字母：a=1, b=2, c=3, d=4, e=5, ..., n=14
        letter_idx = ord(suffix_clean) - ord('a') + 1
        suffix_code = letter_idx
    else:
        # 其他命名后缀（理论上不应出现）
        suffix_code = 8  # 默认归到 8XX 系

    # 新 seq = 后缀代码 × 100 + (原 seq 后 2 位)
    # 例：
    #   605001010-A (old_seq=010, suffix=A=1) → 1*100+10 = 110 → 802011110
    #   605001010-B (suffix=B=2) → 210 → 802011210
    #   605001010-C (suffix=C=3) → 310 → 802011310
    seq_last2 = int(old_seq[-2:])  # 取后 2 位
    new_seq_int = (suffix_code * 100 + seq_last2) % 1000
    return f"{new_npc}{new_group}{new_seq_int:03d}"


def migrate_expose_id(old_id: str) -> str | None:
    """
    把 Expose 9 位 ID（如 190001xxx、290001xxx）迁移到 6 位规范（{轮次2}{序号4}）。
    返回新 ID；若不是 Expose 前缀则返回 None。
    """
    match = re.match(r'^(\d{9})([-_][A-Za-z_]+|[a-z])?$', old_id)
    if not match:
        return None
    base, suffix = match.group(1), match.group(2)
    old_prefix = base[:6]

    if old_prefix not in EXPOSE_PREFIX_MAP:
        return None

    new_prefix_2 = EXPOSE_PREFIX_MAP[old_prefix]  # 如 "11"
    old_seq = base[6:9]  # 原 3 位 sequence

    # 新 ID = {轮次2}{0}{原 sequence 3 位} 共 6 位（第 3 位补 0 以便后续扩展）
    # 字母后缀同样需要扩展——这里暂用简化方案：sequence +100 偏移
    if suffix:
        suffix_offset = ord(suffix[-1].lower()) - ord('a') + 1 if suffix and suffix[-1].isalpha() else 1
        new_seq = f"0{int(old_seq):03d}"  # 4 位：0xxx
        # 用 +1000 偏移避免冲突
        new_seq_int = (int(new_seq) + suffix_offset * 1000) % 10000
        return f"{new_prefix_2}{new_seq_int:04d}"

    return f"{new_prefix_2}0{old_seq}"  # 6 位：{11}{0}{001} = 110001


def migrate_testimony_id(old_id: str) -> str | None:
    """
    把 7 位 testimony ID 迁移到规范格式 {NPC3}{loop1}{seq3}。
    基于 OLD_TESTIMONY_PREFIX_MAP 做前缀查表 + seq_offset 重分配。
    """
    match = re.match(r'^(\d{4})(\d{3})$', old_id)
    if not match:
        return None
    old_prefix4, old_seq3 = match.group(1), match.group(2)
    mapping = OLD_TESTIMONY_PREFIX_MAP.get(old_prefix4)
    if mapping is None:
        return None
    new_prefix4, seq_offset = mapping
    new_seq = int(old_seq3) + seq_offset
    if new_seq >= 1000:
        # 溢出保护——使用取模
        new_seq = new_seq % 1000
    return f"{new_prefix4}{new_seq:03d}"


# ──────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────

def process_file(filepath: Path, dry_run: bool = True) -> dict:
    """处理一个 MD 文件，返回迁移统计 + id_mapping。"""
    content = filepath.read_text(encoding='utf-8')

    stats = {
        "file": str(filepath.relative_to(ROOT)),
        "dialogue_ids_mapped": 0,
        "dialogue_ids_unmapped": [],
        "expose_ids_mapped": 0,
        "expose_ids_unmapped": [],
        "testimony_ids_mapped": 0,
        "testimony_ids_unmapped": [],
    }

    # 收集所有需要替换的 ID（按长度从长到短排序避免部分匹配问题）
    replacements = OrderedDict()
    seq_counter = {}

    # 1. 对话 ID（9 位 + 可选后缀）
    for old_id in re.findall(r'\b\d{9}(?:[-_][A-Za-z_]+|[a-z])?\b', content):
        if old_id in replacements:
            continue
        new_id = migrate_dialogue_id(old_id, DIALOGUE_PREFIX_MAP, seq_counter)
        if new_id:
            replacements[old_id] = new_id
            stats["dialogue_ids_mapped"] += 1
            continue
        new_id = migrate_expose_id(old_id)
        if new_id:
            replacements[old_id] = new_id
            stats["expose_ids_mapped"] += 1
            continue
        stats["dialogue_ids_unmapped"].append(old_id)

    # 2. Testimony ID（7 位，独立扫描）
    for old_id in re.findall(r'\b\d{7}\b', content):
        if old_id in replacements:
            continue
        new_id = migrate_testimony_id(old_id)
        if new_id and old_id != new_id:
            replacements[old_id] = new_id
            stats["testimony_ids_mapped"] += 1

    # 应用替换
    new_content = content
    # 先替换长的（9 位 + 后缀）再替换短的（7 位）避免 "105001001" 被 "1050010" 干扰
    sorted_pairs = sorted(replacements.items(), key=lambda x: -len(x[0]))
    for old_id, new_id in sorted_pairs:
        # 用词边界避免部分替换
        new_content = re.sub(rf'\b{re.escape(old_id)}\b', new_id, new_content)

    if not dry_run and new_content != content:
        # 备份原文件
        backup = filepath.with_suffix(filepath.suffix + '.pre_migration')
        if not backup.exists():
            backup.write_text(content, encoding='utf-8')
        filepath.write_text(new_content, encoding='utf-8')

    stats["replacements"] = dict(replacements)
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', default=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--state-only', action='store_true', help='仅处理 state 文件')
    parser.add_argument('--drafts-only', action='store_true', help='仅处理对话草稿')
    args = parser.parse_args()

    dry_run = not args.apply

    all_stats = []
    all_mappings = {}

    mode = "DRY-RUN（不写文件）" if dry_run else "APPLY（实际执行）"
    print(f"\n{'=' * 60}\n模式: {mode}\n{'=' * 60}\n")

    # 处理对话草稿
    if not args.state_only:
        print("\n── 对话草稿 ──\n")
        for loop_num, filepath in LOOP_FILES.items():
            if not filepath.exists():
                print(f"  跳过（文件不存在）: {filepath.name}")
                continue
            stats = process_file(filepath, dry_run=dry_run)
            all_stats.append(stats)
            all_mappings.update(stats["replacements"])
            print(f"  Loop{loop_num}: 对话 ID {stats['dialogue_ids_mapped']} / Expose ID {stats['expose_ids_mapped']} / Testimony ID {stats['testimony_ids_mapped']}")
            if stats["dialogue_ids_unmapped"]:
                unique_unmapped = list(set(stats["dialogue_ids_unmapped"]))[:5]
                print(f"    ⚠️ 未映射 9 位 ID（前 5 个）: {unique_unmapped}")

    # 处理 state 文件
    if not args.drafts_only:
        print("\n── State 文件（testimony_ids）──\n")
        for loop_num, filepath in STATE_FILES.items():
            if not filepath.exists():
                print(f"  跳过（文件不存在）: {filepath.name}")
                continue
            stats = process_file(filepath, dry_run=dry_run)
            all_stats.append(stats)
            all_mappings.update(stats["replacements"])
            print(f"  loop{loop_num}_state.yaml: Testimony ID {stats['testimony_ids_mapped']}")

    # 输出总映射表
    print(f"\n{'=' * 60}")
    print(f"总映射数: {len(all_mappings)}")
    print(f"{'=' * 60}\n")

    if not dry_run:
        MAPPING_OUT.write_text(
            json.dumps(all_mappings, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"ID 映射表已保存：{MAPPING_OUT}")
    else:
        print("这是 dry-run，未写入任何文件。使用 --apply 执行实际迁移。")


if __name__ == '__main__':
    main()
