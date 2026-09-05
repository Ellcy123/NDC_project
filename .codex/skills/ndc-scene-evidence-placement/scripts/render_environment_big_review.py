#!/usr/bin/env python3
"""Render non-delivery visual-review views for an environmental Big PNG.

This script never changes the input. It exists only to make the required
whole-image checkerboard and nearest-neighbour local inspection views, plus a
small Alpha/RGB technical report. It never writes a visual PASS decision.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def parse_box(value: str, width: int, height: int) -> tuple[int, int, int, int]:
    try:
        left, top, right, bottom = (int(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("focus box must be left,top,right,bottom") from exc
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise argparse.ArgumentTypeError("focus box must be inside the input canvas")
    return left, top, right, bottom


def checkerboard(size: tuple[int, int], light: bool, tile: int = 16) -> Image.Image:
    colors = ((232, 232, 232, 255), (184, 184, 184, 255)) if light else ((62, 62, 62, 255), (34, 34, 34, 255))
    image = Image.new("RGBA", size, colors[0])
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if ((x // tile) + (y // tile)) % 2:
                draw.rectangle((x, y, min(x + tile - 1, size[0] - 1), min(y + tile - 1, size[1] - 1)), fill=colors[1])
    return image


def composite_checker(source: Image.Image, light: bool) -> Image.Image:
    background = checkerboard(source.size, light)
    return Image.alpha_composite(background, source).convert("RGB")


def alpha_zero_rgb_nonzero_pixels(source: Image.Image) -> int:
    raw = source.tobytes()
    count = 0
    for index in range(0, len(raw), 4):
        if raw[index + 3] == 0 and (raw[index] or raw[index + 1] or raw[index + 2]):
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--focus-box", help="left,top,right,bottom; defaults to Alpha bounds")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"missing input: {args.input}")
    with Image.open(args.input) as opened:
        source = opened.convert("RGBA")
    alpha = source.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        parser.error("input has no Alpha-positive pixels")
    focus = parse_box(args.focus_box, *source.size) if args.focus_box else bounds

    args.output_dir.mkdir(parents=True, exist_ok=True)
    light = composite_checker(source, True)
    dark = composite_checker(source, False)
    light_path = args.output_dir / "whole_100_light_checkerboard.png"
    dark_path = args.output_dir / "whole_100_dark_checkerboard.png"
    local_path = args.output_dir / "local_200_light_checkerboard.png"
    light.save(light_path)
    dark.save(dark_path)
    light.crop(focus).resize(((focus[2] - focus[0]) * 2, (focus[3] - focus[1]) * 2), Image.Resampling.NEAREST).save(local_path)

    report = {
        "schema": "ndc-environment-big-review-render/v1",
        "input": str(args.input),
        "canvas": list(source.size),
        "alpha_bounds": list(bounds),
        "focus_box": list(focus),
        "alpha_zero_rgb_nonzero_pixels": alpha_zero_rgb_nonzero_pixels(source),
        "outputs": {
            "whole_100_light_checkerboard": str(light_path),
            "whole_100_dark_checkerboard": str(dark_path),
            "local_200_light_checkerboard": str(local_path),
        },
        "visual_decision": "NOT_SET_BY_SCRIPT",
    }
    (args.output_dir / "render_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
