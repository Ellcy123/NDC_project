#!/usr/bin/env python3
"""Atomically update one artifact or the compact next-action queue in an NDC prop batch."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo


STATUSES = {"PENDING", "CANDIDATE", "PASS"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@contextmanager
def batch_lock(path: Path):
    lock = path.with_name(path.name + ".state-update.lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        yield
    finally:
        os.close(descriptor)
        lock.unlink()


def relative_file(batch_path: Path, raw: Path, label: str) -> tuple[str, str]:
    path = raw.resolve()
    if not path.is_file():
        raise ValueError(f"{label} file is missing: {path}")
    relative = os.path.relpath(path, batch_path.parent.resolve()).replace("\\", "/")
    return relative, sha256(path)


def parse_bool(value: str) -> bool:
    return value.lower() == "true"


def verify_batch(batch: dict) -> None:
    if batch.get("schema") != "ndc-prop-batch/v1" or not isinstance(batch.get("artifacts"), dict):
        raise ValueError("unsupported or incomplete NDC prop batch")
    queue = batch.get("next_action")
    if not isinstance(queue, str) or not queue.strip():
        raise ValueError("batch next_action is missing")


def event(batch: dict, kind: str, reason: str, before: object, after: object) -> dict:
    if not reason.strip():
        raise ValueError("a concrete state-change reason is required")
    prior = batch.get("state_events", [])
    if not isinstance(prior, list):
        raise ValueError("state_events must be a list")
    body = {
        "schema": "ndc-prop-state-event/v1",
        "sequence": len(prior) + 1,
        "type": kind,
        "at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "reason": reason,
        "before_sha256": json_digest(before),
        "after_sha256": json_digest(after),
        "previous_event_sha256": json_digest(prior[-1]) if prior else None,
    }
    body["event_sha256"] = json_digest(body)
    return body


def update_artifact(args: argparse.Namespace) -> dict:
    batch_path = args.batch.resolve()
    with batch_lock(batch_path):
        if args.expect_batch_sha256 and sha256(batch_path).lower() != args.expect_batch_sha256.lower():
            raise ValueError("batch bytes changed before update")
        batch = read_json(batch_path)
        verify_batch(batch)
        if args.artifact_id not in batch["artifacts"]:
            raise ValueError("artifact is outside the locked batch")
        before = dict(batch["artifacts"][args.artifact_id])
        if before.get("status") != args.expect_status:
            raise ValueError(f"artifact status changed: expected {args.expect_status}, found {before.get('status')}")
        after = dict(before)
        after["status"] = args.status
        after["rejected"] = args.rejected
        if args.output is not None:
            after["path"], after["sha256"] = relative_file(batch_path, args.output, "output")
        if args.review is not None:
            after["review"], _ = relative_file(batch_path, args.review, "review")
        if args.published_path is not None:
            after["published_path"], published_hash = relative_file(batch_path, args.published_path, "published")
            if not after.get("sha256") or published_hash.lower() != str(after["sha256"]).lower():
                raise ValueError("published file must be an exact copy of the bound output")
        if args.frozen is not None:
            after["frozen"] = args.frozen
        if args.status == "PASS" and (args.rejected or not after.get("path") or not after.get("sha256") or not after.get("review")):
            raise ValueError("PASS requires a non-rejected output hash and review record")
        if after == before:
            raise ValueError("artifact update is a no-op")
        batch["artifacts"][args.artifact_id] = after
        change = event(batch, "artifact_transition", args.reason, before, after)
        change["artifact_id"] = args.artifact_id
        change["from_status"] = before.get("status")
        change["to_status"] = after.get("status")
        change["event_sha256"] = json_digest({key: value for key, value in change.items()
                                                if key != "event_sha256"})
        batch.setdefault("state_events", []).append(change)
        write_json(batch_path, batch)
        return {"batch": str(batch_path), "artifact_id": args.artifact_id,
                "status": after["status"], "batch_sha256": sha256(batch_path),
                "state_event_sequence": change["sequence"]}


def update_next_action(args: argparse.Namespace) -> dict:
    batch_path = args.batch.resolve()
    actions = [value.strip() for value in args.action if value.strip()]
    if not 1 <= len(actions) <= 3:
        raise ValueError("next_action requires one to three concrete actions")
    value = "；".join(actions)
    if len(value) > 300:
        raise ValueError("next_action must not exceed 300 characters")
    with batch_lock(batch_path):
        if args.expect_batch_sha256 and sha256(batch_path).lower() != args.expect_batch_sha256.lower():
            raise ValueError("batch bytes changed before update")
        batch = read_json(batch_path)
        verify_batch(batch)
        before = batch["next_action"]
        if before == value:
            raise ValueError("next_action update is a no-op")
        batch["next_action"] = value
        change = event(batch, "next_action_update", args.reason, before, value)
        change["actions"] = actions
        change["event_sha256"] = json_digest({key: value for key, value in change.items()
                                                if key != "event_sha256"})
        batch.setdefault("state_events", []).append(change)
        write_json(batch_path, batch)
        return {"batch": str(batch_path), "next_action": value,
                "batch_sha256": sha256(batch_path), "state_event_sequence": change["sequence"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    artifact = sub.add_parser("artifact-transition")
    artifact.add_argument("--batch", type=Path, required=True)
    artifact.add_argument("--artifact-id", required=True)
    artifact.add_argument("--expect-status", choices=sorted(STATUSES), required=True)
    artifact.add_argument("--status", choices=sorted(STATUSES), required=True)
    artifact.add_argument("--rejected", type=parse_bool, choices=(True, False), required=True)
    artifact.add_argument("--output", type=Path)
    artifact.add_argument("--review", type=Path)
    artifact.add_argument("--published-path", type=Path)
    artifact.add_argument("--frozen", type=parse_bool, choices=(True, False))
    artifact.add_argument("--expect-batch-sha256")
    artifact.add_argument("--reason", required=True)
    queue = sub.add_parser("next-action")
    queue.add_argument("--batch", type=Path, required=True)
    queue.add_argument("--action", action="append", required=True)
    queue.add_argument("--expect-batch-sha256")
    queue.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        result = update_artifact(args) if args.command == "artifact-transition" else update_next_action(args)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"blocked": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
