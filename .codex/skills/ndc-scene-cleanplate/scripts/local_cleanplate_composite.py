#!/usr/bin/env python3
"""Composite AI-generated clean content locally while locking the source image."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

try:
    import numpy as np
except ModuleNotFoundError as error:
    raise SystemExit(
        "numpy is required; run this script with the Codex workspace Python runtime"
    ) from error

from PIL import Image, ImageDraw, ImageFilter


Box = tuple[int, int, int, int]
Point = tuple[int, int]
Polygon = list[Point]


def parse_box(raw: str) -> Box:
    values = tuple(int(value.strip()) for value in raw.split(","))
    if len(values) != 4 or values[0] >= values[2] or values[1] >= values[3]:
        raise argparse.ArgumentTypeError("box must be left,top,right,bottom")
    return values


def parse_polygon(raw: str) -> Polygon:
    points: Polygon = []
    for raw_point in raw.split(";"):
        values = tuple(int(value.strip()) for value in raw_point.split(","))
        if len(values) != 2:
            raise argparse.ArgumentTypeError(
                "polygon must be x,y;x,y;x,y with at least three points"
            )
        points.append(values)
    if len(points) < 3:
        raise argparse.ArgumentTypeError("polygon requires at least three points")
    return points


def parse_group(raw: str) -> list[Polygon]:
    polygons = [parse_polygon(value.strip()) for value in raw.split("|") if value.strip()]
    if not polygons:
        raise argparse.ArgumentTypeError("group requires at least one polygon")
    return polygons


def bounded_max_filter(image: Image.Image, radius: int) -> Image.Image:
    maximum_radius = max(0, (min(image.size) - 1) // 2)
    safe_radius = min(radius, maximum_radius)
    if safe_radius <= 0:
        return image.copy()
    return image.filter(ImageFilter.MaxFilter(safe_radius * 2 + 1))


def validate_group_inside_guide(
    polygons: list[Polygon], guide_crop: Box, required_margin: int
) -> None:
    left, top, right, bottom = guide_crop
    for index, polygon in enumerate(polygons, start=1):
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        if (
            min(xs) < left + required_margin
            or max(xs) >= right - required_margin
            or min(ys) < top + required_margin
            or max(ys) >= bottom - required_margin
        ):
            raise SystemExit(
                f"polygon {index} lacks {required_margin}px guide context; "
                "move the guide cut or use a larger bridge crop"
            )


def composite_group(
    base: np.ndarray,
    source: np.ndarray,
    guide: np.ndarray,
    polygons: list[Polygon],
    ring_inner: int,
    ring_outer: int,
    grow: int,
    feather: float,
) -> tuple[np.ndarray, np.ndarray]:
    points = [point for polygon in polygons for point in polygon]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    margin = max(ring_outer + 10, grow + math.ceil(feather * 4) + 5)
    x0 = max(0, min(xs) - margin)
    x1 = min(source.shape[1], max(xs) + margin + 1)
    y0 = max(0, min(ys) - margin)
    y1 = min(source.shape[0], max(ys) + margin + 1)
    width, height = x1 - x0, y1 - y0

    mask_image = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask_image)
    for polygon in polygons:
        draw.polygon([(x - x0, y - y0) for x, y in polygon], fill=255)

    inner = np.asarray(bounded_max_filter(mask_image, ring_inner)) > 0
    outer = np.asarray(bounded_max_filter(mask_image, ring_outer)) > 0
    ring = outer & ~inner
    ring_y, ring_x = np.where(ring)
    if len(ring_x) < 32:
        raise SystemExit("not enough unchanged context pixels for color fitting")

    local_source = source[y0:y1, x0:x1]
    local_guide = guide[y0:y1, x0:x1]
    center_x = float(ring_x.mean())
    center_y = float(ring_y.mean())
    scale = float(max(width, height, 1))
    normalized_x = (ring_x - center_x) / scale
    normalized_y = (ring_y - center_y) / scale
    design = np.column_stack(
        [
            np.ones_like(normalized_x),
            normalized_x,
            normalized_y,
            normalized_x * normalized_x,
            normalized_x * normalized_y,
            normalized_y * normalized_y,
        ]
    )

    all_y, all_x = np.indices((height, width))
    fit_x = (all_x - center_x) / scale
    fit_y = (all_y - center_y) / scale
    full_design = np.stack(
        [
            np.ones_like(fit_x),
            fit_x,
            fit_y,
            fit_x * fit_x,
            fit_x * fit_y,
            fit_y * fit_y,
        ],
        axis=-1,
    )

    corrected = local_guide.copy()
    for channel in range(3):
        delta = (
            local_source[ring_y, ring_x, channel]
            - local_guide[ring_y, ring_x, channel]
        )
        low, high = np.percentile(delta, [15, 85])
        keep = (delta >= low) & (delta <= high)
        if int(keep.sum()) < 16:
            keep = np.ones_like(delta, dtype=bool)
        coefficients, *_ = np.linalg.lstsq(design[keep], delta[keep], rcond=None)
        correction = np.tensordot(full_design, coefficients, axes=([-1], [0]))
        corrected[..., channel] += correction

    expanded = bounded_max_filter(mask_image, grow)
    alpha = np.asarray(
        expanded.filter(ImageFilter.GaussianBlur(feather)), dtype=np.float32
    )[..., None] / 255.0
    result = base.copy()
    local_base = result[y0:y1, x0:x1]
    result[y0:y1, x0:x1] = local_base * (1.0 - alpha) + corrected * alpha

    coverage = np.zeros(source.shape[:2], dtype=bool)
    coverage[y0:y1, x0:x1] = alpha[..., 0] > 0
    return np.clip(result, 0, 255), coverage


def maximum_difference(first: np.ndarray, second: np.ndarray) -> int:
    if first.size == 0:
        return 0
    return int(np.abs(first.astype(np.int16) - second.astype(np.int16)).max())


def main() -> None:
    args = build_parser().parse_args()
    source_path = Path(args.source).resolve()
    output_path = Path(args.output).resolve()
    if source_path == output_path:
        raise SystemExit("output must be a separate file; the source is immutable")

    with Image.open(source_path) as image:
        source_image = image.convert("RGB")
    source = np.asarray(source_image, dtype=np.float32)
    width, height = source_image.size
    crop_left, crop_top, crop_right, crop_bottom = args.guide_crop
    if not (
        0 <= crop_left < crop_right <= width
        and 0 <= crop_top < crop_bottom <= height
    ):
        raise SystemExit("guide crop must stay inside the source image")

    with Image.open(args.guide) as image:
        guide_tile = image.convert("RGB")
    crop_size = (crop_right - crop_left, crop_bottom - crop_top)
    if guide_tile.size != crop_size:
        guide_tile = guide_tile.resize(crop_size, Image.Resampling.LANCZOS)
    guide_image = source_image.copy()
    guide_image.paste(guide_tile, (crop_left, crop_top))
    guide = np.asarray(guide_image, dtype=np.float32)

    groups: list[list[Polygon]] = []
    if args.polygon:
        groups.append(args.polygon)
    groups.extend(args.group or [])
    if not groups:
        raise SystemExit("provide at least one --polygon or --group")

    required_margin = max(
        args.ring_outer + 2, args.grow + math.ceil(args.feather * 3)
    )
    result = source.copy()
    allowed = np.zeros(source.shape[:2], dtype=bool)
    for group in groups:
        validate_group_inside_guide(group, args.guide_crop, required_margin)
        result, coverage = composite_group(
            result,
            source,
            guide,
            group,
            args.ring_inner,
            args.ring_outer,
            args.grow,
            args.feather,
        )
        allowed |= coverage

    output_array = result.astype(np.uint8)
    source_array = source.astype(np.uint8)
    changed = np.any(output_array != source_array, axis=2)
    outside_changed = changed & ~allowed
    outside_max_diff = maximum_difference(
        source_array[outside_changed], output_array[outside_changed]
    )
    if outside_max_diff != 0:
        raise SystemExit(f"FAIL pixels changed outside local edit coverage: {outside_max_diff}")

    seam_results: dict[str, int] = {}
    for seam_x in args.seam_x or []:
        left = max(0, seam_x - args.seam_band)
        right = min(width, seam_x + args.seam_band + 1)
        difference = maximum_difference(
            source_array[:, left:right], output_array[:, left:right]
        )
        seam_results[f"x={seam_x}"] = difference
    for seam_y in args.seam_y or []:
        top = max(0, seam_y - args.seam_band)
        bottom = min(height, seam_y + args.seam_band + 1)
        difference = maximum_difference(
            source_array[top:bottom], output_array[top:bottom]
        )
        seam_results[f"y={seam_y}"] = difference
    failed_seams = {name: value for name, value in seam_results.items() if value != 0}
    if failed_seams:
        raise SystemExit(f"FAIL split-line pixels changed: {failed_seams}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output_array).save(output_path)
    if changed.any():
        changed_y, changed_x = np.where(changed)
        changed_bbox: list[int] | None = [
            int(changed_x.min()),
            int(changed_y.min()),
            int(changed_x.max() + 1),
            int(changed_y.max() + 1),
        ]
    else:
        changed_bbox = None
    report = {
        "source": str(source_path),
        "guide": str(Path(args.guide).resolve()),
        "output": str(output_path),
        "size": [width, height],
        "guide_crop": list(args.guide_crop),
        "changed_bbox": changed_bbox,
        "changed_pixels": int(changed.sum()),
        "outside_edit_max_diff": outside_max_diff,
        "split_line_max_diff": seam_results,
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print("PASS " + json.dumps(report, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("guide", help="AI-cleaned owner crop; never pasted as a whole tile")
    parser.add_argument("--guide-crop", required=True, type=parse_box)
    parser.add_argument(
        "--polygon",
        action="append",
        type=parse_polygon,
        help="repeatable polygon in source coordinates; repeated polygons share one fit",
    )
    parser.add_argument(
        "--group",
        action="append",
        type=parse_group,
        help="separate surface group; use polygon|polygon for one shared fit",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--report")
    parser.add_argument("--ring-inner", type=int, default=15)
    parser.add_argument("--ring-outer", type=int, default=48)
    parser.add_argument("--grow", type=int, default=11)
    parser.add_argument("--feather", type=float, default=5.0)
    parser.add_argument("--seam-x", action="append", type=int)
    parser.add_argument("--seam-y", action="append", type=int)
    parser.add_argument("--seam-band", type=int, default=32)
    return parser


if __name__ == "__main__":
    main()
