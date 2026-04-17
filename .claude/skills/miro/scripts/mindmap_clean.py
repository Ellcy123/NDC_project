"""Clean mindmap roots and their subtrees.

Usage:
    python mindmap_clean.py                      # list all roots, ask before deleting all
    python mindmap_clean.py --contains "Unit1"   # only roots whose content includes this
    python mindmap_clean.py --yes                # no confirmation
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import (api, MINDMAP_BASE, fetch_all_mindmap_nodes, node_content,
                     build_children_map, collect_subtree_ids)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--contains', default=None, help='Only roots whose content contains this substring')
    ap.add_argument('--yes', action='store_true', help='Skip confirmation')
    args = ap.parse_args()

    print('Fetching all mindmap nodes...')
    nodes = fetch_all_mindmap_nodes()
    children_of = build_children_map(nodes)

    target_roots = [n for n in nodes if n.get('data', {}).get('isRoot')]
    if args.contains:
        target_roots = [r for r in target_roots if args.contains in node_content(r)]

    if not target_roots:
        print('No matching roots found.')
        return

    to_delete = []
    for r in target_roots:
        to_delete.extend(collect_subtree_ids(r['id'], children_of))

    print(f'\nMatching roots: {len(target_roots)}')
    for r in target_roots:
        pos = r.get('position', {})
        c = node_content(r)[:60]
        print(f'  {r["id"]} @ ({pos.get("x",0):.0f}, {pos.get("y",0):.0f}) | {c}')
    print(f'\nTotal nodes to delete (roots + all descendants): {len(to_delete)}')

    if not args.yes:
        yn = input('\nConfirm delete? [y/N]: ').strip().lower()
        if yn != 'y':
            print('Cancelled.')
            return

    # 叶子先删：ID 倒序 ≈ 深度深先
    to_delete.sort(reverse=True)
    print('\nDeleting...')
    ok = fail = 0
    for i, nid in enumerate(to_delete):
        status, _ = api('DELETE', f'{MINDMAP_BASE}/{nid}')
        if status in (200, 204, 404): ok += 1
        else: fail += 1
        if (i+1) % 50 == 0:
            print(f'[{i+1}/{len(to_delete)}] deleted (ok={ok} fail={fail})', flush=True)
        time.sleep(0.15)
    print(f'\nDone: ok={ok} fail={fail}')

if __name__ == '__main__':
    main()
