#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
seed.py — 一次性迁移脚本

从 d:/NDC/Assets/table/*.json 拷贝活跃表到 d:/NDC_project/avg_editor/data/table/，
顺手给指定表添加设计期字段（ArtRequirement / openInLoops）。

设计期字段的值默认空，后续在 web UI 里填。

幂等策略：默认不覆盖已存在的目标文件。要重新种用 --force。
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.normpath(os.path.join(HERE, '..', 'preview_new2'))
sys.path.insert(0, PREVIEW_DIR)
from state_to_preview import fix_json  # noqa: E402

SRC_DIR = r"D:\NDC\Assets\table"
DST_DIR = os.path.join(HERE, 'data', 'table')

# 11 张活跃表（弃用 6 张：Event / ExposeTalk / Task / TaskConfig / TimeLineEvent / UITextConfig）
ACTIVE_TABLES = [
    'ChapterConfig', 'ChapterStepConfig', 'DayTimeConfig', 'DoubtConfig',
    'ExposeData', 'GameFlowConfig', 'ItemStaticData', 'LocationConfig',
    'MapConfig', 'NPCLoopData', 'NPCStaticData', 'SceneConfig', 'Talk',
    'Testimony', 'TestimonyItem',
]

# 给每张表加上设计期字段（值为默认空）。键 = 字段名，值 = 默认值。
DESIGN_FIELDS = {
    'NPCStaticData':  {'ArtRequirement': ''},
    'ItemStaticData': {'ArtRequirement': '', 'obtainMethod': 'manual'},
    'SceneConfig':    {'ArtRequirement': '', 'openInLoops': [], 'sceneCategory': 0},
    'MapConfig':      {'ArtRequirement': ''},
    'ChapterConfig':  {'ArtRequirement': ''},
}


def load_official(name):
    p = os.path.join(SRC_DIR, name + '.json')
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        raw = f.read()
    return json.loads(fix_json(raw))


def add_design_fields(name, data):
    fields = DESIGN_FIELDS.get(name)
    if not fields or not isinstance(data, list):
        return data
    for entry in data:
        for k, default in fields.items():
            if k not in entry:
                entry[k] = default if not isinstance(default, list) else list(default)
    return data


def save_clean(name, data):
    p = os.path.join(DST_DIR, name + '.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true', help='覆盖已存在的目标文件')
    args = ap.parse_args()

    if not os.path.isdir(SRC_DIR):
        print(f"[ERR] 源目录不存在: {SRC_DIR}")
        sys.exit(1)

    os.makedirs(DST_DIR, exist_ok=True)

    seeded = 0
    skipped = 0
    failed = 0
    for name in ACTIVE_TABLES:
        dst = os.path.join(DST_DIR, name + '.json')
        if os.path.exists(dst) and not args.force:
            print(f"  skip {name} (已存在；--force 覆盖)")
            skipped += 1
            continue
        data = load_official(name)
        if data is None:
            print(f"  [WARN] 源缺失: {name}.json")
            failed += 1
            continue
        data = add_design_fields(name, data)
        save_clean(name, data)
        n = len(data) if isinstance(data, list) else 'obj'
        extra = list(DESIGN_FIELDS.get(name, {}).keys())
        extra_note = f"  + {','.join(extra)}" if extra else ''
        print(f"  seed {name}: {n} entries{extra_note}")
        seeded += 1

    print()
    print(f"[seed] {seeded} 写入, {skipped} 跳过, {failed} 失败")
    print(f"[seed] 目标: {DST_DIR}")


if __name__ == '__main__':
    main()
