#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
seed_artassets.py — 从 SceneConfig.location.backgroundImage 抽出独立美术资源

输出 data/table/ArtAssetConfig.json（仅设计期，不同步 Unity）
- id = 完整图片路径（作 key，跨 Loop 同图归并）
- displayName = 文件名 + 中文地点名（首个引用它的场景）
- ArtRequirement = 空（待填）

幂等：默认不覆盖已有；--force 重写。
"""

import argparse
import json
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data', 'table')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    out_path = os.path.join(DATA_DIR, 'ArtAssetConfig.json')
    if os.path.exists(out_path) and not args.force:
        print(f"[skip] {out_path} 已存在，--force 覆盖")
        return

    with open(os.path.join(DATA_DIR, 'SceneConfig.json'), encoding='utf-8') as f:
        scenes = json.load(f)

    # 按 backgroundImage 聚合
    groups = OrderedDict()
    for s in scenes:
        loc = s.get('location', {})
        if not isinstance(loc, dict):
            continue
        img = loc.get('backgroundImage', '') or ''
        if not img:
            continue
        if img not in groups:
            name = (loc.get('Name') or [''])[0]
            filename = os.path.basename(img.replace('\\', '/'))
            groups[img] = {
                'id': img,
                'displayName': f"{filename} · {name}",
                'category': 'scene_bg',
                'ArtRequirement': '',
                '_firstSceneId': str(s['sceneId']),
            }

    # 输出
    assets = list(groups.values())
    for a in assets:
        a.pop('_firstSceneId', None)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    print(f"[ok] 写入 {len(assets)} 个资源到 {out_path}")
    print()
    print("样例:")
    for a in assets[:5]:
        print(f"  {a['displayName']}")


if __name__ == '__main__':
    main()
