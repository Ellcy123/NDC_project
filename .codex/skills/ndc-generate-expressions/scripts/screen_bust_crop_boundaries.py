#!/usr/bin/env python3
"""Screen NDC bust assets for likely source-crop boundaries.

This is deliberately a screening tool. CLEAR does not prove source integrity,
and SUSPICIOUS requires Codex review of the original image and critical-region
crops before a formal decision can be made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


GREEN = np.array([0, 255, 43], dtype=np.int16)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def longest_near_constant(values: list[int], tolerance: int = 1) -> tuple[int, int | None]:
    best_len = 0
    best_value: int | None = None
    run_len = 0
    run_value: int | None = None
    for value in values:
        if value < 0:
            run_len = 0
            run_value = None
        elif run_value is not None and abs(value - run_value) <= tolerance:
            run_len += 1
            run_value = int(round((run_value * (run_len - 1) + value) / run_len))
        else:
            run_len = 1
            run_value = value
        if run_len > best_len:
            best_len = run_len
            best_value = run_value
    return best_len, best_value


def foreground_mask(image: Image.Image, profile: str) -> np.ndarray:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    if profile == "transparent":
        return rgba[..., 3] > 8
    rgb = rgba[..., :3].astype(np.int16)
    return np.max(np.abs(rgb - GREEN), axis=2) > 8


def main() -> int:
    parser = argparse.ArgumentParser(description="Screen a bust asset for likely crop boundaries.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=("transparent", "greenscreen"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.input.resolve()
    output = args.output.resolve()
    if not source.is_file():
        raise SystemExit(f"Missing input: {source}")

    image = Image.open(source)
    mask = foreground_mask(image, args.profile)
    height, width = mask.shape
    ys, xs = np.nonzero(mask)
    if not len(xs):
        raise SystemExit("No foreground detected")

    lower_start = int(round(height * 0.45))
    left_edges: list[int] = []
    right_edges: list[int] = []
    for row in mask[lower_start:]:
        columns = np.flatnonzero(row)
        left_edges.append(int(columns[0]) if len(columns) else -1)
        right_edges.append(int(columns[-1]) if len(columns) else -1)

    left_run, left_x = longest_near_constant(left_edges)
    right_run, right_x = longest_near_constant(right_edges)
    top_span = int(np.count_nonzero(mask[0]))
    bottom_span = int(np.count_nonzero(mask[-1]))
    side_threshold = max(40, int(round(height * 0.04)))
    top_threshold = max(35, int(round(width * 0.03)))

    reasons: list[str] = []
    if left_run >= side_threshold:
        reasons.append(f"long_near_vertical_left_boundary:{left_run}px_at_x={left_x}")
    if right_run >= side_threshold:
        reasons.append(f"long_near_vertical_right_boundary:{right_run}px_at_x={right_x}")
    if top_span >= top_threshold:
        reasons.append(f"foreground_intersects_top_edge:{top_span}px")

    result: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ndc_bust_crop_boundary_screen",
        "asset": {
            "path": str(source),
            "sha256": sha256(source),
            "width": width,
            "height": height,
            "profile": args.profile,
        },
        "metrics": {
            "foreground_bbox_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "lower_region_start_y": lower_start,
            "longest_left_near_vertical_run_px": left_run,
            "left_run_x": left_x,
            "longest_right_near_vertical_run_px": right_run,
            "right_run_x": right_x,
            "top_edge_foreground_span_px": top_span,
            "bottom_edge_foreground_span_px": bottom_span,
            "side_run_threshold_px": side_threshold,
            "top_span_threshold_px": top_threshold,
        },
        "screening_status": "SUSPICIOUS" if reasons else "CLEAR",
        "screening_reasons": reasons,
        "semantic_completeness_status": "NOT_CHECKED",
        "manual_resolution": {
            "reviewer": None,
            "top_crop_100": None,
            "top_crop_200": None,
            "left_shoulder_crop_100": None,
            "left_shoulder_crop_200": None,
            "right_shoulder_crop_100": None,
            "right_shoulder_crop_200": None,
            "status": "NOT_CHECKED",
        },
        "warning": "CLEAR is screening-only; SUSPICIOUS requires Codex semantic review. This file never grants bust completeness.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["screening_status"])
    for reason in reasons:
        print(f"REASON: {reason}")
    return 2 if reasons else 0


if __name__ == "__main__":
    raise SystemExit(main())
