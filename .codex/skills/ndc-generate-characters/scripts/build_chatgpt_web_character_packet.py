#!/usr/bin/env python3
"""Build a hash-bound ChatGPT web packet for one formal NDC character asset submission."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "ndc-chatgpt-web-character-submission-source/v1"
PACKET_SCHEMA = "ndc-chatgpt-web-character-submission-packet/v1"
RECEIPT_SCHEMA = "ndc-chatgpt-web-character-generation-receipt/v1"
SUPPORTED_BROWSERS = {"iab", "chrome", "edge"}

ROLE_SEQUENCES = {
    ("general-style-fullbody", "mj-conversion"): [
        ["approved-mj-stage-fullbody", "general-fullbody-style-reference"],
        ["approved-mj-stage-fullbody", "same-source-face-anchor", "general-fullbody-style-reference"],
    ],
    ("general-style-fullbody", "secondary-direct"): [
        ["general-fullbody-style-reference"],
    ],
    ("general-character-card", "default-whole-card"): [
        ["approved-general-style-fullbody"],
        ["approved-general-style-fullbody", "same-source-face-anchor"],
    ],
    ("general-character-card", "modular-component"): [
        ["approved-general-style-fullbody"],
        ["approved-general-style-fullbody", "same-source-face-anchor"],
        ["approved-general-style-fullbody", "approved-same-group-front-module"],
        ["approved-general-style-fullbody", "same-source-face-anchor", "approved-same-group-front-module"],
    ],
    ("black-white-red-character-card", "animation-card"): [
        ["approved-general-character-card", "black-white-red-style-reference"],
    ],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def bound_file(entry, label: str) -> Path:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
        raise ValueError(label + " requires path and sha256")
    path = Path(entry["path"])
    if not path.is_absolute() or not path.is_file():
        raise ValueError(label + " path must be an existing absolute file")
    if sha256(path) != entry["sha256"].lower():
        raise ValueError(label + " hash does not match current bytes")
    return path


def is_supported_image(path: Path) -> bool:
    head = path.read_bytes()[:16]
    return (
        head.startswith(b"\x89PNG\r\n\x1a\n")
        or head.startswith(b"\xff\xd8\xff")
        or (head.startswith(b"RIFF") and head[8:12] == b"WEBP")
    )


def expected_roles(asset_mode: str, branch: str) -> list[list[str]]:
    sequences = ROLE_SEQUENCES.get((asset_mode, branch))
    if sequences is None:
        allowed = ", ".join(f"{mode}/{route}" for mode, route in ROLE_SEQUENCES)
        raise ValueError(f"unsupported asset_mode/branch; allowed: {allowed}")
    return sequences


def build(contract_path: Path, out_dir: Path, browser: str = "iab") -> dict:
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError("browser must be one of: iab, chrome, edge")
    contract = load(contract_path)
    if contract.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    for key in ("character_id", "production_revision", "asset_mode", "branch"):
        if not isinstance(contract.get(key), str) or not contract[key].strip():
            raise ValueError(f"{key} is required")
    revision = contract.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ValueError("revision must be a positive integer")
    conversation_url = contract.get("conversation_url")
    parsed = urlparse(conversation_url) if isinstance(conversation_url, str) else None
    host = (parsed.hostname or "").lower() if parsed else ""
    if not parsed or parsed.scheme != "https" or not (host == "chatgpt.com" or host.endswith(".chatgpt.com")):
        raise ValueError("conversation_url must be an https://chatgpt.com conversation")

    inputs = contract.get("uploaded_inputs")
    roles = [item.get("role") for item in inputs if isinstance(item, dict)] if isinstance(inputs, list) else []
    allowed = expected_roles(contract["asset_mode"], contract["branch"])
    if roles not in allowed:
        expected = " or ".join(" -> ".join(sequence) for sequence in allowed)
        raise ValueError(f"uploaded_inputs roles must be exactly: {expected}")
    input_paths = [bound_file(entry, f"uploaded_inputs[{index}]") for index, entry in enumerate(inputs, start=1)]
    if any(not is_supported_image(path) for path in input_paths):
        raise ValueError("every uploaded input must be a PNG, JPEG or WebP image")
    prompt = bound_file(contract.get("prompt"), "prompt")
    if not prompt.read_text(encoding="utf-8-sig").strip():
        raise ValueError("prompt must contain the complete non-empty submission text")

    if out_dir.exists() and any(out_dir.iterdir()):
        raise ValueError("output directory must be absent or empty; never overwrite a submission packet")
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for index, (entry, path) in enumerate(zip(inputs, input_paths), start=1):
        target = out_dir / f"{index:02d}_{entry['role']}{path.suffix.lower()}"
        shutil.copy2(path, target)
        copied.append({"role": entry["role"], "path": str(target.resolve()), "sha256": sha256(target)})
    prompt_target = out_dir / f"{len(copied) + 1:02d}_full-prompt.txt"
    shutil.copy2(prompt, prompt_target)

    manifest = {
        "schema": PACKET_SCHEMA,
        "character_id": contract["character_id"],
        "production_revision": contract["production_revision"],
        "asset_mode": contract["asset_mode"],
        "branch": contract["branch"],
        "revision": revision,
        "conversation_url": conversation_url,
        "submission_order": roles + ["full-prompt"],
        "uploaded_inputs": copied,
        "prompt": {"path": str(prompt_target.resolve()), "sha256": sha256(prompt_target)},
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
        "character_id": contract["character_id"],
        "production_revision": contract["production_revision"],
        "asset_mode": contract["asset_mode"],
        "branch": contract["branch"],
        "revision": revision,
        "submission_id": "FILL_AFTER_SUBMISSION",
        "submitted_at": "FILL_AFTER_SUBMISSION",
        "completed_at": "FILL_AFTER_SUBMISSION",
        "conversation_url": conversation_url,
        "candidate_index": 0,
        "work_directory": str(out_dir.resolve()),
        "submission_manifest": {"path": str(manifest_path.resolve()), "sha256": sha256(manifest_path)},
        "prompt": manifest["prompt"],
        "uploaded_inputs": copied,
        "download": {"path": "FILL_AFTER_DOWNLOAD", "sha256": "FILL_AFTER_DOWNLOAD"},
    }
    receipt_path = out_dir / "receipt-draft.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "packet": str(out_dir.resolve()),
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": sha256(manifest_path),
        "receipt_draft": str(receipt_path.resolve()),
        "submission_order": manifest["submission_order"],
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
