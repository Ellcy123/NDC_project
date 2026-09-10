#!/usr/bin/env python3
"""Validate the NDC three-plus-cast foreground back-composition evidence gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


SCHEMA = "ndc-multicast-back-composition/v1"
STAGES = {"whitebox", "formal", "final-composite"}
NEAR_DEPTH = {"foreground", "near-midground"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_hash(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def bound_file(entry: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(entry, dict):
        errors.append(f"{label} must contain path and sha256")
        return None
    raw_path = entry.get("path")
    expected = entry.get("sha256")
    if not isinstance(raw_path, str) or not Path(raw_path).is_absolute():
        errors.append(f"{label}.path must be an absolute path")
        return None
    path = Path(raw_path).resolve()
    if not path.is_file():
        errors.append(f"{label}.path does not exist")
        return None
    if not valid_hash(expected) or sha256(path) != str(expected).lower():
        errors.append(f"{label}.sha256 does not match current bytes")
    return path


def positive_bbox(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
        and value[2] > 0
        and value[3] > 0
    )


def actor_id_set(values: object, key: str, label: str, errors: list[str]) -> set[str]:
    if not isinstance(values, list) or not values:
        errors.append(f"{label} must be a non-empty actor list")
        return set()
    ids: list[str] = []
    for index, value in enumerate(values):
        actor_id = value.get(key) if isinstance(value, dict) else None
        if not isinstance(actor_id, str) or not actor_id.strip():
            errors.append(f"{label}[{index}].{key} is required")
            continue
        ids.append(actor_id)
    if len(ids) != len(set(ids)):
        errors.append(f"{label} contains duplicate actor IDs")
    return set(ids)


def exact_actor_coverage(
    expected: set[str], actual: set[str], label: str, errors: list[str]
) -> bool:
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        errors.append(f"{label} is missing snapshot actors: {', '.join(missing)}")
    if unknown:
        errors.append(f"{label} contains actors outside the snapshot: {', '.join(unknown)}")
    return not missing and not unknown


def explicit_exception(data: dict, errors: list[str]) -> bool:
    exception = data.get("exception")
    if exception is None:
        return False
    if not isinstance(exception, dict):
        errors.append("exception must be an object")
        return False
    valid = (
        exception.get("source_kind") == "user_instruction"
        and exception.get("scene_id") == data.get("scene_id")
        and exception.get("snapshot_id") == data.get("snapshot_id")
        and isinstance(exception.get("instruction"), str)
        and bool(exception["instruction"].strip())
    )
    if not valid:
        errors.append("exception must be an explicit user_instruction for this exact scene_id and snapshot_id")
    return valid


def validate(data: dict) -> dict:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    for key in ("scene_id", "snapshot_id"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} is required")
    if data.get("stage") not in STAGES:
        errors.append("stage must be whitebox, formal, or final-composite")

    artifact = bound_file(data.get("artifact"), "artifact", errors)
    actors = data.get("actors")
    if not isinstance(actors, list) or not actors:
        errors.append("actors must be a non-empty list")
        actors = []
    ids: list[str] = []
    for index, actor in enumerate(actors):
        label = f"actors[{index}]"
        if not isinstance(actor, dict):
            errors.append(f"{label} must be an object")
            continue
        actor_id = actor.get("actor_id")
        if not isinstance(actor_id, str) or not actor_id.strip():
            errors.append(f"{label}.actor_id is required")
        else:
            ids.append(actor_id)
        if not isinstance(actor.get("active"), bool):
            errors.append(f"{label}.active must be boolean")
        if actor.get("depth_band") not in {"foreground", "near-midground", "midground", "background"}:
            errors.append(f"{label}.depth_band is invalid")
        if actor.get("facing") not in {"back", "back-three-quarter", "side", "front"}:
            errors.append(f"{label}.facing is invalid")
    if len(ids) != len(set(ids)):
        errors.append("actor_id values must be unique")

    applicable = len(actors) >= 3
    exception_used = explicit_exception(data, errors) if applicable else False
    candidate_ids: list[str] = []
    ui_status = None
    ui_contract_actor_ids: set[str] = set()
    ui_report_actor_ids: set[str] = set()
    ui_actor_coverage = None
    if applicable:
        snapshot_actor_ids = set(ids)
        ui_path = bound_file(data.get("ui_report"), "ui_report", errors)
        if ui_path:
            try:
                ui_data = json.loads(ui_path.read_text(encoding="utf-8-sig"))
                ui_status = str(ui_data.get("status", "")).lower()
                if ui_data.get("schema") != "ndc-ui-safety-report/v1":
                    errors.append("ui_report schema must be ndc-ui-safety-report/v1")
                if ui_status != "pass":
                    errors.append("ui_report must have status pass")
                ui_report_actor_ids = actor_id_set(
                    ui_data.get("actors"), "actorId", "ui_report.actors", errors
                )
                ui_contract_path = bound_file(
                    {
                        "path": ui_data.get("contract"),
                        "sha256": ui_data.get("contractSha256"),
                    },
                    "ui_report.contract",
                    errors,
                )
                if ui_contract_path:
                    ui_contract = json.loads(
                        ui_contract_path.read_text(encoding="utf-8-sig")
                    )
                    if ui_contract.get("schema") != "ndc-ui-safety/v1":
                        errors.append("ui_report.contract schema must be ndc-ui-safety/v1")
                    ui_contract_actor_ids = actor_id_set(
                        ui_contract.get("actors"),
                        "actorId",
                        "ui_report.contract.actors",
                        errors,
                    )
                report_ok = exact_actor_coverage(
                    snapshot_actor_ids, ui_report_actor_ids, "ui_report.actors", errors
                )
                contract_ok = exact_actor_coverage(
                    snapshot_actor_ids,
                    ui_contract_actor_ids,
                    "ui_report.contract.actors",
                    errors,
                )
                if ui_contract_actor_ids != ui_report_actor_ids:
                    errors.append("ui_report actor IDs differ from its bound UI contract")
                ui_actor_coverage = report_ok and contract_ok and ui_contract_actor_ids == ui_report_actor_ids
            except (OSError, json.JSONDecodeError, AttributeError, TypeError) as exc:
                errors.append("ui_report cannot be read: " + str(exc))
        for actor in actors:
            if not isinstance(actor, dict):
                continue
            if (
                actor.get("active") is False
                and actor.get("depth_band") in NEAR_DEPTH
                and actor.get("facing") == "back"
                and positive_bbox(actor.get("visible_back_region_bbox"))
            ):
                candidate_ids.append(str(actor.get("actor_id")))
        if not candidate_ids and not exception_used:
            errors.append("three-plus cast requires a non-active foreground/near-midground actor facing back with a visible back bbox")

    return {
        "schema": "ndc-multicast-back-composition-gate/v1",
        "gate": "MULTICAST_BACK_COMPOSITION_GATE",
        "status": "PASS" if not errors else "FAIL",
        "checks": {
            "applicable": applicable,
            "cast_count": len(actors),
            "stage": data.get("stage"),
            "artifact_sha256": sha256(artifact) if artifact and artifact.is_file() else None,
            "candidate_actor_ids": candidate_ids,
            "ui_status": ui_status,
            "snapshot_actor_ids": sorted(set(ids)),
            "ui_contract_actor_ids": sorted(ui_contract_actor_ids),
            "ui_report_actor_ids": sorted(ui_report_actor_ids),
            "ui_actor_coverage": ui_actor_coverage,
            "exception_used": exception_used,
            "artistic_approval": False,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.contract.resolve().read_text(encoding="utf-8-sig"))
    result = validate(data)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
