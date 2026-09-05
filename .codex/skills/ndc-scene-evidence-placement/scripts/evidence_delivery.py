#!/usr/bin/env python3
"""Package and verify Unity-ready NDC scene evidence assets.

This helper owns deterministic derivatives only. It never generates artwork and
never writes into the Unity EVIDENCE directory. The accepted full scene remains
the coordinate truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageOps


MANIFEST_NAME = "delivery_manifest.json"
VERIFICATION_NAME = "delivery_verification.json"
SCENE_NAME = "scene_with_item.png"
XY_NAME = "XYposition.txt"
PATCH_NAME = "ItemStaticData.patch.json"
OVERLAY_NAME = "position_overlay.png"

Rect = tuple[int, int, int, int]
ICON_FINAL_SIZE = (130, 130)
ICON_FINAL_SAFE_RECT: Rect = (7, 7, 122, 122)


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_preserving_mode(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        if image.mode not in ("RGB", "RGBA"):
            return image.convert("RGBA" if "A" in image.getbands() else "RGB")
        return image.copy()


def as_rect(values: Iterable[int]) -> Rect:
    left, top, right, bottom = (int(value) for value in values)
    return left, top, right, bottom


def validate_rect(rect: Rect, width: int, height: int) -> None:
    left, top, right, bottom = rect
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(
            f"Map rectangle {rect} is empty or outside the {width}x{height} scene"
        )


def expand_rect(rect: Rect, padding: int, width: int, height: int) -> Rect:
    if padding < 0:
        raise ValueError("--map-padding must be non-negative")
    return (
        max(0, rect[0] - padding),
        max(0, rect[1] - padding),
        min(width, rect[2] + padding),
        min(height, rect[3] + padding),
    )


def validate_stem(value: str, label: str) -> str:
    stem = value.strip()
    if not stem:
        raise ValueError(f"{label} is empty")
    if Path(stem).suffix or "/" in stem or "\\" in stem:
        raise ValueError(f"{label} must be a filename stem without path or extension")
    return stem


def normalize_folder_path(value: str) -> str:
    normalized = value.strip().replace("/", "\\").strip("\\")
    if not normalized:
        raise ValueError("folderPath is empty")
    if normalized.startswith("..") or "\\..\\" in f"\\{normalized}\\":
        raise ValueError("folderPath may not contain parent traversal")
    return normalized


def image_array(image: Image.Image) -> bytes:
    return image.convert("RGBA").tobytes()


def images_equal(first: Image.Image, second: Image.Image) -> bool:
    return first.size == second.size and image_array(first) == image_array(second)


def build_contour_map(
    parent_crop: Image.Image, contour_mask: Image.Image | None
) -> Image.Image:
    """Return an exact rectangular crop or an RGBA contour-masked crop."""
    if contour_mask is None:
        return parent_crop.copy()
    if contour_mask.size != parent_crop.size:
        raise ValueError("Contour mask crop and parent crop dimensions differ")
    rgba = parent_crop.convert("RGBA")
    mask = contour_mask.convert("L")
    cleaned: list[tuple[int, int, int, int]] = []
    for pixel, mask_alpha in zip(rgba.getdata(), mask.getdata()):
        red, green, blue, source_alpha = pixel
        alpha = source_alpha * mask_alpha // 255
        cleaned.append((red, green, blue, alpha) if alpha else (0, 0, 0, 0))
    output = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    output.putdata(cleaned)
    return output


def map_matches_parent_pixels(parent_crop: Image.Image, map_sprite: Image.Image) -> bool:
    """Validate a legacy rectangle or a transparent contour against its parent."""
    if parent_crop.size != map_sprite.size:
        return False
    if map_sprite.mode != "RGBA" or map_sprite.getchannel("A").getextrema()[0] > 0:
        return images_equal(parent_crop, map_sprite)
    parent_rgba = parent_crop.convert("RGBA")
    for parent_pixel, map_pixel in zip(parent_rgba.getdata(), map_sprite.getdata()):
        red, green, blue, alpha = map_pixel
        if alpha == 0:
            if (red, green, blue) != (0, 0, 0):
                return False
            continue
        if (red, green, blue) != parent_pixel[:3] or alpha > parent_pixel[3]:
            return False
    return True


def composite_map(base: Image.Image, map_sprite: Image.Image, xy: tuple[int, int]) -> Image.Image:
    if map_sprite.mode == "RGBA" and map_sprite.getchannel("A").getextrema()[0] == 0:
        result = base.convert("RGBA")
        result.alpha_composite(map_sprite.convert("RGBA"), xy)
        return result
    result = base.copy()
    result.paste(map_sprite, xy)
    return result


def nonzero_pixel_count(image: Image.Image) -> int:
    histogram = image.convert("L").histogram()
    return image.width * image.height - histogram[0]


def changed_pixel_mask(first: Image.Image, second: Image.Image) -> Image.Image:
    difference = ImageChops.difference(first.convert("RGBA"), second.convert("RGBA"))
    channels = difference.split()
    changed = channels[0]
    for channel in channels[1:]:
        changed = ImageChops.lighter(changed, channel)
    return changed


def load_mask(path: Path, scene_size: tuple[int, int], rect: Rect) -> Image.Image:
    with Image.open(path) as image:
        mask = image.convert("L")
    crop_size = (rect[2] - rect[0], rect[3] - rect[1])
    if mask.size == crop_size:
        source_sized = Image.new("L", scene_size, 0)
        source_sized.paste(mask, (rect[0], rect[1]))
        mask = source_sized
    elif mask.size != scene_size:
        raise ValueError(
            "Mask must match either the full scene or the exported map rectangle"
        )
    if nonzero_pixel_count(mask) == 0:
        raise ValueError(f"Mask is empty: {path}")
    return mask


def load_source_sized_mask(path: Path, scene_size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as image:
        mask = image.convert("L")
    if mask.size != scene_size:
        raise ValueError(
            "Automatic coordinate export requires an authorization mask matching the full scene"
        )
    if nonzero_pixel_count(mask) == 0:
        raise ValueError(f"Mask is empty: {path}")
    return mask


def rect_mask(size: tuple[int, int], rect: Rect) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle(
        (rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=255
    )
    return mask


def copy_png(source: Path, output: Path) -> None:
    if source.suffix.lower() != ".png":
        raise ValueError(f"Runtime raster assets must use PNG: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output)


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    if "A" not in image.getbands():
        return (0, 0, image.width, image.height)
    return image.getchannel("A").getbbox()


def normalize_transparent_rgb(image: Image.Image) -> Image.Image:
    red, green, blue, alpha = image.convert("RGBA").split()
    transparent = alpha.point(lambda value: 255 if value == 0 else 0)
    for channel in (red, green, blue):
        channel.paste(0, mask=transparent)
    return Image.merge("RGBA", (red, green, blue, alpha))


def premultiplied_resize(
    image: Image.Image, size: tuple[int, int], resample: Image.Resampling
) -> Image.Image:
    resized = image.convert("RGBA").convert("RGBa").resize(size, resample)
    return normalize_transparent_rgb(resized.convert("RGBA"))


def extract_detail(
    final: Image.Image,
    rect: Rect,
    cutout_mask: Image.Image,
    padding: int,
) -> Image.Image:
    if padding < 0:
        raise ValueError("--detail-padding must be non-negative")
    crop = final.crop(rect).convert("RGBA")
    alpha = cutout_mask.crop(rect)
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("Cutout mask has no enabled pixels inside --map-rect")
    crop.putalpha(alpha)
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(crop.width, bbox[2] + padding)
    bottom = min(crop.height, bbox[3] + padding)
    return crop.crop((left, top, right, bottom))


def derive_icon(detail: Image.Image, size: int, content_max: int) -> Image.Image:
    """Legacy-only deterministic derivation for audited old packages."""
    if size != 130:
        raise ValueError("Legacy-derived runtime Icons must still be exactly 130x130")
    if not 1 <= content_max <= 115:
        raise ValueError("--icon-content-max must be between 1 and 115")
    rgba = detail.convert("RGBA")
    bbox = alpha_bbox(rgba)
    if bbox is None:
        raise ValueError("Detail image is fully transparent")
    subject = rgba.crop(bbox)
    scale = min(content_max / subject.width, content_max / subject.height, 1.0)
    new_size = (
        max(1, round(subject.width * scale)),
        max(1, round(subject.height * scale)),
    )
    subject = premultiplied_resize(subject, new_size, Image.Resampling.LANCZOS)
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    icon.alpha_composite(
        subject, ((size - subject.width) // 2, (size - subject.height) // 2)
    )
    return icon


def create_overlay(scene: Image.Image, rect: Rect, item_id: str) -> Image.Image:
    overlay = scene.convert("RGBA")
    draw = ImageDraw.Draw(overlay)
    width = max(3, round(max(scene.size) / 900))
    for offset in range(width):
        draw.rectangle(
            (
                rect[0] - offset,
                rect[1] - offset,
                rect[2] - 1 + offset,
                rect[3] - 1 + offset,
            ),
            outline=(255, 0, 220, 255),
        )
    label_y = max(0, rect[1] - 18)
    draw.rectangle(
        (rect[0], label_y, rect[0] + max(92, len(item_id) * 9), label_y + 17),
        fill=(30, 10, 35, 220),
    )
    draw.text(
        (rect[0] + 4, label_y + 2),
        f"item {item_id}: {rect[0]},{rect[1]}",
        fill=(255, 255, 255, 255),
    )
    return overlay


def read_base_verification(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.is_file():
        raise FileNotFoundError(path)
    report = json.loads(path.read_text(encoding="utf-8"))
    passed = report.get("passed")
    if passed is None:
        passed = (report.get("verification") or {}).get(
            "outside_mask_pixels_bit_identical"
        )
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "passed": bool(passed),
    }


def inspect_runtime_icon(path: Path) -> dict[str, Any]:
    image = load_preserving_mode(path)
    rgba = image.convert("RGBA")
    bbox = alpha_bbox(rgba)
    transparent = rgba.getchannel("A").point(
        lambda value: 255 if value == 0 else 0
    )
    red, green, blue, _ = rgba.split()
    rgb_nonzero = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    transparent_rgb_nonzero = nonzero_pixel_count(
        ImageChops.multiply(rgb_nonzero, transparent)
    )
    inside_safe = bool(
        bbox
        and ICON_FINAL_SAFE_RECT[0] <= bbox[0]
        and ICON_FINAL_SAFE_RECT[1] <= bbox[1]
        and bbox[2] <= ICON_FINAL_SAFE_RECT[2]
        and bbox[3] <= ICON_FINAL_SAFE_RECT[3]
    )
    checks = {
        "sizeIs130": image.size == ICON_FINAL_SIZE,
        "modeIsRGBA": image.mode == "RGBA",
        "contentExists": bbox is not None,
        "contentBounds": list(bbox) if bbox else None,
        "safeRect": list(ICON_FINAL_SAFE_RECT),
        "contentInside115SafeRect": inside_safe,
        "transparentRgbNonzeroPixels": transparent_rgb_nonzero,
    }
    checks["passed"] = all(
        (
            checks["sizeIs130"],
            checks["modeIsRGBA"],
            checks["contentExists"],
            checks["contentInside115SafeRect"],
            checks["transparentRgbNonzeroPixels"] == 0,
        )
    )
    return checks


def make_icon_report(
    image_path: Path,
    checks: dict[str, Any],
    *,
    method: str,
    sources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "ndc-icon",
        "method": method,
        "artifact": {
            "path": str(image_path.resolve()),
            "sha256": sha256(image_path),
            "size": list(ICON_FINAL_SIZE),
            "mode": "RGBA",
        },
        "sources": sources or {},
        "checks": checks,
        "passed": bool(checks.get("passed")),
    }


def read_icon_verification(path: Path, icon_path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    report = json.loads(path.read_text(encoding="utf-8"))
    checks = inspect_runtime_icon(icon_path)
    artifact = report.get("artifact") or {}
    artifact_hash_matches = artifact.get("sha256") == sha256(icon_path)
    passed = bool(
        report.get("passed")
        and report.get("kind") == "ndc-icon"
        and artifact_hash_matches
        and checks.get("passed")
    )
    if not passed:
        raise ValueError(
            "Icon verification must be a passing ndc-icon report for the exact "
            "130x130 RGBA source bytes"
        )
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "kind": report.get("kind"),
        "artifactSha256Matches": artifact_hash_matches,
        "checks": checks,
        "passed": passed,
    }


def scene_checks(
    source: Image.Image | None,
    final: Image.Image,
    mask: Image.Image,
    rect: Rect,
    map_crop: Image.Image,
) -> dict[str, Any]:
    rect_limit = rect_mask(final.size, rect)
    mask_outside = ImageChops.multiply(mask, ImageOps.invert(rect_limit))
    mask_outside_rect = nonzero_pixel_count(mask_outside)
    checks: dict[str, Any] = {
        "mapCropMatchesFinalScenePixels": map_matches_parent_pixels(
            final.crop(rect), map_crop
        ),
        "mapShape": (
            "irregular-alpha"
            if map_crop.mode == "RGBA" and map_crop.getchannel("A").getextrema()[0] == 0
            else "rectangular-exact"
        ),
        "authorizationPixelsOutsideMapRect": mask_outside_rect,
        "authorizationContainedByMapRect": mask_outside_rect == 0,
    }
    if source is None:
        checks.update(
            {
                "sourceProvided": False,
                "sourceFinalSizeMatches": None,
                "sourceFinalModeMatches": None,
                "changedPixelsInsideAuthorization": None,
                "changedPixelsOutsideAuthorization": None,
                "changedPixelsOutsideMapRect": None,
                "changedPixelsContainedByMapRect": None,
                "outsideAuthorizationByteIdentical": None,
                "mapCropReconstructsFinalFromSource": None,
            }
        )
        return checks

    size_matches = source.size == final.size
    mode_matches = source.mode == final.mode
    checks["sourceProvided"] = True
    checks["sourceFinalSizeMatches"] = size_matches
    checks["sourceFinalModeMatches"] = mode_matches
    if not size_matches:
        checks.update(
            {
                "changedPixelsInsideAuthorization": None,
                "changedPixelsOutsideAuthorization": None,
                "changedPixelsOutsideMapRect": None,
                "changedPixelsContainedByMapRect": False,
                "outsideAuthorizationByteIdentical": False,
                "mapCropReconstructsFinalFromSource": False,
            }
        )
        return checks

    changed = changed_pixel_mask(source, final)
    changed_inside = nonzero_pixel_count(ImageChops.multiply(changed, mask))
    changed_outside = nonzero_pixel_count(
        ImageChops.multiply(changed, ImageOps.invert(mask))
    )
    changed_outside_rect = nonzero_pixel_count(
        ImageChops.multiply(changed, ImageOps.invert(rect_limit))
    )
    reconstructed = composite_map(source, map_crop, (rect[0], rect[1]))
    checks.update(
        {
            "changedPixelsInsideAuthorization": changed_inside,
            "changedPixelsOutsideAuthorization": changed_outside,
            "changedPixelsOutsideMapRect": changed_outside_rect,
            "changedPixelsContainedByMapRect": changed_outside_rect == 0,
            "outsideAuthorizationByteIdentical": changed_outside == 0,
            "mapCropReconstructsFinalFromSource": images_equal(
                reconstructed, final.convert(reconstructed.mode)
            ),
        }
    )
    return checks


def checks_pass(checks: dict[str, Any], base: dict[str, Any] | None) -> bool:
    if not checks["mapCropMatchesFinalScenePixels"]:
        return False
    if checks["sourceProvided"]:
        if not all(
            (
                checks["sourceFinalSizeMatches"],
                checks["sourceFinalModeMatches"],
                checks["changedPixelsContainedByMapRect"],
                checks["outsideAuthorizationByteIdentical"],
                checks["mapCropReconstructsFinalFromSource"],
            )
        ):
            return False
    elif not checks["authorizationContainedByMapRect"]:
        return False
    if base is not None and not base["passed"]:
        return False
    return True


def package(args: argparse.Namespace) -> Path:
    final_path = args.final_scene.resolve()
    if final_path.suffix.lower() != ".png":
        raise ValueError("The accepted full scene must be a lossless PNG")
    final = load_preserving_mode(final_path)

    mask_path = args.authorization_mask.resolve() if args.authorization_mask else None
    full_authorization_mask = (
        load_source_sized_mask(mask_path, final.size) if mask_path else None
    )
    map_shape_mask_path = args.map_shape_mask.resolve() if args.map_shape_mask else None
    full_map_shape_mask = (
        load_source_sized_mask(map_shape_mask_path, final.size)
        if map_shape_mask_path
        else None
    )
    source_path = args.source_scene.resolve() if args.source_scene else None
    source = load_preserving_mode(source_path) if source_path else None
    if source is not None and source.size != final.size:
        raise ValueError("Source and final scene dimensions differ")
    changed = changed_pixel_mask(source, final) if source is not None else None
    scene_has_changes = bool(changed is not None and nonzero_pixel_count(changed))

    if args.map_rect:
        rect = as_rect(args.map_rect)
        map_rect_method = "audited-manual-override"
    elif scene_has_changes and changed is not None:
        bbox = changed.getbbox()
        if bbox is None:
            raise AssertionError("Changed-pixel mask unexpectedly has no bounds")
        rect = expand_rect(bbox, args.map_padding, final.width, final.height)
        map_rect_method = "changed-pixel-bounds"
    else:
        if full_authorization_mask is None:
            raise ValueError(
                "Automatic coordinates require changed source/final pixels or a "
                "source-sized --authorization-mask; otherwise use an audited --map-rect"
            )
        bbox = full_authorization_mask.getbbox()
        if bbox is None:
            raise ValueError("Authorization mask is empty")
        rect = expand_rect(bbox, args.map_padding, final.width, final.height)
        map_rect_method = "authorization-mask-fallback"
    validate_rect(rect, final.width, final.height)

    if scene_has_changes and mask_path is None:
        raise ValueError("Changed scenes require --authorization-mask")
    if scene_has_changes and args.base_verification is None:
        raise ValueError("Changed scenes require --base-verification from the coordinate edit")

    map_stem = validate_stem(args.map_stem, "mapSpritePath")
    detail_stem = validate_stem(args.detail_stem, "desSpritePath")
    if args.omit_icon:
        if any(
            (
                args.icon_stem,
                args.icon_image,
                args.icon_verification,
                args.allow_legacy_derived_icon,
            )
        ):
            raise ValueError(
                "--omit-icon cannot be combined with Icon paths, stems, or legacy derivation"
            )
        icon_stem = None
    else:
        if not args.icon_stem:
            raise ValueError("Production packages with an Icon require --icon-stem")
        icon_stem = validate_stem(args.icon_stem, "iconPath")
        if len({map_stem, detail_stem, icon_stem}) != 3:
            raise ValueError("Map, detail, and icon stems must be distinct")
        if args.icon_image and args.allow_legacy_derived_icon:
            raise ValueError(
                "Use an approved --icon-image or explicit legacy derivation, not both"
            )
        if args.icon_verification and not args.icon_image:
            raise ValueError("--icon-verification requires --icon-image")
        if not args.icon_image and not args.allow_legacy_derived_icon:
            raise ValueError(
                "Production packaging requires --icon-image plus --icon-verification; "
                "use --omit-icon only when iconPath is intentionally absent"
            )
    folder_path = normalize_folder_path(args.folder_path)

    if bool(args.detail_image) == bool(args.cutout_mask):
        raise ValueError("Supply exactly one of --detail-image or --cutout-mask")

    output_dir = args.output_dir.resolve()
    unity_evidence_root = Path(
        r"D:\NDC\Assets\Resources\Art\Scene\EVIDENCE"
    ).resolve()
    if output_dir == unity_evidence_root or output_dir.is_relative_to(unity_evidence_root):
        raise ValueError(
            "Refusing to stage directly inside Unity EVIDENCE; use image/edit_jobs first"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / MANIFEST_NAME
    if manifest_path.exists() and not args.force:
        raise FileExistsError(
            f"{manifest_path} already exists; use a new delivery directory or --force"
        )

    scene_output = output_dir / SCENE_NAME
    map_output = output_dir / f"{map_stem}.png"
    detail_output = output_dir / f"{detail_stem}.png"
    icon_output = output_dir / f"{icon_stem}.png" if icon_stem else None
    icon_verification_output = (
        output_dir / f"{icon_stem}_verification.json" if icon_stem else None
    )
    xy_output = output_dir / XY_NAME
    patch_output = output_dir / PATCH_NAME
    overlay_output = output_dir / OVERLAY_NAME

    known_outputs = [
        scene_output,
        map_output,
        detail_output,
        xy_output,
        patch_output,
        overlay_output,
        output_dir / VERIFICATION_NAME,
    ]
    if icon_output:
        known_outputs.append(icon_output)
    if icon_verification_output:
        known_outputs.append(icon_verification_output)
    existing_outputs = [path for path in known_outputs if path.exists()]
    if existing_outputs and not args.force:
        formatted = ", ".join(str(path) for path in existing_outputs)
        raise FileExistsError(
            f"Staged outputs already exist; use a new directory or --force: {formatted}"
        )

    copy_png(final_path, scene_output)
    map_crop = build_contour_map(
        final.crop(rect),
        full_map_shape_mask.crop(rect) if full_map_shape_mask is not None else None,
    )
    map_crop.save(map_output)
    saved_map = load_preserving_mode(map_output)

    mask = (
        full_authorization_mask
        if full_authorization_mask is not None
        else load_mask(mask_path, final.size, rect)
        if mask_path
        else rect_mask(final.size, rect)
    )

    if args.detail_image:
        detail_source = args.detail_image.resolve()
        copy_png(detail_source, detail_output)
        detail_provenance: dict[str, Any] = {
            "method": "approved-detail-image",
            "source": str(detail_source),
            "sourceSha256": sha256(detail_source),
        }
    else:
        cutout_path = args.cutout_mask.resolve()
        cutout_mask = load_mask(cutout_path, final.size, rect)
        cutout_outside = ImageChops.multiply(
            cutout_mask, ImageOps.invert(rect_mask(final.size, rect))
        )
        if nonzero_pixel_count(cutout_outside):
            raise ValueError("Cutout mask contains enabled pixels outside --map-rect")
        detail = extract_detail(final, rect, cutout_mask, args.detail_padding)
        detail.save(detail_output)
        detail_provenance = {
            "method": "accepted-scene-alpha-cutout",
            "source": str(final_path),
            "mask": str(cutout_path),
            "maskSha256": sha256(cutout_path),
        }

    detail = load_preserving_mode(detail_output)
    if detail.width <= 0 or detail.height <= 0 or alpha_bbox(detail) is None:
        raise ValueError("Standalone detail image is empty or fully transparent")

    if args.omit_icon:
        icon_provenance: dict[str, Any] = {
            "omitted": True,
            "method": "runtime-iconPath-intentionally-absent",
        }
    elif args.icon_image:
        if args.icon_verification is None:
            raise ValueError("Approved Icons require --icon-verification")
        assert icon_output is not None and icon_verification_output is not None
        icon_source = args.icon_image.resolve()
        source_verification = read_icon_verification(
            args.icon_verification.resolve(), icon_source
        )
        copy_png(icon_source, icon_output)
        shutil.copy2(args.icon_verification.resolve(), icon_verification_output)
        staged_checks = inspect_runtime_icon(icon_output)
        if not staged_checks.get("passed"):
            raise ValueError("Staged Icon failed the fixed 130x130/115px-safe checks")
        icon_provenance = {
            "omitted": False,
            "method": "approved-icon-image",
            "source": str(icon_source),
            "sourceSha256": sha256(icon_source),
            "verification": source_verification,
            "checks": staged_checks,
        }
    else:
        assert args.allow_legacy_derived_icon
        assert icon_output is not None and icon_verification_output is not None
        icon = derive_icon(detail, args.icon_size, args.icon_content_max)
        icon.save(icon_output)
        staged_checks = inspect_runtime_icon(icon_output)
        legacy_report = make_icon_report(
            icon_output,
            staged_checks,
            method="explicit-legacy-detail-derivation",
            sources={"detail": {"path": str(detail_output), "sha256": sha256(detail_output)}},
        )
        save_json(icon_verification_output, legacy_report)
        icon_provenance = {
            "omitted": False,
            "method": "explicit-legacy-derived-from-detail",
            "size": args.icon_size,
            "contentMax": args.icon_content_max,
            "checks": staged_checks,
        }

    x, y = rect[0], rect[1]
    z = str(args.z)
    try:
        float(z)
    except ValueError as exc:
        raise ValueError("--z must be numeric") from exc
    xy_output.write_text(f"{map_stem} {x},{y}\n", encoding="ascii")
    item_patch = {
        "id": str(args.item_id),
        "folderPath": folder_path,
        "desSpritePath": detail_stem,
        "mapSpritePath": map_stem,
        "Position": [str(x), str(y), z],
    }
    if icon_stem:
        item_patch["iconPath"] = icon_stem
    save_json(patch_output, item_patch)
    create_overlay(final, rect, str(args.item_id)).save(overlay_output)

    base_verification = read_base_verification(
        args.base_verification.resolve() if args.base_verification else None
    )
    checks = scene_checks(source, final, mask, rect, saved_map)
    package_passed = checks_pass(checks, base_verification)
    if not icon_provenance.get("omitted"):
        package_passed = package_passed and bool(
            (icon_provenance.get("checks") or {}).get("passed")
        )

    artifact_paths = {
        "fullScene": scene_output,
        "mapSprite": map_output,
        "detailSprite": detail_output,
        "xyCompatibility": xy_output,
        "itemStaticDataPatch": patch_output,
        "positionOverlay": overlay_output,
    }
    if icon_output is not None and icon_verification_output is not None:
        artifact_paths["iconSprite"] = icon_output
        artifact_paths["iconVerification"] = icon_verification_output
    artifact_records = {
        key: {"path": str(path), "sha256": sha256(path)}
        for key, path in artifact_paths.items()
    }

    manifest: dict[str, Any] = {
        "version": 2,
        "stage": "packaged",
        "passed": package_passed,
        "coordinateSystem": {
            "origin": "top-left",
            "xAxis": "right",
            "yAxis": "down",
            "unit": "pixel",
            "sceneWidth": final.width,
            "sceneHeight": final.height,
        },
        "sourceScene": (
            {"path": str(source_path), "sha256": sha256(source_path)}
            if source_path
            else None
        ),
        "acceptedFinalScene": {
            "path": str(final_path),
            "sha256": sha256(final_path),
            "mode": final.mode,
            "size": [final.width, final.height],
        },
        "authorizationMask": (
            {"path": str(mask_path), "sha256": sha256(mask_path)}
            if mask_path
            else {"path": None, "method": "map-rect-fallback"}
        ),
        "baseVerification": base_verification,
        "item": {
            "id": str(args.item_id),
            "sceneId": str(args.scene_id),
            "folderPath": folder_path,
        },
        "mapCrop": {
            "method": map_rect_method,
            "x": x,
            "y": y,
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1],
            "rect": list(rect),
            "shape": checks.get("mapShape"),
            "shapeMask": (
                {
                    "path": str(map_shape_mask_path),
                    "sha256": sha256(map_shape_mask_path),
                }
                if map_shape_mask_path
                else None
            ),
        },
        "detail": {
            "provenance": detail_provenance,
            "mode": detail.mode,
            "size": [detail.width, detail.height],
            "hasAlpha": "A" in detail.getbands(),
        },
        "icon": icon_provenance,
        "unityDraft": item_patch,
        "checks": checks,
        "artifacts": artifact_records,
    }
    save_json(manifest_path, manifest)
    report = verify_manifest(manifest_path, write_report=True)
    if not report["passed"]:
        raise SystemExit(2)

    print("Delivery: PASS")
    print(f"Item: {args.item_id}; scene: {args.scene_id}")
    print(f"Position: {x},{y},{z}")
    print(f"Map crop: {rect[2] - rect[0]} x {rect[3] - rect[1]}")
    print(f"Output: {output_dir}")
    print(f"Manifest: {manifest_path}")
    return manifest_path


def verify_manifest(manifest_path: Path, write_report: bool) -> dict[str, Any]:
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    artifact_checks: dict[str, Any] = {}
    for name, record in (manifest.get("artifacts") or {}).items():
        path = Path(record["path"])
        exists = path.is_file()
        hash_matches = exists and sha256(path) == record.get("sha256")
        artifact_checks[name] = {
            "path": str(path),
            "exists": exists,
            "hashMatches": hash_matches,
        }
        if not exists:
            failures.append(f"Missing artifact: {name}")
        elif not hash_matches:
            failures.append(f"Artifact hash changed: {name}")

    artifacts = manifest.get("artifacts") or {}
    scene_record = artifacts.get("fullScene")
    map_record = artifacts.get("mapSprite")
    patch_record = artifacts.get("itemStaticDataPatch")
    xy_record = artifacts.get("xyCompatibility")
    crop = manifest.get("mapCrop") or {}
    rect = as_rect(crop.get("rect", [])) if len(crop.get("rect", [])) == 4 else None

    map_matches_scene = False
    if scene_record and map_record and rect:
        scene_path = Path(scene_record["path"])
        map_path = Path(map_record["path"])
        if scene_path.is_file() and map_path.is_file():
            scene = load_preserving_mode(scene_path)
            validate_rect(rect, scene.width, scene.height)
            map_matches_scene = map_matches_parent_pixels(
                scene.crop(rect), load_preserving_mode(map_path)
            )
    if not map_matches_scene:
        failures.append("Map Sprite no longer matches the accepted scene rectangle")

    unity_matches = False
    xy_matches = False
    unity = manifest.get("unityDraft") or {}
    if rect and patch_record and Path(patch_record["path"]).is_file():
        patch = json.loads(Path(patch_record["path"]).read_text(encoding="utf-8"))
        unity_matches = patch == unity and patch.get("Position", [])[:2] == [
            str(rect[0]),
            str(rect[1]),
        ]
    if not unity_matches:
        failures.append("ItemStaticData patch differs from the coordinate manifest")

    if rect and xy_record and Path(xy_record["path"]).is_file():
        expected = f"{unity.get('mapSpritePath')} {rect[0]},{rect[1]}\n"
        xy_matches = Path(xy_record["path"]).read_text(encoding="ascii") == expected
    if not xy_matches:
        failures.append("XYposition compatibility line differs from the manifest")

    icon_record = manifest.get("icon") or {}
    icon_omitted = bool(icon_record.get("omitted"))
    icon_checks: dict[str, Any] | None = None
    icon_verification_matches = False
    icon_sprite_record = artifacts.get("iconSprite")
    icon_verification_record = artifacts.get("iconVerification")
    if icon_omitted:
        icon_verification_matches = (
            "iconPath" not in unity
            and icon_sprite_record is None
            and icon_verification_record is None
        )
        if not icon_verification_matches:
            failures.append(
                "Icon is declared omitted but iconPath or Icon artifacts are still present"
            )
    else:
        if not unity.get("iconPath"):
            failures.append("Icon package is missing iconPath")
        if not icon_sprite_record or not icon_verification_record:
            failures.append("Icon package is missing its Sprite or verification artifact")
        else:
            icon_path = Path(icon_sprite_record["path"])
            icon_report_path = Path(icon_verification_record["path"])
            if icon_path.is_file():
                icon_checks = inspect_runtime_icon(icon_path)
                if not icon_checks.get("passed"):
                    failures.append(
                        "Icon no longer passes the fixed 130x130 RGBA/115px-safe checks"
                    )
            if icon_path.is_file() and icon_report_path.is_file():
                staged_icon_report = json.loads(
                    icon_report_path.read_text(encoding="utf-8")
                )
                icon_verification_matches = bool(
                    staged_icon_report.get("passed")
                    and staged_icon_report.get("kind") == "ndc-icon"
                    and (staged_icon_report.get("artifact") or {}).get("sha256")
                    == sha256(icon_path)
                )
            if not icon_verification_matches:
                failures.append(
                    "Icon verification report does not match the staged Icon bytes"
                )

    original_checks = manifest.get("checks") or {}
    original_passed = checks_pass(original_checks, manifest.get("baseVerification"))
    if not original_passed:
        failures.append("Original scene/package verification did not pass")

    report = {
        "manifest": str(manifest_path),
        "manifestSha256": sha256(manifest_path),
        "artifactChecks": artifact_checks,
        "mapSpriteMatchesScenePixels": map_matches_scene,
        "itemStaticDataMatchesManifest": unity_matches,
        "xyPositionMatchesManifest": xy_matches,
        "iconOmitted": icon_omitted,
        "iconChecks": icon_checks,
        "iconVerificationMatchesArtifact": icon_verification_matches,
        "originalSceneChecksPassed": original_passed,
        "failures": failures,
        "passed": not failures,
    }
    if write_report:
        save_json(manifest_path.parent / VERIFICATION_NAME, report)
    return report


def verify(args: argparse.Namespace) -> None:
    manifest_path = args.manifest.resolve()
    report = verify_manifest(manifest_path, write_report=True)
    print(f"Delivery verification: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Manifest: {manifest_path}")
    print(f"Report: {manifest_path.parent / VERIFICATION_NAME}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    if not report["passed"]:
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser(
        "package", help="Export and verify a staged scene-pickup package"
    )
    package_parser.add_argument("--source-scene", type=Path)
    package_parser.add_argument("--final-scene", type=Path, required=True)
    package_parser.add_argument("--authorization-mask", type=Path)
    package_parser.add_argument(
        "--map-shape-mask",
        type=Path,
        help="Optional source-sized silhouette mask for a preferred irregular RGBA Map",
    )
    package_parser.add_argument("--base-verification", type=Path)
    package_parser.add_argument(
        "--map-rect",
        type=int,
        nargs=4,
        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
    )
    package_parser.add_argument(
        "--map-padding",
        type=int,
        default=32,
        help="Stable scene pixels added around changed-pixel bounds (or the mask fallback)",
    )
    package_parser.add_argument("--item-id", required=True)
    package_parser.add_argument("--scene-id", required=True)
    package_parser.add_argument("--folder-path", required=True)
    package_parser.add_argument("--map-stem", required=True)
    package_parser.add_argument("--detail-stem", required=True)
    package_parser.add_argument("--icon-stem")
    package_parser.add_argument("--detail-image", type=Path)
    package_parser.add_argument("--cutout-mask", type=Path)
    package_parser.add_argument("--detail-padding", type=int, default=4)
    package_parser.add_argument("--icon-image", type=Path)
    package_parser.add_argument("--icon-verification", type=Path)
    package_parser.add_argument(
        "--omit-icon",
        action="store_true",
        help="Omit iconPath and all Icon artifacts for a deliberately iconless record",
    )
    package_parser.add_argument(
        "--allow-legacy-derived-icon",
        action="store_true",
        help="Explicit compatibility switch; never use for new production art",
    )
    package_parser.add_argument("--icon-size", type=int, default=130)
    package_parser.add_argument("--icon-content-max", type=int, default=115)
    package_parser.add_argument("--z", default="-3")
    package_parser.add_argument("--output-dir", type=Path, required=True)
    package_parser.add_argument(
        "--force", action="store_true", help="Replace known staged outputs"
    )
    package_parser.set_defaults(func=package)

    verify_parser = subparsers.add_parser(
        "verify", help="Re-audit a staged delivery package and artifact hashes"
    )
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.set_defaults(func=verify)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
