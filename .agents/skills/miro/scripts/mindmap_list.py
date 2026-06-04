"""List all mindmap roots on the board.

Usage: python mindmap_list.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import fetch_all_mindmap_nodes, node_content, build_children_map, collect_subtree_ids

def main():
    print('Fetching all mindmap nodes...')
    nodes = fetch_all_mindmap_nodes()
    print(f'Total mindmap nodes on board: {len(nodes)}\n')

    children_of = build_children_map(nodes)
    roots = [n for n in nodes if n.get('data', {}).get('isRoot')]
    print(f'{"ID":<22} {"POSITION":<22} {"COUNT":<6} CONTENT')
    print('-' * 100)
    for r in roots:
        subtree = collect_subtree_ids(r['id'], children_of)
        pos = r.get('position', {})
        x, y = pos.get('x', 0), pos.get('y', 0)
        content = node_content(r)[:50]
        print(f'{r["id"]:<22} ({x:>7.0f}, {y:>7.0f})    {len(subtree):<6} {content}')

if __name__ == '__main__':
    main()
