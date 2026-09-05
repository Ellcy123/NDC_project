#!/usr/bin/env python3
"""Validate recorded visual evidence; never perform or manufacture visual review.

Rebuilt from the current NDC skill contracts, not recovered from the unavailable
external validator. See production/art_pipeline/validator_contracts.md.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image


class GateError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def nonempty(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: nonempty text required")
    return value


def object_value(value, label):
    require(isinstance(value, dict), f"{label}: object required")
    return value


def list_value(value, label):
    require(isinstance(value, list) and bool(value), f"{label}: nonempty list required")
    return value


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_record(path):
    return object_value(json.loads(path.read_text(encoding="utf-8-sig"),
                                   object_pairs_hook=_unique_object), "record")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(raw, record_path):
    path = Path(nonempty(raw, "path"))
    return (path if path.is_absolute() else record_path.parent / path).resolve()


def file_reference(value, label, record_path):
    value = object_value(value, label)
    path = resolve_path(value.get("path"), record_path)
    expected = nonempty(value.get("sha256"), f"{label}.sha256").lower()
    require(bool(re.fullmatch(r"[0-9a-f]{64}", expected)), f"{label}: invalid SHA-256")
    require(path.is_file(), f"{label}: file missing: {path}")
    actual = sha256(path)
    require(actual == expected, f"{label}: stale SHA-256: {path}")
    return path, actual


def passing_finding(value, label):
    value = object_value(value, label)
    require(value.get("status") == "PASS",
            f"{label}: explicit PASS required; got {value.get('status')!r}")
    nonempty(value.get("finding"), f"{label}.finding")


def reviewer_and_date(data):
    nonempty(data.get("reviewer"), "reviewer")
    date = nonempty(data.get("reviewed_at"), "reviewed_at")
    try:
        datetime.fromisoformat(date.replace("Z", "+00:00"))
    except ValueError as error:
        raise GateError("reviewed_at: ISO date or datetime required") from error


def image_size(path):
    with Image.open(path) as image:
        image.verify()
        return image.size


def rectangle(value, size, label):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(number) is int for number in value), f"{label}: integer [left, top, right, bottom] required")
    x1, y1, x2, y2 = value
    require(0 <= x1 < x2 <= size[0] and 0 <= y1 < y2 <= size[1], f"{label}: outside source or empty")
    return tuple(value)


def rectangle_is_covered(target, tiles):
    """Exact rectangle-union coverage without a source-sized bitmap allocation."""
    left, top, right, bottom = target
    clipped = [(max(left, x1), max(top, y1), min(right, x2), min(bottom, y2))
               for x1, y1, x2, y2 in tiles
               if x1 < right and x2 > left and y1 < bottom and y2 > top]
    boundaries = sorted({left, right} | {v for box in clipped for v in (box[0], box[2])})
    for x1, x2 in zip(boundaries, boundaries[1:]):
        intervals = sorted((box[1], box[3]) for box in clipped if box[0] <= x1 and box[2] >= x2)
        reached = top
        for start, end in intervals:
            if start > reached:
                return False
            reached = max(reached, end)
        if reached < bottom:
            return False
    return True


def validate_views(data, record_path, allowed_sources, *, require_tiles=False):
    views = object_value(data.get("views"), "views")
    whole = object_value(views.get("whole_100"), "views.whole_100")
    passing_finding(whole, "views.whole_100")
    require(whole.get("scale_percent") == 100, "whole_100.scale_percent must be 100")
    source, source_hash = file_reference(whole.get("source"), "whole_100.source", record_path)
    require((source, source_hash) in allowed_sources, "whole_100 source is not a bound visual input/output")
    whole_path, _ = file_reference(whole, "whole_100", record_path)
    size = image_size(source)
    whole_size = image_size(whole_path)
    require(whole_size[0] >= size[0] and whole_size[1] >= size[1], "whole_100 view is smaller than its source")

    local = object_value(views.get("local_200_or_tiles"), "views.local_200_or_tiles")
    passing_finding(local, "views.local_200_or_tiles")
    local_source = file_reference(local.get("source"), "local.source", record_path)
    require(local_source == (source, source_hash), "whole/local views must inspect the same current source")
    mode = local.get("mode")
    if mode == "nearest_neighbor_200" and not require_tiles:
        scale = local.get("scale_percent")
        require(type(scale) in (int, float) and scale >= 200, "local scale must be at least 200 percent")
        require(local.get("resampling") == "nearest", "local view requires nearest resampling")
        for index, item in enumerate(list_value(local.get("images"), "local.images")):
            label = f"local.images[{index}]"
            passing_finding(item, label)
            path, _ = file_reference(item, label, record_path)
            box = rectangle(item.get("bbox"), size, f"{label}.bbox")
            width, height = image_size(path)
            require(width >= (box[2] - box[0]) * scale / 100 and
                    height >= (box[3] - box[1]) * scale / 100, f"{label}: view was downscaled")
        return source, source_hash

    require(mode == "complete_original_pixel_tiles",
            f"local mode unsupported or incomplete: {mode!r}; complete tiles required" if require_tiles else
            f"Unsupported local view mode: {mode!r}")
    require(local.get("local_tile_coverage_complete") is True, "local tile coverage not explicitly complete")
    require(local.get("source_size") == list(size), "local.source_size does not match source")
    coverage_mode = local.get("coverage_mode")
    if coverage_mode == "full_image_tiles":
        targets = [(0, 0, *size)]
    elif coverage_mode == "authorized_region_plus_boundary_tiles":
        regions = list_value(local.get("required_regions"), "local.required_regions")
        require({item.get("role") for item in regions if isinstance(item, dict)} >=
                {"authorized_region", "boundary"}, "region coverage requires authorized_region and boundary")
        targets = []
        for index, region in enumerate(regions):
            object_value(region, f"required_regions[{index}]")
            nonempty(region.get("finding"), f"required_regions[{index}].finding")
            targets.append(rectangle(region.get("bbox"), size, f"required_regions[{index}].bbox"))
    else:
        raise GateError(f"Unsupported coverage_mode: {coverage_mode!r}")
    boxes = []
    for index, tile in enumerate(list_value(local.get("tiles"), "local.tiles")):
        label = f"local.tiles[{index}]"
        passing_finding(tile, label)
        path, _ = file_reference(tile, label, record_path)
        box = rectangle(tile.get("bbox"), size, f"{label}.bbox")
        tile_size = image_size(path)
        require(tile_size[0] >= box[2] - box[0] and tile_size[1] >= box[3] - box[1],
                f"{label}: original-pixel tile was downscaled")
        boxes.append(box)
    require(all(rectangle_is_covered(target, boxes) for target in targets),
            "Tile geometry leaves an uncovered source/required-region area")
    return source, source_hash


def criteria(data, mandatory=()):
    required = list_value(data.get("required_criteria"), "required_criteria")
    for name in required:
        nonempty(name, "required_criteria entry")
    require(len(required) == len(set(required)), "required_criteria contains duplicates")
    checks = object_value(data.get("criteria"), "criteria")
    missing = (set(required) | set(mandatory)) - checks.keys()
    require(not missing, f"Missing required visual criteria: {', '.join(sorted(missing))}")
    require(set(mandatory) <= set(required), "Mandatory criteria must be explicitly listed in required_criteria")
    for name, check in checks.items():
        passing_finding(check, f"criteria.{name}")


TYPE7_CRITERIA = {
    "mandatory_direct_image_container_rule", "source_anchor_visual_comparison",
    "container_height_and_observation_direction", "visual_self_check",
    "child_container_identity_and_full_visibility",
}


def validate_type7(data, record_path):
    context = object_value(data.get("type7_visual_context"), "type7_visual_context")
    for field in ("real_container_identity", "environment_derivation", "first_person_viewpoint_rationale"):
        nonempty(context.get(field), f"type7_visual_context.{field}")
    height, direction = context.get("height_class"), context.get("observation_direction")
    require(height in {"low", "mid", "high"}, "Type7 height_class must be low/mid/high")
    require(direction in {"downward", "level", "upward"}, "Type7 observation_direction invalid")
    require(height != "low" or direction == "downward", "Low Type7 container requires downward observation")
    require(context.get("method") == "direct_image_generation", "Type7 method must be direct_image_generation")
    require(context.get("child_fully_contained") is True, "Type7 child must be fully contained")
    anchor, _ = file_reference(data.get("original_scene_visual_anchor"), "original_scene_visual_anchor", record_path)
    image_size(anchor)
    comparison, _ = file_reference(data.get("source_anchor_side_by_side"), "source_anchor_side_by_side", record_path)
    image_size(comparison)


def validate_record(record_path, artifact, data=None):
    record_path, artifact = record_path.resolve(), artifact.resolve()
    data = load_record(record_path) if data is None else data
    require(data.get("schema") == "ndc-stage-visual-self-check/v1",
            f"Unsupported schema {data.get('schema')!r}; legacy visual reports cannot supply missing reviewer, per-criterion findings or view evidence")
    stage = nonempty(data.get("stage_id"), "stage_id")
    reviewer_and_date(data)
    require(data.get("visual_check_status") == "PASS", "visual_check_status must be PASS")
    inputs = [file_reference(item, f"inputs[{index}]", record_path)
              for index, item in enumerate(list_value(data.get("inputs"), "inputs"))]
    output = file_reference(data.get("output"), "output", record_path)
    require(artifact.is_file(), f"Current artifact missing: {artifact}")
    require(sha256(artifact) == output[1], f"Current artifact differs from the single reviewed output: {artifact}")
    criteria(data, TYPE7_CRITERIA if stage.startswith("container_type7") else ())
    source = validate_views(data, record_path, set(inputs + [output]))
    # A non-image handoff can review its visual input; an image output must itself
    # be the whole/local reviewed source, not merely appear somewhere in inputs.
    if output[0].suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}:
        require(source == output, "Image output must itself have whole/local review views")
    if stage.startswith("container_type7"):
        validate_type7(data, record_path)
    return {"stage_id": stage, "record": str(record_path), "artifact": str(artifact), "sha256": output[1]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_record(args.record, args.artifact)
        print("STAGE_VISUAL_SELF_CHECK_GATE: PASS " + json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
