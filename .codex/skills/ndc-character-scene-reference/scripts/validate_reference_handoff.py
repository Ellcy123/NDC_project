#!/usr/bin/env python3
"""Validate a complete, current whole-scene reference handoff before publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "ndc-character-scene-reference-handoff/v1"
GATE_SCHEMA = "ndc-character-scene-ready-revision-gate/v1"
ROLES = ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"]
MODES = {"FULL_IN_FRAME", "SCENE_OCCLUDED", "FRAME_CROPPED_FOREGROUND"}
SHARED_PIPELINE = Path(__file__).resolve().parents[2] / "ndc-art-stage-pipeline" / "scripts"
if str(SHARED_PIPELINE) not in sys.path:
    sys.path.insert(0, str(SHARED_PIPELINE))
from asset_discovery import bound as discovery_bound, validate_receipt  # noqa: E402
from manual_review_node import validate_node, verify_approval  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def bound(entry: object, base: Path, label: str) -> Path:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
        raise ValueError(f"{label} requires path and sha256")
    path = Path(entry["path"])
    if not path.is_absolute():
        path = base / path
    path = path.resolve()
    digest = entry.get("sha256")
    if not path.is_file() or not isinstance(digest, str) or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None:
        raise ValueError(f"{label} is missing or has an invalid SHA-256")
    if sha256(path) != digest.lower():
        raise ValueError(f"{label} no longer matches its bound bytes")
    return path


def scope_work(scope: dict) -> set[tuple[str, str]]:
    work: set[tuple[str, str]] = set()
    cases = scope.get("scope", {}).get("cases") if isinstance(scope.get("scope"), dict) else scope.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("scope must contain complete cases")
    for case in cases:
        for snapshot in case.get("snapshots", []):
            mapping = snapshot.get("actor_pose_ids", {})
            if not isinstance(mapping, dict) or not mapping:
                raise ValueError("every snapshot needs actor_pose_ids")
            work.update((actor, pose) for actor, pose in mapping.items())
    return work


def validate(path: Path) -> dict:
    path = path.resolve()
    data = load(path)
    if data.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    scene_id = data.get("scene_id")
    revision = data.get("revision")
    if not isinstance(scene_id, str) or not scene_id:
        raise ValueError("scene_id is required")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ValueError("revision must be a positive integer")
    source_revision = data.get("source_revision")
    if not isinstance(source_revision, dict) or source_revision.get("status") != "CURRENT" or source_revision.get("superseded") is not False:
        raise ValueError("source revision must be CURRENT and not superseded")
    scope_path = bound(data.get("scope"), path.parent, "scope")
    node_path = bound(data.get("manual_review_node"), path.parent, "manual_review_node")
    node = validate_node(node_path)
    branch_mode = data.get("manual_review_branch_mode", "USER_HOLD")
    if branch_mode not in {"PARALLEL_NONBLOCKING", "USER_HOLD"}:
        raise ValueError("manual_review_branch_mode must be PARALLEL_NONBLOCKING or USER_HOLD")
    approval_path = None
    approval_ref = data.get("manual_review_approval")
    if branch_mode == "USER_HOLD" or approval_ref is not None:
        approval_path = bound(approval_ref, path.parent, "manual_review_approval")
        approval = verify_approval(node_path, approval_path)
        if str(approval.get("scene_id")) != str(scene_id) or str(approval.get("revision")) != str(revision):
            raise ValueError("manual review approval is for another scene/revision")
    required = scope_work(load(scope_path))
    scope_sha = sha256(scope_path)
    node_whiteboxes = node.get("deliverables", {}).get("production_whiteboxes")
    if not isinstance(node_whiteboxes, list) or not node_whiteboxes:
        raise ValueError("approved node lacks final production_whiteboxes")
    node_authority = {}
    for entry in node_whiteboxes:
        if not isinstance(entry, dict):
            raise ValueError("approved node production_whiteboxes entry is invalid")
        key = (str(entry.get("actor_id", "")), str(entry.get("pose_id", "")))
        if not all(key) or key in node_authority:
            raise ValueError("approved node production whitebox actor/pose must be unique")
        node_authority[key] = entry
    units = data.get("generation_units")
    if not isinstance(units, list) or not units:
        raise ValueError("generation_units must be a non-empty list")
    supplied: set[tuple[str, str]] = set()
    unit_ids: set[str] = set()
    normalized = []
    for index, unit in enumerate(units):
        label = f"generation_units[{index}]"
        if not isinstance(unit, dict):
            raise ValueError(f"{label} must be an object")
        unit_id = unit.get("generation_unit_id")
        actor = unit.get("actor_id")
        poses = unit.get("pose_ids")
        mode = unit.get("anatomy_mode")
        if not isinstance(unit_id, str) or not unit_id or unit_id in unit_ids:
            raise ValueError(f"{label}.generation_unit_id must be unique")
        if not isinstance(actor, str) or not actor or not isinstance(poses, list) or len(poses) != 1:
            raise ValueError(f"{label} must bind exactly one actor/pose to one final production whitebox")
        if not isinstance(poses[0], str) or not poses[0]:
            raise ValueError(f"{label} needs actor_id and pose_ids")
        if mode not in MODES:
            raise ValueError(f"{label}.anatomy_mode is invalid")
        unit_ids.add(unit_id)
        unit_work = {(actor, pose) for pose in poses}
        if supplied & unit_work:
            raise ValueError("actor/pose work appears in more than one unit")
        supplied |= unit_work
        refs = unit.get("references")
        if not isinstance(refs, list) or [item.get("role") for item in refs if isinstance(item, dict)] != ROLES:
            raise ValueError(f"{label} must bind three independent references in exact order")
        ref_paths = [bound(item, path.parent, f"{label}.references") for item in refs]
        ref_hashes = [sha256(item) for item in ref_paths]
        authority = node_authority.get((actor, poses[0]))
        if authority is None:
            raise ValueError(f"{label} has no matching whitebox authority in the approved node")
        approved_submission = bound(authority.get("final_submission_whitebox"), node_path.parent, f"{label}.node.final_submission_whitebox")
        if ref_paths[0] != approved_submission or ref_hashes[0] != sha256(approved_submission):
            raise ValueError(f"{label} Image 1 is not the exact final_submission_whitebox approved at the node")
        if authority.get("anatomy_mode") != mode:
            raise ValueError(f"{label}.anatomy_mode differs from the approved node")
        discovery = unit.get("discovery")
        if not isinstance(discovery, dict) or str(discovery.get("scope_revision_sha256", "")).lower() != scope_sha:
            raise ValueError(f"{label} requires a discovery receipt bound to the current frozen scope")
        try:
            receipt_path = discovery_bound(discovery.get("receipt"), path.parent, f"{label}.discovery.receipt")
            discovery_failures = validate_receipt(receipt_path, expected_scope={
                "domain": "character_scene", "scene_id": scene_id, "revision": revision,
                "actor_id": actor, "pose_or_state": "|".join(poses), "artifact_role": "whitebox",
                "scope_revision_sha256": scope_sha,
            }, action="GENERATE")
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{label} discovery receipt is invalid: {exc}") from exc
        if discovery_failures:
            raise ValueError(f"{label} discovery receipt blocks new whitebox use: {'; '.join(discovery_failures)}")
        evidence = unit.get("coverage_evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"{label}.coverage_evidence is required")
        evidence_hashes = [sha256(bound(item, path.parent, f"{label}.coverage_evidence")) for item in evidence]
        complete_master = bound(unit.get("complete_master"), path.parent, f"{label}.complete_master")
        approved_master = bound(authority.get("complete_anatomy_master"), node_path.parent, f"{label}.node.complete_anatomy_master")
        if complete_master != approved_master or sha256(complete_master) != sha256(approved_master):
            raise ValueError(f"{label}.complete_master is not the exact approved production whitebox master")
        if mode == "FRAME_CROPPED_FOREGROUND":
            if unit.get("natural_frame_exit") is not True or unit.get("visible_anatomy_complete") is not True:
                raise ValueError(f"{label} cropped foreground must have complete visible anatomy and a natural frame exit")
            off_frame = unit.get("off_frame_scale_support_evidence")
            if not isinstance(off_frame, list) or not off_frame:
                raise ValueError(f"{label} cropped foreground needs off-frame scale/support evidence")
            for item in off_frame:
                bound(item, path.parent, f"{label}.off_frame_scale_support_evidence")
        normalized.append({"generation_unit_id": unit_id, "actor_id": actor, "pose_ids": poses,
                           "anatomy_mode": mode, "reference_sha256": ref_hashes,
                           "coverage_evidence_sha256": evidence_hashes})
    if supplied != required:
        raise ValueError(f"generation unit coverage differs from frozen scope; missing={sorted(required-supplied)} extra={sorted(supplied-required)}")
    return {
        "schema": GATE_SCHEMA,
        "status": "CURRENT",
        "unit_id": scene_id,
        "revision": revision,
        "handoff_path": str(path),
        "handoff_sha256": sha256(path),
        "scope_sha256": sha256(scope_path),
        "manual_review_node": {"path": str(node_path), "sha256": sha256(node_path)},
        "manual_review_branch": {
            "mode": branch_mode,
            "blocks_mainline": branch_mode == "USER_HOLD",
            "approval": (
                {"path": str(approval_path), "sha256": sha256(approval_path)}
                if approval_path is not None
                else None
            ),
        },
        "manual_review_approval": (
            {"path": str(approval_path), "sha256": sha256(approval_path)}
            if approval_path is not None
            else None
        ),
        "generation_units": normalized,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--checked-at", required=True)
    args = parser.parse_args()
    try:
        result = validate(args.handoff)
        result["checked_at"] = args.checked_at
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        result = {"schema": GATE_SCHEMA, "status": "FAIL", "errors": [str(exc)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "CURRENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
