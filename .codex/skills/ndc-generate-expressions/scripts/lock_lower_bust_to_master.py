#!/usr/bin/env python3
"""Restore the stable lower-bust region from a neutral master.

The candidate is retained above ``lock_start_y``.  A vertical feather blends
candidate into the master; every pixel at and below the end of that feather is
copied exactly from the neutral master.  This makes costume/jewelry structure a
deterministic post-generation invariant rather than a prompt-only request.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--lock-start-y", type=int, required=True)
    parser.add_argument("--feather", type=int, default=64)
    args = parser.parse_args()

    master_path = Path(args.master).resolve()
    candidate_path = Path(args.candidate).resolve()
    output_path = Path(args.output).resolve()
    audit_path = Path(args.audit).resolve()

    master = Image.open(master_path).convert("RGBA")
    candidate = Image.open(candidate_path).convert("RGBA")
    if master.size != candidate.size:
        raise SystemExit(f"Size mismatch: master={master.size}, candidate={candidate.size}")
    width, height = master.size
    start = args.lock_start_y
    feather = args.feather
    if not 0 <= start < height:
        raise SystemExit(f"lock-start-y must be within 0..{height - 1}")
    if feather < 0 or start + feather > height:
        raise SystemExit("feather must be non-negative and end inside the image")

    mask = Image.new("L", (width, height), 255)
    pixels = mask.load()
    end = start + feather
    for y in range(start, height):
        if feather == 0 or y >= end:
            value = 0
        else:
            value = round(255 * (end - y) / feather)
        for x in range(width):
            pixels[x, y] = value

    result = Image.composite(candidate, master, mask)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)

    audit = {
        "schema_version": 1,
        "kind": "ndc_lower_bust_master_lock",
        "master": {"path": str(master_path), "sha256": sha256(master_path)},
        "candidate": {"path": str(candidate_path), "sha256": sha256(candidate_path)},
        "output": {"path": str(output_path), "sha256": sha256(output_path)},
        "image_size": [width, height],
        "lock_start_y": start,
        "feather": feather,
        "exact_master_region_y": end,
        "lower_bust_change": False,
        "status": "PASS",
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
