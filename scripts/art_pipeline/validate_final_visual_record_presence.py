#!/usr/bin/env python3
"""Check each final PNG against an individually hash-bound passing visual record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from validate_stage_visual_self_check import load_record, require, sha256, validate_record


def validate_directory(formal_dir, record_root):
    formal_dir, record_root = formal_dir.resolve(), record_root.resolve()
    require(formal_dir.is_dir(), f"Formal directory missing: {formal_dir}")
    require(record_root.is_dir(), f"Record root missing: {record_root}")
    artifacts = sorted(path for path in formal_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".png")
    require(bool(artifacts), "Formal directory contains no PNGs")
    by_hash, invalid = {}, []
    for path in sorted(record_root.rglob("*.json")):
        try:
            data = load_record(path)
        except (OSError, ValueError, TypeError) as error:
            if "visual" in path.name.lower():
                invalid.append({"record": str(path), "reason": str(error)})
            continue
        if data.get("schema") != "ndc-stage-visual-self-check/v1":
            if path.name == "visual_review.json" or str(data.get("schema", "")).startswith("ndc-stage-visual-review"):
                invalid.append({"record": str(path), "reason": "Unsupported legacy visual schema; missing evidence is not inferred"})
            continue
        output = data.get("output")
        if not isinstance(output, dict) or not isinstance(output.get("sha256"), str):
            invalid.append({"record": str(path), "reason": "Missing single-output hash binding"})
            continue
        by_hash.setdefault(output["sha256"].lower(), []).append((path, data))
    results = []
    for artifact in artifacts:
        digest = sha256(artifact)
        accepted, errors = [], []
        for record_path, data in by_hash.get(digest, []):
            try:
                accepted.append(validate_record(record_path, artifact, data))
            except (OSError, ValueError, TypeError, KeyError) as error:
                errors.append({"record": str(record_path), "reason": str(error)})
        passed = bool(accepted) and not errors
        results.append({"artifact": str(artifact), "sha256": digest,
                        "status": "PASS" if passed else "BLOCKED", "matching_reviews": accepted,
                        "rejected_reviews": errors,
                        "reason": None if passed else ("Conflicting or invalid current-hash review remains" if errors else
                                                        "No valid current-hash individual output review")})
    return {"schema": "ndc-final-visual-record-presence/v1", "formal_dir": str(formal_dir),
            "record_root": str(record_root), "status": "PASS" if all(row["status"] == "PASS" for row in results) else "BLOCKED",
            "artifacts": results, "unsupported_or_invalid_records": invalid,
            "scope": "Current formal PNG visual-record presence only; does not replace stage-chain, semantic-release, texture, or human/Codex visual review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal-dir", type=Path, required=True)
    parser.add_argument("--record-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        if args.report:
            report_path = args.report.resolve()
            require(not report_path.is_relative_to(args.formal_dir.resolve()), "Report belongs in process directory, not formal directory")
            require(not report_path.exists(), "Refusing to overwrite an existing report; choose a new process-report path")
        report = validate_directory(args.formal_dir, args.record_root)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with args.report.open("x", encoding="utf-8") as stream:
                json.dump(report, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        print(f"FINAL_VISUAL_RECORD_PRESENCE_GATE: {report['status']}")
        print(json.dumps(report, ensure_ascii=False))
        return 0 if report["status"] == "PASS" else 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"FINAL_VISUAL_RECORD_PRESENCE_GATE: BLOCKED {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
