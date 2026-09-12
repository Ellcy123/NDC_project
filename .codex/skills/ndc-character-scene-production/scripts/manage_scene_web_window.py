#!/usr/bin/env python3
"""Manage one logical scene/revision web workspace with safe parallel conversation lanes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

IDENTITY_SCHEMA = "ndc-chatgpt-web-scene-workspace-identity/v2"
STATE_SCHEMA = "ndc-chatgpt-web-scene-workspace-state/v2"
PACKET_SCHEMA = "ndc-chatgpt-web-submission-packet/v3"
SUPPORTED_BROWSERS = {"iab", "chrome", "edge"}
WORKSPACE_STATES = {"DRAFT", "READY", "QUARANTINED", "SUPERSEDED", "CLOSED"}
OPEN_ATTEMPT_STATES = {"PREPARED", "UPLOAD_CONFIRMED", "PENDING", "UNKNOWN"}
TERMINAL_ATTEMPT_STATES = {
    "PRODUCED", "FAILED", "REFUSED", "ACCOUNT_RECORD_UNAVAILABLE",
    "CANCELLED_BEFORE_SUBMISSION",
}
ALL_ATTEMPT_STATES = OPEN_ATTEMPT_STATES | TERMINAL_ATTEMPT_STATES
REFERENCE_ROLES = ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def text(value: object, label: str, *, max_length: int = 300) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ValueError(f"{label} must be a non-empty string of at most {max_length} characters")
    return value


def timestamp(value: object, label: str) -> str:
    value = text(value, label, max_length=80)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return value


def conversation_url(value: object, label: str = "conversation_url") -> str:
    value = text(value, label, max_length=2000)
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme != "https"
        or not (host == "chatgpt.com" or host.endswith(".chatgpt.com"))
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in {None, 443}
    ):
        raise ValueError(f"{label} must be an https://chatgpt.com conversation URL")
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) != 2 or path_parts[0] != "c" or not path_parts[1]:
        raise ValueError(f"{label} must identify a concrete /c/<conversation-id> conversation")
    return value


def file_ref(path: Path) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"bound file does not exist: {path}")
    return {"path": str(path), "sha256": sha256(path)}


def checked_file_ref(entry: object, label: str) -> Path:
    if not isinstance(entry, dict):
        raise ValueError(f"{label} must be a file binding")
    path_value = entry.get("path")
    digest = entry.get("sha256")
    if not isinstance(path_value, str) or not Path(path_value).is_absolute():
        raise ValueError(f"{label}.path must be absolute")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None:
        raise ValueError(f"{label}.sha256 must be a complete SHA-256")
    path = Path(path_value).resolve()
    if not path.is_file() or sha256(path) != digest.lower():
        raise ValueError(f"{label} no longer matches its bound file")
    return path


def write_json_atomic(path: Path, value: dict) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def validate_identity(identity: dict) -> None:
    if identity.get("schema") != IDENTITY_SCHEMA:
        raise ValueError(f"scene window identity schema must be {IDENTITY_SCHEMA}")
    text(identity.get("scene_id"), "identity.scene_id")
    revision = identity.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ValueError("identity.revision must be a positive integer")
    if identity.get("browser") not in SUPPORTED_BROWSERS:
        raise ValueError("identity.browser must be iab, chrome or edge")
    text(identity.get("window_id"), "identity.window_id")
    text(identity.get("window_label"), "identity.window_label")
    if identity.get("workspace_kind") != "logical_scene_revision":
        raise ValueError("identity.workspace_kind must be logical_scene_revision")
    if identity.get("physical_window_required") is not False:
        raise ValueError("identity.physical_window_required must be false")
    timestamp(identity.get("created_at"), "identity.created_at")
    label = identity.get("account_profile_label")
    if label is not None:
        text(label, "identity.account_profile_label", max_length=100)
        if "@" in label:
            raise ValueError("account_profile_label must be a non-sensitive alias, not an email address")


def unit_work(unit: dict) -> set[tuple[str, str]]:
    return {(unit["actor_id"], pose_id) for pose_id in unit["pose_ids"]}


def latest_status(unit: dict) -> str | None:
    attempts = unit.get("attempts", [])
    return attempts[-1]["status"] if attempts else None


def ancestors(unit_id: str, by_id: dict[str, dict]) -> set[str]:
    result: set[str] = set()
    current = by_id[unit_id].get("supersedes_unit_id")
    while current is not None:
        if current not in by_id:
            raise ValueError(f"superseded unit does not exist: {current}")
        if current == unit_id or current in result:
            raise ValueError("conversation supersession chain contains a cycle")
        result.add(current)
        current = by_id[current].get("supersedes_unit_id")
    return result


def validate_state(state_path: Path) -> dict:
    state_path = state_path.resolve()
    state = load_json(state_path)
    if state.get("schema") != STATE_SCHEMA:
        raise ValueError(f"scene window state schema must be {STATE_SCHEMA}")
    identity_path = checked_file_ref(state.get("identity"), "state.identity")
    identity = load_json(identity_path)
    validate_identity(identity)
    if state.get("status") not in WORKSPACE_STATES:
        raise ValueError("state.status is invalid")
    max_open = state.get("max_open_submissions")
    if not isinstance(max_open, int) or isinstance(max_open, bool) or not 1 <= max_open <= 8:
        raise ValueError("state.max_open_submissions must be an integer from 1 to 8")
    health = state.get("browser_health")
    canary = state.get("canary")
    if not isinstance(health, dict) or health.get("status") not in {"UNVERIFIED", "HEALTHY", "QUARANTINED"}:
        raise ValueError("state.browser_health.status is invalid")
    if not isinstance(canary, dict) or canary.get("status") not in {"NOT_RUN", "PASS", "FAIL"}:
        raise ValueError("state.canary.status is invalid")
    if state["status"] == "READY" and not (
        health.get("status") == "HEALTHY" and canary.get("status") == "PASS"
    ):
        raise ValueError("READY requires current HEALTHY browser evidence and a PASS canary")
    if state["status"] == "QUARANTINED" and health.get("status") != "QUARANTINED":
        raise ValueError("QUARANTINED workspace requires quarantined browser health")
    units = state.get("units")
    events = state.get("events")
    if not isinstance(units, list) or not isinstance(events, list):
        raise ValueError("state.units and state.events must be lists")

    unit_ids: set[str] = set()
    urls: set[str] = set()
    submission_ids: set[str] = set()
    work_by_unit: dict[str, set[tuple[str, str]]] = {}
    by_id: dict[str, dict] = {}
    unresolved_units: list[str] = []
    for index, unit in enumerate(units):
        if not isinstance(unit, dict):
            raise ValueError(f"units[{index}] must be an object")
        unit_id = text(unit.get("generation_unit_id"), f"units[{index}].generation_unit_id")
        if unit_id in unit_ids:
            raise ValueError(f"duplicate generation_unit_id: {unit_id}")
        unit_ids.add(unit_id)
        by_id[unit_id] = unit
        text(unit.get("actor_id"), f"units[{index}].actor_id")
        poses = unit.get("pose_ids")
        if not isinstance(poses, list) or not poses or len(poses) != len(set(poses)) or not all(isinstance(v, str) and v.strip() for v in poses):
            raise ValueError(f"units[{index}].pose_ids must be distinct non-empty strings")
        url = conversation_url(unit.get("conversation_url"), f"units[{index}].conversation_url")
        if url in urls:
            raise ValueError(f"conversation URL is assigned to more than one generation unit: {url}")
        urls.add(url)
        timestamp(unit.get("registered_at"), f"units[{index}].registered_at")
        supersedes = unit.get("supersedes_unit_id")
        if supersedes is not None:
            text(supersedes, f"units[{index}].supersedes_unit_id")
            if supersedes == unit_id:
                raise ValueError(f"{unit_id} cannot supersede itself")
        attempts = unit.get("attempts")
        if not isinstance(attempts, list):
            raise ValueError(f"units[{index}].attempts must be a list")
        open_count = 0
        for attempt_index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict):
                raise ValueError(f"{unit_id}.attempts[{attempt_index}] must be an object")
            checked_file_ref(attempt.get("submission_manifest"), f"{unit_id}.attempts[{attempt_index}].submission_manifest")
            status = attempt.get("status")
            if status not in ALL_ATTEMPT_STATES:
                raise ValueError(f"{unit_id}.attempts[{attempt_index}].status is invalid")
            timestamp(attempt.get("prepared_at"), f"{unit_id}.attempts[{attempt_index}].prepared_at")
            submission_id = attempt.get("submission_id")
            if status in {"PREPARED", "UPLOAD_CONFIRMED", "CANCELLED_BEFORE_SUBMISSION"}:
                if submission_id is not None:
                    raise ValueError(f"{unit_id} unsubmitted attempt cannot have a submission_id")
            else:
                submission_id = text(submission_id, f"{unit_id}.attempts[{attempt_index}].submission_id")
                if submission_id in submission_ids:
                    raise ValueError(f"duplicate submission_id: {submission_id}")
                submission_ids.add(submission_id)
                timestamp(attempt.get("submitted_at"), f"{unit_id}.attempts[{attempt_index}].submitted_at")
            if status in ({"UNKNOWN"} | TERMINAL_ATTEMPT_STATES):
                timestamp(attempt.get("resolved_at"), f"{unit_id}.attempts[{attempt_index}].resolved_at")
                text(attempt.get("evidence"), f"{unit_id}.attempts[{attempt_index}].evidence", max_length=2000)
            confirmation = attempt.get("upload_confirmation")
            needs_confirmation = status in {
                "UPLOAD_CONFIRMED", "PENDING", "UNKNOWN", "PRODUCED", "FAILED", "REFUSED",
                "ACCOUNT_RECORD_UNAVAILABLE",
            }
            if needs_confirmation:
                if not isinstance(confirmation, dict):
                    raise ValueError(f"{unit_id}.attempts[{attempt_index}] needs upload_confirmation")
                timestamp(confirmation.get("confirmed_at"), f"{unit_id}.attempts[{attempt_index}].upload_confirmation.confirmed_at")
                text(confirmation.get("evidence"), f"{unit_id}.attempts[{attempt_index}].upload_confirmation.evidence", max_length=2000)
                if confirmation.get("roles") != REFERENCE_ROLES:
                    raise ValueError(f"{unit_id}.attempts[{attempt_index}] upload confirmation must preserve three independent roles")
                hashes = confirmation.get("sha256")
                if not isinstance(hashes, list) or len(hashes) != 3 or not all(
                    isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes
                ):
                    raise ValueError(f"{unit_id}.attempts[{attempt_index}] upload confirmation needs three SHA-256 values")
                if not isinstance(confirmation.get("prompt_sha256"), str) or re.fullmatch(
                    r"[0-9a-f]{64}", confirmation["prompt_sha256"]
                ) is None:
                    raise ValueError(f"{unit_id}.attempts[{attempt_index}] upload confirmation needs prompt_sha256")
            if status in OPEN_ATTEMPT_STATES:
                open_count += 1
        if open_count > 1:
            raise ValueError(f"{unit_id} has more than one unresolved attempt in its conversation")
        if open_count:
            unresolved_units.append(unit_id)
        work_by_unit[unit_id] = unit_work(unit)

    if len(unresolved_units) > max_open:
        raise ValueError("open submission WIP exceeds state.max_open_submissions")

    if state["status"] == "CLOSED":
        timestamp(state.get("closed_at"), "state.closed_at")
        if unresolved_units:
            raise ValueError("a closed scene window cannot contain unresolved conversations")

    ancestry = {unit_id: ancestors(unit_id, by_id) for unit_id in by_id}
    for unit_id, work in work_by_unit.items():
        overlaps = [other_id for other_id, other_work in work_by_unit.items() if other_id != unit_id and work & other_work]
        for other_id in overlaps:
            unit = by_id[unit_id]
            other = by_id[other_id]
            same_linear_chain = other_id in ancestry[unit_id] or unit_id in ancestry[other_id]
            if not same_linear_chain:
                raise ValueError(f"actor/pose work overlaps across conversation units: {unit_id}, {other_id}")

    for unit in units:
        supersedes = unit.get("supersedes_unit_id")
        if supersedes is not None:
            if supersedes not in by_id:
                raise ValueError(f"superseded unit does not exist: {supersedes}")
            if latest_status(by_id[supersedes]) != "ACCOUNT_RECORD_UNAVAILABLE":
                raise ValueError("a replacement conversation is allowed only after account_record_unavailable")
            if unit_work(unit) != unit_work(by_id[supersedes]):
                raise ValueError("a replacement conversation must cover exactly the superseded actor/pose work")

    return {
        "state": state,
        "identity": identity,
        "identity_path": identity_path,
        "report": {
            "schema": "ndc-chatgpt-web-scene-window-gate/v1",
            "status": "PASS",
            "scene_id": identity["scene_id"],
            "revision": identity["revision"],
            "window_id": identity["window_id"],
            "browser": identity["browser"],
            "window_status": state["status"],
            "workspace_status": state["status"],
            "ready": state["status"] == "READY",
            "browser_health": health["status"],
            "canary": canary["status"],
            "max_open_submissions": max_open,
            "conversation_units": len(units),
            "unresolved_units": unresolved_units,
            "parallel_unresolved_count": len(unresolved_units),
            "parallel_unresolved_allowed": True,
            "rule": "one unresolved attempt per conversation; multiple distinct scene-window conversations may be unresolved concurrently",
        },
    }


def create_window(directory: Path, scene_id: str, revision: int, browser: str, window_id: str,
                  window_label: str, created_at: str, account_profile_label: str | None = None,
                  max_open_submissions: int = 3) -> dict:
    directory = directory.resolve()
    identity_path = directory / "scene-window-identity.json"
    state_path = directory / "scene-window-state.json"
    if identity_path.exists() or state_path.exists():
        raise ValueError("scene window directory already contains identity or state; never overwrite it")
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError("browser must be iab, chrome or edge")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ValueError("revision must be a positive integer")
    if not isinstance(max_open_submissions, int) or isinstance(max_open_submissions, bool) or not 1 <= max_open_submissions <= 8:
        raise ValueError("max_open_submissions must be an integer from 1 to 8")
    identity = {
        "schema": IDENTITY_SCHEMA,
        "scene_id": text(scene_id, "scene_id"),
        "revision": revision,
        "browser": browser,
        "window_id": text(window_id, "window_id"),
        "window_label": text(window_label, "window_label"),
        "workspace_kind": "logical_scene_revision",
        "physical_window_required": False,
        "created_at": timestamp(created_at, "created_at"),
        "account_profile_label": account_profile_label,
    }
    validate_identity(identity)
    write_json_atomic(identity_path, identity)
    state = {
        "schema": STATE_SCHEMA,
        "identity": file_ref(identity_path),
        "status": "DRAFT",
        "max_open_submissions": max_open_submissions,
        "browser_health": {"status": "UNVERIFIED"},
        "canary": {"status": "NOT_RUN"},
        "units": [],
        "events": [{"event": "WORKSPACE_CREATED", "at": created_at, "window_id": window_id}],
    }
    write_json_atomic(state_path, state)
    return {"identity": str(identity_path), "state": str(state_path), **validate_state(state_path)["report"]}


def register_unit(state_path: Path, generation_unit_id: str, actor_id: str, pose_ids: list[str],
                  url: str, registered_at: str, supersedes_unit_id: str | None = None) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    if state["status"] not in {"DRAFT", "READY"}:
        raise ValueError("cannot register a conversation in a quarantined, superseded or closed workspace")
    generation_unit_id = text(generation_unit_id, "generation_unit_id")
    if any(unit["generation_unit_id"] == generation_unit_id for unit in state["units"]):
        raise ValueError(f"generation unit already exists: {generation_unit_id}")
    actor_id = text(actor_id, "actor_id")
    if not pose_ids or len(pose_ids) != len(set(pose_ids)) or not all(isinstance(v, str) and v.strip() for v in pose_ids):
        raise ValueError("pose_ids must contain distinct non-empty strings")
    url = conversation_url(url)
    if any(unit["conversation_url"] == url for unit in state["units"]):
        raise ValueError("each generation unit needs its own ChatGPT conversation URL")
    proposed_work = {(actor_id, pose_id) for pose_id in pose_ids}
    overlapping = [unit for unit in state["units"] if proposed_work & unit_work(unit)]
    if supersedes_unit_id is None and overlapping:
        raise ValueError("actor/pose work already belongs to another conversation unit")
    if supersedes_unit_id is not None:
        supersedes_unit_id = text(supersedes_unit_id, "supersedes_unit_id")
        by_id = {unit["generation_unit_id"]: unit for unit in state["units"]}
        if supersedes_unit_id not in by_id:
            raise ValueError("replacement conversation must supersede an existing overlapping unit")
        prior = by_id[supersedes_unit_id]
        allowed_overlap_ids = {supersedes_unit_id} | ancestors(supersedes_unit_id, by_id)
        actual_overlap_ids = {unit["generation_unit_id"] for unit in overlapping}
        if actual_overlap_ids != allowed_overlap_ids:
            raise ValueError("replacement conversation would branch or bypass the existing supersession chain")
        if latest_status(prior) != "ACCOUNT_RECORD_UNAVAILABLE":
            raise ValueError("replacement conversation requires account_record_unavailable on the prior unit")
        if proposed_work != unit_work(prior):
            raise ValueError("replacement conversation must cover exactly the prior actor/pose work")
    unit = {
        "generation_unit_id": generation_unit_id,
        "actor_id": actor_id,
        "pose_ids": pose_ids,
        "conversation_url": url,
        "registered_at": timestamp(registered_at, "registered_at"),
        "supersedes_unit_id": supersedes_unit_id,
        "attempts": [],
    }
    state["units"].append(unit)
    state["events"].append({"event": "CONVERSATION_REGISTERED", "at": registered_at, "generation_unit_id": generation_unit_id})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def find_unit(state: dict, generation_unit_id: str) -> dict:
    for unit in state["units"]:
        if unit["generation_unit_id"] == generation_unit_id:
            return unit
    raise ValueError(f"generation unit is not registered in this scene window: {generation_unit_id}")


def bind_packet(state_path: Path, generation_unit_id: str, manifest_path: Path, prepared_at: str) -> dict:
    loaded = validate_state(state_path)
    state, identity = loaded["state"], loaded["identity"]
    if state["status"] != "READY":
        raise ValueError("scene workspace must be READY before binding a packet")
    if len(loaded["report"]["unresolved_units"]) >= state["max_open_submissions"]:
        raise ValueError("scene workspace open-submission WIP limit reached")
    unit = find_unit(state, generation_unit_id)
    if any(attempt["status"] in OPEN_ATTEMPT_STATES for attempt in unit["attempts"]):
        raise ValueError("this conversation already has an unresolved attempt")
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    if manifest.get("schema") != PACKET_SCHEMA:
        raise ValueError(f"submission manifest schema must be {PACKET_SCHEMA}")
    expected = {
        "scene_id": identity["scene_id"],
        "revision": identity["revision"],
        "browser": identity["browser"],
        "generation_unit_id": unit["generation_unit_id"],
        "actor_id": unit["actor_id"],
        "pose_ids": unit["pose_ids"],
        "conversation_url": unit["conversation_url"],
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"submission manifest {key} does not match its scene-window unit")
    if manifest.get("scene_window", {}).get("sha256") != state["identity"]["sha256"]:
        raise ValueError("submission manifest does not bind this scene-window identity")
    attempt = {
        "submission_manifest": file_ref(manifest_path),
        "prepared_at": timestamp(prepared_at, "prepared_at"),
        "status": "PREPARED",
        "submission_id": None,
    }
    unit["attempts"].append(attempt)
    state["events"].append({"event": "PACKET_BOUND", "at": prepared_at, "generation_unit_id": generation_unit_id,
                            "manifest_sha256": attempt["submission_manifest"]["sha256"]})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def record_browser_health(state_path: Path, result: str, checked_at: str, evidence: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    if state["status"] in {"SUPERSEDED", "CLOSED"}:
        raise ValueError("cannot update browser health on a superseded or closed workspace")
    result = result.upper()
    if result not in {"HEALTHY", "QUARANTINED"}:
        raise ValueError("browser health result must be healthy or quarantined")
    state["browser_health"] = {
        "status": result,
        "checked_at": timestamp(checked_at, "checked_at"),
        "evidence": text(evidence, "evidence", max_length=2000),
    }
    if result == "QUARANTINED":
        state["status"] = "QUARANTINED"
    elif state["canary"]["status"] == "PASS":
        state["status"] = "READY"
    else:
        state["status"] = "DRAFT"
    state["events"].append({"event": "BROWSER_HEALTH_RECORDED", "at": checked_at, "result": result})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def record_canary(state_path: Path, result: str, checked_at: str, evidence: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    if state["status"] in {"SUPERSEDED", "CLOSED"}:
        raise ValueError("cannot record a canary on a superseded or closed workspace")
    result = result.upper()
    if result not in {"PASS", "FAIL"}:
        raise ValueError("canary result must be pass or fail")
    if result == "PASS" and state["browser_health"]["status"] != "HEALTHY":
        raise ValueError("canary PASS requires current HEALTHY browser evidence")
    state["canary"] = {
        "status": result,
        "checked_at": timestamp(checked_at, "checked_at"),
        "evidence": text(evidence, "evidence", max_length=2000),
    }
    if result == "PASS":
        state["status"] = "READY"
    else:
        state["browser_health"] = {
            "status": "QUARANTINED",
            "checked_at": checked_at,
            "evidence": evidence,
        }
        state["status"] = "QUARANTINED"
    state["events"].append({"event": "CANARY_RECORDED", "at": checked_at, "result": result})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def confirm_uploads(state_path: Path, generation_unit_id: str, confirmed_at: str, evidence: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    if state["status"] != "READY":
        raise ValueError("scene workspace must remain READY during the atomic upload segment")
    unit = find_unit(state, generation_unit_id)
    if not unit["attempts"] or unit["attempts"][-1]["status"] != "PREPARED":
        raise ValueError("only the latest PREPARED packet may confirm uploads")
    attempt = unit["attempts"][-1]
    manifest_path = checked_file_ref(attempt["submission_manifest"], "submission_manifest")
    manifest = load_json(manifest_path)
    inputs = manifest.get("uploaded_inputs")
    if not isinstance(inputs, list) or [item.get("role") for item in inputs if isinstance(item, dict)] != REFERENCE_ROLES:
        raise ValueError("packet no longer contains three independent references in exact order")
    for index, item in enumerate(inputs):
        checked_file_ref(item, f"uploaded_inputs[{index}]")
    prompt_path = checked_file_ref(manifest.get("prompt"), "prompt")
    attempt["status"] = "UPLOAD_CONFIRMED"
    attempt["upload_confirmation"] = {
        "confirmed_at": timestamp(confirmed_at, "confirmed_at"),
        "evidence": text(evidence, "evidence", max_length=2000),
        "roles": REFERENCE_ROLES,
        "sha256": [item["sha256"] for item in inputs],
        "prompt_sha256": sha256(prompt_path),
        "independent_thumbnail_count": 3,
    }
    state["events"].append({"event": "THREE_UPLOADS_CONFIRMED", "at": confirmed_at,
                            "generation_unit_id": generation_unit_id})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def mark_submitted(state_path: Path, generation_unit_id: str, submission_id: str, submitted_at: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    unit = find_unit(state, generation_unit_id)
    if state["status"] != "READY":
        raise ValueError("scene workspace must remain READY at submission")
    if not unit["attempts"] or unit["attempts"][-1]["status"] != "UPLOAD_CONFIRMED":
        raise ValueError("only a packet with three independently confirmed uploads may be submitted")
    submission_id = text(submission_id, "submission_id")
    if any(
        attempt.get("submission_id") == submission_id
        for other in state["units"] for attempt in other["attempts"]
    ):
        raise ValueError("submission_id already exists in this scene window")
    attempt = unit["attempts"][-1]
    attempt["status"] = "PENDING"
    attempt["submission_id"] = submission_id
    attempt["submitted_at"] = timestamp(submitted_at, "submitted_at")
    state["events"].append({"event": "SUBMITTED", "at": submitted_at,
                            "generation_unit_id": generation_unit_id, "submission_id": submission_id})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def cancel_prepared(state_path: Path, generation_unit_id: str, cancelled_at: str, evidence: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    unit = find_unit(state, generation_unit_id)
    if not unit["attempts"] or unit["attempts"][-1]["status"] not in {"PREPARED", "UPLOAD_CONFIRMED"}:
        raise ValueError("only the latest unsubmitted packet may be cancelled before submission")
    attempt = unit["attempts"][-1]
    attempt["status"] = "CANCELLED_BEFORE_SUBMISSION"
    attempt["resolved_at"] = timestamp(cancelled_at, "cancelled_at")
    attempt["evidence"] = text(evidence, "evidence", max_length=2000)
    state["events"].append({
        "event": "PREPARED_CANCELLED",
        "at": cancelled_at,
        "generation_unit_id": generation_unit_id,
        "manifest_sha256": attempt["submission_manifest"]["sha256"],
    })
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def resolve_attempt(state_path: Path, generation_unit_id: str, result: str, resolved_at: str, evidence: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    unit = find_unit(state, generation_unit_id)
    if not unit["attempts"] or unit["attempts"][-1]["status"] not in {"PENDING", "UNKNOWN"}:
        raise ValueError("only the latest PENDING or UNKNOWN attempt may be resolved")
    result = result.upper()
    if result not in {"UNKNOWN", "PRODUCED", "FAILED", "REFUSED", "ACCOUNT_RECORD_UNAVAILABLE"}:
        raise ValueError("result must be unknown, produced, failed, refused or account_record_unavailable")
    if unit["attempts"][-1]["status"] == "UNKNOWN" and result == "UNKNOWN":
        raise ValueError("an UNKNOWN attempt must be reconciled to a terminal result, not recorded unknown twice")
    evidence = text(evidence, "evidence", max_length=2000)
    attempt = unit["attempts"][-1]
    attempt["status"] = result
    attempt["resolved_at"] = timestamp(resolved_at, "resolved_at")
    attempt["evidence"] = evidence
    state["events"].append({"event": "RESULT_RECORDED", "at": resolved_at,
                            "generation_unit_id": generation_unit_id,
                            "submission_id": attempt["submission_id"], "result": result})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def close_window(state_path: Path, closed_at: str) -> dict:
    loaded = validate_state(state_path)
    state = loaded["state"]
    if state["status"] == "CLOSED":
        raise ValueError("scene window is already closed")
    unresolved = loaded["report"]["unresolved_units"]
    if unresolved:
        raise ValueError(f"cannot close a scene window with unresolved conversations: {unresolved}")
    state["status"] = "CLOSED"
    state["closed_at"] = timestamp(closed_at, "closed_at")
    state["events"].append({"event": "WINDOW_CLOSED", "at": closed_at})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def supersede_workspace(state_path: Path, replacement_revision: int, superseded_at: str, evidence: str) -> dict:
    loaded = validate_state(state_path)
    state, identity = loaded["state"], loaded["identity"]
    if state["status"] == "CLOSED":
        raise ValueError("closed workspace is already terminal")
    if not isinstance(replacement_revision, int) or isinstance(replacement_revision, bool) or replacement_revision <= identity["revision"]:
        raise ValueError("replacement_revision must be greater than the current revision")
    reason = text(evidence, "evidence", max_length=2000)
    at = timestamp(superseded_at, "superseded_at")
    for unit in state["units"]:
        if unit["attempts"] and unit["attempts"][-1]["status"] in {"PREPARED", "UPLOAD_CONFIRMED"}:
            attempt = unit["attempts"][-1]
            attempt["status"] = "CANCELLED_BEFORE_SUBMISSION"
            attempt["resolved_at"] = at
            attempt["evidence"] = "revision superseded before submission: " + reason
    state["status"] = "SUPERSEDED"
    state["superseded_at"] = at
    state["replacement_revision"] = replacement_revision
    state["supersession_evidence"] = reason
    state["events"].append({"event": "WORKSPACE_SUPERSEDED", "at": at,
                            "replacement_revision": replacement_revision})
    write_json_atomic(state_path, state)
    return validate_state(state_path)["report"]


def resume_entry(state_path: Path) -> dict:
    loaded = validate_state(state_path)
    state, identity, report = loaded["state"], loaded["identity"], loaded["report"]
    terminal = {"PRODUCED", "FAILED", "REFUSED", "ACCOUNT_RECORD_UNAVAILABLE", "CANCELLED_BEFORE_SUBMISSION"}
    pending_units = [
        unit["generation_unit_id"] for unit in state["units"]
        if not unit["attempts"] or unit["attempts"][-1]["status"] not in terminal
    ]
    return {
        "schema": "ndc-chatgpt-web-resume-entry/v1",
        "scene_id": identity["scene_id"],
        "revision": identity["revision"],
        "workspace_status": state["status"],
        "browser": identity["browser"],
        "ready": report["ready"],
        "unresolved_units": report["unresolved_units"],
        "pending_units": pending_units,
        "next_action": (
            "reconcile unresolved submission in its original conversation"
            if report["unresolved_units"] else
            "record browser health and one canary" if state["status"] == "DRAFT" else
            "use replacement revision only" if state["status"] == "SUPERSEDED" else
            "resume next registered unit" if state["status"] == "READY" else
            "repair or switch the quarantined browser transport" if state["status"] == "QUARANTINED" else
            "workspace complete"
        ),
        "last_event": state["events"][-1] if state["events"] else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--directory", required=True, type=Path)
    init.add_argument("--scene-id", required=True)
    init.add_argument("--revision", required=True, type=int)
    init.add_argument("--browser", required=True, choices=sorted(SUPPORTED_BROWSERS))
    init.add_argument("--window-id", required=True)
    init.add_argument("--window-label", required=True)
    init.add_argument("--created-at", required=True)
    init.add_argument("--account-profile-label")
    init.add_argument("--max-open-submissions", type=int, default=3)
    health = sub.add_parser("record-health")
    health.add_argument("--state", required=True, type=Path)
    health.add_argument("--result", required=True, choices=("healthy", "quarantined"))
    health.add_argument("--checked-at", required=True)
    health.add_argument("--evidence", required=True)
    canary = sub.add_parser("record-canary")
    canary.add_argument("--state", required=True, type=Path)
    canary.add_argument("--result", required=True, choices=("pass", "fail"))
    canary.add_argument("--checked-at", required=True)
    canary.add_argument("--evidence", required=True)
    register = sub.add_parser("register")
    register.add_argument("--state", required=True, type=Path)
    register.add_argument("--unit-id", required=True)
    register.add_argument("--actor-id", required=True)
    register.add_argument("--pose-id", required=True, action="append")
    register.add_argument("--conversation-url", required=True)
    register.add_argument("--registered-at", required=True)
    register.add_argument("--supersedes-unit-id")
    bind = sub.add_parser("bind-packet")
    bind.add_argument("--state", required=True, type=Path)
    bind.add_argument("--unit-id", required=True)
    bind.add_argument("--manifest", required=True, type=Path)
    bind.add_argument("--prepared-at", required=True)
    confirm = sub.add_parser("confirm-uploads")
    confirm.add_argument("--state", required=True, type=Path)
    confirm.add_argument("--unit-id", required=True)
    confirm.add_argument("--confirmed-at", required=True)
    confirm.add_argument("--evidence", required=True)
    submitted = sub.add_parser("mark-submitted")
    submitted.add_argument("--state", required=True, type=Path)
    submitted.add_argument("--unit-id", required=True)
    submitted.add_argument("--submission-id", required=True)
    submitted.add_argument("--submitted-at", required=True)
    cancel = sub.add_parser("cancel-prepared")
    cancel.add_argument("--state", required=True, type=Path)
    cancel.add_argument("--unit-id", required=True)
    cancel.add_argument("--cancelled-at", required=True)
    cancel.add_argument("--evidence", required=True)
    resolve = sub.add_parser("resolve")
    resolve.add_argument("--state", required=True, type=Path)
    resolve.add_argument("--unit-id", required=True)
    resolve.add_argument("--result", required=True, choices=("unknown", "produced", "failed", "refused", "account_record_unavailable"))
    resolve.add_argument("--resolved-at", required=True)
    resolve.add_argument("--evidence", required=True)
    close = sub.add_parser("close")
    close.add_argument("--state", required=True, type=Path)
    close.add_argument("--closed-at", required=True)
    supersede = sub.add_parser("supersede")
    supersede.add_argument("--state", required=True, type=Path)
    supersede.add_argument("--replacement-revision", required=True, type=int)
    supersede.add_argument("--superseded-at", required=True)
    supersede.add_argument("--evidence", required=True)
    resume = sub.add_parser("resume")
    resume.add_argument("--state", required=True, type=Path)
    validate = sub.add_parser("validate")
    validate.add_argument("--state", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = create_window(args.directory, args.scene_id, args.revision, args.browser,
                                   args.window_id, args.window_label, args.created_at, args.account_profile_label,
                                   args.max_open_submissions)
        elif args.command == "record-health":
            result = record_browser_health(args.state, args.result, args.checked_at, args.evidence)
        elif args.command == "record-canary":
            result = record_canary(args.state, args.result, args.checked_at, args.evidence)
        elif args.command == "register":
            result = register_unit(args.state, args.unit_id, args.actor_id, args.pose_id,
                                   args.conversation_url, args.registered_at, args.supersedes_unit_id)
        elif args.command == "bind-packet":
            result = bind_packet(args.state, args.unit_id, args.manifest, args.prepared_at)
        elif args.command == "confirm-uploads":
            result = confirm_uploads(args.state, args.unit_id, args.confirmed_at, args.evidence)
        elif args.command == "mark-submitted":
            result = mark_submitted(args.state, args.unit_id, args.submission_id, args.submitted_at)
        elif args.command == "cancel-prepared":
            result = cancel_prepared(args.state, args.unit_id, args.cancelled_at, args.evidence)
        elif args.command == "resolve":
            result = resolve_attempt(args.state, args.unit_id, args.result, args.resolved_at, args.evidence)
        elif args.command == "close":
            result = close_window(args.state, args.closed_at)
        elif args.command == "supersede":
            result = supersede_workspace(args.state, args.replacement_revision, args.superseded_at, args.evidence)
        elif args.command == "resume":
            result = resume_entry(args.state)
        else:
            result = validate_state(args.state)["report"]
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
