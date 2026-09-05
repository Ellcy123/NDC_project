#!/usr/bin/env python3
"""Build and verify contour-masked NDC Map sprites from an accepted parent image."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Sequence

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter


Point = tuple[int, int]
EXTREME_NAMES = ("top", "bottom", "left", "right")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_points(value: str) -> list[Point]:
    points: list[Point] = []
    for token in value.split(";"):
        pair = token.strip().split(",")
        if len(pair) != 2:
            raise argparse.ArgumentTypeError(
                "Polygon must use x,y;x,y;... parent-image coordinates"
            )
        try:
            points.append((int(pair[0]), int(pair[1])))
        except ValueError as exc:
            raise argparse.ArgumentTypeError("Polygon coordinates must be integers") from exc
    if len(points) < 3:
        raise argparse.ArgumentTypeError("Polygon needs at least three points")
    return points


def parse_extreme_points(value: str) -> dict[str, Point]:
    result: dict[str, Point] = {}
    for token in value.split(";"):
        name, separator, coordinates = token.strip().partition(":")
        if not separator or name not in EXTREME_NAMES:
            raise argparse.ArgumentTypeError(
                "Extreme points must use top:x,y;bottom:x,y;left:x,y;right:x,y"
            )
        points = parse_points(f"{coordinates};{coordinates};{coordinates}")
        result[name] = points[0]
    if set(result) != set(EXTREME_NAMES):
        raise argparse.ArgumentTypeError(
            "Extreme points must define top, bottom, left, and right exactly once"
        )
    return result


def load_rgba(path: Path) -> Image.Image:
    if path.suffix.lower() != ".png":
        raise ValueError("Parent and Map sprite must be lossless PNG files")
    with Image.open(path) as image:
        return image.convert("RGBA")


def rgb_keys(rgb: np.ndarray) -> np.ndarray:
    """Pack uint8 RGB into one uint32 value for translation registration."""
    rgb32 = rgb.astype(np.uint32)
    return (rgb32[..., 0] << 16) | (rgb32[..., 1] << 8) | rgb32[..., 2]


def locate_alpha_reference(
    parent: Image.Image,
    reference: Image.Image,
    min_similarity: float = 0.9,
    min_uniqueness_margin: float = 0.02,
) -> dict[str, object]:
    """Locate a same-scale RGBA review reference by its Alpha-positive RGB.

    The reference is only a contour authority. Registration can tolerate a
    partially re-exported RGB image, but it must resolve to one confident
    translation inside the accepted parent. The rebuilt sprite always takes
    its visible RGB from the parent.
    """
    if not 0.0 <= min_similarity <= 1.0:
        raise ValueError("Minimum similarity must be between 0 and 1")
    if not 0.0 <= min_uniqueness_margin <= 1.0:
        raise ValueError("Minimum uniqueness margin must be between 0 and 1")
    if reference.width > parent.width or reference.height > parent.height:
        raise ValueError("Reference dimensions exceed the accepted parent")

    parent_array = np.array(parent.convert("RGBA"), dtype=np.uint8)
    reference_array = np.array(reference.convert("RGBA"), dtype=np.uint8)
    alpha = reference_array[:, :, 3]
    selected = np.argwhere(alpha > 0)
    opaque = np.argwhere(alpha == 255)
    registration_pixels = opaque if len(opaque) >= 128 else selected
    if len(registration_pixels) < 16:
        raise ValueError("Reference has too few Alpha-positive pixels for registration")

    parent_key = rgb_keys(parent_array[:, :, :3])
    reference_key = rgb_keys(reference_array[:, :, :3])
    sample_indices = np.linspace(
        0,
        len(registration_pixels) - 1,
        num=min(768, len(registration_pixels)),
        dtype=int,
    )
    samples = registration_pixels[sample_indices]
    sample_y = samples[:, 0]
    sample_x = samples[:, 1]

    probe_indices = np.linspace(
        0, len(samples) - 1, num=min(64, len(samples)), dtype=int
    )
    anchors: list[tuple[int, int, int, int]] = []
    for index in probe_indices:
        ref_y = int(sample_y[index])
        ref_x = int(sample_x[index])
        key = int(reference_key[ref_y, ref_x])
        hit_count = int(np.count_nonzero(parent_key == key))
        if hit_count:
            anchors.append((hit_count, ref_y, ref_x, key))
    if not anchors:
        raise ValueError(
            "No reference RGB anchor occurs in the accepted parent; "
            "use a same-scale lossless review reference"
        )

    _, anchor_y, anchor_x, anchor_key = min(anchors)
    hit_y, hit_x = np.where(parent_key == anchor_key)
    candidates: list[tuple[float, int, int]] = []
    for parent_y, parent_x in zip(hit_y.tolist(), hit_x.tolist()):
        origin_y = parent_y - anchor_y
        origin_x = parent_x - anchor_x
        if (
            origin_x < 0
            or origin_y < 0
            or origin_x + reference.width > parent.width
            or origin_y + reference.height > parent.height
        ):
            continue
        similarity = float(
            np.mean(
                parent_key[origin_y + sample_y, origin_x + sample_x]
                == reference_key[sample_y, sample_x]
            )
        )
        candidates.append((similarity, origin_x, origin_y))
    if not candidates:
        raise ValueError("No legal reference translation fits inside the accepted parent")

    candidates.sort(reverse=True)
    best_similarity, best_x, best_y = candidates[0]
    second_similarity = candidates[1][0] if len(candidates) > 1 else None
    margin = (
        best_similarity - second_similarity if second_similarity is not None else 1.0
    )
    if best_similarity < min_similarity:
        raise ValueError(
            f"Reference registration similarity {best_similarity:.6f} "
            f"is below {min_similarity:.6f}"
        )
    if margin < min_uniqueness_margin:
        raise ValueError(
            f"Reference registration is ambiguous; uniqueness margin {margin:.6f} "
            f"is below {min_uniqueness_margin:.6f}"
        )

    all_y, all_x = selected[:, 0], selected[:, 1]
    full_similarity = float(
        np.mean(
            parent_key[best_y + all_y, best_x + all_x]
            == reference_key[all_y, all_x]
        )
    )
    return {
        "origin": [best_x, best_y],
        "sampleSimilarity": best_similarity,
        "allAlphaPositiveExactRgbRatio": full_similarity,
        "secondBestSampleSimilarity": second_similarity,
        "uniquenessMargin": margin,
        "candidateTranslationsTested": len(candidates),
        "registrationPixelCount": int(len(registration_pixels)),
    }


def rebuild_from_alpha_reference(
    parent: Image.Image,
    reference: Image.Image,
    origin_x: int,
    origin_y: int,
    padding: int = 0,
) -> tuple[Image.Image, tuple[int, int, int, int], Image.Image]:
    """Rebuild a tight sprite using reference Alpha and accepted-parent RGB."""
    if padding < 0:
        raise ValueError("Padding must be non-negative")
    if (
        origin_x < 0
        or origin_y < 0
        or origin_x + reference.width > parent.width
        or origin_y + reference.height > parent.height
    ):
        raise ValueError("Registered reference lies outside the accepted parent")

    reference_array = np.array(reference.convert("RGBA"), dtype=np.uint8)
    parent_crop = np.array(
        parent.crop(
            (
                origin_x,
                origin_y,
                origin_x + reference.width,
                origin_y + reference.height,
            )
        ).convert("RGBA"),
        dtype=np.uint8,
    )
    reference_alpha = reference_array[:, :, 3].astype(np.uint16)
    parent_alpha = parent_crop[:, :, 3].astype(np.uint16)
    combined_alpha = ((reference_alpha * parent_alpha) // 255).astype(np.uint8)
    alpha_image = Image.fromarray(combined_alpha, "L")
    alpha_bbox = alpha_image.getbbox()
    if alpha_bbox is None:
        raise ValueError("Reference Alpha produces an empty hotspot")
    local_bbox = expand_bbox(alpha_bbox, padding, reference.size)
    left, top, right, bottom = local_bbox
    output_array = parent_crop[top:bottom, left:right].copy()
    output_alpha = combined_alpha[top:bottom, left:right]
    output_array[:, :, 3] = output_alpha
    output_array[output_alpha == 0, :3] = 0
    parent_bbox = (
        origin_x + left,
        origin_y + top,
        origin_x + right,
        origin_y + bottom,
    )
    return Image.fromarray(output_array, "RGBA"), parent_bbox, alpha_image


def polygon_mask(size: tuple[int, int], points: Sequence[Point]) -> Image.Image:
    return polygon_union_mask(size, [points])


def polygon_union_mask(
    size: tuple[int, int], polygons: Sequence[Sequence[Point]]
) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        if any(
            x < 0 or y < 0 or x >= width or y >= height
            for x, y in polygon
        ):
            raise ValueError("Polygon point lies outside the parent image")
        draw.polygon(polygon, fill=255)
    return mask


def expand_mask(mask: Image.Image, pixels: int) -> Image.Image:
    if pixels < 0:
        raise ValueError("Contour expansion must be non-negative")
    if pixels == 0:
        return mask.copy()
    return mask.filter(ImageFilter.MaxFilter(2 * pixels + 1))


def exclusion_mask(
    size: tuple[int, int], polygons: Sequence[Sequence[Point]]
) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        if any(
            x < 0 or y < 0 or x >= size[0] or y >= size[1]
            for x, y in polygon
        ):
            raise ValueError("Exclusion polygon point lies outside the parent image")
        draw.polygon(polygon, fill=255)
    return mask


def apply_exclusions(mask: Image.Image, exclusions: Image.Image | None) -> Image.Image:
    if exclusions is None:
        return mask.copy()
    if exclusions.size != mask.size:
        raise ValueError("Exclusion mask and contour mask dimensions differ")
    return ImageChops.multiply(mask, ImageChops.invert(exclusions))


def expand_bbox(
    bbox: tuple[int, int, int, int], padding: int, size: tuple[int, int]
) -> tuple[int, int, int, int]:
    if padding < 0:
        raise ValueError("Padding must be non-negative")
    left, top, right, bottom = bbox
    width, height = size
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(width, right + padding),
        min(height, bottom + padding),
    )


def build_sprite(
    parent: Image.Image,
    points: Sequence[Point],
    padding: int,
    expand: int = 0,
    exclude_polygons: Sequence[Sequence[Point]] = (),
    shadow_polygons: Sequence[Sequence[Point]] = (),
) -> tuple[Image.Image, tuple[int, int, int, int], Image.Image]:
    base_mask = polygon_union_mask(parent.size, [points, *shadow_polygons])
    expanded = expand_mask(base_mask, expand)
    exclusions = (
        exclusion_mask(parent.size, exclude_polygons) if exclude_polygons else None
    )
    mask = apply_exclusions(expanded, exclusions)
    raw_bbox = mask.getbbox()
    if raw_bbox is None:
        raise ValueError("Polygon produced an empty mask")
    bbox = expand_bbox(raw_bbox, padding, parent.size)
    parent_crop = np.array(parent.crop(bbox), dtype=np.uint8)
    mask_crop = np.array(mask.crop(bbox), dtype=np.uint8)
    source_alpha = parent_crop[:, :, 3].astype(np.uint16)
    combined_alpha = ((source_alpha * mask_crop.astype(np.uint16)) // 255).astype(
        np.uint8
    )
    parent_crop[:, :, 3] = combined_alpha
    parent_crop[combined_alpha == 0, :3] = 0
    return Image.fromarray(parent_crop, "RGBA"), bbox, mask


def verify_expansion(
    base_mask: Image.Image, expanded_mask: Image.Image, pixels: int
) -> dict[str, object]:
    base_bbox = base_mask.getbbox()
    expanded_bbox = expanded_mask.getbbox()
    if base_bbox is None or expanded_bbox is None:
        return {"passed": False, "reason": "empty-mask"}
    width, height = base_mask.size
    expected_bbox = (
        max(0, base_bbox[0] - pixels),
        max(0, base_bbox[1] - pixels),
        min(width, base_bbox[2] + pixels),
        min(height, base_bbox[3] + pixels),
    )
    missing_base = ImageChops.multiply(
        base_mask, ImageChops.invert(expanded_mask)
    ).getbbox()
    return {
        "pixels": pixels,
        "baseBounds": list(base_bbox),
        "expectedExpandedBounds": list(expected_bbox),
        "actualExpandedBounds": list(expanded_bbox),
        "expandedMaskContainsBaseMask": missing_base is None,
        "boundsExpandedByRequestedPixels": expanded_bbox == expected_bbox,
        "passed": bool(missing_base is None and expanded_bbox == expected_bbox),
    }


def verify_exclusions(
    expanded_mask: Image.Image,
    final_mask: Image.Image,
    exclusions: Image.Image | None,
) -> dict[str, object]:
    if exclusions is None:
        unchanged = ImageChops.difference(expanded_mask, final_mask).getbbox() is None
        return {
            "provided": False,
            "excludedPixelCount": 0,
            "finalMaskEqualsExpandedMask": unchanged,
            "passed": unchanged,
        }
    overlap = ImageChops.multiply(final_mask, exclusions)
    removed = ImageChops.subtract(expanded_mask, final_mask)
    removed_count = int(np.count_nonzero(np.array(removed, dtype=np.uint8)))
    return {
        "provided": True,
        "excludedPixelCount": removed_count,
        "finalMaskHasNoForegroundOccluderOverlap": overlap.getbbox() is None,
        "removedAtLeastOneExpandedPixel": removed_count > 0,
        "passed": bool(overlap.getbbox() is None and removed_count > 0),
    }


def verify_sprite(
    parent: Image.Image, sprite: Image.Image, x: int, y: int
) -> dict[str, object]:
    inside_parent = (
        x >= 0
        and y >= 0
        and x + sprite.width <= parent.width
        and y + sprite.height <= parent.height
    )
    if not inside_parent:
        return {
            "insideParent": False,
            "nonEmptyAlpha": False,
            "transparentRgbZero": False,
            "visiblePixelsMatchParent": False,
            "passed": False,
        }

    sprite_array = np.array(sprite.convert("RGBA"), dtype=np.uint8)
    parent_array = np.array(
        parent.crop((x, y, x + sprite.width, y + sprite.height)).convert("RGBA"),
        dtype=np.uint8,
    )
    alpha = sprite_array[:, :, 3]
    visible = alpha > 0
    transparent = ~visible
    non_empty = bool(np.any(visible))
    transparent_rgb_zero = bool(np.all(sprite_array[transparent, :3] == 0))
    visible_match = bool(
        non_empty and np.all(sprite_array[visible, :3] == parent_array[visible, :3])
    )
    alpha_not_above_parent = bool(
        np.all(sprite_array[:, :, 3] <= parent_array[:, :, 3])
    )
    passed = bool(
        inside_parent
        and non_empty
        and transparent_rgb_zero
        and visible_match
        and alpha_not_above_parent
    )
    return {
        "insideParent": inside_parent,
        "nonEmptyAlpha": non_empty,
        "transparentRgbZero": transparent_rgb_zero,
        "visiblePixelsMatchParent": visible_match,
        "spriteAlphaDoesNotExceedParentAlpha": alpha_not_above_parent,
        "opaqueOrVisiblePixelCount": int(np.count_nonzero(visible)),
        "canvasPixelCount": int(alpha.size),
        "contourCoverageRatio": round(float(np.count_nonzero(visible) / alpha.size), 6),
        "excludedCanvasRatio": round(float(np.count_nonzero(transparent) / alpha.size), 6),
        "passed": passed,
    }


def verify_extreme_points(
    mask: Image.Image, extreme_points: dict[str, Point]
) -> dict[str, object]:
    width, height = mask.size
    point_checks: dict[str, object] = {}
    all_inside = True
    all_selected = True
    for name in EXTREME_NAMES:
        x, y = extreme_points[name]
        inside = 0 <= x < width and 0 <= y < height
        selected = bool(inside and mask.getpixel((x, y)) > 0)
        point_checks[name] = {
            "point": [x, y],
            "insideParent": inside,
            "selectedByContour": selected,
        }
        all_inside = all_inside and inside
        all_selected = all_selected and selected
    bbox = mask.getbbox()
    if bbox is None:
        bounds_cover = False
    else:
        bounds_cover = bool(
            bbox[1] <= extreme_points["top"][1]
            and bbox[3] > extreme_points["bottom"][1]
            and bbox[0] <= extreme_points["left"][0]
            and bbox[2] > extreme_points["right"][0]
        )
    return {
        "points": point_checks,
        "maskBounds": list(bbox) if bbox else None,
        "allPointsInsideParent": all_inside,
        "allFourExtremaSelectedByContour": all_selected,
        "maskBoundsCoverAllFourExtrema": bounds_cover,
        "passed": bool(all_inside and all_selected and bounds_cover),
    }


def connected_component_bounds(mask: Image.Image) -> list[dict[str, object]]:
    visible = np.array(mask, dtype=np.uint8) > 0
    height, width = visible.shape
    visited = np.zeros_like(visible, dtype=bool)
    components: list[dict[str, object]] = []
    for start_y, start_x in np.argwhere(visible):
        y = int(start_y)
        x = int(start_x)
        if visited[y, x]:
            continue
        queue: deque[Point] = deque([(x, y)])
        visited[y, x] = True
        left = right = x
        top = bottom = y
        count = 0
        while queue:
            current_x, current_y = queue.popleft()
            count += 1
            left = min(left, current_x)
            right = max(right, current_x)
            top = min(top, current_y)
            bottom = max(bottom, current_y)
            for next_x, next_y in (
                (current_x - 1, current_y),
                (current_x + 1, current_y),
                (current_x, current_y - 1),
                (current_x, current_y + 1),
            ):
                if (
                    0 <= next_x < width
                    and 0 <= next_y < height
                    and visible[next_y, next_x]
                    and not visited[next_y, next_x]
                ):
                    visited[next_y, next_x] = True
                    queue.append((next_x, next_y))
        components.append(
            {
                "visiblePixelCount": count,
                "bounds": [left, top, right + 1, bottom + 1],
            }
        )
    return sorted(
        components,
        key=lambda component: int(component["visiblePixelCount"]),
        reverse=True,
    )


def save_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def draw_overlay(
    parent: Image.Image,
    points: Sequence[Point],
    bbox: tuple[int, int, int, int],
    output: Path,
    extreme_points: dict[str, Point] | None = None,
    expanded_mask: Image.Image | None = None,
    exclusions: Image.Image | None = None,
    shadow_polygons: Sequence[Sequence[Point]] = (),
) -> None:
    overlay = parent.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    closed = list(points) + [points[0]]
    draw.line(closed, fill=(255, 40, 40, 255), width=3, joint="curve")
    for polygon in shadow_polygons:
        shadow_closed = list(polygon) + [polygon[0]]
        draw.line(
            shadow_closed,
            fill=(40, 160, 255, 255),
            width=3,
            joint="curve",
        )
    draw.rectangle(bbox, outline=(0, 255, 255, 255), width=2)
    if expanded_mask is not None:
        eroded = expanded_mask.filter(ImageFilter.MinFilter(3))
        edge = ImageChops.subtract(expanded_mask, eroded)
        edge_layer = Image.new("RGBA", parent.size, (255, 140, 0, 0))
        edge_layer.putalpha(edge)
        overlay.alpha_composite(edge_layer)
    if exclusions is not None:
        exclusion_edge = ImageChops.subtract(
            exclusions, exclusions.filter(ImageFilter.MinFilter(3))
        )
        exclusion_layer = Image.new("RGBA", parent.size, (160, 32, 240, 0))
        exclusion_layer.putalpha(exclusion_edge)
        overlay.alpha_composite(exclusion_layer)
    if extreme_points:
        colors = {
            "top": (255, 255, 0, 255),
            "bottom": (255, 0, 255, 255),
            "left": (0, 255, 0, 255),
            "right": (0, 128, 255, 255),
        }
        for name in EXTREME_NAMES:
            x, y = extreme_points[name]
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=colors[name])
            draw.text((x + 6, y - 6), name, fill=colors[name])
    output.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output)


def command_build(args: argparse.Namespace) -> int:
    parent_path = args.parent.resolve()
    output_path = args.output.resolve()
    parent = load_rgba(parent_path)
    points = parse_points(args.polygon)
    shadow_polygons = [parse_points(value) for value in args.shadow_polygon]
    exclude_polygons = [parse_points(value) for value in args.exclude_polygon]
    extreme_points = parse_extreme_points(args.extreme_points) if args.extreme_points else None
    base_mask = polygon_union_mask(parent.size, [points, *shadow_polygons])
    expanded_mask = expand_mask(base_mask, args.expand)
    exclusions = (
        exclusion_mask(parent.size, exclude_polygons) if exclude_polygons else None
    )
    sprite, bbox, mask = build_sprite(
        parent,
        points,
        args.padding,
        args.expand,
        exclude_polygons,
        shadow_polygons,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sprite.save(output_path)
    saved = load_rgba(output_path)
    checks = verify_sprite(parent, saved, bbox[0], bbox[1])
    extrema_checks = (
        verify_extreme_points(base_mask, extreme_points) if extreme_points else None
    )
    final_extrema_checks = (
        verify_extreme_points(mask, extreme_points) if extreme_points else None
    )
    expansion_checks = verify_expansion(base_mask, expanded_mask, args.expand)
    exclusion_checks = verify_exclusions(expanded_mask, mask, exclusions)
    passed = bool(
        checks["passed"]
        and expansion_checks["passed"]
        and exclusion_checks["passed"]
        and (extrema_checks is None or extrema_checks["passed"])
        and (final_extrema_checks is None or final_extrema_checks["passed"])
    )
    report = {
        "version": 1,
        "kind": "ndc-irregular-map",
        "parent": {
            "path": str(parent_path),
            "sha256": sha256(parent_path),
            "size": list(parent.size),
        },
        "sprite": {
            "path": str(output_path),
            "sha256": sha256(output_path),
            "mode": saved.mode,
            "size": list(saved.size),
            "parentLocalPosition": [bbox[0], bbox[1]],
            "parentLocalRect": list(bbox),
        },
        "bodyPolygonParentCoordinates": [list(point) for point in points],
        "polygonParentCoordinates": [list(point) for point in points],
        "shadowPolygonsParentCoordinates": [
            [list(point) for point in polygon] for polygon in shadow_polygons
        ],
        "declaredExtremePoints": (
            {name: list(extreme_points[name]) for name in EXTREME_NAMES}
            if extreme_points
            else None
        ),
        "padding": args.padding,
        "contourExpansionPixels": args.expand,
        "expansionPolicy": {
            "productionDefaultPixels": [2, 3],
            "completeBaseContourRequired": True,
            "fivePixelTrialRequiresAssetSpecificVisualEvidence": args.expand == 5,
            "zeroExpansionRequiresAuthoredFinalContour": args.expand == 0,
            "nonDefaultExpansionApprovalRequired": args.expand not in (2, 3),
            "technicalReportDoesNotApproveVisualCompleteness": True,
        },
        "multiIslandPolicy": {
            "allowed": True,
            "keepVisibleShadowBeyondForegroundOccluders": True,
            "largestComponentOnlyIsForbidden": True,
            "finalConnectedComponentCount": len(connected_component_bounds(mask)),
            "finalConnectedComponents": connected_component_bounds(mask),
        },
        "foregroundOccluderExclusionPolygons": [
            [list(point) for point in polygon] for polygon in exclude_polygons
        ],
        "checks": checks,
        "extremePointGate": extrema_checks,
        "finalPostExclusionExtremePointGate": final_extrema_checks,
        "expansionGate": expansion_checks,
        "foregroundOccluderExclusionGate": exclusion_checks,
        "passed": passed,
    }
    if args.overlay:
        overlay_path = args.overlay.resolve()
        draw_overlay(
            parent,
            points,
            bbox,
            overlay_path,
            extreme_points,
            expanded_mask,
            exclusions,
            shadow_polygons,
        )
        report["overlay"] = {
            "path": str(overlay_path),
            "sha256": sha256(overlay_path),
        }
    report_path = args.report.resolve() if args.report else output_path.with_suffix(".verification.json")
    save_json(report_path, report)
    print(f"Irregular Map: {'PASS' if passed else 'FAIL'}")
    print(f"Parent-local Position: {bbox[0]},{bbox[1]}")
    print(f"Sprite: {saved.width} x {saved.height}; contour coverage: {checks['contourCoverageRatio']}")
    print(f"Report: {report_path}")
    return 0 if passed else 2


def command_verify(args: argparse.Namespace) -> int:
    parent_path = args.parent.resolve()
    sprite_path = args.sprite.resolve()
    parent = load_rgba(parent_path)
    sprite = load_rgba(sprite_path)
    checks = verify_sprite(parent, sprite, args.x, args.y)
    report = {
        "version": 1,
        "kind": "ndc-irregular-map-verification",
        "parent": {"path": str(parent_path), "sha256": sha256(parent_path)},
        "sprite": {"path": str(sprite_path), "sha256": sha256(sprite_path)},
        "parentLocalPosition": [args.x, args.y],
        "checks": checks,
        "passed": checks["passed"],
    }
    if args.report:
        save_json(args.report.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if checks["passed"] else 2


def command_rebuild_reference(args: argparse.Namespace) -> int:
    parent_path = args.parent.resolve()
    reference_path = args.reference.resolve()
    output_path = args.output.resolve()
    parent = load_rgba(parent_path)
    reference = load_rgba(reference_path)
    registration = locate_alpha_reference(
        parent,
        reference,
        min_similarity=args.min_similarity,
        min_uniqueness_margin=args.min_uniqueness_margin,
    )
    origin_x, origin_y = registration["origin"]
    sprite, bbox, reference_alpha = rebuild_from_alpha_reference(
        parent,
        reference,
        int(origin_x),
        int(origin_y),
        padding=args.padding,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sprite.save(output_path)
    saved = load_rgba(output_path)
    checks = verify_sprite(parent, saved, bbox[0], bbox[1])
    components = connected_component_bounds(saved.getchannel("A"))
    passed = bool(checks["passed"])
    report = {
        "version": 1,
        "kind": "ndc-irregular-map-alpha-reference-rebuild",
        "parent": {
            "path": str(parent_path),
            "sha256": sha256(parent_path),
            "size": list(parent.size),
        },
        "reference": {
            "path": str(reference_path),
            "sha256": sha256(reference_path),
            "size": list(reference.size),
            "usage": "final-post-exclusion Alpha authority only",
        },
        "registration": registration,
        "sprite": {
            "path": str(output_path),
            "sha256": sha256(output_path),
            "mode": saved.mode,
            "size": list(saved.size),
            "parentLocalPosition": [bbox[0], bbox[1]],
            "parentLocalRect": list(bbox),
        },
        "alphaReferencePolicy": {
            "visibleRgbRebuiltFromAcceptedParent": True,
            "transparentRgbZeroRequired": True,
            "referenceMustAlreadyContainReviewedFivePixelExpansion": True,
            "secondExpansionApplied": False,
            "referenceDoesNotWaiveVisualGates": True,
        },
        "referenceAlphaBounds": list(reference_alpha.getbbox() or ()),
        "multiIslandPolicy": {
            "allowed": True,
            "largestComponentOnlyIsForbidden": True,
            "finalConnectedComponentCount": len(components),
            "finalConnectedComponents": components,
        },
        "checks": checks,
        "visualGate": "NOT_CHECKED_BY_SCRIPT",
        "technicalPassed": passed,
        "passed": passed,
    }
    report_path = (
        args.report.resolve()
        if args.report
        else output_path.with_suffix(".verification.json")
    )
    save_json(report_path, report)
    print(f"Alpha-reference Map rebuild: {'PASS' if passed else 'FAIL'}")
    print(f"Parent-local Position: {bbox[0]},{bbox[1]}")
    print(f"Sprite: {saved.width} x {saved.height}; components: {len(components)}")
    print(f"Report: {report_path}")
    return 0 if passed else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="Build a tight RGBA Map from a parent-space polygon")
    build.add_argument("--parent", type=Path, required=True)
    build.add_argument("--polygon", required=True, help="x,y;x,y;... in parent-image coordinates")
    build.add_argument(
        "--shadow-polygon",
        action="append",
        default=[],
        help=(
            "Repeatable visible target-shadow polygon unioned with the body; "
            "disconnected shadow islands are allowed"
        ),
    )
    build.add_argument(
        "--extreme-points",
        help="Required production gate: top:x,y;bottom:x,y;left:x,y;right:x,y",
    )
    build.add_argument("--padding", type=int, default=1)
    build.add_argument(
        "--expand",
        type=int,
        choices=(0, 2, 3, 5),
        default=3,
        help=(
            "Outward contour expansion in Photoshop pixels; ordinary range 2-3 (default 3). "
            "Use 5 only for an asset-specific visually reviewed trial, or 0 for an authored "
            "final contour. A complete body-plus-shadow base contour is required first."
        ),
    )
    build.add_argument(
        "--exclude-polygon",
        action="append",
        default=[],
        help="Repeatable parent-space polygon removed after expansion for foreground occluders",
    )
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--report", type=Path)
    build.add_argument("--overlay", type=Path)
    build.set_defaults(func=command_build)

    verify = commands.add_parser("verify", help="Verify a Map against its accepted parent pixels")
    verify.add_argument("--parent", type=Path, required=True)
    verify.add_argument("--sprite", type=Path, required=True)
    verify.add_argument("--x", type=int, required=True)
    verify.add_argument("--y", type=int, required=True)
    verify.add_argument("--report", type=Path)
    verify.set_defaults(func=command_verify)

    rebuild_reference = commands.add_parser(
        "rebuild-reference",
        help=(
            "Locate a same-scale reviewed RGBA reference, reuse only its Alpha, "
            "and rebuild visible RGB from the accepted parent"
        ),
    )
    rebuild_reference.add_argument("--parent", type=Path, required=True)
    rebuild_reference.add_argument("--reference", type=Path, required=True)
    rebuild_reference.add_argument("--output", type=Path, required=True)
    rebuild_reference.add_argument("--report", type=Path)
    rebuild_reference.add_argument("--padding", type=int, default=0)
    rebuild_reference.add_argument("--min-similarity", type=float, default=0.9)
    rebuild_reference.add_argument(
        "--min-uniqueness-margin", type=float, default=0.02
    )
    rebuild_reference.set_defaults(func=command_rebuild_reference)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
