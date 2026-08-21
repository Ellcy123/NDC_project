#!/usr/bin/env python3
"""Prepare, compose, and verify coordinate-locked raster edit jobs.

The image model edits a padded crop. This helper owns all geometry and proves
that pixels outside the approved hard mask remain byte-identical to the source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
DEFAULT_OUTPUT_SUFFIX = "_coordinate_edit.png"


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
    source_ratio = source_width / source_height
    target_ratio = target_width / target_height

    if source_ratio > target_ratio:
        crop_width = max(1, round(source_height * target_ratio))
        left = (source_width - crop_width) // 2
        box = (left, 0, left + crop_width, source_height)
    else:
        crop_height = max(1, round(source_width / target_ratio))
        top = (source_height - crop_height) // 2
        box = (0, top, source_width, top + crop_height)
    return image.crop(box).resize(target_size, Image.Resampling.LANCZOS), list(box)


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

    prepare_parser = subparsers.add_parser("prepare", help="Create crop, masks, and manifest")
    prepare_parser.add_argument("--source", type=Path, required=True)
    prepare_parser.add_argument("--edit-rect", type=int, nargs=4, required=True, metavar=("LEFT", "Y1", "RIGHT", "Y2"))
    prepare_parser.add_argument("--crop-rect", type=int, nargs=4, metavar=("LEFT", "Y1", "RIGHT", "Y2"))
    prepare_parser.add_argument("--origin", choices=("top-left", "bottom-left"), default="top-left")
    prepare_parser.add_argument("--padding", type=int, default=96)
    prepare_parser.add_argument("--feather", type=int, default=8)
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
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
