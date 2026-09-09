#!/usr/bin/env python3
"""Portable NDC art job journal. Verifies provenance, never judges artistic quality.

Distributed byte-for-byte into the participating Skills by the maintenance task.
Only the project stage validator may validate the existing visual record schema.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

PLAN = "ndc-art-production-plan/v1"
JOURNAL = "ndc-art-production-journal/v1"
REQUEST = "ndc-art-review-request/v1"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def conversation_id(explicit=None, fallback=None):
    actual = os.environ.get('CODEX_THREAD_ID', '').strip()
    require(not (explicit and actual and explicit != actual), 'task ID must match the executing conversation')
    require(actual or explicit or fallback, 'actual conversation ID required; use CODEX_THREAD_ID or --task-id')
    return actual or explicit or fallback


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def absolute(raw, base):
    p = Path(raw)
    return (p if p.is_absolute() else Path(base) / p).resolve()


def ref(raw, base, check=True):
    require(isinstance(raw, dict) and raw.get("path") and raw.get("sha256"), "file reference needs path and sha256")
    item = dict(raw, path=str(absolute(raw["path"], base)), sha256=raw["sha256"].lower())
    if check:
        require(file_hash(item["path"]) == item["sha256"], "stale file: " + item["path"])
    return item


def snapshot(path, role=None):
    item = {"path": str(Path(path).resolve()), "sha256": file_hash(path)}
    if role:
        item["role"] = role
    return item


def frozen_write(path, data):
    """Create a new artifact; never replace earlier review or plan evidence."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def normalize_plan(data, base):
    require(data.get("schema") == PLAN and data.get("task_id"), "invalid plan schema or task_id")
    jobs = data.get("jobs")
    require(isinstance(jobs, list) and jobs, "plan requires jobs")
    ids, keys = set(), set()
    normalized = copy.deepcopy(data)
    for job in normalized["jobs"]:
        for field in ("job_id", "asset_key", "requirements", "source_decision", "limits", "required_criteria", "output_roles"):
            require(job.get(field), "job missing " + field)
        require(job["job_id"] not in ids and job["asset_key"] not in keys, "duplicate job or semantic asset_key")
        ids.add(job["job_id"])
        keys.add(job["asset_key"])
        require(isinstance(job["requirements"], dict), "requirements must be an object")
        decision = job["source_decision"]
        require(decision.get("mode") in {"reuse", "derive", "generate", "manual_input", "repair"}
                and str(decision.get("evidence", "")).strip(), "source lookup decision and evidence required")
        for field in ("required_criteria", "output_roles"):
            require(isinstance(job[field], list) and all(isinstance(v, str) and v.strip() for v in job[field])
                    and len(job[field]) == len(set(job[field])), field + " must contain distinct names")
        require(isinstance(job["limits"], dict) and all(k in {"model", "ps", "technical"}
                and type(v) is int and v >= 0 for k, v in job["limits"].items()), "invalid explicit limits")
        job["inputs"] = [ref(v, base) for v in job.get("inputs", [])]
        job["depends_on"] = job.get("depends_on", [])
        require(len(job["depends_on"]) == len(set(job["depends_on"])), "duplicate dependency")
        history = job.get("history", {})
        require(set(history) <= set(job["limits"]), "unknown history budget")
        require(all(type(v) is int and v >= 0 for v in history.values()), "history counts must be nonnegative integers")
        if any(history.values()):
            require(job.get("history_evidence"), "historical counts require evidence")
            job["history_evidence"] = [ref(v, base) for v in job["history_evidence"]]
        job["history"] = history
        job["tool_failure_limit"] = job.get("tool_failure_limit", 2)
        require(type(job["tool_failure_limit"]) is int and job["tool_failure_limit"] > 0, "invalid tool failure limit")
    by_id = {j["job_id"]: j for j in normalized["jobs"]}
    def visit(key, stack):
        require(key in by_id and key not in stack, "missing or cyclic dependency: " + key)
        for parent in by_id[key]["depends_on"]:
            visit(parent, stack | {key})
    for key in by_id:
        visit(key, set())
    return normalized


