#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
merge_unit2.py — 从 preview 老备份中只把 Unit2 数据合并到 v2 当前表

策略：
  · 仅处理 id 以 '2' 开头的条目
  · 同 id 已在 v2：跳过（Unity 优先）
  · 仅 preview 有的：reshape 后追加
  · SceneConfig 扁平字段（sceneName/backgroundImage 等）→ Unity 嵌套 location
  · 同时给新增 Scene 自动生成对应的 LocationConfig 条目
  · 保留 preview 已填的 ArtRequirement
  · 给新增 Scene 设默认 sceneCategory=0, openInLoops=[]
  · 备份当前文件再写

ExposeData 用关联反查（testimony 或 item 引用 Unit2 ID）匹配 Unit2 expose
"""

import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from state_to_preview import fix_json  # noqa

PREV = os.path.join(HERE, 'data', 'table_preview_legacy_backup')
CURR = os.path.join(HERE, 'data', 'table')

# 备份目录
TS = time.strftime('%Y%m%d_%H%M%S')

# 双语字段（不是数组的需补成数组）
BILINGUAL_FIELDS = {'Name', 'description', 'words', 'testimony', 'truth',
                    'shortDesc', 'shortTruth', 'chapterTitle', 'chapterBrief',
                    'chapterGoal', 'summaryTitle', 'summaryContent',
                    'newDoubtTitle', 'newDoubtContent', 'itemUseDes'}


def load_prev(name):
    with open(os.path.join(PREV, name + '.json'), encoding='utf-8') as f:
        return json.loads(fix_json(f.read()))


def load_curr(name):
    with open(os.path.join(CURR, name + '.json'), encoding='utf-8') as f:
        return json.load(f)


def save_curr(name, data):
    p = os.path.join(CURR, name + '.json')
    shutil.copy2(p, p + f'.bak.{TS}')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def reshape_scene(s):
    """preview 扁平 SceneConfig → Unity 嵌套 location 结构"""
    sid = s['sceneId']
    out = {
        'sceneId': sid,
        'location': {
            'id': sid,
            'Name': [s.get('sceneName', ''), s.get('sceneNameEn', '')],
            'sceneType': s.get('sceneType', '1'),
            'backgroundImage': s.get('backgroundImage', ''),
        },
    }
    if s.get('backgroundMusic'):
        out['location']['ambientSound'] = s['backgroundMusic']
    # 保留 NPCInfos / ItemIDs / firstEnterTalk
    if s.get('NPCInfos'):
        out['NPCInfos'] = s['NPCInfos']
    if s.get('ItemIDs'):
        out['ItemIDs'] = s['ItemIDs']
    if s.get('firstEnterTalk'):
        out['firstEnterTalk'] = s['firstEnterTalk']
    # 保留 ArtRequirement / Chapter / note
    if s.get('ArtRequirement'):
        out['ArtRequirement'] = s['ArtRequirement']
    else:
        out['ArtRequirement'] = ''
    if s.get('Chapter'):
        out['Chapter'] = s['Chapter']
    if s.get('note'):
        out['note'] = s['note']
    # 设计期字段默认
    out['openInLoops'] = []
    out['sceneCategory'] = 0
    return out


def merge_simple(table_name, pk='id', id_prefix='2', reshape_fn=None, post_fn=None):
    """通用 merge：preview 中 pk 以 id_prefix 开头且当前不存在的 → 追加"""
    prev = load_prev(table_name)
    curr = load_curr(table_name)
    curr_ids = {str(e.get(pk)) for e in curr}
    added = 0
    new_entries = []
    for e in prev:
        eid = str(e.get(pk, ''))
        if not eid.startswith(id_prefix):
            continue
        if eid in curr_ids:
            continue
        new_e = reshape_fn(e) if reshape_fn else e
        if post_fn:
            post_fn(new_e)
        new_entries.append(new_e)
        added += 1
    if added > 0:
        curr.extend(new_entries)
        save_curr(table_name, curr)
    print(f'  {table_name}: +{added} 条 (preview 有 {len([e for e in prev if str(e.get(pk,"")).startswith(id_prefix)])} 条，curr 已有 {len([i for i in curr_ids if i.startswith(id_prefix)])} 条)')
    return added, new_entries


def merge_scene_config():
    """SceneConfig 特殊：要 reshape，同时给 LocationConfig 加新条目"""
    added, new_scenes = merge_simple('SceneConfig', pk='sceneId', id_prefix='2',
                                      reshape_fn=reshape_scene)
    # 给每个新增 Scene 添加 LocationConfig 条目
    if new_scenes:
        loc = load_curr('LocationConfig')
        loc_ids = {str(e.get('id')) for e in loc}
        loc_added = 0
        for s in new_scenes:
            sid = str(s['sceneId'])
            if sid in loc_ids:
                continue
            inline_loc = s.get('location', {})
            loc.append({
                'id': sid,
                'Name': inline_loc.get('Name', ['', '']),
                'sceneType': inline_loc.get('sceneType', '1'),
                'backgroundImage': inline_loc.get('backgroundImage', ''),
                'ambientSound': inline_loc.get('ambientSound', ''),
            })
            loc_added += 1
        if loc_added > 0:
            save_curr('LocationConfig', loc)
        print(f'  LocationConfig: +{loc_added} 条（联动新增）')


def merge_expose():
    """ExposeData 特殊：通过 testimony/item 引用反查 Unit2"""
    prev = load_prev('ExposeData')
    curr = load_curr('ExposeData')
    curr_ids = {str(e.get('id')) for e in curr}

    # Unit2 关联 IDs: TestimonyItem 以 2 开头 或 Item 以 2 开头
    def is_unit2_expose(e):
        t = str(e.get('testimony', ''))
        if t and t != '0' and t.startswith('2'):
            return True
        for it in (e.get('item') or []):
            if str(it).startswith('2'):
                return True
        return False

    added = 0
    new_entries = []
    # ExposeData.id 可能跟 Unity 撞号 → 重新编号
    max_id = max([int(str(e.get('id', 0))) for e in curr] + [0])
    next_id = max_id + 1
    for e in prev:
        if not is_unit2_expose(e):
            continue
        # 强制改 id 避开冲突
        new_e = dict(e)
        new_e['id'] = str(next_id)
        new_entries.append(new_e)
        next_id += 1
        added += 1
    if added > 0:
        curr.extend(new_entries)
        save_curr('ExposeData', curr)
    print(f'  ExposeData: +{added} 条 (按 Unit2 关联反查；id 重新编号避冲突)')


def main():
    print(f'[merge] backup suffix: .bak.{TS}')
    print(f'[merge] preview source: {PREV}')
    print(f'[merge] target: {CURR}')
    print()

    merge_scene_config()
    merge_simple('ItemStaticData', id_prefix='2')
    merge_simple('NPCStaticData', id_prefix='2')
    merge_simple('DoubtConfig', id_prefix='2')
    merge_simple('TestimonyItem', id_prefix='2')
    merge_simple('Testimony', id_prefix='2')
    merge_simple('ChapterConfig', id_prefix='2')  # 201-206 直接 merge
    merge_expose()

    print()
    print('[done] 服务需要重启才能读到新数据')


if __name__ == '__main__':
    main()
