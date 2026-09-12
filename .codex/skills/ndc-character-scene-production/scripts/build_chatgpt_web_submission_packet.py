#!/usr/bin/env python3
"""Build one immutable, scene-window-bound ChatGPT web submission packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from manage_scene_web_window import (
    OPEN_ATTEMPT_STATES,
    SUPPORTED_BROWSERS,
    bind_packet,
    find_unit,
    timestamp,
    validate_state,
)

SCHEMA = "ndc-chatgpt-web-submission-source/v3"
PACKET_SCHEMA = "ndc-chatgpt-web-submission-packet/v3"
RECEIPT_SCHEMA = "ndc-chatgpt-web-generation-receipt/v4"
PROMPT_GATE_SCHEMA = "ndc-prompt-style-binding-gate/v2"
REVISION_GATE_SCHEMA = "ndc-character-scene-ready-revision-gate/v1"
CANONICAL_STYLE_SHA256 = "b1208685aa0dfdde5da5fca44dfde6f94d815c720bc55612a998d2e53859bf79"
ROLES = ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_kind(path: Path) -> str | None:
    head = path.read_bytes()[:16]
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "webp"
    return None


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def source(entry: object, label: str) -> Path:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
        raise ValueError(label + " requires path and sha256")
    path = Path(entry["path"])
    if not path.is_absolute() or not path.is_file():
        raise ValueError(label + " path must be an existing absolute file")
    if sha256(path) != entry["sha256"].lower():
        raise ValueError(label + " hash does not match current bytes")
    return path.resolve()


def absolute_file(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip() or not Path(value).is_absolute():
        raise ValueError(f"{label} must be an absolute file path")
    path = Path(value).resolve()
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    return path


def build(contract_path: Path, out_dir: Path, browser: str = "iab") -> dict:
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError("browser must be one of: iab, chrome, edge")
    contract_path = contract_path.resolve()
    contract = load(contract_path)
    if contract.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    state_path = absolute_file(contract.get("scene_window_state_path"), "scene_window_state_path")
    loaded_window = validate_state(state_path)
    state = loaded_window["state"]
    identity = loaded_window["identity"]
    if state["status"] != "READY":
        raise ValueError("logical scene workspace must be READY")
    if identity["browser"] != browser:
        raise ValueError("--browser must match the dedicated scene window")

    generation_unit_id = contract.get("generation_unit_id")
    if not isinstance(generation_unit_id, str) or not generation_unit_id.strip():
        raise ValueError("generation_unit_id is required")
    unit = find_unit(state, generation_unit_id)
    if any(attempt["status"] in OPEN_ATTEMPT_STATES for attempt in unit["attempts"]):
        raise ValueError("this conversation already has an unresolved packet/submission")
    if contract.get("scene_id") != identity["scene_id"] or contract.get("revision") != identity["revision"]:
        raise ValueError("source scene_id/revision must match the dedicated scene window")
    if contract.get("actor_id") != unit["actor_id"] or contract.get("pose_ids") != unit["pose_ids"]:
        raise ValueError("source actor_id/pose_ids must match the registered conversation unit")
    prepared_at = timestamp(contract.get("prepared_at"), "prepared_at")

    revision_gate = source(contract.get("revision_gate"), "revision_gate")
    revision_record = load(revision_gate)
    if (
        revision_record.get("schema") != REVISION_GATE_SCHEMA
        or revision_record.get("status") != "CURRENT"
        or revision_record.get("unit_id") != identity["scene_id"]
        or revision_record.get("revision") != identity["revision"]
    ):
        raise ValueError("revision_gate must bind a CURRENT guard for this scene/revision")
    checked_at = timestamp(revision_record.get("checked_at"), "revision_gate.checked_at")
    prepared_dt = datetime.fromisoformat(prepared_at.replace("Z", "+00:00"))
    checked_dt = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    age_seconds = (prepared_dt - checked_dt).total_seconds()
    if age_seconds < 0 or age_seconds > 900:
        raise ValueError("revision_gate must be refreshed within 15 minutes before packet preparation")

    retry = contract.get("retry_control")
    if not isinstance(retry, dict):
        raise ValueError("retry_control is required")
    attempt_number = retry.get("attempt_number")
    tier = retry.get("defect_tier")
    repeated = retry.get("consecutive_same_defect_count")
    if not isinstance(attempt_number, int) or isinstance(attempt_number, bool) or not 1 <= attempt_number <= 6:
        raise ValueError("retry_control.attempt_number must be from 1 to 6")
    if tier not in {"H0", "H1", "H2", "H3", "INITIAL"}:
        raise ValueError("retry_control.defect_tier is invalid")
    if not isinstance(repeated, int) or isinstance(repeated, bool) or repeated < 0:
        raise ValueError("retry_control.consecutive_same_defect_count must be non-negative")
    if attempt_number >= 4 and tier != "H0":
        raise ValueError("model attempts 4-6 are reserved for H0 identity/action/structure defects")
    if repeated >= 2 and retry.get("method_changed") is not True:
        raise ValueError("the same defect repeated twice; change method or package the scene before another submission")
    if repeated > 0 and not isinstance(retry.get("defect_id"), str):
        raise ValueError("retry_control.defect_id is required for a repeated defect")

    inputs = contract.get("uploaded_inputs")
    if not isinstance(inputs, list) or [v.get("role") for v in inputs if isinstance(v, dict)] != ROLES:
        raise ValueError("uploaded_inputs must contain the three roles in exact order")
    input_paths = [source(entry, f"uploaded_inputs[{index}]") for index, entry in enumerate(inputs, start=1)]
    for index, path in enumerate(input_paths, start=1):
        if image_kind(path) is None:
            raise ValueError(f"uploaded_inputs[{index}] must be a PNG, JPEG or WebP image")
    prompt = source(contract.get("prompt"), "prompt")
    binding_gate = source(contract.get("prompt_binding_gate"), "prompt_binding_gate")
    profile = source(contract.get("importance_profile"), "importance_profile")
    importance_gate = source(contract.get("importance_gate"), "importance_gate")

    binding = load(binding_gate)
    checks = binding.get("checks", {})
    if (
        binding.get("schema") != PROMPT_GATE_SCHEMA
        or binding.get("status") != "PASS"
        or checks.get("rendered_prompt_sha256") != sha256(prompt)
        or checks.get("canonical_style_sha256") != CANONICAL_STYLE_SHA256
        or checks.get("style_lock_sha256") != CANONICAL_STYLE_SHA256
        or checks.get("style_lock_matches_canonical_bytes") is not True
        or checks.get("original_style_occurrences") != 1
    ):
        raise ValueError("prompt binding gate does not bind the current prompt to the exact original user style bytes")
    style_lock_path = absolute_file(binding.get("style_lock_path"), "prompt_binding_gate.style_lock_path")
    if sha256(style_lock_path) != CANONICAL_STYLE_SHA256:
        raise ValueError("prompt binding gate style file no longer matches the original user style")
    importance = load(importance_gate)
    if importance.get("status") != "PASS" or importance.get("profile_sha256") != sha256(profile):
        raise ValueError("importance gate does not PASS and bind the current profile")

    if out_dir.exists() and any(out_dir.iterdir()):
        raise ValueError("output directory must be absent or empty; never overwrite a submission packet")
    out_dir.mkdir(parents=True, exist_ok=True)
    scene_window_target = out_dir / "00_scene-window-identity.json"
    shutil.copy2(loaded_window["identity_path"], scene_window_target)
    copied = []
    for index, (entry, path) in enumerate(zip(inputs, input_paths), start=1):
        target = out_dir / f"0{index}_{entry['role']}{path.suffix.lower()}"
        shutil.copy2(path, target)
        copied.append({"role": entry["role"], "path": str(target.resolve()), "sha256": sha256(target)})
    prompt_target = out_dir / "04_full-prompt.txt"
    profile_target = out_dir / "05_importance-profile.json"
    binding_target = out_dir / "06_prompt-binding-gate.json"
    importance_target = out_dir / "07_importance-gate.json"
    style_target = out_dir / "08_original-user-style-description.txt"
    revision_target = out_dir / "09_ready-revision-gate.json"
    for src, dst in (
        (prompt, prompt_target),
        (profile, profile_target),
        (binding_gate, binding_target),
        (importance_gate, importance_target),
        (style_lock_path, style_target),
        (revision_gate, revision_target),
    ):
        shutil.copy2(src, dst)

    manifest = {
        "schema": PACKET_SCHEMA,
        "scene_id": identity["scene_id"],
        "revision": identity["revision"],
        "browser": browser,
        "generation_unit_id": generation_unit_id,
        "actor_id": unit["actor_id"],
        "pose_ids": unit["pose_ids"],
        "conversation_url": unit["conversation_url"],
        "prepared_at": prepared_at,
        "scene_window": {"path": str(scene_window_target.resolve()), "sha256": sha256(scene_window_target)},
        "submission_order": ROLES + ["full-prompt"],
        "uploaded_inputs": copied,
        "prompt": {"path": str(prompt_target.resolve()), "sha256": sha256(prompt_target)},
        "style_lock": {"path": str(style_target.resolve()), "sha256": sha256(style_target)},
        "importance_profile": {"path": str(profile_target.resolve()), "sha256": sha256(profile_target)},
        "prompt_binding_gate": {"path": str(binding_target.resolve()), "sha256": sha256(binding_target)},
        "importance_gate": {"path": str(importance_target.resolve()), "sha256": sha256(importance_target)},
        "revision_gate": {"path": str(revision_target.resolve()), "sha256": sha256(revision_target)},
        "retry_control": retry,
    }
    manifest_path = out_dir / "submission-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "backend": "chatgpt_web",
        "browser": browser,
        "submission_tool": "chatgpt_web_browser",
        "submission_operation": "generate_image",
        "codex_image_generation_used": False,
        "task_id": "FILL_AFTER_SUBMISSION",
        "scene_id": identity["scene_id"],
        "revision": identity["revision"],
        "generation_unit_id": generation_unit_id,
        "actor_id": unit["actor_id"],
        "pose_ids": unit["pose_ids"],
        "submission_id": "FILL_AFTER_SUBMISSION",
        "submitted_at": "FILL_AFTER_SUBMISSION",
        "completed_at": "FILL_AFTER_SUBMISSION",
        "conversation_url": unit["conversation_url"],
        "candidate_index": 0,
        "work_directory": str(out_dir.resolve()),
        "scene_window": manifest["scene_window"],
        "submission_manifest": {"path": str(manifest_path.resolve()), "sha256": sha256(manifest_path)},
        "prompt": manifest["prompt"],
        "style_lock": manifest["style_lock"],
        "importance_profile": manifest["importance_profile"],
        "revision_gate": manifest["revision_gate"],
        "retry_control": manifest["retry_control"],
        "uploaded_inputs": copied,
        "download": {"path": "FILL_AFTER_DOWNLOAD", "sha256": "FILL_AFTER_DOWNLOAD"},
    }
    receipt_path = out_dir / "receipt-draft.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    window_report = bind_packet(state_path, generation_unit_id, manifest_path, prepared_at)
    return {
        "packet": str(out_dir.resolve()),
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": sha256(manifest_path),
        "receipt_draft": str(receipt_path.resolve()),
        "submission_order": manifest["submission_order"],
        "scene_window_state": str(state_path),
        "parallel_unresolved_count": window_report["parallel_unresolved_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--browser", choices=sorted(SUPPORTED_BROWSERS), default="iab")
    args = parser.parse_args()
    try:
        result = build(args.contract.resolve(), args.out_dir.resolve(), args.browser)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    print(json.dumps({"status": "PASS", **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
