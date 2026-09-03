#!/usr/bin/env python3
"""Deterministically remove a border-connected light background.

This tool is deliberately non-generative. It protects enclosed light costume
regions by changing only light-neutral pixels connected to the canvas border,
builds a soft Alpha band, and decontaminates partially transparent RGB against
the measured border matte. Its output is a candidate until Codex reviews the
standard multi-background previews.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def border_seed_points(width: int, height: int) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    for x in range(width):
        points.append((x, 0))
        if height > 1:
            points.append((x, height - 1))
    for y in range(1, max(1, height - 1)):
        points.append((0, y))
        if width > 1:
            points.append((width - 1, y))
    return points


def connected_mask(mask: np.ndarray) -> np.ndarray:
    candidate = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), "L").copy()
    width, height = candidate.size
    fill_value = 128
    for seed in border_seed_points(width, height):
        if candidate.getpixel(seed) == 255:
            ImageDraw.floodfill(candidate, seed, fill_value, thresh=0)
    return np.asarray(candidate) == fill_value


def decontaminate(rgb: np.ndarray, alpha: np.ndarray, matte: np.ndarray) -> np.ndarray:
    result = rgb.astype(np.float32)
    a = alpha.astype(np.float32) / 255.0
    partial = (a > 0.0) & (a < 1.0)
    safe_a = np.maximum(a[..., None], 1.0 / 255.0)
    foreground = (result - (1.0 - a[..., None]) * matte[None, None, :]) / safe_a
    foreground = np.clip(foreground, 0.0, 255.0)
    result[partial] = foreground[partial]
    result[a == 0.0] = 0.0
    return np.rint(result).astype(np.uint8)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove a border-connected light-neutral background without an image model."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--background-minimum", type=int, default=230)
    parser.add_argument("--soft-band-minimum", type=int, default=180)
    parser.add_argument("--maximum-chroma", type=int, default=24)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 0 <= args.soft_band_minimum < args.background_minimum <= 255:
        raise SystemExit("Thresholds must satisfy 0 <= soft-band-minimum < background-minimum <= 255")
    if not 0 <= args.maximum_chroma <= 255:
        raise SystemExit("maximum-chroma must be between 0 and 255")

    source = args.input.resolve()
    output = args.output.resolve()
    audit = args.audit.resolve()
    if not source.is_file():
        raise SystemExit(f"Missing input: {source}")

    image = Image.open(source).convert("RGBA")
    array = np.asarray(image, dtype=np.uint8)
    rgb = array[..., :3]
    source_alpha = array[..., 3]
    minimum = np.min(rgb, axis=2)
    chroma = np.max(rgb, axis=2) - minimum
    neutral_limit = args.maximum_chroma
    relaxed_limit = min(255, args.maximum_chroma + 16)

    core_candidates = (minimum >= args.background_minimum) & (chroma <= neutral_limit)
    relaxed_candidates = (minimum >= args.soft_band_minimum) & (chroma <= relaxed_limit)
    connected_core = connected_mask(core_candidates)
    connected_relaxed = connected_mask(relaxed_candidates)

    if not np.any(connected_core):
        raise SystemExit("NO_BORDER_CONNECTED_LIGHT_BACKGROUND: use a reviewed manual mask; do not use an image model")

    matte_samples = rgb[connected_core]
    matte = np.median(matte_samples, axis=0).astype(np.float32)

    alpha = np.full(minimum.shape, 255, dtype=np.uint8)
    alpha[connected_core] = 0
    soft = connected_relaxed & ~connected_core
    numerator = args.background_minimum - minimum.astype(np.float32)
    denominator = float(args.background_minimum - args.soft_band_minimum)
    soft_alpha = np.clip(numerator / denominator, 0.0, 1.0) * 255.0
    alpha[soft] = np.rint(soft_alpha[soft]).astype(np.uint8)
    alpha = np.minimum(alpha, source_alpha)

    output_array = array.copy()
    output_array[..., :3] = decontaminate(rgb, alpha, matte)
    output_array[..., 3] = alpha

    if int(np.count_nonzero(alpha)) == 0:
        raise SystemExit("EMPTY_FOREGROUND: extraction removed every visible pixel")

    output.parent.mkdir(parents=True, exist_ok=True)
    audit.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output_array, "RGBA").save(output)

    record = {
        "schema_version": 2,
        "kind": "ndc_deterministic_expression_background_removal",
        "method": "BORDER_CONNECTED_LIGHT_MATTE_WITH_RGB_DECONTAMINATION",
        "image_model_used": False,
        "source": {
            "path": str(source),
            "sha256": sha256(source),
            "size": list(image.size),
            "mode": "RGBA",
        },
        "output": {
            "path": str(output),
            "sha256": sha256(output),
            "size": list(image.size),
            "mode": "RGBA",
        },
        "thresholds": {
            "background_minimum": args.background_minimum,
            "soft_band_minimum": args.soft_band_minimum,
            "maximum_chroma": args.maximum_chroma,
        },
        "measured_matte_rgb": [int(round(value)) for value in matte],
        "removed_pixels": int(np.count_nonzero(alpha == 0)),
        "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
        "protected_white_review": "NOT_CHECKED",
        "white_fringe_review": "NOT_CHECKED",
        "formal_status": "NOT_CHECKED",
        "required_next_action": (
            "Run prepare_alpha_edge_review.py, inspect white/mid-gray/dark-gray/black/exact-green "
            "previews at 100% and 200%, and record Codex PASS before profile composition."
        ),
    }
    audit.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"BACKGROUND_REMOVAL_CANDIDATE: {output}")
    print("FORMAL_STATUS: NOT_CHECKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
