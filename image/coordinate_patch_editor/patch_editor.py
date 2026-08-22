#!/usr/bin/env python3
"""Coordinate-safe AI patch editor.

The script separates the generative step from geometry:
1. ``prepare`` extracts an exact padded crop and writes a manifest.
2. An image model edits that crop.
3. ``compose`` estimates small scale/translation drift from unchanged context,
   aligns the edited crop, and pastes only the approved object mask back at the
   original integer coordinates.

Pixels outside the hard object rectangle are copied from the source image and
are verified to be bit-identical before the result is saved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


SOURCE_DEFAULT = Path(r"D:\NDC_project\image\备选\法院-档案室.png")
OUT_DIR_DEFAULT = Path(r"D:\NDC_project\image\coordinate_patch_editor")

# Coordinates agreed with the user, expressed with a bottom-left origin.
OBJECT_CARTESIAN = (1232, 512, 1568, 624)
CROP_CARTESIAN = (1120, 408, 1680, 728)

CROP_NAME = "court_archive_folder_crop.png"
MASK_NAME = "court_archive_folder_mask.png"
AI_NAME = "court_archive_folder_ai.png"
REGISTERED_NAME = "court_archive_folder_registered.png"
DIFF_NAME = "court_archive_folder_diff.png"
FINAL_NAME = "法院-档案室_坐标回贴测试.png"
MANIFEST_NAME = "court_archive_folder_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cartesian_to_raster(rect: tuple[int, int, int, int], height: int) -> tuple[int, int, int, int]:
    left, bottom, right, top = rect
    return left, height - top, right, height - bottom


def load_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def relative_rect(
    inner: tuple[int, int, int, int], outer: tuple[int, int, int, int]
) -> tuple[int, int, int, int]:
    return (
        inner[0] - outer[0],
        inner[1] - outer[1],
        inner[2] - outer[0],
        inner[3] - outer[1],
    )


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_masks(size: tuple[int, int], object_rect: tuple[int, int, int, int]) -> tuple[Image.Image, Image.Image]:
    hard = Image.new("L", size, 0)
    left, top, right, bottom = object_rect
    # Coordinate rectangles use the common half-open convention [left, right)
    # and [top, bottom). Pillow's drawing API is inclusive, so subtract one.
    ImageDraw.Draw(hard).rectangle((left, top, right - 1, bottom - 1), fill=255)

    # Feather inward, then clip by the hard rectangle. This softens the seam
    # while making it mathematically impossible to touch surrounding pixels.
    inset = 9
    inner = Image.new("L", size, 0)
    ImageDraw.Draw(inner).rectangle(
        (left + inset, top + inset, right - inset - 1, bottom - inset - 1), fill=255
    )
    feathered = inner.filter(ImageFilter.GaussianBlur(radius=8))
    feathered_array = np.asarray(feathered, dtype=np.uint8)
    hard_array = np.asarray(hard, dtype=np.uint8)
    feathered_array = np.where(hard_array > 0, feathered_array, 0).astype(np.uint8)
    return hard, Image.fromarray(feathered_array, "L")


def prepare(source: Path, out_dir: Path) -> Path:
    source = source.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    image = load_rgb(source)
    width, height = image.size

    object_raster = cartesian_to_raster(OBJECT_CARTESIAN, height)
    crop_raster = cartesian_to_raster(CROP_CARTESIAN, height)
    if not (0 <= crop_raster[0] < crop_raster[2] <= width):
        raise ValueError(f"Crop x range {crop_raster} is outside image width {width}")
    if not (0 <= crop_raster[1] < crop_raster[3] <= height):
        raise ValueError(f"Crop y range {crop_raster} is outside image height {height}")

    crop = image.crop(crop_raster)
    crop_path = out_dir / CROP_NAME
    crop.save(crop_path)

    object_relative = relative_rect(object_raster, crop_raster)
    hard_mask, feather_mask = build_masks(crop.size, object_relative)
    feather_mask.save(out_dir / MASK_NAME)
    hard_mask.save(out_dir / "court_archive_folder_hard_mask.png")

    manifest: dict[str, Any] = {
        "version": 1,
        "stage": "prepared",
        "source": str(source),
        "source_sha256": sha256(source),
        "original_size": [width, height],
        "coordinate_system": "cartesian_bottom_left",
        "object_rect_cartesian": list(OBJECT_CARTESIAN),
        "object_rect_raster_top_left": list(object_raster),
        "crop_rect_cartesian": list(CROP_CARTESIAN),
        "crop_rect_raster_top_left": list(crop_raster),
        "crop_size": list(crop.size),
        "object_rect_in_crop": list(object_relative),
        "files": {
            "crop": CROP_NAME,
            "feather_mask": MASK_NAME,
            "hard_mask": "court_archive_folder_hard_mask.png",
            "ai_patch": AI_NAME,
            "registered_patch": REGISTERED_NAME,
            "difference_preview": DIFF_NAME,
            "final": FINAL_NAME,
        },
    }
    manifest_path = out_dir / MANIFEST_NAME
    save_json(manifest_path, manifest)
    print(f"Prepared crop: {crop_path}")
    print(f"Crop size: {crop.size[0]} x {crop.size[1]}")
    print(f"Object rect in crop: {object_relative}")
    print(f"Manifest: {manifest_path}")
    return crop_path


def normalize_to_canvas(image: Image.Image, target_size: tuple[int, int]) -> tuple[Image.Image, list[int]]:
    """Center-crop without distortion, then resize to the expected canvas."""
    image = image.convert("RGB")
    source_width, source_height = image.size
    target_width, target_height = target_size
    source_ratio = source_width / source_height
    target_ratio = target_width / target_height

    if source_ratio > target_ratio:
        crop_width = round(source_height * target_ratio)
        left = (source_width - crop_width) // 2
        box = (left, 0, left + crop_width, source_height)
    else:
        crop_height = round(source_width / target_ratio)
        top = (source_height - crop_height) // 2
        box = (0, top, source_width, top + crop_height)

    normalized = image.crop(box).resize(target_size, Image.Resampling.LANCZOS)
    return normalized, list(box)


def scaled_center(image: Image.Image, scale: float, canvas_size: tuple[int, int]) -> tuple[Image.Image, Image.Image]:
    canvas_width, canvas_height = canvas_size
    scaled_width = max(1, round(image.width * scale))
    scaled_height = max(1, round(image.height * scale))
    resized = image.resize((scaled_width, scaled_height), Image.Resampling.BICUBIC)
    valid_resized = Image.new("L", (scaled_width, scaled_height), 255)

    canvas = Image.new("RGB", canvas_size, (0, 0, 0))
    valid = Image.new("L", canvas_size, 0)
    x = (canvas_width - scaled_width) // 2
    y = (canvas_height - scaled_height) // 2
    canvas.paste(resized, (x, y))
    valid.paste(valid_resized, (x, y))
    return canvas, valid


def shifted(image: Image.Image, dx: int, dy: int, fill: int | tuple[int, int, int] = 0) -> Image.Image:
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
    object_rect: tuple[int, int, int, int],
) -> dict[str, float]:
    """Estimate a small similarity drift using only unchanged surrounding context."""
    low_size = (140, 80)
    factor_x = reference.width / low_size[0]
    factor_y = reference.height / low_size[1]
    reference_low = reference.resize(low_size, Image.Resampling.LANCZOS)
    candidate_low = candidate.resize(low_size, Image.Resampling.LANCZOS)

    guard = np.ones((low_size[1], low_size[0]), dtype=bool)
    expansion = 24
    left, top, right, bottom = object_rect
    gx0 = max(0, int((left - expansion) / factor_x))
    gy0 = max(0, int((top - expansion) / factor_y))
    gx1 = min(low_size[0], int(np.ceil((right + expansion) / factor_x)))
    gy1 = min(low_size[1], int(np.ceil((bottom + expansion) / factor_y)))
    guard[gy0:gy1, gx0:gx1] = False
    guard[:2, :] = False
    guard[-2:, :] = False
    guard[:, :2] = False
    guard[:, -2:] = False

    ref_gray = grayscale(reference_low)
    ref_grad = gradient_magnitude(ref_gray)
    best: dict[str, float] | None = None

    for scale in np.arange(0.94, 1.061, 0.01):
        scaled_image, scaled_valid = scaled_center(candidate_low, float(scale), low_size)
        for dx_low in range(-7, 8):
            for dy_low in range(-5, 6):
                moved = shifted(scaled_image, dx_low, dy_low, (0, 0, 0))
                valid = np.asarray(shifted(scaled_valid, dx_low, dy_low, 0), dtype=np.uint8) > 0
                comparison = guard & valid
                if comparison.sum() < guard.sum() * 0.72:
                    continue

                cand_gray = grayscale(moved)
                cand_grad = gradient_magnitude(cand_gray)

                # Remove global brightness differences before comparing layout.
                ref_values = ref_gray[comparison]
                cand_values = cand_gray[comparison]
                ref_norm = (ref_values - ref_values.mean()) / max(ref_values.std(), 1e-4)
                cand_norm = (cand_values - cand_values.mean()) / max(cand_values.std(), 1e-4)
                intensity_error = float(np.mean((ref_norm - cand_norm) ** 2))

                ref_gradient = ref_grad[comparison]
                cand_gradient = cand_grad[comparison]
                gradient_error = float(
                    np.mean(
                        (
                            ref_gradient / max(ref_gradient.mean(), 1e-4)
                            - cand_gradient / max(cand_gradient.mean(), 1e-4)
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

    if best is None:
        return {"scale": 1.0, "dx": 0.0, "dy": 0.0, "score": -1.0}
    return best


def apply_registration(image: Image.Image, registration: dict[str, float], size: tuple[int, int]) -> Image.Image:
    scaled_image, _ = scaled_center(image, registration["scale"], size)
    return shifted(
        scaled_image,
        round(registration["dx"]),
        round(registration["dy"]),
        (0, 0, 0),
    )


def difference_preview(reference: Image.Image, edited: Image.Image) -> Image.Image:
    ref = np.asarray(reference, dtype=np.int16)
    out = np.asarray(edited, dtype=np.int16)
    diff = np.abs(out - ref).max(axis=2)
    preview = np.zeros((reference.height, reference.width, 3), dtype=np.uint8)
    preview[..., 0] = np.clip(diff * 4, 0, 255).astype(np.uint8)
    preview[..., 1] = np.clip(diff, 0, 255).astype(np.uint8)
    return Image.fromarray(preview, "RGB")


def compose(source: Path, ai_patch: Path, out_dir: Path) -> Path:
    source = source.resolve()
    ai_patch = ai_patch.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / MANIFEST_NAME
    if not manifest_path.exists():
        prepare(source, out_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if sha256(source) != manifest["source_sha256"]:
        raise ValueError("Source image differs from the one recorded during prepare")

    original = load_rgb(source)
    crop_rect = tuple(manifest["crop_rect_raster_top_left"])
    object_rect = tuple(manifest["object_rect_raster_top_left"])
    object_relative = tuple(manifest["object_rect_in_crop"])
    reference_crop = original.crop(crop_rect)

    raw_ai = load_rgb(ai_patch)
    raw_ai_size = list(raw_ai.size)
    normalized, normalization_box = normalize_to_canvas(raw_ai, reference_crop.size)
    registration = estimate_registration(reference_crop, normalized, object_relative)
    registered = apply_registration(normalized, registration, reference_crop.size)
    registered_path = out_dir / REGISTERED_NAME
    registered.save(registered_path)

    feather = np.asarray(Image.open(out_dir / MASK_NAME).convert("L"), dtype=np.float32) / 255.0
    alpha = feather[..., None]
    reference_array = np.asarray(reference_crop, dtype=np.float32)
    registered_array = np.asarray(registered, dtype=np.float32)
    composed_crop = np.clip(
        registered_array * alpha + reference_array * (1.0 - alpha), 0, 255
    ).round().astype(np.uint8)

    final_array = np.asarray(original, dtype=np.uint8).copy()
    left, top, right, bottom = crop_rect
    final_array[top:bottom, left:right] = composed_crop
    final = Image.fromarray(final_array, "RGB")

    # Hard proof: outside the authorized object rectangle every channel must
    # remain byte-for-byte identical to the source.
    original_array = np.asarray(original, dtype=np.uint8)
    allowed = np.zeros((original.height, original.width), dtype=bool)
    obj_left, obj_top, obj_right, obj_bottom = object_rect
    allowed[obj_top:obj_bottom, obj_left:obj_right] = True
    absolute_diff = np.abs(final_array.astype(np.int16) - original_array.astype(np.int16))
    outside_values = absolute_diff[~allowed]
    outside_nonzero_channels = int(np.count_nonzero(outside_values))
    outside_max_difference = int(outside_values.max(initial=0))
    if outside_nonzero_channels != 0 or outside_max_difference != 0:
        raise AssertionError("Pixels outside the authorized object rectangle changed")

    final_path = out_dir / FINAL_NAME
    final.save(final_path)
    difference_preview(original, final).save(out_dir / DIFF_NAME)

    manifest.update(
        {
            "stage": "composed",
            "ai_patch": str(ai_patch),
            "ai_patch_size": raw_ai_size,
            "normalization_crop_box": normalization_box,
            "registration": registration,
            "verification": {
                "final_size": list(final.size),
                "outside_object_nonzero_channels": outside_nonzero_channels,
                "outside_object_max_channel_difference": outside_max_difference,
                "outside_object_pixels_bit_identical": True,
            },
            "output_sha256": sha256(final_path),
        }
    )
    save_json(manifest_path, manifest)

    print(f"AI input size: {raw_ai_size[0]} x {raw_ai_size[1]}")
    print(
        "Registration: "
        f"scale={registration['scale']:.3f}, dx={registration['dx']:.0f}, "
        f"dy={registration['dy']:.0f}, score={registration['score']:.6f}"
    )
    print(f"Final size: {final.width} x {final.height}")
    print(f"Outside-object differing channels: {outside_nonzero_channels}")
    print(f"Outside-object maximum difference: {outside_max_difference}")
    print(f"Final: {final_path}")
    return final_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "compose"))
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR_DEFAULT)
    parser.add_argument("--ai-patch", type=Path, default=OUT_DIR_DEFAULT / AI_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "prepare":
        prepare(args.source, args.out_dir)
    else:
        compose(args.source, args.ai_patch, args.out_dir)


if __name__ == "__main__":
    main()
