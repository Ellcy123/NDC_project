#!/usr/bin/env python3
"""Write the minimal XYposition.txt used by fixed NDC character-scene layers."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


XY_SUFFIX = re.compile(r"__XY_x(-?[0-9]+)_y(-?[0-9]+)$", re.IGNORECASE)


def render(entries: list[tuple[str, int, int]]) -> str:
    if not entries:
        raise ValueError("at least one --entry is required")
    seen: set[str] = set()
    lines: list[str] = []
    for raw_name, x, y in entries:
        name = Path(raw_name).stem
        if Path(raw_name).name != raw_name or not name:
            raise ValueError(f"entry name must be one filename: {raw_name}")
        match = XY_SUFFIX.search(name)
        if match is None:
            raise ValueError(f"entry name must end with __XY_x<int>_y<int>: {raw_name}")
        if (int(match.group(1)), int(match.group(2))) != (x, y):
            raise ValueError(f"filename XY does not match supplied coordinates: {raw_name}")
        key = name.casefold()
        if key in seen:
            raise ValueError(f"duplicate entry: {raw_name}")
        seen.add(key)
        lines.append(f"{name}\t{x},{y}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--entry", action="append", nargs=3, metavar=("FILE", "X", "Y"), required=True)
    args = parser.parse_args()
    if args.output.name != "XYposition.txt":
        raise ValueError("--output filename must be XYposition.txt")
    parsed = [(name, int(x), int(y)) for name, x, y in args.entry]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(parsed), encoding="utf-8")


if __name__ == "__main__":
    main()
