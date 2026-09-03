#!/usr/bin/env python3
"""Compose approved NDC character-card modules onto an exact white 16:9 canvas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw


BASE_W = 3840
BASE_H = 2160


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--width", type=int, default=BASE_W)
    parser.add_argument("--height", type=int, default=BASE_H)
    parser.add_argument("--qa-overlay-out", type=Path)
    return parser.parse_args()


def resolve(manifest_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else manifest_dir / path


def trim_white(image: Image.Image, tolerance: int = 18) -> Image.Image:
    rgba = image.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flattened = Image.alpha_composite(white, rgba).convert("RGB")
    difference = ImageChops.difference(flattened, Image.new("RGB", flattened.size, "white"))
    mask = difference.convert("L").point(lambda value: 255 if value > tolerance else 0)
    bbox = mask.getbbox()
    return flattened.crop(bbox) if bbox else flattened


def paste_contained(
    canvas: Image.Image,
    image_path: Path,
    box: tuple[int, int, int, int],
    align: str = "center",
    allow_upscale: bool = False,
) -> tuple[int, int, int, int]:
    if not image_path.is_file():
        raise FileNotFoundError(f"Missing panel: {image_path}")
    with Image.open(image_path) as source:
        panel = trim_white(source)
    x, y, width, height = box
    scale = min(width / panel.width, height / panel.height)
    if not allow_upscale:
        scale = min(scale, 1.0)
    resized = panel.resize(
        (max(1, round(panel.width * scale)), max(1, round(panel.height * scale))),
        Image.Resampling.LANCZOS,
    )
    px = x + (width - resized.width) // 2
    if align == "top":
        py = y
    elif align == "bottom":
        py = y + height - resized.height
    else:
        py = y + (height - resized.height) // 2
    canvas.paste(resized, (px, py))
    return px, py, resized.width, resized.height


def load_trimmed(image_path: Path) -> Image.Image:
    if not image_path.is_file():
        raise FileNotFoundError(f"Missing panel: {image_path}")
    with Image.open(image_path) as source:
        return trim_white(source)


def paste_uniform_fullbodies(
    canvas: Image.Image,
    image_paths: list[Path],
    boxes: list[tuple[int, int, int, int]],
    minimum_fill_ratio: float,
) -> list[tuple[int, int, int, int]]:
    """Place all full bodies at one subject height without interpolation upscale."""
    panels = [load_trimmed(path) for path in image_paths]
    maximum_heights = []
    for panel, (_, _, box_width, box_height) in zip(panels, boxes):
        width_limited_height = panel.height * box_width / panel.width
        maximum_heights.append(min(panel.height, box_height, width_limited_height))
    common_height = max(1, int(min(maximum_heights)))
    required_height = round(min(box[3] for box in boxes) * minimum_fill_ratio)
    if common_height < required_height:
        raise RuntimeError(
            "Full-body modules cannot reach the required common subject height "
            f"without upscaling: available={common_height}px required={required_height}px"
        )

    placements = []
    for panel, (x, y, box_width, box_height) in zip(panels, boxes):
        scale = common_height / panel.height
        if scale > 1.0 + 1e-9:
            raise RuntimeError("Full-body normalization attempted an interpolation upscale")
        resized = panel.resize(
            (max(1, round(panel.width * scale)), common_height),
            Image.Resampling.LANCZOS,
        )
        if resized.width > box_width or resized.height > box_height:
            raise RuntimeError("Normalized full-body panel exceeds its layout box")
        px = x + (box_width - resized.width) // 2
        py = y + (box_height - resized.height) // 2
        canvas.paste(resized, (px, py))
        placements.append((px, py, resized.width, resized.height))
    return placements


def scaled_box(box: tuple[int, int, int, int], sx: float, sy: float) -> tuple[int, int, int, int]:
    x, y, width, height = box
    return round(x * sx), round(y * sy), round(width * sx), round(height * sy)


def require_keys(mapping: dict, keys: Iterable[str], label: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ValueError(f"Manifest {label} is missing: {', '.join(missing)}")


def main() -> None:
    args = parse_args()
    if args.width <= 0 or args.height <= 0 or args.width * 9 != args.height * 16:
        raise ValueError("Output canvas must be a positive exact 16:9 size")

    manifest_path = args.manifest.resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    require_keys(data, ("fullbody", "head", "shoe", "details"), "root")
    require_keys(data["fullbody"], ("front", "left", "back"), "fullbody")
    require_keys(data["head"], ("front", "right", "back"), "head")
    details = data["details"]
    if not isinstance(details, list) or len(details) > 3:
        raise ValueError("Manifest details must be a list containing zero to three paths")
    minimum_fullbody_fill = data.get("minimum_fullbody_fill", 0.72)
    if not isinstance(minimum_fullbody_fill, (int, float)) or not 0.65 <= minimum_fullbody_fill <= 0.95:
        raise ValueError("minimum_fullbody_fill must be a number from 0.65 to 0.95")

    manifest_dir = manifest_path.parent
    sx = args.width / BASE_W
    sy = args.height / BASE_H
    canvas = Image.new("RGB", (args.width, args.height), "white")

    # User-approved layout: full-body triptych occupies the left two thirds.
    fullbody_boxes = [
        scaled_box(box, sx, sy)
        for box in (
            (40, 45, 800, 2070),
            (880, 45, 800, 2070),
            (1720, 45, 800, 2070),
        )
    ]
    fullbody_paths = [
        resolve(manifest_dir, data["fullbody"][key])
        for key in ("front", "left", "back")
    ]
    fullbody_placements = paste_uniform_fullbodies(
        canvas,
        fullbody_paths,
        fullbody_boxes,
        float(minimum_fullbody_fill),
    )

    # Head triptych occupies the upper half of the remaining right third.
    head_boxes = (
        (2580, 60, 380, 960),
        (3000, 60, 380, 960),
        (3420, 60, 380, 960),
    )
    for key, box in zip(("front", "right", "back"), head_boxes):
        paste_contained(canvas, resolve(manifest_dir, data["head"][key]), scaled_box(box, sx, sy))

    paste_contained(
        canvas,
        resolve(manifest_dir, data["shoe"]),
        scaled_box((2590, 1120, 1180, 420), sx, sy),
    )

    if details:
        gap = 36
        area_x, area_y, area_w, area_h = 2590, 1580, 1180, 500
        detail_w = (area_w - gap * (len(details) - 1)) // len(details)
        for index, detail in enumerate(details):
            box = (area_x + index * (detail_w + gap), area_y, detail_w, area_h)
            paste_contained(canvas, resolve(manifest_dir, detail), scaled_box(box, sx, sy))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, format="PNG", optimize=True)
    print(f"Saved {args.out.resolve()} ({args.width}x{args.height})")

    if args.qa_overlay_out:
        qa = canvas.copy()
        draw = ImageDraw.Draw(qa)
        left_x = round(30 * sx)
        right_x = round(2530 * sx)
        fullbody_y = fullbody_placements[0][1]
        fullbody_height = fullbody_placements[0][3]
        guide_fractions = data.get("qa_guide_fractions", [0.0, 0.16, 0.48, 0.75, 1.0])
        if not isinstance(guide_fractions, list) or any(
            not isinstance(value, (int, float)) or value < 0 or value > 1
            for value in guide_fractions
        ):
            raise ValueError("qa_guide_fractions must be a list of numbers from zero to one")
        line_width = max(2, round(5 * sy))
        for fraction in guide_fractions:
            y = fullbody_y + round(fullbody_height * fraction)
            draw.line((left_x, y, right_x, y), fill=(255, 30, 30), width=line_width)
        args.qa_overlay_out.parent.mkdir(parents=True, exist_ok=True)
        qa.save(args.qa_overlay_out, format="PNG", optimize=True)
        print(f"Saved QA overlay {args.qa_overlay_out.resolve()}")


if __name__ == "__main__":
    main()
