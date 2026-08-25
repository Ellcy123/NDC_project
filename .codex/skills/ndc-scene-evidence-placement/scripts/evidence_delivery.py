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


def derive_icon(detail: Image.Image, size: int, padding: int) -> Image.Image:
    if size <= 0:
        raise ValueError("--icon-size must be positive")
    if padding < 0 or padding * 2 >= size:
        raise ValueError("--icon-padding must be non-negative and smaller than half the icon")
    rgba = detail.convert("RGBA")
    bbox = alpha_bbox(rgba)
    if bbox is None:
        raise ValueError("Detail image is fully transparent")
    subject = rgba.crop(bbox)
    available = size - padding * 2
    scale = min(available / subject.width, available / subject.height)
    new_size = (
        max(1, round(subject.width * scale)),
        max(1, round(subject.height * scale)),
    )
    subject = subject.resize(new_size, Image.Resampling.LANCZOS)
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    icon.paste(
        subject,
        ((size - subject.width) // 2, (size - subject.height) // 2),
        subject,
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
        "mapCropMatchesFinalScenePixels": images_equal(final.crop(rect), map_crop),
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
    reconstructed = source.copy()
    reconstructed.paste(map_crop, (rect[0], rect[1]))
    checks.update(
        {
            "changedPixelsInsideAuthorization": changed_inside,
            "changedPixelsOutsideAuthorization": changed_outside,
            "outsideAuthorizationByteIdentical": changed_outside == 0,
            "mapCropReconstructsFinalFromSource": images_equal(reconstructed, final),
        }
    )
    return checks


def checks_pass(checks: dict[str, Any], base: dict[str, Any] | None) -> bool:
    required = (
        checks["mapCropMatchesFinalScenePixels"],
        checks["authorizationContainedByMapRect"],
    )
    if not all(required):
        return False
    if checks["sourceProvided"]:
        if not all(
            (
                checks["sourceFinalSizeMatches"],
                checks["sourceFinalModeMatches"],
                checks["outsideAuthorizationByteIdentical"],
                checks["mapCropReconstructsFinalFromSource"],
            )
        ):
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
    full_authorization_mask: Image.Image | None = None
    if args.map_rect:
        rect = as_rect(args.map_rect)
    else:
        if mask_path is None:
            raise ValueError(
                "Supply a source-sized --authorization-mask for automatic coordinates, "
                "or an audited --map-rect for a legacy baked prop"
            )
        full_authorization_mask = load_source_sized_mask(mask_path, final.size)
        bbox = full_authorization_mask.getbbox()
        if bbox is None:
            raise ValueError("Authorization mask is empty")
        rect = expand_rect(bbox, args.map_padding, final.width, final.height)
    validate_rect(rect, final.width, final.height)

    source_path = args.source_scene.resolve() if args.source_scene else None
    source = load_preserving_mode(source_path) if source_path else None
    if source is not None and source.size != final.size:
        raise ValueError("Source and final scene dimensions differ")
    scene_has_changes = bool(
        source is not None and nonzero_pixel_count(changed_pixel_mask(source, final))
    )
    if scene_has_changes and mask_path is None:
        raise ValueError("Changed scenes require --authorization-mask")
    if scene_has_changes and args.base_verification is None:
        raise ValueError("Changed scenes require --base-verification from the coordinate edit")

    map_stem = validate_stem(args.map_stem, "mapSpritePath")
    detail_stem = validate_stem(args.detail_stem, "desSpritePath")
    icon_stem = validate_stem(args.icon_stem, "iconPath")
    if len({map_stem, detail_stem, icon_stem}) != 3:
        raise ValueError("Map, detail, and icon stems must be distinct")
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
    icon_output = output_dir / f"{icon_stem}.png"
    xy_output = output_dir / XY_NAME
    patch_output = output_dir / PATCH_NAME
    overlay_output = output_dir / OVERLAY_NAME

    known_outputs = (
        scene_output,
        map_output,
        detail_output,
        icon_output,
        xy_output,
        patch_output,
        overlay_output,
        output_dir / VERIFICATION_NAME,
    )
    existing_outputs = [path for path in known_outputs if path.exists()]
    if existing_outputs and not args.force:
        formatted = ", ".join(str(path) for path in existing_outputs)
        raise FileExistsError(
            f"Staged outputs already exist; use a new directory or --force: {formatted}"
        )

    copy_png(final_path, scene_output)
    map_crop = final.crop(rect)
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

    if args.icon_image:
        icon_source = args.icon_image.resolve()
        copy_png(icon_source, icon_output)
        icon_provenance: dict[str, Any] = {
            "method": "approved-icon-image",
            "source": str(icon_source),
            "sourceSha256": sha256(icon_source),
        }
    else:
        icon = derive_icon(detail, args.icon_size, args.icon_padding)
        icon.save(icon_output)
        icon_provenance = {
            "method": "derived-from-detail",
            "size": args.icon_size,
            "padding": args.icon_padding,
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
        "iconPath": icon_stem,
        "Position": [str(x), str(y), z],
    }
    save_json(patch_output, item_patch)
    create_overlay(final, rect, str(args.item_id)).save(overlay_output)

    base_verification = read_base_verification(
        args.base_verification.resolve() if args.base_verification else None
    )
    checks = scene_checks(source, final, mask, rect, saved_map)
    package_passed = checks_pass(checks, base_verification)

    artifact_paths = {
        "fullScene": scene_output,
        "mapSprite": map_output,
        "detailSprite": detail_output,
        "iconSprite": icon_output,
        "xyCompatibility": xy_output,
        "itemStaticDataPatch": patch_output,
        "positionOverlay": overlay_output,
    }
    artifact_records = {
        key: {"path": str(path), "sha256": sha256(path)}
        for key, path in artifact_paths.items()
    }

    manifest: dict[str, Any] = {
        "version": 1,
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
            "x": x,
            "y": y,
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1],
            "rect": list(rect),
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
            map_matches_scene = images_equal(
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
        default=6,
        help="Stable scene pixels added around the automatic mask bounding box",
    )
    package_parser.add_argument("--item-id", required=True)
    package_parser.add_argument("--scene-id", required=True)
    package_parser.add_argument("--folder-path", required=True)
    package_parser.add_argument("--map-stem", required=True)
    package_parser.add_argument("--detail-stem", required=True)
    package_parser.add_argument("--icon-stem", required=True)
    package_parser.add_argument("--detail-image", type=Path)
    package_parser.add_argument("--cutout-mask", type=Path)
    package_parser.add_argument("--detail-padding", type=int, default=4)
    package_parser.add_argument("--icon-image", type=Path)
    package_parser.add_argument("--icon-size", type=int, default=256)
    package_parser.add_argument("--icon-padding", type=int, default=24)
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
