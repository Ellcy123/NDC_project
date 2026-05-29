#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_from_state.py — 从 D:/NDC_project/剧情设计/Unit2/state/loop{N}_state.yaml 读取
   场景类型，精准设置 SceneConfig.sceneCategory（覆盖之前的启发式猜测）

state.yaml 中的 scene_id（如 2004）对应 config 的 sceneId（如 2104）：
   config_id = "2" + str(loop_num) + state_id[-2:]

state type → sceneCategory:
   cutscene             → 1 (对话)
   timed_exploration    → 2 (探索)
   free_exploration     → 2 (探索)
   expose_scene         → 3 (指证)
   其他/缺失            → 不动
"""

import os
import re
import json
import sys

STATE_DIR = r"D:\NDC_project\剧情设计\Unit2\state"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'table')

TYPE_MAP = {
    'cutscene': 1,
    'timed_exploration': 2,
    'free_exploration': 2,
    'expose_scene': 3,
}

# 用正则不依赖 yaml 库
RE_SCENE_ID = re.compile(r'^\s*-?\s*id:\s*(\d+)', re.MULTILINE)
RE_SCENE_BLOCK = re.compile(
    r'^\s*-?\s*id:\s*(\d{4})[^\n]*\n((?:[ ]{4,}.+\n)+)',
    re.MULTILINE
)
RE_TYPE = re.compile(r'^\s+type:\s*([a-z_]+)', re.MULTILINE)
RE_EXPOSE_SCENE = re.compile(r'^expose:\s*\n(?:.+\n)*?\s*scene_id:\s*(\d+)', re.MULTILINE)
RE_OPENING_SCENE = re.compile(r'^opening:\s*\n(?:.+\n)*?\s*scene_id:\s*(\d+)', re.MULTILINE)


def parse_state(loop_num):
    p = os.path.join(STATE_DIR, f'loop{loop_num}_state.yaml')
    if not os.path.exists(p):
        return {}
    with open(p, encoding='utf-8') as f:
        text = f.read()

    result = {}  # state_id → category

    # 解析 scenes 列表里每个 - id: XXXX 后跟 type:
    # 简化：先找所有 - id 位置，然后在后续 200 字符内找 type
    for m in re.finditer(r'-\s*id:\s*(\d{4})\s*\n', text):
        sid = m.group(1)
        block_end = m.end() + 600
        block_text = text[m.end():block_end]
        # 找 type 字段（同缩进的 type:）
        type_m = re.search(r'\s+type:\s*([a-z_]+)', block_text)
        if type_m:
            t = type_m.group(1)
            cat = TYPE_MAP.get(t)
            if cat:
                result[sid] = cat

    # opening.scene_id 不是 cutscene 标记！只是表示开篇发生在那个场景
    # 场景本身的 type 必须从 scenes: 数组里的独立 - id / type 取
    # 同理 expose.scene_id 也不强制覆盖，scenes 数组里的 type=expose_scene 才算

    return result


def state_id_to_config_id(state_id, loop_num):
    """state 2004 + loop 1 → config 2104"""
    s = str(state_id)
    if len(s) != 4 or not s.startswith('2'):
        return None
    return '2' + str(loop_num) + s[-2:]


def main():
    with open(os.path.join(DATA, 'SceneConfig.json'), encoding='utf-8') as f:
        scenes = json.load(f)
    by_id = {str(s['sceneId']): s for s in scenes}

    changes = {1: 0, 2: 0, 3: 0}
    no_match = []
    by_loop_stats = {}

    for loop_num in range(1, 7):
        state_cats = parse_state(loop_num)
        by_loop_stats[loop_num] = {'parsed': len(state_cats), 'applied': 0}
        for state_id, cat in state_cats.items():
            config_id = state_id_to_config_id(state_id, loop_num)
            if not config_id:
                continue
            scene = by_id.get(config_id)
            if not scene:
                no_match.append((loop_num, state_id, config_id))
                continue
            old = int(scene.get('sceneCategory') or 0)
            scene['sceneCategory'] = cat
            if old != cat:
                changes[cat] += 1
                by_loop_stats[loop_num]['applied'] += 1

    # 备份再保存
    import time, shutil
    p = os.path.join(DATA, 'SceneConfig.json')
    shutil.copy2(p, p + f'.bak.{time.strftime("%Y%m%d_%H%M%S")}')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

    print(f'[ok] 改动:')
    print(f'  → 对话 (cat=1): {changes[1]}')
    print(f'  → 探索 (cat=2): {changes[2]}')
    print(f'  → 指证 (cat=3): {changes[3]}')
    print()
    print(f'各 Loop 解析:')
    for lp, st in by_loop_stats.items():
        print(f'  L{lp}: state 解析 {st["parsed"]} 个，应用 {st["applied"]} 个')
    if no_match:
        print()
        print(f'[WARN] state 提到但 config 找不到的 ({len(no_match)} 个):')
        for lp, sid, cid in no_match[:10]:
            print(f'  L{lp} state {sid} → expected config {cid} (缺)')


if __name__ == '__main__':
    main()
