"""Block an NDC formal-image package unless every PNG has a passing visual record.

This is intentionally a record-presence gate, not an image-quality classifier.
It accepts a PNG only when a `ndc-stage-visual-self-check/v1` record proves that
the exact final bytes were reviewed whole and locally at 200% (or tiles), and
that every applicable visual criterion passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_pass_record(path: Path) -> tuple[bool, set[str], str]:
    try:
        record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001 - malformed process history must block
        return False, set(), f"invalid JSON: {error}"
    if record.get("schema") != "ndc-stage-visual-self-check/v1":
        return False, set(), "schema is not ndc-stage-visual-self-check/v1"
    if record.get("visual_check_status") != "PASS":
        return False, set(), "visual_check_status is not PASS"
    criteria = record.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        return False, set(), "criteria are missing"
    if any(item.get("applicable") and item.get("status") != "PASS" for item in criteria if isinstance(item, dict)):
        return False, set(), "an applicable criterion is not PASS"
    views = record.get("views")
    if not isinstance(views, list):
        return False, set(), "views are missing"
    view_kinds = {item.get("kind") for item in views if isinstance(item, dict)}
    if "whole_100" not in view_kinds or "local_200_or_tiles" not in view_kinds:
        return False, set(), "whole_100 and local_200_or_tiles are both required"
    outputs = record.get("outputs")
    if not isinstance(outputs, list):
        return False, set(), "outputs are missing"
    hashes = {
        str(item.get("sha256", "")).lower()
        for item in outputs
        if isinstance(item, dict) and item.get("sha256")
    }
    return bool(hashes), hashes, "PASS" if hashes else "no output hashes"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-dir", type=Path, required=True)
    parser.add_argument("--record-root", type=Path, action="append", required=True)
    parser.add_argument("--batch", type=Path, help="Required for new five-stage prop batches.")
    args = parser.parse_args()

    formal_dir = args.formal_dir.resolve()
    if args.batch:
        from workflow_state import formal_errors
        failures = formal_errors(args.batch.resolve(), formal_dir)
        print('FINAL_VISUAL_RECORD_PRESENCE_GATE: ' + ('BLOCKED' if failures else 'PASS'))
        for error in failures:
            print('- ' + error)
        return int(bool(failures))
    if not formal_dir.is_dir():
        print(f"FINAL_VISUAL_RECORD_PRESENCE_GATE: BLOCKED\n- formal directory is missing: {formal_dir}")
        return 1
    artifacts = sorted(path for path in formal_dir.rglob("*.png") if path.is_file())
    if not artifacts:
        print(f"FINAL_VISUAL_RECORD_PRESENCE_GATE: BLOCKED\n- no formal PNG artifacts found: {formal_dir}")
        return 1

    passed_hashes: set[str] = set()
    records_seen = 0
    malformed: list[str] = []
    for root in args.record_root:
        if not root.is_dir():
            malformed.append(f"record root missing: {root}")
            continue
        for record_path in root.rglob("visual_review.json"):
            records_seen += 1
            valid, hashes, message = valid_pass_record(record_path)
            if valid:
                passed_hashes.update(hashes)
            else:
                malformed.append(f"{record_path}: {message}")

    missing = []
    for artifact in artifacts:
        artifact_hash = sha256(artifact).lower()
        if artifact_hash not in passed_hashes:
            missing.append(f"{artifact} sha256={artifact_hash}")

    if missing:
        print("FINAL_VISUAL_RECORD_PRESENCE_GATE: BLOCKED")
        print(f"- formal PNGs: {len(artifacts)}; passing visual records scanned: {records_seen}")
        for item in missing:
            print(f"- missing matching PASS visual record: {item}")
        for item in malformed[:10]:
            print(f"- ignored record: {item}")
        return 1
    print("FINAL_VISUAL_RECORD_PRESENCE_GATE: PASS")
    print(f"- formal PNGs: {len(artifacts)}; passing-record output hashes cover every artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
