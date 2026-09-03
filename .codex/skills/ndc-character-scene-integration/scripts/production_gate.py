#!/usr/bin/env python3
"""Fail closed when an NDC character-in-scene batch bypasses required gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ALLOWED_TECHNICAL_STATUS = {
    "NOT_RUN",
    "TECHNICAL_FILE_PASS",
    "TECHNICAL_FILE_FAIL",
}
ALLOWED_PORTAL_STATE = {"open", "offscreen", "opened-during-transition"}
REQUIRED_VISUAL_STAGES = {
    "pre-generation": {"exact-pose-whitebox"},
    "post-generation": {
        "exact-pose-whitebox",
        "contextual-local-result",
        "matte-extraction",
        "pre-composite-registration",
        "final-full-composite",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_fields(data: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")


def resolve_path(raw: str | Path, ledger_path: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ledger_path.parent / path
    return path.resolve()


def validate_file_ref(
    reference: dict[str, Any],
    label: str,
    ledger_path: Path,
    schemas: set[str] | None = None,
) -> tuple[Path, dict[str, Any] | None]:
    require_fields(reference, ("path", "sha256"), label)
    path = resolve_path(reference["path"], ledger_path)
    if not path.is_file():
        raise ValueError(f"{label} artifact is missing: {path}")
    if sha256(path).lower() != str(reference["sha256"]).lower():
        raise ValueError(f"{label} hash does not match: {path}")
    data = load_json(path) if schemas is not None or path.suffix.lower() == ".json" else None
    if schemas is not None:
        assert data is not None
        if data.get("schema") not in schemas:
            raise ValueError(
                f"{label} schema {data.get('schema')!r} is not one of {sorted(schemas)}."
            )
    return path, data


def require_nonempty_refs(
    values: Any,
    label: str,
    ledger_path: Path,
    schemas: set[str] | None = None,
) -> list[dict[str, Any] | None]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{label} must contain at least one artifact reference.")
    loaded = []
    for index, reference in enumerate(values):
        if not isinstance(reference, dict):
            raise ValueError(f"{label}[{index}] must be an object.")
        _, data = validate_file_ref(reference, f"{label}[{index}]", ledger_path, schemas)
        loaded.append(data)
    return loaded


def validate_placement_contract(data: dict[str, Any], label: str) -> None:
    require_fields(data, ("calibration", "target"), label)
    estimates = data["calibration"].get("projectedHeightEstimatesPx", [])
    groups = {
        str(item.get("independenceGroup", "")).strip()
        for item in estimates
        if str(item.get("independenceGroup", "")).strip()
    }
    if len(estimates) < 2 or len(groups) < 2:
        raise ValueError(f"{label} requires at least two independent scale anchors.")
    if data["calibration"].get("aggregationMethod") != "median-after-depth-projection":
        raise ValueError(f"{label} lacks median-after-depth-projection aggregation.")
    bands = {str(item.get("depthBand", "")).strip() for item in estimates}
    if bands != {"actor-local", "cross-depth"}:
        raise ValueError(f"{label} requires actor-local and cross-depth scale anchors.")
    for index, item in enumerate(estimates):
        if item.get("depthBand") == "cross-depth":
            evidence = item.get("projectionEvidence")
            if not isinstance(evidence, dict) or not evidence.get("perspectiveBasisIds"):
                raise ValueError(
                    f"{label}.calibration.projectedHeightEstimatesPx[{index}] lacks cross-depth projection evidence."
                )
    target = data["target"]
    if "poseDefinition" not in target:
        raise ValueError(f"{label} lacks target.poseDefinition.")
    placement_class = target.get("placementClass")
    if placement_class in {"seated", "lying"}:
        if "standingEquivalentHeightPx" not in target:
            raise ValueError(f"{label} lacks target.standingEquivalentHeightPx.")
        scale_audit = data.get("scaleAudit", target.get("scaleAudit", {}))
        if scale_audit.get("bodyScaleDriver") != "standingEquivalentHeightPx":
            raise ValueError(
                f"{label} must use standingEquivalentHeightPx as the body scale driver."
            )


def validate_staging_contract(data: dict[str, Any], label: str) -> None:
    require_fields(
        data,
        ("timelineSnapshotId", "uiSafetyReview", "characters", "occlusionGraph", "combinedWhiteboxReview"),
        label,
    )
    review = data["combinedWhiteboxReview"]
    require_fields(
        review,
        ("status", "reviewAuthority", "artifact", "artifactSha256", "checks"),
        f"{label}.combinedWhiteboxReview",
    )
    if review["status"] != "passed" or review["reviewAuthority"] != "codex-self-check":
        raise ValueError(f"{label} does not contain a passed Codex combined-whitebox review.")
    failed = [name for name, value in review["checks"].items() if value != "pass"]
    if failed:
        raise ValueError(f"{label} combined-whitebox review has failed checks: {', '.join(failed)}")


def validate_case(case: dict[str, Any], index: int, ledger_path: Path, stage: str) -> dict[str, Any]:
    label = f"cases[{index}]"
    require_fields(
        case,
        (
            "caseId",
            "branch",
            "sourceScene",
            "sourceSceneSha256",
            "technicalStatus",
            "scaleDriver",
            "affordanceContract",
            "uiSafetyReports",
            "placementContracts",
            "stagingContracts",
            "whiteboxEvidence",
            "supportContactReports",
            "castScaleReport",
            "localGenerationHandoffs",
            "visualReviewReports",
        ),
        label,
    )
    branch = case["branch"]
    if branch not in {"pure-narrative", "exploration-click-pair"}:
        raise ValueError(f"{label}.branch is unsupported: {branch}")
    scene = resolve_path(case["sourceScene"], ledger_path)
    if not scene.is_file() or sha256(scene).lower() != str(case["sourceSceneSha256"]).lower():
        raise ValueError(f"{label} source scene is missing or has changed: {scene}")
    technical_status = case["technicalStatus"]
    if technical_status not in ALLOWED_TECHNICAL_STATUS:
        raise ValueError(
            f"{label}.technicalStatus must describe file checks only; use TECHNICAL_FILE_PASS, not PASS."
        )
    allowed_scale_drivers = {
        "standing-equivalent-multi-anchor",
        "approved-card-anatomical-head-ratio-first-then-standing-equivalent-multi-anchor",
    }
    if case["scaleDriver"] not in allowed_scale_drivers:
        raise ValueError(
            f"{label} forbids target-box or alpha-box scale normalization; expected a head-first or standing-equivalent multi-anchor driver."
        )

    if "sceneAbsoluteScaleReport" not in case:
        raise ValueError(f"{label} lacks an independent fixed-scene absolute-scale report.")
    _, absolute_scale_report = validate_file_ref(
        case["sceneAbsoluteScaleReport"],
        f"{label}.sceneAbsoluteScaleReport",
        ledger_path,
        {"ndc-scene-absolute-scale-report/v1"},
    )
    if not absolute_scale_report or absolute_scale_report.get("status") != "pass":
        raise ValueError(f"{label} contains a failed fixed-scene absolute-scale report.")

    component_reports = require_nonempty_refs(
        case.get("componentPolicyReports"),
        f"{label}.componentPolicyReports",
        ledger_path,
        {"ndc-interaction-component-policy-report/v1"},
    )
    if any(report and report.get("status") != "pass" for report in component_reports):
        raise ValueError(f"{label} contains a failed interaction-component policy report.")

    _, affordance = validate_file_ref(
        case["affordanceContract"],
        f"{label}.affordanceContract",
        ledger_path,
        {"ndc-scene-affordance/v1"},
    )
    assert affordance is not None
    ui_reports = require_nonempty_refs(
        case["uiSafetyReports"],
        f"{label}.uiSafetyReports",
        ledger_path,
        {"ndc-ui-safety-report/v1"},
    )
    if any(report and report.get("status") != "pass" for report in ui_reports):
        raise ValueError(f"{label} contains a failed UI safety report.")

    placement_data = require_nonempty_refs(
        case["placementContracts"], f"{label}.placementContracts", ledger_path
    )
    for placement_index, data in enumerate(placement_data):
        assert data is not None
        validate_placement_contract(data, f"{label}.placementContracts[{placement_index}]")

    support_reports = require_nonempty_refs(
        case["supportContactReports"],
        f"{label}.supportContactReports",
        ledger_path,
        {"ndc-support-contact-report/v1"},
    )
    if any(report and report.get("status") != "pass" for report in support_reports):
        raise ValueError(f"{label} contains a failed support-contact report.")
    reported_pose_ids = {
        str(report.get("poseId")) for report in support_reports if report is not None
    }
    expected_pose_ids = {
        str(data["target"]["poseDefinition"]["poseId"])
        for data in placement_data
        if data is not None
    }
    if reported_pose_ids != expected_pose_ids:
        raise ValueError(
            f"{label}.supportContactReports do not cover the exact placement pose IDs."
        )

    _, cast_scale_report = validate_file_ref(
        case["castScaleReport"],
        f"{label}.castScaleReport",
        ledger_path,
        {"ndc-cast-scale-report/v1", "ndc-cast-scale-report/v2"},
    )
    if cast_scale_report and cast_scale_report.get("status") != "pass":
        raise ValueError(f"{label} contains a failed cast-scale report.")
    if case["scaleDriver"].startswith("approved-card-anatomical-head-ratio-first"):
        if (
            not cast_scale_report
            or cast_scale_report.get("schema") != "ndc-cast-scale-report/v2"
            or cast_scale_report.get("headScalePriority") is not True
        ):
            raise ValueError(
                f"{label} head-first scale driver requires a cast-scale v2 head-priority report."
            )
    cast_pose_ids = {
        str(actor.get("poseId"))
        for actor in (cast_scale_report or {}).get("actors", [])
    }
    if cast_pose_ids != expected_pose_ids:
        raise ValueError(f"{label}.castScaleReport does not cover the exact pose IDs.")

    staging_data = require_nonempty_refs(
        case["stagingContracts"], f"{label}.stagingContracts", ledger_path
    )
    for staging_index, data in enumerate(staging_data):
        assert data is not None
        validate_staging_contract(data, f"{label}.stagingContracts[{staging_index}]")

    whitebox = case["whiteboxEvidence"]
    require_fields(
        whitebox,
        ("kind", "isolatedActors", "combinedSnapshots", "reviewReports"),
        f"{label}.whiteboxEvidence",
    )
    if whitebox["kind"] != "3d-anatomical-mannequin-exact-pose":
        raise ValueError(
            f"{label} rejects skeleton, programmatic geometry blocks, rectangles, or filename-only whiteboxes; expected 3d-anatomical-mannequin-exact-pose."
        )
    for field in ("isolatedActors", "combinedSnapshots", "reviewReports"):
        require_nonempty_refs(
            whitebox[field], f"{label}.whiteboxEvidence.{field}", ledger_path
        )

    handoffs = require_nonempty_refs(
        case["localGenerationHandoffs"],
        f"{label}.localGenerationHandoffs",
        ledger_path,
        {"ndc-local-generation-handoff-report/v1"},
    )
    if any(
        report
        and (
            report.get("status") != "READY_FOR_CONTEXTUAL_LOCAL_GENERATION"
            or report.get("outputMode") != "contextual-local-replacement"
            or report.get("cropPolicy") != "expand-original-pixels-no-resize"
        )
        for report in handoffs
    ):
        raise ValueError(f"{label} contains a local-generation handoff that is not ready.")

    visual_reports = require_nonempty_refs(
        case["visualReviewReports"],
        f"{label}.visualReviewReports",
        ledger_path,
        {"ndc-stage-visual-review-report/v1"},
    )
    visual_stages = {str(report.get("stage")) for report in visual_reports if report}
    missing_visual_stages = REQUIRED_VISUAL_STAGES[stage] - visual_stages
    if missing_visual_stages:
        raise ValueError(
            f"{label} lacks required visual stages: {', '.join(sorted(missing_visual_stages))}."
        )
    if any(
        report
        and (
            report.get("reviewAuthority") != "codex-self-check"
            or report.get("status") != "VISUAL_REVIEW_PASS"
            or report.get("nextStageAuthorized") is not True
        )
        for report in visual_reports
        if report and report.get("stage") in REQUIRED_VISUAL_STAGES[stage]
    ):
        raise ValueError(f"{label} contains a failed or incomplete mandatory visual review.")

    if branch == "pure-narrative":
        for field, schemas in (
            ("engineTimeline", {"ndc-scene-timeline/v1"}),
            ("directingTimeline", {"ndc-directing-timeline/v1"}),
            ("timelineBoard", None),
        ):
            if field not in case:
                raise ValueError(f"{label} pure narrative case lacks {field}.")
            _, data = validate_file_ref(case[field], f"{label}.{field}", ledger_path, schemas)
            if field == "engineTimeline" and data and data.get("issues"):
                raise ValueError(f"{label}.engineTimeline still contains unresolved issues.")
        entry_checks = case.get("entryPathChecks")
        if not isinstance(entry_checks, list):
            raise ValueError(f"{label}.entryPathChecks must be a list for pure narrative cases.")
        for entry_index, entry in enumerate(entry_checks):
            entry_label = f"{label}.entryPathChecks[{entry_index}]"
            require_fields(
                entry,
                ("actorId", "entryPathId", "portalState", "visiblePortalState", "clearOfFrozenActors"),
                entry_label,
            )
            if entry["portalState"] not in ALLOWED_PORTAL_STATE:
                raise ValueError(f"{entry_label} does not provide a usable entry portal.")
            if entry["visiblePortalState"] == "closed" and entry["portalState"] != "opened-during-transition":
                raise ValueError(
                    f"{entry_label} claims entry through a visibly closed portal without an opening transition."
                )
            if entry["clearOfFrozenActors"] is not True:
                raise ValueError(f"{entry_label} intersects a frozen actor or support zone.")
    else:
        state_pairs = case.get("statePairs")
        if not isinstance(state_pairs, list) or not state_pairs:
            raise ValueError(f"{label} exploration case requires statePairs.")
        for pair_index, pair in enumerate(state_pairs):
            pair_label = f"{label}.statePairs[{pair_index}]"
            require_fields(
                pair,
                ("contract", "idle", "active", "reuseMasterTransform", "statesIndependentlyNormalized"),
                pair_label,
            )
            if pair["reuseMasterTransform"] is not True or pair["statesIndependentlyNormalized"] is not False:
                raise ValueError(
                    f"{pair_label} must reuse the idle master transform and forbid independent normalization."
                )
            validate_file_ref(pair["contract"], f"{pair_label}.contract", ledger_path, {"ndc-exploration-state-pair/v1"})
            validate_file_ref(pair["idle"], f"{pair_label}.idle", ledger_path)
            validate_file_ref(pair["active"], f"{pair_label}.active", ledger_path)

    if stage == "post-generation":
        gaze_reports = require_nonempty_refs(
            case.get("gazeConformanceReports"),
            f"{label}.gazeConformanceReports",
            ledger_path,
            {"ndc-gaze-conformance-report/v1"},
        )
        if any(report and report.get("status") != "pass" for report in gaze_reports):
            raise ValueError(f"{label} contains a failed final gaze-conformance report.")
        matte_reports = require_nonempty_refs(
            case.get("matteReports"),
            f"{label}.matteReports",
            ledger_path,
            {"ndc-conservative-matte-report/v2"},
        )
        if any(
            report and report.get("status") != "TECHNICAL_FILE_PASS"
            for report in matte_reports
        ):
            raise ValueError(f"{label} contains a failed or legacy matte report.")
        finals = require_nonempty_refs(
            case.get("finalConformanceContracts"),
            f"{label}.finalConformanceContracts",
            ledger_path,
        )
        for final_index, data in enumerate(finals):
            assert data is not None
            review = data.get("formalConformanceReview")
            if not review or review.get("status") != "passed" or review.get("reviewAuthority") != "codex-self-check":
                raise ValueError(
                    f"{label}.finalConformanceContracts[{final_index}] lacks passed Codex formal review."
                )

    return {
        "caseId": case["caseId"],
        "branch": branch,
        "stage": stage,
        "status": "evidence-complete",
    }


def validate_ledger(ledger_path: Path) -> dict[str, Any]:
    data = load_json(ledger_path)
    require_fields(data, ("schema", "stage", "processRoot", "cases"), "ledger")
    if data["schema"] != "ndc-scene-integration-production-ledger/v2":
        raise ValueError("ledger.schema must be ndc-scene-integration-production-ledger/v2.")
    stage = data["stage"]
    if stage not in {"pre-generation", "post-generation"}:
        raise ValueError("ledger.stage must be pre-generation or post-generation.")
    process_root = resolve_path(data["processRoot"], ledger_path)
    if not process_root.is_dir():
        raise ValueError(f"ledger.processRoot does not exist: {process_root}")
    cases = data["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("ledger.cases cannot be empty.")
    results = [validate_case(case, index, ledger_path, stage) for index, case in enumerate(cases)]
    return {
        "schema": "ndc-scene-integration-production-ledger-report/v2",
        "ledger": str(ledger_path.resolve()),
        "ledgerSha256": sha256(ledger_path),
        "stage": stage,
        "status": "EVIDENCE_GATE_PASS",
        "cases": results,
        "note": "EVIDENCE_GATE_PASS proves required evidence coverage, not artistic approval.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate_ledger(args.ledger)
        if args.report:
            write_json(args.report, report)
        print(
            f"EVIDENCE_GATE_PASS cases={len(report['cases'])} stage={report['stage']}"
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=__import__("sys").stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
