#!/usr/bin/env python3
"""Fail-closed pre-submission binding check for formal scene prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "ndc-prompt-style-binding/v1"
REQUIRED_ROLES = ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"]
ALLOWED_DYNAMIC_FIELDS = {
    "character", "whitebox_id", "camera_orientation", "visible_action",
    "support_contact", "visible_detail", "geometry",
}
FORBIDDEN_DYNAMIC_KEYS = {"style", "texture", "brushwork", "line_language", "lighting_style"}
FORBIDDEN_OUTSIDE_LOCK = re.compile(
    r"\b(?:photoreal(?:istic|ism)?|semi-realistic|generic realism|studio(?:\s+background)?|"
    r"bloom|lens flare|glossy|airbrush(?:ed)?|smooth gradient|3d render)\b",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("contract must be a JSON object")
    return value


def resolve(value: object, contract: Path, name: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing {name}")
        return None
    path = Path(value)
    if not path.is_absolute():
        path = contract.parent / path
    if not path.is_file():
        errors.append(f"{name} is not a readable file: {path}")
        return None
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    checks: dict[str, object] = {}
    contract_path = args.contract.resolve()
    try:
        contract = load_json(contract_path)
    except Exception as exc:  # pragma: no cover - safe evidence emission
        payload = {"schema": "ndc-prompt-style-binding-gate/v1", "status": "FAIL", "errors": [str(exc)]}
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2

    if contract.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    lock_path = resolve(contract.get("style_lock_path"), contract_path, "style_lock_path", errors)
    prompt_path = resolve(contract.get("rendered_prompt_path"), contract_path, "rendered_prompt_path", errors)
    expected_hash = contract.get("fixed_style_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
        errors.append("fixed_style_sha256 must be a 64-hex SHA-256")

    roles = contract.get("reference_roles")
    checks["reference_roles"] = roles
    if roles != REQUIRED_ROLES:
        errors.append(f"reference_roles must exactly equal {REQUIRED_ROLES}")

    dynamic = contract.get("dynamic_fields")
    if not isinstance(dynamic, dict) or not dynamic:
        errors.append("dynamic_fields must be a non-empty object")
    else:
        unknown = sorted(set(dynamic) - ALLOWED_DYNAMIC_FIELDS)
        prohibited = sorted(set(dynamic) & FORBIDDEN_DYNAMIC_KEYS)
        if unknown:
            errors.append(f"dynamic_fields contain unapproved keys: {unknown}")
        if prohibited:
            errors.append(f"dynamic_fields contain style keys: {prohibited}")
        empty = sorted(key for key, value in dynamic.items() if not isinstance(value, str) or not value.strip())
        if empty:
            errors.append(f"dynamic_fields contain empty/non-text values: {empty}")

    style_text = prompt_text = None
    if lock_path:
        style_text = lock_path.read_text(encoding="utf-8")
        actual_hash = sha256(lock_path)
        checks["style_lock_sha256"] = actual_hash
        if actual_hash.lower() != str(expected_hash).lower():
            errors.append("fixed style hash does not match style_lock_path bytes")
        if not style_text.strip():
            errors.append("style_lock_path is empty")
    if prompt_path:
        prompt_text = prompt_path.read_text(encoding="utf-8")
        checks["rendered_prompt_sha256"] = sha256(prompt_path)
    if style_text is not None and prompt_text is not None:
        occurrences = prompt_text.count(style_text)
        checks["fixed_style_occurrences"] = occurrences
        if occurrences != 1:
            errors.append(f"rendered prompt must contain fixed style block exactly once; found {occurrences}")
        outside_lock = prompt_text.replace(style_text, "")
        drift_terms = sorted(set(match.group(0) for match in FORBIDDEN_OUTSIDE_LOCK.finditer(outside_lock)))
        checks["forbidden_terms_outside_lock"] = drift_terms
        if drift_terms:
            errors.append(f"forbidden style-drift terms outside fixed lock: {drift_terms}")

    payload = {
        "schema": "ndc-prompt-style-binding-gate/v1",
        "status": "PASS" if not errors else "FAIL",
        "PROMPT_STYLE_BINDING_GATE": "PASS" if not errors else "FAIL",
        "contract": str(contract_path),
        "style_lock_path": str(lock_path) if lock_path else None,
        "rendered_prompt_path": str(prompt_path) if prompt_path else None,
        "checks": checks,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
