"""One-off fix: the 6 nodes replaced earlier ended up at wrong absolute coords
because GET returns relative-to-parent positions but POST treats {x,y} as absolute.

For each broken new_id:
  1. Walk up parent chain from new node's parent → compute parent's TRUE absolute position
  2. target_abs = parent_abs + original_relative_offset (from old node)
  3. DELETE broken new node
  4. CREATE replacement at target_abs with same parent_id and content
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import api, MINDMAP_BASE, fetch_all_mindmap_nodes, node_content

# (broken_new_id, original_relative_offset_x, original_relative_offset_y, new_content)
BROKEN = [
    ("3458764671274304326", 374, -31, "击破：🟢2101 尸体手指照片(无戒指无佩戴痕迹) + 🟢2102 Margaret 相册(30 年始终佩戴婚戒) + 🟢2103 空的首饰盒(戒指凹槽空置)"),
    ("3458764671274304478", 292, -24, "击破：🟢2104 现场地面照片(无任何金属残留)"),
    ("3458764671274304670", 372, -27, "击破：⚪2021001 Emma 转 Foster 初步分析(尸检最快明天，连性别都未定)"),
    ("3458764671274304774", 280, -60, "击破：⚪Vinnie证言 + 🟢217 Leonard 改名档案(原名 Russo→Ross)"),
    ("3458764671274389987", 384, -25, "击破：🟢207 O'Hara 的贷款钞票(连号缺 905-908B) + 🟢208 Vinnie 的钞票(恰好填补缺号) + ⚪209 Vinnie 用崭新钞票消费说\"今天又赚了一笔\""),
    ("3458764671274390114", 350, -25, "击破：⚪210 Vinnie 从不说\"还债\"只说\"赚钱\"\"收钱\" + 🟢213 Vinnie 催债小本子(L.R.给的地址) + 🟢207 O'Hara 钞票(回顾)"),
]

def main():
    print("Fetching board state...")
    nodes = fetch_all_mindmap_nodes()
    by_id = {n["id"]: n for n in nodes}

    def parent_abs(start_id):
        """Walk from start_id up to root, summing positions."""
        x = y = 0.0
        cur = start_id
        depth = 0
        while cur and depth < 100:
            n = by_id.get(cur)
            if not n: break
            pos = n.get("position", {})
            x += pos.get("x", 0)
            y += pos.get("y", 0)
            cur = n.get("parent", {}).get("id")
            depth += 1
        return x, y

    ok = fail = 0
    for new_id, rel_x, rel_y, content in BROKEN:
        n = by_id.get(new_id)
        if not n:
            print(f"! {new_id} not on board, skipping")
            fail += 1
            continue
        parent_id = n.get("parent", {}).get("id")
        if not parent_id:
            print(f"! {new_id} has no parent, aborting")
            fail += 1
            continue

        p_abs_x, p_abs_y = parent_abs(parent_id)
        target_x = p_abs_x + rel_x
        target_y = p_abs_y + rel_y

        print(f"\n{new_id}")
        print(f"  parent_abs = ({p_abs_x:.0f}, {p_abs_y:.0f})")
        print(f"  target_abs = ({target_x:.0f}, {target_y:.0f}) [parent + rel ({rel_x}, {rel_y})]")
        print(f"  content    = {content[:60]}...")

        # 1. Create replacement at correct absolute position
        body = {
            "data": {"nodeView": {"data": {"content": content}}},
            "position": {"x": target_x, "y": target_y},
            "parent": {"id": parent_id},
        }
        status, data = api("POST", MINDMAP_BASE, json_body=body)
        if status not in (200, 201):
            print(f"  ! CREATE FAIL: {status} {str(data)[:200]}")
            fail += 1
            continue
        replacement_id = data.get("id")
        time.sleep(0.2)

        # 2. Delete broken new node
        status, resp = api("DELETE", f"{MINDMAP_BASE}/{new_id}")
        if status not in (200, 204, 404):
            print(f"  ! DELETE FAIL: {status} {str(resp)[:200]}")
            fail += 1
            continue

        print(f"  ✓ replacement_id={replacement_id}, broken {new_id} deleted")
        ok += 1
        time.sleep(0.2)

    print(f"\nDone: ok={ok} fail={fail}")

if __name__ == "__main__":
    main()
