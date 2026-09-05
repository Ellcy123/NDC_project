#!/usr/bin/env python3
"""Prepare anonymous thumbnail and calm-separation evidence for an expression set.

The script is intentionally fail-closed. It validates planning data and asset
inventory, creates evidence, and leaves every artistic decision NOT_CHECKED.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from review_font import load_review_font


PASS = "PASS"
FAIL = "FAIL"
NOT_CHECKED = "NOT_CHECKED"
INTENSITIES = {"0_neutral", "1_micro", "2_readable", "3_strong"}
FACIAL_REGIONS = {
    "brows", "upper_eyelids", "lower_eyelids", "eyes", "gaze", "eye_surround",
    "cheeks", "nose_nasolabial", "mouth", "jaw_chin",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def font(size: int) -> ImageFont.ImageFont:
    return load_review_font(size)


def composite(path: Path, profile: str) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, (232, 232, 232, 255))
    if profile == "transparent":
        background.alpha_composite(image)
        return background.convert("RGB")
    return image.convert("RGB")


def subject_mask(path: Path, profile: str) -> np.ndarray:
    image = Image.open(path).convert("RGBA")
    rgba = np.asarray(image, dtype=np.uint8)
    if profile == "transparent":
        return rgba[..., 3] > 16
    rgb = rgba[..., :3].astype(np.int16)
    green = np.array([0, 255, 43], dtype=np.int16)
    return np.max(np.abs(rgb - green), axis=2) > 8


def subject_bbox(path: Path, profile: str) -> tuple[int, int, int, int]:
    mask = subject_mask(path, profile)
    ys, xs = np.where(mask)
    if not len(xs):
        raise ValueError(f"No subject found: {path}")
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def full_thumbnail(path: Path, profile: str, box: tuple[int, int], subject_height: int) -> Image.Image:
    image = composite(path, profile)
    _, y1, _, y2 = subject_bbox(path, profile)
    scale = subject_height / max(1, y2 - y1)
    resized = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
    resized.thumbnail(box, Image.Resampling.LANCZOS)
    return resized


def head_crop(path: Path, profile: str, size: tuple[int, int]) -> Image.Image:
    image = composite(path, profile)
    x1, y1, x2, y2 = subject_bbox(path, profile)
    width, height = x2 - x1, y2 - y1
    cx = (x1 + x2) / 2
    crop_w = min(image.width, max(width * 0.58, height * 0.48))
    crop_h = min(image.height, height * 0.62)
    left = max(0, int(cx - crop_w / 2))
    right = min(image.width, int(cx + crop_w / 2))
    top = max(0, y1)
    bottom = min(image.height, int(y1 + crop_h))
    crop = image.crop((left, top, right, bottom))
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    return crop


def planning_check(entry: dict[str, Any]) -> tuple[str, list[str]]:
    issues: list[str] = []
    expression_id = entry.get("expression_id")
    intensity = entry.get("intensity_target")
    cues = entry.get("signature_cues")
    if intensity not in INTENSITIES:
        issues.append("intensity_target missing or unsupported")
    if not isinstance(entry.get("contrast_against_calm"), str) or not entry["contrast_against_calm"].strip():
        issues.append("contrast_against_calm missing")
    if not isinstance(entry.get("forbidden_confusions"), list):
        issues.append("forbidden_confusions must be an array")
    if not isinstance(entry.get("thumbnail_readability_target"), str) or not entry["thumbnail_readability_target"].strip():
        issues.append("thumbnail_readability_target missing")
    regions: set[str] = set()
    facial = 0
    if not isinstance(cues, list):
        issues.append("signature_cues must be an array")
        cues = []
    for index, cue in enumerate(cues):
        if not isinstance(cue, dict):
            issues.append(f"signature_cues[{index}] must be an object")
            continue
        region, signal = cue.get("region"), cue.get("signal")
        if not isinstance(region, str) or not region.strip() or not isinstance(signal, str) or not signal.strip():
            issues.append(f"signature_cues[{index}] requires region and signal")
            continue
        regions.add(region)
        facial += int(region in FACIAL_REGIONS)
    if expression_id == "calm" or intensity == "0_neutral":
        pass
    elif intensity == "1_micro":
        if len(regions) < 2 or facial < 2:
            issues.append("1_micro requires two independent facial regions")
    elif intensity in {"2_readable", "3_strong"}:
        if len(regions) < 3 or facial < 2:
            issues.append("2_readable/3_strong requires three regions including two facial regions")
    return (PASS if not issues else FAIL), issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=("transparent", "greenscreen"))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--thumbnail-subject-height", type=int, default=256)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    character_id = str(manifest["character_id"])
    expressions = manifest.get("expressions")
    if not isinstance(expressions, list) or not expressions:
        raise ValueError("Manifest expressions must be a non-empty list")
    by_id = {str(item["expression_id"]): item for item in expressions}
    if "calm" not in by_id:
        raise ValueError("Expression readability review requires calm")

    input_dir = args.input_dir.resolve()
    assets: dict[str, Path] = {}
    for expression_id in by_id:
        path = input_dir / f"{character_id}_{expression_id}.png"
        if not path.is_file():
            raise FileNotFoundError(path)
        assets[expression_id] = path.resolve()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    title_font, code_font, small_font = font(20), font(18), font(14)

    ordered = list(assets)
    seed = int(sha256(manifest_path)[:16], 16) ^ (1 if args.profile == "transparent" else 2)
    random.Random(seed).shuffle(ordered)
    codes = {expression_id: chr(65 + index) for index, expression_id in enumerate(ordered)}

    cell_w, cell_h = 460, 340
    columns = min(4, len(ordered))
    rows = (len(ordered) + columns - 1) // columns
    blind = Image.new("RGB", (cell_w * columns, cell_h * rows), (238, 238, 238))
    draw = ImageDraw.Draw(blind)
    for index, expression_id in enumerate(ordered):
        row, column = divmod(index, columns)
        x0, y0 = column * cell_w, row * cell_h
        thumb = full_thumbnail(assets[expression_id], args.profile, (cell_w - 20, 290), args.thumbnail_subject_height)
        blind.paste(thumb, (x0 + (cell_w - thumb.width) // 2, y0 + 5))
        draw.rectangle((x0, y0, x0 + cell_w - 1, y0 + cell_h - 1), outline=(145, 145, 145))
        draw.text((x0 + 12, y0 + 305), f"CODE {codes[expression_id]}", fill=(20, 20, 20), font=code_font)
    blind_path = output_dir / "thumbnail-blind-sheet.png"
    blind.save(blind_path)

    non_calm = [value for value in assets if value != "calm"]
    pair_w, pair_h = 720, 300
    pairs = Image.new("RGB", (pair_w, pair_h * max(1, len(non_calm))), (236, 236, 236))
    draw = ImageDraw.Draw(pairs)
    for row, expression_id in enumerate(non_calm):
        y0 = row * pair_h
        calm_crop = head_crop(assets["calm"], args.profile, (315, 245))
        candidate_crop = head_crop(assets[expression_id], args.profile, (315, 245))
        pairs.paste(calm_crop, (15 + (315 - calm_crop.width) // 2, y0 + 8))
        pairs.paste(candidate_crop, (390 + (315 - candidate_crop.width) // 2, y0 + 8))
        draw.text((18, y0 + 260), "CALM", fill=(20, 20, 20), font=title_font)
        draw.text((393, y0 + 260), f"CODE {codes[expression_id]}", fill=(20, 20, 20), font=title_font)
        draw.line((360, y0, 360, y0 + pair_h - 1), fill=(120, 120, 120), width=2)
    pair_path = output_dir / "calm-separation-sheet.png"
    pairs.save(pair_path)

    planning_rows = []
    planning_statuses = []
    for expression_id, entry in by_id.items():
        status, issues = planning_check(entry)
        planning_statuses.append(status)
        planning_rows.append({
            "expression_id": expression_id,
            "intensity_target": entry.get("intensity_target"),
            "signature_cues": entry.get("signature_cues", []),
            "contrast_against_calm": entry.get("contrast_against_calm"),
            "forbidden_confusions": entry.get("forbidden_confusions", []),
            "thumbnail_readability_target": entry.get("thumbnail_readability_target"),
            "status": status,
            "issues": issues,
        })

    review = {
        "schema_version": 1,
        "kind": "ndc_expression_readability_review",
        "profile": args.profile,
        "manifest": {"path": str(manifest_path), "sha256": sha256(manifest_path)},
        "thumbnail_subject_height_px": args.thumbnail_subject_height,
        "planning_status": PASS if all(value == PASS for value in planning_statuses) else FAIL,
        "planning": planning_rows,
        "assets": [{"expression_id": expression_id, "path": str(path), "sha256": sha256(path), "anonymous_code": codes[expression_id]} for expression_id, path in assets.items()],
        "artifacts": {"thumbnail_blind_sheet": str(blind_path), "calm_separation_sheet": str(pair_path)},
        "reviewer": None,
        "whole_set_checked": False,
        "delivery_scale_checked": False,
        "expression_reviews": [{
            "expression_id": expression_id,
            "visible_signature_cues": [],
            "all_signature_cues_visible": None,
            "expression_signal_completeness_status": NOT_CHECKED,
            "calm_separation_status": NOT_CHECKED,
            "thumbnail_readability_status": NOT_CHECKED,
            "semantic_accuracy_status": NOT_CHECKED,
        } for expression_id in non_calm],
        "pairwise_confusions": [],
        "pairwise_separation_status": NOT_CHECKED,
        "formal_status": NOT_CHECKED,
        "notes": ["Evidence only. Pixel difference and mechanical variation cannot approve expression readability."],
    }
    report_path = output_dir / "expression_readability_review.json"
    report_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PLANNING_STATUS: {review['planning_status']}")
    print(f"BLIND_SHEET: {blind_path}")
    print(f"CALM_SEPARATION_SHEET: {pair_path}")
    print(f"REPORT: {report_path}")
    return 0 if review["planning_status"] == PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
