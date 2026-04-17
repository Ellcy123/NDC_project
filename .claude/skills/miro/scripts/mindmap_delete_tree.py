"""Delete a single mindmap tree by root ID.

Usage: python mindmap_delete_tree.py <root_id>
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import api, MINDMAP_BASE, fetch_all_mindmap_nodes, build_children_map, collect_subtree_ids

def main():
    if len(sys.argv) < 2:
        print('Usage: python mindmap_delete_tree.py <root_id>')
        sys.exit(1)
    root_id = sys.argv[1]

    print(f'Fetching nodes to resolve subtree of {root_id}...')
    nodes = fetch_all_mindmap_nodes()
    children_of = build_children_map(nodes)
    ids = collect_subtree_ids(root_id, children_of)
    if len(ids) == 1 and not any(n['id'] == root_id for n in nodes):
        print(f'Node {root_id} not found on board')
        sys.exit(1)
    print(f'Tree has {len(ids)} nodes')

    ids.sort(reverse=True)
    ok = fail = 0
    for i, nid in enumerate(ids):
        status, _ = api('DELETE', f'{MINDMAP_BASE}/{nid}')
        if status in (200, 204, 404): ok += 1
        else: fail += 1
        if (i+1) % 50 == 0:
            print(f'[{i+1}/{len(ids)}] deleted', flush=True)
        time.sleep(0.15)
    print(f'\nDone: ok={ok} fail={fail}')

if __name__ == '__main__':
    main()
