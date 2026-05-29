#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_openinloops.py — 一次性填充 SceneConfig.openInLoops

启发式：
  - 场景 sceneId 第二位是它"归属的 Loop"
  - 在归属 Loop 内"开放" ⟺ 该场景有真实内容（firstEnterTalk / NPCs / 非门道具）
  - 此外 ChapterConfig.map2Scenes 中列出的入口场景，强制标记为对应 Loop 开放
  - 已有非空 openInLoops 的不覆盖（保留人工标记）

不做：
  - 沿 door 遍历推可达性（door 的 mapSpritePath 是位置名，与 sceneId 映射脆）
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data', 'table')

# 从 location.Name 里捞 "(L1 xxx)" / "L1 ..." / "L1/L2 ..." 等 Loop 标注
LOOP_TAG_RE = re.compile(r'L(\d)')


def load(name):
    with open(os.path.join(DATA_DIR, name + '.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(DATA_DIR, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    scenes = load('SceneConfig')
    items = load('ItemStaticData')
    chapters = load('ChapterConfig')

    door_ids = {str(it['id']) for it in items if str(it.get('itemType', '')) == '5'}
    print(f"[info] 识别出 {len(door_ids)} 个门道具")

    scene_by_id = {str(s['sceneId']): s for s in scenes}

    # ── pass 1: 按内容标记 ──
    # sceneId 编码：
    #   1101-16XX → unit1, loop=sceneId[1]
    #   10XX → 共享/AVG 专用，loop 从 location.Name 的 "L1"/"L2"... 标注里找
    pass1_marked = 0
    pass1_tagged = 0
    for s in scenes:
        sid = str(s['sceneId'])
        if len(sid) != 4:
            continue
        if s.get('openInLoops'):
            continue

        item_ids = [str(i) for i in (s.get('ItemIDs') or [])]
        non_door_items = [i for i in item_ids if i not in door_ids]
        has_content = bool(s.get('firstEnterTalk')) \
            or bool(s.get('NPCInfos')) \
            or bool(non_door_items)

        loop_digit = sid[1]
        if loop_digit != '0':
            # 11XX-16XX: 直接用 sceneId 第二位
            if has_content:
                s['openInLoops'] = [int(loop_digit)]
                pass1_marked += 1
        else:
            # 10XX: 看 location.Name 里有没有 "L1" 标注
            loc = s.get('location', {})
            name = ''
            if isinstance(loc, dict):
                names = loc.get('Name') or []
                name = ' '.join([n for n in names if n])
            loops = sorted({int(m) for m in LOOP_TAG_RE.findall(name) if 1 <= int(m) <= 6})
            if loops:
                s['openInLoops'] = loops
                pass1_tagged += 1
            elif has_content:
                # 没标注但有内容 → 至少标 unit 第一个 Loop？保守起见跳过
                pass

    # ── pass 2: map2Scenes 入口强制 ──
    pass2_marked = 0
    for c in chapters:
        cid = str(c.get('id', ''))
        if len(cid) != 3:
            continue
        loop = int(cid[2])
        for m2s in (c.get('map2Scenes') or []):
            target_sid = str(m2s.get('sceneId', ''))
            target = scene_by_id.get(target_sid)
            if not target:
                continue
            opens = target.setdefault('openInLoops', [])
            if loop not in opens:
                opens.append(loop)
                pass2_marked += 1

    save('SceneConfig', scenes)

    # ── stats ──
    print()
    print(f"[pass1] 按内容标记: {pass1_marked} 个场景")
    print(f"[pass2] 入口强制 (map2Scenes): {pass2_marked} 个新增")
    print()
    by_loop = {}
    for s in scenes:
        for l in (s.get('openInLoops') or []):
            by_loop.setdefault(l, []).append(str(s['sceneId']))
    print("各 Loop 开放场景数:")
    for l in sorted(by_loop):
        ids = sorted(by_loop[l])
        sample = ', '.join(ids[:6]) + ('...' if len(ids) > 6 else '')
        print(f"  L{l}: {len(ids)} 个 ({sample})")

    empty = [s['sceneId'] for s in scenes if not s.get('openInLoops')]
    print()
    print(f"仍未标记开放（openInLoops=[]）: {len(empty)} 个")
    if empty:
        print(f"  样例: {', '.join(str(x) for x in empty[:10])}{'...' if len(empty) > 10 else ''}")


if __name__ == '__main__':
    main()
