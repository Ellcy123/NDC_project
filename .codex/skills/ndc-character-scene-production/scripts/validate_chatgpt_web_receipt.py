"""Validate scene-window-bound NDC character generation provenance from ChatGPT web."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
import re
from urllib.parse import urlparse


SCHEMA = "ndc-chatgpt-web-generation-receipt/v4"
LEGACY_V3_SCHEMA = "ndc-chatgpt-web-generation-receipt/v3"
LEGACY_V2_SCHEMA = "ndc-chatgpt-web-generation-receipt/v2"
LEGACY_V1_SCHEMA = "ndc-chatgpt-web-generation-receipt/v1"
PACKET_SCHEMA = "ndc-chatgpt-web-submission-packet/v3"
LEGACY_V3_PACKET_SCHEMA = "ndc-chatgpt-web-submission-packet/v2"
LEGACY_PACKET_SCHEMA = "ndc-chatgpt-web-submission-packet/v1"
WINDOW_SCHEMA = "ndc-chatgpt-web-scene-workspace-identity/v2"
LEGACY_WINDOW_SCHEMA = "ndc-chatgpt-web-scene-window-identity/v1"
REVISION_GATE_SCHEMA = "ndc-character-scene-ready-revision-gate/v1"
CANONICAL_STYLE_SHA256 = "b1208685aa0dfdde5da5fca44dfde6f94d815c720bc55612a998d2e53859bf79"
CANONICAL_STYLE_ASSET = Path(__file__).resolve().parents[1] / "assets" / "original-user-style-description.txt"
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


def resolve_file(value: object, label: str, errors: list[str]) -> Path | None:
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


def valid_hash(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def check_bound_file(entry: object, label: str, errors: list[str]) -> Path | None:
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


def chatgpt_url(value: object) -> str | None:
    parsed = urlparse(value) if isinstance(value, str) else None
    host = (parsed.hostname or "").lower() if parsed else ""
    try:
        port = parsed.port if parsed else None
    except ValueError:
        return None
    if (
        not parsed
        or parsed.scheme != "https"
        or not (host == "chatgpt.com" or host.endswith(".chatgpt.com"))
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
    ):
        return None
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) != 2 or path_parts[0] != "c" or not path_parts[1]:
        return None
    return host


def parse_timestamp(value: object, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


def validate(receipt: dict, allow_legacy_v3: bool = False, allow_legacy_v2: bool = False,
             allow_legacy_v1: bool = False) -> dict:
    errors: list[str] = []
    checks: dict[str, object] = {}
    schema = receipt.get("schema")
    current = schema == SCHEMA
    legacy_v3 = schema == LEGACY_V3_SCHEMA
    legacy_v2 = schema == LEGACY_V2_SCHEMA
    legacy_v1 = schema == LEGACY_V1_SCHEMA
    if not current and not (legacy_v3 and allow_legacy_v3) and not (legacy_v2 and allow_legacy_v2) and not (legacy_v1 and allow_legacy_v1):
        errors.append(
            f"schema must be {SCHEMA}; legacy v3/v2/v1 need their explicit audit-only allowance"
        )
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
        (legacy_v2 or legacy_v1) and browser == "iab" and submission_tool == "chatgpt_web_iab"
    ):
        errors.append("new receipts require chatgpt_web_browser; chatgpt_web_iab is legacy iab audit only")
    for key in ("task_id", "scene_id", "submission_id"):
        if not isinstance(receipt.get(key), str) or not receipt[key].strip():
            errors.append(f"{key} is required")
    submitted_at = parse_timestamp(receipt.get("submitted_at"), "submitted_at", errors)
    completed_at = parse_timestamp(receipt.get("completed_at"), "completed_at", errors)
    if submitted_at and completed_at and completed_at < submitted_at:
        errors.append("completed_at cannot precede submitted_at")
    if not isinstance(receipt.get("revision"), int) or isinstance(receipt.get("revision"), bool) or receipt["revision"] < 1:
        errors.append("revision must be a positive integer")
    poses = receipt.get("pose_ids")
    if not isinstance(poses, list) or not poses or len(poses) != len(set(poses)) or not all(isinstance(v, str) and v.strip() for v in poses):
        errors.append("pose_ids must contain distinct non-empty strings")
    if current or legacy_v3:
        for key in ("generation_unit_id", "actor_id"):
            if not isinstance(receipt.get(key), str) or not receipt[key].strip():
                errors.append(f"{key} is required for a scene-window receipt")
    candidate = receipt.get("candidate_index")
    if not isinstance(candidate, int) or isinstance(candidate, bool) or candidate < 0:
        errors.append("candidate_index must be a nonnegative integer")

    host = chatgpt_url(receipt.get("conversation_url"))
    if host is None:
        errors.append("conversation_url must be a concrete https://chatgpt.com conversation")

    work_value = receipt.get("work_directory")
    work = Path(work_value).resolve() if isinstance(work_value, str) and Path(work_value).is_absolute() else None
    if work is None or not work.is_dir():
        errors.append("work_directory must be an existing absolute directory")

    prompt = check_bound_file(receipt.get("prompt"), "prompt", errors)
    profile = None
    manifest = None
    manifest_path = None
    style_lock = None
    window_identity = None
    window_path = None
    binding_gate_path = None
    importance_gate_path = None
    revision_gate_path = None
    if current or legacy_v3 or legacy_v2:
        profile = check_bound_file(receipt.get("importance_profile"), "importance_profile", errors)
        manifest_path = check_bound_file(receipt.get("submission_manifest"), "submission_manifest", errors)
        if manifest_path:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                expected_manifest_schema = (
                    PACKET_SCHEMA if current else
                    LEGACY_V3_PACKET_SCHEMA if legacy_v3 else
                    LEGACY_PACKET_SCHEMA
                )
                if manifest.get("schema") != expected_manifest_schema:
                    errors.append(f"submission_manifest schema must be {expected_manifest_schema}")
                fields = ["scene_id", "revision", "pose_ids", "conversation_url", "prompt", "importance_profile", "uploaded_inputs"]
                if current or legacy_v3:
                    fields += ["browser", "generation_unit_id", "actor_id", "scene_window", "style_lock"]
                if current:
                    fields += ["revision_gate", "retry_control"]
                for key in fields:
                    if receipt.get(key) != manifest.get(key):
                        errors.append(f"receipt.{key} must exactly match submission_manifest")
                if manifest.get("submission_order") != ROLES + ["full-prompt"]:
                    errors.append("submission_manifest must preserve three references then full prompt order")
                if current or legacy_v3:
                    parse_timestamp(manifest.get("prepared_at"), "submission_manifest.prepared_at", errors)
                    binding_gate_path = check_bound_file(
                        manifest.get("prompt_binding_gate"), "submission_manifest.prompt_binding_gate", errors
                    )
                    importance_gate_path = check_bound_file(
                        manifest.get("importance_gate"), "submission_manifest.importance_gate", errors
                    )
                if current:
                    revision_gate_path = check_bound_file(
                        manifest.get("revision_gate"), "submission_manifest.revision_gate", errors
                    )
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                errors.append("submission_manifest cannot be read: " + str(exc))
    if current or legacy_v3:
        style_lock = check_bound_file(receipt.get("style_lock"), "style_lock", errors)
        canonical = None
        try:
            canonical = CANONICAL_STYLE_ASSET.read_bytes()
            if hashlib.sha256(canonical).hexdigest() != CANONICAL_STYLE_SHA256:
                errors.append("bundled original user style asset differs from its locked SHA-256")
        except OSError as exc:
            errors.append("bundled original user style asset cannot be read: " + str(exc))
        if style_lock and canonical is not None and style_lock.read_bytes() != canonical:
            errors.append("style_lock must be byte-identical to the bundled original user style description")
        if prompt and canonical is not None:
            occurrences = prompt.read_bytes().count(canonical)
            checks["original_style_occurrences_in_prompt"] = occurrences
            if occurrences != 1:
                errors.append(f"prompt must contain the exact original user style bytes once; found {occurrences}")
        window_path = check_bound_file(receipt.get("scene_window"), "scene_window", errors)
        if window_path:
            try:
                window_identity = json.loads(window_path.read_text(encoding="utf-8-sig"))
                expected_window_schema = WINDOW_SCHEMA if current else LEGACY_WINDOW_SCHEMA
                if window_identity.get("schema") != expected_window_schema:
                    errors.append(f"scene_window schema must be {expected_window_schema}")
                for key in ("scene_id", "revision", "browser"):
                    if receipt.get(key) != window_identity.get(key):
                        errors.append(f"receipt.{key} must match its dedicated scene window")
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                errors.append("scene_window identity cannot be read: " + str(exc))
        if binding_gate_path:
            try:
                binding_gate = json.loads(binding_gate_path.read_text(encoding="utf-8-sig"))
                binding_checks = binding_gate.get("checks", {})
                if (
                    binding_gate.get("schema") != "ndc-prompt-style-binding-gate/v2"
                    or binding_gate.get("status") != "PASS"
                    or not prompt
                    or binding_checks.get("rendered_prompt_sha256") != sha256(prompt)
                    or binding_checks.get("canonical_style_sha256") != CANONICAL_STYLE_SHA256
                    or binding_checks.get("style_lock_sha256") != CANONICAL_STYLE_SHA256
                    or binding_checks.get("style_lock_matches_canonical_bytes") is not True
                    or binding_checks.get("original_style_occurrences") != 1
                ):
                    errors.append("prompt_binding_gate does not PASS and bind the current exact-style prompt")
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                errors.append("prompt_binding_gate cannot be read: " + str(exc))
        if importance_gate_path:
            try:
                importance_gate = json.loads(importance_gate_path.read_text(encoding="utf-8-sig"))
                if (
                    importance_gate.get("status") != "PASS"
                    or not profile
                    or importance_gate.get("profile_sha256") != sha256(profile)
                ):
                    errors.append("importance_gate does not PASS and bind the current importance profile")
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                errors.append("importance_gate cannot be read: " + str(exc))
        if current and revision_gate_path:
            try:
                revision_gate = json.loads(revision_gate_path.read_text(encoding="utf-8-sig"))
                if (
                    revision_gate.get("schema") != REVISION_GATE_SCHEMA
                    or revision_gate.get("status") != "CURRENT"
                    or revision_gate.get("unit_id") != receipt.get("scene_id")
                    or revision_gate.get("revision") != receipt.get("revision")
                ):
                    errors.append("revision_gate does not bind the current scene/revision")
                parse_timestamp(revision_gate.get("checked_at"), "revision_gate.checked_at", errors)
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                errors.append("revision_gate cannot be read: " + str(exc))

    inputs = receipt.get("uploaded_inputs")
    if not isinstance(inputs, list) or [item.get("role") for item in inputs if isinstance(item, dict)] != ROLES:
        errors.append("uploaded_inputs must contain the three fixed roles in exact order")
    else:
        for index, item in enumerate(inputs, start=1):
            input_path = check_bound_file(item, f"uploaded_inputs[{index}]", errors)
            if input_path and image_kind(input_path) is None:
                errors.append(f"uploaded_inputs[{index}] must be a PNG, JPEG or WebP image")
            if work and input_path and not input_path.is_relative_to(work):
                errors.append(f"uploaded_inputs[{index}] must stay inside the immutable submission packet")

    download = check_bound_file(receipt.get("download"), "download", errors)
    if download and image_kind(download) is None:
        errors.append("download must be an original PNG, JPEG or WebP image, not a screenshot wrapper")
    if work and download and not download.is_relative_to(work):
        errors.append("download must stay inside work_directory")
    for label, path in (
        ("prompt", prompt), ("importance_profile", profile), ("style_lock", style_lock),
        ("prompt_binding_gate", binding_gate_path), ("importance_gate", importance_gate_path),
        ("scene_window", window_path), ("submission_manifest", manifest_path),
        ("revision_gate", revision_gate_path),
    ):
        if work and path and not path.is_relative_to(work):
            errors.append(f"{label} must stay inside the immutable submission packet")

    checks.update({
        "backend": receipt.get("backend"),
        "browser": browser,
        "submission_tool": submission_tool,
        "reference_roles": ROLES,
        "conversation_host": host,
        "generation_unit_id": receipt.get("generation_unit_id"),
        "actor_id": receipt.get("actor_id"),
        "scene_window_id": window_identity.get("window_id") if isinstance(window_identity, dict) else None,
        "original_style_sha256": sha256(style_lock) if style_lock and style_lock.is_file() else None,
        "download_kind": image_kind(download) if download else None,
        "download_sha256": sha256(download) if download and download.is_file() else None,
        "submission_manifest_bound": manifest is not None,
        "legacy_audit_only": legacy_v1 or legacy_v2 or legacy_v3,
    })
    return {
        "schema": "ndc-chatgpt-web-generation-gate/v3",
        "gate": "CHATGPT_WEB_GENERATION_GATE",
        "status": "PASS" if not errors else "FAIL",
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-legacy-v3", action="store_true", help="Audit old v3 receipts only; never use for a new submission.")
    parser.add_argument("--allow-legacy-v2", action="store_true", help="Audit old v2 receipts only; never use for a new submission.")
    parser.add_argument("--allow-legacy-v1", action="store_true", help="Audit old v1 receipts only; never use for a new submission.")
    args = parser.parse_args()
    receipt_path = Path(args.receipt).resolve()
    output_path = Path(args.output).resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    result = validate(receipt, allow_legacy_v3=args.allow_legacy_v3,
                      allow_legacy_v2=args.allow_legacy_v2, allow_legacy_v1=args.allow_legacy_v1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
