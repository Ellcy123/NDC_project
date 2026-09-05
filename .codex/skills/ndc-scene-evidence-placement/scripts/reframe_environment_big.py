#!/usr/bin/env python3
"""Apply one recorded, non-semantic environment-Big reframe on a duplicate.

The script only rotates a premultiplied-alpha source, crops to the resulting
content bounds with declared transparent padding, and zeros RGB under Alpha 0.
It never draws, generates, removes, or replaces semantic image content or
readable text. Its JSON report is technical evidence, not visual approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def premultiply(source: Image.Image) -> Image.Image:
    raw = source.tobytes()
    output = bytearray(len(raw))
    for index in range(0, len(raw), 4):
        alpha = raw[index + 3]
        output[index] = (raw[index] * alpha + 127) // 255
        output[index + 1] = (raw[index + 1] * alpha + 127) // 255
        output[index + 2] = (raw[index + 2] * alpha + 127) // 255
        output[index + 3] = alpha
    return Image.frombytes("RGBA", source.size, bytes(output))


def unpremultiply_and_zero(source: Image.Image) -> Image.Image:
    raw = source.tobytes()
    output = bytearray(len(raw))
    for index in range(0, len(raw), 4):
        alpha = raw[index + 3]
        if alpha:
            output[index] = min(255, (raw[index] * 255 + alpha // 2) // alpha)
            output[index + 1] = min(255, (raw[index + 1] * 255 + alpha // 2) // alpha)
            output[index + 2] = min(255, (raw[index + 2] * 255 + alpha // 2) // alpha)
            output[index + 3] = alpha
    return Image.frombytes("RGBA", source.size, bytes(output))


def alpha_zero_rgb_nonzero_pixels(source: Image.Image) -> int:
    raw = source.tobytes()
    return sum(
        1
        for index in range(0, len(raw), 4)
        if raw[index + 3] == 0 and (raw[index] or raw[index + 1] or raw[index + 2])
    )


def parse_box(value: str, width: int, height: int) -> tuple[int, int, int, int]:
    try:
        left, top, right, bottom = (int(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("source crop must be left,top,right,bottom") from exc
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise argparse.ArgumentTypeError("source crop must be inside the input canvas")
    return left, top, right, bottom


def apply_edge_feather(source: Image.Image, edges: set[str], pixels: int) -> Image.Image:
    if not edges or pixels == 0:
        return source
    raw = source.tobytes()
    output = bytearray(raw)
    width, height = source.size
    for y in range(height):
        for x in range(width):
            distance = pixels
            if "left" in edges:
                distance = min(distance, x)
            if "right" in edges:
                distance = min(distance, width - 1 - x)
            if "top" in edges:
                distance = min(distance, y)
            if "bottom" in edges:
                distance = min(distance, height - 1 - y)
            index = (y * width + x) * 4
            alpha = raw[index + 3]
            feathered_alpha = (alpha * max(0, min(pixels, distance)) + pixels // 2) // pixels
            output[index + 3] = feathered_alpha
            if feathered_alpha == 0:
                output[index] = output[index + 1] = output[index + 2] = 0
    return Image.frombytes("RGBA", source.size, bytes(output))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--correction-degrees", required=True, type=float)
    parser.add_argument("--padding", type=int, default=32)
    parser.add_argument("--source-crop", help="left,top,right,bottom in the input canvas")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument(
        "--feather-edges",
        default="",
        help="comma-separated subset of left,right,top,bottom for a documented contextual-edge taper",
    )
    parser.add_argument("--feather-pixels", type=int, default=0)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"missing input: {args.input}")
    if args.padding < 0:
        parser.error("padding must be non-negative")
    if abs(args.correction_degrees) > 45:
        parser.error("correction-degrees must be between -45 and 45")
    if not 0 < args.scale <= 2:
        parser.error("scale must be greater than 0 and no more than 2")
    edges = {edge.strip() for edge in args.feather_edges.split(",") if edge.strip()}
    if not edges.issubset({"left", "right", "top", "bottom"}):
        parser.error("feather-edges only accepts left,right,top,bottom")
    if args.feather_pixels < 0:
        parser.error("feather-pixels must be non-negative")
    if edges and args.feather_pixels == 0:
        parser.error("feather-pixels must be positive when feather-edges is supplied")
    if args.feather_pixels and not edges:
        parser.error("feather-edges is required when feather-pixels is positive")

    with Image.open(args.input) as opened:
        source = opened.convert("RGBA")
    input_size = source.size
    source_crop = parse_box(args.source_crop, *source.size) if args.source_crop else None
    if source_crop:
        source = source.crop(source_crop)
    rotated = premultiply(source).rotate(
        args.correction_degrees,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )
    if args.scale != 1:
        rotated = rotated.resize(
            (round(rotated.width * args.scale), round(rotated.height * args.scale)),
            resample=Image.Resampling.LANCZOS,
        )
    corrected = unpremultiply_and_zero(rotated)
    corrected = apply_edge_feather(corrected, edges, args.feather_pixels)
    bounds = corrected.getchannel("A").getbbox()
    if bounds is None:
        parser.error("rotation removed every Alpha-positive pixel")
    left = max(0, bounds[0] - args.padding)
    top = max(0, bounds[1] - args.padding)
    right = min(corrected.width, bounds[2] + args.padding)
    bottom = min(corrected.height, bounds[3] + args.padding)
    result = corrected.crop((left, top, right, bottom))
    # Cropping cannot create pixels beyond the rotated source canvas.  When a
    # contextual taper reaches that canvas edge, restore only the missing
    # transparent margin so the delivery alpha is never hard-clipped there.
    extension = {
        "left": max(0, args.padding - bounds[0]),
        "top": max(0, args.padding - bounds[1]),
        "right": max(0, bounds[2] + args.padding - corrected.width),
        "bottom": max(0, bounds[3] + args.padding - corrected.height),
    }
    if any(extension.values()):
        expanded = Image.new(
            "RGBA",
            (
                result.width + extension["left"] + extension["right"],
                result.height + extension["top"] + extension["bottom"],
            ),
        )
        expanded.alpha_composite(result, (extension["left"], extension["top"]))
        result = expanded

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    report = {
        "schema": "ndc-environment-big-reframe/v1",
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "input_canvas": list(input_size),
        "source_crop": list(source_crop) if source_crop else None,
        "correction_degrees": args.correction_degrees,
        "uniform_scale": args.scale,
        "contextual_edge_feather": {
            "edges": sorted(edges),
            "pixels": args.feather_pixels,
        },
        "final_post_transform_rotation_degrees": 0,
        "crop_from_rotated_canvas": [left, top, right, bottom],
        "transparent_padding": args.padding,
        "canvas_extension_for_clipped_padding": extension,
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "output_canvas": list(result.size),
        "output_alpha_bounds": list(result.getchannel("A").getbbox()),
        "alpha_zero_rgb_nonzero_pixels": alpha_zero_rgb_nonzero_pixels(result),
        "visual_decision": "NOT_SET_BY_SCRIPT",
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
