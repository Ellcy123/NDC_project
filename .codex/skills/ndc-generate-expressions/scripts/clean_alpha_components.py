#!/usr/bin/env python3
"""Remove disconnected background debris from an RGBA foreground extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from PIL import Image


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--alpha-threshold", type=int, default=8)
    args = parser.parse_args()
    source_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    audit_path = Path(args.audit).resolve()
    image = Image.open(source_path).convert("RGBA")
    width, height = image.size
    src = image.getchannel("A").load()
    seen = bytearray(width * height)
    largest: list[int] = []
    component_count = 0
    for y in range(height):
        row = y * width
        for x in range(width):
            index = row + x
            if seen[index] or src[x, y] <= args.alpha_threshold:
                seen[index] = 1
                continue
            component_count += 1
            queue = deque([(x, y)])
            seen[index] = 1
            component: list[int] = []
            while queue:
                px, py = queue.popleft()
                component.append(py * width + px)
                for nx, ny in ((px-1,py-1),(px,py-1),(px+1,py-1),(px-1,py),(px+1,py),(px-1,py+1),(px,py+1),(px+1,py+1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        ni = ny * width + nx
                        if not seen[ni]:
                            seen[ni] = 1
                            if src[nx, ny] > args.alpha_threshold:
                                queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    keep = bytearray(width * height)
    for index in largest:
        keep[index] = 1
    new_alpha = Image.new("L", image.size, 0)
    dst = new_alpha.load()
    removed = 0
    for y in range(height):
        row = y * width
        for x in range(width):
            if keep[row + x]:
                dst[x, y] = src[x, y]
            elif src[x, y]:
                removed += 1
    image.putalpha(new_alpha)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    audit = {"schema_version": 1, "kind": "ndc_alpha_component_cleanup", "source": {"path": str(source_path), "sha256": sha256(source_path)}, "output": {"path": str(output_path), "sha256": sha256(output_path)}, "image_size": [width, height], "alpha_threshold": args.alpha_threshold, "component_count": component_count, "largest_component_pixels": len(largest), "removed_nonzero_alpha_pixels": removed, "status": "PASS" if largest else "FAIL_NO_FOREGROUND"}
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    if not largest:
        raise SystemExit("No foreground component found")
    print(output_path)


if __name__ == "__main__":
    main()
