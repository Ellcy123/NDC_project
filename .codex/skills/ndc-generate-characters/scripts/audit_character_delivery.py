#!/usr/bin/env python3
"""Create mechanical QA evidence for an NDC character card or portrait.

This script deliberately does not issue a formal visual pass. It records
measurable facts and produces overlays/composites that a reviewer must inspect.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


SIZE_PATTERN = re.compile(r"^(\d+)x(\d+)$")


def parse_size(value: str) -> tuple[int, int]:
    match = SIZE_PATTERN.fullmatch(value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("size must use WIDTHxHEIGHT")
    width, height = (int(match.group(1)), int(match.group(2)))
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size values must be positive")
    return width, height


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-type", required=True, choices=("card", "portrait"))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--expected-size", required=True, type=parse_size)
    parser.add_argument(
        "--expected-background",
        choices=("transparent", "opaque-paper", "opaque-white"),
        help="Portrait background contract. Defaults to transparent for backward compatibility.",
    )
    parser.add_argument("--white-tolerance", type=int, default=18)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_nonzero(mask: Image.Image) -> int:
    histogram = mask.convert("L").histogram()
    return sum(histogram[1:])


def white_foreground_mask(image: Image.Image, tolerance: int) -> Image.Image:
    rgba = image.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flattened = Image.alpha_composite(white, rgba).convert("RGB")
    difference = ImageChops.difference(flattened, Image.new("RGB", flattened.size, "white"))
    return difference.convert("L").point(lambda value: 255 if value > tolerance else 0)


def absolute_bbox(mask: Image.Image, region: tuple[int, int, int, int]) -> list[int] | None:
    x0, y0, x1, y1 = region
    local = mask.crop(region).getbbox()
    if local is None:
        return None
    return [x0 + local[0], y0 + local[1], x0 + local[2], y0 + local[3]]


def box_metrics(box: list[int] | None, canvas: tuple[int, int]) -> dict:
    if box is None:
        return {"bbox": None, "width": 0, "height": 0, "width_ratio": 0.0, "height_ratio": 0.0}
    width = box[2] - box[0]
    height = box[3] - box[1]
    return {
        "bbox": box,
        "width": width,
        "height": height,
        "width_ratio": round(width / canvas[0], 6),
        "height_ratio": round(height / canvas[1], 6),
    }


def audit_card(image: Image.Image, output: Path, tolerance: int) -> dict:
    width, height = image.size
    split_x = round(width * 2 / 3)
    split_y = height // 2
    fullbody_edges = [round(split_x * index / 3) for index in range(4)]
    head_edges = [split_x + round((width - split_x) * index / 3) for index in range(4)]
    mask = white_foreground_mask(image, tolerance)
    # Remove thin panel rules and isolated marks before estimating subject boxes.
    # The raw image remains visible in the overlay, so this erosion is evidence
    # assistance rather than a hidden alteration of the asset.
    subject_mask = mask.filter(ImageFilter.MinFilter(7))

    fullbody = {}
    for name, index in zip(("front", "left", "back"), range(3)):
        region = (fullbody_edges[index], 0, fullbody_edges[index + 1], height)
        fullbody[name] = box_metrics(absolute_bbox(subject_mask, region), image.size)

    heads = {}
    for name, index in zip(("front", "right", "back"), range(3)):
        region = (head_edges[index], 0, head_edges[index + 1], split_y)
        heads[name] = box_metrics(absolute_bbox(subject_mask, region), image.size)

    valid_fullbody_boxes = [item["bbox"] for item in fullbody.values() if item["bbox"]]
    height_values = [item[3] - item[1] for item in valid_fullbody_boxes]
    top_values = [item[1] for item in valid_fullbody_boxes]
    bottom_values = [item[3] for item in valid_fullbody_boxes]

    overlay = image.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)
    guide_width = max(2, round(width / 960))
    draw.line((split_x, 0, split_x, height), fill=(0, 120, 255), width=guide_width)
    draw.line((split_x, split_y, width, split_y), fill=(0, 120, 255), width=guide_width)
    for edge in fullbody_edges[1:-1]:
        draw.line((edge, 0, edge, height), fill=(120, 190, 255), width=guide_width)
    for edge in head_edges[1:-1]:
        draw.line((edge, 0, edge, split_y), fill=(120, 190, 255), width=guide_width)
    for item in list(fullbody.values()) + list(heads.values()):
        if item["bbox"]:
            draw.rectangle(item["bbox"], outline=(255, 40, 40), width=guide_width)
    overlay_path = output / "card_layout_overlay.png"
    overlay.save(overlay_path, format="PNG", optimize=True)

    return {
        "layout_definition": {
            "fullbody_region": [0, 0, split_x, height],
            "head_region": [split_x, 0, width, split_y],
            "detail_region": [split_x, split_y, width, height],
        },
        "fullbody_regions": fullbody,
        "head_regions": heads,
        "fullbody_height_spread_px": max(height_values) - min(height_values) if len(height_values) == 3 else None,
        "fullbody_head_top_spread_px": max(top_values) - min(top_values) if len(top_values) == 3 else None,
        "fullbody_heel_spread_px": max(bottom_values) - min(bottom_values) if len(bottom_values) == 3 else None,
        "qa_overlay": str(overlay_path),
        "measurement_warning": "Thin rules are eroded before subject-box estimation; inspect the overlay because thick borders or unrelated solid marks can still contaminate a box.",
    }


def make_portrait_composites(image: Image.Image, output: Path) -> dict:
    rgba = image.convert("RGBA")
    backgrounds = {
        "black": (0, 0, 0, 255),
        "white": (255, 255, 255, 255),
        "red": (220, 0, 40, 255),
        "gray": (128, 128, 128, 255),
    }
    paths = {}
    previews = []
    for name, color in backgrounds.items():
        composite = Image.alpha_composite(Image.new("RGBA", rgba.size, color), rgba).convert("RGB")
        path = output / f"portrait_on_{name}.png"
        composite.save(path, format="PNG", optimize=True)
        paths[name] = str(path)
        previews.append(ImageOps.contain(composite, (640, 800)))

    sheet = Image.new("RGB", (1280, 1600), "white")
    for index, preview in enumerate(previews):
        row, column = divmod(index, 2)
        x = column * 640 + (640 - preview.width) // 2
        y = row * 800 + (800 - preview.height) // 2
        sheet.paste(preview, (x, y))
    sheet_path = output / "portrait_edge_review_sheet.png"
    sheet.save(sheet_path, format="PNG", optimize=True)

    alpha = rgba.getchannel("A")
    alpha_bbox = alpha.getbbox()
    alpha_pixels = count_nonzero(alpha)
    eroded = alpha.filter(ImageFilter.MinFilter(3))
    inner_edge = ImageChops.subtract(alpha, eroded).point(lambda value: 255 if value else 0)
    edge_pixels = count_nonzero(inner_edge)
    gray = rgba.convert("RGB").convert("L")
    near_white = gray.point(lambda value: 255 if value >= 235 else 0)
    near_white_edge = ImageChops.multiply(inner_edge, near_white)
    near_white_edge_pixels = count_nonzero(near_white_edge)

    return {
        "has_alpha_channel": "A" in image.getbands(),
        "has_transparent_pixels": alpha.getextrema()[0] < 255,
        "alpha_bbox": list(alpha_bbox) if alpha_bbox else None,
        "visible_alpha_pixel_ratio": round(alpha_pixels / (image.width * image.height), 6),
        "inner_edge_pixel_count": edge_pixels,
        "near_white_inner_edge_pixel_ratio": round(near_white_edge_pixels / edge_pixels, 6) if edge_pixels else 0.0,
        "background_composites": paths,
        "edge_review_sheet": str(sheet_path),
        "measurement_warning": "The near-white edge ratio is a diagnostic signal, not an automatic halo verdict; inspect all background composites.",
    }


def main() -> None:
    args = parse_args()
    source = args.input.resolve()
    if not source.is_file():
        raise SystemExit(f"input image does not exist: {source}")
    if not 0 <= args.white_tolerance <= 255:
        raise SystemExit("--white-tolerance must be from 0 to 255")
    expected_background = args.expected_background
    if expected_background is None:
        expected_background = "transparent" if args.asset_type == "portrait" else "opaque-white"
    if args.asset_type == "card" and args.expected_background not in (None, "opaque-white"):
        raise SystemExit("cards currently support only --expected-background opaque-white")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        opened.load()
        image = opened.copy()
        width, height = image.size
        expected_width, expected_height = args.expected_size
        ratio_ok = width * expected_height == height * expected_width
        dimensions_ok = (width, height) == args.expected_size
        details = (
            audit_card(image, output, args.white_tolerance)
            if args.asset_type == "card"
            else make_portrait_composites(image, output)
        )

    mechanical_checks = {
        "ratio": "PASS" if ratio_ok else "FAIL",
        "dimensions": "PASS" if dimensions_ok else "FAIL",
    }
    if args.asset_type == "portrait":
        if expected_background == "transparent":
            mechanical_checks["alpha_channel"] = "PASS" if details["has_alpha_channel"] else "FAIL"
            mechanical_checks["transparent_pixels"] = "PASS" if details["has_transparent_pixels"] else "FAIL"
        else:
            mechanical_checks["opaque_background"] = "PASS" if not details["has_transparent_pixels"] else "FAIL"

    report = {
        "protocol": "ndc-character-delivery-mechanical-audit/v1",
        "asset_type": args.asset_type,
        "input": str(source),
        "sha256": sha256(source),
        "mode": image.mode,
        "dimensions": [width, height],
        "expected_dimensions": [expected_width, expected_height],
        "expected_background": expected_background,
        "mechanical_checks": mechanical_checks,
        "mechanical_status": "PASS" if all(value == "PASS" for value in mechanical_checks.values()) else "FAIL",
        "formal_status": "NOT_CHECKED",
        "formal_status_reason": "Identity, structure, provenance, style, and complete visual review require stage receipts.",
        "details": details,
    }
    report_path = output / "mechanical_audit.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mechanical status: {report['mechanical_status']}")
    print("Formal status: NOT_CHECKED")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
