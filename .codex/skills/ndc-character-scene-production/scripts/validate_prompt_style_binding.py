#!/usr/bin/env python3
"""Fail closed unless a web prompt contains the user's original style bytes exactly once."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "ndc-prompt-style-binding/v2"
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
ORIGINAL_STYLE_MARKERS = (
    "highly stylized graphic illustration",
    "outer silhouette contour::1.5",
    "American 1928s era context",
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_STYLE_ASSET = SKILL_ROOT / "assets" / "original-user-style-description.txt"
CANONICAL_STYLE_MANIFEST = SKILL_ROOT / "assets" / "original-user-style-description.manifest.json"
CANONICAL_STYLE_SHA256 = "b1208685aa0dfdde5da5fca44dfde6f94d815c720bc55612a998d2e53859bf79"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: object, contract: Path, name: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing {name}")
        return None
    path = Path(value)
    if not path.is_absolute():
        path = contract.parent / path
    path = path.resolve()
    if not path.is_file():
        errors.append(f"{name} is not a readable file: {path}")
        return None
    return path


def canonical_style(errors: list[str], checks: dict[str, object]) -> bytes | None:
    try:
        canonical = CANONICAL_STYLE_ASSET.read_bytes()
        manifest = load_json(CANONICAL_STYLE_MANIFEST)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"canonical style asset cannot be read: {exc}")
        return None
    actual_hash = hashlib.sha256(canonical).hexdigest()
    checks["canonical_style_asset"] = str(CANONICAL_STYLE_ASSET)
    checks["canonical_style_sha256"] = actual_hash
    checks["canonical_terminal_bytes"] = list(canonical[-4:])
    if actual_hash != CANONICAL_STYLE_SHA256:
        errors.append("bundled original user style bytes differ from the validator constant")
    if manifest.get("schema") != "ndc-original-user-style-description/v1":
        errors.append("canonical style manifest schema is invalid")
    if manifest.get("sha256") != actual_hash:
        errors.append("canonical style manifest hash differs from the text asset")
    if not canonical.endswith(b",\xc2\xa0\n"):
        errors.append("canonical style asset lost its original comma, NBSP, LF ending")
    try:
        canonical.decode("utf-8")
    except UnicodeDecodeError:
        errors.append("canonical style asset is not strict UTF-8")
        return None
    return canonical


def validate_contract(contract_path: Path) -> dict:
    errors: list[str] = []
    checks: dict[str, object] = {}
    contract_path = contract_path.resolve()
    try:
        contract = load_json(contract_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "schema": "ndc-prompt-style-binding-gate/v2",
            "status": "FAIL",
            "PROMPT_STYLE_BINDING_GATE": "FAIL",
            "contract": str(contract_path),
            "checks": checks,
            "errors": [str(exc)],
        }

    if contract.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    canonical = canonical_style(errors, checks)
    lock_path = resolve(contract.get("style_lock_path"), contract_path, "style_lock_path", errors)
    prompt_path = resolve(contract.get("rendered_prompt_path"), contract_path, "rendered_prompt_path", errors)
    expected_hash = contract.get("fixed_style_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
        errors.append("fixed_style_sha256 must be a 64-hex SHA-256")
    elif expected_hash.lower() != CANONICAL_STYLE_SHA256:
        errors.append("fixed_style_sha256 must equal the bundled original user style hash")

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

    lock_bytes = prompt_bytes = None
    if lock_path:
        lock_bytes = lock_path.read_bytes()
        actual_hash = hashlib.sha256(lock_bytes).hexdigest()
        checks["style_lock_sha256"] = actual_hash
        checks["style_lock_matches_canonical_bytes"] = canonical is not None and lock_bytes == canonical
        if canonical is not None and lock_bytes != canonical:
            errors.append("style_lock_path must be byte-identical to the bundled original user style asset")
        try:
            lock_bytes.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("style_lock_path must be strict UTF-8")
    if prompt_path:
        prompt_bytes = prompt_path.read_bytes()
        checks["rendered_prompt_sha256"] = hashlib.sha256(prompt_bytes).hexdigest()
        try:
            prompt_bytes.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("rendered_prompt_path must be strict UTF-8")

    if canonical is not None and prompt_bytes is not None:
        occurrences = prompt_bytes.count(canonical)
        checks["original_style_occurrences"] = occurrences
        if occurrences != 1:
            errors.append(f"rendered prompt must contain the original user style bytes exactly once; found {occurrences}")
        outside_bytes = prompt_bytes.replace(canonical, b"")
        try:
            outside_lock = outside_bytes.decode("utf-8")
        except UnicodeDecodeError:
            outside_lock = ""
        duplicate_markers = sorted(marker for marker in ORIGINAL_STYLE_MARKERS if marker in outside_lock)
        checks["original_style_markers_outside_lock"] = duplicate_markers
        if duplicate_markers:
            errors.append(f"a second or rewritten original-style description appears outside the lock: {duplicate_markers}")
        drift_terms = sorted(set(match.group(0) for match in FORBIDDEN_OUTSIDE_LOCK.finditer(outside_lock)))
        checks["forbidden_terms_outside_lock"] = drift_terms
        if drift_terms:
            errors.append(f"forbidden style-drift terms outside original style block: {drift_terms}")

    return {
        "schema": "ndc-prompt-style-binding-gate/v2",
        "status": "PASS" if not errors else "FAIL",
        "PROMPT_STYLE_BINDING_GATE": "PASS" if not errors else "FAIL",
        "contract": str(contract_path),
        "style_lock_path": str(lock_path) if lock_path else None,
        "rendered_prompt_path": str(prompt_path) if prompt_path else None,
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = validate_contract(args.contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
