#!/usr/bin/env python3
"""Validate an NDC expression profile receipt against schema 12."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

PASS = "PASS"
FORMAL_PASS = "FORMAL_PASS"
HEX = set("0123456789abcdef")
PROFILE_SPECS = {
    "transparent": {"canvas": [1164, 916], "mode": "RGBA", "background": "alpha_0"},
    "greenscreen": {"canvas": [1536, 1024], "mode": "RGB", "background": "#00FF2B"},
}
LEGACY_TRANSPARENT = {"canvas": [1152, 900], "mode": "RGBA", "background": "alpha_0"}
PASS_FIELDS = (
    "artistic_status", "identity_status", "viewpoint_status", "style_status",
    "texture_status", "detail_lighting_status", "expression_status", "profile_status",
)
CONTINUITY_FIELDS = (
    "identity", "viewpoint", "style_texture", "detail_lighting",
    "expression_separability", "thumbnail_readability", "geometry",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path, field: str, invalid: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        invalid.append(f"{field}: unreadable JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        invalid.append(f"{field}: expected JSON object")
        return {}
    return value


def resolve(receipt: Path, value: Any, field: str, invalid: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        invalid.append(f"{field}: required path")
        return None
    path = Path(value)
    if not path.is_absolute():
        path = receipt.parent / path
    path = path.resolve()
    if not path.is_file():
        invalid.append(f"{field}: missing file: {path}")
        return None
    return path


def valid_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX


def check_hash(path: Path | None, claimed: Any, field: str, invalid: list[str]) -> None:
    if not valid_hash(claimed):
        invalid.append(f"{field}: expected 64 lowercase hex characters")
    elif path is not None and sha256(path) != claimed:
        invalid.append(f"{field}: current SHA-256 mismatch")


def require_pass(value: Any, field: str, blocked: list[str]) -> None:
    if value != PASS:
        blocked.append(f"{field}: expected PASS")


def check_native_rgba(path: Path | None, field: str, invalid: list[str]) -> None:
    if path is None:
        return
    try:
        image = Image.open(path)
        if image.mode != "RGBA":
            invalid.append(f"{field}: expected RGBA, got {image.mode}")
            return
        low, high = image.getchannel("A").getextrema()
        if low != 0:
            invalid.append(f"{field}: no fully transparent pixels")
        if high == 0:
            invalid.append(f"{field}: Alpha is empty")
    except (OSError, ValueError) as exc:
        invalid.append(f"{field}: unreadable image: {exc}")


def check_profile_asset(path: Path | None, profile: str, spec: dict[str, Any], field: str, invalid: list[str]) -> None:
    if path is None:
        return
    try:
        image = Image.open(path)
        expected_size = tuple(spec["canvas"])
        if image.size != expected_size:
            invalid.append(f"{field}: expected {expected_size}, got {image.size}")
        if image.mode != spec["mode"]:
            invalid.append(f"{field}: expected mode {spec['mode']}, got {image.mode}")
            return
        if profile == "transparent":
            low, high = image.getchannel("A").getextrema()
            if low != 0 or high == 0:
                invalid.append(f"{field}: expected non-empty foreground over Alpha 0 background")
        else:
            rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
            green = np.array([0, 255, 43], dtype=np.uint8)
            corners = np.array([rgb[0, 0], rgb[0, -1], rgb[-1, 0], rgb[-1, -1]])
            if not np.all(corners == green):
                invalid.append(f"{field}: all four corners must be exact #00FF2B")
    except (OSError, ValueError) as exc:
        invalid.append(f"{field}: unreadable image: {exc}")


def check_manual_alpha_evidence(receipt: Path, item: dict[str, Any], index: int, native_path: Path | None,
                                native_hash: Any, invalid: list[str], blocked: list[str]) -> None:
    field = f"expressions[{index}].manual_alpha_return"
    removal = item.get("manual_alpha_return")
    if not isinstance(removal, dict):
        invalid.append(f"{field}: expected object")
        return
    if item.get("background_removal") is not None:
        invalid.append(f"expressions[{index}].background_removal: not allowed in schema 12")
    if removal.get("method") != "USER_RETURNED_MANUAL_BACKGROUND_PROCESSING":
        invalid.append(f"{field}.method: expected USER_RETURNED_MANUAL_BACKGROUND_PROCESSING")
    if removal.get("processor_authority") != "USER_MANUAL_BACKGROUND_PROCESSING":
        invalid.append(f"{field}.processor_authority: expected USER_MANUAL_BACKGROUND_PROCESSING")
    if removal.get("handoff_edit_mode") != "IN_PLACE_OVERWRITE":
        invalid.append(f"{field}.handoff_edit_mode: expected IN_PLACE_OVERWRITE")
    if removal.get("codex_background_removal_used") is not False:
        invalid.append(f"{field}.codex_background_removal_used: must be false")
    if removal.get("user_returned") is not True:
        invalid.append(f"{field}.user_returned: must be true")
    for status in ("protected_white_status", "white_fringe_status", "formal_status"):
        require_pass(removal.get(status), f"{field}.{status}", blocked)

    handoff = removal.get("handoff_source")
    handoff_path: Path | None = None
    handoff_manifest_path: Path | None = None
    if not isinstance(handoff, dict):
        invalid.append(f"{field}.handoff_source: expected object")
    else:
        handoff_path = resolve(receipt, handoff.get("path"), f"{field}.handoff_source.path", invalid)
    handoff_manifest_path = resolve(receipt, removal.get("handoff_manifest"), f"{field}.handoff_manifest", invalid)
    if handoff_path is not None and handoff_manifest_path is not None and isinstance(handoff, dict):
        manifest = load_json(handoff_manifest_path, f"{field}.handoff_manifest", invalid)
        rows = manifest.get("expressions")
        if not isinstance(rows, list):
            invalid.append(f"{field}.handoff_manifest.expressions: expected list")
        else:
            source_row = next((row for row in rows if isinstance(row, dict) and row.get("expression_id") == item.get("expression_id")), None)
            if source_row is None:
                invalid.append(f"{field}.handoff_manifest: missing expression_id {item.get('expression_id')!r}")
            else:
                if str(source_row.get("sha256", "")).lower() != str(handoff.get("sha256", "")).lower():
                    invalid.append(f"{field}.handoff_source.sha256: must match the pre-edit manifest row")
                if source_row.get("handoff_file") != handoff_path.name:
                    invalid.append(f"{field}.handoff_source.path: filename must match the pre-edit manifest row")

    returned = removal.get("returned_native")
    if not isinstance(returned, dict):
        invalid.append(f"{field}.returned_native: expected object")
    else:
        returned_path = resolve(receipt, returned.get("path"), f"{field}.returned_native.path", invalid)
        check_hash(returned_path, returned.get("sha256"), f"{field}.returned_native.sha256", invalid)
        if returned.get("sha256") != native_hash:
            invalid.append(f"{field}.returned_native.sha256: must match native_rgba_sha256")
        if native_path is not None and returned_path is not None and returned_path != native_path:
            invalid.append(f"{field}.returned_native.path: must resolve to native_rgba")

    edge_path = resolve(receipt, removal.get("edge_review"), f"{field}.edge_review", invalid)
    if edge_path:
        edge = load_json(edge_path, f"{field}.edge_review", invalid)
        if edge.get("codex_background_removal_used") is not False:
            invalid.append(f"{field}.edge_review.codex_background_removal_used: must be false")
        source = edge.get("source", {})
        if not isinstance(source, dict) or source.get("sha256") != native_hash:
            invalid.append(f"{field}.edge_review.source.sha256: must match native_rgba_sha256")
        for status in ("protected_white_status", "white_fringe_status", "silhouette_status", "formal_status"):
            require_pass(edge.get(status), f"{field}.edge_review.{status}", blocked)
        previews = edge.get("previews")
        if not isinstance(previews, dict):
            invalid.append(f"{field}.edge_review.previews: expected object")
        else:
            for name in ("white", "mid_gray", "dark_gray", "black", "exact_green"):
                resolve(edge_path, previews.get(name), f"{field}.edge_review.previews.{name}", invalid)
        resolve(edge_path, edge.get("alpha_visualization"), f"{field}.edge_review.alpha_visualization", invalid)


def check_review_file(receipt: Path, value: Any, field: str, invalid: list[str], blocked: list[str]) -> dict[str, Any]:
    path = resolve(receipt, value, field, invalid)
    if path is None:
        return {}
    record = load_json(path, field, invalid)
    status = record.get("formal_status", record.get("mechanical_status", record.get("status")))
    if status != PASS:
        blocked.append(f"{field}: review status is not PASS")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt_path = args.receipt.resolve()
    invalid: list[str] = []
    blocked: list[str] = []
    receipt = load_json(receipt_path, "receipt", invalid)

    if receipt.get("schema_version") != 12:
        invalid.append("schema_version: expected 12")
    if receipt.get("artifact_class") != "PROFILE_DELIVERY_RECEIPT":
        invalid.append("artifact_class: expected PROFILE_DELIVERY_RECEIPT")
    if not isinstance(receipt.get("character_id"), str) or not receipt.get("character_id"):
        invalid.append("character_id: required")

    profile = receipt.get("profile")
    if profile not in PROFILE_SPECS:
        invalid.append("profile: expected transparent or greenscreen")
        profile = "transparent"
    spec = receipt.get("profile_spec")
    if not isinstance(spec, dict):
        invalid.append("profile_spec: expected object")
        spec = PROFILE_SPECS[profile]
    allowed_specs = [PROFILE_SPECS[profile]]
    if profile == "transparent" and receipt.get("legacy_unit1_1152x900") is True:
        allowed_specs.append(LEGACY_TRANSPARENT)
    if spec not in allowed_specs:
        invalid.append(f"profile_spec: does not match exact {profile} specification")

    portrait = receipt.get("portrait_source")
    if not isinstance(portrait, dict):
        invalid.append("portrait_source: expected object")
        portrait = {}
    portrait_path = resolve(receipt_path, portrait.get("path"), "portrait_source.path", invalid)
    check_hash(portrait_path, portrait.get("sha256"), "portrait_source.sha256", invalid)
    if portrait.get("authority") != "USER_CONFIRMED_COMPLETED_PORTRAIT":
        invalid.append("portrait_source.authority: expected USER_CONFIRMED_COMPLETED_PORTRAIT")
    if portrait.get("portrait_completion_used") is not False:
        invalid.append("portrait_source.portrait_completion_used: must be false")
    require_pass(portrait.get("status"), "portrait_source.status", blocked)
    resolve(receipt_path, receipt.get("expression_manifest"), "expression_manifest", invalid)
    resolve(receipt_path, receipt.get("approved_asset_census"), "approved_asset_census", invalid)

    expressions = receipt.get("expressions")
    if not isinstance(expressions, list) or not expressions:
        invalid.append("expressions: expected non-empty list")
        expressions = []
    seen: set[str] = set()
    for index, value in enumerate(expressions):
        field = f"expressions[{index}]"
        if not isinstance(value, dict):
            invalid.append(f"{field}: expected object")
            continue
        expression_id = value.get("expression_id")
        if not isinstance(expression_id, str) or not expression_id:
            invalid.append(f"{field}.expression_id: required")
        elif expression_id in seen:
            invalid.append(f"{field}.expression_id: duplicate {expression_id}")
        else:
            seen.add(expression_id)

        native = resolve(receipt_path, value.get("native_rgba"), f"{field}.native_rgba", invalid)
        native_hash = value.get("native_rgba_sha256")
        check_hash(native, native_hash, f"{field}.native_rgba_sha256", invalid)
        check_native_rgba(native, f"{field}.native_rgba", invalid)
        asset = resolve(receipt_path, value.get("profile_asset"), f"{field}.profile_asset", invalid)
        check_hash(asset, value.get("profile_asset_sha256"), f"{field}.profile_asset_sha256", invalid)
        check_profile_asset(asset, profile, spec, f"{field}.profile_asset", invalid)
        check_manual_alpha_evidence(receipt_path, value, index, native, native_hash, invalid, blocked)
        for gate in PASS_FIELDS:
            require_pass(value.get(gate), f"{field}.{gate}", blocked)

        cross = check_review_file(receipt_path, value.get("cross_profile_source_audit"),
                                  f"{field}.cross_profile_source_audit", invalid, blocked)
        shared_hash = cross.get("native_rgba_sha256", cross.get("shared_native_rgba_sha256"))
        if shared_hash != native_hash:
            invalid.append(f"{field}.cross_profile_source_audit: shared native hash mismatch")
        check_review_file(receipt_path, value.get("profile_guide_review"),
                          f"{field}.profile_guide_review", invalid, blocked)
        check_review_file(receipt_path, value.get("mechanical_audit"),
                          f"{field}.mechanical_audit", invalid, blocked)

    continuity = receipt.get("continuity_review")
    if not isinstance(continuity, dict):
        invalid.append("continuity_review: expected object")
        continuity = {}
    if continuity.get("whole_set_checked") is not True:
        blocked.append("continuity_review.whole_set_checked: expected true")
    for field in CONTINUITY_FIELDS:
        require_pass(continuity.get(field), f"continuity_review.{field}", blocked)
    if receipt.get("final_status") != FORMAL_PASS:
        blocked.append("final_status: expected FORMAL_PASS")

    status = "INVALID" if invalid else "BLOCKED" if blocked else FORMAL_PASS
    report = {"schema_version": 1, "kind": "ndc_expression_receipt_validation",
              "receipt": str(receipt_path), "status": status, "invalid": invalid, "blocked": blocked}
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if invalid:
        print("RECEIPT_INVALID")
        for message in invalid:
            print(f"- {message}")
        return 1
    if blocked:
        print("RECEIPT_VALID: BLOCKED")
        for message in blocked:
            print(f"- {message}")
        return 2
    print("RECEIPT_VALID: FORMAL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
