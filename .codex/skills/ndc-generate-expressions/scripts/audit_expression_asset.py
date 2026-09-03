#!/usr/bin/env python3
"""Audit one NDC expression image against one delivery profile and calm anchor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from expression_audit_core import (
    aggregate_status,
    analyze_image,
    compare_to_anchor,
    parse_box,
    save_mask,
    save_overlay,
    save_transparent_previews,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Mechanical screening for one NDC expression asset. It never grants "
            "formal artistic approval."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="PNG expression asset")
    parser.add_argument("--profile", required=True, choices=("greenscreen", "transparent"))
    parser.add_argument(
        "--legacy-transparent",
        action="store_true",
        help="Use 1152x900 transparent size. Valid only when explicitly requested for a legacy Unit 1 target.",
    )
    parser.add_argument("--anchor", type=Path, help="Same-character, same-profile calm anchor")
    parser.add_argument(
        "--state-class",
        default="basic_emotion",
        choices=("basic_emotion", "micro_expression", "narrative_state", "action_state"),
    )
    parser.add_argument("--pose-exception", action="store_true")
    parser.add_argument("--manual-head-box", help="Candidate head box as x1,y1,x2,y2")
    parser.add_argument("--anchor-manual-head-box", help="Anchor head box as x1,y1,x2,y2")
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.legacy_transparent and args.profile != "transparent":
        print("ERROR: --legacy-transparent is valid only for --profile transparent", file=sys.stderr)
        return 1
    if args.pose_exception and args.state_class != "action_state":
        print("ERROR: --pose-exception is valid only for --state-class action_state", file=sys.stderr)
        return 1

    try:
        candidate_box = parse_box(args.manual_head_box)
        anchor_box = parse_box(args.anchor_manual_head_box)
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        report, mask = analyze_image(
            args.input,
            args.profile,
            legacy_transparent=args.legacy_transparent,
            manual_head_box=candidate_box,
        )
        report["state_class"] = args.state_class
        report["pose_exception"] = bool(args.pose_exception)

        if args.anchor:
            anchor_report, _ = analyze_image(
                args.anchor,
                args.profile,
                legacy_transparent=args.legacy_transparent,
                manual_head_box=anchor_box,
            )
            report["anchor_comparison"] = compare_to_anchor(
                report,
                anchor_report,
                state_class=args.state_class,
                pose_exception=args.pose_exception,
            )
            report["mechanical_status"] = aggregate_status(
                (report["mechanical_status"], report["anchor_comparison"]["status"])
            )
        elif args.input.stem.lower().endswith("_calm"):
            report["anchor_comparison"] = None
        else:
            report["anchor_comparison"] = {
                "status": "NOT_CHECKED",
                "detail": "Non-calm expression requires a same-profile calm anchor.",
            }
            report["mechanical_status"] = aggregate_status((report["mechanical_status"], "NOT_CHECKED"))

        mask_path = output_dir / "subject_mask.png"
        overlay_path = output_dir / "geometry_overlay.png"
        save_mask(mask, mask_path)
        save_overlay(args.input.resolve(), report, overlay_path)
        artifacts = {
            "subject_mask": str(mask_path.resolve()),
            "geometry_overlay": str(overlay_path.resolve()),
        }
        if args.profile == "transparent":
            artifacts["background_previews"] = save_transparent_previews(args.input.resolve(), output_dir)
        report["artifacts"] = artifacts
        report_path = output_dir / "mechanical_audit.json"
        write_json(report_path, report)
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"MECHANICAL_AUDIT: {report['mechanical_status']}")
    print(f"REPORT: {report_path}")
    if report["mechanical_status"] == "FAIL":
        return 2
    if report["mechanical_status"] == "NOT_CHECKED":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
