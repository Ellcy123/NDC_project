#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_new_scenes.py — 给刚 merge 进来的 Unit2 场景填 openInLoops + sceneCategory

启发式：
  · openInLoops: 从 sceneId 第二位推 loop（21XX→[1], 22XX→[2]...）
  · sceneCategory:
    - 有非门道具 或 NPCs → 2 探索
    - 仅 firstEnterTalk → 1 对话
    - 其他 → 0 未分类（探索场景里多数情况）
  · 只动 openInLoops==[] 的条目（不覆盖已填值）
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'table')


def load(name):
    with open(os.path.join(DATA, name + '.json'), encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(DATA, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    scenes = load('SceneConfig')
    items = load('ItemStaticData')
    door_ids = {str(it['id']) for it in items if str(it.get('itemType', '')) == '5'}

    op_fill = 0
    cat_fill = 0
    for s in scenes:
        sid = str(s.get('sceneId', ''))
        if len(sid) != 4:
            continue

        # openInLoops 填充
        if not (s.get('openInLoops') or []):
            loop_digit = sid[1]
            if loop_digit != '0':
                s['openInLoops'] = [int(loop_digit)]
                op_fill += 1
            # 10XX/20XX 共享场景跳过，让人工标

        # sceneCategory 填充
        if Number_or_zero(s.get('sceneCategory')) == 0:
            item_ids = [str(i) for i in (s.get('ItemIDs') or [])]
            has_any_item = len(item_ids) > 0  # 含门
            has_npc = bool(s.get('NPCInfos'))
            opens = s.get('openInLoops') or []
            if has_any_item or has_npc:
                s['sceneCategory'] = 2  # 探索
                cat_fill += 1
            elif opens:
                # 开放但无可点内容 → 默认对话场景（AVG 专用）
                s['sceneCategory'] = 1
                cat_fill += 1
            # 既不开放又啥都没有就留 0（纯地点定义）

    save('SceneConfig', scenes)
    print(f'[ok] openInLoops 新填: {op_fill}')
    print(f'[ok] sceneCategory 新填: {cat_fill}')

    # 统计 Unit2 各 Loop
    u2 = [s for s in scenes if str(s.get('sceneId', '')).startswith('2')]
    from collections import Counter
    by_loop = Counter()
    for s in u2:
        for l in (s.get('openInLoops') or []):
            by_loop[l] += 1
    print()
    print('Unit2 各 Loop 场景数:')
    for l in sorted(by_loop):
        print(f'  L{l}: {by_loop[l]} 个')


def Number_or_zero(v):
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


if __name__ == '__main__':
    main()
