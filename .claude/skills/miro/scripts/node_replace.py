"""Replace mindmap_node text by delete+recreate (PATCH not supported).

Usage:
    python node_replace.py [--dry-run]

Replacement spec is the REPLACEMENTS list below — edit it before running.
For each (node_id, new_text):
  1. GET old node to read position + parent_id
  2. POST new node with same position/parent and new content
  3. DELETE old node
  4. Print before/after

Leaf nodes only — script aborts if any target has children.
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import api, MINDMAP_BASE, fetch_all_mindmap_nodes, build_children_map, node_content

REPLACEMENTS = [
    ("3458764671261751706", "击破：🟢2101 尸体手指照片(无戒指无佩戴痕迹) + 🟢2102 Margaret 相册(30 年始终佩戴婚戒) + 🟢2103 空的首饰盒(戒指凹槽空置)"),
    ("3458764671261751712", "击破：🟢2104 现场地面照片(无任何金属残留)"),
    ("3458764671261751718", "击破：⚪2021001 Emma 转 Foster 初步分析(尸检最快明天，连性别都未定)"),
    ("3458764671261751750", "击破：⚪Vinnie证言 + 🟢217 Leonard 改名档案(原名 Russo→Ross)"),
    ("3458764671261751756", "击破：🟢207 O'Hara 的贷款钞票(连号缺 905-908B) + 🟢208 Vinnie 的钞票(恰好填补缺号) + ⚪209 Vinnie 用崭新钞票消费说\"今天又赚了一笔\""),
    ("3458764671261751762", "击破：⚪210 Vinnie 从不说\"还债\"只说\"赚钱\"\"收钱\" + 🟢213 Vinnie 催债小本子(L.R.给的地址) + 🟢207 O'Hara 钞票(回顾)"),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='Print what would happen, no API writes')
    args = ap.parse_args()

    print(f'Fetching board state...')
    nodes = fetch_all_mindmap_nodes()
    by_id = {n['id']: n for n in nodes}
    children_of = build_children_map(nodes)

    # Pre-flight: all targets exist + are leaf nodes
    for nid, _ in REPLACEMENTS:
        if nid not in by_id:
            print(f'ERROR: node {nid} not found on board')
            sys.exit(1)
        if children_of.get(nid):
            print(f'ERROR: node {nid} has {len(children_of[nid])} children — aborting (script handles leaves only)')
            sys.exit(1)

    print(f'\n{"DRY RUN — " if args.dry_run else ""}{len(REPLACEMENTS)} replacements:\n')

    ok = fail = 0
    for i, (old_id, new_text) in enumerate(REPLACEMENTS, 1):
        old = by_id[old_id]
        old_text = node_content(old)
        pos = old.get('position', {})
        parent_id = old.get('parent', {}).get('id')

        print(f'[{i}/{len(REPLACEMENTS)}] {old_id} ({pos.get("x",0):.0f},{pos.get("y",0):.0f})')
        print(f'  - OLD: {old_text}')
        print(f'  + NEW: {new_text}')

        if args.dry_run:
            ok += 1
            continue

        # 1. Create new node at same pos with same parent
        body = {
            'data': {'nodeView': {'data': {'content': new_text}}},
            'position': {'x': pos.get('x', 0), 'y': pos.get('y', 0)},
        }
        if parent_id:
            body['parent'] = {'id': parent_id}
        status, data = api('POST', MINDMAP_BASE, json_body=body)
        if status not in (200, 201):
            print(f'  ! CREATE FAIL: {status} {str(data)[:200]}')
            fail += 1
            continue
        new_id = data.get('id')
        time.sleep(0.2)

        # 2. Delete old node
        status, resp = api('DELETE', f'{MINDMAP_BASE}/{old_id}')
        if status not in (200, 204, 404):
            print(f'  ! DELETE FAIL: {status} {str(resp)[:200]} — new node {new_id} stays, old {old_id} not deleted')
            fail += 1
            continue
        print(f'  ✓ new_id={new_id}, old deleted')
        ok += 1
        time.sleep(0.2)

    print(f'\nDone: ok={ok} fail={fail}')

if __name__ == '__main__':
    main()
