#!/usr/bin/env python3
"""Validate NDC character-scene importance/tolerance profiles; never grants art PASS."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "ndc-visual-importance/v1"
HARD_GATES = {
    "cast_scope", "identity", "state_and_narrative_action", "active_gaze",
    "support_and_contact", "complete_master", "scene_pixel_protection",
    "ui_critical_clearance", "alpha_xy_reconstruction",
}
LIMITS = {"H0": 0.0, "H1": 0.10, "H2": 0.20, "H3": 0.30}
VIEWS = {"whole_runtime", "whole_100", "local_200"}
REGION_KEYS = {"id", "owner", "tier", "tolerance_ratio", "criteria", "views", "reason", "low_salience_basis", "dependsOn"}


def text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(profile: dict) -> dict:
    errors: list[str] = []
    if profile.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if profile.get("domain") != "character_scene":
        errors.append("domain must be character_scene")
    if not text(profile.get("scene_id")):
        errors.append("scene_id is required")
    revision = profile.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("revision must be a positive integer")
    basis = profile.get("classification_basis")
    if not isinstance(basis, list) or not basis or not all(text(v) for v in basis):
        errors.append("classification_basis must contain concrete evidence")

    hard = profile.get("hard_gates")
    if not isinstance(hard, dict) or set(hard) != HARD_GATES:
        errors.append("hard_gates must contain exactly the fixed H0 gate names")
    else:
        for name, entry in hard.items():
            if not isinstance(entry, dict) or set(entry) != {"applicable", "reason"}:
                errors.append(f"hard_gates.{name} must contain only applicable and reason")
            elif not isinstance(entry.get("applicable"), bool) or not text(entry.get("reason")):
                errors.append(f"hard_gates.{name} requires boolean applicable and concrete reason")

    regions = profile.get("regions")
    ids: set[str] = set()
    if not isinstance(regions, list) or not regions:
        errors.append("regions must be a non-empty list")
        regions = []
    for index, region in enumerate(regions):
        label = f"regions[{index}]"
        if not isinstance(region, dict):
            errors.append(label + " must be an object")
            continue
        unknown = set(region) - REGION_KEYS
        if unknown:
            errors.append(label + f" contains unknown keys: {sorted(unknown)}")
        rid = region.get("id")
        if not text(rid) or rid in ids:
            errors.append(label + ".id must be unique non-empty text")
        else:
            ids.add(rid)
        if not text(region.get("owner")) or not text(region.get("reason")):
            errors.append(label + " requires owner and reason")
        tier = region.get("tier")
        ratio = region.get("tolerance_ratio")
        if tier not in LIMITS:
            errors.append(label + ".tier must be H0, H1, H2 or H3")
        elif not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or ratio < 0 or ratio > LIMITS[tier] + 1e-9:
            errors.append(label + f".tolerance_ratio exceeds {LIMITS[tier]:.2f} for {tier}")
        criteria = region.get("criteria")
        if not isinstance(criteria, list) or not criteria or not all(text(v) for v in criteria):
            errors.append(label + ".criteria must be non-empty concrete text")
        views = region.get("views")
        if not isinstance(views, list) or not views or len(views) != len(set(views)) or not set(views) <= VIEWS:
            errors.append(label + ".views must be distinct supported views")
        else:
            if "whole_runtime" not in views:
                errors.append(label + " must include whole_runtime")
            if tier in {"H0", "H1", "H2"} and "whole_100" not in views:
                errors.append(label + f" {tier} must include whole_100")
        if tier == "H3" and not text(region.get("low_salience_basis")):
            errors.append(label + " H3 requires low_salience_basis")
        depends = region.get("dependsOn", [])
        if not isinstance(depends, list) or len(depends) != len(set(depends)) or not all(text(v) for v in depends):
            errors.append(label + ".dependsOn must be a distinct string list")
    for index, region in enumerate(regions):
        for dep in region.get("dependsOn", []) if isinstance(region, dict) else []:
            if dep not in ids:
                errors.append(f"regions[{index}].dependsOn references unknown region {dep}")

    return {
        "schema": "ndc-visual-importance-gate/v1",
        "gate": "IMPORTANCE_TOLERANCE_GATE",
        "status": "PASS" if not errors else "FAIL",
        "checks": {"hard_gate_count": len(hard) if isinstance(hard, dict) else 0,
                   "region_count": len(regions), "no_cross_region_averaging": True},
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8-sig"))
        result = validate(profile) if isinstance(profile, dict) else {"schema":"ndc-visual-importance-gate/v1","gate":"IMPORTANCE_TOLERANCE_GATE","status":"FAIL","errors":["profile must be an object"]}
        result["profile_path"] = str(args.profile.resolve())
        result["profile_sha256"] = hashlib.sha256(args.profile.read_bytes()).hexdigest()
    except (OSError, json.JSONDecodeError) as exc:
        result = {"schema":"ndc-visual-importance-gate/v1","gate":"IMPORTANCE_TOLERANCE_GATE","status":"FAIL","errors":[str(exc)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
