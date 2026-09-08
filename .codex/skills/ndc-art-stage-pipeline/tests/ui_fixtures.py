"""Isolated synthetic fixtures only. Never import this module for production work."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import re
import shutil
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ui_adapter.py"
spec = importlib.util.spec_from_file_location("ui_adapter_fixture_target", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
workflow, ui = adapter.workflow, adapter.ui
_need, _files = adapter._need, adapter._files
accepted_binding = adapter.accepted_binding
validate_release, validate_result = adapter.validate_release, adapter.validate_result

def _write_fixture(path, data):
    workflow.frozen_write(path, data)
    return Path(path)


def _fixture_accept(journal, key, outputs, root, validator):
    """Synthetic current-evidence fixture. Never a human/artistic approval."""
    outputs_file = _write_fixture(root / (key + "-outputs.json"), outputs)
    request_file = root / (key + "-request.json")
    workflow.prepare_review(journal, key, outputs_file, request_file)
    request = workflow.read(request_file)
    context = request["context"]
    inputs = list(context["inputs"])
    for parent in context["parents"].values():
        inputs.extend(parent["outputs"])
    record = {"schema": "ndc-stage-visual-self-check/v1", "synthetic": True,
              "visual_check_status": "PASS", "stage_id": key,
              "reviewer": "SYNTHETIC_CONTRACT_FIXTURE_NOT_ART_APPROVAL", "reviewed_at": "synthetic-fixture",
              "workflow_context_sha256": request["context_sha256"], "inputs": inputs, "outputs": outputs,
              "criteria": [{"name": name, "applicable": True, "status": "PASS", "finding": "Synthetic contract setup only; no real character was reviewed or approved."} for name in context["required_criteria"]],
              "views": [{**outputs[0], "kind": kind} for kind in ("whole_100", "local_200_or_tiles")]}
    record_file = _write_fixture(root / (key + "-synthetic-record.json"), record)
    workflow.mutate(journal, key, "accept", {"request": str(request_file), "records": [str(record_file)], "validator": str(validator)})


def create_fixture(workroot, unit_id="A", producer_task_id="synthetic-ui-producer", *, missing_profiles=None, manual_required=True):
    """Create a fresh, explicitly synthetic release packet. Never changes real assets.

    Return {packet, base, journal, landmarks, fixture_validator}; producer_task_id
    may be the real validation producer task. No model or Photoshop is called.
    """
    root = Path(workroot).resolve()
    _need(not root.exists(), "fixture workroot must be a new isolated directory")
    _need(isinstance(unit_id, str) and re.fullmatch(r"[A-Za-z0-9_-]+", unit_id), "safe fixture unit_id required")
    requested = ["big", "small"] if missing_profiles is None else list(missing_profiles)
    _need(requested and set(requested) <= {"big", "small"} and len(set(requested)) == len(requested), "invalid fixture profiles")
    root.mkdir(parents=True)
    for name, size, color in (("card", (600, 800), (40, 60, 80)), ("original", (600, 800), (70, 80, 90)), ("portrait", (600, 800), (80, 90, 100)), ("master", (900, 1200), (30, 70, 100))):
        Image.new("RGB", size, color).save(root / (name + ".png"))
    card = workflow.snapshot(root / "card.png", "approved_card")
    portrait = workflow.snapshot(root / "portrait.png", "approved_portrait")
    original = workflow.snapshot(root / "original.png", "original_portrait")
    master = workflow.snapshot(root / "master.png", "ui_master")
    approval_data = {"schema": "ndc-ui-source-approval/v1", "synthetic": True, "character_id": unit_id,
                     "approved": True, "approval_basis": "Synthetic provenance fixture only; not a real character approval.",
                     "card_sha256": card["sha256"], "portrait_sha256": portrait["sha256"],
                     "manual_completion": {"required": manual_required, "status": "received" if manual_required else "not_required",
                                           "confirmation": "Synthetic manual-return contract; no real shoulder edit.", "original_portrait": original}}
    approval_path = _write_fixture(root / "source-approval.synthetic.json", approval_data)
    approval = workflow.snapshot(approval_path, "source_approval")
    landmarks = _write_fixture(root / "landmarks.synthetic.json", {"source_sha256": master["sha256"], "left_eye": [410, 450], "right_eye": [490, 450], "chin": [450, 750], "face_center_x": 450, "reviewer": "SYNTHETIC_FIXTURE", "note": "Synthetic coordinate fixture; no real face landmark annotation."})
    u0, u1 = unit_id + "-U0", unit_id + "-U1"
    def job(key, purpose, mode, inputs, parents, outputs):
        return {"job_id": key, "asset_key": "synthetic:" + unit_id + ":" + purpose,
                "requirements": {"identity_id": unit_id, "purpose": purpose, "synthetic": True},
                "source_decision": {"mode": mode, "evidence": "Synthetic contract fixture; never real production or artistic approval."},
                "inputs": inputs, "depends_on": parents, "limits": {"model": 0, "technical": 0},
                "history": {}, "required_criteria": ["synthetic_contract"], "output_roles": outputs}
    jobs = [job(u0, "ui-source", "manual_input" if manual_required else "reuse", [card, portrait, approval, original], [], ["approved_portrait"]),
            job(u1, "ui-master", "reuse", [card, portrait], [u0], ["ui_master"])]
    profile_jobs, preserved, files = {}, {}, [master, card, portrait, approval, original]
    upstream = [u0, u1]
    for profile in ("big", "small"):
        key = unit_id + "-" + profile
        if profile in requested:
            profile_jobs[profile] = key
            jobs.append(job(key, "ui-" + profile, "derive", [master], [u1], ["ui_" + profile]))
        else:
            path = root / ("historical_" + profile + ".png")
            Image.new("RGB", tuple(ui.profiles()[profile]["size"]), (20, 30, 40)).save(path)
            item = workflow.snapshot(path, "preserved_" + profile)
            files.append(item)
            preserved[profile] = {"file_role": item["role"], "job_id": key}
            upstream.append(key)
            jobs.append(job(key, "ui-" + profile, "reuse", [item], [], [item["role"]]))
    unrelated = unit_id + "-unrelated"
    jobs.append(job(unrelated, "unrelated", "derive", [], [], ["unrelated"]))
    plan = _write_fixture(root / "production-plan.synthetic.json", {"schema": workflow.PLAN, "task_id": producer_task_id, "jobs": jobs})
    journal = root / "production-journal.synthetic.jsonl"
    workflow.initialize(plan, journal)
    validator = root / "synthetic-contract-validator.py"
    validator.write_text('import json,sys\np=sys.argv[sys.argv.index("--record")+1]\nd=json.load(open(p,encoding="utf-8"))\nsys.exit(0 if d.get("synthetic") is True and d.get("reviewer")=="SYNTHETIC_CONTRACT_FIXTURE_NOT_ART_APPROVAL" else 2)\n', encoding="utf-8")
    _fixture_accept(journal, u0, [portrait], root, validator)
    _fixture_accept(journal, u1, [master], root, validator)
    for profile, info in preserved.items():
        _fixture_accept(journal, info["job_id"], [next(f for f in files if f["role"] == info["file_role"])], root, validator)
    packet = {"schema": "ndc-art-stage-packet/v1", "pipeline_kind": "ui_portrait", "execution_mode": "validation",
              "unit_id": unit_id, "revision": 1, "producer_task_id": producer_task_id, "files": files,
              "authority": {"journal": str(journal), "upstream_jobs": upstream, "downstream_jobs": list(profile_jobs.values())},
              "payload": {"character_id": unit_id, "stem": "Synthetic_" + unit_id, "mode": "missing_profiles" if preserved else "new_pair",
                          "u0_job_id": u0, "master_job_id": u1, "master_role": "ui_master",
                          "source_roles": {"card": "approved_card", "portrait": "approved_portrait", "approval": "source_approval"},
                          "manual_completion": "received" if manual_required else "not_required", "requested_profiles": requested,
                          "profile_jobs": profile_jobs, "preserved_profiles": preserved,
                          "acceptance_bindings": {key: accepted_binding(journal, key) for key in upstream}}}
    validate_release(packet, root)
    return {"packet": packet, "base": str(root), "journal": str(journal), "landmarks": str(landmarks), "fixture_validator": str(validator)}


def complete_fixture(packet, base, landmarks=None):
    """Actually crop synthetic pixels, with no downstream artistic acceptance/write."""
    root = Path(base).resolve()
    _need(packet.get("execution_mode") == "validation", "fixture completion only supports validation")
    validate_release(packet, root)
    files = _files(packet, root)
    approval = workflow.read(files[packet["payload"]["source_roles"]["approval"]]["path"])
    _need(approval.get("synthetic") is True, "fixture crop requires synthetic source")
    p = packet["payload"]
    requested = p["requested_profiles"]
    work = Path(packet.get("work_directory", root / "synthetic-crops")).resolve()
    work.mkdir(parents=True, exist_ok=True)
    frozen_landmarks = work / "landmarks.synthetic.json"
    _need(not frozen_landmarks.exists(), "fixture landmarks destination already exists")
    shutil.copyfile(landmarks or root / "landmarks.synthetic.json", frozen_landmarks)
    # The coordinator pre-creates work_directory; compose needs a fresh child.
    out = work / "crops"
    receipt = ui.compose(files[p["master_role"]]["path"], frozen_landmarks, p["stem"], out, "both" if len(requested) == 2 else requested[0])
    result_files = [workflow.snapshot(out / "composition.json", "composition"), workflow.snapshot(receipt["landmarks"]["path"], "landmarks")]
    profile_roles = {}
    for profile, entry in receipt["profiles"].items():
        role = "ui_" + profile
        profile_roles[profile] = role
        result_files.append(workflow.snapshot(out / entry["path"], role))
    result = {"status": "VALIDATION_COMPLETE", "files": result_files, "payload": {"validation_only": True, "receipts": ["composition"], "profile_roles": profile_roles}}
    validate_result(packet, result, root)
    return result
