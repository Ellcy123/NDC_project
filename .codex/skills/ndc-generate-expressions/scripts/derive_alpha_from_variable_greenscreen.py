#!/usr/bin/env python3
"""Derive RGBA from a bright but non-uniform generated green background.

This path is for Image-model outputs whose chroma background contains a mild
gradient.  It keys green dominance instead of distance from one exact RGB and
records review evidence; it never grants formal edge approval by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


KEY = np.array([0.0, 255.0, 43.0], dtype=np.float64)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--foreground-dominance", type=float, default=25.0)
    parser.add_argument("--background-dominance", type=float, default=100.0)
    args = parser.parse_args()
    if not args.foreground_dominance < args.background_dominance:
        parser.error("foreground-dominance must be below background-dominance")

    rgb = np.asarray(Image.open(args.input).convert("RGB"), dtype=np.uint8)
    work = rgb.astype(np.float64)
    dominance = work[:, :, 1] - np.maximum(work[:, :, 0], work[:, :, 2])
    alpha = np.clip(
        255.0
        * (args.background_dominance - dominance)
        / (args.background_dominance - args.foreground_dominance),
        0.0,
        255.0,
    ).round().astype(np.uint8)

    # Undo the known-key contribution on soft pixels so downsampling does not
    # resurrect a green fringe over dark dialogue backgrounds.
    out_rgb = work.copy()
    soft = (alpha > 0) & (alpha < 255)
    if np.any(soft):
        a = (alpha[soft].astype(np.float64) / 255.0)[:, None]
        solved = (work[soft] - (1.0 - a) * KEY) / np.maximum(a, 1e-6)
        out_rgb[soft] = np.clip(solved, 0.0, 255.0)

    out = np.dstack([out_rgb.round().astype(np.uint8), alpha])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out, mode="RGBA").save(args.output)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(
        json.dumps(
            {
                "schema": "ndc-variable-greenscreen-alpha/v1",
                "input": str(args.input.resolve()),
                "input_sha256": sha256(args.input),
                "output": str(args.output.resolve()),
                "output_sha256": sha256(args.output),
                "foreground_dominance": args.foreground_dominance,
                "background_dominance": args.background_dominance,
                "alpha_zero_pixels": int((alpha == 0).sum()),
                "alpha_soft_pixels": int(soft.sum()),
                "alpha_full_pixels": int((alpha == 255).sum()),
                "edge_status": "NOT_CHECKED",
                "formal_status": "NOT_CHECKED",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
