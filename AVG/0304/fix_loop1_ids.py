#!/usr/bin/env python3
"""
Loop1 ID 前缀修正: 1xx → 2xx
将 Loop1 MD 文件中所有 9 位对话 ID 的首位从 1 改为 2（EPI02 规范）。
不影响证据/证词 ID（4-7 位）。
"""

import re
from pathlib import Path

LOOP1_DIR = Path(__file__).parent / "对话草稿" / "Loop1"

def fix_ids(text):
    """Replace first digit of 9-digit dialogue IDs from 1 to 2.

    Matches: 101001001, 110001038a, 104002003 etc.
    Does NOT match: 2021001 (7-digit), 2111 (4-digit)
    """
    # Match 9-digit numbers starting with 1, optionally followed by a letter suffix
    # \b ensures word boundary so we don't match partial numbers
    return re.sub(r'\b1((?:0[0-9]|1[0-9])\d{6}[a-z]?)\b', r'2\1', text)


def process_file(filepath):
    """Process a single MD file, return (old_text, new_text)."""
    old_text = filepath.read_text(encoding='utf-8')
    new_text = fix_ids(old_text)
    return old_text, new_text


def main():
    md_files = sorted(LOOP1_DIR.glob("*.md"))

    for f in md_files:
        old, new = process_file(f)
        if old == new:
            print(f"  [SKIP] {f.name} — no changes")
            continue

        # Count changes
        old_ids = re.findall(r'\b1(?:0[0-9]|1[0-9])\d{6}[a-z]?\b', old)
        new_ids = re.findall(r'\b2(?:0[0-9]|1[0-9])\d{6}[a-z]?\b', new)

        print(f"  [FIX]  {f.name} — {len(old_ids)} IDs changed")

        # Show a few examples
        samples = list(zip(old_ids[:3], new_ids[:3]))
        for o, n in samples:
            print(f"         {o} → {n}")
        if len(old_ids) > 3:
            print(f"         ... and {len(old_ids) - 3} more")

        f.write_text(new, encoding='utf-8')

    print("\nDone!")


if __name__ == "__main__":
    main()
