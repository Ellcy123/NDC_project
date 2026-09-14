#!/usr/bin/env python3
"""Register, audit and summarize selected NDC delivery candidates."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from zoneinfo import ZoneInfo


SCHEMA = "ndc-delivery-candidate/v1"
STATUSES = {
    "DELIVERY_CANDIDATE_SELECTED",
    "DELIVERY_CANDIDATE_REVIEWING",
    "DELIVERY_CANDIDATE_PASS_READY",
    "PROMOTED_FORMAL",
    "REVIEW_FAILED_PENDING_MOVE",
    "MOVED_FROM_DELIVERY_CANDIDATES",
}
ACTIVE_STATUSES = STATUSES - {"PROMOTED_FORMAL", "MOVED_FROM_DELIVERY_CANDIDATES"}
TRANSITIONS = {
    "DELIVERY_CANDIDATE_SELECTED": {"DELIVERY_CANDIDATE_REVIEWING", "DELIVERY_CANDIDATE_PASS_READY", "REVIEW_FAILED_PENDING_MOVE"},
    "DELIVERY_CANDIDATE_REVIEWING": {"DELIVERY_CANDIDATE_PASS_READY", "REVIEW_FAILED_PENDING_MOVE"},
    "DELIVERY_CANDIDATE_PASS_READY": {"PROMOTED_FORMAL", "REVIEW_FAILED_PENDING_MOVE"},
    "REVIEW_FAILED_PENDING_MOVE": {"DELIVERY_CANDIDATE_SELECTED"},
    "PROMOTED_FORMAL": set(),
    "MOVED_FROM_DELIVERY_CANDIDATES": set(),
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    temp = path.with_name(path.name + ".writing")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def safe_segment(value: str, field: str) -> str:
    if (not isinstance(value, str) or not value.strip() or value in {".", ".."}
            or "/" in value or "\\" in value or not re.fullmatch(r"[^<>:\"|?*]+", value)):
        raise ValueError(f"unsafe {field}")
    return value.strip()


def image_binding(path: Path, relative_to: Path) -> dict:
    if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"selected image is missing or unsupported: {path}")
    return {"path": path.relative_to(relative_to).as_posix(), "sha256": sha256(path)}


def candidate_base(delivery_root: Path, category: str, unit: str) -> Path:
    return delivery_root.resolve() / safe_segment(category, "category") / safe_segment(unit, "unit")


def register(args: argparse.Namespace) -> dict:
    source = args.candidate.resolve()
    if not source.is_file() or source.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("candidate must be an existing image")
    base = candidate_base(args.delivery_root, args.category, args.unit)
    target = (base / safe_segment(args.scene, "scene") / safe_segment(args.artifact, "artifact")
              / "交付候选" / safe_segment(args.revision, "revision"))
    if target.exists():
        raise ValueError("candidate revision already exists; never overwrite it")
    stage = target.with_name(target.name + ".writing-" + os.urandom(4).hex())
    candidate_dir = stage / "candidate"
    reference_dir = stage / "selected_references"
    candidate_dir.mkdir(parents=True)
    reference_dir.mkdir()
    candidate_name = source.stem + "__DELIVERY_CANDIDATE" + source.suffix.lower()
    candidate_copy = candidate_dir / candidate_name
    shutil.copy2(source, candidate_copy)
    references = []
    for index, raw in enumerate(args.reference or [], 1):
        ref = raw.resolve()
        if not ref.is_file() or ref.suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"selected reference is missing or unsupported: {ref}")
        name = f"{index:02d}_{ref.stem}__SELECTED_REFERENCE{ref.suffix.lower()}"
        copy = reference_dir / name
        shutil.copy2(ref, copy)
        references.append(image_binding(copy, stage))
    manifest = {
        "schema": SCHEMA,
        "artifact_id": args.artifact,
        "scene_id": args.scene,
        "category": args.category,
        "unit": args.unit,
        "revision": args.revision,
        "scope_revision_sha256": args.scope_revision_sha256.lower(),
        "status": "DELIVERY_CANDIDATE_SELECTED",
        "candidate": image_binding(candidate_copy, stage),
        "selected_references": references,
        "selection_reason": args.reason,
        "selected_by": args.selected_by,
        "selected_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "known_blockers": [],
        "review": None,
        "formal_path": None,
    }
    write_json(stage / "candidate_manifest.json", manifest)
    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(stage, target)
    return {"registered": str(target), "manifest": str(target / "candidate_manifest.json"), "status": manifest["status"]}


def resolve_binding(manifest_path: Path, binding: object, label: str, failures: list[str]) -> Path | None:
    if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
        failures.append(f"{label}: path and sha256 are required")
        return None
    path = (manifest_path.parent / binding["path"]).resolve()
    try:
        path.relative_to(manifest_path.parent.resolve())
    except ValueError:
        failures.append(f"{label}: path escapes the candidate revision")
        return None
    if not path.is_file():
        failures.append(f"{label}: file is missing")
    elif sha256(path).lower() != str(binding["sha256"]).lower():
        failures.append(f"{label}: hash mismatch")
    return path


def audit_manifest(manifest_path: Path) -> list[str]:
    manifest_path = manifest_path.resolve()
    data = read_json(manifest_path)
    failures: list[str] = []
    if data.get("schema") != SCHEMA:
        failures.append("unsupported candidate manifest schema")
    if data.get("status") not in STATUSES:
        failures.append("invalid candidate status")
    for field in ("artifact_id", "scene_id", "category", "unit", "revision", "selection_reason", "selected_by", "selected_at"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            failures.append(f"{field}: nonempty text required")
    scope_hash = data.get("scope_revision_sha256")
    if not isinstance(scope_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", scope_hash):
        failures.append("scope_revision_sha256 must be a SHA-256")
    candidate = resolve_binding(manifest_path, data.get("candidate"), "candidate", failures)
    if candidate is not None and "__DELIVERY_CANDIDATE" not in candidate.stem:
        failures.append("candidate filename lacks DELIVERY_CANDIDATE marker")
    references = data.get("selected_references")
    if not isinstance(references, list):
        failures.append("selected_references must be a list")
    else:
        for index, binding in enumerate(references):
            ref = resolve_binding(manifest_path, binding, f"selected_references[{index}]", failures)
            if ref is not None and "__SELECTED_REFERENCE" not in ref.stem:
                failures.append(f"selected_references[{index}] filename lacks SELECTED_REFERENCE marker")
    if data.get("status") == "PROMOTED_FORMAL":
        raw = data.get("formal_path")
        if not isinstance(raw, str) or not raw:
            failures.append("PROMOTED_FORMAL requires formal_path")
        else:
            formal = Path(raw).resolve()
            if {"交付候选", "_交付候选", "节点交付"} & set(formal.parts):
                failures.append("formal_path cannot remain inside the candidate subtree")
            elif not formal.is_file() or candidate is None or sha256(formal) != sha256(candidate):
                failures.append("formal_path must be an exact candidate-byte copy")
    return failures


def status_update(args: argparse.Namespace) -> dict:
    path = args.manifest.resolve()
    data = read_json(path)
    failures = audit_manifest(path)
    if failures:
        raise ValueError("candidate manifest is invalid: " + "; ".join(failures))
    current = data["status"]
    if args.expect_status != current:
        raise ValueError(f"candidate status changed: expected {args.expect_status}, found {current}")
    if args.status not in TRANSITIONS[current]:
        raise ValueError(f"invalid candidate transition: {current} -> {args.status}")
    if not args.reason.strip():
        raise ValueError("status transition requires a concrete reason")
    review = None
    if args.review:
        review_path = args.review.resolve()
        if not review_path.is_file():
            raise ValueError("review file is missing")
        review = {"path": str(review_path), "sha256": sha256(review_path)}
    if args.status in {"DELIVERY_CANDIDATE_PASS_READY", "REVIEW_FAILED_PENDING_MOVE"} and review is None:
        raise ValueError("review result status requires --review")
    if args.status == "PROMOTED_FORMAL":
        if not args.formal_file:
            raise ValueError("PROMOTED_FORMAL requires --formal-file")
        formal = args.formal_file.resolve()
        candidate = (path.parent / data["candidate"]["path"]).resolve()
        if not formal.is_file() or sha256(formal) != sha256(candidate):
            raise ValueError("formal file must already exist with exact candidate bytes")
        if {"交付候选", "_交付候选", "节点交付"} & set(formal.parts):
            raise ValueError("formal file cannot be inside the candidate subtree")
        data["formal_path"] = str(formal)
    data["status"] = args.status
    if review is not None:
        data["review"] = review
    data.setdefault("status_history", []).append({
        "from": current,
        "to": args.status,
        "at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "reason": args.reason,
    })
    write_json(path, data)
    return {"manifest": str(path), "status": args.status}


def move_failed(args: argparse.Namespace) -> dict:
    path = args.manifest.resolve()
    data = read_json(path)
    failures = audit_manifest(path)
    if failures:
        raise ValueError("candidate manifest is invalid: " + "; ".join(failures))
    if data["status"] != "REVIEW_FAILED_PENDING_MOVE":
        raise ValueError("only a reviewed failed candidate can be moved")
    if not args.reason.strip():
        raise ValueError("move requires a concrete reason")
    revision_dir = path.parent
    target = (args.destination_root.resolve() / "移出的交付候选"
              / safe_segment(data["artifact_id"], "artifact") / safe_segment(data["revision"], "revision"))
    if revision_dir.anchor.lower() != target.anchor.lower():
        raise ValueError("move destination must be on the same volume for an atomic retained move")
    if target.exists():
        raise ValueError("move destination already exists")
    candidate = (revision_dir / data["candidate"]["path"]).resolve()
    data["status"] = "MOVED_FROM_DELIVERY_CANDIDATES"
    data["moved_to"] = str(target)
    data["candidate_pre_move_sha256"] = sha256(candidate)
    data.setdefault("status_history", []).append({
        "from": "REVIEW_FAILED_PENDING_MOVE", "to": "MOVED_FROM_DELIVERY_CANDIDATES",
        "at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(), "reason": args.reason,
    })
    write_json(path, data)
    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(revision_dir, target)
    moved_manifest = target / path.name
    if audit_manifest(moved_manifest):
        raise ValueError("moved candidate failed post-move audit; retain destination for recovery")
    return {"moved_manifest": str(moved_manifest), "status": data["status"],
            "candidate_sha256": data["candidate_pre_move_sha256"]}


def reporting_scope(batch_path: Path) -> set[str]:
    batch_path = batch_path.resolve()
    batch = read_json(batch_path)
    pointer = batch.get("active_delivery_scope_revision")
    if pointer is None:
        return set(batch["scope"]["required_artifacts"])
    revision_path = Path(pointer["path"])
    if not revision_path.is_absolute():
        revision_path = batch_path.parent / revision_path
    if sha256(revision_path).lower() != pointer["sha256"].lower():
        raise ValueError("active scope revision hash mismatch")
    revision = read_json(revision_path)
    return set(revision.get("reporting_asset_artifacts", revision["execution_required_artifacts"]))


def audit_tree(root: Path, batch_path: Path | None = None) -> dict:
    root = root.resolve()
    manifests = sorted(root.rglob("candidate_manifest.json")) if root.is_dir() else []
    entries = []
    active_by_artifact: dict[str, list[str]] = {}
    for path in manifests:
        data = read_json(path)
        failures = audit_manifest(path)
        status = data.get("status")
        artifact = data.get("artifact_id")
        entries.append({"manifest": str(path), "artifact_id": artifact, "status": status, "failures": failures})
        if not failures and status in ACTIVE_STATUSES:
            active_by_artifact.setdefault(artifact, []).append(str(path))
    duplicate_active = {key: value for key, value in active_by_artifact.items() if len(value) > 1}
    required = reporting_scope(batch_path) if batch_path else set()
    active = set(active_by_artifact)
    status_counts = {status: 0 for status in sorted(STATUSES)}
    selected_reference_count = 0
    for entry in entries:
        if entry["failures"]:
            continue
        data = read_json(Path(entry["manifest"]))
        status_counts[data["status"]] += 1
        selected_reference_count += len(data.get("selected_references", []))
    failures = []
    if duplicate_active:
        failures.append("multiple active delivery candidates exist for: " + ", ".join(sorted(duplicate_active)))
    if batch_path and not active <= required:
        failures.append("candidate artifacts outside current reporting scope: " + ", ".join(sorted(active - required)))
    invalid = [entry for entry in entries if entry["failures"]]
    if invalid:
        failures.append(f"{len(invalid)} candidate manifests are invalid")
    return {
        "schema": "ndc-delivery-candidate-audit/v1",
        "candidate_root": str(root),
        "manifest_count": len(manifests),
        "active_candidate_artifacts": len(active),
        "required_reporting_artifacts": len(required) if batch_path else None,
        "candidate_coverage_percent": round(100 * len(active & required) / len(required), 1) if required else None,
        "selected_reference_count": selected_reference_count,
        "status_counts": status_counts,
        "failures": failures,
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    register_parser = sub.add_parser("register")
    register_parser.add_argument("--delivery-root", type=Path, required=True)
    register_parser.add_argument("--category", required=True)
    register_parser.add_argument("--unit", required=True)
    register_parser.add_argument("--scene", required=True)
    register_parser.add_argument("--artifact", required=True)
    register_parser.add_argument("--revision", required=True)
    register_parser.add_argument("--candidate", type=Path, required=True)
    register_parser.add_argument("--reference", type=Path, action="append")
    register_parser.add_argument("--scope-revision-sha256", required=True)
    register_parser.add_argument("--reason", required=True)
    register_parser.add_argument("--selected-by", required=True)
    status_parser = sub.add_parser("set-status")
    status_parser.add_argument("--manifest", type=Path, required=True)
    status_parser.add_argument("--expect-status", required=True, choices=sorted(STATUSES))
    status_parser.add_argument("--status", required=True, choices=sorted(STATUSES))
    status_parser.add_argument("--reason", required=True)
    status_parser.add_argument("--review", type=Path)
    status_parser.add_argument("--formal-file", type=Path)
    move_parser = sub.add_parser("move-failed")
    move_parser.add_argument("--manifest", type=Path, required=True)
    move_parser.add_argument("--destination-root", type=Path, required=True)
    move_parser.add_argument("--reason", required=True)
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("--candidate-root", type=Path, required=True)
    audit_parser.add_argument("--batch", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "register":
            result = register(args)
        elif args.command == "set-status":
            result = status_update(args)
        elif args.command == "move-failed":
            result = move_failed(args)
        else:
            result = audit_tree(args.candidate_root, args.batch)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"blocked": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result.get("failures")))


if __name__ == "__main__":
    raise SystemExit(main())
