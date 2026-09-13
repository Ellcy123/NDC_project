#!/usr/bin/env python3
"""Create, approve, verify, and receive the one non-final NDC review node."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


NODE_SCHEMA = "ndc-manual-review-node/v1"
APPROVAL_SCHEMA = "ndc-manual-review-node-approval/v1"
WORKSPACE_SCHEMA = "ndc-manual-return-workspace/v1"
RETURN_SCHEMA = "ndc-manual-return/v1"
NODE_STATUSES = {
    "NODE_DELIVERABLE_READY",
    "WAITING_USER_NODE_REVIEW",
    "USER_NODE_APPROVED",
    "USER_NODE_REWORK_REQUIRED",
    "NODE_SUPERSEDED",
}
NODE_DOMAINS = {"character_scene", "prop_scene"}
RETURN_KINDS = {"character_render_return", "prop_finished_package"}
HEX = re.compile(r"^[0-9a-f]{64}$")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
ANATOMY_MODES = {"FULL_IN_FRAME", "SCENE_OCCLUDED", "FRAME_CROPPED_FOREGROUND"}
ANATOMY_PARTS = {
    "head", "neck", "torso", "pelvis", "left_arm", "right_arm",
    "left_hand", "right_hand", "left_leg", "right_leg", "left_foot", "right_foot",
}
PROXY_ABSENCE_KEYS = {
    "stick_or_joint_figure",
    "programmatic_geometry_blocks",
    "flat_color_silhouette",
    "technical_ruler",
    "combined_scene_preview_as_master",
}
PROP_NODE_DELIVERY_SCHEMA = "ndc-prop-node-delivery/v1"
PROP_NODE_DELIVERY_STATUS = "NODE_DELIVERY_READY_PENDING_USER_REVIEW"
CHARACTER_NODE_DELIVERY_SCHEMA = "ndc-character-node-delivery/v1"
CHARACTER_NODE_DELIVERY_STATUS = "NODE_DELIVERY_READY_PENDING_USER_REVIEW"
XY_SUFFIX = re.compile(r"__XY_x(-?[0-9]+)_y(-?[0-9]+)$", re.IGNORECASE)
PROP_SCENE_READY_ROLES = {"pickup_layer", "map_hotspot", "type6_container"}
CHARACTER_LEGACY_MIGRATION_ROLES = {"legacy_render_candidate", "legacy_scene_ready_rgba"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(base: Path, raw: str) -> Path:
    candidate = Path(raw)
    return candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()


def bound(entry: object, base: Path, label: str) -> Path:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
        raise ValueError(f"{label} requires path and sha256")
    if HEX.fullmatch(entry["sha256"].lower()) is None:
        raise ValueError(f"{label} has invalid SHA-256")
    path = resolve(base, entry["path"])
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    if sha256(path) != entry["sha256"].lower():
        raise ValueError(f"{label} does not match frozen bytes")
    return path


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value


def scene_label(value: object, scene_id: str, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must identify display_name, location, and time")
    display_name = text(value.get("display_name"), f"{label}.display_name").strip()
    location = text(value.get("location"), f"{label}.location").strip()
    time_label = text(value.get("time"), f"{label}.time").strip()
    if display_name.casefold() == scene_id.casefold():
        raise ValueError(f"{label}.display_name cannot be only the scene code")
    if location.casefold() not in display_name.casefold() or time_label.casefold() not in display_name.casefold():
        raise ValueError(f"{label}.display_name must include both location and time")
    return {"display_name": display_name, "location": location, "time": time_label}


def timestamp(value: object, label: str) -> None:
    try:
        datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be ISO-8601") from exc


def bindings(value: object, base: Path, label: str, *, minimum: int = 1) -> list[Path]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{label} requires at least {minimum} bound file(s)")
    return [bound(entry, base, f"{label}[{index}]") for index, entry in enumerate(value)]


def image_file(entry: object, base: Path, label: str, *, rgba: bool = False, dimensional_proxy_check: bool = False) -> Path:
    path = bound(entry, base, label)
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"{label} must bind an actual viewable image, not JSON metadata")
    try:
        with Image.open(path) as image:
            image.load()
            if image.width < 128 or image.height < 128:
                raise ValueError(f"{label} is too small to be the final production whitebox")
            if rgba and image.mode != "RGBA":
                raise ValueError(f"{label} must be a real RGBA transparent actor master")
            if rgba:
                rgba_image = image
                alpha = rgba_image.getchannel("A")
                if alpha.getbbox() is None or alpha.getextrema() == (255, 255):
                    raise ValueError(f"{label} must contain both actor pixels and transparent canvas")
            if dimensional_proxy_check:
                rgba_image = image.convert("RGBA")
                colors = set()
                luminance = []
                pixels = rgba_image.get_flattened_data() if hasattr(rgba_image, "get_flattened_data") else rgba_image.getdata()
                for red, green, blue, alpha_value in pixels:
                    if alpha_value >= 192:
                        colors.add((red // 16, green // 16, blue // 16))
                        luminance.append((red * 299 + green * 587 + blue * 114) // 1000)
                        if len(colors) >= 16 and luminance and max(luminance) - min(luminance) >= 32:
                            break
                if len(colors) < 16 or not luminance or max(luminance) - min(luminance) < 32:
                    raise ValueError(f"{label} looks like a flat block/stick proxy, not a shaded 3D anatomical mannequin")
    except (OSError, ValueError) as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"{label} cannot be opened as an image: {exc}") from exc
    return path


def character_scope_work(scope_path: Path) -> set[tuple[str, str]]:
    scope = load(scope_path)
    cases = scope.get("scope", {}).get("cases") if isinstance(scope.get("scope"), dict) else scope.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("character node scope must contain complete cases")
    work: set[tuple[str, str]] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("character node scope case must be an object")
        snapshots = case.get("snapshots")
        if not isinstance(snapshots, list) or not snapshots:
            raise ValueError("character node scope case requires snapshots")
        for snapshot in snapshots:
            mapping = snapshot.get("actor_pose_ids") if isinstance(snapshot, dict) else None
            if not isinstance(mapping, dict) or not mapping:
                raise ValueError("every character node snapshot requires actor_pose_ids")
            for actor, pose in mapping.items():
                work.add((text(actor, "actor_id"), text(pose, "pose_id")))
    return work


def validate_character_whiteboxes(delivery: dict, base: Path, scope_path: Path) -> dict[tuple[str, str], dict]:
    entries = delivery.get("production_whiteboxes")
    if not isinstance(entries, list) or not entries:
        raise ValueError("deliverables.production_whiteboxes must contain every final production whitebox")
    joint = image_file(delivery.get("joint_whitebox_preview"), base, "deliverables.joint_whitebox_preview")
    ui = image_file(delivery.get("actual_ui_clearance_preview"), base, "deliverables.actual_ui_clearance_preview")
    if sha256(joint) == sha256(ui):
        raise ValueError("joint whitebox and actual UI preview must be separate reviewed outputs")
    discovery_paths = bindings(delivery.get("discovery_receipts"), base, "deliverables.discovery_receipts")
    discovery_hashes = {sha256(path) for path in discovery_paths}
    supplied: dict[tuple[str, str], dict] = {}
    protected_preview_hashes = {sha256(joint), sha256(ui)}
    for index, entry in enumerate(entries):
        label = f"deliverables.production_whiteboxes[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        actor = text(entry.get("actor_id"), f"{label}.actor_id")
        pose = text(entry.get("pose_id"), f"{label}.pose_id")
        key = (actor, pose)
        if key in supplied:
            raise ValueError(f"duplicate production whitebox for actor/pose {key}")
        mode = entry.get("anatomy_mode")
        if mode not in ANATOMY_MODES:
            raise ValueError(f"{label}.anatomy_mode is invalid")
        if entry.get("whitebox_kind") != "3d-anatomical-mannequin-exact-pose":
            raise ValueError(f"{label} rejects stick figures, joint skeletons, block geometry, rulers, and filename-only claims")
        absence = entry.get("prohibited_proxy_types_absent")
        if not isinstance(absence, dict) or set(absence) != PROXY_ABSENCE_KEYS or any(value is not True for value in absence.values()):
            raise ValueError(f"{label}.prohibited_proxy_types_absent must explicitly reject every proxy type")
        master = image_file(entry.get("complete_anatomy_master"), base, f"{label}.complete_anatomy_master", rgba=True, dimensional_proxy_check=True)
        final_submission = image_file(entry.get("final_submission_whitebox"), base, f"{label}.final_submission_whitebox")
        master_hash = sha256(master)
        final_hash = sha256(final_submission)
        if master_hash == final_hash:
            raise ValueError(f"{label} must separate the transparent anatomy master from the exact scene-context submission image")
        if master_hash in protected_preview_hashes or final_hash in protected_preview_hashes:
            raise ValueError(f"{label} cannot use a joint/UI preview as the production whitebox or complete master")
        if entry.get("final_submission_authority") is not True:
            raise ValueError(f"{label}.final_submission_authority must be true")
        coverage = entry.get("anatomy_coverage")
        if mode in {"FULL_IN_FRAME", "SCENE_OCCLUDED"}:
            if not isinstance(coverage, dict) or set(coverage) != ANATOMY_PARTS or any(value is not True for value in coverage.values()):
                raise ValueError(f"{label}.anatomy_coverage must explicitly pass head-to-foot anatomy")
        else:
            if entry.get("visible_anatomy_complete") is not True or entry.get("natural_frame_exit") is not True:
                raise ValueError(f"{label} cropped foreground requires complete visible anatomy and a natural frame exit")
            bindings(entry.get("off_frame_scale_support_evidence"), base, f"{label}.off_frame_scale_support_evidence")
        technical = bound(entry.get("technical_review"), base, f"{label}.technical_review")
        visual = bound(entry.get("visual_review"), base, f"{label}.visual_review")
        discovery = bound(entry.get("discovery_receipt"), base, f"{label}.discovery_receipt")
        if sha256(discovery) not in discovery_hashes:
            raise ValueError(f"{label}.discovery_receipt is not in the node discovery set")
        supplied[key] = {
            "actor_id": actor,
            "pose_id": pose,
            "anatomy_mode": mode,
            "complete_anatomy_master": {"path": master, "sha256": master_hash},
            "final_submission_whitebox": {"path": final_submission, "sha256": final_hash},
            "technical_review": {"path": technical, "sha256": sha256(technical)},
            "visual_review": {"path": visual, "sha256": sha256(visual)},
        }
    required = character_scope_work(scope_path)
    if set(supplied) != required:
        raise ValueError(f"production whitebox coverage differs from frozen scope; missing={sorted(required-set(supplied))}, extra={sorted(set(supplied)-required)}")
    return supplied


def validate_character_node_delivery(
    manifest_path: Path,
    node: dict,
    scope_path: Path,
    supplied: dict[tuple[str, str], dict],
    node_base: Path,
) -> None:
    manifest = load(manifest_path)
    if manifest.get("schema") != CHARACTER_NODE_DELIVERY_SCHEMA or manifest.get("status") != CHARACTER_NODE_DELIVERY_STATUS:
        raise ValueError("character node delivery manifest is not ready for user review")
    for key in ("unit", "node_id", "scene_id", "revision"):
        if str(manifest.get(key)) != str(node.get(key)):
            raise ValueError(f"character node delivery {key} differs from the manual review node")
    if manifest.get("scene_label") != node.get("scene_label"):
        raise ValueError("character node delivery scene_label differs from the manual review node")
    manifest_migration = manifest.get("legacy_migration_backfill", {"enabled": False, "reason": None, "asset_count": 0})
    node_migration = node.get("legacy_migration_backfill", {"enabled": False, "reason": None, "asset_count": 0})
    if manifest_migration != node_migration:
        raise ValueError("character node delivery legacy_migration_backfill differs from the manual review node")
    if manifest.get("formal_pass") is not False:
        raise ValueError("character node delivery must remain explicitly non-formal")
    package_value = manifest.get("package_root")
    if not isinstance(package_value, str) or not package_value.strip():
        raise ValueError("character node delivery package_root is required")
    package_root = Path(package_value).resolve()
    expected_manifest = package_root / "_节点资料" / "_节点" / str(node["node_id"]) / "节点交付清单.json"
    if manifest_path != expected_manifest:
        raise ValueError("character node delivery manifest is outside the isolated _节点资料 folder")
    if (
        package_root.name != str(node["scene_id"])
        or package_root.parent.name != "节点交付"
        or package_root.parent.parent.name != str(node["unit"])
        or package_root.parent.parent.parent.name != "角色融入场景"
    ):
        raise ValueError("character node delivery must be under 角色融入场景/<Unit>/节点交付/<scene>")
    scope_source = manifest.get("scope_source")
    if not isinstance(scope_source, dict) or scope_source.get("sha256") != sha256(scope_path):
        raise ValueError("character node delivery does not bind the manual node's exact scope bytes")
    coverage = manifest.get("coverage")
    if coverage != {
        "actor_poses_required": len(supplied),
        "actor_poses_packaged": len(supplied),
        "missing": [],
        "extra": [],
    }:
        raise ValueError("character node delivery actor/pose coverage is incomplete")
    support = manifest.get("support_files")
    if not isinstance(support, list):
        raise ValueError("character node delivery lacks support files")
    support_kinds = {entry.get("kind") for entry in support if isinstance(entry, dict)}
    if not {"human_preview_index", "human_asset_list", "non_formal_warning"}.issubset(support_kinds):
        raise ValueError("character node delivery needs an HTML preview, readable list, and warning")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("character node delivery artifacts are required")
    expected_hashes: dict[tuple[str, str, str], str] = {}
    for (actor, pose), value in supplied.items():
        expected_hashes[(actor, pose, "complete_anatomy_master")] = value["complete_anatomy_master"]["sha256"]
        expected_hashes[(actor, pose, "final_submission_whitebox")] = value["final_submission_whitebox"]["sha256"]
    delivery = node["deliverables"]
    for role in ("joint_whitebox_preview", "actual_ui_clearance_preview"):
        expected_hashes[("scene", str(node["revision"]), role)] = sha256(bound(delivery[role], node_base, f"deliverables.{role}"))
    found: set[tuple[str, str, str]] = set()
    actual_images = 0
    for index, artifact in enumerate(artifacts):
        label = f"character node delivery artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise ValueError(f"{label} must be an object")
        role = text(artifact.get("role"), f"{label}.role")
        key = (text(artifact.get("actor_id"), f"{label}.actor_id"), text(artifact.get("pose_id"), f"{label}.pose_id"), role)
        package_file = artifact.get("package_file")
        if not isinstance(package_file, dict):
            raise ValueError(f"{label}.package_file is required")
        relative = text(package_file.get("relative_path"), f"{label}.package_file.relative_path")
        if len(Path(relative).parts) != 1:
            raise ValueError(f"{label} must be flat in the scene root")
        checked = bound({"path": str(package_root / relative), "sha256": package_file.get("sha256")}, package_root, f"{label}.package_file")
        if checked.parent != package_root:
            raise ValueError(f"{label} is not a flat-root asset")
        if role in {"complete_anatomy_master", "final_submission_whitebox", "joint_whitebox_preview", "actual_ui_clearance_preview"}:
            if key not in expected_hashes or package_file.get("sha256") != expected_hashes[key]:
                raise ValueError(f"{label} is not the exact node-approved production whitebox bytes")
            found.add(key)
        elif role not in {"editable_source", *CHARACTER_LEGACY_MIGRATION_ROLES}:
            raise ValueError(f"{label}.role is invalid")
        coordinate_match = XY_SUFFIX.search(checked.stem)
        if role == "legacy_scene_ready_rgba":
            if checked.suffix.lower() != ".png" or coordinate_match is None:
                raise ValueError(f"{label} scene-ready migration PNG must end with __XY_x<int>_y<int>")
            expected_xy = {"x": int(coordinate_match.group(1)), "y": int(coordinate_match.group(2))}
            if artifact.get("placement_xy") != expected_xy:
                raise ValueError(f"{label}.placement_xy must match its XY filename suffix")
            image_file(
                {"path": str(checked), "sha256": sha256(checked)},
                package_root,
                f"{label}.package_file",
                rgba=True,
            )
        elif coordinate_match is not None:
            raise ValueError(f"{label} may claim an XY filename suffix only for a scene-ready migration RGBA")
        candidate = artifact.get("candidate_record")
        if not isinstance(candidate, dict):
            raise ValueError(f"{label}.candidate_record is required")
        candidate_relative = text(candidate.get("relative_path"), f"{label}.candidate_record.relative_path")
        expected_candidate_root = package_root / "_节点资料" / checked.stem
        candidate_path = (package_root / candidate_relative).resolve()
        try:
            candidate_path.relative_to(expected_candidate_root)
        except ValueError as exc:
            raise ValueError(f"{label}.candidate_record is not grouped by the same delivery filename") from exc
        bound({"path": str(candidate_path), "sha256": candidate.get("sha256")}, package_root, f"{label}.candidate_record")
        if checked.suffix.lower() in IMAGE_SUFFIXES:
            actual_images += 1
        elif checked.suffix.lower() not in {".psd", ".psb"}:
            raise ValueError(f"{label} must be an actual viewable whitebox or editable PSD/PSB")
    if found != set(expected_hashes):
        raise ValueError(f"character node delivery exact asset coverage differs; missing={sorted(set(expected_hashes)-found)}")
    if actual_images < len(expected_hashes):
        raise ValueError("character node delivery is JSON/source-only and lacks every required whitebox image")
    root_files = {path.name for path in package_root.iterdir() if path.is_file()}
    if root_files != {artifact["package_file"]["relative_path"] for artifact in artifacts}:
        raise ValueError("character scene root must contain whitebox/source assets only; JSON belongs under _节点资料")
    root_dirs = {path.name for path in package_root.iterdir() if path.is_dir()}
    if root_dirs != {"_节点资料"}:
        raise ValueError("character scene root may contain only _节点资料; actor/type/revision asset folders are forbidden")


def validate_prop_node_delivery(manifest_path: Path, node: dict, scope_path: Path) -> None:
    manifest = load(manifest_path)
    if manifest.get("schema") != PROP_NODE_DELIVERY_SCHEMA or manifest.get("status") != PROP_NODE_DELIVERY_STATUS:
        raise ValueError("prop node delivery manifest is not ready for user review")
    for key in ("node_id", "scene_id", "revision"):
        if str(manifest.get(key)) != str(node.get(key)):
            raise ValueError(f"prop node delivery {key} differs from the manual review node")
    if manifest.get("scene_label") != node.get("scene_label"):
        raise ValueError("prop node delivery scene_label differs from the manual review node")
    if manifest.get("formal_pass") is not False:
        raise ValueError("prop node delivery must remain explicitly non-formal")
    package_root_value = manifest.get("package_root")
    if not isinstance(package_root_value, str) or not package_root_value.strip():
        raise ValueError("prop node delivery package_root is required")
    package_root = Path(package_root_value).resolve()
    expected_manifest = package_root / "_节点资料" / "_节点" / str(node["node_id"]) / "节点交付清单.json"
    if manifest_path != expected_manifest or tuple(package_root.parts[-2:]) != ("节点交付", str(node["scene_id"])):
        raise ValueError("prop node delivery manifest is outside the flat scene root's isolated _节点资料 folder")
    scope_source = manifest.get("scope_source")
    if not isinstance(scope_source, dict) or scope_source.get("sha256") != sha256(scope_path):
        raise ValueError("prop node delivery does not bind the manual node's exact scope bytes")
    coverage = manifest.get("coverage")
    if not isinstance(coverage, dict) or not isinstance(coverage.get("required"), int) or coverage.get("required", 0) < 1:
        raise ValueError("prop node delivery has no required actual assets")
    if coverage.get("packaged") != coverage.get("required") or coverage.get("missing") != [] or coverage.get("extra") != []:
        raise ValueError("prop node delivery is incomplete")
    support = manifest.get("support_files")
    if not isinstance(support, list):
        raise ValueError("prop node delivery lacks human-readable support files")
    support_kinds = {entry.get("kind") for entry in support if isinstance(entry, dict)}
    if not {"human_preview_index", "human_asset_list", "non_formal_warning"}.issubset(support_kinds):
        raise ValueError("prop node delivery must include a human preview, human asset list, and warning")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != coverage["required"]:
        raise ValueError("prop node delivery artifact list is incomplete")
    actual_images = 0
    seen = set()
    for index, artifact in enumerate(artifacts):
        label = f"prop node delivery artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise ValueError(f"{label} must be an object")
        artifact_id = text(artifact.get("artifact_id"), f"{label}.artifact_id")
        if artifact_id in seen:
            raise ValueError(f"duplicate prop node artifact: {artifact_id}")
        seen.add(artifact_id)
        package_file = artifact.get("package_file")
        if not isinstance(package_file, dict):
            raise ValueError(f"{label}.package_file is required")
        relative = text(package_file.get("relative_path"), f"{label}.package_file.relative_path")
        if len(Path(relative).parts) != 1:
            raise ValueError(f"{label} must be flat in the scene root")
        path = resolve(package_root, relative)
        try:
            path.relative_to(package_root)
        except ValueError as exc:
            raise ValueError(f"{label} escapes the node package") from exc
        checked = bound({"path": str(path), "sha256": package_file.get("sha256")}, package_root, f"{label}.package_file")
        if checked.parent != package_root:
            raise ValueError(f"{label} is not a flat-root delivery asset")
        role = text(artifact.get("role"), f"{label}.role")
        coordinate_match = XY_SUFFIX.search(checked.stem)
        if role in PROP_SCENE_READY_ROLES:
            if checked.suffix.lower() != ".png" or coordinate_match is None:
                raise ValueError(f"{label} scene-ready PNG must end with __XY_x<int>_y<int>")
            expected_xy = {"x": int(coordinate_match.group(1)), "y": int(coordinate_match.group(2))}
            if artifact.get("placement_xy") != expected_xy:
                raise ValueError(f"{label}.placement_xy must match its XY filename suffix")
        elif coordinate_match is not None:
            raise ValueError(f"{label} may claim an XY filename suffix only for a scene-ready placement role")
        candidate_record = artifact.get("candidate_record")
        if not isinstance(candidate_record, dict):
            raise ValueError(f"{label}.candidate_record is required")
        candidate_relative = text(candidate_record.get("relative_path"), f"{label}.candidate_record.relative_path")
        expected_candidate_root = package_root / "_节点资料" / checked.stem
        candidate_path = resolve(package_root, candidate_relative)
        try:
            candidate_path.relative_to(expected_candidate_root)
        except ValueError as exc:
            raise ValueError(f"{label}.candidate_record is not grouped by the delivery asset's same name") from exc
        bound({"path": str(candidate_path), "sha256": candidate_record.get("sha256")}, package_root, f"{label}.candidate_record")
        if checked.suffix.lower() in IMAGE_SUFFIXES:
            actual_images += 1
        elif checked.suffix.lower() != ".txt":
            raise ValueError(f"{label} must be an actual viewable image or directly usable XY/TXT file, not JSON-only metadata")
    if actual_images < 1:
        raise ValueError("prop node delivery contains JSON/metadata only and no directly viewable image assets")
    root_files = {path.name for path in package_root.iterdir() if path.is_file()}
    if root_files != {artifact["package_file"]["relative_path"] for artifact in artifacts}:
        raise ValueError("prop scene root must contain delivery assets only; JSON, guides, and candidates belong under _节点资料")
    root_dirs = {path.name for path in package_root.iterdir() if path.is_dir()}
    if root_dirs != {"_节点资料"}:
        raise ValueError("prop scene root may contain only _节点资料; per-type and per-artifact delivery folders are forbidden")


def validate_node(path: Path) -> dict:
    path = path.resolve()
    node = load(path)
    if node.get("schema") != NODE_SCHEMA:
        raise ValueError(f"schema must be {NODE_SCHEMA}")
    if node.get("status") not in NODE_STATUSES:
        raise ValueError("node status is invalid")
    if node.get("status") not in {"NODE_DELIVERABLE_READY", "WAITING_USER_NODE_REVIEW"}:
        raise ValueError("only a ready, unapproved node can be offered for review")
    text(node.get("node_id"), "node_id")
    domain = node.get("domain")
    if domain not in NODE_DOMAINS:
        raise ValueError("domain must be character_scene or prop_scene")
    scene_id = text(node.get("scene_id"), "scene_id")
    node["scene_label"] = scene_label(node.get("scene_label"), scene_id, "scene_label")
    branch_mode = node.get("manual_return_branch_mode", "USER_HOLD")
    if branch_mode not in {"PARALLEL_NONBLOCKING", "USER_HOLD"}:
        raise ValueError("manual_return_branch_mode must be PARALLEL_NONBLOCKING or USER_HOLD")
    revision = node.get("revision")
    if not isinstance(revision, (str, int)) or isinstance(revision, bool) or str(revision).strip() == "":
        raise ValueError("revision is required")
    timestamp(node.get("created_at"), "created_at")
    scope_path = bound(node.get("scope"), path.parent, "scope")
    delivery = node.get("deliverables")
    if not isinstance(delivery, dict):
        raise ValueError("deliverables is required")
    bound(node.get("source_index"), path.parent, "source_index")
    bound(node.get("handoff_document"), path.parent, "handoff_document")
    bound(node.get("naming_table"), path.parent, "naming_table")
    bound(node.get("web_prompt"), path.parent, "web_prompt")
    if domain == "character_scene":
        unit = text(node.get("unit"), "unit")
        if re.fullmatch(r"Unit[0-9A-Za-z_-]+", unit) is None:
            raise ValueError("unit must look like Unit2")
        supplied = validate_character_whiteboxes(delivery, path.parent, scope_path)
        manifest_path = bound(delivery.get("node_delivery_manifest"), path.parent, "deliverables.node_delivery_manifest")
        validate_character_node_delivery(manifest_path, node, scope_path, supplied, path.parent)
        required_focus = {"proportion", "narrative_pose", "landing_plausibility", "ui_clearance"}
        focus = node.get("user_review_focus")
        if not isinstance(focus, list) or set(focus) != required_focus:
            raise ValueError("character node review focus must be proportion, narrative_pose, landing_plausibility, ui_clearance only")
    else:
        bindings(delivery.get("discovery_receipts"), path.parent, "deliverables.discovery_receipts")
        manifest_path = bound(delivery.get("node_delivery_manifest"), path.parent, "deliverables.node_delivery_manifest")
        validate_prop_node_delivery(manifest_path, node, scope_path)
        accepted_focus = (
            {"node_required_assets", "cross_asset_identity", "stage_relationships", "scene_grouping"},
            {"complete_assets", "cross_asset_identity", "runtime_relationships", "scene_grouping"},
        )
        focus = node.get("user_review_focus")
        if not isinstance(focus, list) or set(focus) not in accepted_focus:
            raise ValueError(
                "prop node review focus must cover node_required_assets, cross_asset_identity, "
                "stage_relationships, and scene_grouping"
            )
    workspace = node.get("manual_return_workspace")
    bound(workspace, path.parent, "manual_return_workspace")
    return node


def approval_for(node_path: Path, approved_at: str, user_statement: str) -> dict:
    node = validate_node(node_path)
    timestamp(approved_at, "approved_at")
    return {
        "schema": APPROVAL_SCHEMA,
        "status": "USER_NODE_APPROVED",
        "node_id": node["node_id"],
        "domain": node["domain"],
        "scene_id": node["scene_id"],
        "revision": node["revision"],
        "approved_at": approved_at,
        "user_statement": text(user_statement, "user_statement"),
        "node_manifest": {"path": str(node_path.resolve()), "sha256": sha256(node_path.resolve())},
        "authority": "The bound node manifest bytes are the only upstream authority for this scene/revision. Downstream may verify fidelity only; it must not rediscover, replace, regenerate, or re-evaluate node inputs.",
    }


def verify_approval(node_path: Path, approval_path: Path) -> dict:
    validate_node(node_path)
    approval = load(approval_path.resolve())
    if approval.get("schema") != APPROVAL_SCHEMA or approval.get("status") != "USER_NODE_APPROVED":
        raise ValueError("approval is not USER_NODE_APPROVED")
    node_ref = approval.get("node_manifest")
    if not isinstance(node_ref, dict):
        raise ValueError("approval lacks node_manifest binding")
    actual_path = Path(node_ref.get("path", "")).resolve()
    if actual_path != node_path.resolve() or sha256(node_path.resolve()) != node_ref.get("sha256"):
        raise ValueError("approval does not bind the exact node manifest bytes")
    node = load(node_path.resolve())
    for key in ("node_id", "domain", "scene_id", "revision"):
        if str(approval.get(key)) != str(node.get(key)):
            raise ValueError(f"approval {key} differs from its frozen node")
    return approval


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def receive_return(workspace_manifest_path: Path, approval_path: Path, workspace: Path, output: Path, returned_at: str, user_statement: str) -> dict:
    workspace_manifest_path = workspace_manifest_path.resolve()
    contract = load(workspace_manifest_path)
    if contract.get("schema") != WORKSPACE_SCHEMA:
        raise ValueError(f"workspace schema must be {WORKSPACE_SCHEMA}")
    kind = contract.get("return_kind")
    if kind not in RETURN_KINDS:
        raise ValueError("workspace return_kind is invalid")
    timestamp(returned_at, "returned_at")
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise ValueError("workspace must be an existing directory")
    approval_path = approval_path.resolve()
    if not approval_path.is_file():
        raise ValueError("approval must be an existing file")
    approval = load(approval_path)
    node_ref = approval.get("node_manifest")
    node_path = bound(node_ref, approval_path.parent, "node_approval.node_manifest")
    verify_approval(node_path, approval_path)
    node = load(node_path)
    declared_workspace = bound(node.get("manual_return_workspace"), node_path.parent, "node.manual_return_workspace")
    if declared_workspace != workspace_manifest_path:
        raise ValueError("workspace manifest is not the exact pre-approved manual return workspace")
    for key in ("node_id", "domain", "scene_id", "revision"):
        if str(contract.get(key, "")) != str(node.get(key, "")):
            raise ValueError(f"workspace {key} does not match the approved node")
    slots = contract.get("slots")
    if not isinstance(slots, list) or not slots:
        raise ValueError("workspace needs explicit slot contracts")
    seen: set[str] = set()
    snapshots, gaps = [], []
    for index, slot in enumerate(slots):
        label = f"slots[{index}]"
        if not isinstance(slot, dict):
            raise ValueError(f"{label} must be an object")
        slot_id = text(slot.get("slot_id"), f"{label}.slot_id")
        if slot_id in seen:
            raise ValueError("slot_id must be unique")
        seen.add(slot_id)
        relative = text(slot.get("relative_path"), f"{label}.relative_path")
        candidate = (workspace / relative).resolve()
        if not inside(workspace, candidate):
            raise ValueError(f"{label}.relative_path escapes the workspace")
        record = {"slot_id": slot_id, "role": text(slot.get("role"), f"{label}.role"), "relative_path": relative}
        if candidate.is_file():
            record.update({"status": "PRESENT", "path": str(candidate), "sha256": sha256(candidate), "bytes": candidate.stat().st_size})
        else:
            record.update({"status": "INPUT_GAP", "reason": "declared slot is absent from the current workspace"})
            gaps.append(record.copy())
        snapshots.append(record)
    all_files = []
    for path in sorted(candidate for candidate in workspace.rglob("*") if candidate.is_file()):
        all_files.append({"relative_path": str(path.relative_to(workspace)), "sha256": sha256(path), "bytes": path.stat().st_size})
    output = output.resolve()
    if output.exists():
        raise ValueError("return output already exists; preserve the prior accepted revision")
    if inside(workspace, output):
        raise ValueError("return output must stay outside the reviewed workspace snapshot")
    result = {
        "schema": RETURN_SCHEMA,
        "status": "USER_RETURN_ACCEPTED_FOR_PACKAGING",
        "return_kind": kind,
        "returned_at": returned_at,
        "user_statement": text(user_statement, "user_statement"),
        "workspace": str(workspace),
        "workspace_manifest": {"path": str(workspace_manifest_path), "sha256": sha256(workspace_manifest_path)},
        "node_approval": {"path": str(approval_path), "sha256": sha256(approval_path)},
        "slots": snapshots,
        "input_gaps": gaps,
        "workspace_current_files": all_files,
        "downstream_rule": "Treat this as a manual-return branch revision. Preserve the frozen production mainline, revalidate only affected dependencies, continue independent mainline work, and never use the return to shrink the original scope.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--node-manifest", required=True, type=Path)
    approve = sub.add_parser("approve")
    approve.add_argument("--node-manifest", required=True, type=Path)
    approve.add_argument("--out", required=True, type=Path)
    approve.add_argument("--approved-at", required=True)
    approve.add_argument("--user-statement", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--node-manifest", required=True, type=Path)
    verify.add_argument("--approval", required=True, type=Path)
    returned = sub.add_parser("return")
    returned.add_argument("--workspace-manifest", required=True, type=Path)
    returned.add_argument("--approval", required=True, type=Path)
    returned.add_argument("--workspace", required=True, type=Path)
    returned.add_argument("--out", required=True, type=Path)
    returned.add_argument("--returned-at", required=True)
    returned.add_argument("--user-statement", required=True)
    args = parser.parse_args()
    try:
        if args.command == "create":
            node = validate_node(args.node_manifest)
            result = {"schema": NODE_SCHEMA, "status": "NODE_DELIVERABLE_READY", "node_id": node["node_id"], "node_manifest_sha256": sha256(args.node_manifest.resolve())}
        elif args.command == "approve":
            if args.out.exists():
                raise ValueError("approval output already exists; never overwrite approval history")
            result = approval_for(args.node_manifest, args.approved_at, args.user_statement)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif args.command == "verify":
            result = verify_approval(args.node_manifest, args.approval)
            result = {"schema": APPROVAL_SCHEMA, "status": "PASS", "node_id": result["node_id"]}
        else:
            result = receive_return(args.workspace_manifest, args.approval, args.workspace, args.out, args.returned_at, args.user_statement)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
