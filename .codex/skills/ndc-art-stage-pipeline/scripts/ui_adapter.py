"""Read-only UI handoff evidence gates; never initialize or accept production jobs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re

from PIL import Image

SIBLING = Path(__file__).resolve().parents[2] / "ndc-generate-ui-portraits"


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


workflow = _module("ui_pipeline_workflow", SIBLING / "scripts/art_workflow_state.py")
ui = _module("ui_pipeline_portrait", SIBLING / "scripts/ui_portrait.py")


def _need(ok, message):
    if not ok:
        raise ValueError(message)


def _text(value, label):
    _need(isinstance(value, str) and value.strip(), label + " must be nonempty text")
    return value


def _reference(item, base):
    _need(isinstance(item, dict), "file reference must be an object")
    _text(item.get("path"), "file path")
    _need(isinstance(item.get("sha256"), str) and re.fullmatch(r"[0-9a-fA-F]{64}", item["sha256"]), "invalid file SHA-256")
    return workflow.ref(item, base)


def _files(container, base):
    entries = container.get("files")
    _need(isinstance(entries, list), "files must be an array")
    result = {}
    for raw in entries:
        item = _reference(raw, base)
        role = _text(item.get("role"), "file role")
        _need(role not in result, "duplicate file role: " + role)
        result[role] = item
    return result


def _same(a, b):
    return Path(a["path"]).resolve() == Path(b["path"]).resolve() and a["sha256"].lower() == b["sha256"].lower()


def _has(refs, target):
    return any(_same(item, target) for item in refs)


def _load(journal):
    journal = Path(journal).resolve()
    header, events, _ = workflow.load(journal)
    return header, workflow.state(header, events)


def _binding(accepted):
    request = accepted["request_data"]
    return workflow.digest({"context_sha256": request["context_sha256"], "outputs": request["outputs"]})


def accepted_binding(journal_path, job_id):
    """Freeze one current accepted context/output binding, never the whole journal hash."""
    try:
        _, jobs = _load(journal_path)
        _need(job_id in jobs, "unknown accepted job: " + str(job_id))
        return _binding(workflow.current_acceptance(jobs, job_id))
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(str(exc)) from exc


def _ancestors(jobs, key):
    found, todo = set(), list(jobs[key]["depends_on"])
    while todo:
        parent = todo.pop()
        _need(parent in jobs and parent != key, "invalid job dependency")
        if parent not in found:
            found.add(parent)
            todo.extend(jobs[parent]["depends_on"])
    return found


def _job(jobs, key, character, purpose=None):
    _need(key in jobs, "unknown UI job: " + str(key))
    job = jobs[key]
    _need(job["requirements"].get("identity_id") == character, "UI job belongs to another character: " + key)
    if purpose:
        _need(job["requirements"].get("purpose") == purpose, "wrong UI stage purpose: " + key)
    return job


def _accepted_output(jobs, key, target):
    accepted = workflow.current_acceptance(jobs, key)
    _need(_has(accepted["request_data"]["outputs"], target), "file is not the current accepted output: " + key)
    return accepted


def _release(packet, base):
    _need(isinstance(packet, dict) and packet.get("schema") == "ndc-art-stage-packet/v1", "invalid stage packet schema")
    _need(packet.get("pipeline_kind") == "ui_portrait", "wrong pipeline kind")
    _need(packet.get("execution_mode") in {"validation", "production"}, "explicit execution_mode required")
    _text(packet.get("unit_id"), "unit_id")
    _text(packet.get("producer_task_id"), "producer_task_id")
    _need(type(packet.get("revision")) is int and packet["revision"] >= 1, "positive packet revision required")
    files = _files(packet, base)
    p, authority = packet["payload"], packet["authority"]
    _need(isinstance(p, dict) and isinstance(authority, dict), "payload and authority must be objects")
    journal = Path(_text(authority.get("journal"), "authority.journal"))
    _need(journal.is_absolute(), "authority journal must be absolute")
    _need(all(Path(f["path"]).resolve() != journal.resolve() for f in files.values()), "mutable journal must not be included in hashed packet files")
    header, jobs = _load(journal)
    _need(header["plan"]["task_id"] == packet["producer_task_id"], "journal belongs to a different producer task")
    for scope in ("upstream_jobs", "downstream_jobs"):
        items = authority.get(scope)
        _need(isinstance(items, list) and items and all(isinstance(x, str) and x in jobs for x in items)
              and len(set(items)) == len(items), "invalid " + scope)
    upstream, downstream = set(authority["upstream_jobs"]), set(authority["downstream_jobs"])
    _need(not upstream & downstream, "upstream and downstream overlap")
    workflow.status(journal, require_all=True, selected=authority["upstream_jobs"])
    bindings = p.get("acceptance_bindings")
    _need(isinstance(bindings, dict) and set(bindings) == upstream, "bind every declared upstream job, not the whole journal")
    for key in upstream:
        _need(bindings[key] == _binding(workflow.current_acceptance(jobs, key)), "upstream acceptance changed: " + key)

    character = _text(p.get("character_id"), "character_id")
    _text(p.get("stem"), "stem")
    u0, master_id = p["u0_job_id"], p["master_job_id"]
    _need({u0, master_id} <= upstream and u0 != master_id, "upstream scope must include U0 and U1")
    source_job = _job(jobs, u0, character, "ui-source")
    master_job = _job(jobs, master_id, character, "ui-master")
    _need(u0 in _ancestors(jobs, master_id), "U1 must depend on accepted U0")
    master = files[p.get("master_role", "ui_master")]
    master_acceptance = _accepted_output(jobs, master_id, master)
    _need(any(x.get("role") == "ui_master" and _same(x, master) for x in master_acceptance["request_data"]["outputs"]), "U1 output must be ui_master")
    with Image.open(master["path"]) as image:
        image.load()
        _need(image.width * 4 == image.height * 3 and image.mode in {"RGB", "RGBA"}, "invalid 3:4 native UI master")
        _need(image.mode != "RGBA" or image.getchannel("A").getextrema() == (255, 255), "UI master must be opaque")

    roles = p["source_roles"]
    _need(set(roles) == {"card", "portrait", "approval"}, "card, portrait and approval roles required")
    sources = {key: files[role] for key, role in roles.items()}
    source_acceptance = workflow.current_acceptance(jobs, u0)
    u0_evidence = source_job["inputs"] + source_acceptance["request_data"]["outputs"]
    for target in sources.values():
        _need(_has(u0_evidence, target), "source or approval evidence is not bound to accepted U0")
    for key in ("card", "portrait"):
        _need(_has(master_job["inputs"], sources[key]), "U1 input differs from frozen " + key)
    approval = workflow.read(sources["approval"]["path"])
    _need(approval.get("schema") == "ndc-ui-source-approval/v1" and approval.get("character_id") == character
          and approval.get("approved") is True, "approved identity/source evidence required")
    _text(approval.get("approval_basis"), "source approval basis")
    for key in ("card", "portrait"):
        _need(approval.get(key + "_sha256", "").lower() == sources[key]["sha256"], "approval refers to a different " + key)
    manual = approval.get("manual_completion")
    _need(isinstance(manual, dict) and type(manual.get("required")) is bool, "manual source applicability must be explicit")
    expected_manual = "received" if manual["required"] else "not_required"
    _need(p.get("manual_completion") == expected_manual and manual.get("status") == expected_manual, "U0 manual shoulder source has not been received")
    if manual["required"]:
        _need(source_job["source_decision"]["mode"] == "manual_input", "manual source may not be claimed as automatic completion")
        _text(manual.get("confirmation"), "actual manual return confirmation")
        original = _reference(manual.get("original_portrait"), Path(sources["approval"]["path"]).parent)
        _need(_has(u0_evidence, original), "original portrait missing from U0 manual provenance")
    synthetic = approval.get("synthetic") is True
    if packet["execution_mode"] == "production":
        _need(not synthetic and not any(jobs[k]["requirements"].get("synthetic") is True for k in upstream | downstream), "synthetic fixture cannot enter production")

    requested = p.get("requested_profiles")
    _need(isinstance(requested, list) and requested and len(set(requested)) == len(requested)
          and set(requested) <= {"big", "small"}, "invalid requested profiles")
    profile_jobs, preserved = p.get("profile_jobs"), p.get("preserved_profiles", {})
    _need(isinstance(profile_jobs, dict) and set(profile_jobs) == set(requested), "profile jobs must exactly match requested missing profiles")
    _need(isinstance(preserved, dict) and not set(preserved) & set(requested)
          and set(preserved) | set(requested) == {"big", "small"}, "both profile coverage and preserved/requested separation required")
    _need(p.get("mode") == ("missing_profiles" if preserved else "new_pair"), "UI production mode disagrees with coverage")
    for profile, key in profile_jobs.items():
        _need(key in downstream, "requested profile missing from downstream authority")
        job = _job(jobs, key, character, "ui-" + profile)
        _need(master_id in _ancestors(jobs, key), "profile job is not a descendant of this U1")
        _need(job["source_decision"]["mode"] != "reuse", "a requested missing profile cannot be claimed as existing reuse")
    _need(len(set(profile_jobs.values())) == len(profile_jobs), "one independently accepted job per requested profile")
    for profile, kept in preserved.items():
        key, target = kept["job_id"], files[kept["file_role"]]
        _need(key in upstream, "preserved profile missing from upstream authority")
        job = _job(jobs, key, character, "ui-" + profile)
        # A prior accepted derive/repair job is also preservable; never require a
        # new reuse job or a rewritten history just to retain approved bytes.
        _accepted_output(jobs, key, target)
        with Image.open(target["path"]) as image:
            _need(image.format == "PNG" and image.mode == "RGB" and image.size == tuple(ui.profiles()[profile]["size"]), "invalid preserved UI profile")
    return {"valid": True, "pipeline_kind": "ui_portrait", "execution_mode": packet["execution_mode"],
            "character_id": character, "requested_profiles": requested,
            "preserved_profiles": list(preserved), "master_sha256": master["sha256"],
            "acceptance_bindings": bindings, "meaning": "Current evidence binding; no new artistic approval."}, jobs, files


def validate_release(packet, base: Path) -> dict:
    try:
        return _release(packet, Path(base))[0]
    except (OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError(str(exc)) from exc


def validate_result(packet, result, base: Path) -> dict:
    try:
        release, jobs, source_files = _release(packet, Path(base))
        _need(isinstance(result, dict), "result must be an object")
        status = result.get("status")
        _need(status in {"PASS", "FAIL", "WAITING_MANUAL", "VALIDATION_COMPLETE"}, "invalid UI result status")
        files = _files(result, base)
        payload = result.get("payload")
        _need(isinstance(payload, dict), "UI result payload required")
        if status in {"FAIL", "WAITING_MANUAL"}:
            _text(payload.get("reason"), "actual failure/manual reason")
            _need(payload.get("return_stage") in {"U0", "U1", "U2", "U3"}, "explicit return stage required")
            return {"valid": True, "status": status, "accepted": False, "return_stage": payload["return_stage"], "meaning": "Actual return only; no PASS or budget reset."}
        expected = "VALIDATION_COMPLETE" if packet["execution_mode"] == "validation" else "PASS"
        _need(status == expected, "validation cannot report production PASS or vice versa")
        if status == "VALIDATION_COMPLETE":
            _need(payload.get("validation_only") is True, "synthetic result must explicitly be validation_only")
        p = packet["payload"]
        profile_roles, receipt_roles = payload.get("profile_roles"), payload.get("receipts")
        _need(isinstance(profile_roles, dict) and set(profile_roles) == set(p["requested_profiles"]), "result must contain only requested profiles")
        _need(isinstance(receipt_roles, list) and receipt_roles and len(set(receipt_roles)) == len(receipt_roles), "actual composition receipts required")
        master = source_files[p.get("master_role", "ui_master")]
        observed = set()
        for role in receipt_roles:
            receipt_ref = files[role]
            receipt = ui.read_json(receipt_ref["path"])
            _need(_same(receipt["source"], master), "receipt uses a different U1 master")
            _need(_has(list(files.values()) + list(source_files.values()), receipt["landmarks"]), "receipt landmarks must be a declared hashed handoff/result file")
            audited = ui.audit(receipt_ref["path"])
            _need(audited["technical_status"] == "TECHNICAL_PASS", "UI crop technical gate failed")
            for profile, entry in receipt["profiles"].items():
                _need(profile in profile_roles and profile not in observed, "receipt duplicates or redraws a preserved profile")
                target = files[profile_roles[profile]]
                expected_ref = {"path": str((Path(receipt_ref["path"]).parent / entry["path"]).resolve()), "sha256": entry["sha256"]}
                _need(_same(target, expected_ref), "result file differs from audited crop")
                _need(Path(target["path"]).name == p["stem"] + "_" + profile + ".png", "wrong character stem/profile output")
                if status == "PASS":
                    _accepted_output(jobs, p["profile_jobs"][profile], target)
                observed.add(profile)
        _need(observed == set(p["requested_profiles"]), "missing audited profile")
        if status == "PASS":
            workflow.status(packet["authority"]["journal"], require_all=True, selected=packet["authority"]["downstream_jobs"])
        _need(not ({Path(x["path"]).resolve() for x in files.values()} & {Path(x["path"]).resolve() for x in source_files.values()}), "downstream result must not overwrite/relabel frozen upstream files")
        return {**release, "status": status, "accepted": status == "PASS", "profiles_checked": sorted(observed), "preserved_bytes_unchanged": True,
                "meaning": "Synthetic protocol completion only." if status == "VALIDATION_COMPLETE" else "Existing UI technical gate and original journal current acceptance verified."}
    except (OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError(str(exc)) from exc
