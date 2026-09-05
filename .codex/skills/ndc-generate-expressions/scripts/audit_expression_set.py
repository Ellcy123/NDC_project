#!/usr/bin/env python3
"""Audit a profile-isolated NDC expression set and build a visual review sheet."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from review_font import load_review_font

from expression_audit_core import (
    AUDIT_REVISION,
    SET_SD_LIMITS_PP,
    SET_SD_LIMITS_PERFORMANCE_PP,
    aggregate_status,
    analyze_image,
    compare_to_anchor,
    composite_for_review,
    load_json,
    parse_box,
    round_floats,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mechanical set audit for exactly one NDC expression delivery profile."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=("greenscreen", "transparent"))
    parser.add_argument("--legacy-transparent", action="store_true")
    parser.add_argument("--manual-head-box", help="Shared candidate head box x1,y1,x2,y2; use only after visual verification")
    parser.add_argument("--anchor-manual-head-box", help="Calm anchor head box x1,y1,x2,y2")
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def resolve_from_manifest(manifest_path: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = manifest_path.parent / path
    return path.resolve()


def load_font(size: int) -> ImageFont.ImageFont:
    return load_review_font(size)


def make_review_sheet(items: list[dict[str, Any]], destination: Path) -> None:
    thumb_width, thumb_height = 320, 270
    columns = min(4, max(1, len(items)))
    rows = max(1, (len(items) + columns - 1) // columns)
    sheet = Image.new("RGB", (columns * thumb_width, rows * thumb_height), (238, 238, 238))
    draw = ImageDraw.Draw(sheet)
    font = load_font(17)
    small = load_font(14)
    for index, item in enumerate(items):
        row, column = divmod(index, columns)
        x0, y0 = column * thumb_width, row * thumb_height
        with Image.open(item["path"]) as opened:
            review = composite_for_review(opened.copy(), item["profile"])
        review.thumbnail((thumb_width - 20, 205), Image.Resampling.LANCZOS)
        paste_x = x0 + (thumb_width - review.width) // 2
        paste_y = y0 + 6
        sheet.paste(review, (paste_x, paste_y))
        draw.rectangle((x0, y0, x0 + thumb_width - 1, y0 + thumb_height - 1), outline=(150, 150, 150), width=1)
        draw.text((x0 + 8, y0 + 214), item["expression_id"], fill=(15, 15, 15), font=font)
        metrics = item["report"]["subject"]
        detail = (
            f"{item['status']} | cov {metrics['coverage_pct']:.2f}% | "
            f"W {metrics['bbox_width_pct']:.2f}% | H {metrics['bbox_height_pct']:.2f}%"
        )
        draw.text((x0 + 8, y0 + 239), detail, fill=(30, 30, 30), font=small)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination)


def main() -> int:
    args = build_parser().parse_args()
    if args.legacy_transparent and args.profile != "transparent":
        print("ERROR: --legacy-transparent requires --profile transparent", file=sys.stderr)
        return 1
    try:
        manifest_path = args.manifest.resolve()
        manifest = load_json(manifest_path)
        character_id = str(manifest["character_id"])
        expressions = manifest["expressions"]
        if not isinstance(expressions, list) or not expressions:
            raise ValueError("Manifest expressions must be a non-empty list")
        profile_entry = manifest["delivery_profiles"][args.profile]
        if not profile_entry.get("required", False):
            raise ValueError(f"Manifest does not require profile {args.profile}")
        manifest_legacy = bool(profile_entry.get("legacy_transparent", False))
        if manifest_legacy != bool(args.legacy_transparent):
            raise ValueError("CLI legacy-transparent flag does not match manifest profile")
        anchor_path = resolve_from_manifest(manifest_path, profile_entry["calm_anchor"])
        shared_box = parse_box(args.manual_head_box)
        anchor_box = parse_box(args.anchor_manual_head_box)
        anchor_report, _ = analyze_image(
            anchor_path,
            args.profile,
            legacy_transparent=args.legacy_transparent,
            manual_head_box=anchor_box,
        )

        expected: dict[str, dict[str, Any]] = {}
        for entry in expressions:
            expression_id = str(entry["expression_id"])
            if expression_id in expected:
                raise ValueError(f"Duplicate expression_id in manifest: {expression_id}")
            expected[expression_id] = entry

        input_dir = args.input_dir.resolve()
        actual_pngs = list(input_dir.glob("*.png"))
        actual_by_name = {path.name: path.resolve() for path in actual_pngs}
        expected_names = {f"{character_id}_{expression_id}.png" for expression_id in expected}
        missing = sorted(expected_names - set(actual_by_name))
        extras = sorted(set(actual_by_name) - expected_names)
        items: list[dict[str, Any]] = []
        status_parts: list[str] = []
        hashes: dict[str, list[str]] = {}

        for expression_id, entry in expected.items():
            name = f"{character_id}_{expression_id}.png"
            if name not in actual_by_name:
                continue
            path = actual_by_name[name]
            report, _ = analyze_image(
                path,
                args.profile,
                legacy_transparent=args.legacy_transparent,
                manual_head_box=anchor_box if expression_id == "calm" else shared_box,
            )
            comparison = compare_to_anchor(
                report,
                anchor_report,
                state_class=str(entry.get("class", "basic_emotion")),
                pose_exception=bool(entry.get("pose_exception", False)),
            )
            status = aggregate_status((report["mechanical_status"], comparison["status"]))
            status_parts.append(status)
            hashes.setdefault(report["sha256"], []).append(expression_id)
            items.append(
                {
                    "expression_id": expression_id,
                    "path": path,
                    "profile": args.profile,
                    "class": entry.get("class"),
                    "pose_exception": bool(entry.get("pose_exception", False)),
                    "status": status,
                    "report": report,
                    "anchor_comparison": comparison,
                }
            )

        if missing or extras:
            status_parts.append("FAIL")
        duplicate_hash_groups = [ids for ids in hashes.values() if len(ids) > 1]
        if duplicate_hash_groups:
            # Identical bytes under different expression IDs can be legitimate only
            # after a semantic reuse decision, which mechanical checks cannot make.
            status_parts.append("NOT_CHECKED")

        non_action_items = [
            item for item in items if item["class"] != "action_state" and not item["pose_exception"]
        ]
        non_action_entries = [
            entry for entry in expressions
            if entry.get("class") != "action_state" and not bool(entry.get("pose_exception", False))
        ]
        performance_records_valid = all(
            isinstance(entry.get("performance_delta"), dict)
            and entry["performance_delta"].get("viewpoint_change") is False
            for entry in non_action_entries
        )
        performance_motion_present = any(
            any(
                str(entry["performance_delta"].get(field, "none")).strip().lower() != "none"
                for field in ("shoulders", "upper_torso", "head_neck", "gaze", "garment_response")
            )
            for entry in non_action_entries
            if isinstance(entry.get("performance_delta"), dict)
        )
        performance_motion_enabled = performance_records_valid and performance_motion_present
        set_limits = SET_SD_LIMITS_PERFORMANCE_PP if performance_motion_enabled else SET_SD_LIMITS_PP
        set_variation: dict[str, Any] = {}
        for key, limit in set_limits.items():
            values = [float(item["report"]["subject"][key]) for item in non_action_items]
            sd = statistics.pstdev(values) if len(values) >= 2 else 0.0
            gate_status = "PASS" if sd <= limit + 1e-9 else "FAIL"
            if gate_status == "FAIL":
                status_parts.append("FAIL")
            set_variation[key] = {
                "population_sd_pp": sd,
                "limit_pp": limit,
                "status": gate_status,
                "sample_count": len(values),
            }

        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        review_sheet = output_dir / "expression_set_review_sheet.png"
        make_review_sheet(items, review_sheet)
        metrics_csv = output_dir / "expression_set_metrics.csv"
        with metrics_csv.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=(
                    "expression_id",
                    "class",
                    "pose_exception",
                    "status",
                    "coverage_pct",
                    "bbox_width_pct",
                    "bbox_height_pct",
                    "centroid_x_pct",
                    "centroid_y_pct",
                    "sha256",
                ),
            )
            writer.writeheader()
            for item in items:
                subject = item["report"]["subject"]
                writer.writerow(
                    {
                        "expression_id": item["expression_id"],
                        "class": item["class"],
                        "pose_exception": item["pose_exception"],
                        "status": item["status"],
                        "coverage_pct": subject["coverage_pct"],
                        "bbox_width_pct": subject["bbox_width_pct"],
                        "bbox_height_pct": subject["bbox_height_pct"],
                        "centroid_x_pct": subject["centroid_x_pct"],
                        "centroid_y_pct": subject["centroid_y_pct"],
                        "sha256": item["report"]["sha256"],
                    }
                )

        set_status = aggregate_status(status_parts)
        audit = round_floats(
            {
                "schema_version": 1,
                "audit_revision": AUDIT_REVISION,
                "manifest": str(manifest_path),
                "character_id": character_id,
                "profile": args.profile,
                "legacy_transparent": bool(args.legacy_transparent),
                "profile_spec": anchor_report["profile_spec"],
                "calm_anchor": str(anchor_path),
                "expected_files": sorted(expected_names),
                "actual_files": sorted(actual_by_name),
                "missing_files": missing,
                "extra_files": extras,
                "duplicate_sha256_expression_groups": duplicate_hash_groups,
                "performance_motion_enabled": performance_motion_enabled,
                "set_sd_limits_pp": set_limits,
                "set_variation_non_action": set_variation,
                "expressions": [
                    {
                        "expression_id": item["expression_id"],
                        "path": str(item["path"]),
                        "class": item["class"],
                        "pose_exception": item["pose_exception"],
                        "status": item["status"],
                        "mechanical_status": item["report"]["mechanical_status"],
                        "anchor_status": item["anchor_comparison"]["status"],
                        "sha256": item["report"]["sha256"],
                    }
                    for item in items
                ],
                "artifacts": {
                    "metrics_csv": str(metrics_csv),
                    "review_sheet": str(review_sheet),
                },
                "set_status": set_status,
                "formal_status": "NOT_CHECKED",
                "formal_status_note": "Review sheet still needs explicit identity, costume, pose/gaze, style, and expression-semantic approval.",
            }
        )
        audit_path = output_dir / "expression_set_audit.json"
        write_json(audit_path, audit)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"SET_AUDIT: {set_status}")
    print(f"REPORT: {audit_path}")
    if set_status == "FAIL":
        return 2
    if set_status == "NOT_CHECKED":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
