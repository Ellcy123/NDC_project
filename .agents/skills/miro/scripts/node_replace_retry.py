"""Recreate 6 击破 nodes — Miro auto-layout (no explicit position).

User deleted the previous 6 fixed nodes (they appeared to draw long curves
visually, despite the API showing correct relative positions). This time we
POST with only `parent.id` and `content` — no position — and let Miro
auto-place each child node next to its parent.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import api, MINDMAP_BASE, fetch_all_mindmap_nodes

# (parent_id, content) — parent_id is the 谎言 mindmap_node these击破 nodes should hang under
REPLACEMENTS = [
    ("3458764671261751704", "击破：🟢2101 尸体手指照片(无戒指无佩戴痕迹) + 🟢2102 Margaret 相册(30 年始终佩戴婚戒) + 🟢2103 空的首饰盒(戒指凹槽空置)"),
    ("3458764671261751710", "击破：🟢2104 现场地面照片(无任何金属残留)"),
    ("3458764671261751716", "击破：⚪2021001 Emma 转 Foster 初步分析(尸检最快明天，连性别都未定)"),
    ("3458764671261751748", "击破：⚪Vinnie证言 + 🟢217 Leonard 改名档案(原名 Russo→Ross)"),
    ("3458764671261751754", "击破：🟢207 O'Hara 的贷款钞票(连号缺 905-908B) + 🟢208 Vinnie 的钞票(恰好填补缺号) + ⚪209 Vinnie 用崭新钞票消费说\"今天又赚了一笔\""),
    ("3458764671261751760", "击破：⚪210 Vinnie 从不说\"还债\"只说\"赚钱\"\"收钱\" + 🟢213 Vinnie 催债小本子(L.R.给的地址) + 🟢207 O'Hara 钞票(回顾)"),
]

def main():
    print("Pre-flight: verify parent nodes exist...")
    nodes = fetch_all_mindmap_nodes()
    by_id = {n['id']: n for n in nodes}
    for pid, _ in REPLACEMENTS:
        if pid not in by_id:
            print(f"ERROR: parent {pid} not found")
            sys.exit(1)
    print("All 6 parents OK\n")

    ok = fail = 0
    for i, (pid, content) in enumerate(REPLACEMENTS, 1):
        body = {
            'data': {'nodeView': {'data': {'content': content}}},
            'parent': {'id': pid},
        }
        status, data = api('POST', MINDMAP_BASE, json_body=body)
        if status not in (200, 201):
            print(f"[{i}/6] FAIL  parent={pid}  {status} {str(data)[:200]}")
            fail += 1
            continue
        new_id = data.get('id')
        pos = data.get('position', {})
        print(f"[{i}/6] OK  new_id={new_id}  parent={pid}  pos=({pos.get('x',0):.0f},{pos.get('y',0):.0f}) relativeTo={pos.get('relativeTo')}")
        print(f"      content: {content[:80]}...")
        ok += 1
        time.sleep(0.25)

    print(f"\nDone: ok={ok} fail={fail}")

if __name__ == '__main__':
    main()
