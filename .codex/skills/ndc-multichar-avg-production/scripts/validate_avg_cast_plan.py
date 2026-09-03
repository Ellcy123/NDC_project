#!/usr/bin/env python3
"""Validate an NDC multi-character AVG cast-plan v2 JSON file."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import sys
from itertools import combinations
from pathlib import Path
from typing import Any


SCHEMA = "ndc-multichar-avg-plan/v2"
STAGES = {"blocking", "whitebox-approved", "final"}
BACK_FRAMINGS = {"half-body", "waist-up", "upper-thigh"}
PRESENCE_STATES = {"already-present", "enters-now"}
OCCLUSION_RELATIONS = {"no-overlap", "first-in-front", "second-in-front"}
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
SHA256 = re.compile(r"^[0-9A-Fa-f]{64}$")
MIN_CHANNEL_SPREAD = 40
MIN_PAIRWISE_COLOR_DISTANCE = 50.0
POINT_LANDMARKS = (
    "neck",
    "leftShoulder",
    "rightShoulder",
    "leftElbow",
    "rightElbow",
    "leftHand",
    "rightHand",
    "hipCenter",
    "leftKnee",
    "rightKnee",
    "leftFoot",
    "rightFoot",
)
RECT_LANDMARKS = ("headBox", "outerBBox")
PERFORMANCE_FIELDS = (
    "silentFrameVerb",
    "beatEnergy",
    "ongoingOccupation",
    "performanceFamily",
    "action",
    "emotion",
    "facialExpression",
    "bodyLine",
    "weightDistribution",
    "leftHandMotivation",
    "rightHandMotivation",
    "namedSupport",
    "socialTerritory",
    "actionFocus",
    "subtext",
    "costumeState",
    "propContinuity",
    "depthHonesty",
)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _positive_number(value: Any) -> bool:
    return _finite_number(value) and value > 0


def _size(value: Any) -> tuple[int, int] | None:
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) and not isinstance(item, bool) and item > 0 for item in value)
    ):
        return value[0], value[1]
    return None


def _point(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(_finite_number(item) for item in value)


def _rect(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(_finite_number(item) for item in value)
        and value[2] > value[0]
        and value[3] > value[1]
    )


def _rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))


def _distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _png_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def _validate_file_hash(
    container: dict[str, Any],
    path_field: str,
    hash_field: str,
    label: str,
    errors: list[str],
    *,
    required: bool,
) -> Path | None:
    raw_path = container.get(path_field)
    raw_hash = container.get(hash_field)
    if not _nonempty(raw_path):
        errors.append(f"{label}.{path_field} must be a non-empty string")
        return None
    path = Path(raw_path)
    if not required:
        if raw_hash not in (None, "") and not (isinstance(raw_hash, str) and SHA256.fullmatch(raw_hash)):
            errors.append(f"{label}.{hash_field} must be empty or a SHA-256 hex digest while pending")
        return path
    if not path.is_file():
        errors.append(f"{label}.{path_field} must point to an existing file")
        return path
    if not isinstance(raw_hash, str) or not SHA256.fullmatch(raw_hash):
        errors.append(f"{label}.{hash_field} must be a SHA-256 hex digest")
    elif _sha256_file(path) != raw_hash.lower():
        errors.append(f"{label}.{hash_field} does not match {path_field}")
    return path


def _validate_review(
    review: Any,
    label: str,
    errors: list[str],
    *,
    require_pass: bool,
    require_preview: bool = False,
    require_contract: bool = False,
) -> None:
    if not isinstance(review, dict):
        errors.append(f"{label} must be an object")
        return

    status = review.get("status")
    normalized = status.upper() if isinstance(status, str) else ""
    if normalized not in {"PENDING", "PASS"}:
        errors.append(f"{label}.status must be 'PENDING' or 'PASS'")
    if require_pass and normalized != "PASS":
        errors.append(f"{label}.status must be 'PASS' at this stage")

    must_exist = require_pass or normalized == "PASS"
    _validate_file_hash(review, "report", "reportSha256", label, errors, required=must_exist)

    for field, needed in (("preview", require_preview), ("contract", require_contract)):
        if not needed:
            continue
        value = review.get(field)
        if not _nonempty(value):
            errors.append(f"{label}.{field} must be a non-empty string")
        elif must_exist and not Path(value).is_file():
            errors.append(f"{label}.{field} must point to an existing file")


def _validate_scale_anchors(review: Any, errors: list[str]) -> None:
    if not isinstance(review, dict):
        return
    anchors = review.get("anchorGroups")
    if not isinstance(anchors, list) or len(anchors) < 3:
        errors.append("sceneAbsoluteScaleReview.anchorGroups must contain at least three groups")
        return

    ids: set[str] = set()
    scopes: set[str] = set()
    depths: set[str] = set()
    axes: set[str] = set()
    for index, anchor in enumerate(anchors):
        label = f"sceneAbsoluteScaleReview.anchorGroups[{index}]"
        if not isinstance(anchor, dict):
            errors.append(f"{label} must be an object")
            continue
        anchor_id = anchor.get("id")
        if not _nonempty(anchor_id):
            errors.append(f"{label}.id must be a non-empty string")
        elif anchor_id in ids:
            errors.append(f"{label}.id duplicates {anchor_id!r}")
        else:
            ids.add(anchor_id)
        scope = anchor.get("scope")
        if scope not in {"actor-local", "cross-depth"}:
            errors.append(f"{label}.scope must be 'actor-local' or 'cross-depth'")
        else:
            scopes.add(scope)
        depth = anchor.get("depthBand")
        if not _nonempty(depth):
            errors.append(f"{label}.depthBand must be a non-empty string")
        else:
            depths.add(depth)
        measured_axes = anchor.get("measuredAxes")
        if not isinstance(measured_axes, list) or not measured_axes:
            errors.append(f"{label}.measuredAxes must be a non-empty array")
        else:
            for axis in measured_axes:
                if axis not in {"horizontal", "vertical"}:
                    errors.append(f"{label}.measuredAxes may contain only 'horizontal' and 'vertical'")
                else:
                    axes.add(axis)
        lines = anchor.get("measurementLines")
        line_axes: set[str] = set()
        if not isinstance(lines, list) or not lines:
            errors.append(f"{label}.measurementLines must be a non-empty array")
        else:
            for line_index, line in enumerate(lines):
                line_label = f"{label}.measurementLines[{line_index}]"
                if not isinstance(line, dict):
                    errors.append(f"{line_label} must be an object")
                    continue
                axis = line.get("axis")
                if axis not in {"horizontal", "vertical"}:
                    errors.append(f"{line_label}.axis must be 'horizontal' or 'vertical'")
                else:
                    line_axes.add(axis)
                for field in ("start", "end"):
                    if not _point(line.get(field)):
                        errors.append(f"{line_label}.{field} must be a two-number coordinate")
                real_range = line.get("realWorldRangeCm")
                if (
                    not isinstance(real_range, list)
                    or len(real_range) != 2
                    or not all(_positive_number(value) for value in real_range)
                    or real_range[1] < real_range[0]
                ):
                    errors.append(f"{line_label}.realWorldRangeCm must be two ordered positive numbers")
                if not _nonempty(line.get("assumption")):
                    errors.append(f"{line_label}.assumption must be a non-empty string")
        if isinstance(measured_axes, list):
            declared_axes = {axis for axis in measured_axes if axis in {"horizontal", "vertical"}}
            if declared_axes != line_axes:
                errors.append(f"{label}.measurementLines axes must exactly match measuredAxes")
        if anchor.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"{label}.confidence must be 'low', 'medium', or 'high'")

    if scopes != {"actor-local", "cross-depth"}:
        errors.append("sceneAbsoluteScaleReview.anchorGroups must cover actor-local and cross-depth evidence")
    if len(depths) < 2:
        errors.append("sceneAbsoluteScaleReview.anchorGroups must cover at least two depth bands")
    if axes != {"horizontal", "vertical"}:
        errors.append("sceneAbsoluteScaleReview.anchorGroups must cover horizontal and vertical measurements")


def _validate_occlusion_graph(graph: Any, actor_ids: list[str], errors: list[str]) -> None:
    if not isinstance(graph, dict):
        errors.append("occlusionGraph must be an object")
        return
    pairwise = graph.get("pairwise")
    if not isinstance(pairwise, list):
        errors.append("occlusionGraph.pairwise must be an array")
        pairwise = []

    actor_set = set(actor_ids)
    seen: set[tuple[str, str]] = set()
    for index, edge in enumerate(pairwise):
        label = f"occlusionGraph.pairwise[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{label} must be an object")
            continue
        pair = edge.get("actors")
        if not isinstance(pair, list) or len(pair) != 2 or not all(_nonempty(item) for item in pair):
            errors.append(f"{label}.actors must contain two actorIds")
            continue
        if pair[0] == pair[1]:
            errors.append(f"{label}.actors must name two different actors")
            continue
        if any(item not in actor_set for item in pair):
            errors.append(f"{label}.actors contains an unknown actorId")
        key = tuple(sorted(pair))
        if key in seen:
            errors.append(f"{label} duplicates actor pair {key}")
        seen.add(key)
        if edge.get("relation") not in OCCLUSION_RELATIONS:
            errors.append(f"{label}.relation must be one of {sorted(OCCLUSION_RELATIONS)}")

    expected = {tuple(sorted(pair)) for pair in combinations(actor_ids, 2)}
    missing = expected - seen
    if missing:
        errors.append(f"occlusionGraph.pairwise is missing actor pairs: {sorted(missing)}")

    occluders = graph.get("sceneOccluders")
    if not isinstance(occluders, list):
        errors.append("occlusionGraph.sceneOccluders must be an array")
        return
    for index, item in enumerate(occluders):
        label = f"occlusionGraph.sceneOccluders[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        if not _nonempty(item.get("id")):
            errors.append(f"{label}.id must be a non-empty string")
        if item.get("source") != "sourceScene":
            errors.append(f"{label}.source must be 'sourceScene'")
        above = item.get("aboveActors")
        if not isinstance(above, list) or not above or any(actor not in actor_set for actor in above):
            errors.append(f"{label}.aboveActors must contain known actorIds")


def validate_plan(plan: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return ["root must be a JSON object"], warnings

    if plan.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA!r}; migrate legacy v1 plans before production")

    stage = plan.get("stage")
    if stage not in STAGES:
        errors.append(f"stage must be one of {sorted(STAGES)}")
    whitebox_ready = stage in {"whitebox-approved", "final"}
    final_ready = stage == "final"

    if plan.get("sceneKind") != "static-multichar-avg":
        errors.append("sceneKind must be 'static-multichar-avg'")
    for field in ("sceneId", "silentFrameStatement"):
        if not _nonempty(plan.get(field)):
            errors.append(f"{field} must be a non-empty string")

    scene_size = _size(plan.get("sceneSize"))
    if scene_size is None:
        errors.append("sceneSize must contain two positive integers")

    source_path = _validate_file_hash(
        plan, "sourceScene", "sourceSceneSha256", "plan", errors, required=True
    )
    if source_path and source_path.is_file() and scene_size:
        actual = _png_size(source_path)
        if actual is None:
            errors.append("sourceScene must be a readable PNG so canvas size can be verified")
        elif actual != scene_size:
            errors.append(f"sceneSize {scene_size} does not match sourceScene PNG size {actual}")

    if plan.get("castClusterSide") not in {"left", "right"}:
        errors.append("castClusterSide must be 'left' or 'right'")
    if plan.get("uiSide") not in {"left", "right"}:
        errors.append("uiSide must be 'left' or 'right'; unresolved UI cannot enter blocking")
    _validate_file_hash(plan, "uiReference", "uiReferenceSha256", "plan", errors, required=True)
    ui_placement = plan.get("uiPlacement")
    if not isinstance(ui_placement, dict):
        errors.append("uiPlacement must be an object")
    else:
        ui_canvas = _size(ui_placement.get("canvasSize"))
        if ui_canvas is None:
            errors.append("uiPlacement.canvasSize must contain two positive integers")
        elif scene_size and ui_canvas != scene_size:
            errors.append("uiPlacement.canvasSize must equal sceneSize")
        if not _point(ui_placement.get("topLeft")):
            errors.append("uiPlacement.topLeft must be a two-number coordinate")
        if not isinstance(ui_placement.get("mirrorX"), bool):
            errors.append("uiPlacement.mirrorX must be boolean")

    timeline = plan.get("timelineReview")
    if not isinstance(timeline, dict) or not _nonempty(timeline.get("snapshotId")):
        errors.append("timelineReview.snapshotId must be a non-empty string")
    _validate_review(timeline, "timelineReview", errors, require_pass=True)

    ui_review = plan.get("uiSafetyReview")
    _validate_review(
        ui_review,
        "uiSafetyReview",
        errors,
        require_pass=whitebox_ready,
        require_preview=True,
    )
    if not isinstance(ui_review, dict):
        pass
    else:
        required_regions = {"headBox", "leftHand", "rightHand", "ownedProp", "actionFocus"}
        protected = ui_review.get("protectedRegions")
        if not isinstance(protected, list) or not required_regions.issubset(set(protected)):
            errors.append(f"uiSafetyReview.protectedRegions must include {sorted(required_regions)}")
        for field in ("maxHeadOverlapRatio", "maxCriticalOverlapRatio"):
            value = ui_review.get(field)
            if not _finite_number(value) or value != 0:
                errors.append(f"uiSafetyReview.{field} must be 0")
    scene_scale = plan.get("sceneAbsoluteScaleReview")
    _validate_review(
        scene_scale,
        "sceneAbsoluteScaleReview",
        errors,
        require_pass=whitebox_ready,
        require_preview=True,
        require_contract=True,
    )
    _validate_scale_anchors(scene_scale, errors)
    if not isinstance(scene_scale, dict) or not _nonempty(scene_scale.get("projectionModel")):
        errors.append("sceneAbsoluteScaleReview.projectionModel must be a non-empty string")
    if not isinstance(scene_scale, dict) or not _finite_number(scene_scale.get("horizonY")):
        errors.append("sceneAbsoluteScaleReview.horizonY must be a finite number")
    cast_scale = plan.get("castScaleReview")
    _validate_review(
        cast_scale,
        "castScaleReview",
        errors,
        require_pass=whitebox_ready,
        require_contract=True,
    )
    if not isinstance(cast_scale, dict) or cast_scale.get("headScalePriority") is not True:
        errors.append("castScaleReview.headScalePriority must be true")
    if isinstance(cast_scale, dict):
        deviation = cast_scale.get("maxDeviationRatio")
        head_deviation = cast_scale.get("maxHeadDeviationRatio")
        if not _positive_number(deviation) or deviation > 0.03:
            errors.append("castScaleReview.maxDeviationRatio must be positive and no greater than 0.03")
        if not _positive_number(head_deviation) or head_deviation > 0.05:
            errors.append("castScaleReview.maxHeadDeviationRatio must be positive and no greater than 0.05")

    visual = plan.get("whiteboxVisualReview")
    _validate_review(
        visual,
        "whiteboxVisualReview",
        errors,
        require_pass=whitebox_ready,
        require_preview=True,
    )
    if not isinstance(visual, dict) or visual.get("wholeFrameZoomPercent") != 100:
        errors.append("whiteboxVisualReview.wholeFrameZoomPercent must be 100")
    if not isinstance(visual, dict) or visual.get("localZoomPercent") != 200:
        errors.append("whiteboxVisualReview.localZoomPercent must be 200")

    contacts = plan.get("actorContacts", [])
    if not isinstance(contacts, list):
        errors.append("actorContacts must be an array")
    elif contacts:
        errors.append("actorContacts must be empty for the default production route")

    actors = plan.get("actors")
    if not isinstance(actors, list) or len(actors) < 2:
        errors.append("actors must contain at least two people")
        actors = []

    actor_ids: list[str] = []
    colors: list[tuple[str, tuple[int, int, int], int]] = []
    held_props: dict[str, str] = {}
    required_actor_strings = (
        "actorId",
        "name",
        "characterCard",
        "canonicalHeightSource",
        "isolatedWhitebox",
        "depthClass",
        "framing",
        "poseFamily",
        "facing",
        "gazeTarget",
        "support",
        "anchor",
    )

    for index, actor in enumerate(actors):
        label = f"actors[{index}]"
        if not isinstance(actor, dict):
            errors.append(f"{label} must be an object")
            continue

        for field in required_actor_strings:
            if not _nonempty(actor.get(field)):
                errors.append(f"{label}.{field} must be a non-empty string")

        actor_id = actor.get("actorId")
        if _nonempty(actor_id):
            if actor_id in actor_ids:
                errors.append(f"{label}.actorId duplicates {actor_id!r}")
            actor_ids.append(actor_id)

        if actor.get("presenceAtSnapshot") not in PRESENCE_STATES:
            errors.append(f"{label}.presenceAtSnapshot must be one of {sorted(PRESENCE_STATES)}")
        height = actor.get("canonicalHeightCm")
        if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
            errors.append(f"{label}.canonicalHeightCm must be a positive integer from canon")

        _validate_file_hash(actor, "characterCard", "characterCardSha256", label, errors, required=True)
        _validate_file_hash(
            actor,
            "canonicalHeightSource",
            "canonicalHeightSourceSha256",
            label,
            errors,
            required=True,
        )

        identity = actor.get("identityScaleReference")
        if not isinstance(identity, dict):
            errors.append(f"{label}.identityScaleReference must be an object")
        else:
            full = identity.get("referenceFullBodyHeightPx")
            head = identity.get("referenceAnatomicalHeadHeightPx")
            if not _positive_number(full):
                errors.append(f"{label}.identityScaleReference.referenceFullBodyHeightPx must be positive")
            if not _positive_number(head):
                errors.append(f"{label}.identityScaleReference.referenceAnatomicalHeadHeightPx must be positive")
            if _positive_number(full) and _positive_number(head) and head >= full:
                errors.append(f"{label}.identityScaleReference anatomical head height must be smaller than full body")
            for field in ("bodyBuild", "headToBodyNotes"):
                if not _nonempty(identity.get(field)):
                    errors.append(f"{label}.identityScaleReference.{field} must be a non-empty string")

        if not isinstance(actor.get("backFacing"), bool):
            errors.append(f"{label}.backFacing must be boolean")
        if not isinstance(actor.get("feetVisible"), bool):
            errors.append(f"{label}.feetVisible must be boolean")

        canvas_size = _size(actor.get("whiteboxCanvasSize"))
        if canvas_size is None:
            errors.append(f"{label}.whiteboxCanvasSize must contain two positive integers")
        elif scene_size and canvas_size != scene_size:
            errors.append(f"{label}.whiteboxCanvasSize must equal sceneSize")
        if not _point(actor.get("supportPoint")):
            errors.append(f"{label}.supportPoint must be a two-number coordinate")
        if not _positive_number(actor.get("standingEquivalentHeightPx")):
            errors.append(f"{label}.standingEquivalentHeightPx must be positive")

        landmarks = actor.get("poseLandmarks")
        if not isinstance(landmarks, dict):
            errors.append(f"{label}.poseLandmarks must be an object")
        else:
            for field in POINT_LANDMARKS:
                if not _point(landmarks.get(field)):
                    errors.append(f"{label}.poseLandmarks.{field} must be a two-number coordinate")
            for field in RECT_LANDMARKS:
                if not _rect(landmarks.get(field)):
                    errors.append(f"{label}.poseLandmarks.{field} must be [x1,y1,x2,y2]")

        performance = actor.get("performance")
        if not isinstance(performance, dict):
            errors.append(f"{label}.performance must be an object")
        else:
            for field in PERFORMANCE_FIELDS:
                if not _nonempty(performance.get(field)):
                    errors.append(f"{label}.performance.{field} must be a non-empty string")
            if performance.get("namedSupport") != actor.get("support"):
                errors.append(f"{label}.performance.namedSupport must equal {label}.support")
            if performance.get("tenSecondHold") is not True:
                errors.append(f"{label}.performance.tenSecondHold must be true")

        _validate_review(
            actor.get("supportContactReview"),
            f"{label}.supportContactReview",
            errors,
            require_pass=whitebox_ready,
            require_preview=True,
        )

        color = actor.get("whiteboxColor")
        if isinstance(color, str) and HEX_COLOR.fullmatch(color):
            rgb = _rgb(color)
            colors.append((color.upper(), rgb, index))
            if max(rgb) - min(rgb) < MIN_CHANNEL_SPREAD:
                errors.append(f"{label}.whiteboxColor must have enough chroma to read as a distinct actor label")
        else:
            errors.append(f"{label}.whiteboxColor must be #RRGGBB")

        pose = actor.get("poseFamily")
        if isinstance(pose, str) and "seated" in pose.lower() and not _nonempty(actor.get("seatedJustification")):
            errors.append(f"{label}.seatedJustification is required for a seated pose")

        prop = actor.get("prop")
        if prop is not None:
            if not isinstance(prop, dict):
                errors.append(f"{label}.prop must be null or an object")
            else:
                prop_id = prop.get("id")
                if not _nonempty(prop_id):
                    errors.append(f"{label}.prop.id must be a non-empty string")
                if prop.get("ownership") != "held":
                    errors.append(f"{label}.prop.ownership must be 'held'")
                if prop.get("handoff") is not False:
                    errors.append(f"{label}.prop.handoff must be false")
                if _nonempty(prop_id):
                    if prop_id in held_props:
                        errors.append(
                            f"prop {prop_id!r} is assigned to both {held_props[prop_id]!r} and {actor_id!r}"
                        )
                    else:
                        held_props[prop_id] = actor_id

        if whitebox_ready:
            isolated = _validate_file_hash(
                actor,
                "isolatedWhitebox",
                "isolatedWhiteboxSha256",
                label,
                errors,
                required=True,
            )
            if isolated and isolated.is_file() and scene_size:
                actual = _png_size(isolated)
                if actual != scene_size:
                    errors.append(f"{label}.isolatedWhitebox PNG size {actual} must equal sceneSize {scene_size}")

    color_names = [item[0] for item in colors]
    if len(color_names) != len(set(color_names)):
        errors.append("each actor must use a distinct whiteboxColor within this snapshot")
    for left_index, (left_hex, left_rgb, left_actor) in enumerate(colors):
        for right_hex, right_rgb, right_actor in colors[left_index + 1 :]:
            if _distance(left_rgb, right_rgb) < MIN_PAIRWISE_COLOR_DISTANCE:
                errors.append(
                    f"actors[{left_actor}] and actors[{right_actor}] use colors that are too similar "
                    f"({left_hex} vs {right_hex})"
                )

    actor_id_set = set(actor_ids)
    for index, actor in enumerate(actors):
        if not isinstance(actor, dict):
            continue
        gaze_target = actor.get("gazeTarget")
        actor_id = actor.get("actorId")
        if gaze_target == actor_id:
            errors.append(f"actors[{index}].gazeTarget cannot target the same actor")
        elif _nonempty(gaze_target) and gaze_target not in actor_id_set:
            if not (gaze_target.startswith("prop:") or gaze_target.startswith("scene:")):
                errors.append(
                    f"actors[{index}].gazeTarget must be another actorId or start with 'prop:' or 'scene:'"
                )

    _validate_occlusion_graph(plan.get("occlusionGraph"), actor_ids, errors)

    if len(actors) >= 3:
        back_actors = [actor for actor in actors if isinstance(actor, dict) and actor.get("backFacing") is True]
        if not back_actors:
            errors.append("scenes with three or more actors require at least one back-facing actor")
        for actor in back_actors:
            actor_id = actor.get("actorId", "<unknown>")
            if actor.get("feetVisible") is not False:
                errors.append(f"back-facing actor {actor_id!r} must have feetVisible=false")
            if actor.get("framing") not in BACK_FRAMINGS:
                errors.append(f"back-facing actor {actor_id!r} must use one of {sorted(BACK_FRAMINGS)}")

    if whitebox_ready:
        combined = _validate_file_hash(
            plan,
            "combinedWhitebox",
            "combinedWhiteboxSha256",
            "plan",
            errors,
            required=True,
        )
        if combined and combined.is_file() and scene_size:
            actual = _png_size(combined)
            if actual != scene_size:
                errors.append(f"combinedWhitebox PNG size {actual} must equal sceneSize {scene_size}")
    elif not _nonempty(plan.get("combinedWhitebox")):
        errors.append("combinedWhitebox must declare an intended output path")

    if final_ready:
        for path_field, hash_field in (("outputPsd", "outputPsdSha256"), ("outputPng", "outputPngSha256")):
            _validate_file_hash(plan, path_field, hash_field, "plan", errors, required=True)
        output_png = Path(plan["outputPng"]) if _nonempty(plan.get("outputPng")) else None
        if output_png and output_png.is_file() and scene_size:
            actual = _png_size(output_png)
            if actual != scene_size:
                errors.append(f"outputPng PNG size {actual} must equal sceneSize {scene_size}")

        for field in ("finalGazeReview", "backgroundPreservationReview", "finalVisualReview"):
            _validate_review(
                plan.get(field),
                field,
                errors,
                require_pass=True,
                require_preview=True,
            )
        final_visual = plan.get("finalVisualReview")
        if not isinstance(final_visual, dict) or final_visual.get("wholeFrameZoomPercent") != 100:
            errors.append("finalVisualReview.wholeFrameZoomPercent must be 100")
        if not isinstance(final_visual, dict) or final_visual.get("localZoomPercent") != 200:
            errors.append("finalVisualReview.localZoomPercent must be 200")

        for index, actor in enumerate(actors):
            if not isinstance(actor, dict):
                continue
            label = f"actors[{index}]"
            for field in ("contextualCandidate", "rawCutout"):
                if not _nonempty(actor.get(field)) or not Path(actor[field]).is_file():
                    errors.append(f"{label}.{field} must point to an existing file at stage 'final'")
            if not _nonempty(actor.get("finalLayerName")):
                errors.append(f"{label}.finalLayerName must be a non-empty string at stage 'final'")

            registration = actor.get("registration")
            if not isinstance(registration, dict):
                errors.append(f"{label}.registration must be an object at stage 'final'")
            else:
                if not _positive_number(registration.get("uniformScalePercent")):
                    errors.append(f"{label}.registration.uniformScalePercent must be a positive finite number")
                for field in ("translateX", "translateY"):
                    if not _finite_number(registration.get(field)):
                        errors.append(f"{label}.registration.{field} must be a finite number")
                if registration.get("anchor") != actor.get("anchor"):
                    errors.append(f"{label}.registration.anchor must equal {label}.anchor")

            for field in ("edgeReview", "identityReview", "lightingReview"):
                if actor.get(field) != "PASS":
                    errors.append(f"{label}.{field} must be 'PASS' at stage 'final'")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Path to the cast-plan JSON file")
    args = parser.parse_args(argv)

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        print(f"ERROR: plan file does not exist: {args.plan}")
        return 1
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read plan: {exc}")
        return 1

    errors, warnings = validate_plan(plan)
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print(f"AVG_CAST_PLAN_OK actors={len(plan['actors'])} stage={plan['stage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
