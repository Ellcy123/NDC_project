#!/usr/bin/env python3
"""Validate fail-closed NDC character delivery receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED_GATE_STATUS = {"PASS", "FAIL", "NOT_CHECKED"}
REQUIRED_GATES = {
    "card": {
        "ratio",
        "dimensions",
        "provenance",
        "layout",
        "required_views",
        "fullbody_alignment",
        "empty_hands_and_anatomy",
        "identity",
        "style",
        "prompt_lock",
        "technical_normalization",
    },
    "portrait_legacy_transparent": {
        "ratio",
        "dimensions",
        "provenance",
        "identity",
        "hair_shape_and_color",
        "portrait_style",
        "transparent_background",
        "silhouette_black",
        "silhouette_white",
        "silhouette_red",
        "prompt_lock",
        "technical_normalization",
    },
    "portrait": {
        "ratio",
        "dimensions",
        "provenance",
        "identity",
        "hair_shape_and_color",
        "portrait_style",
        "background_conformance",
        "prompt_lock",
        "technical_normalization",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True, type=Path)
    return parser.parse_args()


def require_path(
    value: object,
    label: str,
    errors: list[str],
    must_be_file: bool = True,
) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty path string")
        return None
    path = Path(value).resolve()
    if (must_be_file and not path.is_file()) or (not must_be_file and not path.exists()):
        expected = "file" if must_be_file else "file or directory"
        errors.append(f"{label} must be an existing {expected}: {path}")
        return None
    return path


def validate_reference_list(
    data: dict,
    key: str,
    errors: list[str],
    allow_empty: bool = False,
    allow_directory: bool = False,
) -> None:
    items = data.get(key)
    if not isinstance(items, list) or (not allow_empty and not items):
        errors.append(f"reference_manifest.{key} must be a {'possibly empty' if allow_empty else 'non-empty'} list")
        return
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"reference_manifest.{key}[{index}] must be an object")
            continue
        require_path(
            item.get("path"),
            f"reference_manifest.{key}[{index}].path",
            errors,
            must_be_file=not allow_directory,
        )
        if not isinstance(item.get("role"), str) or not item["role"].strip():
            errors.append(f"reference_manifest.{key}[{index}].role must be non-empty")
        if item.get("approval_status") not in {"APPROVED", "REJECTED", "REFERENCE_ONLY"}:
            errors.append(
                f"reference_manifest.{key}[{index}].approval_status must be APPROVED, REJECTED, or REFERENCE_ONLY"
            )


def main() -> None:
    args = parse_args()
    receipt_path = args.receipt.resolve()
    if not receipt_path.is_file():
        raise SystemExit(f"receipt does not exist: {receipt_path}")
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    asset_type = data.get("asset_type")
    if asset_type not in {"card", "portrait"}:
        errors.append("asset_type must be card or portrait")

    references = data.get("reference_manifest")
    if not isinstance(references, dict):
        errors.append("reference_manifest must be an object")
    else:
        validate_reference_list(references, "identity_sources", errors)
        validate_reference_list(references, "style_sources", errors, allow_directory=True)
        validate_reference_list(references, "landed_peer_comparisons", errors)
        validate_reference_list(references, "rejected_examples", errors, allow_empty=True)
        style_sources = references.get("style_sources", [])
        style_paths = [
            Path(item["path"]).resolve()
            for item in style_sources
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        ]
        if not any(path.is_dir() for path in style_paths):
            errors.append("reference_manifest.style_sources must include the matching self-check library directory")
        if not any(path.is_file() for path in style_paths):
            errors.append("reference_manifest.style_sources must include the branch style-only reference file")

    mechanical_path = require_path(data.get("mechanical_audit"), "mechanical_audit", errors)
    if mechanical_path:
        mechanical = json.loads(mechanical_path.read_text(encoding="utf-8"))
        if mechanical.get("mechanical_status") != "PASS":
            errors.append("mechanical_audit.mechanical_status must be PASS for formal delivery")
        if mechanical.get("formal_status") != "NOT_CHECKED":
            errors.append("mechanical audit must not claim a formal pass")
        receipt_background = data.get("required_background")
        if asset_type == "portrait" and receipt_background is not None:
            background_map = {
                "TRANSPARENT": "transparent",
                "OPAQUE_PAPER": "opaque-paper",
                "OPAQUE_WHITE": "opaque-white",
            }
            expected_mechanical_background = background_map.get(receipt_background)
            if expected_mechanical_background is None:
                errors.append("required_background must be TRANSPARENT, OPAQUE_PAPER, or OPAQUE_WHITE")
            elif mechanical.get("expected_background") != expected_mechanical_background:
                errors.append("mechanical_audit.expected_background does not match required_background")

    style_path = require_path(data.get("style_review_manifest"), "style_review_manifest", errors)
    if style_path:
        style = json.loads(style_path.read_text(encoding="utf-8"))
        if style.get("all_sources_covered") is not True:
            errors.append("style_review_manifest.all_sources_covered must be true")

    if data.get("whole_image_checked") is not True:
        errors.append("whole_image_checked must be true")
    if data.get("local_tile_coverage_complete") is not True:
        errors.append("local_tile_coverage_complete must be true")

    gates = data.get("gates")
    if asset_type == "portrait" and data.get("required_background") is None:
        required = REQUIRED_GATES["portrait_legacy_transparent"]
    else:
        required = set(REQUIRED_GATES.get(asset_type, set()))
        if asset_type == "portrait" and data.get("required_background") == "TRANSPARENT":
            required.update({"silhouette_black", "silhouette_white", "silhouette_red"})
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        gates = {}
    missing = sorted(required - set(gates))
    if missing:
        errors.append(f"missing required gates: {', '.join(missing)}")

    statuses = []
    for name in sorted(required & set(gates)):
        gate = gates[name]
        if not isinstance(gate, dict):
            errors.append(f"gates.{name} must be an object")
            continue
        status = gate.get("status")
        statuses.append(status)
        if status not in ALLOWED_GATE_STATUS:
            errors.append(f"gates.{name}.status must be PASS, FAIL, or NOT_CHECKED")
        evidence = gate.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(item, str) and item.strip() for item in evidence
        ):
            errors.append(f"gates.{name}.evidence must be a non-empty list of strings")

    expected_formal_status = "FORMAL_PASS" if statuses and all(item == "PASS" for item in statuses) else "BLOCKED"
    if data.get("formal_status") != expected_formal_status:
        errors.append(
            f"formal_status must be {expected_formal_status} for the recorded gate statuses"
        )

    if errors:
        print("RECEIPT_INVALID")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"RECEIPT_VALID: {expected_formal_status}")


if __name__ == "__main__":
    main()
