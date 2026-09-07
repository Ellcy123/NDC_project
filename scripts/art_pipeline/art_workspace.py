"""Manage scratch jobs and verified cleanup; never imports art into Unity.

The caller supplies the user's actual selection/cancellation note. A note is
provenance, not an authentication mechanism or machine-generated approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
from datetime import datetime, timezone
from uuid import uuid4

from art_paths import contained, load_art_paths

SCHEMA = "ndc-art-job/v1"
CLOSED = {"closed-delivered", "closed-cancelled"}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reparse(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def regular_tree(root):
    """Never traverse junctions, symlinks, or special files during cleanup."""
    if reparse(root):
        raise ValueError(f"Linked path is not a managed payload: {root}")
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = Path(directory) / name
            if reparse(path):
                raise ValueError(f"Linked path blocks cleanup: {path}")
            if name in names:
                if not stat.S_ISREG(path.stat().st_mode):
                    raise ValueError(f"Non-regular file blocks cleanup: {path}")
                files.append(path)
    return files


def usage(root):
    total = 0
    skipped = []
    if not root.exists():
        return total, skipped
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in list(dirs):
            p = Path(directory) / name
            if reparse(p):
                dirs.remove(name)
                skipped.append(str(p))
        for name in files:
            p = Path(directory) / name
            if reparse(p):
                skipped.append(str(p))
            else:
                total += p.stat().st_size
    return total, skipped


def save(job, record):
    record["updatedAt"] = now()
    temporary = job / "job.json.tmp"
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(job / "job.json")


def load_job(job, paths):
    raw = Path(job).absolute()
    if not raw.exists() or reparse(raw):
        raise ValueError("Job must exist and must not be a link")
    job = raw.resolve()
    # Only one level below work_root/jobs; never accepts a repository or legacy tree.
    if job.parent != (paths.work_root / "jobs").resolve():
        raise ValueError("Not a managed job directly under work_root/jobs")
    for parent in [paths.work_root, paths.work_root / "jobs"]:
        if reparse(parent):
            raise ValueError("Linked workspace roots are not supported")
    marker = job / "job.json"
    if reparse(marker):
        raise ValueError("Linked job metadata is forbidden")
    record = json.loads(marker.read_text(encoding="utf-8"))
    if record.get("schema") != SCHEMA or record.get("jobId") != job.name:
        raise ValueError("Invalid job identity")
    if Path(record.get("workRoot", "")).resolve() != paths.work_root:
        raise ValueError("Job belongs to a different workspace")
    return job, record


def payload_file(job, relative):
    path = job / "payload" / relative
    if not contained(path, job / "payload") or not path.is_file():
        raise ValueError(f"Not a file in this job payload: {relative}")
    for p in [path, *path.parents]:
        if p == job:
            break
        if reparse(p):
            raise ValueError("Linked payload path is forbidden")
    return path


def external_copy(job, source, destination, paths):
    destination = Path(destination).absolute()
    if contained(destination, paths.work_root, allow_root=True):
        raise ValueError("Retained copy must be outside the entire temporary workspace")
    if not destination.is_file() or reparse(destination):
        raise ValueError("Retained copy must already exist as a regular file")
    if os.path.samefile(source, destination):
        raise ValueError("A link to the same file is not an independent retained copy")
    digest = sha(source)
    if sha(destination) != digest:
        raise ValueError("Source and retained-copy hashes differ")
    return {"source": source.relative_to(job / "payload").as_posix(),
            "destination": str(destination.resolve()), "sha256": digest,
            "bytes": source.stat().st_size, "verifiedAt": now()}


def verify_retained(job, record, paths, *, require_sources=True):
    for entry in record.get("retained", []):
        destination = Path(entry["destination"])
        if contained(destination, paths.work_root, allow_root=True):
            raise ValueError("Retained copy is still in the temporary workspace")
        if not destination.is_file() or sha(destination) != entry["sha256"]:
            raise ValueError(f"Retained copy missing or changed: {destination}")
        raw_source = job / "payload" / entry["source"]
        if require_sources or raw_source.exists():
            source = payload_file(job, entry["source"])
            if sha(source) != entry["sha256"]:
                raise ValueError(f"Source changed after retention: {source}")
    if record["state"] == "closed-delivered":
        approval = record.get("approval", {})
        if not approval.get("note") or not approval.get("assets"):
            raise ValueError("Missing user selection record")
        deliveries = {e["source"]: e for e in record.get("retained", []) if e["kind"] == "delivery"}
        for entry in approval["assets"]:
            match = deliveries.get(entry["source"])
            if not match or match["sha256"] != entry["sha256"]:
                raise ValueError(f"Selected deliverable has no verified copy: {entry['source']}")
            if not contained(Path(match["destination"]), paths.engine_root):
                raise ValueError("Delivered file must be in the configured engine project")
    if record["state"] == "closed-cancelled" and not record.get("closureNote"):
        raise ValueError("Missing explicit cancellation note")
    retained = {e["source"] for e in record.get("retained", [])}
    missing = set(record.get("masters", [])) - retained
    if missing:
        raise ValueError(f"Reusable masters not safely retained: {sorted(missing)}")


def cleanup_one(job, paths, apply=False):
    job, record = load_job(job, paths)
    if record["state"] not in CLOSED:
        return {"job": job.name, "action": "keep", "state": record["state"]}
    if record.get("cleanup"):
        return {"job": job.name, "action": "already-cleaned"}
    payload = job / "payload"
    intent = record.get("cleanupIntent")
    verify_retained(job, record, paths, require_sources=not bool(intent))
    files = regular_tree(payload) if payload.exists() else []
    if not payload.exists() and not intent:
        raise ValueError("Payload vanished before any verified cleanup started")
    current = {p.relative_to(payload).as_posix():
               {"bytes": p.stat().st_size, "mtimeNs": p.stat().st_mtime_ns} for p in files}
    if intent:
        if any(name not in intent["files"] or info != intent["files"][name]
               for name, info in current.items()):
            raise ValueError("New or modified payload files appeared after cleanup began; retained")
        size = intent["bytes"]
        count = len(intent["files"])
    else:
        size = sum(info["bytes"] for info in current.values())
        count = len(current)
    # Check final absolute target immediately before recursive deletion.
    if payload.resolve().parent != job or payload.name != "payload":
        raise ValueError("Unsafe cleanup target")
    if apply:
        if not intent:
            # Persist verification before deletion so a Windows sharing violation can
            # be retried without requiring already-deleted approved source bytes.
            record["cleanupIntent"] = {"at": now(), "files": current, "bytes": size}
            save(job, record)
        if payload.exists():
            shutil.rmtree(payload)
        record["cleanup"] = {"at": now(), "files": count, "bytes": size}
        record.pop("cleanupIntent", None)
        save(job, record)
    return {"job": job.name, "action": "cleaned" if apply else "would-clean",
            "files": count, "bytes": size}


def cleanup_all(paths, apply=False):
    root = paths.work_root / "jobs"
    result = []
    if root.exists():
        if reparse(root):
            raise ValueError("Linked jobs root is forbidden")
        for job in sorted(root.iterdir()):
            if job.is_dir():
                try:
                    result.append(cleanup_one(job, paths, apply))
                except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
                    result.append({"job": job.name, "action": "keep", "reason": str(exc)})
    return result


def run(args):
    paths = load_art_paths()
    if args.command == "create":
        if not re.fullmatch(r"[\w\-\u3400-\u9fff]{1,80}", args.name):
            raise ValueError("Task name: 1–80 letters, numbers, Chinese, hyphen or underscore")
        # Only completed managed jobs are ever pruned. Unknown/legacy directories stay.
        reclaimed = cleanup_all(paths, apply=True)
        size, linked = usage(paths.work_root)
        if size >= paths.quota_gib * 1024**3:
            raise ValueError("Workspace quota reached; active, waiting and unknown jobs are retained")
        ancestor = paths.work_root
        while not ancestor.exists():
            ancestor = ancestor.parent
        if shutil.disk_usage(ancestor).free < paths.minimum_free_gib * 1024**3:
            raise ValueError("Insufficient free space for a new art job")
        jobs = paths.work_root / "jobs"
        jobs.mkdir(parents=True, exist_ok=True)
        if reparse(paths.work_root) or reparse(jobs):
            raise ValueError("Linked workspace roots are forbidden")
        job = jobs / (datetime.now().strftime("%Y%m%d_%H%M%S_") + args.name + "_" + uuid4().hex[:8])
        job.mkdir()
        (job / "payload").mkdir()
        record = {"schema": SCHEMA, "jobId": job.name, "name": args.name, "kind": args.kind,
                  "workRoot": str(paths.work_root), "state": "working", "createdAt": now(),
                  "masters": [], "retained": [], "approval": None}
        save(job, record)
        return {"job": str(job), "output": str(job / "payload"), "pruned": reclaimed}
    if args.command == "status":
        size, linked = usage(paths.work_root)
        return {"workRoot": str(paths.work_root), "bytes": size, "quotaGiB": paths.quota_gib,
                "overQuota": size >= paths.quota_gib * 1024**3, "linkedPathsNotCounted": linked,
                "jobs": cleanup_all(paths, apply=False)}
    if args.command == "cleanup":
        return cleanup_one(args.job, paths, args.apply) if args.job else cleanup_all(paths, args.apply)
    job, record = load_job(args.job, paths)
    if record["state"] in CLOSED or record.get("cleanup"):
        raise ValueError("Closed jobs are immutable; create a new job to resume")
    if args.command == "ready":
        record["state"] = "waiting-for-user"
    elif args.command == "resume":
        record["state"] = "working"
        record["approval"] = None
        record["retained"] = [e for e in record["retained"] if e["kind"] != "delivery"]
    elif args.command == "mark-master":
        source = payload_file(job, args.source)
        relative = source.relative_to(job / "payload").as_posix()
        if relative not in record["masters"]:
            record["masters"].append(relative)
    elif args.command == "approve":
        assets = []
        for relative in args.asset:
            source = payload_file(job, relative)
            assets.append({"source": source.relative_to(job / "payload").as_posix(), "sha256": sha(source)})
        record["approval"] = {"note": args.note, "at": now(), "assets": assets}
        record["state"] = "approved"
    elif args.command == "record-copy":
        source = payload_file(job, args.source)
        entry = external_copy(job, source, args.destination, paths)
        if args.kind == "delivery":
            approved = {e["source"]: e["sha256"] for e in (record.get("approval") or {}).get("assets", [])}
            if record["state"] != "approved" or approved.get(entry["source"]) != entry["sha256"]:
                raise ValueError("Only the exact user-selected bytes can be recorded as delivered")
            if not contained(Path(entry["destination"]), paths.engine_root):
                raise ValueError("Delivery destination must be inside the engine")
        entry["kind"] = args.kind
        record["retained"] = [e for e in record["retained"] if e["source"] != entry["source"]]
        record["retained"].append(entry)
    elif args.command == "close":
        if args.result == "delivered" and record["state"] != "approved":
            raise ValueError("Cannot finish delivery without explicit user approval")
        record["state"] = "closed-" + args.result
        record["closureNote"] = args.note
        record["closedAt"] = now()
        verify_retained(job, record, paths)
    save(job, record)
    if args.command == "close":
        return cleanup_one(job, paths, apply=True)
    return {"job": str(job), "state": record["state"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    create = subs.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--kind", required=True)
    subs.add_parser("status")
    clean = subs.add_parser("cleanup", help="Dry run unless --apply; completed managed jobs only")
    clean.add_argument("--job")
    clean.add_argument("--apply", action="store_true")
    for name in ("ready", "resume", "mark-master", "approve", "record-copy", "close"):
        sub = subs.add_parser(name)
        sub.add_argument("--job", required=True)
        if name in {"mark-master", "record-copy"}:
            sub.add_argument("--source", required=True, help="Path relative to payload")
        if name == "approve":
            sub.add_argument("--asset", action="append", required=True)
            sub.add_argument("--note", required=True, help="Actual user selection evidence, not a self-review")
        if name == "record-copy":
            sub.add_argument("--destination", required=True)
            sub.add_argument("--kind", choices=["delivery", "master"], required=True)
        if name == "close":
            sub.add_argument("--result", choices=["delivered", "cancelled"], required=True)
            sub.add_argument("--note", required=True, help="User cancellation or completed delivery evidence")
    args = parser.parse_args()
    try:
        if hasattr(args, "note") and not args.note.strip():
            raise ValueError("A non-empty user decision or completion note is required")
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
