#!/usr/bin/env python3
"""Extract a conservative soft alpha from a saturated green-screen character render."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--preview-prefix", required=True, type=Path)
    parser.add_argument("--transparent-green-excess", type=float, default=38.0)
    parser.add_argument("--opaque-green-excess", type=float, default=2.0)
    parser.add_argument("--minimum-green", type=float, default=15.0)
    return parser.parse_args()


def composite_preview(rgba: Image.Image, color: tuple[int, int, int], path: Path) -> None:
    background = Image.new("RGBA", rgba.size, (*color, 255))
    background.alpha_composite(rgba)
    background.convert("RGB").save(path)


def main() -> int:
    args = parse_args()
    source = Image.open(args.input).convert("RGB")
    rgb = np.asarray(source).astype(np.float32)
    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green_excess = green - np.maximum(red, blue)

    denominator = args.transparent_green_excess - args.opaque_green_excess
    if denominator <= 0:
        raise ValueError("transparent-green-excess must exceed opaque-green-excess")
    alpha = (args.transparent_green_excess - green_excess) / denominator
    alpha = np.clip(alpha, 0.0, 1.0)
    alpha = np.where(green < args.minimum_green, 1.0, alpha)

    # Despill every green-key-affected pixel, including the almost-opaque rim.
    # Limiting despill to transitional alpha leaves a bright green contour on
    # dark hair and clothes when the source antialiasing is nearly opaque.
    foreground_rgb = rgb.copy()
    keyed = (green >= args.minimum_green) & (green_excess > 0.0)
    neutral_cap = np.maximum(red, blue)
    foreground_rgb[..., 1] = np.where(keyed, np.minimum(green, neutral_cap), green)

    rgba_array = np.dstack(
        [np.clip(foreground_rgb, 0, 255).astype(np.uint8), np.round(alpha * 255).astype(np.uint8)]
    )
    rgba = Image.fromarray(rgba_array, "RGBA")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.preview_prefix.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(args.output)

    composite_preview(rgba, (0, 0, 0), args.preview_prefix.with_name(args.preview_prefix.name + "-black.png"))
    composite_preview(rgba, (255, 255, 255), args.preview_prefix.with_name(args.preview_prefix.name + "-white.png"))
    composite_preview(rgba, (24, 34, 32), args.preview_prefix.with_name(args.preview_prefix.name + "-scene-tone.png"))

    visible = np.argwhere(alpha >= 0.5)
    if visible.size:
        yy1, xx1 = visible.min(axis=0)
        yy2, xx2 = visible.max(axis=0) + 1
        bbox = [int(xx1), int(yy1), int(xx2), int(yy2)]
    else:
        bbox = None
    report = {
        "schema": "ndc-chroma-green-matte/v1",
        "input": str(args.input),
        "output": str(args.output),
        "canvas": list(source.size),
        "bboxAtAlpha50": bbox,
        "opaqueCoverage": float(np.mean(alpha >= 0.995)),
        "transitionCoverage": float(np.mean((alpha > 0.0) & (alpha < 0.995))),
        "parameters": {
            "transparentGreenExcess": args.transparent_green_excess,
            "opaqueGreenExcess": args.opaque_green_excess,
            "minimumGreen": args.minimum_green,
        },
        "previewSourceMatchesRGBA": True,
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
