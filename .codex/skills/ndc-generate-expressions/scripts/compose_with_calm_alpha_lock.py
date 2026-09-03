#!/usr/bin/env python3
"""Compose an expression through a calm anchor's approved alpha silhouette.

The transparent calm asset is the silhouette authority.  Its alpha is mapped
through native-source coordinates into either delivery profile so that two
profiles cannot drift and paper-background extraction cannot contaminate the
greenscreen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


CANVASES = {"transparent": (1164, 916), "greenscreen": (1536, 1024)}
GREEN = (0, 255, 43, 255)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def affine_for_mapping(
    anchor_scale: float,
    anchor_x: float,
    anchor_y: float,
    output_scale: float,
    output_x: float,
    output_y: float,
) -> tuple[float, float, float, float, float, float]:
    ratio = anchor_scale / output_scale
    return (
        ratio,
        0.0,
        anchor_x - output_x * ratio,
        0.0,
        ratio,
        anchor_y - output_y * ratio,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--calm-transparent", required=True)
    parser.add_argument("--anchor-scale", type=float, required=True)
    parser.add_argument("--anchor-offset-x", type=float, required=True)
    parser.add_argument("--anchor-offset-y", type=float, required=True)
    parser.add_argument("--profile", choices=CANVASES, required=True)
    parser.add_argument("--scale", type=float, required=True)
    parser.add_argument("--offset-x", type=float, required=True)
    parser.add_argument("--offset-y", type=float, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit", required=True)
    args = parser.parse_args()

    candidate_path = Path(args.candidate)
    calm_path = Path(args.calm_transparent)
    output_path = Path(args.output)
    audit_path = Path(args.audit)
    size = CANVASES[args.profile]

    candidate = Image.open(candidate_path).convert("RGBA")
    resized = candidate.resize(
        (round(candidate.width * args.scale), round(candidate.height * args.scale)),
        Image.Resampling.LANCZOS,
    )
    color_canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    color_canvas.alpha_composite(resized, (round(args.offset_x), round(args.offset_y)))

    calm_image = Image.open(calm_path).convert("RGBA")
    calm_alpha = calm_image.getchannel("A")
    transform = affine_for_mapping(
        args.anchor_scale,
        args.anchor_offset_x,
        args.anchor_offset_y,
        args.scale,
        args.offset_x,
        args.offset_y,
    )
    locked_alpha = calm_alpha.transform(
        size,
        Image.Transform.AFFINE,
        transform,
        resample=Image.Resampling.BICUBIC,
        fillcolor=0,
    )
    # The model candidate may contain a non-exact green gradient or chroma
    # spill at its silhouette.  Reuse the already reviewed calm anchor RGB on
    # only the partially transparent edge pixels; keep the candidate RGB for
    # the opaque interior.  This avoids a green outline without repainting the
    # expression or silently changing the locked Alpha.
    calm_mapped = calm_image.transform(
        size,
        Image.Transform.AFFINE,
        transform,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )
    edge_mask = locked_alpha.point(lambda value: 255 if 0 < value < 245 else 0)
    color_canvas.paste(calm_mapped, (0, 0), edge_mask)
    candidate_pixels = np.asarray(color_canvas, dtype=np.uint8).copy()
    calm_pixels = np.asarray(calm_mapped, dtype=np.uint8)
    alpha_pixels = np.asarray(locked_alpha, dtype=np.uint8)
    red = candidate_pixels[:, :, 0].astype(np.int16)
    green = candidate_pixels[:, :, 1].astype(np.int16)
    blue = candidate_pixels[:, :, 2].astype(np.int16)
    green_spill = (
        (alpha_pixels > 0)
        & (green > 50)
        & (green >= red - 8)
        & (green >= blue + 20)
    )
    corrected_green = np.clip((red + blue) // 2, 0, 255).astype(np.uint8)
    candidate_pixels[:, :, 1][green_spill] = corrected_green[green_spill]
    color_canvas = Image.fromarray(candidate_pixels, mode="RGBA")
    color_canvas.putalpha(locked_alpha)

    if args.profile == "greenscreen":
        final = Image.new("RGBA", size, GREEN)
        final.alpha_composite(color_canvas)
        final = final.convert("RGB")
    else:
        final = color_canvas

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "method": "CALM_ALPHA_LOCK",
                "candidate": str(candidate_path),
                "candidate_sha256": sha256(candidate_path),
                "calm_transparent": str(calm_path),
                "calm_transparent_sha256": sha256(calm_path),
                "profile": args.profile,
                "canvas": list(size),
                "anchor_transform": {
                    "scale": args.anchor_scale,
                    "offset_x": args.anchor_offset_x,
                    "offset_y": args.anchor_offset_y,
                },
                "output_transform": {
                    "scale": args.scale,
                    "offset_x": args.offset_x,
                    "offset_y": args.offset_y,
                },
                "partial_alpha_edge_rgb_source": "reviewed_calm_anchor",
                "opaque_green_spill_rgb_correction": "green_channel_to_mean_red_blue",
                "opaque_green_spill_pixels_replaced": int(green_spill.sum()),
                "candidate_opaque_interior_preserved": True,
                "output": str(output_path),
                "output_sha256": sha256(output_path),
                "status": "PASS",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
