"""Validate provenance for NDC character-scene generation performed in ChatGPT web."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse


SCHEMA = "ndc-chatgpt-web-generation-receipt/v2"
LEGACY_SCHEMA = "ndc-chatgpt-web-generation-receipt/v1"
ROLES = ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"]
SUPPORTED_BROWSERS = {"iab", "chrome", "edge"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_kind(path: Path) -> str | None:
    with path.open("rb") as handle:
        head = handle.read(16)
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "webp"
    return None


def resolve_file(value, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be an absolute path")
        return None
    path = Path(value)
    if not path.is_absolute():
        errors.append(f"{label} must be an absolute path")
        return None
    path = path.resolve()
    if not path.is_file():
        errors.append(f"{label} does not exist: {path}")
        return None
    return path


def valid_hash(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def check_bound_file(entry, label: str, errors: list[str]) -> Path | None:
    if not isinstance(entry, dict):
        errors.append(f"{label} must be an object")
        return None
    path = resolve_file(entry.get("path"), f"{label}.path", errors)
    expected = entry.get("sha256")
    if not valid_hash(expected):
        errors.append(f"{label}.sha256 must be a complete SHA-256")
    elif path and sha256(path) != expected.lower():
        errors.append(f"{label} SHA-256 does not match the current file")
    return path


def validate(receipt: dict, allow_legacy_v1: bool = False) -> dict:
    errors: list[str] = []
    checks: dict[str, object] = {}
    schema = receipt.get("schema")
    if schema != SCHEMA and not (allow_legacy_v1 and schema == LEGACY_SCHEMA):
        errors.append(f"schema must be {SCHEMA}; legacy v1 needs explicit audit-only allowance")
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
    for key in ("task_id", "scene_id", "submission_id", "submitted_at", "completed_at"):
        if not isinstance(receipt.get(key), str) or not receipt[key].strip():
            errors.append(f"{key} is required")
    if not isinstance(receipt.get("revision"), int) or isinstance(receipt.get("revision"), bool) or receipt["revision"] < 1:
        errors.append("revision must be a positive integer")
    poses = receipt.get("pose_ids")
    if not isinstance(poses, list) or not poses or len(poses) != len(set(poses)) or not all(isinstance(v, str) and v.strip() for v in poses):
        errors.append("pose_ids must contain distinct non-empty strings")
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

    prompt = check_bound_file(receipt.get("prompt"), "prompt", errors)
    profile = None
    manifest = None
    if schema == SCHEMA:
        profile = check_bound_file(receipt.get("importance_profile"), "importance_profile", errors)
        manifest_path = check_bound_file(receipt.get("submission_manifest"), "submission_manifest", errors)
        if manifest_path:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                if manifest.get("schema") != "ndc-chatgpt-web-submission-packet/v1":
                    errors.append("submission_manifest has unsupported schema")
                for key in ("scene_id", "revision", "pose_ids", "prompt", "importance_profile", "uploaded_inputs"):
                    if receipt.get(key) != manifest.get(key):
                        errors.append(f"receipt.{key} must exactly match submission_manifest")
                if manifest.get("submission_order") != ROLES + ["full-prompt"]:
                    errors.append("submission_manifest must preserve three references then full prompt order")
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                errors.append("submission_manifest cannot be read: " + str(exc))
    inputs = receipt.get("uploaded_inputs")
    if not isinstance(inputs, list) or [item.get("role") for item in inputs if isinstance(item, dict)] != ROLES:
        errors.append("uploaded_inputs must contain the three fixed roles in exact order")
    else:
        for index, item in enumerate(inputs, start=1):
            check_bound_file(item, f"uploaded_inputs[{index}]", errors)

    download = check_bound_file(receipt.get("download"), "download", errors)
    if download and image_kind(download) is None:
        errors.append("download must be an original PNG, JPEG or WebP image, not a screenshot wrapper")
    if work and download and not download.is_relative_to(work):
        errors.append("download must stay inside work_directory")
    if work and prompt and not prompt.is_relative_to(work):
        errors.append("prompt must stay inside the immutable submission packet")
    if work and profile and not profile.is_relative_to(work):
        errors.append("importance_profile must stay inside the immutable submission packet")

    checks.update({
        "backend": receipt.get("backend"),
        "browser": browser,
        "submission_tool": submission_tool,
        "reference_roles": ROLES,
        "conversation_host": host,
        "download_kind": image_kind(download) if download else None,
        "download_sha256": sha256(download) if download and download.is_file() else None,
        "submission_manifest_bound": manifest is not None,
        "legacy_audit_only": schema == LEGACY_SCHEMA,
    })
    return {
        "schema": "ndc-chatgpt-web-generation-gate/v1",
        "gate": "CHATGPT_WEB_GENERATION_GATE",
        "status": "PASS" if not errors else "FAIL",
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-legacy-v1", action="store_true", help="Audit old receipts only; never use for a new submission.")
    args = parser.parse_args()
    receipt_path = Path(args.receipt).resolve()
    output_path = Path(args.output).resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    result = validate(receipt, allow_legacy_v1=args.allow_legacy_v1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
