#!/usr/bin/env python3
"""Align a candidate once, composite a reviewed face ellipse, and restore master Alpha."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--candidate-scale", required=True, type=float)
    parser.add_argument("--candidate-offset-x", required=True, type=int)
    parser.add_argument("--candidate-offset-y", required=True, type=int)
    parser.add_argument("--center-x", required=True, type=int)
    parser.add_argument("--center-y", required=True, type=int)
    parser.add_argument("--radius-x", required=True, type=int)
    parser.add_argument("--radius-y", required=True, type=int)
    parser.add_argument("--feather", type=float, default=16.0)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    if not 0 < args.candidate_scale <= 1:
        raise ValueError("candidate-scale must be within (0, 1]; candidate upscaling is forbidden")

    master = Image.open(args.master).convert("RGBA")
    candidate = Image.open(args.candidate).convert("RGBA")
    resized = candidate.resize(
        (round(candidate.width * args.candidate_scale), round(candidate.height * args.candidate_scale)),
        Image.Resampling.LANCZOS,
    )
    aligned = Image.new("RGBA", master.size, (0, 0, 0, 0))
    aligned.alpha_composite(resized, (args.candidate_offset_x, args.candidate_offset_y))

    mask = Image.new("L", master.size, 0)
    draw = ImageDraw.Draw(mask)
    box = (
        args.center_x - args.radius_x,
        args.center_y - args.radius_y,
        args.center_x + args.radius_x,
        args.center_y + args.radius_y,
    )
    draw.ellipse(box, fill=255)
    if args.feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(args.feather))
    result = Image.composite(aligned, master, mask)
    result.putalpha(master.getchannel("A"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    record = {
        "kind": "ndc_transformed_expression_region_composite",
        "master": str(args.master.resolve()),
        "master_sha256": sha256(args.master),
        "candidate": str(args.candidate.resolve()),
        "candidate_sha256": sha256(args.candidate),
        "candidate_transform": {
            "scale": args.candidate_scale,
            "offset_x": args.candidate_offset_x,
            "offset_y": args.candidate_offset_y,
            "resample": "LANCZOS_ONCE",
            "upscale": False,
        },
        "ellipse": {"center": [args.center_x, args.center_y], "radius": [args.radius_x, args.radius_y], "feather": args.feather},
        "alpha_source": "neutral_master_exact",
        "output": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "formal_status": "NOT_CHECKED",
    }
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
