#!/usr/bin/env python3
"""Prepare, compose, and verify coordinate-locked raster edit jobs.

The image model edits a padded crop. This helper owns all geometry and proves
that pixels outside the approved hard mask remain byte-identical to the source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


MANIFEST_NAME = "manifest.json"
CROP_NAME = "source_crop.png"
HARD_MASK_NAME = "hard_mask.png"
BLEND_MASK_NAME = "blend_mask.png"
GENERATED_NAME = "generated.png"
REGISTERED_NAME = "registered.png"
DIFF_NAME = "difference_preview.png"
SEAM_REPORT_NAME = "seam_report.json"
SEAM_OVERLAY_NAME = "seam_overlay.png"
BOUNDARY_REPORT_NAME = "boundary_report.json"
BOUNDARY_OVERLAY_NAME = "boundary_overlay.png"
FINAL_REPORT_NAME = "final_verification.json"
FINAL_DIFF_NAME = "final_difference_preview.png"
DEFAULT_OUTPUT_SUFFIX = "_coordinate_edit.png"

GENERATION_MIN_PIXELS = 655_360
GENERATION_MAX_PIXELS = 8_294_400
GENERATION_MAX_EDGE = 3_840
GENERATION_MAX_ASPECT = 3.0


Rect = tuple[int, int, int, int]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def as_rect(values: Iterable[int]) -> Rect:
    left, first_y, right, second_y = (int(value) for value in values)
    return left, first_y, right, second_y


def validate_rect(rect: Rect, width: int, height: int, label: str) -> None:
    left, top, right, bottom = rect
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(
            f"{label} {rect} is outside the {width}x{height} image or is empty"
        )


def convert_rect(rect: Rect, origin: str, image_height: int) -> Rect:
    if origin == "top-left":
        return rect
    left, bottom, right, top = rect
    return left, image_height - top, right, image_height - bottom


def relative_rect(inner: Rect, outer: Rect) -> Rect:
    return (
        inner[0] - outer[0],
        inner[1] - outer[1],
        inner[2] - outer[0],
        inner[3] - outer[1],
    )


def expand_rect(rect: Rect, padding: int, width: int, height: int) -> Rect:
    left, top, right, bottom = rect
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(width, right + padding),
        min(height, bottom + padding),
    )


def contains(outer: Rect, inner: Rect) -> bool:
    return (
        outer[0] <= inner[0]
        and outer[1] <= inner[1]
        and outer[2] >= inner[2]
        and outer[3] >= inner[3]
    )


def validate_generation_canvas(size: tuple[int, int]) -> None:
    width, height = size
    errors: list[str] = []
    if width % 16 or height % 16:
        errors.append("both edges must be multiples of 16")
    if max(width, height) > GENERATION_MAX_EDGE:
        errors.append(f"neither edge may exceed {GENERATION_MAX_EDGE}px")
    if max(width, height) / min(width, height) > GENERATION_MAX_ASPECT:
        errors.append(f"long-to-short ratio may not exceed {GENERATION_MAX_ASPECT}:1")
    pixels = width * height
    if not GENERATION_MIN_PIXELS <= pixels <= GENERATION_MAX_PIXELS:
        errors.append(
            f"total pixels must be between {GENERATION_MIN_PIXELS:,} and "
            f"{GENERATION_MAX_PIXELS:,}"
        )
    if errors:
        raise ValueError(
            f"Illegal generation canvas {width}x{height}: " + "; ".join(errors)
        )


def source_mode(image: Image.Image) -> str:
    return "RGBA" if "A" in image.getbands() else "RGB"


def load_source(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert(source_mode(image))


def load_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def build_rect_mask(size: tuple[int, int], rect: Rect) -> Image.Image:
    left, top, right, bottom = rect
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((left, top, right - 1, bottom - 1), fill=255)
    return mask


def expand_authorization_mask(args: argparse.Namespace) -> Path:
    """Expand a tight intent mask into a generous rectangular authoring workspace."""
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    if input_path == output_path:
        raise ValueError("--output must differ from --input")
    if args.scale < 1:
        raise ValueError("--scale must be at least 1")
    if args.min_margin < 0:
        raise ValueError("--min-margin must be non-negative")
    if output_path.exists() and not args.force:
        raise FileExistsError(f"Output already exists: {output_path}")

    with Image.open(input_path) as image:
        intent = image.convert("L")
    canvas_size = tuple(args.canvas_size) if args.canvas_size else intent.size
    if canvas_size[0] <= 0 or canvas_size[1] <= 0:
        raise ValueError("--canvas-size edges must be positive")
    offset_x, offset_y = args.offset
    if not (
        0 <= offset_x
        and 0 <= offset_y
        and offset_x + intent.width <= canvas_size[0]
        and offset_y + intent.height <= canvas_size[1]
    ):
        raise ValueError("Input mask plus --offset does not fit inside --canvas-size")

    intent_canvas = Image.new("L", canvas_size, 0)
    intent_canvas.paste(intent, (offset_x, offset_y))
    intent_array = np.asarray(intent_canvas, dtype=np.uint8) >= 128
    intent_canvas = Image.fromarray((intent_array * 255).astype(np.uint8), "L")
    bbox = intent_canvas.getbbox()
    if bbox is None:
        raise ValueError("Input intent mask is empty")

    limit_rect = as_rect(args.limit_rect) if args.limit_rect else (0, 0, *canvas_size)
    validate_rect(limit_rect, canvas_size[0], canvas_size[1], "Limit rectangle")
    if not contains(limit_rect, bbox):
        raise ValueError("Intent mask lies outside --limit-rect")

    intent_width = bbox[2] - bbox[0]
    intent_height = bbox[3] - bbox[1]
    target_width = max(
        math.ceil(intent_width * args.scale), intent_width + 2 * args.min_margin
    )
    target_height = max(
        math.ceil(intent_height * args.scale), intent_height + 2 * args.min_margin
    )
    limit_width = limit_rect[2] - limit_rect[0]
    limit_height = limit_rect[3] - limit_rect[1]
    if target_width > limit_width or target_height > limit_height:
        raise ValueError(
            "Required authorization workspace does not fit inside --limit-rect; "
            "enlarge the legal region, shrink/relocate the object, or explicitly revise the rule"
        )

    def choose_start(
        inner_start: int,
        inner_end: int,
        target_size: int,
        limit_start: int,
        limit_end: int,
    ) -> int:
        lowest = max(limit_start, inner_end + args.min_margin - target_size)
        highest = min(inner_start - args.min_margin, limit_end - target_size)
        if lowest > highest:
            raise ValueError(
                "Required per-side authorization margin does not fit inside --limit-rect"
            )
        centered = round((inner_start + inner_end - target_size) / 2)
        return max(lowest, min(centered, highest))

    left = choose_start(bbox[0], bbox[2], target_width, limit_rect[0], limit_rect[2])
    top = choose_start(bbox[1], bbox[3], target_height, limit_rect[1], limit_rect[3])
    authorization_rect = (left, top, left + target_width, top + target_height)
    margins = {
        "left": bbox[0] - authorization_rect[0],
        "top": bbox[1] - authorization_rect[1],
        "right": authorization_rect[2] - bbox[2],
        "bottom": authorization_rect[3] - bbox[3],
    }
    if min(margins.values()) < args.min_margin:
        raise AssertionError("Authorization expansion failed the requested side margin")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    authorization = build_rect_mask(canvas_size, authorization_rect)
    authorization.save(output_path)

    report_path = args.report.resolve() if args.report else output_path.with_suffix(".json")
    if report_path.exists() and not args.force:
        output_path.unlink(missing_ok=True)
        raise FileExistsError(f"Report already exists: {report_path}")
    report = {
        "version": 1,
        "input": str(input_path),
        "inputSha256": sha256(input_path),
        "inputSize": list(intent.size),
        "canvasSize": list(canvas_size),
        "offset": [offset_x, offset_y],
        "intentBounds": list(bbox),
        "intentSize": [intent_width, intent_height],
        "scale": args.scale,
        "minimumSideMargin": args.min_margin,
        "limitRect": list(limit_rect),
        "authorizationRect": list(authorization_rect),
        "authorizationSize": [target_width, target_height],
        "actualSideMargins": margins,
        "output": str(output_path),
        "outputSha256": sha256(output_path),
        "passed": True,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(report_path, report)
    print("Authorization mask expansion: PASS")
    print(f"Intent bounds: {bbox}; size: {intent_width} x {intent_height}")
    print(
        f"Authorization bounds: {authorization_rect}; "
        f"size: {target_width} x {target_height}"
    )
    print(f"Side margins: {margins}")
    print(f"Mask: {output_path}")
    print(f"Report: {report_path}")
    return output_path


def load_authorization_mask(
    mask_path: Path | None,
    source_size: tuple[int, int],
    crop_rect: Rect,
    crop_size: tuple[int, int],
    edit_relative: Rect,
) -> Image.Image:
    edit_limit = np.asarray(build_rect_mask(crop_size, edit_relative), dtype=np.uint8) > 0
    if mask_path is None:
        return Image.fromarray((edit_limit * 255).astype(np.uint8), "L")

    with Image.open(mask_path) as image:
        supplied = image.convert("L")
    if supplied.size == source_size:
        supplied = supplied.crop(crop_rect)
    elif supplied.size != crop_size:
        raise ValueError(
            "Authorization mask must match either the source dimensions or the context crop"
        )

    supplied_array = np.asarray(supplied, dtype=np.uint8) >= 128
    if np.any(supplied_array & ~edit_limit):
        raise ValueError("Authorization mask contains enabled pixels outside --edit-rect")
    if not np.any(supplied_array):
        raise ValueError("Authorization mask is empty")
    return Image.fromarray((supplied_array * 255).astype(np.uint8), "L")


def build_blend_mask(hard_mask: Image.Image, feather: int) -> Image.Image:
    hard_array = np.asarray(hard_mask.convert("L"), dtype=np.uint8)
    if feather <= 0:
        return Image.fromarray(hard_array, "L")
    blurred = hard_mask.filter(ImageFilter.GaussianBlur(radius=feather))
    blurred_array = np.asarray(blurred, dtype=np.uint8)
    clipped = np.where(hard_array > 0, blurred_array, 0).astype(np.uint8)
    return Image.fromarray(clipped, "L")


def prepare(args: argparse.Namespace) -> Path:
    source = args.source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if args.padding < 0:
        raise ValueError("--padding must be non-negative")
    if args.feather < 0:
        raise ValueError("--feather must be non-negative")

    original = load_source(source)
    width, height = original.size
    edit_input = as_rect(args.edit_rect)
    edit_rect = convert_rect(edit_input, args.origin, height)
    validate_rect(edit_rect, width, height, "Edit rectangle")

    if args.crop_rect is None:
        crop_rect = expand_rect(edit_rect, args.padding, width, height)
        crop_input: Rect | None = None
    else:
        crop_input = as_rect(args.crop_rect)
        crop_rect = convert_rect(crop_input, args.origin, height)
        validate_rect(crop_rect, width, height, "Crop rectangle")
    if not contains(crop_rect, edit_rect):
        raise ValueError("Context crop must fully contain the edit rectangle")
    if args.canvas_kind == "generation":
        validate_generation_canvas((crop_rect[2] - crop_rect[0], crop_rect[3] - crop_rect[1]))

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / MANIFEST_NAME
    if manifest_path.exists() and not args.force:
        raise FileExistsError(
            f"{manifest_path} already exists; use a new job directory or pass --force"
        )

    crop = original.crop(crop_rect)
    crop_path = out_dir / CROP_NAME
    crop.save(crop_path)

    edit_relative = relative_rect(edit_rect, crop_rect)
    hard_mask = load_authorization_mask(
        args.mask.resolve() if args.mask else None,
        original.size,
        crop_rect,
        crop.size,
        edit_relative,
    )
    blend_mask = build_blend_mask(hard_mask, args.feather)
    hard_mask_path = out_dir / HARD_MASK_NAME
    blend_mask_path = out_dir / BLEND_MASK_NAME
    hard_mask.save(hard_mask_path)
    blend_mask.save(blend_mask_path)

    manifest: dict[str, Any] = {
        "version": 1,
        "stage": "prepared",
        "source": str(source),
        "source_sha256": sha256(source),
        "source_size": [width, height],
        "source_mode": original.mode,
        "coordinate_origin_input": args.origin,
        "edit_rect_input": list(edit_input),
        "crop_rect_input": list(crop_input) if crop_input else None,
        "edit_rect_top_left": list(edit_rect),
        "crop_rect_top_left": list(crop_rect),
        "edit_rect_in_crop": list(edit_relative),
        "crop_size": list(crop.size),
        "padding": args.padding,
        "feather": args.feather,
        "canvas_kind": args.canvas_kind,
        "authorization_mask_source": str(args.mask.resolve()) if args.mask else None,
        "files": {
            "source_crop": str(crop_path),
            "hard_mask": str(hard_mask_path),
            "blend_mask": str(blend_mask_path),
            "generated": str(out_dir / GENERATED_NAME),
            "registered": str(out_dir / REGISTERED_NAME),
            "difference_preview": str(out_dir / DIFF_NAME),
        },
        "artifact_sha256": {
            "source_crop": sha256(crop_path),
            "hard_mask": sha256(hard_mask_path),
            "blend_mask": sha256(blend_mask_path),
        },
    }
    save_json(manifest_path, manifest)
    print(f"Stage: prepared")
    print(f"Source: {source}")
    print(f"Source size: {width} x {height}")
    print(f"Edit rectangle (top-left): {edit_rect}")
    print(f"Context crop (top-left): {crop_rect}")
    print(f"Crop: {crop_path}")
    print(f"Hard mask: {hard_mask_path}")
    print(f"Manifest: {manifest_path}")
    return manifest_path


def normalize_to_canvas(image: Image.Image, target_size: tuple[int, int]) -> tuple[Image.Image, list[int]]:
    image = image.convert("RGB")
    source_width, source_height = image.size
    target_width, target_height = target_size
    if source_width * target_height != target_width * source_height:
        raise ValueError(
            "AI patch aspect ratio differs from the prepared crop; refusing to "
            "stretch or center-crop it"
        )
    box = [0, 0, source_width, source_height]
    if image.size == target_size:
        return image, box
    return image.resize(target_size, Image.Resampling.LANCZOS), box


def scaled_center(
    image: Image.Image, scale: float, canvas_size: tuple[int, int]
) -> tuple[Image.Image, Image.Image]:
    canvas_width, canvas_height = canvas_size
    scaled_width = max(1, round(image.width * scale))
    scaled_height = max(1, round(image.height * scale))
    resized = image.resize((scaled_width, scaled_height), Image.Resampling.BICUBIC)
    validity = Image.new("L", (scaled_width, scaled_height), 255)
    canvas = Image.new("RGB", canvas_size, (0, 0, 0))
    valid_canvas = Image.new("L", canvas_size, 0)
    x = (canvas_width - scaled_width) // 2
    y = (canvas_height - scaled_height) // 2
    canvas.paste(resized, (x, y))
    valid_canvas.paste(validity, (x, y))
    return canvas, valid_canvas


def shifted(
    image: Image.Image, dx: int, dy: int, fill: int | tuple[int, int, int] = 0
) -> Image.Image:
    canvas = Image.new(image.mode, image.size, fill)
    canvas.paste(image, (dx, dy))
    return canvas


def grayscale(image: Image.Image) -> np.ndarray:
    return np.asarray(image.convert("L"), dtype=np.float32) / 255.0


def gradient_magnitude(array: np.ndarray) -> np.ndarray:
    gx = np.zeros_like(array)
    gy = np.zeros_like(array)
    gx[:, 1:-1] = (array[:, 2:] - array[:, :-2]) * 0.5
    gy[1:-1, :] = (array[2:, :] - array[:-2, :]) * 0.5
    return np.sqrt(gx * gx + gy * gy)


def estimate_registration(
    reference: Image.Image,
    candidate: Image.Image,
    hard_mask: Image.Image,
) -> dict[str, float]:
    low_width = min(180, max(80, reference.width))
    low_height = min(120, max(60, reference.height))
    low_size = (low_width, low_height)
    factor_x = reference.width / low_width
    factor_y = reference.height / low_height

    reference_low = reference.resize(low_size, Image.Resampling.LANCZOS)
    candidate_low = candidate.resize(low_size, Image.Resampling.LANCZOS)
    protected = hard_mask.resize(low_size, Image.Resampling.NEAREST)
    expansion = max(3, round(min(low_size) * 0.04))
    expansion = expansion if expansion % 2 == 1 else expansion + 1
    protected = protected.filter(ImageFilter.MaxFilter(expansion))
    context = np.asarray(protected, dtype=np.uint8) == 0
    context[:2, :] = False
    context[-2:, :] = False
    context[:, :2] = False
    context[:, -2:] = False
    if int(context.sum()) < max(200, int(context.size * 0.12)):
        return {"scale": 1.0, "dx": 0.0, "dy": 0.0, "score": -1.0}

    reference_gray = grayscale(reference_low)
    reference_gradient = gradient_magnitude(reference_gray)
    best: dict[str, float] | None = None

    for scale in np.arange(0.94, 1.061, 0.01):
        scaled_image, scaled_valid = scaled_center(candidate_low, float(scale), low_size)
        for dx_low in range(-7, 8):
            for dy_low in range(-5, 6):
                moved = shifted(scaled_image, dx_low, dy_low, (0, 0, 0))
                valid = np.asarray(
                    shifted(scaled_valid, dx_low, dy_low, 0), dtype=np.uint8
                ) > 0
                comparison = context & valid
                if comparison.sum() < context.sum() * 0.72:
                    continue

                candidate_gray = grayscale(moved)
                candidate_gradient = gradient_magnitude(candidate_gray)
                reference_values = reference_gray[comparison]
                candidate_values = candidate_gray[comparison]
                reference_normalized = (reference_values - reference_values.mean()) / max(
                    reference_values.std(), 1e-4
                )
                candidate_normalized = (candidate_values - candidate_values.mean()) / max(
                    candidate_values.std(), 1e-4
                )
                intensity_error = float(
                    np.mean((reference_normalized - candidate_normalized) ** 2)
                )

                reference_edges = reference_gradient[comparison]
                candidate_edges = candidate_gradient[comparison]
                gradient_error = float(
                    np.mean(
                        (
                            reference_edges / max(reference_edges.mean(), 1e-4)
                            - candidate_edges / max(candidate_edges.mean(), 1e-4)
                        )
                        ** 2
                    )
                )
                score = 0.35 * intensity_error + 0.65 * gradient_error
                if best is None or score < best["score"]:
                    best = {
                        "scale": float(scale),
                        "dx": float(round(dx_low * factor_x)),
                        "dy": float(round(dy_low * factor_y)),
                        "score": score,
                    }

    return best or {"scale": 1.0, "dx": 0.0, "dy": 0.0, "score": -1.0}


def apply_registration(
    image: Image.Image,
    registration: dict[str, float],
    size: tuple[int, int],
) -> tuple[Image.Image, Image.Image]:
    scaled_image, scaled_valid = scaled_center(image, registration["scale"], size)
    dx = round(registration["dx"])
    dy = round(registration["dy"])
    return (
        shifted(scaled_image, dx, dy, (0, 0, 0)),
        shifted(scaled_valid, dx, dy, 0),
    )


def difference_preview(reference: Image.Image, edited: Image.Image) -> Image.Image:
    reference_array = np.asarray(reference.convert("RGBA"), dtype=np.int16)
    edited_array = np.asarray(edited.convert("RGBA"), dtype=np.int16)
    difference = np.abs(edited_array - reference_array).max(axis=2)
    preview = np.zeros((reference.height, reference.width, 3), dtype=np.uint8)
    preview[..., 0] = np.clip(difference * 4, 0, 255).astype(np.uint8)
    preview[..., 1] = np.clip(difference, 0, 255).astype(np.uint8)
    return Image.fromarray(preview, "RGB")


def vertical_edge_profile(array: np.ndarray) -> np.ndarray:
    """Return a smoothed per-x vertical-edge strength profile."""
    if array.ndim == 3:
        array = (
            array[..., 0] * 0.299
            + array[..., 1] * 0.587
            + array[..., 2] * 0.114
        )
    profile = np.abs(np.diff(array.astype(np.float32), axis=1)).mean(axis=0)
    if profile.size >= 3:
        profile = np.convolve(profile, np.array([0.25, 0.5, 0.25]), mode="same")
    return profile


def horizontal_edge_profile(array: np.ndarray) -> np.ndarray:
    """Return a smoothed per-y horizontal-edge strength profile."""
    if array.ndim == 3:
        array = (
            array[..., 0] * 0.299
            + array[..., 1] * 0.587
            + array[..., 2] * 0.114
        )
    profile = np.abs(np.diff(array.astype(np.float32), axis=0)).mean(axis=1)
    if profile.size >= 3:
        profile = np.convolve(profile, np.array([0.25, 0.5, 0.25]), mode="same")
    return profile


def profile_peaks(profile: np.ndarray, min_strength: float, separation: int = 3) -> list[int]:
    if profile.size < 3:
        return []
    adaptive = max(
        float(min_strength),
        float(np.percentile(profile, 80)),
        float(profile.mean() + profile.std() * 0.5),
    )
    candidates = [
        index
        for index in range(1, profile.size - 1)
        if profile[index] >= adaptive
        and profile[index] >= profile[index - 1]
        and profile[index] >= profile[index + 1]
    ]
    selected: list[int] = []
    for index in sorted(candidates, key=lambda value: float(profile[value]), reverse=True):
        if all(abs(index - existing) > separation for existing in selected):
            selected.append(index)
    return sorted(selected)


def match_profile_peaks(
    top_peaks: list[int],
    bottom_peaks: list[int],
    search_radius: int,
) -> tuple[list[dict[str, int]], list[int], list[int]]:
    available = set(bottom_peaks)
    matches: list[dict[str, int]] = []
    unmatched: list[int] = []
    for top in top_peaks:
        candidates = [bottom for bottom in available if abs(bottom - top) <= search_radius]
        if not candidates:
            unmatched.append(top)
            continue
        bottom = min(candidates, key=lambda value: (abs(value - top), value))
        available.remove(bottom)
        matches.append({"top_x": top, "bottom_x": bottom, "drift": bottom - top})
    return matches, unmatched, sorted(available)


def scan_structure(args: argparse.Namespace) -> None:
    """Scan structural edges across an x- or y-axis paste boundary."""
    image_path = args.image.resolve()
    if not image_path.is_file():
        raise FileNotFoundError(image_path)
    image = load_rgb(image_path)
    if not 0.0 <= args.unmatched_strength_ratio <= 1.0:
        raise ValueError("--unmatched-strength-ratio must be between 0 and 1")
    if args.band < 2:
        raise ValueError("--band must be at least 2")

    rect = as_rect(args.rect)
    validate_rect(rect, image.width, image.height, "Scan rectangle")
    left, top, right, bottom = rect
    seam = int(args.seam)
    pixels = np.asarray(image, dtype=np.uint8)

    if args.seam_axis == "y":
        if not top + 1 <= seam <= bottom - 1:
            raise ValueError("--seam must lie inside --rect with pixels above and below")
        first_start = max(top, seam - args.band)
        second_end = min(bottom, seam + args.band)
        if seam - first_start < 2 or second_end - seam < 2:
            raise ValueError("Scan bands must contain at least two rows on both sides")
        first_profile = vertical_edge_profile(pixels[first_start:seam, left:right])
        second_profile = vertical_edge_profile(pixels[seam:second_end, left:right])
        coordinate_offset = left
        first_band = [left, first_start, right, seam]
        second_band = [left, seam, right, second_end]
        feature_axis = "x"
    else:
        if not left + 1 <= seam <= right - 1:
            raise ValueError("--seam must lie inside --rect with pixels left and right")
        first_start = max(left, seam - args.band)
        second_end = min(right, seam + args.band)
        if seam - first_start < 2 or second_end - seam < 2:
            raise ValueError("Scan bands must contain at least two columns on both sides")
        first_profile = horizontal_edge_profile(pixels[top:bottom, first_start:seam])
        second_profile = horizontal_edge_profile(pixels[top:bottom, seam:second_end])
        coordinate_offset = top
        first_band = [first_start, top, seam, bottom]
        second_band = [seam, top, second_end, bottom]
        feature_axis = "y"

    first_peaks = profile_peaks(first_profile, args.min_strength)
    second_peaks = profile_peaks(second_profile, args.min_strength)
    raw_matches, unmatched_first, unmatched_second = match_profile_peaks(
        first_peaks, second_peaks, args.search_radius
    )
    strongest_first = float(first_profile.max(initial=0.0))
    strongest_second = float(second_profile.max(initial=0.0))
    blocking_unmatched_first = [
        value
        for value in unmatched_first
        if strongest_first > 0
        and float(first_profile[value])
        >= strongest_first * args.unmatched_strength_ratio
    ]
    blocking_unmatched_second = [
        value
        for value in unmatched_second
        if strongest_second > 0
        and float(second_profile[value])
        >= strongest_second * args.unmatched_strength_ratio
    ]
    matches = [
        {
            "first_coord": match["top_x"] + coordinate_offset,
            "second_coord": match["bottom_x"] + coordinate_offset,
            "drift": match["drift"],
        }
        for match in raw_matches
    ]
    unmatched_first_source = [
        value + coordinate_offset for value in unmatched_first
    ]
    unmatched_second_source = [
        value + coordinate_offset for value in unmatched_second
    ]
    blocking_unmatched_first_source = [
        value + coordinate_offset for value in blocking_unmatched_first
    ]
    blocking_unmatched_second_source = [
        value + coordinate_offset for value in blocking_unmatched_second
    ]
    max_drift = max((abs(match["drift"]) for match in matches), default=0)
    passed = (
        bool(matches)
        and not blocking_unmatched_first_source
        and not blocking_unmatched_second_source
        and max_drift <= args.max_drift
    )

    report = {
        "scan_type": "structure",
        "image": str(image_path),
        "image_sha256": sha256(image_path),
        "rect_top_left": list(rect),
        "seam_axis": args.seam_axis,
        "seam_coordinate": seam,
        "feature_axis": feature_axis,
        "band": args.band,
        "max_allowed_drift": args.max_drift,
        "search_radius": args.search_radius,
        "min_edge_strength": args.min_strength,
        "unmatched_strength_ratio": args.unmatched_strength_ratio,
        "first_band_top_left": first_band,
        "second_band_top_left": second_band,
        "matches": matches,
        "unmatched_first_edges": unmatched_first_source,
        "blocking_unmatched_first_edges": blocking_unmatched_first_source,
        "unmatched_second_edges": unmatched_second_source,
        "blocking_unmatched_second_edges": blocking_unmatched_second_source,
        "max_observed_drift": max_drift,
        "passed": passed,
    }
    report_path = args.report.resolve() if args.report else image_path.parent / SEAM_REPORT_NAME
    overlay_path = args.overlay.resolve() if args.overlay else image_path.parent / SEAM_OVERLAY_NAME
    report_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(report_path, report)

    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((left, top, right - 1, bottom - 1), outline=(255, 255, 0), width=1)
    if args.seam_axis == "y":
        draw.line((left, seam, right - 1, seam), fill=(255, 0, 0), width=1)
        for match in matches:
            color = (0, 255, 0) if abs(match["drift"]) <= args.max_drift else (255, 0, 255)
            draw.line((match["first_coord"], first_start, match["first_coord"], seam - 1), fill=color, width=1)
            draw.line((match["second_coord"], seam, match["second_coord"], second_end - 1), fill=color, width=1)
        for coordinate in unmatched_first_source:
            color = (255, 0, 0) if coordinate in blocking_unmatched_first_source else (255, 128, 0)
            draw.line((coordinate, first_start, coordinate, seam - 1), fill=color, width=1)
        for coordinate in unmatched_second_source:
            color = (255, 0, 255) if coordinate in blocking_unmatched_second_source else (0, 128, 255)
            draw.line((coordinate, seam, coordinate, second_end - 1), fill=color, width=1)
    else:
        draw.line((seam, top, seam, bottom - 1), fill=(255, 0, 0), width=1)
        for match in matches:
            color = (0, 255, 0) if abs(match["drift"]) <= args.max_drift else (255, 0, 255)
            draw.line((first_start, match["first_coord"], seam - 1, match["first_coord"]), fill=color, width=1)
            draw.line((seam, match["second_coord"], second_end - 1, match["second_coord"]), fill=color, width=1)
        for coordinate in unmatched_first_source:
            color = (255, 0, 0) if coordinate in blocking_unmatched_first_source else (255, 128, 0)
            draw.line((first_start, coordinate, seam - 1, coordinate), fill=color, width=1)
        for coordinate in unmatched_second_source:
            color = (255, 0, 255) if coordinate in blocking_unmatched_second_source else (0, 128, 255)
            draw.line((seam, coordinate, second_end - 1, coordinate), fill=color, width=1)
    overlay.crop(rect).save(overlay_path)

    print(f"Structure scan: {'PASS' if passed else 'FAIL'}")
    print(f"Seam axis: {args.seam_axis}")
    print(f"Matched edges: {len(matches)}")
    print(
        "Blocking unmatched structural edges: "
        f"first={len(blocking_unmatched_first_source)}, "
        f"second={len(blocking_unmatched_second_source)}"
    )
    print(f"Maximum observed drift: {max_drift} px")
    print(f"Report: {report_path}")
    print(f"Overlay: {overlay_path}")
    if not passed and not args.allow_fail:
        raise SystemExit(2)


def scan_seam(args: argparse.Namespace) -> None:
    image_path = args.image.resolve()
    if not image_path.is_file():
        raise FileNotFoundError(image_path)
    image = load_rgb(image_path)
    if not 0.0 <= args.unmatched_strength_ratio <= 1.0:
        raise ValueError("--unmatched-strength-ratio must be between 0 and 1")
    rect = as_rect(args.rect)
    validate_rect(rect, image.width, image.height, "Scan rectangle")
    left, top, right, bottom = rect
    seam_y = int(args.seam_y)
    if not top + 1 <= seam_y <= bottom - 1:
        raise ValueError("--seam-y must lie inside --rect with pixels on both sides")
    top_start = max(top, seam_y - args.band)
    bottom_end = min(bottom, seam_y + args.band)
    if seam_y - top_start < 2 or bottom_end - seam_y < 2:
        raise ValueError("Scan bands must contain at least two rows above and below the seam")

    pixels = np.asarray(image, dtype=np.uint8)
    top_profile = vertical_edge_profile(pixels[top_start:seam_y, left:right])
    bottom_profile = vertical_edge_profile(pixels[seam_y:bottom_end, left:right])
    top_peaks = profile_peaks(top_profile, args.min_strength)
    bottom_peaks = profile_peaks(bottom_profile, args.min_strength)
    matches, unmatched, unmatched_bottom = match_profile_peaks(
        top_peaks, bottom_peaks, args.search_radius
    )
    strongest_top = float(top_profile.max(initial=0.0))
    strongest_bottom = float(bottom_profile.max(initial=0.0))
    blocking_unmatched = [
        value
        for value in unmatched
        if strongest_top > 0
        and float(top_profile[value]) >= strongest_top * args.unmatched_strength_ratio
    ]
    for match in matches:
        match["top_x"] += left
        match["bottom_x"] += left
    unmatched_source = [value + left for value in unmatched]
    unmatched_bottom_source = [value + left for value in unmatched_bottom]
    blocking_unmatched_source = [value + left for value in blocking_unmatched]
    blocking_unmatched_bottom_source = [
        value + left
        for value in unmatched_bottom
        if strongest_bottom > 0
        and float(bottom_profile[value])
        >= strongest_bottom * args.unmatched_strength_ratio
    ]
    max_drift = max((abs(match["drift"]) for match in matches), default=0)
    passed = (
        bool(matches)
        and not blocking_unmatched_source
        and not blocking_unmatched_bottom_source
        and max_drift <= args.max_drift
    )

    report = {
        "image": str(image_path),
        "rect_top_left": list(rect),
        "seam_y": seam_y,
        "band": args.band,
        "max_allowed_drift": args.max_drift,
        "search_radius": args.search_radius,
        "min_edge_strength": args.min_strength,
        "unmatched_strength_ratio": args.unmatched_strength_ratio,
        "top_band": [top_start, seam_y],
        "bottom_band": [seam_y, bottom_end],
        "matches": matches,
        "unmatched_top_edges": unmatched_source,
        "blocking_unmatched_top_edges": blocking_unmatched_source,
        "unmatched_bottom_edges": unmatched_bottom_source,
        "blocking_unmatched_bottom_edges": blocking_unmatched_bottom_source,
        "max_observed_drift": max_drift,
        "passed": passed,
    }
    report_path = args.report.resolve() if args.report else image_path.parent / SEAM_REPORT_NAME
    overlay_path = args.overlay.resolve() if args.overlay else image_path.parent / SEAM_OVERLAY_NAME
    report_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(report_path, report)

    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((left, top, right - 1, bottom - 1), outline=(255, 255, 0), width=1)
    draw.line((left, seam_y, right - 1, seam_y), fill=(255, 0, 0), width=1)
    for match in matches:
        color = (0, 255, 0) if abs(match["drift"]) <= args.max_drift else (255, 0, 255)
        draw.line((match["top_x"], top_start, match["top_x"], seam_y - 1), fill=color, width=1)
        draw.line((match["bottom_x"], seam_y, match["bottom_x"], bottom_end - 1), fill=color, width=1)
    for x in unmatched_source:
        color = (255, 0, 0) if x in blocking_unmatched_source else (255, 128, 0)
        draw.line((x, top_start, x, seam_y - 1), fill=color, width=1)
    for x in unmatched_bottom_source:
        color = (255, 0, 255) if x in blocking_unmatched_bottom_source else (0, 128, 255)
        draw.line((x, seam_y, x, bottom_end - 1), fill=color, width=1)
    overlay.crop(rect).save(overlay_path)

    print(f"Seam scan: {'PASS' if passed else 'FAIL'}")
    print(f"Matched edges: {len(matches)}")
    print(f"Unmatched top edges: {len(unmatched_source)}")
    print(
        "Blocking unmatched structural edges: "
        f"top={len(blocking_unmatched_source)}, "
        f"bottom={len(blocking_unmatched_bottom_source)}"
    )
    print(f"Maximum observed drift: {max_drift} px")
    print(f"Report: {report_path}")
    print(f"Overlay: {overlay_path}")
    if not passed and not args.allow_fail:
        raise SystemExit(2)


def repair_vertical_seam(args: argparse.Namespace) -> Path:
    """Build a deterministic crop patch by extending protected columns downward."""
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = Path(manifest["source"]).resolve()
    if sha256(source) != manifest["source_sha256"]:
        raise ValueError("Source image differs from the version recorded during prepare")
    crop_rect = as_rect(manifest["crop_rect_top_left"])
    edit_rect = as_rect(manifest["edit_rect_top_left"])
    seam_y = int(args.seam_y)
    if not edit_rect[1] <= seam_y < edit_rect[3]:
        raise ValueError("--seam-y must lie inside the prepared edit rectangle")
    if seam_y - args.sample_band < crop_rect[1]:
        raise ValueError("Context crop does not contain the full protected sample band")
    if args.anchor_rows < 1:
        raise ValueError("--anchor-rows must be at least 1")
    if args.anchor_rows > args.sample_band:
        raise ValueError("--anchor-rows cannot exceed --sample-band")

    source_image = load_rgb(source)
    crop = source_image.crop(crop_rect)
    crop_array = np.asarray(crop, dtype=np.uint8).copy()
    local_edit = relative_rect(edit_rect, crop_rect)
    local_seam = seam_y - crop_rect[1]
    sample_top = local_seam - args.sample_band
    anchor_top = local_seam - args.anchor_rows
    sample = crop_array[anchor_top:local_seam, local_edit[0]:local_edit[2]]
    if sample.shape[0] < 1:
        raise ValueError("Protected anchor rows are empty")

    column_reference = np.median(sample, axis=0).round().astype(np.uint8)
    repair_bottom = local_edit[3]
    crop_array[local_seam:repair_bottom, local_edit[0]:local_edit[2]] = column_reference[None, ...]
    output_path = args.output.resolve() if args.output else manifest_path.parent / GENERATED_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(crop_array, "RGB").save(output_path)

    manifest["deterministic_repair"] = {
        "mode": "vertical-column-extension",
        "seam_y_top_left": seam_y,
        "sample_band": args.sample_band,
        "sample_rows_top_left": [seam_y - args.sample_band, seam_y],
        "anchor_rows": args.anchor_rows,
        "anchor_rows_top_left": [seam_y - args.anchor_rows, seam_y],
        "repair_rect_top_left": [edit_rect[0], seam_y, edit_rect[2], edit_rect[3]],
        "output": str(output_path),
        "output_sha256": sha256(output_path),
    }
    save_json(manifest_path, manifest)
    print("Deterministic repair patch created")
    print(f"Context sample rows: [{seam_y - args.sample_band}, {seam_y})")
    print(f"Coordinate anchor rows: [{seam_y - args.anchor_rows}, {seam_y})")
    print(f"Repair rectangle: {(edit_rect[0], seam_y, edit_rect[2], edit_rect[3])}")
    print(f"Patch: {output_path}")
    return output_path


def crop_parent_authorization_mask(
    mask_path: Path,
    source_size: tuple[int, int],
    crop_rect: Rect,
) -> np.ndarray:
    with Image.open(mask_path) as image:
        mask = image.convert("L")
    if mask.size != source_size:
        raise ValueError(
            "Parent authorization mask must match the full source dimensions"
        )
    return np.asarray(mask.crop(crop_rect), dtype=np.uint8) >= 128


def repair_structure(args: argparse.Namespace) -> Path:
    """Create a narrow deterministic structural bridge without rotating the source."""
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("stage") != "prepared":
        raise ValueError("Structural repair requires a prepared, not yet composed, job")
    if manifest.get("canvas_kind") != "deterministic":
        raise ValueError("Structural repair jobs must be prepared with --canvas-kind deterministic")

    source = Path(manifest["source"]).resolve()
    if sha256(source) != manifest["source_sha256"]:
        raise ValueError("Source image differs from the version recorded during prepare")
    crop_rect = as_rect(manifest["crop_rect_top_left"])
    edit_rect = as_rect(manifest["edit_rect_top_left"])
    seam = int(args.seam)
    if args.sample_band < 1 or args.anchor_width < 1:
        raise ValueError("--sample-band and --anchor-width must be positive")
    if args.anchor_width > args.sample_band:
        raise ValueError("--anchor-width cannot exceed --sample-band")
    if args.max_depth < 1:
        raise ValueError("--max-depth must be positive")

    source_image = load_rgb(source)
    crop = source_image.crop(crop_rect)
    crop_array = np.asarray(crop, dtype=np.uint8).copy()
    local_edit = relative_rect(edit_rect, crop_rect)

    prepared_mask = np.asarray(
        Image.open(manifest["files"]["hard_mask"]).convert("L"), dtype=np.uint8
    ) >= 128
    parent_mask_path = args.authorization_mask.resolve()
    parent_mask = crop_parent_authorization_mask(
        parent_mask_path, source_image.size, crop_rect
    )
    if np.any(prepared_mask & ~parent_mask):
        raise ValueError(
            "Prepared repair mask extends outside --authorization-mask; refusing repair"
        )

    if args.seam_axis == "y":
        seam_is_valid = (
            edit_rect[1] <= seam < edit_rect[3]
            if args.direction == "positive"
            else edit_rect[1] < seam <= edit_rect[3]
        )
        if not seam_is_valid:
            raise ValueError("--seam must lie inside the prepared edit rectangle")
        local_seam = seam - crop_rect[1]
        if args.direction == "positive":
            depth = edit_rect[3] - seam
            if seam - args.sample_band < crop_rect[1]:
                raise ValueError("Context crop lacks the protected sample band above the seam")
            sample = crop_array[
                local_seam - args.anchor_width : local_seam,
                local_edit[0] : local_edit[2],
            ]
            reference = np.median(sample, axis=0).round().astype(np.uint8)
            crop_array[
                local_seam : local_edit[3], local_edit[0] : local_edit[2]
            ] = reference[None, ...]
            repair_rect = [edit_rect[0], seam, edit_rect[2], edit_rect[3]]
            anchor_range = [seam - args.anchor_width, seam]
        else:
            depth = seam - edit_rect[1]
            if seam + args.sample_band > crop_rect[3]:
                raise ValueError("Context crop lacks the protected sample band below the seam")
            sample = crop_array[
                local_seam : local_seam + args.anchor_width,
                local_edit[0] : local_edit[2],
            ]
            reference = np.median(sample, axis=0).round().astype(np.uint8)
            crop_array[
                local_edit[1] : local_seam, local_edit[0] : local_edit[2]
            ] = reference[None, ...]
            repair_rect = [edit_rect[0], edit_rect[1], edit_rect[2], seam]
            anchor_range = [seam, seam + args.anchor_width]
    else:
        seam_is_valid = (
            edit_rect[0] <= seam < edit_rect[2]
            if args.direction == "positive"
            else edit_rect[0] < seam <= edit_rect[2]
        )
        if not seam_is_valid:
            raise ValueError("--seam must lie inside the prepared edit rectangle")
        local_seam = seam - crop_rect[0]
        if args.direction == "positive":
            depth = edit_rect[2] - seam
            if seam - args.sample_band < crop_rect[0]:
                raise ValueError("Context crop lacks the protected sample band left of the seam")
            sample = crop_array[
                local_edit[1] : local_edit[3],
                local_seam - args.anchor_width : local_seam,
            ]
            reference = np.median(sample, axis=1).round().astype(np.uint8)
            crop_array[
                local_edit[1] : local_edit[3], local_seam : local_edit[2]
            ] = reference[:, None, :]
            repair_rect = [seam, edit_rect[1], edit_rect[2], edit_rect[3]]
            anchor_range = [seam - args.anchor_width, seam]
        else:
            depth = seam - edit_rect[0]
            if seam + args.sample_band > crop_rect[2]:
                raise ValueError("Context crop lacks the protected sample band right of the seam")
            sample = crop_array[
                local_edit[1] : local_edit[3],
                local_seam : local_seam + args.anchor_width,
            ]
            reference = np.median(sample, axis=1).round().astype(np.uint8)
            crop_array[
                local_edit[1] : local_edit[3], local_edit[0] : local_seam
            ] = reference[:, None, :]
            repair_rect = [edit_rect[0], edit_rect[1], seam, edit_rect[3]]
            anchor_range = [seam, seam + args.anchor_width]

    if depth < 1 or depth > args.max_depth:
        raise ValueError(
            f"Repair depth {depth}px is outside the allowed range 1..{args.max_depth}px"
        )

    output_path = args.output.resolve() if args.output else manifest_path.parent / GENERATED_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(crop_array, "RGB").save(output_path)
    manifest["deterministic_repair"] = {
        "mode": "axis-locked-structure-extension",
        "seam_axis": args.seam_axis,
        "seam_coordinate_top_left": seam,
        "direction": args.direction,
        "sample_band": args.sample_band,
        "anchor_width": args.anchor_width,
        "anchor_range_top_left": anchor_range,
        "max_depth": args.max_depth,
        "actual_depth": depth,
        "repair_rect_top_left": repair_rect,
        "parent_authorization_mask": str(parent_mask_path),
        "parent_authorization_mask_sha256": sha256(parent_mask_path),
        "output": str(output_path),
        "output_sha256": sha256(output_path),
    }
    save_json(manifest_path, manifest)
    print("Deterministic structure patch created")
    print(f"Seam: axis={args.seam_axis}, coordinate={seam}, direction={args.direction}")
    print(f"Anchor range: {anchor_range}")
    print(f"Repair depth: {depth}px")
    print(f"Repair rectangle: {tuple(repair_rect)}")
    print(f"Patch: {output_path}")
    return output_path


def erode_mask(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask.copy()
    size = radius * 2 + 1
    image = Image.fromarray((mask.astype(np.uint8) * 255), "L")
    return np.asarray(image.filter(ImageFilter.MinFilter(size)), dtype=np.uint8) > 0


def scan_boundary(args: argparse.Namespace) -> None:
    """Inspect the inside edge of a hard mask for retained source-object halos."""
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("stage") != "composed":
        raise ValueError("Boundary scanning requires a composed job")
    source_path = Path(manifest["source"]).resolve()
    output_path = Path(manifest["output"]).resolve()
    registered_path = Path(manifest["files"]["registered"]).resolve()
    for path in (source_path, output_path, registered_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    crop_rect = as_rect(manifest["crop_rect_top_left"])
    source_crop = load_rgb(source_path).crop(crop_rect)
    final_crop = load_rgb(output_path).crop(crop_rect)
    registered = load_rgb(registered_path)
    hard_mask = np.asarray(Image.open(manifest["files"]["hard_mask"]).convert("L"), dtype=np.uint8) > 0
    if not np.any(hard_mask):
        raise ValueError("Hard mask is empty")
    if args.ring < 1:
        raise ValueError("--ring must be positive")
    if args.min_informative_pixels < 1:
        raise ValueError("--min-informative-pixels must be positive")
    if not 0.0 <= args.min_informative_fraction <= 1.0:
        raise ValueError("--min-informative-fraction must be between 0 and 1")

    eroded_once = erode_mask(hard_mask, args.ring)
    eroded_twice = erode_mask(eroded_once, args.ring)
    inside_ring = hard_mask & ~eroded_once
    comparison_ring = eroded_once & ~eroded_twice
    if not np.any(inside_ring) or not np.any(comparison_ring):
        raise ValueError("Mask is too small for the requested boundary ring")

    source_array = np.asarray(source_crop, dtype=np.float32)
    final_array = np.asarray(final_crop, dtype=np.float32)
    registered_array = np.asarray(registered, dtype=np.float32)
    generated_delta = np.linalg.norm(registered_array - source_array, axis=2)
    final_delta = np.linalg.norm(final_array - source_array, axis=2)
    informative = inside_ring & (generated_delta >= args.min_generated_delta)
    retained_fraction_map = np.ones_like(generated_delta, dtype=np.float32)
    retained_fraction_map[informative] = final_delta[informative] / np.maximum(
        generated_delta[informative], 1e-6
    )
    retained_source_risk = informative & (retained_fraction_map < args.min_applied_fraction)

    final_gradient = gradient_magnitude(grayscale(final_crop))
    inner_q95 = float(np.percentile(final_gradient[inside_ring], 95))
    comparison_q95 = float(np.percentile(final_gradient[comparison_ring], 95))
    edge_ratio = inner_q95 / max(comparison_q95, 1e-6)
    edge_threshold = max(args.min_edge_strength, comparison_q95 * args.edge_multiplier)
    hard_edge_risk = inside_ring & (final_gradient >= edge_threshold)
    combined_risk = retained_source_risk | hard_edge_risk

    informative_count = int(np.count_nonzero(informative))
    retained_risk_count = int(np.count_nonzero(retained_source_risk))
    ring_count = int(np.count_nonzero(inside_ring))
    hard_edge_count = int(np.count_nonzero(hard_edge_risk))
    combined_count = int(np.count_nonzero(combined_risk))
    minimum_informative = max(
        args.min_informative_pixels,
        int(np.ceil(ring_count * args.min_informative_fraction)),
    )
    informative_sufficient = informative_count >= minimum_informative
    retained_risk_fraction = retained_risk_count / max(informative_count, 1)
    hard_edge_fraction = hard_edge_count / max(ring_count, 1)
    combined_risk_fraction = combined_count / max(ring_count, 1)
    passed = (
        informative_sufficient
        and retained_risk_fraction <= args.max_retained_fraction
        and hard_edge_fraction <= args.max_hard_edge_fraction
        and edge_ratio <= args.max_edge_ratio
    )

    report = {
        "scan_type": "boundary",
        "manifest": str(manifest_path),
        "image": str(output_path),
        "image_sha256": sha256(output_path),
        "crop_rect_top_left": list(crop_rect),
        "ring_width": args.ring,
        "inside_ring_pixels": ring_count,
        "informative_ring_pixels": informative_count,
        "minimum_informative_ring_pixels": minimum_informative,
        "informative_coverage_sufficient": informative_sufficient,
        "retained_source_risk_pixels": retained_risk_count,
        "retained_source_risk_fraction": retained_risk_fraction,
        "hard_edge_risk_pixels": hard_edge_count,
        "hard_edge_risk_fraction": hard_edge_fraction,
        "combined_risk_pixels": combined_count,
        "combined_risk_fraction": combined_risk_fraction,
        "inside_ring_gradient_q95": inner_q95,
        "comparison_ring_gradient_q95": comparison_q95,
        "boundary_edge_ratio": edge_ratio,
        "limits": {
            "max_retained_fraction": args.max_retained_fraction,
            "max_hard_edge_fraction": args.max_hard_edge_fraction,
            "max_edge_ratio": args.max_edge_ratio,
            "min_informative_pixels": args.min_informative_pixels,
            "min_informative_fraction": args.min_informative_fraction,
            "min_generated_delta": args.min_generated_delta,
            "min_applied_fraction": args.min_applied_fraction,
            "min_edge_strength": args.min_edge_strength,
            "edge_multiplier": args.edge_multiplier,
        },
        "passed": passed,
    }
    report_path = args.report.resolve() if args.report else manifest_path.parent / BOUNDARY_REPORT_NAME
    overlay_path = args.overlay.resolve() if args.overlay else manifest_path.parent / BOUNDARY_OVERLAY_NAME
    report_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(report_path, report)

    overlay_array = np.asarray(final_crop, dtype=np.uint8).copy()
    overlay_array[inside_ring] = (
        overlay_array[inside_ring].astype(np.float32) * 0.55
        + np.array([255, 210, 0], dtype=np.float32) * 0.45
    ).round().astype(np.uint8)
    overlay_array[combined_risk] = np.array([255, 0, 255], dtype=np.uint8)
    Image.fromarray(overlay_array, "RGB").save(overlay_path)

    print(f"Boundary scan: {'PASS' if passed else 'FAIL'}")
    print(
        "Informative boundary pixels: "
        f"{informative_count}/{minimum_informative} minimum"
    )
    print(f"Retained-source risk fraction: {retained_risk_fraction:.4f}")
    print(f"Hard-edge risk fraction: {hard_edge_fraction:.4f}")
    print(f"Boundary edge ratio: {edge_ratio:.4f}")
    print(f"Report: {report_path}")
    print(f"Overlay: {overlay_path}")
    if not passed and not args.allow_fail:
        raise SystemExit(2)


def verify_final(args: argparse.Namespace) -> None:
    """Verify a chained result against the original source and union of all masks."""
    source_path = args.source.resolve()
    output_path = args.output.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if not output_path.is_file():
        raise FileNotFoundError(output_path)
    if source_path == output_path:
        raise ValueError("Source and output must be different files")
    if output_path.suffix.lower() != ".png":
        raise ValueError("Final coordinate-locked output must be a PNG")

    source = load_source(source_path)
    output = load_source(output_path)
    size_matches = output.size == source.size
    mode_matches = output.mode == source.mode
    if not size_matches or not mode_matches:
        raise ValueError("Final image size and mode must match the original source")

    union_mask = np.zeros((source.height, source.width), dtype=bool)
    mask_records: list[dict[str, Any]] = []
    for raw_path in args.mask:
        mask_path = raw_path.resolve()
        if not mask_path.is_file():
            raise FileNotFoundError(mask_path)
        with Image.open(mask_path) as image:
            mask = image.convert("L")
        if mask.size != source.size:
            raise ValueError(
                f"Final authorization mask must match source size: {mask_path}"
            )
        enabled = np.asarray(mask, dtype=np.uint8) >= 128
        if not np.any(enabled):
            raise ValueError(f"Final authorization mask is empty: {mask_path}")
        union_mask |= enabled
        mask_records.append(
            {
                "path": str(mask_path),
                "sha256": sha256(mask_path),
                "enabled_pixels": int(np.count_nonzero(enabled)),
            }
        )

    source_array = np.asarray(source, dtype=np.uint8)
    output_array = np.asarray(output, dtype=np.uint8)
    absolute_diff = np.abs(
        output_array.astype(np.int16) - source_array.astype(np.int16)
    )
    outside_values = absolute_diff[~union_mask]
    outside_nonzero_channels = int(np.count_nonzero(outside_values))
    outside_max_difference = int(outside_values.max(initial=0))
    changed_pixels = np.any(absolute_diff > 0, axis=2)
    changed_inside = int(np.count_nonzero(changed_pixels & union_mask))
    changed_outside = int(np.count_nonzero(changed_pixels & ~union_mask))
    containment_passed = outside_nonzero_channels == 0 and outside_max_difference == 0

    manifest_checks: list[dict[str, Any]] = []
    for raw_path in args.manifest:
        manifest_path = raw_path.resolve()
        if not manifest_path.is_file():
            raise FileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_source = Path(manifest.get("source", "")).resolve()
        recorded_source_hash = manifest.get("source_sha256")
        source_hash_valid = bool(
            manifest_source.is_file()
            and recorded_source_hash
            and sha256(manifest_source) == recorded_source_hash
        )
        hard_mask_path = Path(manifest.get("files", {}).get("hard_mask", "")).resolve()
        crop_rect = as_rect(manifest["crop_rect_top_left"])
        validate_rect(crop_rect, source.width, source.height, "Manifest crop rectangle")
        artifact_hash = manifest.get("artifact_sha256", {}).get("hard_mask")
        hard_mask_valid = bool(
            hard_mask_path.is_file()
            and artifact_hash
            and sha256(hard_mask_path) == artifact_hash
        )
        hard_mask_inside_union = False
        hard_mask_enabled_pixels = 0
        if hard_mask_valid:
            with Image.open(hard_mask_path) as image:
                job_mask = np.asarray(image.convert("L"), dtype=np.uint8) >= 128
            expected_size = (crop_rect[2] - crop_rect[0], crop_rect[3] - crop_rect[1])
            if (job_mask.shape[1], job_mask.shape[0]) != expected_size:
                hard_mask_valid = False
            else:
                full_job_mask = np.zeros_like(union_mask)
                full_job_mask[crop_rect[1] : crop_rect[3], crop_rect[0] : crop_rect[2]] = job_mask
                hard_mask_inside_union = not bool(np.any(full_job_mask & ~union_mask))
                hard_mask_enabled_pixels = int(np.count_nonzero(full_job_mask))

        verification = manifest.get("verification", {})
        manifest_output = Path(manifest.get("output", "")).resolve()
        output_hash_valid = bool(
            manifest_output.is_file()
            and manifest.get("output_sha256")
            and sha256(manifest_output) == manifest.get("output_sha256")
        )
        verification_passed = bool(
            verification.get("source_unchanged")
            and verification.get("final_size_matches_source")
            and verification.get("final_mode_matches_source")
            and verification.get("outside_mask_nonzero_channels") == 0
            and verification.get("outside_mask_max_channel_difference") == 0
            and verification.get("outside_mask_pixels_bit_identical")
        )
        manifest_passed = bool(
            manifest.get("stage") == "composed"
            and source_hash_valid
            and hard_mask_valid
            and hard_mask_inside_union
            and output_hash_valid
            and verification_passed
        )
        manifest_checks.append(
            {
                "path": str(manifest_path),
                "stage": manifest.get("stage"),
                "source": str(manifest_source),
                "source_sha256": recorded_source_hash,
                "source_hash_valid": source_hash_valid,
                "hard_mask": str(hard_mask_path),
                "hard_mask_hash_valid": hard_mask_valid,
                "hard_mask_inside_final_union": hard_mask_inside_union,
                "hard_mask_enabled_pixels": hard_mask_enabled_pixels,
                "output": str(manifest_output),
                "output_sha256": manifest.get("output_sha256"),
                "output_hash_valid": output_hash_valid,
                "job_verification_passed": verification_passed,
                "passed": manifest_passed,
            }
        )

    expected_input_hash = sha256(source_path)
    for item in manifest_checks:
        item["chain_input_matches_previous"] = bool(
            item["source_hash_valid"] and item["source_sha256"] == expected_input_hash
        )
        expected_input_hash = item["output_sha256"]
    chain_ends_at_final = bool(
        manifest_checks and expected_input_hash == sha256(output_path)
    )
    manifest_chain_passed = bool(
        manifest_checks
        and all(item["chain_input_matches_previous"] for item in manifest_checks)
        and chain_ends_at_final
    )

    manifest_output_hashes = {
        item["output_sha256"]
        for item in manifest_checks
        if item["output_hash_valid"]
    }
    allowed_scan_hashes = manifest_output_hashes | {sha256(output_path)}
    manifest_paths = {item["path"] for item in manifest_checks}

    scan_checks: list[dict[str, Any]] = []
    for raw_path in args.scan_report:
        scan_path = raw_path.resolve()
        if not scan_path.is_file():
            raise FileNotFoundError(scan_path)
        scan = json.loads(scan_path.read_text(encoding="utf-8"))
        scan_type = scan.get("scan_type")
        scan_image = Path(scan.get("image", "")).resolve()
        recorded_image_hash = scan.get("image_sha256")
        image_hash_valid = bool(
            scan_image.is_file()
            and recorded_image_hash
            and sha256(scan_image) == recorded_image_hash
        )
        image_belongs_to_job = bool(
            image_hash_valid and recorded_image_hash in allowed_scan_hashes
        )
        boundary_manifest_valid = True
        if scan_type == "boundary":
            boundary_manifest = str(Path(scan.get("manifest", "")).resolve())
            boundary_manifest_valid = boundary_manifest in manifest_paths
            if boundary_manifest_valid:
                linked_manifest = next(
                    item for item in manifest_checks if item["path"] == boundary_manifest
                )
                boundary_manifest_valid = bool(
                    linked_manifest["output"] == str(scan_image)
                    and linked_manifest["output_hash_valid"]
                )
        recognized_type = scan_type in {"boundary", "structure"}
        scan_passed = bool(
            recognized_type
            and scan.get("passed") is True
            and image_hash_valid
            and image_belongs_to_job
            and boundary_manifest_valid
        )
        scan_checks.append(
            {
                "path": str(scan_path),
                "scan_type": scan_type,
                "recognized_scan_type": recognized_type,
                "image": str(scan_image),
                "recorded_image_sha256": recorded_image_hash,
                "image_hash_valid": image_hash_valid,
                "image_belongs_to_job": image_belongs_to_job,
                "boundary_manifest_valid": boundary_manifest_valid,
                "report_passed": scan.get("passed") is True,
                "passed": scan_passed,
            }
        )

    all_manifests_passed = bool(
        manifest_chain_passed and all(item["passed"] for item in manifest_checks)
    )
    all_scans_passed = bool(scan_checks) and all(
        item["passed"] for item in scan_checks
    )
    passed = containment_passed and all_manifests_passed and all_scans_passed

    report = {
        "source": str(source_path),
        "output": str(output_path),
        "source_sha256": sha256(source_path),
        "output_sha256": sha256(output_path),
        "source_size": list(source.size),
        "output_size": list(output.size),
        "source_mode": source.mode,
        "output_mode": output.mode,
        "size_matches": size_matches,
        "mode_matches": mode_matches,
        "authorization_masks": mask_records,
        "union_authorized_pixels": int(np.count_nonzero(union_mask)),
        "changed_pixels_inside_union": changed_inside,
        "changed_pixels_outside_union": changed_outside,
        "outside_union_nonzero_channels": outside_nonzero_channels,
        "outside_union_max_channel_difference": outside_max_difference,
        "outside_union_pixels_bit_identical": containment_passed,
        "job_manifests": manifest_checks,
        "manifest_chain_ends_at_final": chain_ends_at_final,
        "manifest_chain_passed": manifest_chain_passed,
        "all_job_manifests_passed": all_manifests_passed,
        "scan_reports": scan_checks,
        "all_scan_reports_passed": all_scans_passed,
        "passed": passed,
    }
    report_path = args.report.resolve() if args.report else output_path.parent / FINAL_REPORT_NAME
    difference_path = (
        args.difference_preview.resolve()
        if args.difference_preview
        else output_path.parent / FINAL_DIFF_NAME
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    difference_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(report_path, report)
    difference_preview(source, output).save(difference_path)

    print(f"Final verification: {'PASS' if passed else 'FAIL'}")
    print(f"Source size/mode preserved: {size_matches and mode_matches}")
    print(f"Changed pixels outside union: {changed_outside}")
    print(f"Outside-union differing channels: {outside_nonzero_channels}")
    print(f"Outside-union maximum difference: {outside_max_difference}")
    print(
        f"Job manifests individually: {sum(item['passed'] for item in manifest_checks)}/"
        f"{len(manifest_checks)} passed; chain: "
        f"{'PASS' if manifest_chain_passed else 'FAIL'}"
    )
    print(
        f"Scan reports: {sum(item['passed'] for item in scan_checks)}/"
        f"{len(scan_checks)} passed"
    )
    print(f"Report: {report_path}")
    print(f"Difference preview: {difference_path}")
    if not passed and not args.allow_fail:
        raise SystemExit(2)


def default_output_path(source: Path, out_dir: Path) -> Path:
    return out_dir / f"{source.stem}{DEFAULT_OUTPUT_SUFFIX}"


def compose(args: argparse.Namespace) -> Path:
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = Path(manifest["source"]).resolve()
    source_hash_before = sha256(source)
    if source_hash_before != manifest["source_sha256"]:
        raise ValueError("Source image differs from the version recorded during prepare")

    ai_patch = args.ai_patch.resolve()
    if not ai_patch.is_file():
        raise FileNotFoundError(ai_patch)
    out_dir = manifest_path.parent
    output_path = args.output.resolve() if args.output else default_output_path(source, out_dir)
    if output_path == source:
        raise ValueError("Refusing to overwrite the source image")
    if output_path.suffix.lower() != ".png":
        raise ValueError("Coordinate-locked results must use lossless PNG output")
    if output_path.exists() and not args.force_output:
        raise FileExistsError(
            f"{output_path} already exists; choose another output or pass --force-output"
        )

    for artifact_name in ("source_crop", "hard_mask", "blend_mask"):
        artifact_path = Path(manifest["files"][artifact_name])
        expected_hash = manifest["artifact_sha256"][artifact_name]
        if not artifact_path.is_file() or sha256(artifact_path) != expected_hash:
            raise ValueError(f"Prepared artifact changed: {artifact_name}")

    original = load_source(source)
    crop_rect = as_rect(manifest["crop_rect_top_left"])
    crop = original.crop(crop_rect)
    reference_rgb = crop.convert("RGB")
    hard_mask = Image.open(manifest["files"]["hard_mask"]).convert("L")
    blend_mask = Image.open(manifest["files"]["blend_mask"]).convert("L")

    raw_ai = load_rgb(ai_patch)
    normalized, normalization_box = normalize_to_canvas(raw_ai, reference_rgb.size)
    if args.registration == "auto":
        registration = estimate_registration(reference_rgb, normalized, hard_mask)
    else:
        registration = {"scale": 1.0, "dx": 0.0, "dy": 0.0, "score": -1.0}
    registered, valid_mask = apply_registration(normalized, registration, reference_rgb.size)

    hard_array = np.asarray(hard_mask, dtype=np.uint8) > 0
    valid_array = np.asarray(valid_mask, dtype=np.uint8) > 0
    if np.any(hard_array & ~valid_array):
        raise AssertionError("Registration created invalid pixels inside the authorization mask")

    registered_path = out_dir / REGISTERED_NAME
    registered.save(registered_path)
    alpha = np.asarray(blend_mask, dtype=np.float32)[..., None] / 255.0
    reference_array = np.asarray(reference_rgb, dtype=np.float32)
    registered_array = np.asarray(registered, dtype=np.float32)
    composed_rgb = np.clip(
        registered_array * alpha + reference_array * (1.0 - alpha), 0, 255
    ).round().astype(np.uint8)

    if original.mode == "RGBA":
        final_array = np.asarray(original, dtype=np.uint8).copy()
        crop_array = np.asarray(crop, dtype=np.uint8).copy()
        crop_array[..., :3] = composed_rgb
    else:
        final_array = np.asarray(original, dtype=np.uint8).copy()
        crop_array = composed_rgb
    left, top, right, bottom = crop_rect
    final_array[top:bottom, left:right] = crop_array
    final = Image.fromarray(final_array, original.mode)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path)
    saved_final = load_source(output_path)
    if saved_final.size != original.size:
        raise AssertionError("Saved final dimensions differ from source dimensions")
    if saved_final.mode != original.mode:
        raise AssertionError("Saved final mode differs from source mode")

    allowed = np.zeros((original.height, original.width), dtype=bool)
    allowed[top:bottom, left:right] = hard_array
    original_array = np.asarray(original, dtype=np.uint8)
    saved_array = np.asarray(saved_final, dtype=np.uint8)
    absolute_diff = np.abs(saved_array.astype(np.int16) - original_array.astype(np.int16))
    outside_values = absolute_diff[~allowed]
    outside_nonzero_channels = int(np.count_nonzero(outside_values))
    outside_max_difference = int(outside_values.max(initial=0))
    if outside_nonzero_channels != 0 or outside_max_difference != 0:
        raise AssertionError("Pixels outside the authorization mask changed after saving")

    difference_preview(original, saved_final).save(out_dir / DIFF_NAME)
    source_hash_after = sha256(source)
    source_unchanged = source_hash_after == source_hash_before == manifest["source_sha256"]
    if not source_unchanged:
        raise AssertionError("Source file changed during composition")

    generated_in_job = out_dir / GENERATED_NAME
    manifest.update(
        {
            "stage": "composed",
            "ai_patch": str(ai_patch),
            "ai_patch_sha256": sha256(ai_patch),
            "ai_patch_size": list(raw_ai.size),
            "generated_persisted_in_job": generated_in_job.is_file(),
            "normalization_crop_box": normalization_box,
            "registration_mode": args.registration,
            "registration": registration,
            "output": str(output_path),
            "output_sha256": sha256(output_path),
            "verification": {
                "source_unchanged": source_unchanged,
                "final_size_matches_source": saved_final.size == original.size,
                "final_mode_matches_source": saved_final.mode == original.mode,
                "outside_mask_nonzero_channels": outside_nonzero_channels,
                "outside_mask_max_channel_difference": outside_max_difference,
                "outside_mask_pixels_bit_identical": True,
            },
        }
    )
    save_json(manifest_path, manifest)

    print("Stage: composed")
    print(f"AI input size: {raw_ai.width} x {raw_ai.height}")
    print(
        "Registration: "
        f"mode={args.registration}, scale={registration['scale']:.3f}, "
        f"dx={registration['dx']:.0f}, dy={registration['dy']:.0f}, "
        f"score={registration['score']:.6f}"
    )
    print(f"Final size: {saved_final.width} x {saved_final.height}")
    print(f"Source unchanged: {source_unchanged}")
    print(f"Outside-mask differing channels: {outside_nonzero_channels}")
    print(f"Outside-mask maximum difference: {outside_max_difference}")
    print(f"Final: {output_path}")
    print(f"Manifest: {manifest_path}")
    return output_path


def status(args: argparse.Namespace) -> None:
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    generated_path = Path(manifest["files"]["generated"])
    output_path = Path(manifest["output"]) if manifest.get("output") else None
    summary = {
        "stage": manifest.get("stage"),
        "source": manifest.get("source"),
        "source_exists": Path(manifest["source"]).is_file(),
        "source_hash_matches": (
            Path(manifest["source"]).is_file()
            and sha256(Path(manifest["source"])) == manifest.get("source_sha256")
        ),
        "crop": manifest.get("files", {}).get("source_crop"),
        "generated": str(generated_path),
        "generated_exists": generated_path.is_file(),
        "output": str(output_path) if output_path else None,
        "output_exists": bool(output_path and output_path.is_file()),
        "verification": manifest.get("verification"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    expand_mask_parser = subparsers.add_parser(
        "expand-mask",
        help="Expand a tight intent mask into a broad evidence authoring workspace",
    )
    expand_mask_parser.add_argument("--input", type=Path, required=True)
    expand_mask_parser.add_argument("--output", type=Path, required=True)
    expand_mask_parser.add_argument("--scale", type=float, default=3.0)
    expand_mask_parser.add_argument("--min-margin", type=int, default=128)
    expand_mask_parser.add_argument(
        "--canvas-size", type=int, nargs=2, metavar=("WIDTH", "HEIGHT")
    )
    expand_mask_parser.add_argument(
        "--offset", type=int, nargs=2, default=(0, 0), metavar=("X", "Y")
    )
    expand_mask_parser.add_argument(
        "--limit-rect",
        type=int,
        nargs=4,
        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
    )
    expand_mask_parser.add_argument("--report", type=Path)
    expand_mask_parser.add_argument("--force", action="store_true")
    expand_mask_parser.set_defaults(func=expand_authorization_mask)

    prepare_parser = subparsers.add_parser("prepare", help="Create crop, masks, and manifest")
    prepare_parser.add_argument("--source", type=Path, required=True)
    prepare_parser.add_argument("--edit-rect", type=int, nargs=4, required=True, metavar=("LEFT", "Y1", "RIGHT", "Y2"))
    prepare_parser.add_argument("--crop-rect", type=int, nargs=4, metavar=("LEFT", "Y1", "RIGHT", "Y2"))
    prepare_parser.add_argument("--origin", choices=("top-left", "bottom-left"), default="top-left")
    prepare_parser.add_argument("--padding", type=int, default=96)
    prepare_parser.add_argument("--feather", type=int, default=8)
    prepare_parser.add_argument(
        "--canvas-kind",
        choices=("generation", "deterministic"),
        default="generation",
        help="Validate legal AI canvas constraints or allow a small deterministic repair crop",
    )
    prepare_parser.add_argument("--mask", type=Path)
    prepare_parser.add_argument("--out-dir", type=Path, required=True)
    prepare_parser.add_argument("--force", action="store_true", help="Replace an existing job manifest")
    prepare_parser.set_defaults(func=prepare)

    compose_parser = subparsers.add_parser("compose", help="Register, mask, compose, and verify")
    compose_parser.add_argument("--manifest", type=Path, required=True)
    compose_parser.add_argument("--ai-patch", type=Path, required=True)
    compose_parser.add_argument("--output", type=Path)
    compose_parser.add_argument("--registration", choices=("auto", "off"), default="auto")
    compose_parser.add_argument("--force-output", action="store_true", help="Replace an existing output PNG")
    compose_parser.set_defaults(func=compose)

    status_parser = subparsers.add_parser("status", help="Print a compact recovery summary")
    status_parser.add_argument("--manifest", type=Path, required=True)
    status_parser.set_defaults(func=status)

    structure_scan_parser = subparsers.add_parser(
        "scan-structure",
        help="Check structural edges across an x- or y-axis paste boundary",
    )
    structure_scan_parser.add_argument("--image", type=Path, required=True)
    structure_scan_parser.add_argument(
        "--rect",
        type=int,
        nargs=4,
        required=True,
        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
    )
    structure_scan_parser.add_argument(
        "--seam-axis",
        choices=("x", "y"),
        required=True,
        help="x for a vertical paste boundary; y for a horizontal paste boundary",
    )
    structure_scan_parser.add_argument("--seam", type=int, required=True)
    structure_scan_parser.add_argument("--band", type=int, default=16)
    structure_scan_parser.add_argument("--max-drift", type=int, default=1)
    structure_scan_parser.add_argument("--search-radius", type=int, default=8)
    structure_scan_parser.add_argument("--min-strength", type=float, default=6.0)
    structure_scan_parser.add_argument(
        "--unmatched-strength-ratio",
        type=float,
        default=0.35,
        help="Only unmatched edges at least this fraction of the strongest edge block delivery",
    )
    structure_scan_parser.add_argument("--report", type=Path)
    structure_scan_parser.add_argument("--overlay", type=Path)
    structure_scan_parser.add_argument("--allow-fail", action="store_true")
    structure_scan_parser.set_defaults(func=scan_structure)

    structure_repair_parser = subparsers.add_parser(
        "repair-structure",
        help="Create a narrow mask-authorized structural bridge without rotating the source",
    )
    structure_repair_parser.add_argument("--manifest", type=Path, required=True)
    structure_repair_parser.add_argument(
        "--seam-axis", choices=("x", "y"), required=True
    )
    structure_repair_parser.add_argument("--seam", type=int, required=True)
    structure_repair_parser.add_argument(
        "--direction",
        choices=("positive", "negative"),
        required=True,
        help="positive extends toward increasing coordinates; negative extends toward decreasing coordinates",
    )
    structure_repair_parser.add_argument("--sample-band", type=int, default=16)
    structure_repair_parser.add_argument("--anchor-width", type=int, default=4)
    structure_repair_parser.add_argument("--max-depth", type=int, default=12)
    structure_repair_parser.add_argument(
        "--authorization-mask",
        type=Path,
        required=True,
        help="Parent source-sized mask that the repair job must remain inside",
    )
    structure_repair_parser.add_argument("--output", type=Path)
    structure_repair_parser.set_defaults(func=repair_structure)

    final_verify_parser = subparsers.add_parser(
        "verify-final",
        help="Compare a chained final PNG with the original through the union of all masks",
    )
    final_verify_parser.add_argument("--source", type=Path, required=True)
    final_verify_parser.add_argument("--output", type=Path, required=True)
    final_verify_parser.add_argument(
        "--mask", type=Path, action="append", required=True
    )
    final_verify_parser.add_argument(
        "--manifest",
        type=Path,
        action="append",
        required=True,
        help="Composed job manifest; repeat for every AI and deterministic job",
    )
    final_verify_parser.add_argument(
        "--scan-report",
        type=Path,
        action="append",
        required=True,
        help="Passing boundary or structure report; repeat for every required scan",
    )
    final_verify_parser.add_argument("--report", type=Path)
    final_verify_parser.add_argument("--difference-preview", type=Path)
    final_verify_parser.add_argument("--allow-fail", action="store_true")
    final_verify_parser.set_defaults(func=verify_final)

    scan_parser = subparsers.add_parser(
        "scan-seam",
        help="Legacy y-axis seam scanner retained for existing jobs; use scan-structure",
    )
    scan_parser.add_argument("--image", type=Path, required=True)
    scan_parser.add_argument("--rect", type=int, nargs=4, required=True, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    scan_parser.add_argument("--seam-y", type=int, required=True)
    scan_parser.add_argument("--band", type=int, default=16)
    scan_parser.add_argument("--max-drift", type=int, default=1)
    scan_parser.add_argument("--search-radius", type=int, default=8)
    scan_parser.add_argument("--min-strength", type=float, default=6.0)
    scan_parser.add_argument(
        "--unmatched-strength-ratio",
        type=float,
        default=0.35,
        help="Only unmatched edges at least this fraction of the strongest edge block delivery",
    )
    scan_parser.add_argument("--report", type=Path)
    scan_parser.add_argument("--overlay", type=Path)
    scan_parser.add_argument("--allow-fail", action="store_true")
    scan_parser.set_defaults(func=scan_seam)

    repair_parser = subparsers.add_parser(
        "repair-vertical-seam",
        help="Legacy downward repair retained for existing jobs; use repair-structure",
    )
    repair_parser.add_argument("--manifest", type=Path, required=True)
    repair_parser.add_argument("--seam-y", type=int, required=True)
    repair_parser.add_argument("--sample-band", type=int, default=24)
    repair_parser.add_argument(
        "--anchor-rows",
        type=int,
        default=4,
        help="Number of protected rows immediately above the seam used to lock column coordinates",
    )
    repair_parser.add_argument("--output", type=Path)
    repair_parser.set_defaults(func=repair_vertical_seam)

    boundary_parser = subparsers.add_parser(
        "scan-boundary", help="Check a composed mask edge for source-object halos and hard cut lines"
    )
    boundary_parser.add_argument("--manifest", type=Path, required=True)
    boundary_parser.add_argument("--ring", type=int, default=6)
    boundary_parser.add_argument("--min-generated-delta", type=float, default=18.0)
    boundary_parser.add_argument("--min-informative-pixels", type=int, default=16)
    boundary_parser.add_argument("--min-informative-fraction", type=float, default=0.02)
    boundary_parser.add_argument("--min-applied-fraction", type=float, default=0.35)
    boundary_parser.add_argument("--max-retained-fraction", type=float, default=0.25)
    boundary_parser.add_argument("--min-edge-strength", type=float, default=0.08)
    boundary_parser.add_argument("--edge-multiplier", type=float, default=2.0)
    boundary_parser.add_argument("--max-hard-edge-fraction", type=float, default=0.12)
    boundary_parser.add_argument("--max-edge-ratio", type=float, default=2.5)
    boundary_parser.add_argument("--report", type=Path)
    boundary_parser.add_argument("--overlay", type=Path)
    boundary_parser.add_argument("--allow-fail", action="store_true")
    boundary_parser.set_defaults(func=scan_boundary)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
