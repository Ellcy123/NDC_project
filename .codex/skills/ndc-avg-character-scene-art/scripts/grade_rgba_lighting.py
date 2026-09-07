from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def parse_rgb_gain(value: str) -> tuple[float, float, float]:
    parts = [float(part) for part in value.split(",")]
    if len(parts) != 3 or any(part <= 0 for part in parts):
        raise argparse.ArgumentTypeError(
            "rgb gain must be three positive comma-separated values"
        )
    return parts[0], parts[1], parts[2]


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    return np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    )


def linear_to_srgb(rgb: np.ndarray) -> np.ndarray:
    return np.where(
        rgb <= 0.0031308,
        rgb * 12.92,
        1.055 * np.power(rgb, 1.0 / 2.4) - 0.055,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministically grade RGB inside an RGBA actor while preserving "
            "Alpha, dimensions, and transparent pixels"
        )
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--exposure-ev", type=float, default=-0.60)
    parser.add_argument(
        "--gamma",
        type=float,
        default=1.08,
        help="Direct sRGB exponent; values above 1 darken midtones",
    )
    parser.add_argument("--contrast", type=float, default=0.98)
    parser.add_argument("--saturation", type=float, default=0.88)
    parser.add_argument(
        "--rgb-gain",
        type=parse_rgb_gain,
        default=(0.97, 0.99, 1.01),
    )
    args = parser.parse_args()

    if args.gamma <= 0 or args.contrast < 0 or args.saturation < 0:
        parser.error(
            "gamma must be positive; contrast and saturation must be non-negative"
        )
    if args.input.resolve() == args.output.resolve():
        parser.error("output must not overwrite input")

    image = Image.open(args.input).convert("RGBA")
    source = np.asarray(image, dtype=np.uint8)
    rgb = source[..., :3].astype(np.float32) / 255.0
    alpha = source[..., 3].copy()
    visible = alpha > 0

    linear = srgb_to_linear(rgb)
    linear *= 2.0**args.exposure_ev
    linear *= np.asarray(args.rgb_gain, dtype=np.float32)
    graded = np.clip(
        linear_to_srgb(np.clip(linear, 0.0, 1.0)),
        0.0,
        1.0,
    )
    graded = np.power(graded, args.gamma)
    graded = np.clip((graded - 0.5) * args.contrast + 0.5, 0.0, 1.0)
    luma = np.sum(
        graded * np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32),
        axis=2,
        keepdims=True,
    )
    graded = np.clip(luma + (graded - luma) * args.saturation, 0.0, 1.0)

    output = source.copy()
    output_rgb = np.rint(graded * 255.0).astype(np.uint8)
    output[..., :3][visible] = output_rgb[visible]
    output[..., 3] = alpha

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output, mode="RGBA").save(args.output)

    ys, xs = np.nonzero(visible)
    alpha_bbox = (
        None
        if len(xs) == 0
        else [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
    )
    output_image = Image.open(args.output).convert("RGBA")
    saved = np.asarray(output_image, dtype=np.uint8)
    alpha_unchanged = bool(np.array_equal(alpha, saved[..., 3]))
    changed_outside_alpha = int(
        np.count_nonzero(
            np.any(source[..., :3][~visible] != saved[..., :3][~visible], axis=1)
        )
    )
    dimensions_unchanged = image.size == output_image.size
    saved_visible = saved[..., 3] > 0
    saved_ys, saved_xs = np.nonzero(saved_visible)
    saved_alpha_bbox = (
        None
        if len(saved_xs) == 0
        else [
            int(saved_xs.min()),
            int(saved_ys.min()),
            int(saved_xs.max() + 1),
            int(saved_ys.max() + 1),
        ]
    )
    alpha_bbox_unchanged = alpha_bbox == saved_alpha_bbox
    passed = (
        dimensions_unchanged
        and alpha_unchanged
        and alpha_bbox_unchanged
        and changed_outside_alpha == 0
    )

    report = {
        "input": str(args.input),
        "output": str(args.output),
        "input_size": list(image.size),
        "output_size": list(output_image.size),
        "dimensions_unchanged": dimensions_unchanged,
        "input_alpha_bbox": alpha_bbox,
        "output_alpha_bbox": saved_alpha_bbox,
        "alpha_bbox_unchanged": alpha_bbox_unchanged,
        "parameters": {
            "exposure_ev": args.exposure_ev,
            "gamma": args.gamma,
            "contrast": args.contrast,
            "saturation": args.saturation,
            "rgb_gain": list(args.rgb_gain),
        },
        "alpha_unchanged": alpha_unchanged,
        "changed_rgb_pixels_outside_alpha": changed_outside_alpha,
        "input_sha256": sha256(args.input),
        "output_sha256": sha256(args.output),
        "passed": passed,
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