def initialize(plan_path, journal_path):
    plan_path, journal_path = Path(plan_path), Path(journal_path)
    plan = normalize_plan(read(plan_path), plan_path.parent)
    plan['conversation_task_id'] = conversation_id(plan.get('conversation_task_id'))
    header = {"schema": JOURNAL, "plan": plan, "plan_sha256": digest(plan)}
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    if journal_path.exists():
        raise FileExistsError("journal already exists: " + str(journal_path))
    registry = journal_path.parent / ".ndc-art-task-registry.json"
    lock = registry.with_name(registry.name + ".lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        mapping = read(registry) if registry.exists() else {}
        require(plan["task_id"] not in mapping, "task already has an authoritative journal; restore/resume it instead of resetting counters")
        mapping[plan["task_id"]] = {"journal": str(journal_path.resolve()), "plan_sha256": digest(plan)}
        staging = registry.with_name(registry.name + ".new")
        frozen_write(staging, mapping)
        os.replace(staging, registry)
        with journal_path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(header, ensure_ascii=False, allow_nan=False) + "\n")
    finally:
        os.close(fd)
        lock.unlink()
    return {"status": "INITIALIZED", "task_id": plan["task_id"]}


def load(journal_path):
    raw = Path(journal_path).read_text(encoding="utf-8")
    require(raw.endswith("\n"), "partial journal write: preserve and recover explicitly")
    lines = raw.splitlines()
    header = json.loads(lines[0])
    require(header.get("schema") == JOURNAL and digest(header["plan"]) == header.get("plan_sha256"), "plan modified")
    events, previous = [], digest(header)
    for number, line in enumerate(lines[1:], 1):
        event = json.loads(line)
        recorded = event.pop("event_sha256")
        require(event.get("sequence") == number and event.get("previous") == previous
                and digest(event) == recorded, "journal chain mismatch")
        event["event_sha256"] = recorded
        events.append(event)
        previous = recorded
    return header, events, previous


def state(header, events):
    jobs = {j["job_id"]: copy.deepcopy(j) for j in header["plan"]["jobs"]}
    for job in jobs.values():
        job.update(attempts={}, accepted=None, waiting=None, tool_failures=0, revision=0)
        job['_origin_task_id'] = header['plan'].get('conversation_task_id', header['plan']['task_id'])
    def invalidate(key):
        jobs[key]["accepted"] = None
        jobs[key]["revision"] += 1
        for child in jobs:
            if key in jobs[child]["depends_on"]:
                invalidate(child)
    for e in events:
        key, action, data = e["job_id"], e["action"], e["data"]
        j = jobs[key]
        if action == "attempt":
            invalidate(key)
            j["attempts"][data["submission_id"]] = dict(data, result="pending")
        elif action == 'bind_task':
            require(not j.get('_task_attribution'), 'legacy task attribution is immutable')
            j['_origin_task_id'] = data['task_id']
            j['_task_attribution'] = True
        elif action == "resolve":
            j["attempts"][data["submission_id"]].update(data)
            if data["result"] == "no_output":
                j["tool_failures"] += 1
            elif data["result"] == "produced":
                j["tool_failures"] = 0
        elif action in {"reject", "revise"}:
            invalidate(key)
            if action == "revise":
                j.update(data["changes"])
        elif action == "wait":
            j["waiting"] = data["reason"]
        elif action == "resume":
            j["waiting"] = None
        elif action == "recover_tool":
            j["tool_failures"] = 0
        elif action == "accept":
            j["accepted"] = dict(data, event_sha256=e["event_sha256"])
    return jobs


def used(job, kind, task_id=None):
    task_id = conversation_id(task_id, job.get('_origin_task_id'))
    history = job['history'].get(kind, 0) if job.get('history_task_id') == task_id else 0
    return history + sum(a['kind'] == kind and a['result'] != 'no_output'
                         and (a.get('task_id') or job['_origin_task_id']) == task_id
                         for a in job['attempts'].values())


def live_context(jobs, key, stack=None):
    stack = set() if stack is None else stack
    require(key not in stack, "dependency cycle")
    j = jobs[key]
    for item in j["inputs"]:
        ref(item, ".")
    parents = {}
    for parent in j["depends_on"]:
        accepted = current_acceptance(jobs, parent, stack | {key})
        binding = {"context_sha256": accepted["request_data"]["context_sha256"], "outputs": accepted["request_data"]["outputs"]}
        parents[parent] = {"binding_sha256": digest(binding), "outputs": binding["outputs"]}
    return {"asset_key": j["asset_key"], "requirements": j["requirements"], "inputs": j["inputs"],
            "parents": parents, "required_criteria": j["required_criteria"],
            "output_roles": j["output_roles"], "revision": j["revision"]}


