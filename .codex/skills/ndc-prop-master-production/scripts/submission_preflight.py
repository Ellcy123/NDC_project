#!/usr/bin/env python3
"""Fail before an NDC prop generation attempt is reserved or submitted."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


SHARED_PIPELINE = Path(__file__).resolve().parents[2] / "ndc-art-stage-pipeline" / "scripts"
if str(SHARED_PIPELINE) not in sys.path:
    sys.path.insert(0, str(SHARED_PIPELINE))
from asset_discovery import bound as discovery_bound, validate_receipt  # noqa: E402


SCHEMA = "ndc-prop-submission-preflight/v2"
LIMITS = {"master": 6, "scene": 3, "menu": 3, "derived": 3}
WEB_EXCEPTION_ROLES = {"scene_evidence", "container_menu", "environmental_narrative_big"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def execution_scope(batch_path: Path, batch: dict) -> tuple[set[str], str | None]:
    pointer = batch.get("active_delivery_scope_revision")
    if pointer is None:
        return set(batch["scope"]["required_artifacts"]), None
    path = resolve(batch_path.parent, pointer["path"])
    actual = sha256(path).lower()
    if actual != pointer["sha256"].lower():
        raise ValueError("active delivery scope revision hash mismatch")
    revision = read_json(path)
    return set(revision["execution_required_artifacts"]), actual


def check_file(binding: dict, base: Path, field: str, failures: list[str]) -> None:
    if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
        failures.append(f"{field}: path and sha256 are required")
        return
    path = resolve(base, binding["path"])
    if not path.is_file():
        failures.append(f"{field}: file is missing")
    elif sha256(path).lower() != str(binding["sha256"]).lower():
        failures.append(f"{field}: hash mismatch")


def check_discovery(manifest: dict, manifest_path: Path, active_scope_sha256: str | None, failures: list[str]) -> None:
    discovery = manifest.get("discovery")
    if not isinstance(discovery, dict):
        failures.append("discovery receipt is required; legacy batches must migrate before submission")
        return
    declared_scope = discovery.get("scope")
    if not isinstance(declared_scope, dict):
        failures.append("discovery.scope is required")
        return
    if active_scope_sha256 is None:
        failures.append("active delivery scope revision is required; migrate legacy batches before submission")
        return
    if str(discovery.get("scope_revision_sha256", "")).lower() != active_scope_sha256.lower():
        failures.append("discovery does not bind the current active scope revision")
        return
    item_id = manifest.get("item_id")
    pose_or_state = manifest.get("pose_or_state")
    artifact_role = manifest.get("artifact_role")
    if not isinstance(item_id, str) or not item_id.strip():
        failures.append("item_id is required for discovery binding")
        return
    if not isinstance(pose_or_state, str) or not pose_or_state.strip():
        failures.append("pose_or_state is required for discovery binding")
        return
    if not isinstance(artifact_role, str) or not artifact_role.strip():
        failures.append("artifact_role is required for discovery binding")
        return
    expected = {
        "domain": "prop",
        "scene_id": manifest.get("scene_id") or "GLOBAL",
        "item_id": item_id,
        "pose_or_state": pose_or_state,
        "artifact_role": artifact_role,
        "scope_revision_sha256": active_scope_sha256,
    }
    for key, value in expected.items():
        if key != "scope_revision_sha256" and str(declared_scope.get(key, "")) != str(value):
            failures.append(f"discovery.scope must match the preflight {key}")
    if failures:
        return
    try:
        receipt_path = discovery_bound(discovery.get("receipt"), manifest_path.parent, "discovery.receipt")
        failures.extend(validate_receipt(receipt_path, expected_scope=expected, action="GENERATE"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        failures.append(f"discovery receipt is invalid: {exc}")


def validate(manifest_path: Path, batch_path: Path) -> list[str]:
    manifest_path = manifest_path.resolve()
    batch_path = batch_path.resolve()
    manifest = read_json(manifest_path)
    batch = read_json(batch_path)
    failures: list[str] = []
    if manifest.get("schema") != SCHEMA:
        failures.append("unsupported preflight schema")
    artifact_id = manifest.get("artifact_id")
    active, revision_sha = execution_scope(batch_path, batch)
    if artifact_id not in active:
        failures.append("artifact is outside the active execution scope")
    artifact = batch.get("artifacts", {}).get(artifact_id, {})
    if manifest.get("job_id") != artifact.get("job_id"):
        failures.append("job_id does not match the batch artifact")
    job_id = manifest.get("job_id")
    job = batch.get("jobs", {}).get(job_id)
    task_id = manifest.get("task_id")
    planned = manifest.get("planned_task_attempt")
    if not isinstance(task_id, str) or not task_id.strip():
        failures.append("task_id must identify the current conversation")
    if job is None or job.get("kind") not in LIMITS:
        failures.append("job is not registered with a supported attempt budget")
    else:
        log_raw = batch.get("attempt_log")
        if not isinstance(log_raw, str) or not log_raw:
            failures.append("batch attempt_log is required")
        else:
            log_path = resolve(batch_path.parent, log_raw)
            try:
                events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
                used = sum(event.get("type") == "attempt" and event.get("job_id") == job_id
                           and event.get("task_id") == task_id for event in events)
                if type(planned) is not int or planned != used + 1 or planned > LIMITS[job["kind"]]:
                    failures.append("planned_task_attempt is stale or exceeds the current task budget")
            except (OSError, json.JSONDecodeError) as exc:
                failures.append(f"attempt log cannot be read: {exc}")
    expected_scene = artifact.get("scene_id", "")
    if manifest.get("scene_id", "") != expected_scene:
        failures.append("scene_id does not match the batch artifact")
    declared_revision = manifest.get("scope_revision_sha256")
    if revision_sha and str(declared_revision).lower() != revision_sha:
        failures.append("preflight does not bind the active scope revision")
    check_discovery(manifest, manifest_path, revision_sha, failures)
    check_file(manifest.get("prompt"), manifest_path.parent, "prompt", failures)
    refs = manifest.get("references")
    if not isinstance(refs, list):
        failures.append("references must be a list")
    else:
        for index, ref in enumerate(refs):
            check_file(ref, manifest_path.parent, f"references[{index}]", failures)
    target = manifest.get("target", {})
    if (type(target.get("width")) is not int or target["width"] <= 0
            or type(target.get("height")) is not int or target["height"] <= 0
            or target.get("format") not in {"PNG", "WEBP", "JPEG"}):
        failures.append("target requires positive width/height and an allowed format")
    if not isinstance(manifest.get("backend"), str) or not manifest["backend"].strip():
        failures.append("backend is required")
    elif manifest["backend"] == "chatgpt_web" and manifest.get("artifact_role") not in WEB_EXCEPTION_ROLES:
        failures.append("chatgpt_web is only allowed for scene evidence, container menus, or environmental-narrative Big; it cannot generate ordinary masters, Big, or Icons")
    if manifest.get("submission_state") not in {"NOT_SUBMITTED", "CONFIRMED_NO_PRIOR_SUBMISSION"}:
        failures.append("unknown or existing submission must be resolved before a new attempt")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--batch", type=Path, required=True)
    args = parser.parse_args()
    try:
        failures = validate(args.manifest, args.batch)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
    print(json.dumps({"submission_preflight_valid": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
