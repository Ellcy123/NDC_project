from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


NDC_ROOT = Path(r"D:\Codex\NDC")


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
    head_height = head_box[3] - head_box[1]
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
    try:
        delivery_root.resolve().relative_to(NDC_ROOT.resolve())
    except ValueError as error:
        raise ValueError("deliveryRoot must stay under D:\\Codex\\NDC.") from error
    if "工作过程文件" in delivery_root.parts:
        raise ValueError("Formal deliveryRoot cannot be inside 工作过程文件.")


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


def validate_contract(data: dict) -> tuple[float, float]:
    validate_delivery_root(data)
    character_height_cm = float(data["characterHeightCm"])
    if character_height_cm <= 0:
        raise ValueError("characterHeightCm must be positive.")
    estimates = data["calibration"]["projectedHeightEstimatesPx"]
    if data["calibration"].get("aggregationMethod") != "median-after-depth-projection":
        raise ValueError(
            "calibration.aggregationMethod must be median-after-depth-projection."
        )
    derived_tolerance = float(data["calibration"].get("derivedValueToleranceRatio", 0.03))
    values = validate_scale_anchors(estimates, character_height_cm, derived_tolerance)
    median = statistics.median(values)
    spread = (max(values) - min(values)) / median
    allowed = float(data["calibration"].get("maxSpreadRatio", 0.08))
    if spread > allowed:
        raise ValueError(f"Scale estimates disagree: spread={spread:.4f}, allowed={allowed:.4f}")
    band_values = {
        band: [
            value
            for estimate, value in zip(estimates, values)
            if estimate["depthBand"] == band
        ]
        for band in ("actor-local", "cross-depth")
    }
    local_median = statistics.median(band_values["actor-local"])
    cross_depth_median = statistics.median(band_values["cross-depth"])
    cross_depth_delta = abs(local_median - cross_depth_median) / median
    cross_depth_allowed = float(
        data["calibration"].get("maxCrossDepthMedianDeltaRatio", allowed)
    )
    if cross_depth_delta > cross_depth_allowed:
        raise ValueError(
            "Actor-local and cross-depth scale estimates disagree after projection: "
            f"delta={cross_depth_delta:.4f}, allowed={cross_depth_allowed:.4f}"
        )

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
        if abs((head_box[3] - head_box[1]) - seated_head) > 2:
            raise ValueError(
                "seatedPose.headBox must be the anatomical head box and match "
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
        if abs((head_box[3] - head_box[1]) - lying_head) > 2:
            raise ValueError(
                "lyingPose.headBox must be the anatomical head box and match "
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
        validate_contract(contract)
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
    process_root = (NDC_ROOT / "工作过程文件").resolve()
    if process_root not in candidate_root.parents:
        raise ValueError("Candidate handoff must stay under D:\\Codex\\NDC\\工作过程文件.")


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
    args = parser.parse_args()
    if args.command == "validate-contract":
        median, spread = validate_contract(load_contract(args.contract))
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


if __name__ == "__main__":
    main()
