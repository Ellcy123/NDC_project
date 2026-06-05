#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
config-edit 自校验闸门（基线对比模式）。
校验 avg_editor_v2/data/table 下所有表：JSON 可解析 + 跨表外键完整 + ID 编码 + 关键语言规则。

设计要点：表里有历史欠债（既有断链），所以闸门不是"必须全对"，而是"不许改坏"。
  改动前：python validate.py --save  .ce_baseline.json   # 记录当前问题基线
  改动后：python validate.py --compare .ce_baseline.json  # 只拦【新增】的 ERROR
仅查看：python validate.py                               # 打全量报告，退出码恒 0

退出码：--compare 且出现【新增 ERROR】→ 1；其余 → 0。
"""
import json, os, re, sys

TABLE_DIR = os.environ.get(
    'NDC_TABLE_DIR',
    r'D:\NDC_project\avg_editor_v2\data\table')

ERRORS, WARNS = [], []
def err(m):  ERRORS.append(m)
def warn(m): WARNS.append(m)

def load(name):
    p = os.path.join(TABLE_DIR, name + '.json')
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        err(f'[{name}] JSON 解析失败: {e}')
        return None

def ids(rows, pk='id'):
    return set(str(r.get(pk)) for r in rows) if rows else set()

def main():
    T = {}
    for fn in os.listdir(TABLE_DIR):
        if fn.endswith('.json') and '.bak.' not in fn:
            T[fn[:-5]] = load(fn[:-5])

    # ---- 主键集合 ----
    item_ids  = ids(T.get('ItemStaticData') or [])
    npc_ids   = ids(T.get('NPCStaticData') or [])
    scene_ids = ids(T.get('SceneConfig') or [], 'sceneId')
    talk_ids  = ids(T.get('Talk') or [])
    tit_ids   = ids(T.get('TestimonyItem') or [])
    expose_ids= ids(T.get('ExposeData') or [])
    bg_ids    = ids(T.get('ArtAssetConfig') or [])

    # ---- ItemStaticData 自引用 ----
    for it in (T.get('ItemStaticData') or []):
        for f in ('analysedEvidence', 'beforeAnalysedEvidence'):
            v = str(it.get(f) or '').strip()
            if v and v not in item_ids:
                err(f'[ItemStaticData {it.get("id")}] {f}={v} 指向不存在的物品')
        for v in (it.get('combineParameter') or []):
            if str(v).strip() and str(v) not in item_ids:
                err(f'[ItemStaticData {it.get("id")}] combineParameter {v} 不存在')

    # ---- SceneConfig ----
    for s in (T.get('SceneConfig') or []):
        sid = s.get('sceneId')
        for iid in (s.get('ItemIDs') or []):
            if str(iid) not in item_ids:
                warn(f'[SceneConfig {sid}] ItemIDs {iid} 不在 ItemStaticData（装饰物可忽略）')
        bg = (s.get('location') or {}).get('backgroundImage') or s.get('backgroundImage')
        if bg and str(bg) not in bg_ids:
            warn(f'[SceneConfig {sid}] 背景图未登记到 ArtAssetConfig: {str(bg).split(chr(92))[-1]}')
        # 设计期字段
        if 'isOpen' in s and not isinstance(s['isOpen'], bool):
            warn(f'[SceneConfig {sid}] isOpen 应为 true/false')

    # ---- ExposeData ----
    for e in (T.get('ExposeData') or []):
        t = str(e.get('testimony') or '').strip()
        if t and t != '0' and t not in tit_ids:
            err(f'[ExposeData {e.get("id")}] testimony={t} 不在 TestimonyItem')
        for iid in (e.get('item') or []):
            if str(iid).strip() and str(iid) not in item_ids:
                err(f'[ExposeData {e.get("id")}] item {iid} 不在 ItemStaticData')
        tk = str(e.get('talkId') or '').strip()
        if tk and talk_ids and tk not in talk_ids:
            warn(f'[ExposeData {e.get("id")}] talkId={tk} 不在 Talk（Talk 走 AVG 管线，可能尚未 sync）')

    # ---- DoubtConfig ----
    TYPE_TARGET = {'1': item_ids, 'Item': item_ids}  # type=1/Item → 物品；其余多为证词
    for d in (T.get('DoubtConfig') or []):
        for c in (d.get('condition') or []):
            ctype = str(c.get('type'))
            param = str(c.get('param') or '').strip()
            if not param:
                continue
            if ctype in ('1', 'Item'):
                if param not in item_ids:
                    err(f'[DoubtConfig {d.get("id")}] condition Item param={param} 不在 ItemStaticData')
            else:
                if param not in tit_ids and param not in item_ids:
                    warn(f'[DoubtConfig {d.get("id")}] condition param={param} 既不在 TestimonyItem 也不在 ItemStaticData')

    # ---- Testimony.evidenceItem → TestimonyItem ----
    for t in (T.get('Testimony') or []):
        for ev in (t.get('evidenceItem') or []):
            eid = str(ev.get('id') if isinstance(ev, dict) else ev)
            if eid and eid not in tit_ids:
                warn(f'[Testimony {t.get("id")}] evidenceItem {eid} 不在 TestimonyItem')

    # ---- ChapterConfig ----
    for ch in (T.get('ChapterConfig') or []):
        cid = ch.get('id')
        isc = str(ch.get('initScene') or '').strip()
        if isc and scene_ids and isc not in scene_ids:
            err(f'[ChapterConfig {cid}] initScene={isc} 不在 SceneConfig')
        enp = str(ch.get('exposeNpcId') or '').strip()
        if enp and enp not in npc_ids:
            err(f'[ChapterConfig {cid}] exposeNpcId={enp} 不在 NPCStaticData')
        for sc in (ch.get('map2Scenes') or []):
            if str(sc).strip() and str(sc) not in scene_ids:
                warn(f'[ChapterConfig {cid}] map2Scenes {sc} 不在 SceneConfig')

    # ---- ArtAssetConfig（新表）----
    for a in (T.get('ArtAssetConfig') or []):
        sk = a.get('sceneKind')
        if a.get('category', 'scene_bg') == 'scene_bg' and sk not in ('explore', 'dialogue'):
            warn(f'[ArtAssetConfig {a.get("displayName")}] sceneKind="{sk}" 非 explore/dialogue')
        for ev in (a.get('events') or []):
            if not ev.get('name'):
                warn(f'[ArtAssetConfig {a.get("displayName")}] 有 event 缺 name')

    # ---- 语言规则轻量 lint ----
    for ti in (T.get('TestimonyItem') or []):
        for f in ('shortDesc', 'shortTruth'):
            v = ti.get(f)
            txt = v[0] if isinstance(v, list) and v else (v if isinstance(v, str) else '')
            if re.search(r'\[\d{1,2}[:：]\d{2}', str(txt)):
                warn(f'[TestimonyItem {ti.get("id")}] {f} 含时间前缀 "{txt[:20]}"——时间应由 triggerParam/TimeLineEvent 渲染')

    # ---- 模式分发 ----
    args = sys.argv[1:]
    mode = None; basefile = '.ce_baseline.json'
    if '--save' in args:
        mode = 'save'
        i = args.index('--save')
        if i + 1 < len(args) and not args[i+1].startswith('--'): basefile = args[i+1]
    elif '--compare' in args:
        mode = 'compare'
        i = args.index('--compare')
        if i + 1 < len(args) and not args[i+1].startswith('--'): basefile = args[i+1]

    print(f'校验目录: {TABLE_DIR}  表数量: {len(T)}')
    print(f'当前: ERROR {len(ERRORS)} / WARN {len(WARNS)}')

    if mode == 'save':
        with open(basefile, 'w', encoding='utf-8') as f:
            json.dump({'errors': ERRORS, 'warns': WARNS}, f, ensure_ascii=False, indent=2)
        print(f'\n📌 已写基线 {basefile}（记录改动前的既有问题）。改完用 --compare 比对。')
        sys.exit(0)

    if mode == 'compare':
        try:
            base = json.load(open(basefile, encoding='utf-8'))
        except Exception as e:
            print(f'\n[!] 读不到基线 {basefile}: {e}（改动前忘了 --save？）'); sys.exit(0)
        base_err = set(base.get('errors', []))
        new_err = [m for m in ERRORS if m not in base_err]
        fixed    = [m for m in base_err if m not in set(ERRORS)]
        if fixed:
            print(f'\n✅ 顺手修复了 {len(fixed)} 条既有问题。')
        if new_err:
            print(f'\n❌ 本次改动【新增】{len(new_err)} 条 ERROR —— 闸门拦截，请修复或回滚:')
            for m in new_err: print('  ', m)
            sys.exit(1)
        print('\n✅ 未引入任何新的断链/破坏。本次改动安全放行。')
        sys.exit(0)

    # 默认：全量报告（不阻断）
    if ERRORS:
        print(f'\n❌ ERROR {len(ERRORS)}（其中含历史欠债；用 --save/--compare 区分新旧）:')
        for m in ERRORS[:60]: print('  ', m)
        if len(ERRORS) > 60: print(f'   …还有 {len(ERRORS)-60} 条')
    if WARNS:
        print(f'\n⚠️  WARN {len(WARNS)}:')
        for m in WARNS[:40]: print('  ', m)
        if len(WARNS) > 40: print(f'   …还有 {len(WARNS)-40} 条')
    if not ERRORS and not WARNS:
        print('\n✅ 全部通过。')
    sys.exit(0)

if __name__ == '__main__':
    main()
