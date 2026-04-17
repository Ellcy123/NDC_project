"""Convert Markdown outline to tab-indented text for mindmap_import.

Handles:
- # / ## / ### ... headings (each # is a depth level)
- - / * / + bullet lists (nesting via 2-space indent)
- | tables (header row → parent, each data row → sibling, each cell → child labeled as "<header>·<value>")
- > blockquotes (treated as a child paragraph)
- Strips **bold**, *italic*, `code`, [text](link), leading emoji like ✅❌⚠️
- Drops horizontal rules (---)

Usage: python md_to_indent.py <input.md> [-o output.txt]
"""
import sys, os, re, argparse
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

def clean(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    t = re.sub(r'`(.+?)`', r'\1', t)
    t = re.sub(r'\[(.+?)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'^[✅⚠️❌🎮📌📝⭐🔒⏸️⚡🎭]+\s*', '', t)
    return t.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', help='Input Markdown file')
    ap.add_argument('-o', '--output', default=None, help='Output .txt (default: <input>.indent.txt)')
    args = ap.parse_args()
    if not args.output:
        args.output = args.input.rsplit('.', 1)[0] + '.indent.txt'

    with open(args.input, encoding='utf-8') as f:
        lines = f.read().split('\n')

    out = []  # (depth, text)
    header_depth = 0
    table_mode = False
    table_headers = []
    # "段落标签" 支持：形如 **xxx**： 或 xxx：（结尾冒号）的段落，
    # 作为 parent 把后续 bullets 挂在其下
    label_depth = None  # 当前活跃的段落标签深度；None 表示未启用

    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if not s:
            table_mode = False
            continue
        if s.startswith('---'):
            table_mode = False
            label_depth = None
            continue
        m = re.match(r'^(#{1,6})\s+(.+)$', s)
        if m:
            lvl = len(m.group(1))
            out.append((lvl - 1, clean(m.group(2))))
            header_depth = lvl - 1
            table_mode = False
            label_depth = None  # 新 heading 重置标签
            continue
        if s.startswith('|') and not table_mode:
            cells = [c.strip() for c in s.strip('|').split('|')]
            table_headers = cells
            table_mode = True
            continue
        if table_mode and re.match(r'^\|[\s\-\|:]+\|$', s):
            continue  # separator
        if table_mode and s.startswith('|'):
            cells = [clean(c.strip()) for c in s.strip('|').split('|')]
            out.append((header_depth + 1, cells[0] if cells else '·'))
            for i, c in enumerate(cells[1:], 1):
                if c and i < len(table_headers):
                    label = f'{table_headers[i]}·{c}' if table_headers[i] else c
                    out.append((header_depth + 2, label))
            continue
        table_mode = False
        if s.startswith('>'):
            q = s.lstrip('>').strip()
            if q: out.append((header_depth + 1, clean(q)))
            continue
        m = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
        if m:
            indent_str = m.group(1)
            bullet_level = len(indent_str) // 2
            base = label_depth if label_depth is not None else header_depth
            depth = base + 1 + bullet_level
            t = clean(m.group(2))
            if t: out.append((depth, t))
            continue
        # 段落：检测是否是"段落标签"（以：或:结尾、非 bullet、非 heading）
        # 形如 **开场情境**： / 谎言层级： / 实际发展：
        t = clean(s)
        if not t: continue
        if re.match(r'^[^：:]{1,30}[：:]$', t):
            # 段落标签：挂在当前 header 或外层标签下
            base = label_depth if label_depth is not None else header_depth
            new_depth = base + 1
            out.append((new_depth, t.rstrip('：:').strip()))
            label_depth = new_depth  # 后续 bullet 以此为父
        else:
            # 普通段落：作为当前 parent 的 child，但不改变 label_depth
            base = label_depth if label_depth is not None else header_depth
            out.append((base + 1, t))

    with open(args.output, 'w', encoding='utf-8') as f:
        for depth, text in out:
            f.write('\t' * depth + text + '\n')
    print(f'wrote {len(out)} lines → {args.output}')

if __name__ == '__main__':
    main()
