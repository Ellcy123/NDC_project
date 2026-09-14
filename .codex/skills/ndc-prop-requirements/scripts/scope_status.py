#!/usr/bin/env python3
"""Report immutable, execution and delivery-candidate reporting scopes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def active_scope(batch_path: Path, batch: dict) -> dict:
    full = list(batch["scope"]["required_artifacts"])
    pointer = batch.get("active_delivery_scope_revision")
    if pointer is None:
        return {
            "revision_sha256": None,
            "execution": full,
            "reporting": full,
            "excluded": [],
        }
    revision_path = resolve(batch_path.parent, pointer["path"])
    actual = sha256(revision_path)
    if actual.lower() != pointer["sha256"].lower():
        raise ValueError("active delivery scope revision hash mismatch")
    revision = read_json(revision_path)
    execution = revision.get("execution_required_artifacts")
    reporting = revision.get("reporting_asset_artifacts", execution)
    excluded = revision.get("excluded_artifacts", sorted(set(full) - set(execution or [])))
    for name, values in (("execution", execution), ("reporting", reporting), ("excluded", excluded)):
        if not isinstance(values, list) or len(values) != len(set(values)):
            raise ValueError(f"active scope {name} must be a unique list")
    if not set(execution) <= set(full) or not set(reporting) <= set(execution):
        raise ValueError("active scope widens the immutable batch scope")
    return {
        "revision_sha256": actual.lower(),
        "execution": execution,
        "reporting": reporting,
        "excluded": excluded,
    }


def metric(batch: dict, ids: list[str]) -> dict:
    counts = {"PASS": 0, "CANDIDATE": 0, "PENDING": 0, "REJECTED": 0}
    for artifact_id in ids:
        artifact = batch["artifacts"][artifact_id]
        status = artifact.get("status", "PENDING")
        if status in counts:
            counts[status] += 1
        if artifact.get("rejected") is True:
            counts["REJECTED"] += 1
    return {"required": len(ids), "declared_status": counts}


def summarize(batch_path: Path) -> dict:
    batch_path = batch_path.resolve()
    batch = read_json(batch_path)
    scope = active_scope(batch_path, batch)
    return {
        "schema": "ndc-prop-scope-status/v1",
        "batch_id": batch["batch_id"],
        "scope_revision_sha256": scope["revision_sha256"],
        "immutable": metric(batch, list(batch["scope"]["required_artifacts"])),
        "execution": metric(batch, scope["execution"]),
        "reporting": metric(batch, scope["reporting"]),
        "excluded": len(scope["excluded"]),
        "next_action_length": len(batch.get("next_action", "")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = summarize(args.batch)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"blocked": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
