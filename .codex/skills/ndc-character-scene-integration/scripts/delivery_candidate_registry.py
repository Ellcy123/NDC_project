from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import uuid
from pathlib import Path

from PIL import Image


REGISTRATION_SCHEMA = "ndc-delivery-candidate-registration/v2"
MANIFEST_SCHEMA = "ndc-delivery-candidate-status/v2"
LEGACY_MANIFEST_SCHEMA = "ndc-delivery-candidate-status/v1"
SCOPE_SCHEMA = "ndc-delivery-candidate-scope/v1"
INVENTORY_SCHEMA = "ndc-delivery-candidate-inventory/v1"
ALLOWED_ROLES = {"delivery_candidate", "selected_reference"}
ALLOWED_CATEGORIES = {"场景", "道具", "角色", "角色表情", "角色融入场景"}
CURRENT_STATES = {
    "DELIVERY_CANDIDATE_PENDING_REVIEW",
    "DELIVERY_CANDIDATE_REVIEW_PASS",
    "DELIVERY_CANDIDATE_REVIEW_FAILED_MOVE_ELIGIBLE",
}
ALL_STATES = CURRENT_STATES | {"DELIVERY_CANDIDATE_SUPERSEDED"}
CANDIDATE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
UNIT_RE = re.compile(r"^Unit[1-9][0-9]*$")
XY_NAME_RE = re.compile(r"__XY_x(-?[0-9]+)_y(-?[0-9]+)$", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def configured_root(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f"Missing {name}. Run through scripts/art_pipeline/ndc_art.py run so roots are injected."
        )
    root = Path(value).expanduser()
    if not root.is_absolute():
        raise ValueError(f"{name} must be absolute.")
    return root.resolve()


def is_within(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def require_fields(value: dict, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if name not in value]
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")


def resolve_reference(reference: dict, owner_path: Path, label: str) -> tuple[Path, str]:
    if not isinstance(reference, dict):
        raise ValueError(f"{label} must be an object.")
    require_fields(reference, ("path", "sha256"), label)
    path = Path(str(reference["path"])).expanduser()
    if not path.is_absolute():
        path = owner_path.parent / path
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"{label}.path does not exist: {path}")
    expected = str(reference["sha256"]).lower()
    actual = sha256_file(path)
    if expected != actual:
        raise ValueError(f"{label}.sha256 does not match current bytes: {path}")
    return path, actual


def verify_image(path: Path) -> dict:
    try:
        with Image.open(path) as image:
            image.load()
            has_mixed_alpha = False
            if "A" in image.getbands():
                extrema = image.getchannel("A").getextrema()
                has_mixed_alpha = extrema[0] < 255 and extrema[1] > 0
            return {"format": image.format, "mode": image.mode, "hasMixedAlpha": has_mixed_alpha}
    except Exception as exc:
        raise ValueError(f"Candidate must be a readable raster image: {path}: {exc}") from exc


def validate_scene_placement(value: object, role: str, candidate_name: str, image_facts: dict, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must explicitly declare SCENE_READY_RGBA or NOT_SCENE_PLACEABLE")
    mode = value.get("mode")
    if mode not in {"SCENE_READY_RGBA", "NOT_SCENE_PLACEABLE"}:
        raise ValueError(f"{label}.mode must be SCENE_READY_RGBA or NOT_SCENE_PLACEABLE")
    basis = str(value.get("basis", "")).strip()
    if not basis:
        raise ValueError(f"{label}.basis is required")
    inferred_scene_ready = role == "delivery_candidate" and image_facts["hasMixedAlpha"]
    if inferred_scene_ready and mode != "SCENE_READY_RGBA":
        raise ValueError(f"{label} must mark a transparent delivery_candidate as SCENE_READY_RGBA")
    if mode == "SCENE_READY_RGBA":
        if role != "delivery_candidate" or not image_facts["hasMixedAlpha"]:
            raise ValueError(f"{label} SCENE_READY_RGBA requires a transparent delivery_candidate")
        x = value.get("x")
        y = value.get("y")
        if not isinstance(x, int) or isinstance(x, bool) or not isinstance(y, int) or isinstance(y, bool):
            raise ValueError(f"{label}.x and .y must be integer Photoshop top-left coordinates")
        match = XY_NAME_RE.search(Path(candidate_name).stem)
        if match is None:
            raise ValueError(f"scene-ready targetFilename must end with __XY_x<int>_y<int>")
        if (int(match.group(1)), int(match.group(2))) != (x, y):
            raise ValueError(f"targetFilename XY suffix does not match {label}.x/.y")
        return {"mode": mode, "x": x, "y": y, "basis": basis}
    if XY_NAME_RE.search(Path(candidate_name).stem) is not None:
        raise ValueError("NOT_SCENE_PLACEABLE targetFilename must not claim an XY suffix")
    return {"mode": mode, "basis": basis}


def validate_delivery_parent(value: str, delivery_root: Path) -> tuple[Path, str]:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        raise ValueError("deliveryParent must be a safe path relative to NDC_ART_DELIVERY_ROOT.")
    if len(relative.parts) < 3:
        raise ValueError("deliveryParent must contain category/Unit<n>/asset-or-scene.")
    if relative.parts[0] not in ALLOWED_CATEGORIES:
        raise ValueError("deliveryParent must start with a supported NDC art category.")
    if not UNIT_RE.fullmatch(relative.parts[1]):
        raise ValueError("deliveryParent second segment must be Unit<n>.")
    if "交付候选" in relative.parts:
        raise ValueError("deliveryParent must not include the managed 交付候选 segment.")
    resolved = (delivery_root / relative).resolve()
    if not is_within(resolved, delivery_root):
        raise ValueError("deliveryParent resolves outside NDC_ART_DELIVERY_ROOT.")
    normalized = "/".join(relative.parts)
    return resolved, normalized


def label_text(manifest: dict) -> str:
    state = manifest["state"]
    lines = [
        "交付候选（非正式 PASS）",
        f"candidate_id={manifest['candidateId']}",
        f"requirement_id={manifest['requirementId']}",
        f"artifact_role={manifest['artifactRole']}",
        f"state={state}",
        "说明：本目录是审计与制作进度的首选目标；候选状态不得当作正式批准或工程接入依据。",
    ]
    placement = manifest.get("scenePlacement")
    if isinstance(placement, dict) and placement.get("mode") == "SCENE_READY_RGBA":
        lines.append(f"scene_placement=XY_x{placement['x']}_y{placement['y']}")
    review = manifest.get("review", {})
    if review.get("status") == "FAIL":
        lines.append("复核不合格：已具备移出候选区的条件，但不会自动移动或删除。")
    return "\n".join(lines) + "\n"


def write_label(candidate_dir: Path, manifest: dict) -> None:
    label_path = candidate_dir / "00_交付候选_状态.txt"
    temporary = label_path.with_name(f".{label_path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(label_text(manifest), encoding="utf-8")
    os.replace(temporary, label_path)


def candidate_manifests(root: Path) -> list[Path]:
    return sorted(
        path.resolve()
        for path in root.rglob("candidate-status.json")
        if "交付候选" in path.parts
    )


def validate_manifest_location(path: Path, delivery_root: Path) -> None:
    resolved = path.resolve()
    if not is_within(resolved, delivery_root) or "交付候选" not in resolved.parts:
        raise ValueError("candidate manifest must stay inside a managed 交付候选 directory.")


def validate_candidate_manifest(path: Path, value: dict, delivery_root: Path) -> Path:
    validate_manifest_location(path, delivery_root)
    schema = value.get("schema")
    if schema not in {MANIFEST_SCHEMA, LEGACY_MANIFEST_SCHEMA}:
        raise ValueError("unsupported candidate manifest schema")
    require_fields(
        value,
        (
            "candidateId",
            "requirementId",
            "artifactRole",
            "state",
            "current",
            "selectedForDelivery",
            "candidateRelativePath",
            "candidateFile",
            "review",
            "formalApproval",
            "engineSyncAllowed",
        ),
        str(path),
    )
    if not CANDIDATE_ID_RE.fullmatch(str(value["candidateId"])):
        raise ValueError("candidate manifest has an invalid candidateId")
    if not str(value["requirementId"]).strip():
        raise ValueError("candidate manifest has an empty requirementId")
    if value["artifactRole"] not in ALLOWED_ROLES:
        raise ValueError("candidate manifest has an unsupported artifactRole")
    state = value["state"]
    if state not in ALL_STATES:
        raise ValueError("candidate manifest has an unsupported state")
    if not isinstance(value["current"], bool):
        raise ValueError("candidate manifest current must be boolean")
    if value["current"] != (state in CURRENT_STATES):
        raise ValueError("candidate manifest current/state relationship is invalid")
    if value["selectedForDelivery"] is not True:
        raise ValueError("candidate manifest must preserve selectedForDelivery=true")
    if value["formalApproval"] is not False or value["engineSyncAllowed"] is not False:
        raise ValueError("candidate manifest cannot grant formal approval or engine sync")
    candidate_file_value = value["candidateFile"]
    if not isinstance(candidate_file_value, dict):
        raise ValueError("candidateFile must be an object")
    require_fields(candidate_file_value, ("name", "sha256"), "candidateFile")
    candidate_name = str(candidate_file_value["name"])
    if Path(candidate_name).name != candidate_name or candidate_name in {"", ".", ".."}:
        raise ValueError("candidateFile.name must be one safe filename")
    candidate_file = (path.parent / candidate_name).resolve()
    if not is_within(candidate_file, path.parent.resolve()) or not candidate_file.is_file():
        raise ValueError("candidate image is missing or outside its candidate directory")
    expected_relative = candidate_file.relative_to(delivery_root).as_posix()
    if value["candidateRelativePath"] != expected_relative:
        raise ValueError("candidateRelativePath does not match the registered image")
    actual_hash = sha256_file(candidate_file)
    if actual_hash != str(candidate_file_value["sha256"]).lower():
        raise ValueError("candidate image hash mismatch")
    if schema == MANIFEST_SCHEMA:
        facts = verify_image(candidate_file)
        normalized_placement = validate_scene_placement(
            value.get("scenePlacement"), value["artifactRole"], candidate_name, facts, "candidate.scenePlacement"
        )
        if value.get("scenePlacement") != normalized_placement:
            raise ValueError("candidate.scenePlacement is not normalized")
    review = value["review"]
    if not isinstance(review, dict):
        raise ValueError("candidate review must be an object")
    expected_review = {
        "DELIVERY_CANDIDATE_PENDING_REVIEW": ("NOT_REVIEWED", False),
        "DELIVERY_CANDIDATE_REVIEW_PASS": ("PASS", False),
        "DELIVERY_CANDIDATE_REVIEW_FAILED_MOVE_ELIGIBLE": ("FAIL", True),
    }.get(state)
    if expected_review is not None and (
        review.get("status"), review.get("moveEligible")
    ) != expected_review:
        raise ValueError("candidate review/state relationship is invalid")
    return candidate_file


def register_candidate(spec_path: Path) -> dict:
    spec_path = spec_path.resolve()
    spec = read_json(spec_path)
    require_fields(
        spec,
        (
            "schema",
            "candidateId",
            "requirementId",
            "artifactRole",
            "source",
            "deliveryParent",
            "selectedAt",
            "selectionBasis",
            "scenePlacement",
        ),
        "registration",
    )
    if spec["schema"] != REGISTRATION_SCHEMA:
        raise ValueError(f"registration.schema must be {REGISTRATION_SCHEMA}.")
    candidate_id = str(spec["candidateId"])
    if not CANDIDATE_ID_RE.fullmatch(candidate_id):
        raise ValueError("candidateId must be 1-96 safe ASCII filename characters.")
    requirement_id = str(spec["requirementId"]).strip()
    if not requirement_id:
        raise ValueError("requirementId must be non-empty.")
    role = str(spec["artifactRole"])
    if role not in ALLOWED_ROLES:
        raise ValueError(f"artifactRole must be one of: {', '.join(sorted(ALLOWED_ROLES))}.")
    basis = str(spec["selectionBasis"]).strip()
    if not basis:
        raise ValueError("selectionBasis must explain why this image is selected for delivery.")
    selected_at = str(spec["selectedAt"]).strip()
    if not selected_at:
        raise ValueError("selectedAt must be non-empty ISO-8601 text.")
    source_path, source_hash = resolve_reference(spec["source"], spec_path, "source")
    image_facts = verify_image(source_path)
    evidence = spec.get("processEvidence", [])
    if not isinstance(evidence, list):
        raise ValueError("processEvidence must be a list.")
    normalized_evidence = []
    for index, item in enumerate(evidence):
        path, digest = resolve_reference(item, spec_path, f"processEvidence[{index}]")
        normalized_evidence.append({"path": str(path), "sha256": digest})

    delivery_root = configured_root("NDC_ART_DELIVERY_ROOT")
    delivery_parent, delivery_parent_relative = validate_delivery_parent(
        str(spec["deliveryParent"]), delivery_root
    )
    candidate_root = delivery_parent / "交付候选"
    candidate_dir = candidate_root / candidate_id
    if candidate_dir.exists():
        raise ValueError(f"Candidate directory already exists and will not be overwritten: {candidate_dir}")

    current_same_requirement: list[tuple[Path, dict]] = []
    if candidate_root.is_dir():
        for manifest_path in candidate_manifests(candidate_root):
            manifest = read_json(manifest_path)
            validate_candidate_manifest(manifest_path, manifest, delivery_root)
            if (
                manifest.get("requirementId") == requirement_id
                and manifest.get("current") is True
            ):
                current_same_requirement.append((manifest_path, manifest))
    if len(current_same_requirement) > 1:
        raise ValueError("Multiple current candidates already exist for requirementId; audit before registering.")
    supersedes = spec.get("supersedesCandidateId")
    if current_same_requirement:
        prior_path, prior = current_same_requirement[0]
        if supersedes != prior.get("candidateId"):
            raise ValueError(
                "A current candidate already exists; supersedesCandidateId must name it explicitly."
            )
    elif supersedes is not None:
        raise ValueError("supersedesCandidateId was provided but no current candidate exists.")

    target_name = str(spec.get("targetFilename") or source_path.name)
    if Path(target_name).name != target_name or target_name in {"", ".", ".."}:
        raise ValueError("targetFilename must be one filename without directories.")
    scene_placement = validate_scene_placement(
        spec["scenePlacement"], role, target_name, image_facts, "registration.scenePlacement"
    )
    staging = candidate_root / f".register-{candidate_id}-{uuid.uuid4().hex}"
    staging.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidateId": candidate_id,
        "requirementId": requirement_id,
        "artifactRole": role,
        "state": "DELIVERY_CANDIDATE_PENDING_REVIEW",
        "current": True,
        "selectedForDelivery": True,
        "selectedAt": selected_at,
        "selectionBasis": basis,
        "scenePlacement": scene_placement,
        "deliveryParent": delivery_parent_relative,
        "candidateRelativePath": "/".join(
            (*Path(delivery_parent_relative).parts, "交付候选", candidate_id, target_name)
        ),
        "candidateFile": {"name": target_name, "sha256": source_hash},
        "sourceProvenance": {"path": str(source_path), "sha256": source_hash},
        "processEvidence": normalized_evidence,
        "supersedesCandidateId": supersedes,
        "supersededByCandidateId": None,
        "review": {"status": "NOT_REVIEWED", "moveEligible": False},
        "formalApproval": False,
        "engineSyncAllowed": False,
    }
    try:
        copied = staging / target_name
        shutil.copyfile(source_path, copied)
        copied_hash = sha256_file(copied)
        if copied_hash != source_hash:
            raise RuntimeError("Candidate copy failed SHA-256 verification.")
        write_json_atomic(staging / "candidate-status.json", manifest)
        write_label(staging, manifest)
        candidate_root.mkdir(parents=True, exist_ok=True)
        os.replace(staging, candidate_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    if current_same_requirement:
        prior_path, prior = current_same_requirement[0]
        prior["state"] = "DELIVERY_CANDIDATE_SUPERSEDED"
        prior["current"] = False
        prior["supersededByCandidateId"] = candidate_id
        write_json_atomic(prior_path, prior)
        write_label(prior_path.parent, prior)

    result = dict(manifest)
    result["manifestPath"] = str((candidate_dir / "candidate-status.json").resolve())
    return result


def review_candidate(
    manifest_path: Path, result: str, reviewed_at: str, reason: str, evidence: list[dict]
) -> dict:
    delivery_root = configured_root("NDC_ART_DELIVERY_ROOT")
    manifest_path = manifest_path.resolve()
    validate_manifest_location(manifest_path, delivery_root)
    manifest = read_json(manifest_path)
    validate_candidate_manifest(manifest_path, manifest, delivery_root)
    if manifest.get("current") is not True:
        raise ValueError("Only the current delivery candidate may receive a new review result.")
    if result not in {"pass", "fail"}:
        raise ValueError("review result must be pass or fail.")
    if not reviewed_at.strip() or not reason.strip():
        raise ValueError("reviewedAt and reason are required.")
    normalized_evidence = []
    for index, item in enumerate(evidence):
        path, digest = resolve_reference(item, manifest_path, f"evidence[{index}]")
        normalized_evidence.append({"path": str(path), "sha256": digest})
    if result == "pass":
        state = "DELIVERY_CANDIDATE_REVIEW_PASS"
        move_eligible = False
        review_status = "PASS"
    else:
        state = "DELIVERY_CANDIDATE_REVIEW_FAILED_MOVE_ELIGIBLE"
        move_eligible = True
        review_status = "FAIL"
    manifest["state"] = state
    manifest["review"] = {
        "status": review_status,
        "reviewedAt": reviewed_at,
        "reason": reason,
        "evidence": normalized_evidence,
        "moveEligible": move_eligible,
    }
    write_json_atomic(manifest_path, manifest)
    write_label(manifest_path.parent, manifest)
    return manifest


def inventory_candidates(scope_path: Path | None = None) -> dict:
    delivery_root = configured_root("NDC_ART_DELIVERY_ROOT")
    manifests = candidate_manifests(delivery_root)
    entries = []
    invalid = []
    current_by_requirement: dict[str, list[dict]] = {}
    for path in manifests:
        try:
            value = read_json(path)
            candidate_file = validate_candidate_manifest(path, value, delivery_root)
            actual_hash = sha256_file(candidate_file)
            entry = {
                "candidateId": value["candidateId"],
                "requirementId": value["requirementId"],
                "artifactRole": value["artifactRole"],
                "state": value["state"],
                "current": value["current"],
                "manifestPath": str(path),
                "candidateRelativePath": value.get("candidateRelativePath"),
                "sha256": actual_hash,
                "scenePlacement": value.get("scenePlacement"),
                "legacyPlacementContract": value.get("schema") == LEGACY_MANIFEST_SCHEMA,
            }
            entries.append(entry)
            if entry["current"] is True:
                current_by_requirement.setdefault(str(entry["requirementId"]), []).append(entry)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            invalid.append({"manifestPath": str(path), "error": str(exc)})
    duplicates = {key: values for key, values in current_by_requirement.items() if len(values) > 1}
    for requirement_id, values in duplicates.items():
        invalid.append(
            {
                "requirementId": requirement_id,
                "error": "multiple current delivery candidates",
                "candidateIds": [value["candidateId"] for value in values],
            }
        )
    current_entries = [value for values in current_by_requirement.values() for value in values]
    required_ids: list[str] | None = None
    unexpected: list[str] = []
    missing: list[str] = []
    coverage_percent: float | None = None
    if scope_path is not None:
        scope_path = scope_path.resolve()
        scope = read_json(scope_path)
        require_fields(scope, ("schema", "requiredArtifactIds"), "scope")
        if scope["schema"] != SCOPE_SCHEMA:
            raise ValueError(f"scope.schema must be {SCOPE_SCHEMA}.")
        required_ids = scope["requiredArtifactIds"]
        if (
            not isinstance(required_ids, list)
            or not all(isinstance(value, str) and value for value in required_ids)
            or len(required_ids) != len(set(required_ids))
        ):
            raise ValueError("scope.requiredArtifactIds must be a distinct non-empty string list.")
        current_ids = set(current_by_requirement)
        required_set = set(required_ids)
        missing = sorted(required_set - current_ids)
        unexpected = sorted(current_ids - required_set)
        coverage_percent = round(100.0 * len(required_set & current_ids) / len(required_set), 2) if required_set else 100.0
    counts = {
        "manifestCount": len(entries),
        "currentCandidateCount": len(current_entries),
        "pendingReviewCount": sum(
            value["state"] == "DELIVERY_CANDIDATE_PENDING_REVIEW" for value in current_entries
        ),
        "reviewPassCount": sum(
            value["state"] == "DELIVERY_CANDIDATE_REVIEW_PASS" for value in current_entries
        ),
        "reviewFailedMoveEligibleCount": sum(
            value["state"] == "DELIVERY_CANDIDATE_REVIEW_FAILED_MOVE_ELIGIBLE"
            for value in current_entries
        ),
        "supersededCount": sum(
            value["state"] == "DELIVERY_CANDIDATE_SUPERSEDED" for value in entries
        ),
        "invalidCount": len(invalid),
    }
    return {
        "schema": INVENTORY_SCHEMA,
        "primaryAuditTarget": "delivery-root candidate-status.json manifests",
        "candidateCoverageIsFormalApproval": False,
        "counts": counts,
        "scope": {
            "path": str(scope_path) if scope_path else None,
            "requiredArtifactCount": len(required_ids) if required_ids is not None else None,
            "candidateCoveragePercent": coverage_percent,
            "missingRequirementIds": missing,
            "unexpectedRequirementIds": unexpected,
        },
        "currentCandidates": sorted(
            current_entries, key=lambda value: (str(value["requirementId"]), str(value["candidateId"]))
        ),
        "invalid": invalid,
    }


def parse_evidence(values: list[str]) -> list[dict]:
    result = []
    for value in values:
        if "=" not in value:
            raise ValueError("--evidence must use path=sha256.")
        path, digest = value.rsplit("=", 1)
        result.append({"path": path, "sha256": digest})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    register = subparsers.add_parser("register")
    register.add_argument("--spec", required=True, type=Path)
    review = subparsers.add_parser("review")
    review.add_argument("--manifest", required=True, type=Path)
    review.add_argument("--result", required=True, choices=("pass", "fail"))
    review.add_argument("--reviewed-at", required=True)
    review.add_argument("--reason", required=True)
    review.add_argument("--evidence", action="append", default=[])
    inventory = subparsers.add_parser("inventory")
    inventory.add_argument("--scope", type=Path)
    inventory.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "register":
        result = register_candidate(args.spec)
    elif args.command == "review":
        result = review_candidate(
            args.manifest, args.result, args.reviewed_at, args.reason, parse_evidence(args.evidence)
        )
    else:
        result = inventory_candidates(args.scope)
        if args.output:
            output = args.output.resolve()
            work_root = configured_root("NDC_ART_WORK_ROOT")
            if not is_within(output, work_root):
                raise ValueError("inventory --output must stay under NDC_ART_WORK_ROOT.")
            write_json_atomic(output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.command == "inventory" and result["counts"]["invalidCount"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
