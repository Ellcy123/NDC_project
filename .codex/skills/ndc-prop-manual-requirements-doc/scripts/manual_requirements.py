#!/usr/bin/env python3
"""Initialize, validate, and summarize NDC prop manual-requirements records."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA = "ndc-prop-manual-requirements/v1"
SEMANTIC_CLASSES = {
    "ordinary_prop",
    "photo_clue",
    "environment_narrative",
    "minigame_only",
    "unresolved",
}
ACQUISITION_ROUTES = {
    "scene-pickup",
    "container-state",
    "detail-only",
    "environment",
    "minigame-only",
    "unresolved",
}
REQUIREMENTS = {"REQUIRED", "NOT_APPLICABLE"}
CURRENT_STATUSES = {
    "MISSING",
    "CANDIDATE",
    "PROVISIONAL",
    "EFFECTIVE_PASS",
    "REJECTED",
    "UNKNOWN",
}
MANUAL_ACTIONS = {
    "NONE",
    "SOURCE_RESEARCH",
    "CONTENT_AUTHORING",
    "CREATE",
    "REPAIR",
    "ALPHA_EXTRACT",
    "PLACE_IN_SCENE",
    "BUILD_MENU_STATE",
    "HOTSPOT_XY",
    "REVIEW",
    "REPACK",
    "INTEGRATE",
}
OWNERS = {"CODEX", "HUMAN", "EXTERNAL", "UNKNOWN"}
TASK_STATUSES = {"READY", "BLOCKED", "WAITING_RETURN", "DONE"}
TASK_PHASES = {
    "source_research",
    "content_authoring",
    "image_creation",
    "image_edit",
    "alpha_extraction",
    "scene_placement",
    "menu_state",
    "hotspot_xy",
    "visual_review",
    "technical_review",
    "integration",
}
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _required_role(errors: list[str], item_id: str, role_map: dict[str, dict[str, Any]], role: str) -> None:
    artifact = role_map.get(role)
    if artifact is None:
        errors.append(f"items[{item_id}]: missing artifact role {role}")
    elif artifact.get("requirement") != "REQUIRED":
        errors.append(f"items[{item_id}].artifacts[{role}]: must be REQUIRED for this acquisition route")


def _not_applicable_role(errors: list[str], item_id: str, role_map: dict[str, dict[str, Any]], role: str) -> None:
    artifact = role_map.get(role)
    if artifact is not None and artifact.get("requirement") != "NOT_APPLICABLE":
        errors.append(f"items[{item_id}].artifacts[{role}]: must be NOT_APPLICABLE for this class/route")


def validate_data(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("schema") != SCHEMA:
        errors.append(f"schema: expected {SCHEMA!r}")

    chapter = data.get("chapter")
    if not isinstance(chapter, dict):
        errors.append("chapter: must be an object")
        chapter = {}
    for field in ("id", "title", "revision", "generated_at"):
        if not _nonempty(chapter.get(field)):
            errors.append(f"chapter.{field}: non-empty string required")

    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope: must be an object")
        scope = {}
    if not _nonempty(scope.get("objective")):
        errors.append("scope.objective: non-empty string required")
    scope_hash = scope.get("active_scope_sha256", "")
    if scope_hash and not HASH_RE.fullmatch(str(scope_hash)):
        errors.append("scope.active_scope_sha256: must be empty or a 64-character SHA-256")
    if not scope_hash:
        warnings.append("scope.active_scope_sha256 is empty; document must explain that no active batch scope is available")

    sources = _list(data.get("sources"))
    if not sources:
        errors.append("sources: at least one current source is required")
    source_ids: list[str] = []
    current_source_count = 0
    for index, source in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        source_id = source.get("source_id")
        if not _nonempty(source_id):
            errors.append(f"{prefix}.source_id: non-empty string required")
        else:
            source_ids.append(source_id)
        for field in ("kind", "path", "note"):
            if not _nonempty(source.get(field)):
                errors.append(f"{prefix}.{field}: non-empty string required")
        if not HASH_RE.fullmatch(str(source.get("sha256", ""))):
            errors.append(f"{prefix}.sha256: 64-character SHA-256 required")
        authority = source.get("authority")
        if authority not in {"current", "historical", "supplemental"}:
            errors.append(f"{prefix}.authority: invalid value {authority!r}")
        if authority == "current":
            current_source_count += 1
    duplicate_source_ids = sorted(key for key, count in Counter(source_ids).items() if count > 1)
    if duplicate_source_ids:
        errors.append(f"sources: duplicate source_id values {duplicate_source_ids}")
    if sources and current_source_count == 0:
        errors.append("sources: at least one source must have authority=current")
    source_id_set = set(source_ids)

    items = _list(data.get("items"))
    if not items:
        errors.append("items: at least one item is required")
    item_ids: list[str] = []
    all_task_ids: list[str] = []
    semantic_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    required_status_counts: Counter[str] = Counter()
    manual_task_counts: Counter[str] = Counter()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}]: must be an object")
            continue
        item_id = str(item.get("item_id", "")).strip()
        prefix = f"items[{item_id or index}]"
        if not item_id:
            errors.append(f"items[{index}].item_id: non-empty string required")
        else:
            item_ids.append(item_id)
        if not _nonempty(item.get("name")):
            errors.append(f"{prefix}.name: non-empty string required")

        semantic = item.get("semantic_class")
        route = item.get("acquisition_route")
        if semantic not in SEMANTIC_CLASSES:
            errors.append(f"{prefix}.semantic_class: invalid value {semantic!r}")
        else:
            semantic_counts[semantic] += 1
        if route not in ACQUISITION_ROUTES:
            errors.append(f"{prefix}.acquisition_route: invalid value {route!r}")
        else:
            route_counts[route] += 1
        if not _nonempty(item.get("acquisition_event")):
            errors.append(f"{prefix}.acquisition_event: non-empty string required")

        item_source_refs = _list(item.get("source_refs"))
        if not item_source_refs:
            errors.append(f"{prefix}.source_refs: at least one source_id required")
        invalid_refs = sorted({str(ref) for ref in item_source_refs if ref not in source_id_set})
        if invalid_refs:
            errors.append(f"{prefix}.source_refs: unknown source_id values {invalid_refs}")

        contract = item.get("content_contract")
        if not isinstance(contract, dict):
            errors.append(f"{prefix}.content_contract: object required")
            contract = {}
        for field in ("hard_facts", "allowed_differences", "visual_freedom"):
            if not isinstance(contract.get(field), list):
                errors.append(f"{prefix}.content_contract.{field}: array required")
        if not _list(contract.get("hard_facts")):
            errors.append(f"{prefix}.content_contract.hard_facts: at least one fact required")

        artifacts = _list(item.get("artifacts"))
        if not artifacts:
            errors.append(f"{prefix}.artifacts: at least one role record required")
        role_map: dict[str, dict[str, Any]] = {}
        manual_roles: set[str] = set()
        for artifact_index, artifact in enumerate(artifacts):
            artifact_prefix = f"{prefix}.artifacts[{artifact_index}]"
            if not isinstance(artifact, dict):
                errors.append(f"{artifact_prefix}: must be an object")
                continue
            role = str(artifact.get("role", "")).strip()
            if not role:
                errors.append(f"{artifact_prefix}.role: non-empty string required")
                continue
            if role in role_map:
                errors.append(f"{prefix}.artifacts: duplicate role {role}")
            role_map[role] = artifact
            requirement = artifact.get("requirement")
            status = artifact.get("current_status")
            action = artifact.get("manual_action")
            owner = artifact.get("owner")
            if requirement not in REQUIREMENTS:
                errors.append(f"{artifact_prefix}.requirement: invalid value {requirement!r}")
            if status not in CURRENT_STATUSES:
                errors.append(f"{artifact_prefix}.current_status: invalid value {status!r}")
            elif requirement == "REQUIRED":
                required_status_counts[status] += 1
            if action not in MANUAL_ACTIONS:
                errors.append(f"{artifact_prefix}.manual_action: invalid value {action!r}")
            if owner not in OWNERS:
                errors.append(f"{artifact_prefix}.owner: invalid value {owner!r}")
            if not _nonempty(artifact.get("spec")):
                errors.append(f"{artifact_prefix}.spec: non-empty string required")
            if not _nonempty(artifact.get("reason")):
                errors.append(f"{artifact_prefix}.reason: non-empty string required")
            if requirement == "NOT_APPLICABLE" and action != "NONE":
                errors.append(f"{artifact_prefix}: NOT_APPLICABLE role must use manual_action=NONE")
            if action != "NONE":
                manual_roles.add(role)
                if owner != "HUMAN":
                    errors.append(f"{artifact_prefix}: non-NONE manual_action requires owner=HUMAN")

        tasks = _list(item.get("human_tasks"))
        covered_manual_roles: set[str] = set()
        for task_index, task in enumerate(tasks):
            task_prefix = f"{prefix}.human_tasks[{task_index}]"
            if not isinstance(task, dict):
                errors.append(f"{task_prefix}: must be an object")
                continue
            task_id = str(task.get("task_id", "")).strip()
            if not task_id:
                errors.append(f"{task_prefix}.task_id: non-empty string required")
            else:
                all_task_ids.append(task_id)
            if task.get("phase") not in TASK_PHASES:
                errors.append(f"{task_prefix}.phase: invalid value {task.get('phase')!r}")
            if task.get("status") not in TASK_STATUSES:
                errors.append(f"{task_prefix}.status: invalid value {task.get('status')!r}")
            else:
                manual_task_counts[task.get("status")] += 1
            for field in ("instruction", "return_to"):
                if not _nonempty(task.get(field)):
                    errors.append(f"{task_prefix}.{field}: non-empty string required")
            for field in ("artifact_roles", "inputs", "deliverables", "acceptance", "blocked_by"):
                if not isinstance(task.get(field), list):
                    errors.append(f"{task_prefix}.{field}: array required")
            for field in ("artifact_roles", "inputs", "deliverables", "acceptance"):
                if not _list(task.get(field)):
                    errors.append(f"{task_prefix}.{field}: at least one entry required")
            roles = {str(role) for role in _list(task.get("artifact_roles"))}
            covered_manual_roles.update(roles)
            unknown_roles = sorted(roles - set(role_map))
            if unknown_roles:
                errors.append(f"{task_prefix}.artifact_roles: unknown roles {unknown_roles}")
            if task.get("status") == "BLOCKED" and not _list(task.get("blocked_by")):
                errors.append(f"{task_prefix}.blocked_by: blocked task needs a concrete blocker")

        uncovered = sorted(manual_roles - covered_manual_roles)
        if uncovered:
            errors.append(f"{prefix}: manual-action roles without a human task {uncovered}")

        open_questions = _list(item.get("open_questions"))
        if (semantic == "unresolved" or route == "unresolved") and not open_questions:
            errors.append(f"{prefix}.open_questions: unresolved classification needs a concrete question")

        big = role_map.get("big")
        icon = role_map.get("icon")
        if semantic == "photo_clue":
            _required_role(errors, item_id, role_map, "big")
            if big and big.get("profile") != "clue_big_620x620":
                errors.append(f"{prefix}.artifacts[big].profile: photo clue requires clue_big_620x620")
        elif semantic == "environment_narrative":
            _required_role(errors, item_id, role_map, "big")
            if big and big.get("profile") != "environment_big":
                errors.append(f"{prefix}.artifacts[big].profile: environment narrative requires environment_big")
            _not_applicable_role(errors, item_id, role_map, "icon")
        elif semantic == "ordinary_prop" and big and big.get("requirement") == "REQUIRED":
            if big.get("profile") != "ordinary_big":
                errors.append(f"{prefix}.artifacts[big].profile: ordinary prop requires ordinary_big")

        if route == "scene-pickup":
            for role in ("scene_original", "carrier_without_prop", "pickup_layer", "scene_before_pickup", "map_hotspot", "xy"):
                _required_role(errors, item_id, role_map, role)
        elif route == "container-state":
            for role in ("type6_container", "type7_menu", "menu_preview", "map_hotspot", "xy"):
                _required_role(errors, item_id, role_map, role)
        elif route == "detail-only":
            for role in ("map_hotspot", "xy", "type6_container", "type7_menu"):
                _not_applicable_role(errors, item_id, role_map, role)
        elif route == "environment":
            for role in ("map_hotspot", "xy", "big"):
                _required_role(errors, item_id, role_map, role)
            _not_applicable_role(errors, item_id, role_map, "icon")
        elif route == "minigame-only":
            for role in ("map_hotspot", "xy"):
                artifact = role_map.get(role)
                if artifact and artifact.get("requirement") == "REQUIRED":
                    warnings.append(f"{prefix}.artifacts[{role}] is REQUIRED for minigame-only; document the actual gameplay reason")

    duplicate_item_ids = sorted(key for key, count in Counter(item_ids).items() if count > 1)
    if duplicate_item_ids:
        errors.append(f"items: duplicate item_id values {duplicate_item_ids}")
    duplicate_task_ids = sorted(key for key, count in Counter(all_task_ids).items() if count > 1)
    if duplicate_task_ids:
        errors.append(f"human_tasks: duplicate task_id values {duplicate_task_ids}")

    scope_item_ids = [str(value) for value in _list(scope.get("item_ids"))]
    if set(scope_item_ids) != set(item_ids) or len(scope_item_ids) != len(item_ids):
        errors.append("scope.item_ids must exactly match unique items[].item_id values")
    scope_scene_ids = [str(value) for value in _list(scope.get("scene_ids"))]
    if len(scope_scene_ids) != len(set(scope_scene_ids)):
        errors.append("scope.scene_ids contains duplicates")

    scene_packages = _list(data.get("scene_packages"))
    package_scene_ids: list[str] = []
    all_task_id_set = set(all_task_ids)
    item_id_set = set(item_ids)
    for index, package in enumerate(scene_packages):
        prefix = f"scene_packages[{index}]"
        if not isinstance(package, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        scene_id = str(package.get("scene_id", "")).strip()
        if not scene_id:
            errors.append(f"{prefix}.scene_id: non-empty string required")
        else:
            package_scene_ids.append(scene_id)
        label = package.get("label")
        if not isinstance(label, dict):
            errors.append(f"{prefix}.label: object required")
        else:
            for field in ("location", "time", "state"):
                if not _nonempty(label.get(field)):
                    errors.append(f"{prefix}.label.{field}: non-empty string required")
        invalid_items = sorted({str(value) for value in _list(package.get("item_ids")) if str(value) not in item_id_set})
        if invalid_items:
            errors.append(f"{prefix}.item_ids: unknown item IDs {invalid_items}")
        invalid_tasks = sorted({str(value) for value in _list(package.get("manual_task_ids")) if str(value) not in all_task_id_set})
        if invalid_tasks:
            errors.append(f"{prefix}.manual_task_ids: unknown task IDs {invalid_tasks}")
        if not isinstance(package.get("release_blockers"), list):
            errors.append(f"{prefix}.release_blockers: array required")
    if set(package_scene_ids) != set(scope_scene_ids) or len(package_scene_ids) != len(scope_scene_ids):
        errors.append("scene_packages must exactly cover unique scope.scene_ids")

    calculated_summary = {
        "candidate_count": required_status_counts["CANDIDATE"],
        "provisional_count": required_status_counts["PROVISIONAL"],
        "effective_pass_count": required_status_counts["EFFECTIVE_PASS"],
        "rejected_count": required_status_counts["REJECTED"],
        "unknown_count": required_status_counts["UNKNOWN"],
    }
    status_summary = data.get("status_summary")
    if not isinstance(status_summary, dict):
        errors.append("status_summary: object required")
    else:
        for key, calculated in calculated_summary.items():
            if status_summary.get(key) != calculated:
                errors.append(f"status_summary.{key}: expected {calculated}, got {status_summary.get(key)!r}")

    return {
        "schema": "ndc-prop-manual-requirements-validation/v1",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "items": len(item_ids),
            "scenes": len(scope_scene_ids),
            "sources": len(source_ids),
            "human_tasks": len(all_task_ids),
            "semantic_classes": dict(sorted(semantic_counts.items())),
            "acquisition_routes": dict(sorted(route_counts.items())),
            "required_artifact_statuses": dict(sorted(required_status_counts.items())),
            "human_task_statuses": dict(sorted(manual_task_counts.items())),
        },
    }


def _escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def build_summary(data: dict[str, Any], report: dict[str, Any]) -> str:
    chapter = data["chapter"]
    lines = [
        f"# {chapter['title']} 道具人工处理需求审阅摘要",
        "",
        f"- 章节：{chapter['id']}",
        f"- Revision：{chapter['revision']}",
        f"- Item：{report['counts']['items']}",
        f"- 场景：{report['counts']['scenes']}",
        f"- 人工任务：{report['counts']['human_tasks']}",
        "- 状态：需求清单和人工交接，不等于资产正式 PASS。",
        "",
        "## 资产性质",
        "",
        "| 分类 | 数量 |",
        "| --- | ---: |",
    ]
    for key, count in report["counts"]["semantic_classes"].items():
        lines.append(f"| {_escape_cell(key)} | {count} |")
    lines.extend(["", "## 取得路线", "", "| 路线 | 数量 |", "| --- | ---: |"])
    for key, count in report["counts"]["acquisition_routes"].items():
        lines.append(f"| {_escape_cell(key)} | {count} |")
    lines.extend([
        "",
        "## 人工任务",
        "",
        "| Task ID | Item | 阶段 | 状态 | 操作 | 产物 | 阻塞 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for item in data["items"]:
        for task in item.get("human_tasks", []):
            lines.append(
                "| {task_id} | {item_id} {name} | {phase} | {status} | {instruction} | {deliverables} | {blocked} |".format(
                    task_id=_escape_cell(task["task_id"]),
                    item_id=_escape_cell(item["item_id"]),
                    name=_escape_cell(item["name"]),
                    phase=_escape_cell(task["phase"]),
                    status=_escape_cell(task["status"]),
                    instruction=_escape_cell(task["instruction"]),
                    deliverables=_escape_cell("；".join(map(str, task.get("deliverables", [])))),
                    blocked=_escape_cell("；".join(map(str, task.get("blocked_by", []))) or "无"),
                )
            )
    if report["warnings"]:
        lines.extend(["", "## 校验提醒", ""])
        lines.extend(f"- {_escape_cell(warning)}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def command_init(args: argparse.Namespace) -> int:
    skill_root = Path(__file__).resolve().parent.parent
    template = _load_json(skill_root / "assets" / "manual-requirements.template.json")
    data = copy.deepcopy(template)
    data["chapter"].update(
        {
            "id": args.chapter_id,
            "title": args.title,
            "revision": args.revision,
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )
    _write_json(Path(args.output), data)
    print(json.dumps({"status": "DRAFT_INPUT_REQUIRED", "output": str(Path(args.output).resolve())}, ensure_ascii=False))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    report = validate_data(_load_json(input_path))
    report["input"] = str(input_path.resolve())
    if args.report:
        _write_json(Path(args.report), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


def command_summary(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    data = _load_json(input_path)
    report = validate_data(data)
    if not report["valid"]:
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_summary(data, report), encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output_path.resolve()), "counts": report["counts"]}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare NDC prop manual-requirements document inputs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a chapter-specific draft from the bundled template")
    init_parser.add_argument("--chapter-id", required=True)
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--revision", required=True)
    init_parser.add_argument("--output", required=True)
    init_parser.set_defaults(func=command_init)

    validate_parser = subparsers.add_parser("validate", help="validate structure and cross-field rules")
    validate_parser.add_argument("--input", required=True)
    validate_parser.add_argument("--report")
    validate_parser.set_defaults(func=command_validate)

    summary_parser = subparsers.add_parser("summary", help="write a human-review Markdown summary from valid JSON")
    summary_parser.add_argument("--input", required=True)
    summary_parser.add_argument("--output", required=True)
    summary_parser.set_defaults(func=command_summary)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
