#!/usr/bin/env python3
"""Deterministically finalize and verify NDC Big, Icon, and clue Polaroid art.

The image model or an artist owns the high-resolution semantic master. This
helper owns exact runtime canvas sizes, alpha-safe downsampling, layout bounds,
template composition, hashes, and machine-verifiable reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageOps


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSET_DIR = SKILL_DIR / "assets"

ICON_MASTER_SIZE = (1040, 1040)
ICON_MASTER_SAFE_RECT = (60, 60, 980, 980)
ICON_FINAL_SIZE = (130, 130)
ICON_FINAL_SAFE_RECT = (7, 7, 122, 122)

BIG_FRAMES: dict[str, dict[str, tuple[int, ...]]] = {
    "portrait": {
        "size": (571, 1000),
        "safeRect": (58, 100, 513, 900),
        "guideRect": (502, 243, 1073, 1243),
    },
    "square": {
        "size": (818, 818),
        "safeRect": (82, 82, 736, 736),
        "guideRect": (378, 334, 1196, 1152),
    },
    "landscape": {
        "size": (1000, 571),
        "safeRect": (100, 58, 900, 513),
        "guideRect": (288, 458, 1288, 1029),
    },
}

POLAROID_SIZE = (620, 620)
POLAROID_QUAD = ((37, 65), (555, 37), (580, 478), (62, 508))
BIG_GUIDE_SHA256 = "231df5803aff0ae1430c65dc79304bb0278ae569ffcaf7447da4c955f61bc33e"
POLAROID_TEMPLATE_SHA256 = (
    "8c5bd335a686e4a5ff7be1887c65cd30cfaa08646c8b2643566583a395e4a244"
)
POLAROID_MASK_SHA256 = (
    "58995e55031cc2c264e6320da683e9dd6e727ec052f80a90ad9167a12876cc04"
)


Rect = tuple[int, int, int, int]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def ensure_new_output(output: Path, inputs: Iterable[Path], force: bool) -> None:
    resolved = output.resolve()
    if any(resolved == value.resolve() for value in inputs):
        raise ValueError("Output must differ from every input")
    if output.exists() and not force:
        raise FileExistsError(f"Output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)


def load_png(path: Path, *, require_rgba: bool = False) -> Image.Image:
    if path.suffix.lower() != ".png" or not path.is_file():
        raise ValueError(f"Expected an existing PNG: {path}")
    with Image.open(path) as image:
        if require_rgba and image.mode != "RGBA":
            raise ValueError(f"Expected RGBA PNG, got {image.mode}: {path}")
        return image.convert("RGBA") if image.mode != "RGBA" else image.copy()


def load_mask(path: Path, expected_size: tuple[int, int]) -> Image.Image:
    if path.suffix.lower() != ".png" or not path.is_file():
        raise ValueError(f"Expected an existing mask PNG: {path}")
    with Image.open(path) as image:
        mask = image.convert("L")
    if mask.size != expected_size:
        raise ValueError(
            f"Mask must be {expected_size[0]}x{expected_size[1]}, got {mask.size}: {path}"
        )
    if mask.getbbox() is None:
        raise ValueError(f"Mask is empty: {path}")
    return mask


def normalize_transparent_rgb(image: Image.Image) -> Image.Image:
    red, green, blue, alpha = image.convert("RGBA").split()
    transparent = alpha.point(lambda value: 255 if value == 0 else 0)
    for channel in (red, green, blue):
        channel.paste(0, mask=transparent)
    return Image.merge("RGBA", (red, green, blue, alpha))


def premultiplied_resize(
    image: Image.Image, size: tuple[int, int], resample: Image.Resampling
) -> Image.Image:
    premultiplied = image.convert("RGBA").convert("RGBa")
    resized = premultiplied.resize(size, resample)
    return normalize_transparent_rgb(resized.convert("RGBA"))


def premultiplied_rotate(image: Image.Image, degrees: float) -> Image.Image:
    premultiplied = image.convert("RGBA").convert("RGBa")
    rotated = premultiplied.rotate(
        degrees,
        resample=Image.Resampling.BICUBIC,
        expand=True,
        fillcolor=(0, 0, 0, 0),
    )
    return normalize_transparent_rgb(rotated.convert("RGBA"))


def alpha_bbox(image: Image.Image) -> Rect | None:
    return image.convert("RGBA").getchannel("A").getbbox()


def rect_contains(outer: Rect, inner: Rect | None) -> bool:
    if inner is None:
        return False
    return (
        outer[0] <= inner[0]
        and outer[1] <= inner[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def rect_size(rect: Rect | None) -> list[int] | None:
    if rect is None:
        return None
    return [rect[2] - rect[0], rect[3] - rect[1]]


def outside_rect_nonzero(mask: Image.Image, rect: Rect) -> int:
    allowed = Image.new("L", mask.size, 0)
    allowed.paste(255, rect)
    outside = ImageChops.multiply(mask, ImageOps.invert(allowed))
    histogram = outside.histogram()
    return outside.width * outside.height - histogram[0]


def transparent_rgb_nonzero(image: Image.Image) -> int:
    red, green, blue, alpha = image.convert("RGBA").split()
    rgb_nonzero = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    transparent = alpha.point(lambda value: 255 if value == 0 else 0)
    return nonzero_count(ImageChops.multiply(rgb_nonzero, transparent))


def nonzero_count(image: Image.Image) -> int:
    histogram = image.convert("L").histogram()
    return image.width * image.height - histogram[0]


def mask_centroid(mask: Image.Image) -> tuple[float, float] | None:
    grayscale = mask.convert("L")
    bbox = grayscale.getbbox()
    if bbox is None:
        return None
    pixels = grayscale.load()
    total = 0.0
    weighted_x = 0.0
    weighted_y = 0.0
    for y in range(bbox[1], bbox[3]):
        for x in range(bbox[0], bbox[2]):
            weight = float(pixels[x, y])
            total += weight
            weighted_x += x * weight
            weighted_y += y * weight
    if total <= 0:
        return None
    return weighted_x / total, weighted_y / total


def inspect_icon(
    image: Image.Image,
    subject_mask: Image.Image | None = None,
    shadow_mask: Image.Image | None = None,
) -> dict[str, Any]:
    rgba = image.convert("RGBA")
    bbox = alpha_bbox(rgba)
    alpha = rgba.getchannel("A")
    checks: dict[str, Any] = {
        "sizeIs130": rgba.size == ICON_FINAL_SIZE,
        "modeIsRGBA": image.mode == "RGBA",
        "contentExists": bbox is not None,
        "contentBounds": list(bbox) if bbox else None,
        "contentSize": rect_size(bbox),
        "safeRect": list(ICON_FINAL_SAFE_RECT),
        "contentInside115SafeRect": rect_contains(ICON_FINAL_SAFE_RECT, bbox),
        "alphaPixelsOutsideSafeRect": (
            outside_rect_nonzero(alpha, ICON_FINAL_SAFE_RECT)
            if rgba.size == ICON_FINAL_SIZE
            else None
        ),
        "transparentRgbNonzeroPixels": transparent_rgb_nonzero(rgba),
    }

    if subject_mask is not None or shadow_mask is not None:
        if subject_mask is None or shadow_mask is None:
            checks["layerMasksProvidedTogether"] = False
        elif subject_mask.size != rgba.size or shadow_mask.size != rgba.size:
            checks["layerMasksProvidedTogether"] = True
            checks["layerMaskSizesMatch"] = False
        else:
            subject_center = mask_centroid(subject_mask)
            shadow_center = mask_centroid(shadow_mask)
            checks.update(
                {
                    "layerMasksProvidedTogether": True,
                    "layerMaskSizesMatch": True,
                    "subjectBounds": (
                        list(subject_mask.getbbox()) if subject_mask.getbbox() else None
                    ),
                    "shadowBounds": (
                        list(shadow_mask.getbbox()) if shadow_mask.getbbox() else None
                    ),
                    "subjectCentroid": list(subject_center) if subject_center else None,
                    "shadowCentroid": list(shadow_center) if shadow_center else None,
                    "shadowFallsLeftAndDown": bool(
                        subject_center
                        and shadow_center
                        and shadow_center[0] < subject_center[0]
                        and shadow_center[1] > subject_center[1]
                    ),
                }
            )

    required = (
        checks["sizeIs130"],
        checks["modeIsRGBA"],
        checks["contentExists"],
        checks["contentInside115SafeRect"],
        checks["alphaPixelsOutsideSafeRect"] == 0,
        checks["transparentRgbNonzeroPixels"] == 0,
    )
    if "layerMasksProvidedTogether" in checks:
        required += (
            checks.get("layerMasksProvidedTogether") is True,
            checks.get("layerMaskSizesMatch") is True,
            checks.get("shadowFallsLeftAndDown") is True,
        )
    checks["passed"] = all(required)
    return checks


def icon_report(
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


def finalize_icon(args: argparse.Namespace) -> None:
    master_path = args.master.resolve()
    subject_path = args.subject_mask.resolve()
    shadow_path = args.shadow_mask.resolve()
    output_path = args.output.resolve()
    report_path = (
        args.report.resolve()
        if args.report
        else output_path.with_name(f"{output_path.stem}_verification.json")
    )
    ensure_new_output(output_path, (master_path, subject_path, shadow_path), args.force)
    if report_path.exists() and not args.force:
        raise FileExistsError(f"Report already exists: {report_path}")

    master = load_png(master_path, require_rgba=True)
    if master.size != ICON_MASTER_SIZE:
        raise ValueError("Icon master must be exactly 1040x1040 RGBA")
    subject = load_mask(subject_path, ICON_MASTER_SIZE)
    shadow = load_mask(shadow_path, ICON_MASTER_SIZE)
    master_bbox = alpha_bbox(master)
    if not rect_contains(ICON_MASTER_SAFE_RECT, master_bbox):
        raise ValueError(
            "Icon master content must fit inside the centered 920x920 work safe rect"
        )

    final = premultiplied_resize(master, ICON_FINAL_SIZE, Image.Resampling.LANCZOS)
    final_subject = subject.resize(ICON_FINAL_SIZE, Image.Resampling.LANCZOS)
    final_shadow = shadow.resize(ICON_FINAL_SIZE, Image.Resampling.LANCZOS)
    checks = inspect_icon(final, final_subject, final_shadow)

    final.save(output_path)
    if args.output_subject_mask:
        final_subject.save(args.output_subject_mask.resolve())
    if args.output_shadow_mask:
        final_shadow.save(args.output_shadow_mask.resolve())
    report = icon_report(
        output_path,
        checks,
        method="1040-master-premultiplied-lanczos",
        sources={
            "master": {"path": str(master_path), "sha256": sha256(master_path)},
            "subjectMask": {
                "path": str(subject_path),
                "sha256": sha256(subject_path),
            },
            "shadowMask": {"path": str(shadow_path), "sha256": sha256(shadow_path)},
            "workSafeRect": list(ICON_MASTER_SAFE_RECT),
        },
    )
    save_json(report_path, report)
    print(f"Icon finalization: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Icon: {output_path}")
    print(f"Report: {report_path}")
    if not report["passed"]:
        raise SystemExit(2)


def verify_icon(args: argparse.Namespace) -> None:
    input_path = args.input.resolve()
    image = load_png(input_path, require_rgba=True)
    subject = load_mask(args.subject_mask.resolve(), image.size) if args.subject_mask else None
    shadow = load_mask(args.shadow_mask.resolve(), image.size) if args.shadow_mask else None
    checks = inspect_icon(image, subject, shadow)
    report_path = (
        args.report.resolve()
        if args.report
        else input_path.with_name(f"{input_path.stem}_verification.json")
    )
    report = icon_report(input_path, checks, method="verification-only")
    save_json(report_path, report)
    print(f"Icon verification: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Report: {report_path}")
    if not report["passed"]:
        raise SystemExit(2)


def inspect_big(image: Image.Image, frame: str) -> dict[str, Any]:
    contract = BIG_FRAMES[frame]
    bbox = alpha_bbox(image)
    checks = {
        "frame": frame,
        "expectedSize": list(contract["size"]),
        "safeRect": list(contract["safeRect"]),
        "sizeMatchesFrame": image.size == tuple(contract["size"]),
        "modeIsRGBA": image.mode == "RGBA",
        "contentExists": bbox is not None,
        "contentBounds": list(bbox) if bbox else None,
        "contentInsideSafeRect": rect_contains(contract["safeRect"], bbox),
        "transparentRgbNonzeroPixels": transparent_rgb_nonzero(image),
    }
    checks["passed"] = all(
        (
            checks["sizeMatchesFrame"],
            checks["modeIsRGBA"],
            checks["contentExists"],
            checks["contentInsideSafeRect"],
            checks["transparentRgbNonzeroPixels"] == 0,
        )
    )
    return checks


def big_report(
    output_path: Path,
    frame: str,
    rotation_degrees: float,
    checks: dict[str, Any],
    sources: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "ndc-big-detail",
        "artifact": {
            "path": str(output_path.resolve()),
            "sha256": sha256(output_path),
            "size": list(output_path_image_size(output_path)),
            "mode": "RGBA",
        },
        "frame": frame,
        "rotationDegrees": rotation_degrees,
        "rotationConvention": "positive is counter-clockwise in image coordinates",
        "sources": sources,
        "checks": checks,
        "passed": bool(checks.get("passed")),
    }


def output_path_image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def finalize_big(args: argparse.Namespace) -> None:
    master_path = args.master.resolve()
    output_path = args.output.resolve()
    report_path = (
        args.report.resolve()
        if args.report
        else output_path.with_name(f"{output_path.stem}_verification.json")
    )
    inputs = [master_path]
    ensure_new_output(output_path, inputs, args.force)
    if report_path.exists() and not args.force:
        raise FileExistsError(f"Report already exists: {report_path}")
    if not math.isclose(abs(args.rotation_degrees), 10.0, abs_tol=1e-6):
        raise ValueError("Ordinary Big rotation must be explicitly +10 or -10 degrees")

    master = load_png(master_path, require_rgba=True)
    bbox = alpha_bbox(master)
    if bbox is None:
        raise ValueError("Big master is fully transparent")
    subject = master.crop(bbox)
    rotated = premultiplied_rotate(subject, args.rotation_degrees)
    rotated_bbox = alpha_bbox(rotated)
    if rotated_bbox is None:
        raise AssertionError("Rotated Big unexpectedly became empty")
    rotated = rotated.crop(rotated_bbox)

    contract = BIG_FRAMES[args.frame]
    safe = contract["safeRect"]
    safe_size = (safe[2] - safe[0], safe[3] - safe[1])
    scale = min(safe_size[0] / rotated.width, safe_size[1] / rotated.height)
    if scale > 1.0 and not args.allow_upscale:
        raise ValueError(
            "Big master is too small for the selected frame; provide a larger master "
            "or use --allow-upscale only for an audited legacy asset"
        )
    if not math.isclose(scale, 1.0):
        target = (
            max(1, math.floor(rotated.width * scale)),
            max(1, math.floor(rotated.height * scale)),
        )
        resample = Image.Resampling.LANCZOS if scale < 1.0 else Image.Resampling.BICUBIC
        rotated = premultiplied_resize(rotated, target, resample)

    frame_size = tuple(contract["size"])
    final = Image.new("RGBA", frame_size, (0, 0, 0, 0))
    x = safe[0] + (safe_size[0] - rotated.width) // 2
    y = safe[1] + (safe_size[1] - rotated.height) // 2
    final.alpha_composite(rotated, (x, y))
    final = normalize_transparent_rgb(final)
    checks = inspect_big(final, args.frame)
    final.save(output_path)

    sources: dict[str, Any] = {
        "master": {"path": str(master_path), "sha256": sha256(master_path)},
        "masterContentBounds": list(bbox),
        "rotatedContentBounds": list(rotated_bbox),
        "appliedScale": scale,
    }
    if args.layout_preview:
        guide_path = (ASSET_DIR / "big_layout_guide_2560x1600.png").resolve()
        if sha256(guide_path) != BIG_GUIDE_SHA256:
            raise ValueError("Bundled Big layout guide hash does not match the locked asset")
        guide = load_png(guide_path, require_rgba=True)
        preview = Image.new("RGBA", guide.size, (0, 0, 0, 0))
        preview.alpha_composite(final, tuple(contract["guideRect"][:2]))
        preview.alpha_composite(guide)
        preview_path = args.layout_preview.resolve()
        ensure_new_output(preview_path, (guide_path, output_path), args.force)
        preview.save(preview_path)
        sources["layoutPreview"] = {
            "path": str(preview_path),
            "sha256": sha256(preview_path),
            "guideSha256": BIG_GUIDE_SHA256,
        }

    report = big_report(
        output_path, args.frame, args.rotation_degrees, checks, sources
    )
    save_json(report_path, report)
    print(f"Big finalization: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Big: {output_path}")
    print(f"Report: {report_path}")
    if not report["passed"]:
        raise SystemExit(2)


def verify_big(args: argparse.Namespace) -> None:
    if not math.isclose(abs(args.rotation_degrees), 10.0, abs_tol=1e-6):
        raise ValueError("Ordinary Big rotation must be explicitly +10 or -10 degrees")
    input_path = args.input.resolve()
    image = load_png(input_path, require_rgba=True)
    checks = inspect_big(image, args.frame)
    report_path = (
        args.report.resolve()
        if args.report
        else input_path.with_name(f"{input_path.stem}_verification.json")
    )
    report = big_report(
        input_path,
        args.frame,
        args.rotation_degrees,
        checks,
        {"method": "verification-only"},
    )
    save_json(report_path, report)
    print(f"Big verification: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Report: {report_path}")
    if not report["passed"]:
        raise SystemExit(2)


def center_crop_to_aspect(image: Image.Image, aspect: float) -> Image.Image:
    current = image.width / image.height
    if current > aspect:
        width = max(1, round(image.height * aspect))
        left = (image.width - width) // 2
        return image.crop((left, 0, left + width, image.height))
    height = max(1, round(image.width / aspect))
    top = (image.height - height) // 2
    return image.crop((0, top, image.width, top + height))


def perspective_coefficients(
    destination: list[tuple[float, float]], source: list[tuple[float, float]]
) -> tuple[float, ...]:
    rows: list[list[float]] = []
    values: list[float] = []
    for (x, y), (u, v) in zip(destination, source, strict=True):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        values.append(u)
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        values.append(v)
    return tuple(solve_linear_system(rows, values))


def solve_linear_system(matrix: list[list[float]], values: list[float]) -> list[float]:
    size = len(values)
    augmented = [row[:] + [values[index]] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("Perspective quadrilateral is degenerate")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    return [augmented[row][-1] for row in range(size)]


def polaroid_checks(
    template: Image.Image, output: Image.Image, mask: Image.Image
) -> dict[str, Any]:
    difference = ImageChops.difference(template.convert("RGBA"), output.convert("RGBA"))
    red, green, blue, alpha = difference.split()
    changed = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    changed = ImageChops.lighter(changed, alpha)
    outside = mask.point(lambda value: 255 if value == 0 else 0)
    inside = mask.point(lambda value: 255 if value > 0 else 0)
    outside_count = nonzero_count(ImageChops.multiply(changed, outside))
    inside_count = nonzero_count(ImageChops.multiply(changed, inside))
    checks = {
        "sizeIs620": output.size == POLAROID_SIZE,
        "modeIsRGBA": output.mode == "RGBA",
        "templateSizeMatches": template.size == output.size,
        "maskSizeMatches": mask.size == output.size,
        "changedPixelsOutsideWindowMask": outside_count,
        "changedPixelsInsideWindowMask": inside_count,
        "frameAndTransparentExteriorByteIdentical": outside_count == 0,
        "photoWindowChanged": inside_count > 0,
    }
    checks["passed"] = all(
        (
            checks["sizeIs620"],
            checks["modeIsRGBA"],
            checks["templateSizeMatches"],
            checks["maskSizeMatches"],
            checks["frameAndTransparentExteriorByteIdentical"],
            checks["photoWindowChanged"],
        )
    )
    return checks


def compose_polaroid(args: argparse.Namespace) -> None:
    photo_path = args.photo.resolve()
    template_path = (
        args.template.resolve()
        if args.template
        else (ASSET_DIR / "clue_polaroid_frame_620x620.png").resolve()
    )
    mask_path = (
        args.window_mask.resolve()
        if args.window_mask
        else (ASSET_DIR / "clue_polaroid_window_mask_620x620.png").resolve()
    )
    output_path = args.output.resolve()
    report_path = (
        args.report.resolve()
        if args.report
        else output_path.with_name(f"{output_path.stem}_verification.json")
    )
    ensure_new_output(output_path, (photo_path, template_path, mask_path), args.force)
    if report_path.exists() and not args.force:
        raise FileExistsError(f"Report already exists: {report_path}")
    if not args.allow_unlocked_template:
        if sha256(template_path) != POLAROID_TEMPLATE_SHA256:
            raise ValueError("Polaroid template hash does not match the locked skill asset")
        if sha256(mask_path) != POLAROID_MASK_SHA256:
            raise ValueError("Polaroid window-mask hash does not match the locked skill asset")

    photo = load_png(photo_path).convert("RGBA")
    template = load_png(template_path, require_rgba=True)
    mask = load_mask(mask_path, POLAROID_SIZE)
    if template.size != POLAROID_SIZE:
        raise ValueError("Polaroid template must be exactly 620x620")

    top_width = math.dist(POLAROID_QUAD[0], POLAROID_QUAD[1])
    bottom_width = math.dist(POLAROID_QUAD[3], POLAROID_QUAD[2])
    left_height = math.dist(POLAROID_QUAD[0], POLAROID_QUAD[3])
    right_height = math.dist(POLAROID_QUAD[1], POLAROID_QUAD[2])
    aspect = ((top_width + bottom_width) / 2) / ((left_height + right_height) / 2)
    photo = center_crop_to_aspect(photo, aspect)
    source_quad = [
        (0.0, 0.0),
        (float(photo.width - 1), 0.0),
        (float(photo.width - 1), float(photo.height - 1)),
        (0.0, float(photo.height - 1)),
    ]
    coefficients = perspective_coefficients(
        [(float(x), float(y)) for x, y in POLAROID_QUAD], source_quad
    )
    warped = photo.transform(
        POLAROID_SIZE,
        Image.Transform.PERSPECTIVE,
        coefficients,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )
    output = Image.composite(warped, template, mask).convert("RGBA")
    checks = polaroid_checks(template, output, mask)
    output.save(output_path)
    report = {
        "version": 1,
        "kind": "ndc-clue-polaroid",
        "artifact": {
            "path": str(output_path),
            "sha256": sha256(output_path),
            "size": list(output.size),
            "mode": output.mode,
        },
        "sources": {
            "photo": {"path": str(photo_path), "sha256": sha256(photo_path)},
            "template": {
                "path": str(template_path),
                "sha256": sha256(template_path),
            },
            "windowMask": {"path": str(mask_path), "sha256": sha256(mask_path)},
            "windowQuad": [list(point) for point in POLAROID_QUAD],
        },
        "checks": checks,
        "passed": bool(checks.get("passed")),
    }
    save_json(report_path, report)
    print(f"Polaroid composition: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Output: {output_path}")
    print(f"Report: {report_path}")
    if not report["passed"]:
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    icon_parser = subparsers.add_parser(
        "finalize-icon", help="Downsample a verified 1040 master to a 130 runtime Icon"
    )
    icon_parser.add_argument("--master", type=Path, required=True)
    icon_parser.add_argument("--subject-mask", type=Path, required=True)
    icon_parser.add_argument("--shadow-mask", type=Path, required=True)
    icon_parser.add_argument("--output", type=Path, required=True)
    icon_parser.add_argument("--output-subject-mask", type=Path)
    icon_parser.add_argument("--output-shadow-mask", type=Path)
    icon_parser.add_argument("--report", type=Path)
    icon_parser.add_argument("--force", action="store_true")
    icon_parser.set_defaults(func=finalize_icon)

    verify_icon_parser = subparsers.add_parser(
        "verify-icon", help="Verify a final 130x130 RGBA Icon and its safe bounds"
    )
    verify_icon_parser.add_argument("--input", type=Path, required=True)
    verify_icon_parser.add_argument("--subject-mask", type=Path)
    verify_icon_parser.add_argument("--shadow-mask", type=Path)
    verify_icon_parser.add_argument("--report", type=Path)
    verify_icon_parser.set_defaults(func=verify_icon)

    big_parser = subparsers.add_parser(
        "finalize-big", help="Rotate and fit a transparent Big master into a runtime frame"
    )
    big_parser.add_argument("--master", type=Path, required=True)
    big_parser.add_argument("--frame", choices=sorted(BIG_FRAMES), required=True)
    big_parser.add_argument("--rotation-degrees", type=float, required=True)
    big_parser.add_argument("--output", type=Path, required=True)
    big_parser.add_argument("--layout-preview", type=Path)
    big_parser.add_argument("--report", type=Path)
    big_parser.add_argument("--allow-upscale", action="store_true")
    big_parser.add_argument("--force", action="store_true")
    big_parser.set_defaults(func=finalize_big)

    verify_big_parser = subparsers.add_parser(
        "verify-big", help="Verify an already-finalized ordinary Big image"
    )
    verify_big_parser.add_argument("--input", type=Path, required=True)
    verify_big_parser.add_argument("--frame", choices=sorted(BIG_FRAMES), required=True)
    verify_big_parser.add_argument("--rotation-degrees", type=float, required=True)
    verify_big_parser.add_argument("--report", type=Path)
    verify_big_parser.set_defaults(func=verify_big)

    polaroid_parser = subparsers.add_parser(
        "compose-polaroid", help="Warp a clue photo into the locked 620x620 frame"
    )
    polaroid_parser.add_argument("--photo", type=Path, required=True)
    polaroid_parser.add_argument("--template", type=Path)
    polaroid_parser.add_argument("--window-mask", type=Path)
    polaroid_parser.add_argument("--output", type=Path, required=True)
    polaroid_parser.add_argument("--report", type=Path)
    polaroid_parser.add_argument("--allow-unlocked-template", action="store_true")
    polaroid_parser.add_argument("--force", action="store_true")
    polaroid_parser.set_defaults(func=compose_polaroid)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
