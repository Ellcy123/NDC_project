#!/usr/bin/env python3
"""Derive a reviewed RGBA silhouette authority from an exact NDC greenscreen calm.

This is a deterministic recovery path for a transparent calm whose alpha was
contaminated by hidden opaque paper/halo pixels. The resulting file is review
evidence, not an automatic edge PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


GREEN = (0, 255, 43)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--inner-distance", type=float, default=30.0)
    parser.add_argument("--outer-distance", type=float, default=160.0)
    args = parser.parse_args()

    if not 0 <= args.inner_distance < args.outer_distance:
        parser.error("require 0 <= inner-distance < outer-distance")

    source_path = Path(args.input)
    output_path = Path(args.output)
    audit_path = Path(args.audit)
    source = Image.open(source_path).convert("RGB")
    out = Image.new("RGBA", source.size)
    source_pixels = source.load()
    out_pixels = out.load()
    alpha_zero = alpha_partial = alpha_full = 0

    span = args.outer_distance - args.inner_distance
    for y in range(source.height):
        for x in range(source.width):
            r, g, b = source_pixels[x, y]
            distance = ((r - GREEN[0]) ** 2 + (g - GREEN[1]) ** 2 + (b - GREEN[2]) ** 2) ** 0.5
            if distance <= args.inner_distance:
                alpha = 0
                alpha_zero += 1
            elif distance >= args.outer_distance:
                alpha = 255
                alpha_full += 1
            else:
                alpha = round(255 * (distance - args.inner_distance) / span)
                alpha_partial += 1
            # Decontaminate partially keyed pixels.  The source edge is a
            # straight RGB mixture of foreground and the known chroma green:
            #   observed = a * foreground + (1-a) * GREEN
            # Solving for foreground prevents the hidden green RGB from
            # reappearing as a fringe after the RGBA asset is downsampled or
            # composited over a dark dialogue background.
            if 0 < alpha < 255:
                a = alpha / 255.0
                foreground = []
                for observed, key in zip((r, g, b), GREEN):
                    value = (observed - (1.0 - a) * key) / a
                    foreground.append(max(0, min(255, round(value))))
                rr, gg, bb = foreground
            else:
                rr, gg, bb = r, g, b
            out_pixels[x, y] = (rr, gg, bb, alpha)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit = {
        "schema": "ndc-greenscreen-alpha-derivation/v1",
        "input": str(source_path),
        "input_sha256": sha256(source_path),
        "output": str(output_path),
        "output_sha256": sha256(output_path),
        "key_color": list(GREEN),
        "inner_distance": args.inner_distance,
        "outer_distance": args.outer_distance,
        "alpha_counts": {"zero": alpha_zero, "partial": alpha_partial, "full": alpha_full},
        "partial_pixel_rgb_decontamination": "inverse_known_key_mix",
        "edge_status": "NOT_CHECKED",
        "formal_status": "NOT_CHECKED",
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
