"""Dump a mindmap subtree as indented text for inspection.

Usage: python mindmap_dump_tree.py <root_id> [--out file]
"""
import sys, os, argparse, html, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

from _common import fetch_all_mindmap_nodes, build_children_map

TAG_RE = re.compile(r'<[^>]+>')

def clean(text):
    if not text: return ''
    text = html.unescape(text)
    text = TAG_RE.sub('', text)
    return text.strip()

def node_content_raw(n):
    return n.get('data', {}).get('nodeView', {}).get('data', {}).get('content', '')

def sort_children(ids, nodes_by_id):
    def key(nid):
        n = nodes_by_id[nid]
        p = n.get('position', {})
        return (p.get('y', 0), p.get('x', 0))
    return sorted(ids, key=key)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root_id')
    ap.add_argument('--out')
    args = ap.parse_args()

    print('Fetching all mindmap nodes...', file=sys.stderr)
    nodes = fetch_all_mindmap_nodes()
    nodes_by_id = {n['id']: n for n in nodes}
    children_of = build_children_map(nodes)
    if args.root_id not in nodes_by_id:
        print(f'ERROR: root {args.root_id} not found', file=sys.stderr)
        sys.exit(1)

    lines = []
    def dfs(nid, depth):
        n = nodes_by_id[nid]
        text = clean(node_content_raw(n))
        lines.append('  ' * depth + text)
        for cid in sort_children(children_of.get(nid, []), nodes_by_id):
            dfs(cid, depth + 1)

    dfs(args.root_id, 0)

    out = '\n'.join(lines)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(out)
        print(f'Wrote {len(lines)} lines to {args.out}', file=sys.stderr)
    else:
        print(out)

if __name__ == '__main__':
    main()
