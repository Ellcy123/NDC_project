"""Replace 6 击破 nodes — v3 using empirically-measured parent top-left canvas positions.

Step 1: DELETE 6 misplaced retry nodes
Step 2: CREATE 6 new nodes at exact canvas absolute coords
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import api, MINDMAP_BASE, fetch_all_mindmap_nodes

# Misplaced nodes from retry — DELETE these
TO_DELETE = [
    "3458764671298071434", "3458764671298071454", "3458764671298071465",
    "3458764671298071505", "3458764671298071531", "3458764671298071557",
]

# (parent_id, parent_top_left_canvas_x, parent_top_left_canvas_y, child_offset_x, child_offset_y, content)
REPLACEMENTS = [
    ("3458764671261751704", 2801, 1687, 374, -31, "击破：🟢2101 尸体手指照片(无戒指无佩戴痕迹) + 🟢2102 Margaret 相册(30 年始终佩戴婚戒) + 🟢2103 空的首饰盒(戒指凹槽空置)"),
    ("3458764671261751710", 2808, 1772, 292, -24, "击破：🟢2104 现场地面照片(无任何金属残留)"),
    ("3458764671261751716", 2858, 1868, 372, -27, "击破：⚪2021001 Emma 转 Foster 初步分析(尸检最快明天，连性别都未定)"),
    ("3458764671261751748", 3336, 4195, 280, -60, "击破：⚪Vinnie证言 + 🟢217 Leonard 改名档案(原名 Russo→Ross)"),
    ("3458764671261751754", 3338, 4302, 384, -25, "击破：🟢207 O'Hara 的贷款钞票(连号缺 905-908B) + 🟢208 Vinnie 的钞票(恰好填补缺号) + ⚪209 Vinnie 用崭新钞票消费说\"今天又赚了一笔\""),
    ("3458764671261751760", 3343, 4405, 350, -25, "击破：⚪210 Vinnie 从不说\"还债\"只说\"赚钱\"\"收钱\" + 🟢213 Vinnie 催债小本子(L.R.给的地址) + 🟢207 O'Hara 钞票(回顾)"),
]

def main():
    # Step 1: delete the 6 misplaced retry nodes
    print("Step 1: deleting 6 misplaced retry nodes...")
    for did in TO_DELETE:
        status, resp = api("DELETE", f"{MINDMAP_BASE}/{did}")
        ok = status in (200, 204, 404)
        print(f"  {'OK ' if ok else 'FAIL'} {did}  ({status})")
        time.sleep(0.2)

    # Step 2: create 6 new nodes at correct canvas absolute coords
    print("\nStep 2: creating 6 nodes at empirically-measured positions...")
    ok = fail = 0
    for i, (pid, ptl_x, ptl_y, off_x, off_y, content) in enumerate(REPLACEMENTS, 1):
        target_x = ptl_x + off_x
        target_y = ptl_y + off_y
        body = {
            "data": {"nodeView": {"data": {"content": content}}},
            "position": {"x": target_x, "y": target_y},
            "parent": {"id": pid},
        }
        status, data = api("POST", MINDMAP_BASE, json_body=body)
        if status not in (200, 201):
            print(f"  [{i}/6] FAIL  parent={pid}  {status} {str(data)[:200]}")
            fail += 1
            continue
        new_id = data.get("id")
        pos = data.get("position", {})
        print(f"  [{i}/6] OK  new_id={new_id}  target_abs=({target_x},{target_y})  stored relative=({pos.get('x',0):.0f},{pos.get('y',0):.0f})")
        ok += 1
        time.sleep(0.25)
    print(f"\nDone: ok={ok} fail={fail}")

if __name__ == "__main__":
    main()
