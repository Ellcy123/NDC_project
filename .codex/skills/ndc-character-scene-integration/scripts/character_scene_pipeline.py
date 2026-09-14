from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw
from head_measurement import anatomical_head_height


TEST_ROOT_OVERRIDE: Path | None = None


def configured_root(name: str) -> Path:
    """Resolve a root injected by the portable ndc_art.py entrypoint."""
    if TEST_ROOT_OVERRIDE is not None:
        if name == "NDC_ART_WORK_ROOT":
            return (TEST_ROOT_OVERRIDE / "工作过程文件").resolve()
        return TEST_ROOT_OVERRIDE.resolve()
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f"Missing {name}. Run this Skill through "
            "scripts/art_pipeline/ndc_art.py run so machine roots are injected."
        )
    root = Path(value).expanduser()
    if not root.is_absolute():
        raise ValueError(f"{name} must be an absolute path.")
    return root.resolve()


def is_within(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def load_contract(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_fields(mapping: dict, fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")


def validate_bbox(box: list | tuple, label: str) -> tuple[float, float, float, float]:
    if len(box) != 4:
        raise ValueError(f"{label} must contain [left, top, right, bottom].")
    left, top, right, bottom = (float(value) for value in box)
    if right <= left or bottom <= top:
        raise ValueError(f"{label} must have positive width and height.")
    return left, top, right, bottom


def point_inside_bbox(point: list | tuple, bbox: tuple[float, float, float, float]) -> bool:
    x, y = (float(value) for value in point)
    left, top, right, bottom = bbox
    return left <= x <= right and top <= y <= bottom


POSE_POINT_FIELDS = (
    "neck",
    "leftShoulder",
    "rightShoulder",
    "leftElbow",
    "rightElbow",
    "leftHand",
    "rightHand",
    "leftHip",
    "rightHip",
    "leftKnee",
    "rightKnee",
    "leftFoot",
    "rightFoot",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pose_key(placement_class: str) -> str:
    return {
        "standing": "standingPose",
        "walking": "standingPose",
        "leaning": "standingPose",
        "seated": "seatedPose",
        "lying": "lyingPose",
    }[placement_class]


def get_exact_pose(target: dict, placement_class: str) -> dict:
    key = pose_key(placement_class)
    pose = target.get(key)
    if not pose:
        raise ValueError(f"Exact-pose workflow requires target.{key}.")
    return pose


def validate_exact_pose(
    target: dict,
    placement_class: str,
    outer_bbox: tuple[float, float, float, float],
    standing_equivalent_height: float,
) -> dict:
    definition = target.get("poseDefinition")
    if not definition:
        raise ValueError("Exact-pose workflow requires target.poseDefinition.")
    require_fields(
        definition,
        (
            "poseId",
            "action",
            "facing",
            "gazeTarget",
            "leftHandAction",
            "rightHandAction",
            "requiredProps",
        ),
        "target.poseDefinition",
    )
    for name in (
        "poseId",
        "action",
        "facing",
        "gazeTarget",
        "leftHandAction",
        "rightHandAction",
    ):
        if not str(definition[name]).strip():
            raise ValueError(f"target.poseDefinition.{name} cannot be empty.")
    if not isinstance(definition["requiredProps"], list):
        raise ValueError("target.poseDefinition.requiredProps must be a list.")

    pose = get_exact_pose(target, placement_class)
    require_fields(pose, ("headBox", "supportObject", *POSE_POINT_FIELDS), f"target.{pose_key(placement_class)}")
    if not str(pose["supportObject"]).strip():
        raise ValueError(f"target.{pose_key(placement_class)}.supportObject cannot be empty.")
    head_box = validate_bbox(pose["headBox"], f"target.{pose_key(placement_class)}.headBox")
    if not (
        outer_bbox[0] <= head_box[0] < head_box[2] <= outer_bbox[2]
        and outer_bbox[1] <= head_box[1] < head_box[3] <= outer_bbox[3]
    ):
        raise ValueError("Exact-pose headBox must stay inside target.outerBBox.")
    for name in POSE_POINT_FIELDS:
        if not point_inside_bbox(pose[name], outer_bbox):
            raise ValueError(f"Exact-pose landmark {name} must stay inside target.outerBBox.")
    head_height = anatomical_head_height(pose, head_box)
    head_ratio = head_height / standing_equivalent_height
    if not 0.09 <= head_ratio <= 0.18:
        raise ValueError(
            "Exact-pose anatomical head height is implausible relative to the "
            f"standing equivalent: ratio={head_ratio:.4f}."
        )

    relations = target.get("sceneRelations")
    if not isinstance(relations, list) or not relations:
        raise ValueError("target.sceneRelations must declare support and occlusion relations.")
    allowed_relations = {"supported-by", "touching", "in-front-of", "behind", "inside"}
    has_support = False
    has_behind_relation = False
    for index, relation in enumerate(relations):
        label = f"target.sceneRelations[{index}]"
        require_fields(relation, ("objectId", "relation", "regions", "reason"), label)
        if relation["relation"] not in allowed_relations:
            raise ValueError(f"{label}.relation is unsupported: {relation['relation']}")
        if not str(relation["objectId"]).strip() or not str(relation["reason"]).strip():
            raise ValueError(f"{label} objectId and reason cannot be empty.")
        if not isinstance(relation["regions"], list) or not relation["regions"]:
            raise ValueError(f"{label}.regions must identify the affected body/scene regions.")
        has_support = has_support or relation["relation"] == "supported-by"
        has_behind_relation = has_behind_relation or relation["relation"] == "behind"
    if not has_support:
        raise ValueError("target.sceneRelations requires at least one supported-by relation.")
    if has_behind_relation and not target.get("occluderPolygons"):
        raise ValueError(
            "A behind scene relation requires target.occluderPolygons for deterministic occlusion."
        )
    if placement_class != "lying":
        left_foot = pose["leftFoot"]
        right_foot = pose["rightFoot"]
        foot_x, foot_y = (float(value) for value in target["foot"])
        expected_x = (float(left_foot[0]) + float(right_foot[0])) / 2
        expected_y = max(float(left_foot[1]), float(right_foot[1]))
        if abs(foot_x - expected_x) > 2 or abs(foot_y - expected_y) > 2:
            raise ValueError(
                "target.foot must match the exact-pose feet midpoint and lowest contact."
            )
    return pose


def validate_delivery_root(data: dict) -> None:
    require_fields(data, ("scene", "deliveryRoot"), "placement contract")
    scene = Path(data["scene"])
    delivery_root = Path(data["deliveryRoot"])
    if not delivery_root.is_absolute():
        raise ValueError("deliveryRoot must be an absolute path.")
    if delivery_root.name != scene.stem:
        raise ValueError(
            "deliveryRoot folder name must exactly match the source scene basename: "
            f"expected={scene.stem}, actual={delivery_root.name}"
        )
    delivery_root = delivery_root.resolve()
    formal_root = configured_root("NDC_ART_DELIVERY_ROOT")
    work_root = configured_root("NDC_ART_WORK_ROOT")
    if is_within(delivery_root, work_root):
        raise ValueError("Formal deliveryRoot cannot be inside the configured work root.")
    if not is_within(delivery_root, formal_root):
        raise ValueError(
            "deliveryRoot must stay under the configured formal delivery root; "
            "keep provisional packages under the configured work root instead."
        )


def validate_scale_anchors(
    estimates: list[dict], character_height_cm: float, derived_tolerance: float
) -> list[float]:
    if len(estimates) < 2:
        raise ValueError("Scale calibration requires at least two projected anchors.")
    object_ids: set[str] = set()
    independence_groups: set[str] = set()
    values: list[float] = []
    required = (
        "objectId",
        "independenceGroup",
        "dimension",
        "realWorldRangeCm",
        "assumedCm",
        "imageMeasurementPx",
        "projectedMeasurementPxAtTarget",
        "projectionMethod",
        "planeRelation",
        "depthBand",
        "value",
        "confidence",
    )
    for index, estimate in enumerate(estimates):
        label = f"calibration.projectedHeightEstimatesPx[{index}]"
        require_fields(estimate, required, label)
        object_id = str(estimate["objectId"]).strip()
        independence_group = str(estimate["independenceGroup"]).strip()
        if not object_id or not independence_group:
            raise ValueError(f"{label} objectId and independenceGroup cannot be empty.")
        object_ids.add(object_id)
        independence_groups.add(independence_group)
        real_range = estimate["realWorldRangeCm"]
        if len(real_range) != 2:
            raise ValueError(f"{label}.realWorldRangeCm must contain [min, max].")
        real_min, real_max = (float(value) for value in real_range)
        if real_min <= 0 or real_max < real_min:
            raise ValueError(f"{label}.realWorldRangeCm must be a positive ordered range.")
        assumed_cm = float(estimate["assumedCm"])
        if not real_min <= assumed_cm <= real_max:
            raise ValueError(f"{label}.assumedCm must stay inside realWorldRangeCm.")
        if float(estimate["imageMeasurementPx"]) <= 0:
            raise ValueError(f"{label}.imageMeasurementPx must be positive.")
        projected_measurement = float(estimate["projectedMeasurementPxAtTarget"])
        if projected_measurement <= 0:
            raise ValueError(f"{label}.projectedMeasurementPxAtTarget must be positive.")
        if not str(estimate["projectionMethod"]).strip():
            raise ValueError(f"{label}.projectionMethod cannot be empty.")
        if not str(estimate["planeRelation"]).strip():
            raise ValueError(f"{label}.planeRelation cannot be empty.")
        depth_band = estimate["depthBand"]
        if depth_band not in {"actor-local", "cross-depth"}:
            raise ValueError(
                f"{label}.depthBand must be actor-local or cross-depth."
            )
        if depth_band == "cross-depth":
            evidence = estimate.get("projectionEvidence")
            if not isinstance(evidence, dict):
                raise ValueError(f"{label}.projectionEvidence is required for cross-depth anchors.")
            require_fields(
                evidence,
                ("sourceSupportPoint", "targetSupportPoint", "perspectiveBasisIds"),
                f"{label}.projectionEvidence",
            )
            for point_name in ("sourceSupportPoint", "targetSupportPoint"):
                point = evidence[point_name]
                if not isinstance(point, list) or len(point) != 2:
                    raise ValueError(
                        f"{label}.projectionEvidence.{point_name} must contain [x, y]."
                    )
            basis_ids = evidence["perspectiveBasisIds"]
            if not isinstance(basis_ids, list) or not basis_ids or not all(
                str(value).strip() for value in basis_ids
            ):
                raise ValueError(
                    f"{label}.projectionEvidence.perspectiveBasisIds must be a non-empty list."
                )
        if estimate["confidence"] not in {"low", "medium", "high"}:
            raise ValueError(f"{label}.confidence must be low, medium, or high.")
        value = float(estimate["value"])
        if value <= 0:
            raise ValueError("Projected height estimates must be positive.")
        derived_value = projected_measurement * character_height_cm / assumed_cm
        if abs(value - derived_value) / derived_value > derived_tolerance:
            raise ValueError(
                f"{label}.value does not match the 170cm arithmetic chain: "
                f"recorded={value:.3f}, derived={derived_value:.3f}, "
                f"tolerance={derived_tolerance:.4f}"
            )
        values.append(value)
    if len(object_ids) < 2 or len(independence_groups) < 2:
        raise ValueError(
            "Scale calibration requires at least two distinct real objects and "
            "two independence groups; multiple dimensions of one object are not independent anchors."
        )
    bands = {str(estimate["depthBand"]) for estimate in estimates}
    if bands != {"actor-local", "cross-depth"}:
        raise ValueError(
            "Scale calibration requires both actor-local and cross-depth anchors."
        )
    for band in ("actor-local", "cross-depth"):
        if not any(
            estimate["depthBand"] == band and estimate["confidence"] in {"medium", "high"}
            for estimate in estimates
        ):
            raise ValueError(
                f"Scale calibration requires at least one medium/high-confidence {band} anchor."
            )
    return values


def validate_contract(data: dict, shared_scale_report: dict | None = None) -> tuple[float, float]:
    validate_delivery_root(data)
    character_height_cm = float(data["characterHeightCm"])
    if character_height_cm <= 0:
        raise ValueError("characterHeightCm must be positive.")
    if data["calibration"].get("sceneScaleEvidence"):
        from scene_scale_v2 import placement_scale
        shared = placement_scale(data, expected_report=shared_scale_report)
        median, spread, allowed = shared["heightPx"], shared["spread"], 0.08
    else:
        estimates = data["calibration"]["projectedHeightEstimatesPx"]
        if data["calibration"].get("aggregationMethod") != "median-after-depth-projection":
            raise ValueError("calibration.aggregationMethod must be median-after-depth-projection.")
        derived_tolerance = float(data["calibration"].get("derivedValueToleranceRatio", 0.03))
        values = validate_scale_anchors(estimates, character_height_cm, derived_tolerance)
        median = statistics.median(values)
        spread = (max(values) - min(values)) / median
        allowed = float(data["calibration"].get("maxSpreadRatio", 0.08))
        if spread > allowed:
            raise ValueError(f"Scale estimates disagree: spread={spread:.4f}, allowed={allowed:.4f}")
        band_values = {band: [value for estimate, value in zip(estimates, values)
                              if estimate["depthBand"] == band] for band in ("actor-local", "cross-depth")}
        local_median = statistics.median(band_values["actor-local"])
        cross_depth_median = statistics.median(band_values["cross-depth"])
        cross_depth_delta = abs(local_median - cross_depth_median) / median
        cross_depth_allowed = float(data["calibration"].get("maxCrossDepthMedianDeltaRatio", allowed))
        if cross_depth_delta > cross_depth_allowed:
            raise ValueError("Actor-local and cross-depth scale estimates disagree after projection: "
                             f"delta={cross_depth_delta:.4f}, allowed={cross_depth_allowed:.4f}")

    target = data["target"]
    scene_size = tuple(data["sceneSize"])
    if len(scene_size) != 2 or min(scene_size) <= 0:
        raise ValueError("sceneSize must contain positive width and height.")
    outer_bbox = validate_bbox(target["outerBBox"], "target.outerBBox")
    if not (
        0 <= outer_bbox[0] < outer_bbox[2] <= scene_size[0]
        and 0 <= outer_bbox[1] < outer_bbox[3] <= scene_size[1]
    ):
        raise ValueError("target.outerBBox must stay inside sceneSize.")
    placement_class = target.get("placementClass", "standing")
    visible_height = float(target["visibleHeightPx"])
    if visible_height <= 0:
        raise ValueError("target.visibleHeightPx must be positive.")
    if placement_class in {"standing", "walking", "leaning"}:
        scale_height = visible_height
    elif placement_class == "seated":
        scale_height = float(target.get("standingEquivalentHeightPx", 0))
        if scale_height <= 0:
            raise ValueError("Seated placement requires positive target.standingEquivalentHeightPx.")
        bbox = outer_bbox
        bbox_height = bbox[3] - bbox[1]
        if bbox_height <= 0 or abs(visible_height - bbox_height) > 2:
            raise ValueError("Seated visibleHeightPx must match outerBBox height within two pixels.")
        ratio = visible_height / scale_height
        ratio_range = target.get("poseToStandingRatioRange", [0.55, 1.20])
        if len(ratio_range) != 2 or not (float(ratio_range[0]) <= ratio <= float(ratio_range[1])):
            raise ValueError(
                "Seated pose-to-standing ratio is outside the approved range: "
                f"ratio={ratio:.4f}, range={ratio_range}"
            )
        scale_audit = target.get("scaleAudit")
        if not scale_audit:
            raise ValueError("Seated placement requires target.scaleAudit.")
        require_fields(
            scale_audit,
            (
                "anatomicalTopY",
                "anatomicalBottomY",
                "standingHeadHeightPx",
                "seatedHeadHeightPx",
                "bodyScaleDriver",
                "outerExtensions",
            ),
            "target.scaleAudit",
        )
        if scale_audit["bodyScaleDriver"] != "standingEquivalentHeightPx":
            raise ValueError(
                "Seated bodyScaleDriver must be standingEquivalentHeightPx; "
                "outerBBox and alphaBBox cannot drive body scale."
            )
        anatomical_top = float(scale_audit["anatomicalTopY"])
        anatomical_bottom = float(scale_audit["anatomicalBottomY"])
        anatomical_height = anatomical_bottom - anatomical_top
        if anatomical_height <= 0 or anatomical_height >= scale_height:
            raise ValueError(
                "Seated anatomical span must be positive and lower than the "
                "same-depth standing-equivalent height."
            )
        if anatomical_top < bbox[1] or anatomical_bottom > bbox[3]:
            raise ValueError("Seated anatomical span must stay inside target.outerBBox.")
        standing_head = float(scale_audit["standingHeadHeightPx"])
        seated_head = float(scale_audit["seatedHeadHeightPx"])
        if standing_head <= 0 or seated_head <= 0:
            raise ValueError("Standing and seated head heights must be positive.")
        head_tolerance = float(scale_audit.get("headToleranceRatio", 0.05))
        if abs(seated_head - standing_head) / standing_head > head_tolerance:
            raise ValueError("Seated head scale does not match the approved standing master.")
        pose = target.get("seatedPose")
        if not pose:
            raise ValueError("Seated placement requires target.seatedPose.")
        require_fields(
            pose,
            (
                "headBox",
                "leftShoulder",
                "rightShoulder",
                "hipSeat",
                "leftKnee",
                "rightKnee",
                "leftFoot",
                "rightFoot",
                "supportObject",
            ),
            "target.seatedPose",
        )
        if not str(pose["supportObject"]).strip():
            raise ValueError("target.seatedPose.supportObject cannot be empty.")
        head_box = validate_bbox(pose["headBox"], "target.seatedPose.headBox")
        if abs(anatomical_head_height(pose, head_box) - seated_head) > 2:
            raise ValueError(
                "seatedPose anatomical head measurement must match "
                "scaleAudit.seatedHeadHeightPx within two pixels."
            )
        if abs(head_box[1] - anatomical_top) > 2:
            raise ValueError("Anatomical head top must match scaleAudit.anatomicalTopY.")
        if not (
            bbox[0] <= head_box[0] < head_box[2] <= bbox[2]
            and bbox[1] <= head_box[1] < head_box[3] <= bbox[3]
        ):
            raise ValueError("target.seatedPose.headBox must stay inside target.outerBBox.")
        for name in (
            "leftShoulder",
            "rightShoulder",
            "hipSeat",
            "leftKnee",
            "rightKnee",
            "leftFoot",
            "rightFoot",
        ):
            if not point_inside_bbox(pose[name], bbox):
                raise ValueError(f"target.seatedPose.{name} must stay inside target.outerBBox.")
        left_foot = pose["leftFoot"]
        right_foot = pose["rightFoot"]
        foot_x, foot_y = (float(value) for value in target["foot"])
        if abs(foot_x - (float(left_foot[0]) + float(right_foot[0])) / 2) > 2:
            raise ValueError("target.foot X must match the midpoint of the seated feet.")
        if abs(foot_y - max(float(left_foot[1]), float(right_foot[1]))) > 2:
            raise ValueError("target.foot Y must match the lowest seated foot contact.")
        kinematics = target.get("seatedKinematics")
        if not kinematics:
            raise ValueError("Seated placement requires target.seatedKinematics.")
        require_fields(
            kinematics,
            (
                "torsoFacing",
                "pelvisSupportObjectId",
                "footSupportObjectId",
                "primarySupportFoot",
                "rightFootYMinusLeftFootY",
                "stanceWidthShoulderRatioRange",
                "orientationRationale",
            ),
            "target.seatedKinematics",
        )
        if kinematics["primarySupportFoot"] not in {"leftFoot", "rightFoot"}:
            raise ValueError("seatedKinematics.primarySupportFoot is invalid.")
        if not str(kinematics["torsoFacing"]).strip() or not str(kinematics["orientationRationale"]).strip():
            raise ValueError("seatedKinematics facing and rationale cannot be empty.")
        declared_stagger = float(kinematics["rightFootYMinusLeftFootY"])
        actual_stagger = float(right_foot[1]) - float(left_foot[1])
        if abs(declared_stagger - actual_stagger) > 1:
            raise ValueError("seatedKinematics foot stagger does not match the pose.")
        if kinematics["primarySupportFoot"] == "rightFoot" and actual_stagger < 0:
            raise ValueError("Primary right support foot must not sit behind the left foot.")
        if kinematics["primarySupportFoot"] == "leftFoot" and actual_stagger > 0:
            raise ValueError("Primary left support foot must not sit behind the right foot.")
        shoulder_width = abs(float(pose["rightShoulder"][0]) - float(pose["leftShoulder"][0]))
        foot_width = abs(float(right_foot[0]) - float(left_foot[0]))
        if shoulder_width <= 0:
            raise ValueError("Seated shoulder width must be positive.")
        ratio = foot_width / shoulder_width
        ratio_range = kinematics["stanceWidthShoulderRatioRange"]
        if len(ratio_range) != 2 or not (float(ratio_range[0]) <= ratio <= float(ratio_range[1])):
            raise ValueError(
                "Seated foot stance is incompatible with the declared torso orientation: "
                f"ratio={ratio:.3f}, range={ratio_range}"
            )
        support_relations = {
            str(relation["objectId"]): set(relation.get("regions", []))
            for relation in target.get("sceneRelations", [])
            if relation.get("relation") == "supported-by"
        }
        pelvis_support = str(kinematics["pelvisSupportObjectId"])
        foot_support = str(kinematics["footSupportObjectId"])
        if "hipSeat" not in support_relations.get(pelvis_support, set()):
            raise ValueError("seatedKinematics pelvis support does not match sceneRelations.")
        if not {"leftFoot", "rightFoot"}.issubset(support_relations.get(foot_support, set())):
            raise ValueError("seatedKinematics foot support does not match sceneRelations.")
        extensions = scale_audit["outerExtensions"]
        if not isinstance(extensions, list):
            raise ValueError("target.scaleAudit.outerExtensions must be a list.")
        for index, extension in enumerate(extensions):
            label = f"target.scaleAudit.outerExtensions[{index}]"
            require_fields(extension, ("label", "bbox", "reason"), label)
            if not str(extension["label"]).strip() or not str(extension["reason"]).strip():
                raise ValueError(f"{label} label and reason cannot be empty.")
            extension_bbox = validate_bbox(extension["bbox"], f"{label}.bbox")
            if not (
                bbox[0] <= extension_bbox[0] < extension_bbox[2] <= bbox[2]
                and bbox[1] <= extension_bbox[1] < extension_bbox[3] <= bbox[3]
            ):
                raise ValueError(f"{label}.bbox must stay inside target.outerBBox.")
        if visible_height > scale_height and not extensions:
            raise ValueError(
                "A seated outer bbox taller than the standing equivalent requires "
                "declared outerExtensions; extensions cannot rescale the body."
            )
    elif placement_class == "lying":
        scale_height = float(target.get("standingEquivalentHeightPx", 0))
        if scale_height <= 0:
            raise ValueError("Lying placement requires positive target.standingEquivalentHeightPx.")
        bbox = outer_bbox
        bbox_height = bbox[3] - bbox[1]
        if abs(visible_height - bbox_height) > 2:
            raise ValueError("Lying visibleHeightPx must match outerBBox height within two pixels.")
        ratio = visible_height / scale_height
        ratio_range = target.get("poseToStandingRatioRange", [0.22, 0.70])
        if len(ratio_range) != 2 or not (float(ratio_range[0]) <= ratio <= float(ratio_range[1])):
            raise ValueError(
                "Lying pose-to-standing ratio is outside the approved range: "
                f"ratio={ratio:.4f}, range={ratio_range}"
            )
        scale_audit = target.get("scaleAudit")
        if not scale_audit:
            raise ValueError("Lying placement requires target.scaleAudit.")
        require_fields(
            scale_audit,
            (
                "anatomicalTopY",
                "anatomicalBottomY",
                "standingHeadHeightPx",
                "lyingHeadHeightPx",
                "bodyScaleDriver",
                "outerExtensions",
            ),
            "target.scaleAudit",
        )
        if scale_audit["bodyScaleDriver"] != "standingEquivalentHeightPx":
            raise ValueError(
                "Lying bodyScaleDriver must be standingEquivalentHeightPx; "
                "outerBBox and alphaBBox cannot drive body scale."
            )
        anatomical_top = float(scale_audit["anatomicalTopY"])
        anatomical_bottom = float(scale_audit["anatomicalBottomY"])
        anatomical_height = anatomical_bottom - anatomical_top
        if anatomical_height <= 0 or anatomical_height >= scale_height:
            raise ValueError(
                "Lying anatomical vertical span must be positive and lower than the "
                "same-depth standing-equivalent height."
            )
        if anatomical_top < bbox[1] or anatomical_bottom > bbox[3]:
            raise ValueError("Lying anatomical span must stay inside target.outerBBox.")
        standing_head = float(scale_audit["standingHeadHeightPx"])
        lying_head = float(scale_audit["lyingHeadHeightPx"])
        if standing_head <= 0 or lying_head <= 0:
            raise ValueError("Standing and lying head heights must be positive.")
        head_tolerance = float(scale_audit.get("headToleranceRatio", 0.05))
        if abs(lying_head - standing_head) / standing_head > head_tolerance:
            raise ValueError("Lying head scale does not match the approved standing master.")
        pose = target.get("lyingPose")
        if not pose:
            raise ValueError("Lying placement requires target.lyingPose.")
        require_fields(
            pose,
            (
                "headBox",
                "leftShoulder",
                "rightShoulder",
                "leftElbow",
                "rightElbow",
                "leftHand",
                "rightHand",
                "hip",
                "leftKnee",
                "rightKnee",
                "leftFoot",
                "rightFoot",
                "bodyAxis",
                "supportObject",
            ),
            "target.lyingPose",
        )
        if not str(pose["supportObject"]).strip():
            raise ValueError("target.lyingPose.supportObject cannot be empty.")
        head_box = validate_bbox(pose["headBox"], "target.lyingPose.headBox")
        if abs(anatomical_head_height(pose, head_box) - lying_head) > 2:
            raise ValueError(
                "lyingPose anatomical head measurement must match "
                "scaleAudit.lyingHeadHeightPx within two pixels."
            )
        if not (
            bbox[0] <= head_box[0] < head_box[2] <= bbox[2]
            and bbox[1] <= head_box[1] < head_box[3] <= bbox[3]
        ):
            raise ValueError("target.lyingPose.headBox must stay inside target.outerBBox.")
        for name in (
            "leftShoulder",
            "rightShoulder",
            "leftElbow",
            "rightElbow",
            "leftHand",
            "rightHand",
            "hip",
            "leftKnee",
            "rightKnee",
            "leftFoot",
            "rightFoot",
        ):
            if not point_inside_bbox(pose[name], bbox):
                raise ValueError(f"target.lyingPose.{name} must stay inside target.outerBBox.")
        body_axis = pose["bodyAxis"]
        if len(body_axis) != 2 or any(not point_inside_bbox(point, bbox) for point in body_axis):
            raise ValueError("target.lyingPose.bodyAxis must contain two in-bbox points.")
        if tuple(body_axis[0]) == tuple(body_axis[1]):
            raise ValueError("target.lyingPose.bodyAxis must have positive length.")
        contact_point = target.get("contactPoint")
        if not contact_point or not point_inside_bbox(contact_point, bbox):
            raise ValueError("Lying placement requires an in-bbox target.contactPoint.")
        extensions = scale_audit["outerExtensions"]
        if not isinstance(extensions, list):
            raise ValueError("target.scaleAudit.outerExtensions must be a list.")
        for index, extension in enumerate(extensions):
            label = f"target.scaleAudit.outerExtensions[{index}]"
            require_fields(extension, ("label", "bbox", "reason"), label)
            if not str(extension["label"]).strip() or not str(extension["reason"]).strip():
                raise ValueError(f"{label} label and reason cannot be empty.")
            extension_bbox = validate_bbox(extension["bbox"], f"{label}.bbox")
            if not (
                bbox[0] <= extension_bbox[0] < extension_bbox[2] <= bbox[2]
                and bbox[1] <= extension_bbox[1] < extension_bbox[3] <= bbox[3]
            ):
                raise ValueError(f"{label}.bbox must stay inside target.outerBBox.")
    else:
        raise ValueError(f"Unsupported placementClass: {placement_class}")
    validate_exact_pose(target, placement_class, outer_bbox, scale_height)
    if abs(scale_height - median) / median > allowed:
        raise ValueError("Approved scale height does not match the multi-anchor median.")

    anchor_name = "contactPoint" if placement_class == "lying" else "foot"
    anchor_x, anchor_y = target[anchor_name]
    if not (0 <= anchor_x < scene_size[0] and 0 <= anchor_y < scene_size[1]):
        raise ValueError(f"{anchor_name} lies outside the scene.")
    affordance_zone = str(target.get("affordanceZoneId", "")).strip()
    if not affordance_zone:
        raise ValueError(
            "target.affordanceZoneId is required. Validate the placement against an "
            "ndc-scene-affordance/v1 contract before scale/pose validation."
        )
    return median, spread


def proxy_alpha(proxy: Image.Image) -> Image.Image:
    rgba = proxy.convert("RGBA")
    alpha = Image.new("L", rgba.size, 0)
    src = rgba.load()
    dst = alpha.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, _ = src[x, y]
            if r > 180 and g < 100 and b < 100:
                dst[x, y] = 255
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("Proxy contains no red silhouette.")
    return alpha.crop(bbox)


def draw_exact_pose_skeleton(draw: ImageDraw.ImageDraw, pose: dict, color: tuple[int, int, int, int]) -> None:
    head_box = tuple(round(float(value)) for value in pose["headBox"])
    head_width = head_box[2] - head_box[0]
    line_width = max(4, round(head_width * 0.12))
    draw.ellipse(head_box, fill=color)
    neck = tuple(pose["neck"])
    left_shoulder = tuple(pose["leftShoulder"])
    right_shoulder = tuple(pose["rightShoulder"])
    left_hip = tuple(pose["leftHip"])
    right_hip = tuple(pose["rightHip"])
    draw.line((neck, ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2)), fill=color, width=line_width * 2)
    draw.line((left_shoulder, right_shoulder), fill=color, width=line_width * 2)
    draw.line((left_hip, right_hip), fill=color, width=line_width * 2)
    for start, mid, end in (
        (left_shoulder, tuple(pose["leftElbow"]), tuple(pose["leftHand"])),
        (right_shoulder, tuple(pose["rightElbow"]), tuple(pose["rightHand"])),
        (left_hip, tuple(pose["leftKnee"]), tuple(pose["leftFoot"])),
        (right_hip, tuple(pose["rightKnee"]), tuple(pose["rightFoot"])),
    ):
        draw.line((start, mid, end), fill=color, width=line_width)


def _tapered_limb(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    start_width: float,
    end_width: float,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
) -> None:
    dx = float(end[0]) - float(start[0])
    dy = float(end[1]) - float(start[1])
    length = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / length, dx / length
    polygon = [
        (start[0] + nx * start_width / 2, start[1] + ny * start_width / 2),
        (end[0] + nx * end_width / 2, end[1] + ny * end_width / 2),
        (end[0] - nx * end_width / 2, end[1] - ny * end_width / 2),
        (start[0] - nx * start_width / 2, start[1] - ny * start_width / 2),
    ]
    draw.polygon(polygon, fill=fill, outline=outline)
    radius = max(2, round(end_width / 2))
    draw.ellipse(
        (end[0] - radius, end[1] - radius, end[0] + radius, end[1] + radius),
        fill=fill,
        outline=outline,
        width=2,
    )


def draw_volumetric_pose(draw: ImageDraw.ImageDraw, pose: dict, label: str = "") -> None:
    head_box = tuple(round(float(value)) for value in pose["headBox"])
    head_width = max(8, head_box[2] - head_box[0])
    fill = (226, 228, 230, 245)
    outline = (74, 78, 82, 255)
    upper_arm_width = max(14, round(head_width * 0.34))
    forearm_width = max(11, round(head_width * 0.25))
    thigh_width = max(22, round(head_width * 0.48))
    calf_width = max(15, round(head_width * 0.32))
    left_shoulder = tuple(pose["leftShoulder"])
    right_shoulder = tuple(pose["rightShoulder"])
    left_hip = tuple(pose["leftHip"])
    right_hip = tuple(pose["rightHip"])
    draw.ellipse(head_box, fill=fill, outline=outline, width=max(2, round(head_width * 0.04)))
    shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
    hip_y = (left_hip[1] + right_hip[1]) / 2
    waist_y = shoulder_y + (hip_y - shoulder_y) * 0.62
    waist_left = (left_shoulder[0] * 0.38 + left_hip[0] * 0.62, waist_y)
    waist_right = (right_shoulder[0] * 0.38 + right_hip[0] * 0.62, waist_y)
    torso = (left_shoulder, right_shoulder, waist_right, right_hip, left_hip, waist_left)
    draw.polygon(torso, fill=fill, outline=outline)
    for shoulder, elbow, hand in (
        (left_shoulder, tuple(pose["leftElbow"]), tuple(pose["leftHand"])),
        (right_shoulder, tuple(pose["rightElbow"]), tuple(pose["rightHand"])),
    ):
        _tapered_limb(draw, shoulder, elbow, upper_arm_width, forearm_width, fill, outline)
        _tapered_limb(draw, elbow, hand, forearm_width, max(8, forearm_width * 0.62), fill, outline)
        hand_radius = max(5, round(head_width * 0.10))
        draw.ellipse((hand[0] - hand_radius, hand[1] - hand_radius, hand[0] + hand_radius, hand[1] + hand_radius), fill=fill, outline=outline, width=2)
    for hip, knee, foot in (
        (left_hip, tuple(pose["leftKnee"]), tuple(pose["leftFoot"])),
        (right_hip, tuple(pose["rightKnee"]), tuple(pose["rightFoot"])),
    ):
        _tapered_limb(draw, hip, knee, thigh_width, calf_width, fill, outline)
        _tapered_limb(draw, knee, foot, calf_width, max(10, calf_width * 0.72), fill, outline)
        foot_width = max(14, round(head_width * 0.28))
        foot_height = max(8, round(head_width * 0.13))
        draw.ellipse((foot[0] - foot_width, foot[1] - foot_height, foot[0] + foot_width, foot[1] + foot_height), fill=fill, outline=outline, width=2)
    neck = tuple(pose["neck"])
    neck_bottom = ((left_shoulder[0] + right_shoulder[0]) / 2, shoulder_y)
    _tapered_limb(draw, neck, neck_bottom, head_width * 0.22, head_width * 0.28, fill, outline)
    if label:
        draw.text((head_box[0], max(2, head_box[1] - 20)), label, fill=(35, 38, 42, 255))


def place_proxy(contract_path: Path, output: Path, base_path: Path | None = None) -> None:
    data = load_contract(contract_path)
    validate_contract(data)
    scene_path = base_path if base_path is not None else Path(data["scene"])
    scene = Image.open(scene_path).convert("RGBA")
    if scene.size != tuple(data["sceneSize"]):
        raise ValueError("Scene dimensions do not match contract.")
    source_scene = scene.copy()
    target = data["target"]
    placement_class = target.get("placementClass", "standing")
    if placement_class in {"standing", "walking", "leaning"}:
        pose = get_exact_pose(target, placement_class)
        overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        draw_exact_pose_skeleton(ImageDraw.Draw(overlay), pose, (255, 0, 0, 255))
        scene = Image.alpha_composite(scene, overlay)
    elif placement_class == "seated":
        pose = get_exact_pose(target, placement_class)
        overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        draw_exact_pose_skeleton(ImageDraw.Draw(overlay), pose, (255, 0, 0, 255))
        for extension in target["scaleAudit"]["outerExtensions"]:
            ImageDraw.Draw(overlay).rectangle(
                tuple(extension["bbox"]),
                outline=(255, 0, 0, 255),
                width=3,
            )
        scene = Image.alpha_composite(scene, overlay)
    elif placement_class == "lying":
        pose = get_exact_pose(target, placement_class)
        overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        draw_exact_pose_skeleton(ImageDraw.Draw(overlay), pose, (255, 0, 0, 255))
        for extension in target["scaleAudit"]["outerExtensions"]:
            ImageDraw.Draw(overlay).rectangle(
                tuple(extension["bbox"]),
                outline=(255, 0, 0, 255),
                width=3,
            )
        scene = Image.alpha_composite(scene, overlay)
    else:
        raise ValueError(f"Unsupported placementClass: {placement_class}")
    if target.get("drawOuterBBox", True):
        bbox_overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        bbox_draw = ImageDraw.Draw(bbox_overlay)
        bbox_draw.rectangle(
            tuple(round(float(value)) for value in target["outerBBox"]),
            outline=(255, 0, 0, 255),
            width=max(6, round(scene.width / 320)),
        )
        scene = Image.alpha_composite(scene, bbox_overlay)
    label = str(data.get("characterName", "")).strip()
    if label and target.get("drawLabel", True):
        label_overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        label_draw = ImageDraw.Draw(label_overlay)
        left, top, _, _ = (round(float(value)) for value in target["outerBBox"])
        label_draw.text((left + 8, max(4, top - 22)), label, fill=(255, 0, 0, 255))
        scene = Image.alpha_composite(scene, label_overlay)
    occluder_polygons = target.get("occluderPolygons", [])
    if occluder_polygons:
        occluder_mask = Image.new("L", scene.size, 0)
        mask_draw = ImageDraw.Draw(occluder_mask)
        for polygon in occluder_polygons:
            mask_draw.polygon([tuple(point) for point in polygon], fill=255)
        scene = Image.composite(source_scene, scene, occluder_mask)
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.save(output)


def bbox_intersection(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> tuple[float, float, float, float] | None:
    box = (
        max(first[0], second[0]),
        max(first[1], second[1]),
        min(first[2], second[2]),
        min(first[3], second[3]),
    )
    return box if box[2] > box[0] and box[3] > box[1] else None


def validate_staging(data: dict, require_reviewed_whitebox: bool = False) -> list[tuple[dict, dict]]:
    require_fields(
        data,
        (
            "scene",
            "sceneSize",
            "timelineSnapshotId",
            "uiSide",
            "uiSafetyReview",
            "characters",
            "occlusionGraph",
        ),
        "scene staging contract",
    )
    if not str(data["timelineSnapshotId"]).strip():
        raise ValueError("scene staging contract timelineSnapshotId cannot be empty.")
    if data["uiSide"] not in {"left", "right"}:
        raise ValueError("scene staging contract uiSide must be left or right.")
    ui_review = data["uiSafetyReview"]
    require_fields(ui_review, ("status", "report", "reportSha256"), "uiSafetyReview")
    if ui_review["status"] != "passed":
        raise ValueError("UI_SAFETY_REVIEW_REQUIRED: uiSafetyReview.status must be passed.")
    ui_report_path = Path(ui_review["report"])
    if not ui_report_path.is_file():
        raise ValueError(f"UI safety report is missing: {ui_report_path}")
    if sha256_file(ui_report_path).lower() != str(ui_review["reportSha256"]).lower():
        raise ValueError("UI safety report hash does not match the artifact.")
    ui_report = load_contract(ui_report_path)
    if ui_report.get("schema") != "ndc-ui-safety-report/v1" or ui_report.get("status") != "pass":
        raise ValueError("UI safety report must be a passing ndc-ui-safety-report/v1 artifact.")
    entries = data["characters"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("scene staging contract requires at least one character.")
    loaded: list[tuple[dict, dict]] = []
    names: set[str] = set()
    orders: set[int] = set()
    scene_path = Path(data["scene"]).resolve()
    scene_size = tuple(data["sceneSize"])
    shared_scale_reports: dict[tuple[str, str], dict] = {}
    for index, entry in enumerate(entries):
        label = f"characters[{index}]"
        require_fields(entry, ("name", "contract", "layerOrder"), label)
        name = str(entry["name"]).strip()
        if not name or name in names:
            raise ValueError(f"{label}.name must be non-empty and unique.")
        names.add(name)
        order = int(entry["layerOrder"])
        if order in orders:
            raise ValueError("Every character requires a unique layerOrder.")
        orders.add(order)
        contract_path = Path(entry["contract"])
        if not contract_path.is_file():
            raise ValueError(f"Missing character contract: {contract_path}")
        contract = load_contract(contract_path)
        shared_ref = contract.get("calibration", {}).get("sceneScaleEvidence")
        shared_report = None
        if shared_ref:
            from scene_scale_v2 import current_report
            identity = (str(Path(shared_ref["path"]).resolve()), str(shared_ref["sha256"]).lower())
            if identity not in shared_scale_reports:
                shared_scale_reports[identity] = current_report(shared_ref, contract_path.parent)
            shared_report = shared_scale_reports[identity]
        validate_contract(contract, shared_report)
        if str(contract.get("characterName", "")).strip() != name:
            raise ValueError(f"{label}.name differs from the placement contract characterName.")
        if Path(contract["scene"]).resolve() != scene_path:
            raise ValueError("All staging characters must use the same source scene.")
        if tuple(contract["sceneSize"]) != scene_size:
            raise ValueError("All staging characters must use the same sceneSize.")
        affordance_zone = str(contract["target"].get("affordanceZoneId", "")).strip()
        if not affordance_zone:
            raise ValueError(f"{label} placement contract lacks target.affordanceZoneId.")
        loaded.append((entry, contract))

    graph = data["occlusionGraph"]
    if not isinstance(graph, list):
        raise ValueError("occlusionGraph must be a list.")
    declared_pairs: set[frozenset[str]] = set()
    allowed_box_by_pair: dict[frozenset[str], tuple[float, float, float, float]] = {}
    order_by_name = {entry["name"]: int(entry["layerOrder"]) for entry, _ in loaded}
    for index, relation in enumerate(graph):
        label = f"occlusionGraph[{index}]"
        require_fields(
            relation,
            (
                "front",
                "back",
                "reason",
                "allowedOverlapBBox",
                "maxBackOcclusionRatio",
                "requiredVisibleLandmarks",
            ),
            label,
        )
        front = relation["front"]
        back = relation["back"]
        if front not in names or back not in names or front == back:
            raise ValueError(f"{label} must name two distinct staging characters.")
        pair = frozenset((front, back))
        if pair in declared_pairs:
            raise ValueError(f"Duplicate pairwise occlusion relation: {front}/{back}")
        declared_pairs.add(pair)
        if order_by_name[front] <= order_by_name[back]:
            raise ValueError(f"{label}.front must have a greater layerOrder than back.")
        allowed_box_by_pair[pair] = validate_bbox(
            relation["allowedOverlapBBox"], f"{label}.allowedOverlapBBox"
        )
        ratio = float(relation["maxBackOcclusionRatio"])
        if not 0 <= ratio <= 0.60:
            raise ValueError(f"{label}.maxBackOcclusionRatio must stay between 0 and 0.60.")
        if not str(relation["reason"]).strip():
            raise ValueError(f"{label}.reason cannot be empty.")
        if not isinstance(relation["requiredVisibleLandmarks"], list):
            raise ValueError(f"{label}.requiredVisibleLandmarks must be a list.")

    for first_index, (first_entry, first_contract) in enumerate(loaded):
        first_box = validate_bbox(first_contract["target"]["outerBBox"], "first outerBBox")
        for second_entry, second_contract in loaded[first_index + 1:]:
            second_box = validate_bbox(second_contract["target"]["outerBBox"], "second outerBBox")
            intersection = bbox_intersection(first_box, second_box)
            if intersection is not None:
                pair = frozenset((first_entry["name"], second_entry["name"]))
                if pair not in declared_pairs:
                    raise ValueError(
                        "Overlapping character boxes require an explicit occlusionGraph entry: "
                        f"{first_entry['name']} / {second_entry['name']}"
                    )
                allowed_box = allowed_box_by_pair[pair]
                if not (
                    allowed_box[0] <= intersection[0]
                    and allowed_box[1] <= intersection[1]
                    and allowed_box[2] >= intersection[2]
                    and allowed_box[3] >= intersection[3]
                ):
                    raise ValueError(
                        "allowedOverlapBBox must contain the complete intersecting action-box region: "
                        f"{first_entry['name']} / {second_entry['name']}"
                    )

    if require_reviewed_whitebox:
        review = data.get("combinedWhiteboxReview")
        if not review:
            raise ValueError("WHITEBOX_REVIEW_REQUIRED: combinedWhiteboxReview is missing.")
        require_fields(
            review,
            (
                "status",
                "reviewAuthority",
                "artifact",
                "artifactSha256",
                "depthReference",
                "depthReferenceSha256",
                "poseIds",
                "wholeImageChecked",
                "localTileCoverageComplete",
                "comparisonReport",
                "checks",
            ),
            "combinedWhiteboxReview",
        )
        if review["status"] != "passed" or review["reviewAuthority"] != "codex-self-check":
            raise ValueError(
                "WHITEBOX_REVIEW_REQUIRED: Codex pre-generation review must be passed."
            )
        if review["wholeImageChecked"] is not True or review["localTileCoverageComplete"] is not True:
            raise ValueError(
                "WHITEBOX_REVIEW_REQUIRED: full-frame and complete local-tile review are mandatory."
            )
        artifact = Path(review["artifact"])
        if not artifact.is_file():
            raise ValueError(f"Reviewed combined whitebox is missing: {artifact}")
        if sha256_file(artifact).lower() != str(review["artifactSha256"]).lower():
            raise ValueError("Reviewed combined whitebox hash does not match the artifact.")
        depth_reference = Path(review["depthReference"])
        if not depth_reference.is_file():
            raise ValueError(f"Reviewed depth reference is missing: {depth_reference}")
        if sha256_file(depth_reference).lower() != str(review["depthReferenceSha256"]).lower():
            raise ValueError("Reviewed depth reference hash does not match the artifact.")
        comparison_report = Path(review["comparisonReport"])
        if not comparison_report.is_file():
            raise ValueError(f"Whitebox comparison report is missing: {comparison_report}")
        checks = review["checks"]
        required_checks = (
            "timelineConformance",
            "storyBeatConformance",
            "performanceConformance",
            "affordanceConformance",
            "scaleConformance",
            "poseConformance",
            "supportContactConformance",
            "sceneOcclusionConformance",
            "castOcclusionConformance",
            "uiSafeAreaConformance",
        )
        require_fields(checks, required_checks, "combinedWhiteboxReview.checks")
        failed_checks = [name for name in required_checks if checks[name] != "pass"]
        if failed_checks:
            raise ValueError(
                "WHITEBOX_REVIEW_FAILED: " + ", ".join(failed_checks)
            )
        pose_ids = review["poseIds"]
        for entry, contract in loaded:
            expected = contract["target"]["poseDefinition"]["poseId"]
            if pose_ids.get(entry["name"]) != expected:
                raise ValueError(f"Reviewed pose ID mismatch for {entry['name']}.")
    return loaded


def validate_final_conformance(data: dict) -> None:
    validate_staging(data, True)
    review = data.get("formalConformanceReview")
    if not review:
        raise ValueError("FORMAL_REVIEW_REQUIRED: formalConformanceReview is missing.")
    require_fields(
        review,
        (
            "status",
            "reviewAuthority",
            "finalComposite",
            "finalCompositeSha256",
            "combinedWhitebox",
            "combinedWhiteboxSha256",
            "depthReference",
            "depthReferenceSha256",
            "wholeImageChecked",
            "localTileCoverageComplete",
            "comparisonReport",
            "attempt",
            "checks",
        ),
        "formalConformanceReview",
    )
    if review["status"] != "passed" or review["reviewAuthority"] != "codex-self-check":
        raise ValueError("FORMAL_REVIEW_REQUIRED: Codex final conformance review must be passed.")
    if review["wholeImageChecked"] is not True or review["localTileCoverageComplete"] is not True:
        raise ValueError(
            "FORMAL_REVIEW_REQUIRED: full-frame and complete local-tile review are mandatory."
        )
    attempt = int(review["attempt"])
    if not 1 <= attempt <= 6:
        raise ValueError("formalConformanceReview.attempt must be between 1 and 6 per branch.")
    for path_field, hash_field, label in (
        ("finalComposite", "finalCompositeSha256", "final composite"),
        ("combinedWhitebox", "combinedWhiteboxSha256", "combined whitebox"),
        ("depthReference", "depthReferenceSha256", "depth reference"),
    ):
        artifact = Path(review[path_field])
        if not artifact.is_file():
            raise ValueError(f"Reviewed {label} is missing: {artifact}")
        if sha256_file(artifact).lower() != str(review[hash_field]).lower():
            raise ValueError(f"Reviewed {label} hash does not match the artifact.")
    report = Path(review["comparisonReport"])
    if not report.is_file():
        raise ValueError(f"Final conformance comparison report is missing: {report}")
    required_checks = (
        "timelineConformance",
        "storyBeatConformance",
        "performanceConformance",
        "affordanceConformance",
        "scaleConformance",
        "poseConformance",
        "jointPlacementConformance",
        "supportContactConformance",
        "actionEnvelopeConformance",
        "sceneOcclusionConformance",
        "castOcclusionConformance",
        "uiSafeAreaConformance",
        "identityConformance",
        "costumeStateConformance",
        "styleConformance",
        "shadowConformance",
        "backgroundPreservationConformance",
    )
    checks = review["checks"]
    require_fields(checks, required_checks, "formalConformanceReview.checks")
    failed_checks = [name for name in required_checks if checks[name] != "pass"]
    if failed_checks:
        raise ValueError("FORMAL_CONFORMANCE_FAILED: " + ", ".join(failed_checks))


def validate_candidate_handoff(data: dict) -> None:
    review = data.get("candidateHandoff")
    if not review:
        raise ValueError("CANDIDATE_HANDOFF_REQUIRED: candidateHandoff is missing.")
    require_fields(
        review,
        (
            "status",
            "reviewAuthority",
            "attemptCount",
            "artifact",
            "artifactSha256",
            "comparisonReport",
            "failedChecks",
            "selectionReason",
            "candidateRoot",
        ),
        "candidateHandoff",
    )
    if review["status"] != "best-available" or review["reviewAuthority"] != "codex-self-check":
        raise ValueError("CANDIDATE_HANDOFF_REQUIRED: best-available Codex review is required.")
    if int(review["attemptCount"]) != 6:
        raise ValueError("candidateHandoff.attemptCount must be exactly 6.")
    failed_checks = review["failedChecks"]
    if not isinstance(failed_checks, list) or not failed_checks:
        raise ValueError("candidateHandoff.failedChecks must list unresolved gates.")
    if not str(review["selectionReason"]).strip():
        raise ValueError("candidateHandoff.selectionReason cannot be empty.")
    artifact = Path(review["artifact"])
    if not artifact.is_file():
        raise ValueError(f"Candidate artifact is missing: {artifact}")
    if sha256_file(artifact).lower() != str(review["artifactSha256"]).lower():
        raise ValueError("Candidate artifact hash does not match.")
    comparison_report = Path(review["comparisonReport"])
    if not comparison_report.is_file():
        raise ValueError(f"Candidate comparison report is missing: {comparison_report}")
    candidate_root = Path(review["candidateRoot"]).resolve()
    process_root = configured_root("NDC_ART_WORK_ROOT")
    if candidate_root == process_root or not candidate_root.is_relative_to(process_root):
        raise ValueError("Candidate handoff must stay in a child of the configured work root.")


def apply_occluders(image: Image.Image, base: Image.Image, polygons: list) -> Image.Image:
    if not polygons:
        return image
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        draw.polygon([tuple(point) for point in polygon], fill=255)
    return Image.composite(base, image, mask)


def render_whitebox(contract_or_staging_path: Path, output: Path, base_path: Path | None = None) -> None:
    data = load_contract(contract_or_staging_path)
    if "characters" in data:
        loaded = validate_staging(data)
        scene_path = base_path if base_path is not None else Path(data["scene"])
        scene = Image.open(scene_path).convert("RGBA")
        if scene.size != tuple(data["sceneSize"]):
            raise ValueError("Whitebox base dimensions differ from staging sceneSize.")
        base = scene.copy()
        for entry, contract in sorted(loaded, key=lambda item: int(item[0]["layerOrder"])):
            target = contract["target"]
            placement_class = target.get("placementClass", "standing")
            pose = get_exact_pose(target, placement_class)
            overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
            draw_volumetric_pose(ImageDraw.Draw(overlay), pose, entry["name"])
            scene = Image.alpha_composite(scene, overlay)
            scene = apply_occluders(scene, base, target.get("occluderPolygons", []))
    else:
        validate_contract(data)
        scene_path = base_path if base_path is not None else Path(data["scene"])
        scene = Image.open(scene_path).convert("RGBA")
        if scene.size != tuple(data["sceneSize"]):
            raise ValueError("Whitebox base dimensions differ from placement sceneSize.")
        base = scene.copy()
        target = data["target"]
        placement_class = target.get("placementClass", "standing")
        pose = get_exact_pose(target, placement_class)
        overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        draw_volumetric_pose(ImageDraw.Draw(overlay), pose, str(data.get("characterName", "")))
        scene = Image.alpha_composite(scene, overlay)
        scene = apply_occluders(scene, base, target.get("occluderPolygons", []))
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.save(output)


def render_shadow(contract_path: Path, output: Path) -> None:
    data = load_contract(contract_path)
    shadow = data["shadow"]
    size = tuple(data["sceneSize"])
    rgba = tuple(shadow.get("rgba", [0, 0, 0, 255]))
    if tuple(rgba[:3]) != (0, 0, 0):
        raise ValueError("NDC block shadow RGB must be pure black.")
    if rgba[3] != 255 and not shadow.get("opacityApproved", False):
        raise ValueError("Non-opaque shadow requires explicit opacityApproved=true.")
    if len(shadow.get("evidence", [])) < 2 and shadow.get("castPolygons"):
        raise ValueError("Cast shadow requires at least two light-direction cues.")
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for polygon in shadow.get("contactPolygons", []):
        draw.polygon([tuple(point) for point in polygon], fill=rgba)
    for polygon in shadow.get("castPolygons", []):
        draw.polygon([tuple(point) for point in polygon], fill=rgba)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def validate_state_assembly_contract(data: dict) -> None:
    assembly = data.get("stateAssembly")
    if not assembly:
        raise ValueError("State verification requires stateAssembly contract data.")
    require_fields(
        assembly,
        (
            "beforeIsMaster",
            "assemblyMode",
            "reuseMasterTransform",
            "assetCanvasSize",
            "allowedChangeMasks",
            "naturalSeamPaths",
            "facialAccessoryChanges",
            "occlusionStrategy",
        ),
        "stateAssembly",
    )
    if assembly["beforeIsMaster"] is not True:
        raise ValueError("The accepted before state must be the only state master.")
    if assembly["reuseMasterTransform"] is not True:
        raise ValueError("After state must reuse the exact master transform.")
    if assembly["assemblyMode"] not in {"registered-local-patch", "exact-master-canvas"}:
        raise ValueError(
            "stateAssembly.assemblyMode must be registered-local-patch or "
            "exact-master-canvas; independently generated full-body splices are forbidden."
        )
    canvas_size = tuple(assembly["assetCanvasSize"])
    if len(canvas_size) != 2 or min(canvas_size) <= 0:
        raise ValueError("stateAssembly.assetCanvasSize must contain positive width and height.")
    canvas_bbox = (0.0, 0.0, float(canvas_size[0]), float(canvas_size[1]))
    change_masks = assembly["allowedChangeMasks"]
    if not change_masks:
        raise ValueError("stateAssembly.allowedChangeMasks cannot be empty.")
    for index, change_mask in enumerate(change_masks):
        label = f"stateAssembly.allowedChangeMasks[{index}]"
        require_fields(change_mask, ("label", "bbox"), label)
        box = validate_bbox(change_mask["bbox"], f"{label}.bbox")
        if not (
            canvas_bbox[0] <= box[0] < box[2] <= canvas_bbox[2]
            and canvas_bbox[1] <= box[1] < box[3] <= canvas_bbox[3]
        ):
            raise ValueError(f"{label}.bbox must stay inside assetCanvasSize.")
    seam_paths = assembly["naturalSeamPaths"]
    if not seam_paths:
        raise ValueError("stateAssembly.naturalSeamPaths cannot be empty.")
    for index, seam in enumerate(seam_paths):
        label = f"stateAssembly.naturalSeamPaths[{index}]"
        require_fields(seam, ("label", "points"), label)
        points = seam["points"]
        if len(points) < 2 or any(not point_inside_bbox(point, canvas_bbox) for point in points):
            raise ValueError(f"{label}.points must contain at least two in-canvas points.")
        x_values = [float(point[0]) for point in points]
        y_values = [float(point[1]) for point in points]
        if max(x_values) - min(x_values) >= canvas_size[0] * 0.50 and max(y_values) - min(y_values) <= 2:
            raise ValueError("Broad horizontal state seams are forbidden.")
    for index, accessory in enumerate(assembly["facialAccessoryChanges"]):
        label = f"stateAssembly.facialAccessoryChanges[{index}]"
        require_fields(accessory, ("name", "anchors"), label)
        anchors = accessory["anchors"]
        require_fields(anchors, ("leftEye", "rightEye", "noseBridge"), f"{label}.anchors")
        if any(not point_inside_bbox(anchors[name], canvas_bbox) for name in anchors):
            raise ValueError(f"{label}.anchors must stay inside assetCanvasSize.")
    if assembly["occlusionStrategy"] not in {
        "none",
        "separate-source-occluder",
        "source-exact-irregular-mask",
    }:
        raise ValueError(
            "stateAssembly.occlusionStrategy forbids constant horizontal alpha cuts."
        )


def verify_states(contract_path: Path, before_path: Path, after_path: Path) -> None:
    data = load_contract(contract_path)
    validate_state_assembly_contract(data)
    before = Image.open(before_path).convert("RGBA")
    after = Image.open(after_path).convert("RGBA")
    if before.size != after.size:
        raise ValueError("State canvases differ.")
    for name, image in (("before", before), ("after", after)):
        alpha = image.getchannel("A")
        corners = (alpha.getpixel((0, 0)), alpha.getpixel((image.width - 1, 0)),
                   alpha.getpixel((0, image.height - 1)), alpha.getpixel((image.width - 1, image.height - 1)))
        if corners != (0, 0, 0, 0):
            raise ValueError(f"{name} has nontransparent corners.")
    for rectangle in data.get("freeze", {}).get("rectangles", []):
        box = tuple(rectangle)
        if ImageChops.difference(before.crop(box), after.crop(box)).getbbox() is not None:
            raise ValueError(f"Frozen rectangle changed: {box}")
    seam_bands = data.get("freeze", {}).get("seamBands", [])
    if not seam_bands:
        raise ValueError("At least one seam band is required for continuity review.")
    print("STATE_VERIFY_OK")
    print("Frozen rectangles are identical; seam bands still require visual continuity review.")


FINALIZATION_SCHEMA = "ndc-character-scene-finalization/v2"
FINALIZATION_IMPLEMENTATION_VERSION = 9
FINALIZATION_PROFILES = {"probe", "provisional", "formal"}
FINALIZATION_BASE_CHECKS = (
    "scope_timeline",
    "actual_ui",
    "support_contact",
    "scene_scale",
    "occlusion_layer_order",
    "identity_action_orientation",
    "whole_scene_review",
)


def resolve_manifest_path(value: str, manifest_path: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = manifest_path.parent / path
    return path.resolve()


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalization_branches(scope: dict) -> list[str]:
    """Resolve only scene facts; universal checks never disappear."""
    cast_count = scope.get("simultaneousCastCount")
    if not isinstance(cast_count, int) or isinstance(cast_count, bool) or cast_count < 1:
        raise ValueError("scope.simultaneousCastCount must be a positive integer.")
    interaction_type = scope.get("interactionType")
    if interaction_type not in {"pure-narrative", "exploration-click-pair"}:
        raise ValueError(
            "scope.interactionType must be pure-narrative or exploration-click-pair."
        )
    support_types = scope.get("supportTypes", [])
    if not isinstance(support_types, list) or not all(
        isinstance(value, str) and value for value in support_types
    ):
        raise ValueError("scope.supportTypes must be a string list.")
    branches: list[str] = []
    if interaction_type == "exploration-click-pair":
        branches.append("idle_click_continuity")
    if cast_count >= 2:
        branches.extend(
            ("multicast_links", "multi_actor_relative_scale", "pairwise_actor_occlusion")
        )
    if cast_count >= 3:
        branches.append("multicast_back_composition")
    if scope.get("hasSoftSupport") is True:
        branches.append("soft_support_response")
    if scope.get("hasRecliningOrElevatedActor") is True or any(
        value in {"bed", "sofa", "stretcher", "table", "elevated", "reclining"}
        for value in support_types
    ):
        branches.append("reclining_elevated_projection")
    return branches


def validate_ui_contract(ui: dict, manifest_path: Path) -> tuple[list[str], dict[str, Path]]:
    if ui.get("required") is not True:
        raise ValueError("ui.required must be true for every NPC scene.")
    variant = ui.get("variant")
    if variant not in {"left", "right", "both_or_dynamic"}:
        raise ValueError("ui.variant must be left, right or both_or_dynamic.")
    references = ui.get("references")
    if not isinstance(references, dict):
        raise ValueError("ui.references must map actual UI sides to files.")
    sides = [variant] if variant in {"left", "right"} else ["left", "right"]
    resolved: dict[str, Path] = {}
    for side in sides:
        value = references.get(side)
        if not isinstance(value, str) or not value:
            raise ValueError(f"ui.references.{side} is required for variant {variant}.")
        path = resolve_manifest_path(value, manifest_path)
        if not path.is_file():
            raise ValueError(f"Actual UI reference does not exist: {path}")
        resolved[side] = path
    return sides, resolved


def verified_evidence_signature(entry: dict, manifest_path: Path, label: str) -> list[dict]:
    evidence = entry.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError(f"{label}.evidence must bind at least one reviewed file.")
    signature: list[dict] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError(f"{label}.evidence[{index}] requires path and sha256.")
        path = resolve_manifest_path(item["path"], manifest_path)
        if not path.is_file():
            raise ValueError(f"{label}.evidence[{index}] does not exist: {path}")
        actual = sha256_file(path)
        if item.get("sha256") != actual:
            raise ValueError(f"{label}.evidence[{index}] SHA-256 does not match current bytes.")
        signature.append({"path": str(path), "sha256": actual})
    return signature


def finalization_check_state(
    criteria: dict,
    applicable: list[str],
    manifest_path: Path,
    profile: str,
) -> tuple[dict, list[dict], list[str], list[str]]:
    if not isinstance(criteria, dict):
        raise ValueError("criteria must be an object keyed by criterion name.")
    checks: dict[str, dict] = {}
    signature: list[dict] = []
    blocked: list[str] = []
    provisional: list[str] = []
    for name in applicable:
        entry = criteria.get(name)
        if not isinstance(entry, dict):
            checks[name] = {"status": "MISSING", "evidence": []}
            if profile == "provisional":
                provisional.append(f"missing duplicate or unfinished review evidence: {name}")
            else:
                blocked.append(f"missing required review criterion: {name}")
            continue
        status = entry.get("status")
        if status not in {"PASS", "PROVISIONAL", "FAIL", "NOT_CHECKED"}:
            raise ValueError(
                f"criteria.{name}.status must be PASS, PROVISIONAL, FAIL or NOT_CHECKED."
            )
        evidence = verified_evidence_signature(entry, manifest_path, f"criteria.{name}")
        tier = entry.get("tier", "H0" if status in {"FAIL", "NOT_CHECKED"} else None)
        if tier is not None and tier not in {"H0", "H1", "H2", "H3"}:
            raise ValueError(f"criteria.{name}.tier must be H0, H1, H2 or H3.")
        checks[name] = {"status": status, "tier": tier, "evidence": evidence}
        signature.append({"name": name, "status": status, "tier": tier, "evidence": evidence})
        if status in {"FAIL", "NOT_CHECKED"}:
            if tier == "H0" or profile != "provisional":
                blocked.append(f"required review criterion is {status} at {tier}: {name}")
            else:
                provisional.append(f"soft review criterion is {status} at {tier}: {name}")
        elif status == "PROVISIONAL":
            provisional.append(name)
    return checks, signature, blocked, provisional


def validate_anatomy_coverage(scope: dict, required_layer_ids: list[str], manifest_path: Path) -> tuple[list[dict], list[str]]:
    entries = scope.get("anatomyCoverage")
    if not isinstance(entries, list):
        raise ValueError("scope.anatomyCoverage must be a list covering every required layer.")
    normalized: list[dict] = []
    blocked: list[str] = []
    ids: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"scope.anatomyCoverage[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object.")
        layer_id = entry.get("id")
        mode = entry.get("mode")
        if not isinstance(layer_id, str) or not layer_id or layer_id in ids:
            raise ValueError(f"{label}.id must be unique non-empty text.")
        if mode not in {"FULL_IN_FRAME", "SCENE_OCCLUDED", "FRAME_CROPPED_FOREGROUND"}:
            raise ValueError(f"{label}.mode is invalid.")
        ids.add(layer_id)
        evidence = verified_evidence_signature(entry, manifest_path, label)
        item = {"id": layer_id, "mode": mode, "evidence": evidence}
        if entry.get("visibleAnatomyReview") != "PASS":
            blocked.append(f"visible anatomy is not PASS: {layer_id}")
        if mode in {"FULL_IN_FRAME", "SCENE_OCCLUDED"}:
            master = entry.get("completeMaster")
            try:
                master_path = resolve_manifest_path(master.get("path", ""), manifest_path) if isinstance(master, dict) else Path()
                if not master_path.is_file() or master.get("sha256") != sha256_file(master_path):
                    raise ValueError
                item["completeMaster"] = {"path": str(master_path), "sha256": sha256_file(master_path)}
            except (OSError, ValueError, TypeError):
                blocked.append(f"complete head-to-toe master is missing or stale: {layer_id}")
            if entry.get("completeMasterReview") != "PASS":
                blocked.append(f"complete master review is not PASS: {layer_id}")
        else:
            if entry.get("naturalFrameExit") is not True:
                blocked.append(f"foreground crop is not a natural frame exit: {layer_id}")
            if entry.get("visibleAnatomyComplete") is not True:
                blocked.append(f"foreground crop has incomplete visible anatomy: {layer_id}")
            support = entry.get("offFrameScaleSupportEvidence")
            if not isinstance(support, list) or not support:
                blocked.append(f"foreground crop lacks off-frame scale/support evidence: {layer_id}")
            else:
                item["offFrameScaleSupportEvidence"] = verified_evidence_signature(
                    {"evidence": support}, manifest_path, label + ".offFrameScaleSupportEvidence"
                )
        normalized.append(item)
    missing = sorted(set(required_layer_ids) - ids)
    extra = sorted(ids - set(required_layer_ids))
    if missing:
        blocked.append("anatomy coverage missing required layers: " + ", ".join(missing))
    if extra:
        blocked.append("anatomy coverage has unknown layers: " + ", ".join(extra))
    return normalized, blocked


def validate_ps_handoff(data: object, manifest_path: Path) -> tuple[dict, list[str]]:
    if data is None:
        return {"used": False}, []
    if not isinstance(data, dict) or data.get("used") is not True:
        raise ValueError("psSession must be omitted or declare used:true.")
    blocked: list[str] = []
    owner = data.get("ownerTaskId")
    if not isinstance(owner, str) or not owner:
        blocked.append("Photoshop ownerTaskId is missing")
    if data.get("openDocumentCount") != 0:
        blocked.append("Photoshop handoff requires actual docs0")
    if data.get("inFlightCommandCount") != 0 or data.get("unknownCommandCount") != 0:
        blocked.append("Photoshop handoff requires queue0 and no unknown command")
    if data.get("handoffStatus") != "RELEASED":
        blocked.append("Photoshop handoffStatus must be RELEASED")
    evidence = verified_evidence_signature(data, manifest_path, "psSession")
    capability = data.get("capabilitySnapshot")
    capability_path = None
    if isinstance(capability, dict):
        capability_path = resolve_manifest_path(str(capability.get("path", "")), manifest_path)
    if not capability_path or not capability_path.is_file() or capability.get("sha256") != sha256_file(capability_path):
        blocked.append("current Photoshop capability snapshot is missing or stale")
    return {
        "used": True,
        "ownerTaskId": owner,
        "openDocumentCount": data.get("openDocumentCount"),
        "inFlightCommandCount": data.get("inFlightCommandCount"),
        "unknownCommandCount": data.get("unknownCommandCount"),
        "handoffStatus": data.get("handoffStatus"),
        "evidence": evidence,
        "capabilitySnapshot": (
            {"path": str(capability_path), "sha256": sha256_file(capability_path)}
            if capability_path and capability_path.is_file() else None
        ),
    }, blocked


def _load_rgba_layer(item: dict, manifest_path: Path, label: str) -> tuple[Path, Image.Image]:
    path_value = item.get("path")
    if not isinstance(path_value, str) or not path_value:
        raise ValueError(f"{label}.path is required.")
    path = resolve_manifest_path(path_value, manifest_path)
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    source = Image.open(path)
    if source.mode != "RGBA":
        raise ValueError(f"{label} must be an RGBA image, not {source.mode}.")
    image = source.copy()
    alpha = image.getchannel("A")
    extrema = alpha.getextrema()
    if extrema[0] == 255 or extrema[1] == 0:
        raise ValueError(f"{label} needs both transparent and visible pixels.")
    return path, image


def validate_extraction_layers(
    extraction: dict,
    required_layer_ids: list[str],
    profile: str,
    manifest_path: Path,
) -> tuple[list[dict], list[str], list[str], dict]:
    layers = extraction.get("layers", [])
    if not isinstance(layers, list):
        raise ValueError("extraction.layers must be a list.")
    normalized: list[dict] = []
    ids: set[str] = set()
    blocked: list[str] = []
    provisional: list[str] = []
    first_usable = False
    formal_layer_ids: list[str] = []
    for index, item in enumerate(layers):
        label = f"extraction.layers[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be an object.")
        layer_id = item.get("id")
        quality = item.get("quality")
        if not isinstance(layer_id, str) or not layer_id or layer_id in ids:
            raise ValueError(f"{label}.id must be unique non-empty text.")
        if quality not in {"usable", "formal"}:
            raise ValueError(f"{label}.quality must be usable or formal.")
        ids.add(layer_id)
        path, image = _load_rgba_layer(item, manifest_path, label)
        structural = item.get("structuralReview")
        edge = item.get("edgeReview")
        if structural != "PASS":
            blocked.append(f"H0 structural Alpha is not PASS: {layer_id}")
        if edge not in {"PASS", "PROVISIONAL", "FAIL"}:
            raise ValueError(f"{label}.edgeReview must be PASS, PROVISIONAL or FAIL.")
        if edge == "FAIL":
            blocked.append(f"H1/H2 edge review failed: {layer_id}")
        elif edge == "PROVISIONAL":
            provisional.append(f"H1/H2 edge review is provisional: {layer_id}")
        review_evidence: list[dict] = []
        if item.get("reviewEvidence"):
            review_evidence = verified_evidence_signature(
                {"evidence": item["reviewEvidence"]}, manifest_path, label
            )
        else:
            blocked.append(f"hash-bound Alpha review evidence is missing: {layer_id}")
        normalized.append(
            {
                "id": layer_id,
                "quality": quality,
                "path": str(path),
                "sha256": sha256_file(path),
                "xy": item.get("xy", [0, 0]),
                "structuralReview": structural,
                "edgeReview": edge,
                "reviewEvidence": review_evidence,
                "image": image,
            }
        )
        if structural == "PASS" and edge in {"PASS", "PROVISIONAL"}:
            first_usable = True
            if quality == "formal" and edge == "PASS":
                formal_layer_ids.append(layer_id)
    missing = sorted(set(required_layer_ids) - ids)
    if not first_usable:
        blocked.append("no first usable RGBA exists")
    if profile == "formal":
        for layer_id in required_layer_ids:
            match = next((item for item in normalized if item["id"] == layer_id), None)
            if match is None:
                blocked.append(f"required formal RGBA is missing: {layer_id}")
            elif match["quality"] != "formal":
                blocked.append(f"required layer is not formal RGBA: {layer_id}")
            elif match["edgeReview"] != "PASS":
                blocked.append(f"formal H1/H2 edge review is not PASS: {layer_id}")
    routes = extraction.get("routeExhaustion", [])
    if not isinstance(routes, list):
        raise ValueError("extraction.routeExhaustion must be a list.")
    terminal = {"FORMAL_PASS", "FAILED", "NOT_APPLICABLE", "UNSUPPORTED"}
    exhausted = bool(routes) and all(
        isinstance(item, dict) and item.get("status") in terminal for item in routes
    )
    route_state = {
        "firstUsableRgba": first_usable,
        "firstFormalRgba": bool(formal_layer_ids),
        "formalLayerIds": sorted(formal_layer_ids),
        "stopRemainingRoutesForLayerIds": sorted(formal_layer_ids),
        "stopRemainingRoutes": bool(required_layer_ids) and set(required_layer_ids) <= set(formal_layer_ids),
        "allApplicableRoutesExhausted": exhausted,
        "missingLayerIds": missing,
    }
    if profile != "probe" and not first_usable and not exhausted:
        blocked.append("continue remaining applicable supported extraction routes")
    return normalized, blocked, provisional, route_state


def _alpha_overlay(base: Image.Image, overlay: Image.Image, xy: list | tuple = (0, 0)) -> None:
    if not isinstance(xy, (list, tuple)) or len(xy) != 2:
        raise ValueError("Each extraction layer xy must be [x, y].")
    x, y = (int(round(float(value))) for value in xy)
    base.alpha_composite(overlay, dest=(x, y))


def _fit_panel(image: Image.Image, size: tuple[int, int], background: tuple[int, int, int]) -> Image.Image:
    panel = Image.new("RGB", size, background)
    copy = image.convert("RGBA")
    copy.thumbnail((size[0] - 24, size[1] - 48), Image.Resampling.LANCZOS)
    x = (size[0] - copy.width) // 2
    y = 34 + (size[1] - 34 - copy.height) // 2
    panel.paste(copy, (x, y), copy)
    return panel


def _apply_ui(base: Image.Image, ui_path: Path) -> Image.Image:
    overlay = Image.open(ui_path).convert("RGBA")
    if overlay.size != base.size:
        raise ValueError(
            f"UI reference must already use the exact scene canvas; no implicit resize/placement: {ui_path}"
        )
    result = base.copy().convert("RGBA")
    result.alpha_composite(overlay, dest=(0, 0))
    return result


def _save_variant_board(
    base: Image.Image,
    sides: list[str],
    ui_paths: dict[str, Path],
    output: Path,
) -> None:
    variants = [_apply_ui(base, ui_paths[side]) for side in sides]
    if len(variants) == 1:
        output.parent.mkdir(parents=True, exist_ok=True)
        variants[0].save(output)
        return
    board = Image.new("RGBA", (base.width * len(variants), base.height), (0, 0, 0, 0))
    for index, variant in enumerate(variants):
        board.alpha_composite(variant, dest=(index * base.width, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output)


def render_matte_contact_sheet(layers: list[dict], scene: Image.Image, output: Path) -> None:
    if not layers:
        return
    sampled_tone = tuple(scene.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0)))
    luminance = 0.2126 * sampled_tone[0] + 0.7152 * sampled_tone[1] + 0.0722 * sampled_tone[2]
    tone_factor = min(1.0, 72.0 / max(luminance, 1.0))
    scene_tone = tuple(max(8, int(round(channel * tone_factor))) for channel in sampled_tone)
    backgrounds = ((0, 0, 0), (255, 255, 255), scene_tone)
    panel_size = (360, 300)
    board = Image.new(
        "RGB", (panel_size[0] * len(backgrounds), panel_size[1] * len(layers)), (32, 32, 32)
    )
    for row, item in enumerate(layers):
        for column, background in enumerate(backgrounds):
            panel = _fit_panel(item["image"], panel_size, background)
            draw = ImageDraw.Draw(panel)
            draw.rectangle((0, 0, panel_size[0], 30), fill=(28, 28, 28))
            draw.text((10, 8), f"{item['id']} | {('black', 'white', 'dark-scene-tone')[column]}", fill=(240, 240, 240))
            board.paste(panel, (column * panel_size[0], row * panel_size[1]))
    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output)


def validator_signature(validators: list, profile: str, manifest_path: Path) -> list[dict]:
    signature: list[dict] = []
    for index, item in enumerate(validators):
        if not isinstance(item, dict):
            raise ValueError(f"validators[{index}] must be an object.")
        profiles = item.get("profiles", ["probe", "provisional", "formal"])
        if not isinstance(profiles, list) or not set(profiles) <= FINALIZATION_PROFILES:
            raise ValueError(f"validators[{index}].profiles contains an unsupported profile.")
        if profile not in profiles:
            continue
        contract = resolve_manifest_path(str(item.get("contract", "")), manifest_path)
        if not contract.is_file():
            raise ValueError(f"validators[{index}].contract does not exist: {contract}")
        signature.append(
            {
                "name": item.get("name"),
                "contract": str(contract),
                "sha256": sha256_file(contract),
                "required": item.get("required", True) is True,
            }
        )
    return signature


def run_finalization_validators(
    validators: list,
    profile: str,
    manifest_path: Path,
    output_dir: Path,
) -> tuple[list[dict], list[str]]:
    script_root = Path(__file__).resolve().parent
    results: list[dict] = []
    blocked: list[str] = []
    for index, item in enumerate(validators):
        profiles = item.get("profiles", ["probe", "provisional", "formal"])
        if profile not in profiles:
            continue
        name = item.get("name")
        contract = resolve_manifest_path(str(item.get("contract", "")), manifest_path)
        required = item.get("required", True) is True
        try:
            if name == "final-conformance":
                validate_final_conformance(load_contract(contract))
                detail = "FINAL_CONFORMANCE_OK"
            elif name == "whitebox-gate":
                loaded = validate_staging(load_contract(contract), True)
                detail = f"WHITEBOX_GATE_OK characters={len(loaded)}"
            elif name == "candidate-handoff":
                validate_candidate_handoff(load_contract(contract))
                detail = "CANDIDATE_HANDOFF_OK"
            else:
                report_path = output_dir / "validator-reports" / f"{index:02d}-{name}.json"
                commands = {
                    "production-ledger": [sys.executable, str(script_root / "production_gate.py"), str(contract), "--report", str(report_path)],
                    "importance-profile": [sys.executable, str(script_root / "validate_importance_profile.py"), "--profile", str(contract), "--output", str(report_path)],
                    "multicast-back-composition": [sys.executable, str(script_root / "validate_multicast_back_composition.py"), "--contract", str(contract), "--output", str(report_path)],
                    "visual-review": [sys.executable, str(script_root / "visual_review_gate.py"), str(contract), str(report_path.parent / f"{index:02d}-visual")],
                }
                if name not in commands:
                    raise ValueError(f"Unsupported finalization validator: {name}")
                completed = subprocess.run(
                    commands[name], capture_output=True, text=True, encoding="utf-8",
                    errors="replace", check=False
                )
                detail = (completed.stdout or completed.stderr).strip()
                if completed.returncode != 0:
                    raise ValueError(detail or f"validator exited {completed.returncode}")
            results.append({"name": name, "status": "PASS", "detail": detail})
        except (OSError, ValueError, KeyError, TypeError) as error:
            results.append({"name": name, "status": "FAIL", "detail": str(error)})
            if required:
                blocked.append(f"required validator failed: {name}")
    return results, blocked


def finalization_cache_key(
    profile: str,
    scope: dict,
    sides: list[str],
    ui_paths: dict[str, Path],
    scene_path: Path,
    layout_path: Path,
    layers: list[dict],
    criteria_signature: list[dict],
    validators_signature: list[dict],
    anatomy_signature: list[dict],
    ps_handoff: dict,
) -> str:
    cache_criteria = [
        {
            "name": item["name"],
            "status": item["status"],
            "tier": item.get("tier"),
            "evidenceSha256": sorted(evidence["sha256"] for evidence in item["evidence"]),
        }
        for item in criteria_signature
    ]
    cache_validators = [
        {key: item[key] for key in ("name", "sha256", "required")}
        for item in validators_signature
    ]
    payload = {
        "implementationVersion": FINALIZATION_IMPLEMENTATION_VERSION,
        "profile": profile,
        "scope": {
            "interactionType": scope.get("interactionType"),
            "simultaneousCastCount": scope.get("simultaneousCastCount"),
            "supportTypes": sorted(scope.get("supportTypes", [])),
            "hasSoftSupport": scope.get("hasSoftSupport") is True,
            "hasRecliningOrElevatedActor": scope.get("hasRecliningOrElevatedActor") is True,
            "requiredLayerIds": sorted(scope.get("requiredLayerIds", [])),
        },
        "ui": [{"side": side, "sha256": sha256_file(ui_paths[side])} for side in sides],
        "pixels": {
            "scene": sha256_file(scene_path),
            "layout": sha256_file(layout_path),
            "layers": [
                {
                    "id": item["id"],
                    "quality": item["quality"],
                    "sha256": item["sha256"],
                    "xy": item["xy"],
                    "structuralReview": item["structuralReview"],
                    "edgeReview": item["edgeReview"],
                    "reviewEvidenceSha256": sorted(
                        evidence["sha256"] for evidence in item["reviewEvidence"]
                    ),
                }
                for item in layers
            ],
        },
        "criteria": cache_criteria,
        "validators": cache_validators,
        "anatomyCoverage": anatomy_signature,
        "psHandoff": {
            "used": ps_handoff.get("used", False),
            "openDocumentCount": ps_handoff.get("openDocumentCount"),
            "inFlightCommandCount": ps_handoff.get("inFlightCommandCount"),
            "unknownCommandCount": ps_handoff.get("unknownCommandCount"),
            "handoffStatus": ps_handoff.get("handoffStatus"),
            "evidenceSha256": sorted(item["sha256"] for item in ps_handoff.get("evidence", [])),
            "capabilitySha256": (ps_handoff.get("capabilitySnapshot") or {}).get("sha256"),
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_timing_ledger(records: list, pixel_preview_ready: bool) -> tuple[list[dict], list[str], float]:
    if not isinstance(records, list):
        raise ValueError("timingLedger must be a list.")
    normalized: list[dict] = []
    actions: list[str] = []
    targets = {"layout": 600, "pixel-preview": 900, "finalization": 600}
    total_active = 0.0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"timingLedger[{index}] must be an object.")
        require_fields(
            record,
            (
                "phase",
                "started_at",
                "finished_at",
                "active_seconds",
                "external_wait_seconds",
                "cache_hit",
                "result",
                "block_reason",
            ),
            f"timingLedger[{index}]",
        )
        active = record["active_seconds"]
        wait = record["external_wait_seconds"]
        if not isinstance(active, (int, float)) or active < 0:
            raise ValueError(f"timingLedger[{index}].active_seconds must be non-negative.")
        if not isinstance(wait, (int, float)) or wait < 0:
            raise ValueError(f"timingLedger[{index}].external_wait_seconds must be non-negative.")
        total_active += float(active)
        normalized.append(dict(record))
        target = targets.get(record["phase"])
        if target is not None and active > target:
            actions.append(f"{record['phase']} exceeded active-time target {target}s")
    if total_active >= 1800 and not pixel_preview_ready:
        actions.append("SWITCH_METHOD: 30m active without Pixel Proof Preview")
    if total_active >= 3600:
        actions.append("PACKAGE_PROVISIONAL: stop low-value polish at 60m active")
    return normalized, actions, total_active


def finalize_scene(manifest_path: Path, profile: str) -> dict:
    started_clock = time.perf_counter()
    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    if profile not in FINALIZATION_PROFILES:
        raise ValueError("profile must be probe, provisional or formal.")
    manifest_path = manifest_path.resolve()
    data = load_contract(manifest_path)
    require_fields(data, ("schema", "sceneId", "scope", "ui", "artifacts", "criteria"), "manifest")
    if data["schema"] != FINALIZATION_SCHEMA:
        raise ValueError(f"manifest.schema must be {FINALIZATION_SCHEMA}.")
    scope = data["scope"]
    if not isinstance(scope, dict):
        raise ValueError("scope must be an object.")
    required_layer_ids = scope.get("requiredLayerIds", [])
    if not isinstance(required_layer_ids, list) or not required_layer_ids or len(required_layer_ids) != len(set(required_layer_ids)) or not all(
        isinstance(value, str) and value for value in required_layer_ids
    ):
        raise ValueError("scope.requiredLayerIds must be a non-empty distinct string list.")
    branches = finalization_branches(scope)
    applicable = list(FINALIZATION_BASE_CHECKS) + branches
    anatomy_coverage, anatomy_blocked = validate_anatomy_coverage(
        scope, required_layer_ids, manifest_path
    )
    ps_handoff, ps_blocked = validate_ps_handoff(data.get("psSession"), manifest_path)
    sides, ui_paths = validate_ui_contract(data["ui"], manifest_path)
    artifacts = data["artifacts"]
    if not isinstance(artifacts, dict):
        raise ValueError("artifacts must be an object.")
    scene_path = resolve_manifest_path(str(artifacts.get("sourceScene", "")), manifest_path)
    layout_path = resolve_manifest_path(str(artifacts.get("layoutSource", "")), manifest_path)
    for label, path in (("sourceScene", scene_path), ("layoutSource", layout_path)):
        if not path.is_file():
            raise ValueError(f"artifacts.{label} does not exist: {path}")
    scene = Image.open(scene_path).convert("RGBA")
    layout = Image.open(layout_path).convert("RGBA")
    if layout.size != scene.size:
        raise ValueError("artifacts.layoutSource must use the source-scene canvas.")
    checks, criteria_sig, blocked, provisional = finalization_check_state(
        data["criteria"], applicable, manifest_path, profile
    )
    blocked.extend(anatomy_blocked)
    blocked.extend(ps_blocked)
    extraction = data.get("extraction", {})
    if not isinstance(extraction, dict):
        raise ValueError("extraction must be an object.")
    layers, extraction_blocked, extraction_provisional, route_state = validate_extraction_layers(
        extraction, required_layer_ids, profile, manifest_path
    )
    blocked.extend(extraction_blocked)
    if profile != "probe":
        provisional.extend(extraction_provisional)
    validators = data.get("validators", [])
    if not isinstance(validators, list):
        raise ValueError("validators must be a list.")
    validators_sig = validator_signature(validators, profile, manifest_path)
    if profile == "formal":
        validator_names = {item["name"] for item in validators_sig}
        for required_name in ("production-ledger", "final-conformance"):
            if required_name not in validator_names:
                blocked.append(f"formal profile requires validator: {required_name}")
    output_value = data.get("outputDir", f"finalization/{data['sceneId']}")
    if not isinstance(output_value, str) or not output_value:
        raise ValueError("outputDir must be a non-empty path string.")
    output_dir = resolve_manifest_path(output_value, manifest_path)
    if os.environ.get("NDC_ART_WORK_ROOT"):
        work_root = configured_root("NDC_ART_WORK_ROOT")
        if not is_within(output_dir, work_root):
            raise ValueError(
                "Finalization previews, evidence and provisional outputs must stay under NDC_ART_WORK_ROOT."
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_key = finalization_cache_key(
        profile, scope, sides, ui_paths, scene_path, layout_path, layers,
        criteria_sig, validators_sig, anatomy_coverage, ps_handoff,
    )
    report_path = output_dir / f"finalize-{profile}-report.json"
    cache_hit = False
    prior: dict | None = None
    if report_path.is_file():
        try:
            loaded = load_contract(report_path)
            required_outputs = [Path(value) for value in loaded.get("outputs", {}).values()]
            if loaded.get("cacheKey") == cache_key and all(path.is_file() for path in required_outputs):
                prior = loaded
                cache_hit = True
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            prior = None
    if cache_hit and prior is not None:
        outputs = prior["outputs"]
    else:
        layout_output = output_dir / f"layout-preview-{profile}.png"
        _save_variant_board(layout, sides, ui_paths, layout_output)
        outputs = {"layoutPreview": str(layout_output.resolve())}
        usable_layers = [
            item
            for item in layers
            if item["structuralReview"] == "PASS" and item["edgeReview"] in {"PASS", "PROVISIONAL"}
        ]
        pixel_preview_ready = bool(usable_layers)
        if usable_layers:
            composite = scene.copy()
            for item in usable_layers:
                _alpha_overlay(composite, item["image"], item["xy"])
            pixel_output = output_dir / f"pixel-proof-preview-{profile}.png"
            _save_variant_board(composite, sides, ui_paths, pixel_output)
            outputs["pixelProofPreview"] = str(pixel_output.resolve())
            if profile != "probe":
                matte_output = output_dir / f"matte-contact-sheet-{profile}.png"
                render_matte_contact_sheet(usable_layers, scene, matte_output)
                outputs["matteContactSheet"] = str(matte_output.resolve())
            if profile != "probe" and data.get("reconstruction", {}).get("enabled") is True:
                reconstruction_output = output_dir / f"reconstruction-{profile}.png"
                composite.save(reconstruction_output)
                outputs["reconstruction"] = str(reconstruction_output.resolve())
                xy_output = output_dir / f"xy-manifest-{profile}.json"
                write_json(
                    xy_output,
                    {
                        "sceneId": data["sceneId"],
                        "sourceScene": {"path": str(scene_path), "sha256": sha256_file(scene_path)},
                        "layers": [
                            {key: item[key] for key in ("id", "path", "sha256", "xy", "quality")}
                            for item in usable_layers
                        ],
                    },
                )
                outputs["xyManifest"] = str(xy_output.resolve())
    validator_results, validator_blocked = run_finalization_validators(
        validators, profile, manifest_path, output_dir
    )
    blocked.extend(validator_blocked)
    if profile != "provisional" and provisional:
        blocked.extend(
            f"provisional review is not accepted by {profile}: {item}" for item in provisional
        )
    if blocked:
        result = "BLOCKED"
    elif profile == "provisional" or provisional:
        result = "PROVISIONAL"
    else:
        result = "PASS"
    block_reason = "; ".join(blocked)
    pixel_preview_ready = "pixelProofPreview" in outputs
    timing_records, schedule_actions, total_active_seconds = validate_timing_ledger(
        data.get("timingLedger", []), pixel_preview_ready
    )
    if profile == "formal":
        package_state = "FORMAL_CANDIDATE" if result == "PASS" else "FORMAL_REVIEW_BLOCKED"
    elif profile == "provisional":
        package_state = "H0_BLOCKED_PACKAGE" if result == "BLOCKED" else "PROVISIONAL_SCENE_PACKAGE"
    else:
        package_state = "PIXEL_PROOF_READY" if result == "PASS" else "PROBE_BLOCKED"
    finished_at = datetime.now().astimezone().isoformat(timespec="seconds")
    timing_records.append(
        {
            "phase": "finalization",
            "started_at": started_at,
            "finished_at": finished_at,
            "active_seconds": round(time.perf_counter() - started_clock, 3),
            "external_wait_seconds": 0.0,
            "cache_hit": cache_hit,
            "result": result,
            "block_reason": block_reason,
        }
    )
    timing_path = output_dir / "timing-ledger.json"
    write_json(timing_path, timing_records)
    canonical_path = output_dir / "finalization.json"
    summary_path = output_dir / "finalization-summary.txt"
    outputs["finalization"] = str(canonical_path.resolve())
    outputs["summary"] = str(summary_path.resolve())
    report = {
        "schema": "ndc-character-scene-finalization-report/v1",
        "implementationVersion": FINALIZATION_IMPLEMENTATION_VERSION,
        "sceneId": data["sceneId"],
        "profile": profile,
        "result": result,
        "packageState": package_state,
        "cacheKey": cache_key,
        "cacheHit": cache_hit,
        "ui": {"required": True, "variant": data["ui"]["variant"], "reviewedSides": sides},
        "inputBindings": {
            "sourceScene": {"path": str(scene_path), "sha256": sha256_file(scene_path)},
            "layoutSource": {"path": str(layout_path), "sha256": sha256_file(layout_path)},
            "ui": [
                {"side": side, "path": str(ui_paths[side]), "sha256": sha256_file(ui_paths[side])}
                for side in sides
            ],
            "rgbaLayers": [
                {key: item[key] for key in ("id", "path", "sha256", "xy", "quality", "structuralReview", "edgeReview", "reviewEvidence")}
                for item in layers
            ],
        },
        "universalChecks": list(FINALIZATION_BASE_CHECKS),
        "conditionalBranches": branches,
        "anatomyCoverage": anatomy_coverage,
        "photoshopHandoff": ps_handoff,
        "checks": checks,
        "routeState": route_state,
        "validators": validator_results,
        "outputs": outputs,
        "blockedReasons": blocked,
        "provisionalReasons": provisional,
        "scheduleActions": schedule_actions,
        "totalActiveSecondsBeforeFinalization": total_active_seconds,
        "timingLedger": str(timing_path.resolve()),
        "note": (
            "PASS is limited to this execution profile and requires explicit hash-bound review evidence. "
            "The finalizer does not infer artistic approval from pixels or technical metrics."
        ),
    }
    write_json(report_path, report)
    write_json(canonical_path, report)
    stable_outputs = {
        key: {"file": Path(value).name, "sha256": sha256_file(Path(value))}
        for key, value in outputs.items()
        if key not in {"finalization", "summary", "packageIndex"} and Path(value).is_file()
    }
    package_index_path = output_dir / "package-index.json"
    write_json(
        package_index_path,
        {
            "schema": "ndc-character-scene-package-index/v1",
            "sceneId": data["sceneId"],
            "profile": profile,
            "packageState": package_state,
            "cacheKey": cache_key,
            "sourceSceneSha256": sha256_file(scene_path),
            "requiredLayerIds": sorted(required_layer_ids),
            "layers": [
                {key: item[key] for key in ("id", "sha256", "xy", "quality", "structuralReview", "edgeReview")}
                for item in sorted(layers, key=lambda value: value["id"])
            ],
            "artifacts": stable_outputs,
        },
    )
    outputs["packageIndex"] = str(package_index_path.resolve())
    write_json(report_path, report)
    write_json(canonical_path, report)
    summary_path.write_text(
        "\n".join(
            (
                f"scene={data['sceneId']}",
                f"profile={profile}",
                f"result={result}",
                f"package_state={package_state}",
                f"cache_hit={str(cache_hit).lower()}",
                f"blocked={'; '.join(report['blockedReasons']) or '-'}",
                f"provisional={'; '.join(report['provisionalReasons']) or '-'}",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-contract")
    validate.add_argument("contract", type=Path)
    place = subparsers.add_parser("place-proxy")
    place.add_argument("contract", type=Path)
    place.add_argument("output", type=Path)
    place.add_argument("--base", type=Path, default=None)
    staging = subparsers.add_parser("validate-staging")
    staging.add_argument("contract", type=Path)
    staging.add_argument("--require-reviewed-whitebox", action="store_true")
    whitebox = subparsers.add_parser("render-whitebox")
    whitebox.add_argument("contract", type=Path)
    whitebox.add_argument("output", type=Path)
    whitebox.add_argument("--base", type=Path, default=None)
    whitebox_gate = subparsers.add_parser("validate-whitebox-gate")
    whitebox_gate.add_argument("contract", type=Path)
    final_gate = subparsers.add_parser("validate-final-conformance")
    final_gate.add_argument("contract", type=Path)
    candidate_gate = subparsers.add_parser("validate-candidate-handoff")
    candidate_gate.add_argument("contract", type=Path)
    shadow = subparsers.add_parser("render-shadow")
    shadow.add_argument("contract", type=Path)
    shadow.add_argument("output", type=Path)
    states = subparsers.add_parser("verify-states")
    states.add_argument("contract", type=Path)
    states.add_argument("before", type=Path)
    states.add_argument("after", type=Path)
    finalize = subparsers.add_parser("finalize-scene")
    finalize.add_argument("--manifest", required=True, type=Path)
    finalize.add_argument("--profile", required=True, choices=sorted(FINALIZATION_PROFILES))
    args = parser.parse_args()
    if args.command == "validate-contract":
        data = load_contract(args.contract)
        median, spread = validate_contract(data)
        if data.get("calibration", {}).get("sceneScaleEvidence"):
            print(f"CONTRACT_OK shared geometry; reviewed image height={median:.2f}px (not a camera calibration claim)")
        else:
            print(f"CONTRACT_OK median={median:.2f}px spread={spread:.4f}")
    elif args.command == "place-proxy":
        place_proxy(args.contract, args.output, args.base)
    elif args.command == "validate-staging":
        loaded = validate_staging(load_contract(args.contract), args.require_reviewed_whitebox)
        print(f"STAGING_OK characters={len(loaded)}")
    elif args.command == "render-whitebox":
        render_whitebox(args.contract, args.output, args.base)
        print(f"WHITEBOX_RENDER_OK output={args.output}")
    elif args.command == "validate-whitebox-gate":
        loaded = validate_staging(load_contract(args.contract), True)
        print(f"WHITEBOX_GATE_OK characters={len(loaded)}")
    elif args.command == "validate-final-conformance":
        validate_final_conformance(load_contract(args.contract))
        print("FINAL_CONFORMANCE_OK")
    elif args.command == "validate-candidate-handoff":
        validate_candidate_handoff(load_contract(args.contract))
        print("CANDIDATE_HANDOFF_OK")
    elif args.command == "render-shadow":
        render_shadow(args.contract, args.output)
    elif args.command == "verify-states":
        verify_states(args.contract, args.before, args.after)
    elif args.command == "finalize-scene":
        report = finalize_scene(args.manifest, args.profile)
        print(
            f"FINALIZE_SCENE_{report['result']} profile={report['profile']} "
            f"cache_hit={str(report['cacheHit']).lower()}"
        )
        if report["result"] == "BLOCKED":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
