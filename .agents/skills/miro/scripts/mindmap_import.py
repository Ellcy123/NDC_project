"""Import tab-indented outline → native editable Mind Map on Miro.

Usage:
    python mindmap_import.py <tab_indent_txt> [--root-x N] [--root-y N] [--x-step N] [--y-step N]

Layout: horizontal tree, Reingold-Tilford style. Children distributed vertically
by leaf count of their subtrees (so no overlap).

Key API notes:
- position is ABSOLUTE board coords (not relative to parent)
- style.fillColor is rejected (400). Don't send it.
- No PATCH support: to fix anything, delete and recreate.
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import api, MINDMAP_BASE

class Node:
    __slots__ = ('text', 'children', 'leaves', 'abs_x', 'abs_y')
    def __init__(self, text):
        self.text = text
        self.children = []
        self.leaves = 0
        self.abs_x = 0.0
        self.abs_y = 0.0

def parse_tab_indent(path):
    """Parse tab-indented file. Multiple depth-0 lines get demoted to depth-1 under the first."""
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    raw = []
    for line in lines:
        if not line.strip(): continue
        d = 0
        while d < len(line) and line[d] == '\t': d += 1
        t = line[d:].strip()
        if t: raw.append((d, t))
    flat = []
    first = False; sub = False
    for d, t in raw:
        if d == 0:
            if not first: first = True; flat.append((0, t)); sub = False
            else: flat.append((1, t)); sub = True
        else:
            flat.append((d + 1 if sub else d, t))
    return flat

def build_tree(flat):
    stack = []
    root = None
    for d, t in flat:
        n = Node(t)
        while stack and stack[-1][0] >= d: stack.pop()
        if not stack: root = n
        else: stack[-1][1].children.append(n)
        stack.append((d, n))
    return root

def calc_leaves(n):
    if not n.children: n.leaves = 1
    else: n.leaves = sum(calc_leaves(c) for c in n.children)
    return n.leaves

def assign_abs(n, x, y, x_step, y_step):
    n.abs_x = x
    n.abs_y = y
    if not n.children: return
    total = sum(c.leaves for c in n.children)
    cumul = 0
    for c in n.children:
        rel_y = (cumul * y_step + (c.leaves * y_step) / 2) - (total * y_step) / 2
        assign_abs(c, x + x_step, y + rel_y, x_step, y_step)
        cumul += c.leaves

def count(n):
    return 1 + sum(count(c) for c in n.children)

def create_tree(node, parent_id, created_counter, total):
    body = {
        'data': {'nodeView': {'data': {'content': node.text}}},
        'position': {'x': node.abs_x, 'y': node.abs_y}
    }
    if parent_id: body['parent'] = {'id': parent_id}
    status, data = api('POST', MINDMAP_BASE, json_body=body)
    if status not in (200, 201):
        print(f'  FAIL: {status} {str(data)[:150]}', flush=True)
        return None
    created_counter[0] += 1
    c = created_counter[0]
    if c % 25 == 0 or c <= 3:
        print(f'[{c}/{total}] ({node.abs_x:.0f},{node.abs_y:.0f}) {node.text[:40]}', flush=True)
    nid = data['id']
    time.sleep(0.2)
    for child in node.children:
        create_tree(child, nid, created_counter, total)
    return nid

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', help='Tab-indented outline text file')
    ap.add_argument('--root-x', type=float, default=35000)
    ap.add_argument('--root-y', type=float, default=0)
    ap.add_argument('--x-step', type=float, default=350)
    ap.add_argument('--y-step', type=float, default=50)
    args = ap.parse_args()

    flat = parse_tab_indent(args.file)
    if not flat:
        print('ERROR: empty input'); sys.exit(1)
    root = build_tree(flat)
    calc_leaves(root)
    assign_abs(root, args.root_x, args.root_y, args.x_step, args.y_step)
    total = count(root)
    height = root.leaves * args.y_step
    print(f'解析: {total} 节点, {root.leaves} 叶子')
    print(f'布局: X {args.root_x:.0f} ~ {args.root_x + args.x_step * 10:.0f} (每级 {args.x_step})')
    print(f'      Y 总高度 ≈ {height:.0f} (每叶 {args.y_step})')
    print(f'预计时间 ≈ {total * 0.25 / 60:.1f} 分钟\n')

    counter = [0]
    create_tree(root, None, counter, total)
    print(f'\n完成: {counter[0]}/{total}')

if __name__ == '__main__':
    main()