def current_acceptance(jobs, key, stack=None):
    j = jobs[key]
    require(not j["waiting"], "job waiting for external input: " + key)
    accepted = j["accepted"]
    require(accepted, "no accepted current artifact: " + key)
    context = live_context(jobs, key, stack)
    request = accepted["request_data"]
    require(request["context_sha256"] == digest(context), "stale requirement/dependency: " + key)
    for item in request["outputs"] + accepted["records"] + [accepted["request"]]:
        ref(item, ".")
    for item in accepted["review_files"]:
        ref(item, ".")
    return accepted


def prepare_review(journal_path, key, outputs_path, out):
    header, events, _ = load(journal_path)
    jobs = state(header, events)
    j = jobs[key]
    require(not j["waiting"], "job waiting for external input")
    require(not any(a["result"] in {"pending", "unknown"} for a in j["attempts"].values()), "resolve pending submission before review")
    context = live_context(jobs, key)
    spec_path = Path(outputs_path)
    outputs = [ref(v, spec_path.parent) for v in read(spec_path)]
    require(len(outputs) == len(j["output_roles"]) and {v.get("role") for v in outputs} == set(j["output_roles"]), "output roles do not exactly cover the job")
    request = {"schema": REQUEST, "task_id": header["plan"]["task_id"], "job_id": key,
               "context": context, "context_sha256": digest(context), "outputs": outputs,
               "created_at": datetime.now(timezone.utc).isoformat()}
    frozen_write(out, request)
    return {"status": "REVIEW_REQUIRED", "request": snapshot(out), "context_sha256": request["context_sha256"]}


def verify_copy(journal_path, key, copies_path, out):
    header, events, _ = load(journal_path)
    jobs = state(header, events)
    accepted = current_acceptance(jobs, key)
    expected = {v["role"]: v["sha256"].lower() for v in accepted["request_data"]["outputs"]}
    copies_path = Path(copies_path)
    copies = [ref(v, copies_path.parent) for v in read(copies_path)]
    require(copies and len({v.get("role") for v in copies}) == len(copies), "distinct copied roles required")
    require(all(v.get("role") in expected and v["sha256"] == expected[v["role"]] for v in copies), "copy differs from reviewed bytes")
    result = {"schema": "ndc-art-byte-copy/v1", "status": "BYTE_IDENTITY_ONLY",
              "task_id": header["plan"]["task_id"], "job_id": key,
              "source_acceptance": accepted["event_sha256"], "context_sha256": accepted["request_data"]["context_sha256"],
              "sources": accepted["request_data"]["outputs"], "copies": copies}
    frozen_write(out, result)
    return result


def validate_acceptance(jobs, key, request_path, records, validator):
    request_path = Path(request_path).resolve()
    request = read(request_path)
    j = jobs[key]
    require(not j["waiting"], "waiting job cannot be accepted")
    require(request.get("schema") == REQUEST and request.get("job_id") == key, "wrong review request")
    context = live_context(jobs, key)
    require(request["context_sha256"] == digest(context) and request["context"] == context, "review request stale")
    require(len(request["outputs"]) == len(j["output_roles"]) and {v.get("role") for v in request["outputs"]} == set(j["output_roles"]), "review output coverage mismatch")
    expected_outputs = {(v["role"], v["sha256"].lower()): ref(v, ".") for v in request["outputs"]}
    expected_inputs = {v["sha256"].lower() for v in context["inputs"]}
    for parent in context["parents"].values():
        expected_inputs.update(v["sha256"].lower() for v in parent["outputs"])
    covered, record_refs, review_files = set(), [], []
    require(records and Path(validator).is_file(), "existing stage validator and records are required")
    for raw in records:
        path = Path(raw).resolve()
        data = read(path)
        require(data.get("schema") == "ndc-stage-visual-self-check/v1" and data.get("visual_check_status") == "PASS", "real current stage visual PASS required")
        require(data.get("workflow_context_sha256") == request["context_sha256"], "record not bound at inspection to this context")
        checks = {c.get("name"): c for c in data.get("criteria", [])}
        require(all(checks.get(name, {}).get("applicable") is True and checks[name].get("status") == "PASS"
                    and str(checks[name].get("finding", "")).strip() for name in j["required_criteria"]), "missing required visual criterion")
        input_refs = [ref(v, path.parent) for v in data.get("inputs", [])]
        require(expected_inputs <= {v["sha256"] for v in input_refs}, "review does not cover current input/dependency sources")
        output_refs = [ref(v, path.parent) for v in data.get("outputs", [])]
        for output in output_refs:
            pair = (output.get("role", data.get("role")), output["sha256"])
            require(pair in expected_outputs and output["path"] == expected_outputs[pair]["path"], "record covers an unrelated output")
            completed = subprocess.run([sys.executable, str(validator), "--record", str(path), "--artifact", output["path"]],
                                       capture_output=True, text=True, encoding="utf-8", errors="replace")
            require(completed.returncode == 0, "stage validation failed: " + completed.stdout + completed.stderr)
            covered.add(pair)
        view_refs = [ref(v, path.parent) for v in data.get("views", []) if v.get("path")]
        require({v.get("kind") for v in data.get("views", [])} >= {"whole_100", "local_200_or_tiles"}, "missing whole/local views")
        review_files += input_refs + output_refs + view_refs
        record_refs.append(snapshot(path))
    require(covered == set(expected_outputs), "missing review for an output role")
    return {"request": snapshot(request_path), "request_data": request, "records": record_refs, "review_files": review_files}


