#!/usr/bin/env python3
"""Validate recorded style-lock and complete-local texture evidence, never artistry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from validate_stage_visual_self_check import (
    criteria, file_reference, list_value, load_record, nonempty, object_value,
    passing_finding, require, reviewer_and_date, validate_views,
)

TEXTURE_CRITERIA = {
    "large_shape_readability", "focal_detail_hierarchy", "quiet_plane_control",
    "material_texture_continuity", "texture_scale_consistency",
    "depth_aware_detail_density", "repeated_pattern_artifacts_absent",
    "nonsemantic_microdetail_absent",
}


def validate_record(record_path):
    record_path = record_path.resolve()
    data = load_record(record_path)
    require(data.get("schema") == "ndc-texture-coherence/v1",
            f"Unsupported texture schema: {data.get('schema')!r}")
    reviewer_and_date(data)
    artifact = file_reference(data.get("artifact"), "artifact", record_path)
    require(data.get("formal_status") == "FORMAL_PASS", "formal_status must be FORMAL_PASS")
    require(data.get("whole_image_checked") is True, "whole_image_checked must be true")
    require(data.get("local_tile_coverage_complete") is True, "local_tile_coverage_complete must be true")
    style = object_value(data.get("STYLE_LOCK_GATE"), "STYLE_LOCK_GATE")
    passing_finding(style, "STYLE_LOCK_GATE")
    for index, reference in enumerate(list_value(style.get("references"), "STYLE_LOCK_GATE.references")):
        file_reference(reference, f"STYLE_LOCK_GATE.references[{index}]", record_path)
    for invariant in list_value(style.get("frozen_invariants"), "STYLE_LOCK_GATE.frozen_invariants"):
        nonempty(invariant, "frozen style invariant")
    texture = object_value(data.get("TEXTURE_COHERENCE_GATE"), "TEXTURE_COHERENCE_GATE")
    passing_finding(texture, "TEXTURE_COHERENCE_GATE")
    criteria(texture, TEXTURE_CRITERIA)
    validate_views(data, record_path, {artifact}, require_tiles=True)
    return {"record": str(record_path), "artifact": str(artifact[0]), "sha256": artifact[1]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_record(args.record)
        print("TEXTURE_GATE_VALID: FORMAL_PASS " + json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"TEXTURE_GATE_VALID: BLOCKED {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
