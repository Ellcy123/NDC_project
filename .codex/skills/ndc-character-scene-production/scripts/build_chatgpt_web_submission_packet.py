#!/usr/bin/env python3
"""Build a hash-bound, fixed-order ChatGPT web submission packet for one scene revision."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

SCHEMA = "ndc-chatgpt-web-submission-source/v1"
ROLES = ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"]
SUPPORTED_BROWSERS = {"iab", "chrome", "edge"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def source(entry, label: str) -> Path:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
        raise ValueError(label + " requires path and sha256")
    path = Path(entry["path"])
    if not path.is_absolute() or not path.is_file():
        raise ValueError(label + " path must be an existing absolute file")
    if sha256(path) != entry["sha256"].lower():
        raise ValueError(label + " hash does not match current bytes")
    return path


def build(contract_path: Path, out_dir: Path, browser: str = "iab") -> dict:
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError("browser must be one of: iab, chrome, edge")
    contract = load(contract_path)
    if contract.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    if not isinstance(contract.get("scene_id"), str) or not contract["scene_id"].strip():
        raise ValueError("scene_id is required")
    if not isinstance(contract.get("revision"), int) or isinstance(contract.get("revision"), bool) or contract["revision"] < 1:
        raise ValueError("revision must be positive")
    poses = contract.get("pose_ids")
    if not isinstance(poses, list) or not poses or len(poses) != len(set(poses)) or not all(isinstance(v, str) and v.strip() for v in poses):
        raise ValueError("pose_ids must contain distinct non-empty strings")

    inputs = contract.get("uploaded_inputs")
    if not isinstance(inputs, list) or [v.get("role") for v in inputs if isinstance(v, dict)] != ROLES:
        raise ValueError("uploaded_inputs must contain the three roles in exact order")
    input_paths = [source(entry, f"uploaded_inputs[{index}]") for index, entry in enumerate(inputs, start=1)]
    prompt = source(contract.get("prompt"), "prompt")
    binding_gate = source(contract.get("prompt_binding_gate"), "prompt_binding_gate")
    profile = source(contract.get("importance_profile"), "importance_profile")
    importance_gate = source(contract.get("importance_gate"), "importance_gate")

    binding = load(binding_gate)
    if binding.get("status") != "PASS" or binding.get("checks", {}).get("rendered_prompt_sha256") != sha256(prompt):
        raise ValueError("prompt binding gate does not PASS and bind the current full prompt")
    importance = load(importance_gate)
    if importance.get("status") != "PASS" or importance.get("profile_sha256") != sha256(profile):
        raise ValueError("importance gate does not PASS and bind the current profile")

    if out_dir.exists() and any(out_dir.iterdir()):
        raise ValueError("output directory must be absent or empty; never overwrite a submission packet")
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for index, (entry, path) in enumerate(zip(inputs, input_paths), start=1):
        target = out_dir / f"0{index}_{entry['role']}{path.suffix.lower()}"
        shutil.copy2(path, target)
        copied.append({"role": entry["role"], "path": str(target.resolve()), "sha256": sha256(target)})
    prompt_target = out_dir / "04_full-prompt.txt"
    profile_target = out_dir / "05_importance-profile.json"
    binding_target = out_dir / "06_prompt-binding-gate.json"
    importance_target = out_dir / "07_importance-gate.json"
    for src, dst in ((prompt, prompt_target), (profile, profile_target), (binding_gate, binding_target), (importance_gate, importance_target)):
        shutil.copy2(src, dst)

    manifest = {
        "schema": "ndc-chatgpt-web-submission-packet/v1",
        "scene_id": contract["scene_id"], "revision": contract["revision"], "pose_ids": poses,
        "conversation_url": contract.get("conversation_url"),
        "submission_order": ROLES + ["full-prompt"],
        "uploaded_inputs": copied,
        "prompt": {"path": str(prompt_target.resolve()), "sha256": sha256(prompt_target)},
        "importance_profile": {"path": str(profile_target.resolve()), "sha256": sha256(profile_target)},
        "prompt_binding_gate": {"path": str(binding_target.resolve()), "sha256": sha256(binding_target)},
        "importance_gate": {"path": str(importance_target.resolve()), "sha256": sha256(importance_target)},
    }
    manifest_path = out_dir / "submission-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "ndc-chatgpt-web-generation-receipt/v2", "backend": "chatgpt_web", "browser": browser,
        "submission_tool": "chatgpt_web_browser", "submission_operation": "generate_image",
        "codex_image_generation_used": False, "task_id": "FILL_AFTER_SUBMISSION",
        "scene_id": contract["scene_id"], "revision": contract["revision"], "pose_ids": poses,
        "submission_id": "FILL_AFTER_SUBMISSION", "submitted_at": "FILL_AFTER_SUBMISSION",
        "completed_at": "FILL_AFTER_SUBMISSION", "conversation_url": contract.get("conversation_url"),
        "candidate_index": 0, "work_directory": str(out_dir.resolve()),
        "submission_manifest": {"path": str(manifest_path.resolve()), "sha256": sha256(manifest_path)},
        "prompt": manifest["prompt"], "importance_profile": manifest["importance_profile"],
        "uploaded_inputs": copied,
        "download": {"path": "FILL_AFTER_DOWNLOAD", "sha256": "FILL_AFTER_DOWNLOAD"},
    }
    receipt_path = out_dir / "receipt-draft.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"packet": str(out_dir.resolve()), "manifest": str(manifest_path.resolve()),
            "manifest_sha256": sha256(manifest_path), "receipt_draft": str(receipt_path.resolve()),
            "submission_order": manifest["submission_order"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--browser", choices=sorted(SUPPORTED_BROWSERS), default="iab")
    args = parser.parse_args()
    try:
        result = build(args.contract.resolve(), args.out_dir.resolve(), args.browser)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"FAIL", "errors":[str(exc)]}, ensure_ascii=False))
        return 2
    print(json.dumps({"status":"PASS", **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
