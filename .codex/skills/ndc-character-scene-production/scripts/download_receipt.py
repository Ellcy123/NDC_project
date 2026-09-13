#!/usr/bin/env python3
"""Claim one browser download without relying on an observable download event."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_SNAPSHOT = "codex-browser-download-snapshot/v1"
SCHEMA_RECEIPT = "codex-browser-download-receipt/v1"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_LOCK = ".codex-browser-download.lock.json"


def utc_iso(ns: int | None = None) -> str:
    value = time.time_ns() if ns is None else ns
    return datetime.fromtimestamp(value / 1_000_000_000, timezone.utc).isoformat().replace("+00:00", "Z")


def local_iso(ns: int | None = None) -> str:
    value = time.time_ns() if ns is None else ns
    return datetime.fromtimestamp(value / 1_000_000_000).astimezone().isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_info(path: Path) -> tuple[str, int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return "png", width, height
    if data.startswith(b"\xff\xd8"):
        offset = 2
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            offset += 2
            if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
                continue
            if offset + 2 > len(data):
                break
            length = struct.unpack(">H", data[offset:offset + 2])[0]
            if marker in sof and length >= 7 and offset + 7 <= len(data):
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return "jpeg", width, height
            if length < 2:
                break
            offset += length
    if data.startswith(b"RIFF") and len(data) >= 30 and data[8:12] == b"WEBP":
        chunk = data[12:16]
        payload = data[20:]
        if chunk == b"VP8X" and len(payload) >= 10:
            width = int.from_bytes(payload[4:7], "little") + 1
            height = int.from_bytes(payload[7:10], "little") + 1
            return "webp", width, height
        if chunk == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
            bits = int.from_bytes(payload[1:5], "little")
            return "webp", (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if chunk == b"VP8 " and len(payload) >= 10 and payload[3:6] == b"\x9d\x01\x2a":
            width = int.from_bytes(payload[6:8], "little") & 0x3FFF
            height = int.from_bytes(payload[8:10], "little") & 0x3FFF
            return "webp", width, height
    raise ValueError("unsupported or unreadable image payload")


def stat_entry(path: Path, *, include_hash: bool) -> dict[str, Any]:
    stat = path.stat()
    entry: dict[str, Any] = {
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "ctime_ns": stat.st_ctime_ns,
        "file_id": f"{stat.st_dev}:{stat.st_ino}",
    }
    if include_hash:
        entry["sha256"] = sha256(path)
    return entry


def scan(directory: Path, *, include_hash: bool) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                result[path.name] = stat_entry(path, include_hash=include_hash)
            except (FileNotFoundError, PermissionError):
                continue
    return result


def write_json(path: Path, value: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def acquire_lock(directory: Path, owner: str, lock_name: str) -> tuple[Path, str]:
    lock = directory / lock_name
    token = uuid.uuid4().hex
    payload = {
        "schema": "codex-browser-download-lock/v1",
        "token": token,
        "owner": owner,
        "acquired_at_utc": utc_iso(),
        "acquired_at_local": local_iso(),
        "pid": os.getpid(),
    }
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as exc:
        raise RuntimeError(f"download directory already locked: {lock}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return lock, token


def release_lock(snapshot: dict[str, Any]) -> None:
    lock = Path(snapshot["lock"]["path"])
    if not lock.exists():
        return
    current = load_json(lock)
    if current.get("token") != snapshot["lock"].get("token"):
        raise RuntimeError("refusing to release a lock owned by another receipt")
    lock.unlink()


def begin(directory: Path, snapshot_path: Path, owner: str, lock_name: str = DEFAULT_LOCK) -> dict[str, Any]:
    directory = directory.resolve()
    if not directory.is_dir():
        raise ValueError(f"download directory does not exist: {directory}")
    lock, token = acquire_lock(directory, owner, lock_name)
    captured_ns = time.time_ns()
    try:
        value = {
            "schema": SCHEMA_SNAPSHOT,
            "state": "ARMED",
            "receipt_id": uuid.uuid4().hex,
            "owner": owner,
            "directory": str(directory),
            "snapshot_path": str(snapshot_path.resolve()),
            "captured_at_ns": captured_ns,
            "captured_at_utc": utc_iso(captured_ns),
            "captured_at_local": local_iso(captured_ns),
            "lock": {"path": str(lock.resolve()), "token": token},
            "files": scan(directory, include_hash=True),
        }
        write_json(snapshot_path, value)
        return value
    except Exception:
        lock.unlink(missing_ok=True)
        raise


def changed_names(snapshot: dict[str, Any], current: dict[str, dict[str, Any]], tolerance_ns: int) -> list[str]:
    previous = snapshot.get("files", {})
    cutoff = int(snapshot["captured_at_ns"]) - tolerance_ns
    changed: list[str] = []
    for name, entry in current.items():
        old = previous.get(name)
        signature = (entry["size"], entry["mtime_ns"], entry["ctime_ns"], entry["file_id"])
        old_signature = None if old is None else (old["size"], old["mtime_ns"], old["ctime_ns"], old["file_id"])
        if signature != old_signature and max(entry["mtime_ns"], entry["ctime_ns"]) >= cutoff:
            changed.append(name)
    return changed


def validate_candidate(path: Path, expected_width: int | None, expected_height: int | None, expected_sha256: str | None) -> dict[str, Any]:
    errors: list[str] = []
    kind: str | None = None
    width: int | None = None
    height: int | None = None
    digest: str | None = None
    try:
        digest = sha256(path)
        kind, width, height = image_info(path)
    except (OSError, ValueError) as exc:
        errors.append(f"unreadable image: {type(exc).__name__}: {exc}")
    if expected_width is not None and width != expected_width:
        errors.append(f"width {width} != {expected_width}")
    if expected_height is not None and height != expected_height:
        errors.append(f"height {height} != {expected_height}")
    if expected_sha256 is not None and (digest is None or digest.lower() != expected_sha256.lower()):
        errors.append("sha256 mismatch")
    return {
        "path": str(path.resolve()),
        "format": kind,
        "width": width,
        "height": height,
        "size": path.stat().st_size if path.exists() else None,
        "sha256": digest,
        "validation_errors": errors,
    }


def copy_candidate(path: Path, destination: Path | None) -> Path:
    if destination is None:
        return path
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return destination


def receipt_base(snapshot: dict[str, Any], method: str) -> dict[str, Any]:
    finished_ns = time.time_ns()
    return {
        "schema": SCHEMA_RECEIPT,
        "receipt_id": snapshot["receipt_id"],
        "owner": snapshot["owner"],
        "method": method,
        "directory": snapshot["directory"],
        "snapshot_path": snapshot["snapshot_path"],
        "click_must_not_be_repeated": True,
        "captured_at_utc": snapshot["captured_at_utc"],
        "captured_at_local": snapshot["captured_at_local"],
        "finished_at_utc": utc_iso(finished_ns),
        "finished_at_local": local_iso(finished_ns),
    }


def settle(snapshot_path: Path, receipt_path: Path, timeout_seconds: float, stable_seconds: float, tolerance_seconds: float = 2.0, expected_width: int | None = None, expected_height: int | None = None, expected_sha256: str | None = None, destination: Path | None = None) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    if snapshot.get("schema") != SCHEMA_SNAPSHOT:
        raise ValueError("unsupported download snapshot schema")
    directory = Path(snapshot["directory"])
    deadline = time.monotonic() + timeout_seconds
    stable_since: dict[str, tuple[tuple[Any, ...], float]] = {}
    stable_names: list[str] = []
    observed_names: list[str] = []
    while True:
        current = scan(directory, include_hash=False)
        names = changed_names(snapshot, current, round(tolerance_seconds * 1_000_000_000))
        observed_names = names
        now = time.monotonic()
        stable_names = []
        for name in names:
            entry = current[name]
            signature = (entry["size"], entry["mtime_ns"], entry["ctime_ns"], entry["file_id"])
            prior = stable_since.get(name)
            if prior is None or prior[0] != signature:
                stable_since[name] = (signature, now)
            elif now - prior[1] >= stable_seconds:
                stable_names.append(name)
        stable_since = {name: value for name, value in stable_since.items() if name in names}
        if len(stable_names) > 1 or (len(stable_names) == 1 and len(names) == 1):
            break
        if now >= deadline:
            break
        time.sleep(min(0.25, max(0.01, deadline - now)))

    receipt = receipt_base(snapshot, "directory_delta")
    receipt["changed_files"] = sorted(observed_names)
    try:
        if not observed_names:
            receipt["status"] = "NO_NEW_FILE_OBSERVED"
            receipt["selected"] = None
        elif len(observed_names) > 1:
            receipt["status"] = "AMBIGUOUS_DIRECTORY_DELTA"
            receipt["selected"] = None
            receipt["candidates"] = [
                {"path": str((directory / name).resolve()), **current[name]}
                for name in sorted(observed_names)
            ]
        elif not stable_names:
            receipt["status"] = "FILE_NOT_STABLE_BEFORE_TIMEOUT"
            receipt["selected"] = None
        else:
            source = directory / stable_names[0]
            selected_path = copy_candidate(source, destination)
            selected = validate_candidate(selected_path, expected_width, expected_height, expected_sha256)
            selected["source_path"] = str(source.resolve())
            receipt["selected"] = selected
            receipt["status"] = "UNIQUE_DIRECTORY_DELTA" if not selected["validation_errors"] else "CANDIDATE_VALIDATION_FAILED"
        write_json(receipt_path, receipt)
    except Exception as exc:
        receipt.update({"status": "RECEIPT_OPERATION_FAILED", "selected": None, "error": f"{type(exc).__name__}: {exc}"})
        write_json(receipt_path, receipt)
        raise
    finally:
        release_lock(snapshot)
    return receipt


def complete_event(snapshot_path: Path, event_path: Path, receipt_path: Path, destination: Path | None = None, expected_width: int | None = None, expected_height: int | None = None, expected_sha256: str | None = None) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    event_path = event_path.resolve()
    receipt = receipt_base(snapshot, "playwright_download_path")
    try:
        if not event_path.is_file():
            receipt.update({"status": "EVENT_PATH_UNAVAILABLE", "selected": None, "event_path": str(event_path)})
        else:
            selected_path = copy_candidate(event_path, destination)
            selected = validate_candidate(selected_path, expected_width, expected_height, expected_sha256)
            selected["event_path"] = str(event_path)
            receipt["selected"] = selected
            receipt["status"] = "EVENT_PATH_VERIFIED" if not selected["validation_errors"] else "CANDIDATE_VALIDATION_FAILED"
        write_json(receipt_path, receipt)
    except Exception as exc:
        receipt.update({"status": "RECEIPT_OPERATION_FAILED", "selected": None, "error": f"{type(exc).__name__}: {exc}"})
        write_json(receipt_path, receipt)
        raise
    finally:
        release_lock(snapshot)
    return receipt


def verify(receipt_path: Path) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    selected = receipt.get("selected")
    if not isinstance(selected, dict) or not selected.get("path"):
        return {"verified": False, "reason": "receipt has no selected file"}
    path = Path(selected["path"])
    if not path.is_file():
        return {"verified": False, "reason": "selected file is missing", "path": str(path)}
    actual = validate_candidate(path, selected.get("width"), selected.get("height"), selected.get("sha256"))
    return {"verified": not actual["validation_errors"], "actual": actual}


def add_expectations(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--expected-width", type=int)
    parser.add_argument("--expected-height", type=int)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--destination", type=Path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    arm = sub.add_parser("begin", help="lock a download directory and save its pre-click snapshot")
    arm.add_argument("--directory", type=Path, required=True)
    arm.add_argument("--snapshot", type=Path, required=True)
    arm.add_argument("--owner", required=True)
    arm.add_argument("--lock-name", default=DEFAULT_LOCK)
    watch = sub.add_parser("settle", help="claim a unique stable post-click image by directory delta")
    watch.add_argument("--snapshot", type=Path, required=True)
    watch.add_argument("--receipt", type=Path, required=True)
    watch.add_argument("--timeout-seconds", type=float, default=15.0)
    watch.add_argument("--stable-seconds", type=float, default=1.0)
    watch.add_argument("--timestamp-tolerance-seconds", type=float, default=2.0)
    add_expectations(watch)
    event = sub.add_parser("complete-event", help="verify the value returned by PlaywrightDownload.path()")
    event.add_argument("--snapshot", type=Path, required=True)
    event.add_argument("--event-path", type=Path, required=True)
    event.add_argument("--receipt", type=Path, required=True)
    add_expectations(event)
    check = sub.add_parser("verify", help="recompute the selected file identity from a receipt")
    check.add_argument("--receipt", type=Path, required=True)
    release = sub.add_parser("release", help="release an interrupted receipt's matching lock")
    release.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "begin":
        result = begin(args.directory, args.snapshot, args.owner, args.lock_name)
    elif args.command == "settle":
        result = settle(args.snapshot, args.receipt, args.timeout_seconds, args.stable_seconds, args.timestamp_tolerance_seconds, args.expected_width, args.expected_height, args.expected_sha256, args.destination)
    elif args.command == "complete-event":
        result = complete_event(args.snapshot, args.event_path, args.receipt, args.destination, args.expected_width, args.expected_height, args.expected_sha256)
    elif args.command == "verify":
        result = verify(args.receipt)
    else:
        snapshot = load_json(args.snapshot)
        release_lock(snapshot)
        result = {"released": True, "receipt_id": snapshot.get("receipt_id")}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") in {"NO_NEW_FILE_OBSERVED", "AMBIGUOUS_DIRECTORY_DELTA", "FILE_NOT_STABLE_BEFORE_TIMEOUT", "EVENT_PATH_UNAVAILABLE", "CANDIDATE_VALIDATION_FAILED", "RECEIPT_OPERATION_FAILED"} or result.get("verified") is False:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
