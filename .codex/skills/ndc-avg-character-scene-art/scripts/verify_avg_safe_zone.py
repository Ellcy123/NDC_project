#!/usr/bin/env python3
"""Verify that generated actor Alpha does not enter the selected AVG TalkPanel side."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image


REFERENCE_SIZE = (2560, 1600)
REFERENCE_PANEL_WIDTH = 913


def default_panel() -> Path:
    """Resolve the runtime asset only when a preview actually requires it."""
    for ancestor in Path(__file__).resolve().parents:
        module_root = ancestor / "scripts" / "art_pipeline"
        if (module_root / "art_paths.py").is_file():
            sys.path.insert(0, str(module_root))
            from art_paths import load_art_paths

            return load_art_paths().engine_root / "Assets/Resources/Art/UI/AVG/left_BG.png"
    raise RuntimeError("Cannot locate Git-managed art_paths.py; pass --panel explicitly")


def parse_rect(value: str) -> tuple[int, int, int, int]:
    parts = value.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("Expected LEFT,TOP,WIDTH,HEIGHT")
    try:
        rect = tuple(int(part) for part in parts)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Rectangle values must be integers") from error
    if rect[2] <= 0 or rect[3] <= 0:
        raise argparse.ArgumentTypeError("Rectangle width and height must be positive")
    return rect


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_safe_rect(
    size: tuple[int, int], side: str, explicit: tuple[int, int, int, int] | None
) -> tuple[int, int, int, int]:
    if explicit is not None:
        left, top, width, height = explicit
    elif size == REFERENCE_SIZE:
        width = REFERENCE_PANEL_WIDTH
        height = REFERENCE_SIZE[1]
        left = 0 if side == "left" else REFERENCE_SIZE[0] - width
        top = 0
    else:
        raise ValueError(
            f"Image size {size} is not the 2560x1600 TalkPanel reference size; "
            "pass --safe-rect after resolving the runtime source-to-render mapping"
        )

    if left < 0 or top < 0 or left + width > size[0] or top + height > size[1]:
        raise ValueError(f"Safe rectangle {(left, top, width, height)} is outside image {size}")
    return left, top, width, height


def load_mask(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path)
    if image.size != size:
        raise ValueError(f"Mask {path} has size {image.size}, expected {size}")
    if image.mode == "RGBA":
        return image.getchannel("A")
    return image.convert("L")


def make_panel_preview(
    image: Image.Image,
    panel_path: Path,
    side: str,
    rect: tuple[int, int, int, int],
) -> Image.Image:
    left, top, width, height = rect
    panel = Image.open(panel_path).convert("RGBA")
    if side == "right":
        panel = panel.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if panel.size != (width, height):
        panel = panel.resize((width, height), Image.Resampling.LANCZOS)
    preview = image.convert("RGBA")
    preview.alpha_composite(panel, (left, top))
    return preview


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True, help="Full-scene image or preview")
    parser.add_argument("--union-mask", type=Path, required=True, help="Full-size actor Alpha union")
    parser.add_argument("--side", choices=("left", "right"), required=True)
    parser.add_argument("--safe-rect", type=parse_rect, help="Mapped LEFT,TOP,WIDTH,HEIGHT")
    parser.add_argument("--panel", type=Path, help="UI source; defaults to the configured engine asset")
    parser.add_argument("--preview-output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--allow-intersection",
        action="store_true",
        help="Return success even when Alpha enters the safe zone; useful for auditing old assets",
    )
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGBA")
    rect = resolve_safe_rect(image.size, args.side, args.safe_rect)
    union = load_mask(args.union_mask, image.size)
    left, top, width, height = rect
    safe_alpha = union.crop((left, top, left + width, top + height))
    histogram = safe_alpha.histogram()
    intersection_pixels = sum(histogram[1:])
    intersection_bbox_local = safe_alpha.getbbox()
    intersection_bbox_scene = None
    if intersection_bbox_local is not None:
        intersection_bbox_scene = [
            intersection_bbox_local[0] + left,
            intersection_bbox_local[1] + top,
            intersection_bbox_local[2] + left,
            intersection_bbox_local[3] + top,
        ]

    result = {
        "image": str(args.image.resolve()),
        "image_sha256": sha256(args.image),
        "image_size": list(image.size),
        "union_mask": str(args.union_mask.resolve()),
        "union_mask_sha256": sha256(args.union_mask),
        "panel_side": args.side,
        "safe_rect": [left, top, width, height],
        "actor_alpha_pixels_inside_safe_rect": intersection_pixels,
        "intersection_bbox_scene": intersection_bbox_scene,
        "passed": intersection_pixels == 0,
    }

    if args.preview_output is not None:
        if args.panel is None:
            args.panel = default_panel()
        args.preview_output.parent.mkdir(parents=True, exist_ok=True)
        preview = make_panel_preview(image, args.panel, args.side, rect)
        preview.save(args.preview_output)
        result["preview_output"] = str(args.preview_output.resolve())
        result["panel"] = str(args.panel.resolve())
        result["panel_sha256"] = sha256(args.panel)

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["passed"] or args.allow_intersection:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
