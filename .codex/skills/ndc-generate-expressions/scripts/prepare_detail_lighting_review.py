#!/usr/bin/env python3
"""Prepare fail-closed source-detail and lighting-topology review evidence.

The tool writes native 100% crops, nearest-neighbour 200% previews, a review
sheet, and a JSON record. Numeric edge-energy values are screening evidence
only. They never approve sharpness, source fidelity, or lighting continuity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat


SOURCE_KEYS = ("approved_portrait", "neutral_master", "native_source", "profile_asset")
SOURCE_LABELS = {
    "approved_portrait": "APPROVED PORTRAIT",
    "neutral_master": "COMPLETED CALM MASTER",
    "native_source": "RAW NATIVE SOURCE",
    "profile_asset": "FINAL PROFILE ASSET",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def validate_box(value: Any, image: Image.Image, field: str) -> tuple[int, int, int, int]:
    if not isinstance(value, list) or len(value) != 4 or any(not isinstance(v, int) for v in value):
        raise ValueError(f"{field}: expected integer [left, top, right, bottom]")
    left, top, right, bottom = value
    if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
        raise ValueError(f"{field}: box {value} outside image {image.size}")
    return left, top, right, bottom


def checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    board = Image.new("RGB", size, (222, 222, 222))
    draw = ImageDraw.Draw(board)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(x + cell - 1, size[0] - 1), min(y + cell - 1, size[1] - 1)), fill=(184, 184, 184))
    return board


def edge_energy(crop: Image.Image) -> float:
    gray = crop.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    return round(float(ImageStat.Stat(edges).rms[0]), 4)


def render_panel(crop: Image.Image, size: tuple[int, int]) -> Image.Image:
    contained = ImageOps.contain(crop.convert("RGBA"), (size[0] - 20, size[1] - 20), Image.Resampling.LANCZOS)
    panel = checkerboard(size).convert("RGBA")
    panel.alpha_composite(contained, ((size[0] - contained.width) // 2, (size[1] - contained.height) // 2))
    return panel.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-portrait", required=True, type=Path)
    parser.add_argument("--neutral-master", required=True, type=Path)
    parser.add_argument("--native-source", required=True, type=Path)
    parser.add_argument("--profile-asset", required=True, type=Path)
    parser.add_argument("--composition-audit", required=True, type=Path)
    parser.add_argument("--regions", required=True, type=Path)
    parser.add_argument("--expression-id", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    paths = {
        "approved_portrait": args.approved_portrait.resolve(),
        "neutral_master": args.neutral_master.resolve(),
        "native_source": args.native_source.resolve(),
        "profile_asset": args.profile_asset.resolve(),
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    audit_path = args.composition_audit.resolve()
    regions_path = args.regions.resolve()
    if not audit_path.is_file():
        raise FileNotFoundError(audit_path)
    if not regions_path.is_file():
        raise FileNotFoundError(regions_path)

    images = {key: Image.open(path).convert("RGBA") for key, path in paths.items()}
    region_spec = load_json(regions_path)
    if region_spec.get("schema_version") != 1 or not isinstance(region_spec.get("regions"), list):
        raise ValueError("Regions file must be schema_version 1 with a regions array")
    if not region_spec["regions"]:
        raise ValueError("At least one semantic review region is required")

    composition = load_json(audit_path)
    if composition.get("kind") != "ndc_expression_profile_composition":
        raise ValueError("Composition audit kind mismatch")
    output_record = composition.get("output", {})
    if Path(output_record.get("path", "")).resolve() != paths["profile_asset"]:
        raise ValueError("Composition audit output does not match profile asset")
    if output_record.get("sha256") != sha256(paths["profile_asset"]):
        raise ValueError("Composition audit output hash is stale")
    transform = composition.get("transform", {})
    scale = transform.get("uniform_scale")
    resample_count = transform.get("resample_count")
    no_upscale = isinstance(scale, (int, float)) and not isinstance(scale, bool) and 0 < float(scale) <= 1.0
    single_resample = resample_count == 1

    output_dir = args.output_dir.resolve()
    crops_dir = output_dir / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    panel_w, panel_h = 320, 300
    label_h, margin, gap = 58, 28, 18
    rows: list[dict[str, Any]] = []
    seen_region_ids: set[str] = set()

    for index, item in enumerate(region_spec["regions"]):
        if not isinstance(item, dict):
            raise ValueError(f"regions[{index}]: expected object")
        region_id = item.get("region_id")
        if not isinstance(region_id, str) or not region_id.strip() or region_id in seen_region_ids:
            raise ValueError(f"regions[{index}].region_id: expected unique non-empty string")
        seen_region_ids.add(region_id)
        boxes = item.get("boxes")
        if not isinstance(boxes, dict):
            raise ValueError(f"regions[{index}].boxes: expected object")
        checks = item.get("checks", ["detail"])
        if not isinstance(checks, list) or any(v not in ("detail", "lighting") for v in checks):
            raise ValueError(f"regions[{index}].checks: supported values are detail and lighting")
        source_records: dict[str, Any] = {}
        for key in SOURCE_KEYS:
            box = validate_box(boxes.get(key), images[key], f"regions[{index}].boxes.{key}")
            crop = images[key].crop(box)
            safe_region = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in region_id)
            native_path = crops_dir / f"{safe_region}__{key}__100pct.png"
            preview_path = crops_dir / f"{safe_region}__{key}__200pct-nearest.png"
            crop.save(native_path)
            crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(preview_path)
            source_records[key] = {
                "box_xyxy": list(box),
                "native_crop": {"path": str(native_path), "sha256": sha256(native_path), "size": list(crop.size)},
                "preview_200pct_nearest": {"path": str(preview_path), "sha256": sha256(preview_path)},
                "edge_energy_screen": edge_energy(crop),
            }
        rows.append({"region_id": region_id, "checks": checks, "sources": source_records})

    sheet_w = margin * 2 + panel_w * 4 + gap * 3
    row_h = label_h + panel_h + 54
    sheet_h = margin * 2 + 52 + row_h * len(rows)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (34, 36, 39))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), f"Detail + lighting evidence | {args.expression_id}", fill=(245, 245, 245), font=font)
    for row_index, row in enumerate(rows):
        base_y = margin + 52 + row_index * row_h
        draw.text((margin, base_y), f"REGION: {row['region_id']} | CHECKS: {', '.join(row['checks'])}", fill=(255, 220, 120), font=font)
        for column, key in enumerate(SOURCE_KEYS):
            x = margin + column * (panel_w + gap)
            record = row["sources"][key]
            crop = Image.open(record["native_crop"]["path"]).convert("RGBA")
            draw.text((x, base_y + 22), SOURCE_LABELS[key], fill=(235, 235, 235), font=font)
            draw.text((x, base_y + 38), f"native {crop.width}x{crop.height} | edge {record['edge_energy_screen']}", fill=(185, 190, 196), font=font)
            panel = render_panel(crop, (panel_w, panel_h))
            sheet.paste(panel, (x, base_y + label_h))
            draw.rectangle((x, base_y + label_h, x + panel_w - 1, base_y + label_h + panel_h - 1), outline=(110, 114, 119), width=2)
        draw.text((margin, base_y + label_h + panel_h + 14), "Use saved 100% and 200% crops for the formal decision; the sheet is an overview only.", fill=(205, 205, 205), font=font)

    sheet_path = output_dir / "detail-lighting-review-sheet.png"
    report_path = output_dir / "detail-lighting-review.json"
    sheet.save(sheet_path)
    has_hat_brim = any(row["region_id"] == "hat_brim" and "lighting" in row["checks"] for row in rows)
    report = {
        "schema_version": 1,
        "kind": "ndc_expression_detail_lighting_review",
        "expression_id": args.expression_id,
        "sources": {
            key: {"path": str(path), "sha256": sha256(path), "size": list(images[key].size)}
            for key, path in paths.items()
        },
        "composition_audit": {"path": str(audit_path), "sha256": sha256(audit_path)},
        "resampling_screen": {
            "uniform_scale": scale,
            "upscale_used": not no_upscale,
            "resample_count": resample_count,
            "no_upscale_status": "PASS" if no_upscale else "FAIL",
            "single_resample_status": "PASS" if single_resample else "FAIL",
            "status": "PASS" if no_upscale and single_resample else "FAIL",
        },
        "regions_spec": {"path": str(regions_path), "sha256": sha256(regions_path)},
        "regions": rows,
        "evidence_sheet": {"path": str(sheet_path), "sha256": sha256(sheet_path)},
        "manual_review": {
            "reviewer": None,
            "whole_images_checked": False,
            "native_100pct_crops_checked": False,
            "nearest_200pct_previews_checked": False,
            "source_detail_status": "NOT_CHECKED",
            "lighting_topology_status": "NOT_CHECKED",
            "hat_brim_shadow_status": "NOT_CHECKED" if has_hat_brim else "NOT_APPLICABLE",
            "formal_status": "NOT_CHECKED",
        },
        "warning": "Edge-energy values are screening evidence only. Codex/Terra must review original pixels, 100% crops, 200% nearest previews, and lighting topology before changing manual_review to PASS.",
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0 if no_upscale and single_resample else 2


if __name__ == "__main__":
    raise SystemExit(main())
