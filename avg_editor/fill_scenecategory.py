#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_scenecategory.py — 一次性填充 SceneConfig.sceneCategory

枚举：
  0 = 未分类
  1 = 对话场景 (dialogue)  无可点 NPC/道具，进场即对话
  2 = 探索场景 (exploration) 含可点 NPC 或非门道具
  3 = 指证场景 (expose)   纯指证（目前没有对应场景，全靠人工标）

启发式：
  · 有非门道具 或 NPCInfos → 2 探索
  · 仅 firstEnterTalk → 1 对话
  · 啥都没有 → 0 未分类（包括只放门的过道）

已有非 0 值的不覆盖（保留人工标记）。
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data', 'table')


def load(name):
    with open(os.path.join(DATA_DIR, name + '.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(DATA_DIR, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    scenes = load('SceneConfig')
    items = load('ItemStaticData')

    door_ids = {str(it['id']) for it in items if str(it.get('itemType', '')) == '5'}
    print(f"[info] 识别出 {len(door_ids)} 个门道具")

    changed = 0
    for s in scenes:
        if int(s.get('sceneCategory', 0)) != 0:
            continue  # 已有人工标记

        item_ids = [str(i) for i in (s.get('ItemIDs') or [])]
        non_door_items = [i for i in item_ids if i not in door_ids]
        has_npc = bool(s.get('NPCInfos'))
        has_fet = bool(s.get('firstEnterTalk'))

        if non_door_items or has_npc:
            s['sceneCategory'] = 2  # 探索
        elif has_fet:
            s['sceneCategory'] = 1  # 对话
        # else: 0 未分类

        if s['sceneCategory'] != 0:
            changed += 1

    save('SceneConfig', scenes)

    # stats
    from collections import Counter
    dist = Counter(int(s.get('sceneCategory', 0)) for s in scenes)
    labels = {0: '未分类', 1: '[对话]', 2: '[探索]', 3: '[指证]'}
    print()
    print(f"[填充完成] 本次新标 {changed} 个场景")
    print()
    print("当前分布:")
    for cat in (0, 1, 2, 3):
        print(f"  {labels[cat]:8s}: {dist.get(cat, 0)} 个")


if __name__ == '__main__':
    main()
