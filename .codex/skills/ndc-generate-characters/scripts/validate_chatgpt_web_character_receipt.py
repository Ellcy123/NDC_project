#!/usr/bin/env python3
"""Validate provenance for formal NDC character assets generated in ChatGPT web."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from build_chatgpt_web_character_packet import PACKET_SCHEMA, RECEIPT_SCHEMA, SUPPORTED_BROWSERS, expected_roles


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_hash(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def image_kind(path: Path) -> str | None:
    head = path.read_bytes()[:16]
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "webp"
    return None


def bound_file(entry, label: str, errors: list[str]) -> Path | None:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
        errors.append(f"{label} requires an absolute path and SHA-256")
        return None
    path = Path(entry["path"])
    if not path.is_absolute() or not path.is_file():
        errors.append(f"{label}.path must be an existing absolute file")
        return None
    path = path.resolve()
    expected = entry.get("sha256")
    if not valid_hash(expected) or sha256(path) != expected.lower():
        errors.append(f"{label}.sha256 does not match current bytes")
    return path


def validate(receipt: dict) -> dict:
    errors: list[str] = []
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append(f"schema must be {RECEIPT_SCHEMA}")
    for key, expected in {
        "backend": "chatgpt_web",
        "submission_operation": "generate_image",
        "codex_image_generation_used": False,
    }.items():
        if receipt.get(key) != expected:
            errors.append(f"{key} must equal {expected!r}")
    browser = receipt.get("browser")
    if browser not in SUPPORTED_BROWSERS:
        errors.append("browser must be one of: iab, chrome, edge")
    submission_tool = receipt.get("submission_tool")
    if submission_tool != "chatgpt_web_browser" and not (
        browser == "iab" and submission_tool == "chatgpt_web_iab"
    ):
        errors.append("submission_tool must be chatgpt_web_browser; legacy chatgpt_web_iab is valid only with browser iab")
    for key in ("task_id", "character_id", "production_revision", "asset_mode", "branch", "submission_id", "submitted_at", "completed_at"):
        if not isinstance(receipt.get(key), str) or not receipt[key].strip():
            errors.append(f"{key} is required")
    revision = receipt.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("revision must be a positive integer")
    candidate = receipt.get("candidate_index")
    if not isinstance(candidate, int) or isinstance(candidate, bool) or candidate < 0:
        errors.append("candidate_index must be a nonnegative integer")
    url = receipt.get("conversation_url")
    parsed = urlparse(url) if isinstance(url, str) else None
    host = (parsed.hostname or "").lower() if parsed else ""
    if not parsed or parsed.scheme != "https" or not (host == "chatgpt.com" or host.endswith(".chatgpt.com")):
        errors.append("conversation_url must be an https://chatgpt.com conversation")

    work_value = receipt.get("work_directory")
    work = Path(work_value).resolve() if isinstance(work_value, str) and Path(work_value).is_absolute() else None
    if work is None or not work.is_dir():
        errors.append("work_directory must be an existing absolute directory")
    manifest_path = bound_file(receipt.get("submission_manifest"), "submission_manifest", errors)
    prompt = bound_file(receipt.get("prompt"), "prompt", errors)
    manifest = None
    if manifest_path:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if manifest.get("schema") != PACKET_SCHEMA:
                errors.append("submission_manifest has unsupported schema")
            for key in ("character_id", "production_revision", "asset_mode", "branch", "revision", "conversation_url", "prompt", "uploaded_inputs"):
                if receipt.get(key) != manifest.get(key):
                    errors.append(f"receipt.{key} must exactly match submission_manifest")
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            errors.append("submission_manifest cannot be read: " + str(exc))

    inputs = receipt.get("uploaded_inputs")
    roles = [item.get("role") for item in inputs if isinstance(item, dict)] if isinstance(inputs, list) else []
    try:
        allowed = expected_roles(receipt.get("asset_mode"), receipt.get("branch"))
        if roles not in allowed:
            errors.append("uploaded_inputs roles do not match the exact mode/branch contract")
    except ValueError as exc:
        errors.append(str(exc))
        allowed = []
    if isinstance(inputs, list):
        for index, item in enumerate(inputs, start=1):
            bound_file(item, f"uploaded_inputs[{index}]", errors)
    if manifest and manifest.get("submission_order") != roles + ["full-prompt"]:
        errors.append("submission_manifest must preserve every reference then the full prompt")

    download = bound_file(receipt.get("download"), "download", errors)
    if download and image_kind(download) is None:
        errors.append("download must be an original PNG, JPEG or WebP image, not a screenshot wrapper")
    if work and download and not download.is_relative_to(work):
        errors.append("download must stay inside work_directory")
    if work and prompt and not prompt.is_relative_to(work):
        errors.append("prompt must stay inside the immutable submission packet")
    if work and isinstance(inputs, list):
        for index, item in enumerate(inputs, start=1):
            path_value = item.get("path") if isinstance(item, dict) else None
            if isinstance(path_value, str) and Path(path_value).is_absolute() and not Path(path_value).resolve().is_relative_to(work):
                errors.append(f"uploaded_inputs[{index}] must stay inside the immutable submission packet")

    return {
        "schema": "ndc-chatgpt-web-character-generation-gate/v1",
        "gate": "CHATGPT_WEB_CHARACTER_GENERATION_GATE",
        "status": "PASS" if not errors else "FAIL",
        "checks": {
            "backend": receipt.get("backend"),
            "browser": browser,
            "submission_tool": submission_tool,
            "reference_roles": roles,
            "allowed_role_sequences": allowed,
            "conversation_host": host,
            "download_kind": image_kind(download) if download else None,
            "submission_manifest_bound": manifest is not None,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.resolve().read_text(encoding="utf-8-sig"))
    result = validate(receipt)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
