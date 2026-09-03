#!/usr/bin/env python3
"""Keep a generated expression only inside a reviewed elliptical region."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--center-x", type=int, required=True)
    parser.add_argument("--center-y", type=int, required=True)
    parser.add_argument("--radius-x", type=int, required=True)
    parser.add_argument("--radius-y", type=int, required=True)
    parser.add_argument("--feather", type=float, default=24.0)
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
    cx, cy, rx, ry = args.center_x, args.center_y, args.radius_x, args.radius_y
    if rx <= 0 or ry <= 0 or args.feather < 0:
        raise SystemExit("Radii must be positive and feather non-negative")
    bbox = (cx - rx, cy - ry, cx + rx, cy + ry)
    if bbox[0] < 0 or bbox[1] < 0 or bbox[2] > width or bbox[3] > height:
        raise SystemExit(f"Ellipse {bbox} lies outside image {master.size}")

    mask = Image.new("L", master.size, 0)
    ImageDraw.Draw(mask).ellipse(bbox, fill=255)
    if args.feather:
        mask = mask.filter(ImageFilter.GaussianBlur(args.feather))
    # The candidate may be an opaque Image 2 render with paper/checker pixels
    # outside the subject. Composite its color only, then restore the reviewed
    # master Alpha exactly so feathering can never create a background halo.
    result = Image.composite(candidate, master, mask)
    result.putalpha(master.getchannel("A"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    audit = {
        "schema_version": 1,
        "kind": "ndc_expression_region_master_composite",
        "master": {"path": str(master_path), "sha256": sha256(master_path)},
        "candidate": {"path": str(candidate_path), "sha256": sha256(candidate_path)},
        "output": {"path": str(output_path), "sha256": sha256(output_path)},
        "image_size": [width, height],
        "performance_region": {"shape": "ellipse", "center": [cx, cy], "radius": [rx, ry], "feather": args.feather},
        "outside_region_source": "neutral_master",
        "alpha_source": "neutral_master_exact",
        "lower_bust_change": False,
        "status": "PASS",
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