def mutate(journal_path, key, action, data, expected_previous=None):
    """One short journal writer; lock failure is explicit, never a silent lost update."""
    path = Path(journal_path)
    lock = path.with_name(path.name + ".lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, str(os.getpid()).encode())
        header, events, previous = load(path)
        require(expected_previous is None or previous == expected_previous, "journal changed; reread before continuing")
        jobs = state(header, events)
        require(key in jobs, "unknown job")
        j = jobs[key]
        if action == "attempt":
            data = dict(data, task_id=conversation_id(data.get('task_id')))
            if not header['plan'].get('conversation_task_id') and not j.get('_task_attribution'):
                require(not any(not a.get('task_id') for a in j['attempts'].values()),
                        'bind untagged calls to their verified originating conversation before new submissions')
            require(not j["waiting"], "job is waiting: " + str(j["waiting"]))
            live_context(jobs, key)
            require(j["source_decision"]["mode"] not in {"manual_input", "reuse"}, "manual or exact-reuse job cannot start automatic production")
            require(data["kind"] in j["limits"] and used(j, data["kind"], data['task_id']) < j["limits"][data["kind"]], "conversation budget exhausted or kind not enabled")
            require(data["submission_id"] and data["submission_id"] not in j["attempts"], "duplicate submission_id")
            require(not any(a["result"] in {"pending", "unknown"} for a in j["attempts"].values()), "unresolved submission: inspect existing job, do not resubmit")
            require(j["tool_failures"] < j["tool_failure_limit"], "repeated tool failure: recover the capability first")
            submission = data.get("submission")
            require(isinstance(submission, dict) and submission.get("tool") and submission.get("operation")
                    and isinstance(submission.get("arguments"), dict), "actual submission snapshot requires tool, operation and arguments")
        elif action == 'bind_task':
            require(data.get('task_id') and str(data.get('reason', '')).strip(), 'origin task ID and local evidence reason required')
            require(not header['plan'].get('conversation_task_id') and not j.get('_task_attribution'), 'legacy task attribution is immutable')
            require(not any(a.get('task_id') for a in j['attempts'].values()), 'bind legacy origin before new submissions')
        elif action == "resolve":
            prior = j["attempts"].get(data["submission_id"])
            require(prior and prior["result"] in {"pending", "unknown"}, "submission not pending")
            require(data["result"] in {"produced", "no_output", "unknown"} and data.get("evidence"), "result and evidence required")
        elif action == "revise":
            changes = data["changes"]
            require(changes and set(changes) <= {"requirements", "inputs"}, "revise cannot rename jobs, reset history, change scope/limits or dependencies")
            if "requirements" in changes:
                require(isinstance(changes["requirements"], dict) and changes["requirements"], "requirements must be nonempty")
            if "inputs" in changes:
                base = data.pop("base")
                changes["inputs"] = [ref(v, base) for v in changes["inputs"]]
            data.pop("base", None)
            if all(j[field] == value for field, value in changes.items()):
                return {"status": "ALREADY_RECORDED", "action": action, "reason": "no material change"}
        elif action in {"reject", "wait", "resume", "recover_tool"}:
            require(str(data.get("reason", "")).strip(), "specific reason/evidence required")
        elif action == "accept":
            require(not any(a["result"] in {"pending", "unknown"} for a in j["attempts"].values()), "pending submission")
            data = validate_acceptance(jobs, key, data["request"], data["records"], data["validator"])
            require(data["request_data"].get("task_id") == header["plan"]["task_id"], "wrong task review request")
            if j["accepted"] and {k: v for k, v in j["accepted"].items() if k != "event_sha256"} == data:
                return {"status": "ALREADY_RECORDED", "action": action, "reason": "same current review binding"}
        else:
            raise ValueError("unsupported journal action")
        event = {"sequence": len(events) + 1, "previous": previous, "at": datetime.now(timezone.utc).isoformat(),
                 "job_id": key, "action": action, "data": data}
        event["event_sha256"] = digest(event)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return {"status": "RECORDED", "sequence": event["sequence"], "action": action}
    finally:
        os.close(fd)
        lock.unlink()


def status(journal_path, require_all=False, selected=None):
    header, events, _ = load(journal_path)
    jobs = state(header, events)
    result = {}
    for key, job in jobs.items():
        try:
            current_acceptance(jobs, key)
            value, reason = "CURRENT_REVIEW_BOUND", None
        except (ValueError, OSError) as exc:
            value, reason = "WAITING" if job["waiting"] else "INCOMPLETE_OR_STALE", job["waiting"] or str(exc)
        result[key] = {"status": value, "reason": reason,
                       "used": {k: used(job, k) for k in job["limits"]}, "limits": job["limits"],
                       "tool_failures_since_recovery": job["tool_failures"]}
    if require_all:
        keys = selected or list(result)
        require(set(keys) <= set(result), "unknown requested job")
        require(all(result[key]["status"] == "CURRENT_REVIEW_BOUND" for key in keys), json.dumps(result, ensure_ascii=False))
    return {"task_id": header["plan"]["task_id"], 'budget_task_id': conversation_id(fallback=header['plan'].get('conversation_task_id', header['plan']['task_id'])), 'budget_scope': 'conversation', "jobs": result,
            "checked_scope": selected or list(result),
            "whole_plan_current": all(j["status"] == "CURRENT_REVIEW_BOUND" for j in result.values()),
            "meaning": "Evidence currency only; retain specialized technical, visual and delivery gates."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--plan", required=True)
    init.add_argument("--journal", required=True)
    for name in ("status", "check", "attempt", "resolve", "revise", "reject", "wait", "resume", "recover-tool", "prepare-review", "accept", "verify-copy", 'bind-task'):
        c = sub.add_parser(name)
        c.add_argument("--journal", required=True)
        if name == "check":
            c.add_argument("--job", action="append", help="Check explicit delivery subset; other unfinished jobs stay visible")
        if name not in {"status", "check"}:
            c.add_argument("--job", required=True)
        if name == "attempt":
            c.add_argument('--task-id')
            c.add_argument("--kind", choices=["model", "ps", "technical"], required=True)
            c.add_argument("--submission-id", required=True)
            c.add_argument("--submission", required=True, help="JSON with actual tool, operation and arguments; journal embeds it")
        if name == "resolve":
            c.add_argument("--submission-id", required=True)
            c.add_argument("--result", choices=["produced", "no_output", "unknown"], required=True)
            c.add_argument("--evidence", required=True)
        if name == "revise":
            c.add_argument("--changes", required=True)
        if name == 'bind-task':
            c.add_argument('--task-id', required=True)
        if name in {"reject", "wait", "resume", "recover-tool", 'bind-task'}:
            c.add_argument("--reason", required=True)
        if name == "prepare-review":
            c.add_argument("--outputs", required=True)
            c.add_argument("--out", required=True)
        if name == "verify-copy":
            c.add_argument("--copies", required=True)
            c.add_argument("--out", required=True)
        if name == "accept":
            c.add_argument("--request", required=True)
            c.add_argument("--record", action="append", required=True)
            c.add_argument("--stage-validator", required=True)
    args = p.parse_args()
    try:
        if args.command == "init":
            value = initialize(args.plan, args.journal)
        elif args.command in {"status", "check"}:
            value = status(args.journal, args.command == "check", getattr(args, "job", None))
        elif args.command == "prepare-review":
            value = prepare_review(args.journal, args.job, args.outputs, args.out)
        elif args.command == "verify-copy":
            value = verify_copy(args.journal, args.job, args.copies, args.out)
        else:
            data = {}
            if args.command == "attempt":
                data = {"kind": args.kind, "submission_id": args.submission_id, "submission": read(args.submission), 'task_id': args.task_id}
            elif args.command == 'bind-task':
                data = {'task_id': args.task_id, 'reason': args.reason}
            elif args.command == "resolve":
                data = {"submission_id": args.submission_id, "result": args.result, "evidence": args.evidence}
            elif args.command == "revise":
                data = {"changes": read(args.changes), "base": str(Path(args.changes).resolve().parent)}
            elif args.command == "accept":
                data = {"request": args.request, "records": args.record, "validator": args.stage_validator}
            else:
                data = {"reason": args.reason}
            value = mutate(args.journal, args.job, args.command.replace("-", "_"), data)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
