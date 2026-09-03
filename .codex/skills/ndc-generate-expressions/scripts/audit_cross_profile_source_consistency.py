#!/usr/bin/env python3
"""Fail-closed proof that two profile assets share one artistic source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_KIND = "ndc_expression_profile_composition"
CALM_ALPHA_LOCK_METHOD = "CALM_ALPHA_LOCK"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_audit(path: Path, expected_profile: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind") == EXPECTED_KIND:
        output = data.get("output", {})
        source = data.get("source", {})
    elif data.get("method") == CALM_ALPHA_LOCK_METHOD:
        output = {
            "path": data.get("output"),
            "sha256": data.get("output_sha256"),
            "profile": data.get("profile"),
        }
        source = {
            "path": data.get("candidate"),
            "sha256": data.get("candidate_sha256"),
        }
    else:
        raise ValueError(f"Composition audit kind mismatch: {path}")
    if output.get("profile") != expected_profile:
        raise ValueError(f"Expected {expected_profile} profile: {path}")
    for label, record in (("source", source), ("output", output)):
        asset_path = Path(record.get("path", "")).resolve()
        if not asset_path.is_file():
            raise FileNotFoundError(f"Missing {label} file: {asset_path}")
        actual_hash = sha256(asset_path)
        if record.get("sha256") != actual_hash:
            raise ValueError(f"Stale {label} hash in {path}: {asset_path}")
    return {"source": source, "output": output, "raw": data}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that green and transparent profile compositions use one native expression source."
    )
    parser.add_argument("--greenscreen-audit", required=True, type=Path)
    parser.add_argument("--transparent-audit", required=True, type=Path)
    parser.add_argument("--expression-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    checks: dict[str, bool] = {}
    errors: list[str] = []
    try:
        green = load_audit(args.greenscreen_audit.resolve(), "greenscreen")
        transparent = load_audit(args.transparent_audit.resolve(), "transparent")
        green_source = green["source"]
        transparent_source = transparent["source"]
        green_output = green["output"]
        transparent_output = transparent["output"]
        checks = {
            "same_native_source_sha256": green_source["sha256"] == transparent_source["sha256"],
            "same_output_basename": Path(green_output["path"]).name == Path(transparent_output["path"]).name,
            "distinct_profile_labels": green_output["profile"] != transparent_output["profile"],
            "expression_id_matches_basename": args.expression_id in Path(green_output["path"]).stem,
        }
        if not checks["same_native_source_sha256"]:
            errors.append("green and transparent compositions use different native-source hashes")
        if not checks["same_output_basename"]:
            errors.append("profile output basenames do not match")
        if not checks["distinct_profile_labels"]:
            errors.append("composition audits do not represent distinct profiles")
        if not checks["expression_id_matches_basename"]:
            errors.append("expression ID is not present in the output basename")
        source_sha = green_source["sha256"] if checks["same_native_source_sha256"] else None
        payload = {
            "schema_version": 1,
            "kind": "ndc_expression_cross_profile_source_audit",
            "expression_id": args.expression_id,
            "composition_audits": {
                "greenscreen": str(args.greenscreen_audit.resolve()),
                "transparent": str(args.transparent_audit.resolve()),
            },
            "native_source_sha256": source_sha,
            "checks": checks,
            "errors": errors,
            "formal_status": "PASS" if not errors and all(checks.values()) else "FAIL",
        }
    except Exception as exc:  # fail closed with a readable record
        errors.append(str(exc))
        payload = {
            "schema_version": 1,
            "kind": "ndc_expression_cross_profile_source_audit",
            "expression_id": args.expression_id,
            "composition_audits": {
                "greenscreen": str(args.greenscreen_audit.resolve()),
                "transparent": str(args.transparent_audit.resolve()),
            },
            "native_source_sha256": None,
            "checks": checks,
            "errors": errors,
            "formal_status": "FAIL",
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CROSS_PROFILE_NATIVE_SOURCE_GATE: {payload['formal_status']}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if payload["formal_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
