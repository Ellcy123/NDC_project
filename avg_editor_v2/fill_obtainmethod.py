#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_obtainmethod.py — 给 ItemStaticData 加 obtainMethod 字段（设计期，不动 Unity）

枚举：
  manual (默认) — 玩家场景内点击拾取
  dialog        — Talk script=3 (get) 自动给
  auto          — 开局/事件自动获得（暂不自动识别，留待人工标）

反查策略：
  · 扫 Talk 表 script=3 且 Parameters[0].ParameterInt 指向 Item → 标 dialog
  · 已有非 manual 值的不覆盖（保留人工标记）
  · 同步加 LocationConfig.id 不存在的别撞库

幂等：可重复跑，只会把新的 dialog 标识应用。
"""

import json
import os
import shutil
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'table')

# Talk.script 中表示"获取道具"的动作
GET_ITEM_SCRIPTS = {'3', 'get', 'Get'}


def load(name):
    with open(os.path.join(DATA, name + '.json'), encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    p = os.path.join(DATA, name + '.json')
    shutil.copy2(p, p + f'.bak.{time.strftime("%Y%m%d_%H%M%S")}')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    items = load('ItemStaticData')
    talks = load('Talk')
    item_by_id = {str(it['id']): it for it in items}

    # 先保证字段存在
    field_added = 0
    for it in items:
        if 'obtainMethod' not in it:
            it['obtainMethod'] = 'manual'
            field_added += 1

    # 反查：Talk.script=3 → ParameterInt → Item
    dialog_ids = set()
    for t in talks:
        sc = str(t.get('script', ''))
        if sc not in GET_ITEM_SCRIPTS:
            continue
        params = t.get('Parameters') or []
        for p in params:
            iid = str(p.get('ParameterInt', ''))
            if iid and iid != '0' and iid in item_by_id:
                dialog_ids.add(iid)

    # 应用：仅当当前是 manual（未人工标记）时改为 dialog
    changed = 0
    for iid in dialog_ids:
        it = item_by_id[iid]
        if it.get('obtainMethod', 'manual') == 'manual':
            it['obtainMethod'] = 'dialog'
            changed += 1

    save('ItemStaticData', items)

    # 统计
    from collections import Counter
    dist = Counter(it.get('obtainMethod', 'manual') for it in items)
    print(f'[字段添加] obtainMethod 给 {field_added} 个道具补默认值')
    print(f'[反查] Talk script=get 引用到 {len(dialog_ids)} 个道具')
    print(f'[应用] 新标 dialog: {changed} 个')
    print()
    print('当前分布:')
    for m in ('manual', 'dialog', 'auto'):
        print(f'  {m}: {dist.get(m, 0)}')

    # 展示几个 dialog 样例
    if changed > 0:
        print()
        print('新标 dialog 样例:')
        cnt = 0
        for iid in sorted(dialog_ids):
            it = item_by_id[iid]
            if it.get('obtainMethod') != 'dialog':
                continue
            name = (it.get('Name') or [''])[0]
            print(f'  #{iid} {name}')
            cnt += 1
            if cnt >= 10:
                break


if __name__ == '__main__':
    main()
