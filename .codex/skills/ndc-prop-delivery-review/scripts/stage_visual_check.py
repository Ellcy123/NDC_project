#!/usr/bin/env python3
"""Fail-closed validator for NDC per-stage visual self-check records."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA = "ndc-stage-visual-self-check/v1"
ALLOWED_STATUSES = {"PASS", "FAIL", "NOT_CHECKED"}
REQUIRED_VIEW_KINDS = {"whole_100", "local_200_or_tiles"}
IMPORTANCE_LIMITS = {"H1": 0.10, "H2": 0.20, "H3": 0.30}
TYPE7_REQUIRED_CRITERIA = {
    "mandatory_direct_image_container_rule",
    "source_anchor_visual_comparison",
    "container_height_and_observation_direction",
    "visual_self_check",
}
TYPE7_CHILD_VISIBILITY_CRITERIA = {
    "container_child_complete_visibility",
    "container_identity_and_child_visibility",
}
TYPE7_HEIGHT_CLASSES = {"low", "mid", "high"}
TYPE7_VIEW_DIRECTIONS = {"downward", "level", "upward"}
HOTSPOT_REQUIRED_VIEW_KINDS = {"alpha_only", "checkerboard", "parent_overlay"}
HOTSPOT_REQUIRED_CRITERIA = {
    "semantic_target_completeness",
    "transparent_negative_space_justification",
    "unrelated_parent_pixel_exclusion",
    "adjacent_interactable_exclusion",
    "click_mislead_risk",
    "parent_overlay_semantic_alignment",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_text(value: Any, field: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field}: missing non-empty text")
        return ""
    return value.strip()


def nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(entry, str) and entry.strip() for entry in value)
    )


def resolve_record_path(raw: str, record_dir: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = record_dir / path
    return path.resolve()


def validate_artifact(
    artifact: Any,
    field: str,
    record_dir: Path,
    errors: list[str],
) -> Path | None:
    if not isinstance(artifact, dict):
        errors.append(f"{field}: must be an object")
        return None
    raw_path = require_text(artifact.get("path"), f"{field}.path", errors)
    expected_hash = require_text(artifact.get("sha256"), f"{field}.sha256", errors).upper()
    if not raw_path:
        return None
    path = resolve_record_path(raw_path, record_dir)
    if not path.is_file():
        errors.append(f"{field}.path: file does not exist: {path}")
        return path
    if expected_hash and sha256(path) != expected_hash:
        errors.append(f"{field}.sha256: stale or mismatched hash for {path}")
    return path


def validate_type7_visual_context(data: dict[str, Any], errors: list[str]) -> None:
    """Require source-derived visual evidence for a passing Type 7 record."""

    role = data.get("role")
    if not isinstance(role, str) or not role.startswith("container_type7"):
        return
    if data.get("visual_check_status") != "PASS":
        return

    inputs = data.get("inputs")
    input_roles = {
        item.get("role")
        for item in inputs
        if isinstance(item, dict) and isinstance(item.get("role"), str)
    } if isinstance(inputs, list) else set()
    if "original_scene_visual_anchor" not in input_roles:
        errors.append(
            "Type7: inputs must include an original_scene_visual_anchor with a current hash"
        )

    views = data.get("views")
    view_kinds = {
        item.get("kind")
        for item in views
        if isinstance(item, dict) and isinstance(item.get("kind"), str)
    } if isinstance(views, list) else set()
    if "source_anchor_side_by_side" not in view_kinds:
        errors.append(
            "Type7: views must include source_anchor_side_by_side visual comparison evidence"
        )

    criteria = data.get("criteria")
    criterion_by_name = {
        item.get("name"): item
        for item in criteria
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    } if isinstance(criteria, list) else {}
    for name in sorted(TYPE7_REQUIRED_CRITERIA):
        item = criterion_by_name.get(name)
        if not isinstance(item, dict) or item.get("applicable") is not True or item.get("status") != "PASS":
            errors.append(f"Type7: required applicable PASS criterion missing: {name}")
    if not any(
        isinstance(criterion_by_name.get(name), dict)
        and criterion_by_name[name].get("applicable") is True
        and criterion_by_name[name].get("status") == "PASS"
        for name in TYPE7_CHILD_VISIBILITY_CRITERIA
    ):
        errors.append(
            "Type7: require one applicable PASS child/container identity and full-visibility criterion"
        )

    context = data.get("type7_visual_context")
    if not isinstance(context, dict):
        errors.append("Type7: type7_visual_context is required for a passing record")
        return
    require_text(context.get("container_identity"), "Type7.type7_visual_context.container_identity", errors)
    require_text(context.get("environment_derivation"), "Type7.type7_visual_context.environment_derivation", errors)
    require_text(context.get("viewpoint_rationale"), "Type7.type7_visual_context.viewpoint_rationale", errors)
    if context.get("height_class") not in TYPE7_HEIGHT_CLASSES:
        errors.append("Type7.type7_visual_context.height_class: must be low, mid, or high")
    if context.get("observation_direction") not in TYPE7_VIEW_DIRECTIONS:
        errors.append(
            "Type7.type7_visual_context.observation_direction: must be downward, level, or upward"
        )
    if context.get("first_person_view") is not True:
        errors.append("Type7.type7_visual_context.first_person_view: must be true")
    if context.get("interior_composition_method") != "direct_image_generation":
        errors.append(
            "Type7.type7_visual_context.interior_composition_method: must be direct_image_generation"
        )
    if context.get("child_fully_contained") is not True:
        errors.append("Type7.type7_visual_context.child_fully_contained: must be true")


def is_coordinate_hotspot_role(role: Any) -> bool:
    """Return whether a passing stage owns a coordinate-bearing clickable Alpha."""

    if not isinstance(role, str):
        return False
    normalized = role.strip().lower().replace("-", "_")
    return (
        "type6" in normalized
        or "hotspot" in normalized
        or "child_map" in normalized
        or normalized.startswith("map_")
        or normalized.endswith("_map")
        or "_map_" in normalized
    )


def validate_hotspot_visual_context(data: dict[str, Any], errors: list[str]) -> None:
    """Fail closed on semantic omissions and misleading neighboring hit regions."""

    if data.get("visual_check_status") != "PASS" or not is_coordinate_hotspot_role(data.get("role")):
        return

    outputs = data.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != 1:
        errors.append("Hotspot: one PASS record must bind exactly one coordinate-bearing output")

    views = data.get("views")
    view_kinds = {
        item.get("kind")
        for item in views
        if isinstance(item, dict) and isinstance(item.get("kind"), str)
    } if isinstance(views, list) else set()
    missing_views = HOTSPOT_REQUIRED_VIEW_KINDS - view_kinds
    if missing_views:
        errors.append(
            "Hotspot: missing semantic Alpha review views: "
            + ", ".join(sorted(missing_views))
        )

    criteria = data.get("criteria")
    criterion_by_name = {
        item.get("name"): item
        for item in criteria
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    } if isinstance(criteria, list) else {}
    for name in sorted(HOTSPOT_REQUIRED_CRITERIA):
        item = criterion_by_name.get(name)
        if not isinstance(item, dict) or item.get("applicable") is not True or item.get("status") != "PASS":
            errors.append(f"Hotspot: required applicable PASS criterion missing: {name}")

    context = data.get("hotspot_visual_context")
    if not isinstance(context, dict):
        errors.append("Hotspot: hotspot_visual_context is required for a passing record")
        return
    require_text(context.get("target_identity"), "Hotspot.hotspot_visual_context.target_identity", errors)
    components = context.get("target_components")
    if not nonempty_string_list(components):
        errors.append("Hotspot.hotspot_visual_context.target_components: require complete named components")
    for field in (
        "semantic_extrema_confirmed",
        "complete_visible_planes_confirmed",
        "alpha_only_reviewed",
        "checkerboard_reviewed",
        "parent_overlay_reviewed",
    ):
        if context.get(field) is not True:
            errors.append(f"Hotspot.hotspot_visual_context.{field}: must be true")
    if context.get("missing_target_pixels") is not False:
        errors.append("Hotspot.hotspot_visual_context.missing_target_pixels: must be false")
    if context.get("unrelated_parent_pixels") is not False:
        errors.append("Hotspot.hotspot_visual_context.unrelated_parent_pixels: must be false")
    if context.get("click_mislead_risk") != "none":
        errors.append("Hotspot.hotspot_visual_context.click_mislead_risk: must be none")

    negative_spaces = context.get("transparent_negative_spaces")
    if not isinstance(negative_spaces, list):
        errors.append("Hotspot.hotspot_visual_context.transparent_negative_spaces: must be a list")
    else:
        for index, item in enumerate(negative_spaces):
            label = f"Hotspot.hotspot_visual_context.transparent_negative_spaces[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: must be an object")
                continue
            require_text(item.get("location"), f"{label}.location", errors)
            require_text(item.get("physical_reason"), f"{label}.physical_reason", errors)
            if item.get("intentionally_transparent") is not True:
                errors.append(f"{label}.intentionally_transparent: must be true")

    adjacent_present = context.get("adjacent_interactables_present")
    if not isinstance(adjacent_present, bool):
        errors.append("Hotspot.hotspot_visual_context.adjacent_interactables_present: must be boolean")
    excluded = context.get("excluded_adjacent_interactables")
    if not isinstance(excluded, list) or not all(isinstance(item, str) and item.strip() for item in excluded):
        errors.append("Hotspot.hotspot_visual_context.excluded_adjacent_interactables: must be a string list")
    elif adjacent_present and not excluded:
        errors.append("Hotspot: adjacent interactables are present but none are explicitly excluded")
    if adjacent_present and context.get("adjacent_interactables_alpha_zero") is not True:
        errors.append("Hotspot.hotspot_visual_context.adjacent_interactables_alpha_zero: must be true when neighbors exist")


def validate_record(record_path: Path, required_artifacts: list[Path]) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(record_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"record: cannot read valid JSON: {exc}"]

    if not isinstance(data, dict):
        return ["record: top level must be an object"]

    if data.get("schema") != SCHEMA:
        errors.append(f"schema: expected {SCHEMA}")
    require_text(data.get("stage_id"), "stage_id", errors)
    require_text(data.get("reviewer"), "reviewer", errors)
    require_text(data.get("reviewed_at"), "reviewed_at", errors)

    status = data.get("visual_check_status")
    if status not in ALLOWED_STATUSES:
        errors.append("visual_check_status: must be PASS, FAIL, or NOT_CHECKED")
    elif status != "PASS":
        errors.append(f"visual_check_status: formal progression requires PASS, got {status}")
        require_text(data.get("rework_stage"), "rework_stage", errors)

    record_dir = record_path.parent
    outputs = data.get("outputs")
    output_paths: list[Path] = []
    if not isinstance(outputs, list) or not outputs:
        errors.append("outputs: at least one current stage output is required")
    else:
        for index, artifact in enumerate(outputs):
            path = validate_artifact(artifact, f"outputs[{index}]", record_dir, errors)
            if path is not None:
                output_paths.append(path)

    inputs = data.get("inputs", [])
    if not isinstance(inputs, list):
        errors.append("inputs: must be an array")
    else:
        for index, artifact in enumerate(inputs):
            validate_artifact(artifact, f"inputs[{index}]", record_dir, errors)

    views = data.get("views")
    seen_view_kinds: set[str] = set()
    if not isinstance(views, list) or not views:
        errors.append("views: whole-image and local visual review evidence is required")
    else:
        for index, view in enumerate(views):
            if not isinstance(view, dict):
                errors.append(f"views[{index}]: must be an object")
                continue
            kind = require_text(view.get("kind"), f"views[{index}].kind", errors)
            raw_path = require_text(view.get("path"), f"views[{index}].path", errors)
            if kind:
                seen_view_kinds.add(kind)
            if raw_path:
                path = resolve_record_path(raw_path, record_dir)
                if not path.is_file():
                    errors.append(f"views[{index}].path: file does not exist: {path}")
        tier = data.get("importance_tier")
        if tier is None:
            required_views = REQUIRED_VIEW_KINDS
        elif tier not in IMPORTANCE_LIMITS:
            errors.append("importance_tier: must be H1, H2 or H3")
            required_views = REQUIRED_VIEW_KINDS
        else:
            ratio = data.get("tolerance_ratio")
            if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or ratio < 0 or ratio > IMPORTANCE_LIMITS[tier]:
                errors.append(f"tolerance_ratio: exceeds {IMPORTANCE_LIMITS[tier]:.2f} for {tier}")
            if tier == "H3" and not require_text(data.get("low_salience_basis"), "low_salience_basis", errors):
                pass
            if tier == "H1" and not isinstance(data.get("local_200_required"), bool):
                errors.append("local_200_required: H1 requires an explicit boolean")
            required_views = {"whole_runtime", "whole_100"}
            if tier == "H3":
                required_views = {"whole_runtime"}
            elif tier == "H1" and data.get("local_200_required") is True:
                required_views.add("local_200_or_tiles")
        missing_views = required_views - seen_view_kinds
        if missing_views:
            errors.append("views: missing required kinds: " + ", ".join(sorted(missing_views)))

    criteria = data.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        errors.append("criteria: at least one applicable visual criterion is required")
    else:
        applicable_count = 0
        for index, item in enumerate(criteria):
            if not isinstance(item, dict):
                errors.append(f"criteria[{index}]: must be an object")
                continue
            require_text(item.get("name"), f"criteria[{index}].name", errors)
            applicable = item.get("applicable")
            if not isinstance(applicable, bool):
                errors.append(f"criteria[{index}].applicable: must be boolean")
                continue
            item_status = item.get("status")
            if item_status not in ALLOWED_STATUSES:
                errors.append(f"criteria[{index}].status: must be PASS, FAIL, or NOT_CHECKED")
            finding = require_text(item.get("finding"), f"criteria[{index}].finding", errors)
            if applicable:
                applicable_count += 1
                if item_status != "PASS":
                    errors.append(f"criteria[{index}]: applicable criterion must PASS")
                if not finding:
                    errors.append(f"criteria[{index}]: applicable criterion needs an explicit finding")
        if applicable_count == 0:
            errors.append("criteria: at least one criterion must be applicable")

    validate_type7_visual_context(data, errors)
    validate_hotspot_visual_context(data, errors)

    required_resolved = [path.resolve() for path in required_artifacts]
    for required in required_resolved:
        if not required.is_file():
            errors.append(f"required artifact does not exist: {required}")
        elif required not in output_paths:
            errors.append(f"required artifact is not bound to this passing record: {required}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a fail-closed NDC stage visual self-check record."
    )
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--batch", type=Path, help="Check current prop-batch facts, scope and dependency bindings.")
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        type=Path,
        help="Current output that must be hash-bound to the record; repeat as needed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    record_path = args.record.resolve()
    errors = validate_record(record_path, args.artifact)
    if args.batch:
        from workflow_state import load_batch, read, resolve, review_errors
        try:
            bp = args.batch.resolve()
            batch = load_batch(bp)
            archive = read(resolve(bp.parent, batch['content_archive']))
            matches = [key for key, a in batch['artifacts'].items()
                       if a.get('review') and resolve(bp.parent, a['review']) == record_path]
            if not matches:
                errors.append('record is not referenced by this batch')
            for key in matches:
                errors.extend(review_errors(bp, batch, archive, key))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append('invalid batch: ' + str(exc))
    if errors:
        print("STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("STAGE_VISUAL_SELF_CHECK_GATE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
