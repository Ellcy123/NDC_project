#!/usr/bin/env python3
"""Fail-closed preflight for non-generative contextual character extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


CONTRACT_SCHEMA = "ndc-non-generative-extraction-capability/v1"
SNAPSHOT_SCHEMA = "ndc-photoshop-execution-capabilities/v1"
METHODS = {
    "selection_to_layer_mask": {
        "subject_selection": ("subject_selection", ("select", "subject")),
        "selection_to_mask": ("selection_to_layer_mask", ("mask", "selection")),
        "rgba_export": ("rgba_export", ("export",)),
    },
}
BLOCKING_STATUSES = {"requires_user", "unavailable", "unverified", "experimental"}
ACTION_CANDIDATE_COMMAND_IDS = {"action.play"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: object, contract_path: Path, field: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing {field}")
        return None
    path = Path(value)
    if not path.is_absolute():
        path = contract_path.parent / path
    if not path.is_file():
        errors.append(f"{field} is not a readable file: {path}")
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
        contract = read_object(contract_path)
    except Exception as exc:  # Safe evidence emission even for malformed input.
        payload = {
            "schema": "ndc-extraction-capability-gate/v1",
            "status": "FAIL",
            "EXTRACTION_CAPABILITY_GATE": "FAIL",
            "errors": [str(exc)],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2

    if contract.get("schema") != CONTRACT_SCHEMA:
        errors.append(f"schema must be {CONTRACT_SCHEMA}")
    if contract.get("route") != "photoshop_non_generative":
        errors.append("route must be photoshop_non_generative")
    method = contract.get("method")
    if method not in METHODS:
        errors.append(f"method must be one of {sorted(METHODS)}")
        method = None

    source_path = resolve(contract.get("source_candidate_path"), contract_path, "source_candidate_path", errors)
    expected_hash = contract.get("source_candidate_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        errors.append("source_candidate_sha256 must be 64 lowercase hexadecimal characters")
    elif source_path:
        actual_hash = sha256(source_path)
        checks["source_candidate_sha256"] = actual_hash
        if actual_hash != expected_hash:
            errors.append("source candidate SHA-256 does not match the bound source")

    snapshot_path = resolve(contract.get("capability_snapshot_path"), contract_path, "capability_snapshot_path", errors)
    snapshot: dict = {}
    if snapshot_path:
        try:
            snapshot = read_object(snapshot_path)
        except Exception as exc:
            errors.append(str(exc))
        else:
            if snapshot.get("schema") != SNAPSHOT_SCHEMA:
                errors.append(f"capability snapshot schema must be {SNAPSHOT_SCHEMA}")
            if not isinstance(snapshot.get("session_id"), str) or not snapshot["session_id"].strip():
                errors.append("capability snapshot must identify the current session")
            if not isinstance(snapshot.get("captured_at"), str) or not snapshot["captured_at"].strip():
                errors.append("capability snapshot must include captured_at")

    catalog_commands: dict[str, dict] = {}
    if snapshot_path and isinstance(snapshot, dict):
        catalog_path = resolve(snapshot.get("catalog_path"), snapshot_path, "catalog_path", errors)
        expected_catalog_hash = snapshot.get("catalog_sha256")
        if not isinstance(expected_catalog_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_catalog_hash):
            errors.append("catalog_sha256 must be 64 lowercase hexadecimal characters")
        elif catalog_path:
            actual_catalog_hash = sha256(catalog_path)
            checks["catalog_sha256"] = actual_catalog_hash
            if actual_catalog_hash != expected_catalog_hash:
                errors.append("catalog SHA-256 does not match catalog_path bytes")
        if catalog_path:
            try:
                raw_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
                if not isinstance(raw_catalog, list):
                    raise ValueError("catalog must be a JSON list")
                for entry in raw_catalog:
                    if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                        catalog_commands[entry["id"]] = entry
            except Exception as exc:
                errors.append(f"could not read current command catalog: {exc}")

    operations = contract.get("operations")
    if not isinstance(operations, dict):
        errors.append("operations must be an object")
        operations = {}
    required_operations = METHODS.get(method, {})
    missing_operations = [
        name for name, (effect, _) in required_operations.items()
        if not isinstance(operations.get(name), dict)
        or not isinstance(operations[name].get("command_id"), str)
        or not operations[name]["command_id"].strip()
        or operations[name].get("effect") != effect
    ]
    if missing_operations:
        errors.append(f"missing operation command IDs: {missing_operations}")

    requirements = contract.get("output_requirements")
    expected_requirements = {"format": "png", "alpha": True, "no_generated_pixels": True}
    if requirements != expected_requirements:
        errors.append(f"output_requirements must exactly equal {expected_requirements}")

    command_statuses: dict[str, str] = {}
    command_descriptions: dict[str, str] = {}
    commands = snapshot.get("commands") if isinstance(snapshot, dict) else None
    if not isinstance(commands, list):
        errors.append("capability snapshot commands must be a list")
    else:
        for command in commands:
            if isinstance(command, dict) and isinstance(command.get("id"), str) and isinstance(command.get("status"), str):
                command_statuses[command["id"]] = command["status"]
                if isinstance(command.get("description"), str):
                    command_descriptions[command["id"]] = command["description"]
    checks["command_statuses"] = command_statuses

    for operation, (_, terms) in required_operations.items():
        operation_spec = operations.get(operation)
        if not isinstance(operation_spec, dict):
            continue
        command_id = operation_spec.get("command_id")
        if not isinstance(command_id, str) or not command_id.strip():
            continue
        if command_id in ACTION_CANDIDATE_COMMAND_IDS:
            errors.append(
                f"{operation} cannot use {command_id}: installed Photoshop actions are "
                "candidate trials, not verified subject-selection or selection-to-mask operations"
            )
        status = command_statuses.get(command_id)
        description = command_descriptions.get(command_id, "")
        checks[f"{operation}_command"] = command_id
        checks[f"{operation}_status"] = status
        if status is None:
            errors.append(f"{operation} command is absent from current-session capability snapshot: {command_id}")
        elif status in BLOCKING_STATUSES:
            errors.append(f"{operation} command is not remotely executable: {command_id} ({status})")
        elif status != "supported":
            errors.append(f"{operation} command must be supported: {command_id} ({status})")
        if not all(term in description.lower() for term in terms):
            errors.append(f"{operation} command description does not prove required effect: {command_id}")
        catalog_entry = catalog_commands.get(command_id)
        if catalog_entry is None:
            errors.append(f"{operation} command is absent from current Photoshop command catalog: {command_id}")
        else:
            catalog_status = catalog_entry.get("status")
            catalog_description = catalog_entry.get("description")
            if status != catalog_status or description != catalog_description:
                errors.append(f"{operation} snapshot does not match current catalog: {command_id}")

    payload = {
        "schema": "ndc-extraction-capability-gate/v1",
        "status": "PASS" if not errors else "FAIL",
        "EXTRACTION_CAPABILITY_GATE": "PASS" if not errors else "FAIL",
        "contract": str(contract_path),
        "source_candidate_path": str(source_path) if source_path else None,
        "capability_snapshot_path": str(snapshot_path) if snapshot_path else None,
        "checks": checks,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
