#!/usr/bin/env python3
"""Build and verify a complete, scene-grouped NDC prop node-delivery package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import quote


SCOPE_SCHEMA = "ndc-prop-node-delivery-scope/v1"
PACK_SCHEMA = "ndc-prop-node-delivery-pack/v1"
MANIFEST_SCHEMA = "ndc-prop-node-delivery/v1"
BATCH_AUDIT_SCHEMA = "ndc-prop-node-delivery-batch-audit/v1"
BATCH_REPORT_SCHEMA = "ndc-prop-node-delivery-batch-report/v1"
HOTSPOT_RECONCILIATION_SCHEMA = "ndc-prop-node-hotspot-reconciliation/v1"
READY_STATUS = "NODE_DELIVERY_READY_PENDING_USER_REVIEW"
WARNING_NAME = "README_节点交付_非正式PASS.txt"
HUMAN_INDEX_NAME = "请先打开_节点交付总览.html"
HUMAN_LIST_NAME = "节点交付资产清单.md"
MANIFEST_NAME = "节点交付清单.json"
METADATA_DIR = "_节点资料"
NODE_METADATA_DIR = "_节点"
CANDIDATE_RECORD_SUFFIX = "_交付候选.json"
ROLE_CATALOG = (
    "source_master",
    "state_master",
    "psd_source",
    "big",
    "icon",
    "scene_original",
    "scene_final",
    "scene_preview",
    "carrier_without_prop",
    "pickup_layer",
    "scene_before_pickup",
    "map_hotspot",
    "xy",
    "type6_container",
    "type7_menu",
    "menu_preview",
)
SUBJECT_KINDS = {"item", "scene", "container", "shared"}
SEMANTIC_CLASSES = {"prop", "clue", "environment_narrative", "container", "scene"}
DISPOSITIONS = {"REQUIRED", "MAINLINE_AFTER_NODE", "NOT_APPLICABLE"}
REVIEW_STATUSES = {"PASS", "PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW", "REVIEW_FAILED_VISIBLE_FOR_USER"}
CHECK_KINDS = {"technical_review", "visual_review", "provenance", "relationship_review"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
HEX = re.compile(r"^[0-9a-f]{64}$")
UNIT = re.compile(r"^Unit[0-9A-Za-z_-]+$")
SAFE_ID = re.compile(r"^[0-9A-Za-z_.-]+$")
XY_SUFFIX = re.compile(r"__XY_x(-?[0-9]+)_y(-?[0-9]+)$", re.IGNORECASE)
SCENE_READY_ROLES = {"pickup_layer", "map_hotspot", "type6_container"}
BATCH_HOTSPOT_ROLE_MAP = {
    "scene_pickup_map": "map_hotspot",
    "container_child_map": "map_hotspot",
    "container_type6": "type6_container",
}

ROLE_FILE_TOKENS = {
    "source_master": "master",
    "state_master": "master",
    "psd_source": "psd",
    "big": "big",
    "icon": "icon",
    "scene_original": "original",
    "scene_final": "final",
    "scene_preview": "preview",
    "carrier_without_prop": "carrier",
    "pickup_layer": "pickup",
    "scene_before_pickup": "before_pickup",
    "map_hotspot": "map",
    "xy": "xy",
    "type6_container": "container",
    "type7_menu": "prop",
    "menu_preview": "prop_preview",
}

ROLE_LABELS = {
    "source_master": "源母图",
    "state_master": "状态母图",
    "psd_source": "PSD 源文件",
    "big": "Big",
    "icon": "Icon",
    "scene_original": "原场景",
    "scene_final": "定稿场景",
    "scene_preview": "场景审核预览",
    "carrier_without_prop": "无道具承载物状态",
    "pickup_layer": "道具与归属阴影层",
    "scene_before_pickup": "拾取前场景",
    "map_hotspot": "Map／热区",
    "xy": "XY 坐标",
    "type6_container": "Type 6 容器入口",
    "type7_menu": "Type 7 菜单",
    "menu_preview": "菜单场景预览",
}


WARNING_TEXT = """节点交付审核包 - 非正式 PASS

场景目录根层只平铺可直接打开或使用的交付图片、PSD 源文件与 XY/TXT；不得再按 big/icon/master/map/prop/psd 拆资产文件夹。
所有 JSON 指引、交付候选记录、审核证据和人类总览统一放在“_节点资料”中，并按对应交付资产的同名 stem 归组，不与交付资产混放。
它不是正式资产目录，不代表视觉 PASS、技术 PASS、工程接入或最终发布完成。
本节点只证明当前人工节点明确要求的阶段资产已打包；标为 MAINLINE_AFTER_NODE 的后续资产仍留在冻结生产主线中，不能因节点未携带而取消。
完整性以“_节点资料/_节点/<node-id>/节点交付清单.json”和其中绑定的 scope SHA-256 为准；任何文件变化都必须建立新 revision。
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value.strip()


def require_id(value: object, label: str) -> str:
    result = require_text(value, label)
    if SAFE_ID.fullmatch(result) is None or result in {".", ".."}:
        raise ValueError(f"{label} must use only letters, digits, dot, underscore, or hyphen")
    return result


def require_segment(value: object, label: str) -> str:
    result = require_text(value, label)
    if Path(result).name != result or result in {".", ".."} or any(char in result for char in "<>:\"/\\|?*"):
        raise ValueError(f"{label} must be one safe path segment")
    return result


def require_timestamp(value: object, label: str) -> str:
    result = require_text(value, label)
    try:
        parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return result


def resolve(base: Path, raw: str) -> Path:
    candidate = Path(raw)
    return candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()


def binding(entry: object, base: Path, label: str, *, verify_file: bool) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(f"{label} must be a file binding")
    raw_path = require_text(entry.get("path"), f"{label}.path")
    digest = require_text(entry.get("sha256"), f"{label}.sha256").lower()
    if HEX.fullmatch(digest) is None:
        raise ValueError(f"{label}.sha256 is invalid")
    path = resolve(base, raw_path)
    if verify_file:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"{label} is missing or is a symlink: {path}")
        if sha256(path) != digest:
            raise ValueError(f"{label} does not match frozen bytes")
    return {"path": path, "sha256": digest}


def identity(document: dict, label: str) -> dict:
    unit = require_text(document.get("unit"), f"{label}.unit")
    if UNIT.fullmatch(unit) is None:
        raise ValueError(f"{label}.unit must look like Unit4")
    scene_id = require_id(document.get("scene_id"), f"{label}.scene_id")
    scene_label = document.get("scene_label")
    if not isinstance(scene_label, dict):
        raise ValueError(f"{label}.scene_label must identify display_name, location, and time")
    display_name = require_text(scene_label.get("display_name"), f"{label}.scene_label.display_name")
    location = require_text(scene_label.get("location"), f"{label}.scene_label.location")
    time_label = require_text(scene_label.get("time"), f"{label}.scene_label.time")
    if display_name.casefold() == scene_id.casefold():
        raise ValueError(f"{label}.scene_label.display_name cannot be only the scene code")
    if location.casefold() not in display_name.casefold() or time_label.casefold() not in display_name.casefold():
        raise ValueError(f"{label}.scene_label.display_name must include both location and time")
    return {
        "unit": unit,
        "scene_id": scene_id,
        "scene_label": {"display_name": display_name, "location": location, "time": time_label},
        "revision": require_id(str(document.get("revision", "")), f"{label}.revision"),
        "node_id": require_id(document.get("node_id"), f"{label}.node_id"),
    }


def scene_file_prefix(scene_id: str) -> str:
    return scene_id if scene_id.upper().startswith("SC") else f"SC{scene_id}"


def subject_file_prefix(scene_id: str, subject_id: str) -> str:
    scene = scene_file_prefix(scene_id)
    subject = subject_id.replace(".", "_")
    if subject.casefold() in {scene_id.casefold(), scene.casefold()}:
        return scene
    return f"{scene}_{subject}"


def validate_delivery_name(delivery_name: str, scene_id: str, subject_id: str, role: str, label: str) -> tuple[str, dict | None]:
    suffix = Path(delivery_name).suffix.lower()
    if role == "xy":
        if suffix != ".txt":
            raise ValueError(f"{label} for xy must be a directly usable .txt file")
    elif role == "psd_source":
        if suffix != ".psd":
            raise ValueError(f"{label} for psd_source must be a directly usable .psd source file")
    elif suffix not in IMAGE_SUFFIXES:
        raise ValueError(f"{label} for {role} must be a directly viewable image, not JSON-only metadata")
    stem = Path(delivery_name).stem
    prefix = subject_file_prefix(scene_id, subject_id)
    token = ROLE_FILE_TOKENS[role]
    coordinate_match = XY_SUFFIX.search(stem)
    placement = None
    role_stem = stem
    if role in SCENE_READY_ROLES:
        if suffix != ".png":
            raise ValueError(f"{label} for scene-ready {role} must be a transparent-ready PNG")
        if coordinate_match is None:
            raise ValueError(f"{label} for scene-ready {role} must end with __XY_x<int>_y<int>")
        placement = {"x": int(coordinate_match.group(1)), "y": int(coordinate_match.group(2))}
        role_stem = stem[: coordinate_match.start()]
    elif coordinate_match is not None:
        raise ValueError(f"{label} may use an XY filename suffix only for a scene-ready placement role")
    if not role_stem.casefold().startswith(f"{prefix}_".casefold()) or not role_stem.casefold().endswith(f"_{token}".casefold()):
        raise ValueError(
            f"{label} must identify scene and prop as {prefix}_[optional-state]_{token}"
            f"{'__XY_x<int>_y<int>' if role in SCENE_READY_ROLES else ''}{suffix}; "
            "use map/big/icon/master/prop/psd and the declared extended state tokens"
        )
    middle = role_stem[len(prefix) + 1 : -len(token) - 1]
    if middle and any(char in middle for char in "<>:\"/\\|?*"):
        raise ValueError(f"{label} has an invalid state segment")
    return stem, placement


def validate_scope(path: Path, *, verify_external: bool = True) -> tuple[dict, dict[str, dict]]:
    path = path.resolve()
    scope = load(path)
    if scope.get("schema") != SCOPE_SCHEMA:
        raise ValueError(f"scope schema must be {SCOPE_SCHEMA}")
    identity(scope, "scope")
    binding(scope.get("source_scope"), path.parent, "scope.source_scope", verify_file=verify_external)
    subjects = scope.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        raise ValueError("scope.subjects requires at least one subject")
    expected: dict[str, dict] = {}
    subject_ids: set[str] = set()
    declared_artifact_ids: set[str] = set()
    for subject_index, subject in enumerate(subjects):
        label = f"scope.subjects[{subject_index}]"
        if not isinstance(subject, dict):
            raise ValueError(f"{label} must be an object")
        subject_id = require_id(subject.get("subject_id"), f"{label}.subject_id")
        if subject_id in subject_ids:
            raise ValueError(f"duplicate subject_id: {subject_id}")
        subject_ids.add(subject_id)
        kind = subject.get("subject_kind")
        semantic_class = subject.get("semantic_class")
        if kind not in SUBJECT_KINDS:
            raise ValueError(f"{label}.subject_kind is invalid")
        if semantic_class not in SEMANTIC_CLASSES:
            raise ValueError(f"{label}.semantic_class is invalid")
        dispositions = subject.get("role_dispositions")
        if not isinstance(dispositions, list) or len(dispositions) != len(ROLE_CATALOG):
            raise ValueError(f"{label}.role_dispositions must explicitly cover all {len(ROLE_CATALOG)} roles")
        roles: dict[str, dict] = {}
        for role_index, entry in enumerate(dispositions):
            role_label = f"{label}.role_dispositions[{role_index}]"
            if not isinstance(entry, dict):
                raise ValueError(f"{role_label} must be an object")
            role = entry.get("role")
            if role not in ROLE_CATALOG or role in roles:
                raise ValueError(f"{role_label}.role is invalid or duplicated")
            disposition = entry.get("disposition")
            if disposition not in DISPOSITIONS:
                raise ValueError(
                    f"{role_label}.disposition must be REQUIRED, MAINLINE_AFTER_NODE, or NOT_APPLICABLE"
                )
            if disposition in {"REQUIRED", "MAINLINE_AFTER_NODE"}:
                artifact_ids = entry.get("artifact_ids")
                if not isinstance(artifact_ids, list) or not artifact_ids:
                    raise ValueError(f"{role_label}.artifact_ids is required")
                normalized = []
                for artifact_index, artifact_id_value in enumerate(artifact_ids):
                    artifact_id = require_id(artifact_id_value, f"{role_label}.artifact_ids[{artifact_index}]")
                    if artifact_id in declared_artifact_ids:
                        raise ValueError(f"artifact_id must be unique in the node scope: {artifact_id}")
                    declared_artifact_ids.add(artifact_id)
                    if disposition == "REQUIRED":
                        expected[artifact_id] = {
                            "subject_id": subject_id,
                            "subject_kind": kind,
                            "semantic_class": semantic_class,
                            "role": role,
                        }
                    normalized.append(artifact_id)
                role_data = {"disposition": disposition, "artifact_ids": normalized}
                if disposition == "MAINLINE_AFTER_NODE":
                    role_data["reason"] = require_text(entry.get("reason"), f"{role_label}.reason")
                roles[role] = role_data
            else:
                require_text(entry.get("reason"), f"{role_label}.reason")
                roles[role] = {"disposition": disposition}
        if set(roles) != set(ROLE_CATALOG):
            missing = sorted(set(ROLE_CATALOG) - set(roles))
            extra = sorted(set(roles) - set(ROLE_CATALOG))
            raise ValueError(f"{label} role matrix differs from catalog; missing={missing}, extra={extra}")
        required_roles = {role for role, entry in roles.items() if entry["disposition"] == "REQUIRED"}
        if kind != "scene":
            if not ({"source_master", "state_master"} & required_roles):
                raise ValueError(f"{label} must require source_master or state_master")
        if "pickup_layer" in required_roles:
            if "xy" not in required_roles:
                raise ValueError(f"{label} pickup_layer requires xy in the same node payload")
        if "map_hotspot" in required_roles and "xy" not in required_roles:
            raise ValueError(f"{label} map_hotspot requires xy")
        if "type6_container" in required_roles and "xy" not in required_roles:
            raise ValueError(f"{label} type6_container requires xy")
    if not expected:
        raise ValueError("scope does not require any artifacts")
    return scope, expected


def mainline_after_node(scope: dict) -> list[dict]:
    rows = []
    for subject in scope["subjects"]:
        for entry in subject["role_dispositions"]:
            if entry.get("disposition") == "MAINLINE_AFTER_NODE":
                rows.append({
                    "subject_id": subject["subject_id"],
                    "role": entry["role"],
                    "artifact_ids": list(entry["artifact_ids"]),
                    "reason": entry["reason"],
                })
    return rows


def validate_pack(path: Path, scope_path: Path, expected: dict[str, dict], *, verify_external: bool = True) -> tuple[dict, dict[str, dict]]:
    path = path.resolve()
    pack = load(path)
    if pack.get("schema") != PACK_SCHEMA:
        raise ValueError(f"pack schema must be {PACK_SCHEMA}")
    require_timestamp(pack.get("created_at"), "pack.created_at")
    pack_identity = identity(pack, "pack")
    scope = load(scope_path)
    if pack_identity != identity(scope, "scope"):
        raise ValueError("pack identity differs from its node scope")
    scope_ref = binding(pack.get("scope"), path.parent, "pack.scope", verify_file=verify_external)
    if scope_ref["sha256"] != sha256(scope_path.resolve()):
        raise ValueError("pack.scope must bind the exact supplied node scope bytes")
    if verify_external and scope_ref["path"] != scope_path.resolve():
        raise ValueError("pack.scope path must name the supplied node scope")
    artifacts = pack.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("pack.artifacts requires at least one artifact")
    actual: dict[str, dict] = {}
    delivery_names: set[str] = set()
    metadata_stems: set[str] = set()
    placement_by_subject: dict[str, dict] = {}
    for index, artifact in enumerate(artifacts):
        label = f"pack.artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise ValueError(f"{label} must be an object")
        artifact_id = require_id(artifact.get("artifact_id"), f"{label}.artifact_id")
        if artifact_id in actual:
            raise ValueError(f"duplicate pack artifact_id: {artifact_id}")
        if artifact_id not in expected:
            raise ValueError(f"unscoped artifact in pack: {artifact_id}")
        expected_entry = expected[artifact_id]
        for key in ("subject_id", "role"):
            if artifact.get(key) != expected_entry[key]:
                raise ValueError(f"{label}.{key} differs from scope")
        source = binding(artifact.get("source"), path.parent, f"{label}.source", verify_file=verify_external)
        delivery_name = require_segment(artifact.get("delivery_name"), f"{label}.delivery_name")
        asset_stem, placement = validate_delivery_name(
            delivery_name,
            pack_identity["scene_id"],
            expected_entry["subject_id"],
            expected_entry["role"],
            f"{label}.delivery_name",
        )
        source_suffix = Path(delivery_name).suffix.lower()
        review_status = artifact.get("review_status")
        if review_status not in REVIEW_STATUSES:
            raise ValueError(f"{label}.review_status is invalid")
        require_text(artifact.get("selection_basis"), f"{label}.selection_basis")
        checks = artifact.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"{label}.checks requires bound technical and visual review evidence")
        kinds: set[str] = set()
        normalized_checks = []
        for check_index, check in enumerate(checks):
            check_label = f"{label}.checks[{check_index}]"
            if not isinstance(check, dict) or check.get("kind") not in CHECK_KINDS:
                raise ValueError(f"{check_label}.kind is invalid")
            kind = check["kind"]
            if kind in kinds:
                raise ValueError(f"{label}.checks duplicates {kind}")
            kinds.add(kind)
            normalized_checks.append({"kind": kind, "binding": binding(check.get("file"), path.parent, f"{check_label}.file", verify_file=verify_external)})
        if "technical_review" not in kinds:
            raise ValueError(f"{label} requires technical_review evidence")
        if source["path"].suffix.lower() in IMAGE_SUFFIXES and "visual_review" not in kinds:
            raise ValueError(f"{label} image requires visual_review evidence")
        key = delivery_name.casefold()
        if key in delivery_names:
            raise ValueError(f"duplicate flat-root delivery filename: {delivery_name}")
        delivery_names.add(key)
        metadata_key = asset_stem.casefold()
        if metadata_key in metadata_stems:
            raise ValueError(f"delivery stems must be unique so metadata can use one same-named folder: {asset_stem}")
        metadata_stems.add(metadata_key)
        if placement is not None:
            subject_id = expected_entry["subject_id"]
            prior_placement = placement_by_subject.get(subject_id)
            if prior_placement is not None and prior_placement != placement:
                raise ValueError(
                    f"scene-ready assets for {subject_id} disagree on XY filename coordinates: "
                    f"{prior_placement} versus {placement}"
                )
            placement_by_subject[subject_id] = placement
        actual[artifact_id] = {
            **expected_entry,
            "source": source,
            "delivery_name": delivery_name,
            "review_status": review_status,
            "selection_basis": artifact["selection_basis"].strip(),
            "checks": normalized_checks,
            "asset_stem": asset_stem,
            "placement_xy": placement,
        }
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing or extra:
        raise ValueError(f"pack coverage differs from frozen scope; missing={missing}, extra={extra}")
    return pack, actual


def copy_exact(source: Path, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    digest = sha256(destination)
    if digest != sha256(source):
        raise ValueError(f"copy hash mismatch: {destination}")
    return {"path": destination, "sha256": digest, "bytes": destination.stat().st_size}


def tree_hash(root: Path, relative_paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(relative_paths):
        path = root / relative
        digest.update(relative.replace("\\", "/").encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def render_human_index(doc_identity: dict, artifacts: list[dict]) -> str:
    cards = []
    for artifact in artifacts:
        relative = artifact["package_file"]["relative_path"].replace("\\", "/")
        href = quote(f"../../../{relative}", safe="/")
        label = html.escape(ROLE_LABELS[artifact["role"]])
        title = html.escape(f"{artifact['artifact_id']} · {label}")
        status = html.escape(artifact["review_status"])
        subject = html.escape(artifact["subject_id"])
        basis = html.escape(artifact["selection_basis"])
        if Path(relative).suffix.lower() in IMAGE_SUFFIXES:
            preview = f'<a href="{href}"><img src="{href}" alt="{title}" loading="lazy"></a>'
        else:
            preview = f'<a class="file-link" href="{href}">打开实际文件</a>'
        cards.append(
            "<article class=\"card\">"
            f"<h2>{title}</h2>{preview}"
            f"<p><b>对象：</b>{subject}<br><b>状态：</b>{status}</p>"
            f"<p><b>选用依据：</b>{basis}</p>"
            f"<p><a href=\"{href}\">{html.escape(relative)}</a></p>"
            "</article>"
        )
    scene = doc_identity["scene_label"]
    title = html.escape(f"{doc_identity['unit']} · {doc_identity['scene_id']} · {scene['display_name']} · {doc_identity['node_id']} 节点交付")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{margin:0;background:#171717;color:#f4f4f4;font-family:"Microsoft YaHei",sans-serif}}
header{{position:sticky;top:0;z-index:2;padding:20px 28px;background:#242424;border-bottom:3px solid #e34b4b}}
header h1{{margin:0 0 8px;font-size:24px}} header p{{margin:0;color:#ffc7c7}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;padding:24px}}
.card{{background:#242424;border:1px solid #444;border-radius:10px;padding:16px;overflow:hidden}}
.card h2{{margin:0 0 12px;font-size:17px}} .card p{{font-size:13px;line-height:1.6;word-break:break-all}}
.card img{{display:block;width:100%;height:260px;object-fit:contain;background:#101010;border:1px solid #555}}
a{{color:#8ecbff}} .file-link{{display:flex;min-height:120px;align-items:center;justify-content:center;border:1px dashed #8ecbff;font-size:18px}}
</style>
</head>
<body>
<header><h1>{title}</h1><p>地点：{html.escape(scene['location'])}；时段：{html.escape(scene['time'])}。这是可直接浏览和取用的实际资产总览。JSON 仅作机器校验；本包仍是待用户节点审核，非正式 PASS。</p></header>
<main>{''.join(cards)}</main>
</body>
</html>
"""


def render_human_list(doc_identity: dict, artifacts: list[dict], deferred: list[dict]) -> str:
    scene = doc_identity["scene_label"]
    lines = [
        f"# {doc_identity['unit']} / {doc_identity['scene_id']} / {scene['display_name']} 节点交付资产清单",
        "",
        f"> 地点：{scene['location']}；时段：{scene['time']}。",
        "",
        "> 本清单链接到目录内的实际资产。JSON 仅作机器校验；当前包非正式 PASS。",
        "",
        "| 资产 ID | 对象 | 类型 | XY | 审核状态 | 实际文件 |",
        "|---|---|---|---|---|---|",
    ]
    for artifact in artifacts:
        relative = artifact["package_file"]["relative_path"].replace("\\", "/")
        safe_label = relative.replace("|", "\\|")
        lines.append(
            f"| {artifact['artifact_id']} | {artifact['subject_id']} | {ROLE_LABELS[artifact['role']]} | "
            f"{('__XY_x' + str(artifact['placement_xy']['x']) + '_y' + str(artifact['placement_xy']['y'])) if artifact.get('placement_xy') else '-'} | "
            f"{artifact['review_status']} | [{safe_label}](<../../../{relative}>) |"
        )
    lines.extend([
        "",
        "## 冻结主线中本节点之后继续生产的资产",
        "",
        "> 以下内容没有从冻结范围删除，只是不属于当前节点必须交出的阶段成果。",
        "",
        "| 对象 | 角色 | 资产 ID | 延后依据 |",
        "|---|---|---|---|",
    ])
    if deferred:
        for row in deferred:
            lines.append(
                f"| {row['subject_id']} | {ROLE_LABELS[row['role']]} | {', '.join(row['artifact_ids'])} | "
                f"{row['reason'].replace('|', chr(92) + '|')} |"
            )
    else:
        lines.append("| - | - | 无 | 当前节点未声明延后主线资产 |")
    lines.append("")
    return "\n".join(lines)


def package_target(delivery_root: Path, doc_identity: dict) -> Path:
    return delivery_root.resolve() / doc_identity["unit"] / "节点交付" / doc_identity["scene_id"]


def manifest_relative(doc_identity: dict) -> Path:
    return Path(METADATA_DIR) / NODE_METADATA_DIR / doc_identity["node_id"] / MANIFEST_NAME


def build(scope_path: Path, pack_path: Path, delivery_root: Path) -> Path:
    scope_path = scope_path.resolve()
    pack_path = pack_path.resolve()
    scope, expected = validate_scope(scope_path)
    pack, artifacts = validate_pack(pack_path, scope_path, expected)
    doc_identity = identity(scope, "scope")
    target = package_target(delivery_root, doc_identity)
    if target.exists():
        raise ValueError(f"node package already exists; preserve it and create a new revision: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{doc_identity['node_id']}.building-", dir=target.parent))
    try:
        support_files = []
        deferred_mainline = mainline_after_node(scope)
        node_metadata = Path(METADATA_DIR) / NODE_METADATA_DIR / doc_identity["node_id"]
        scope_copy = copy_exact(scope_path, temporary / node_metadata / "node_delivery_scope.json")
        support_files.append({"kind": "scope_snapshot", "relative_path": str(scope_copy["path"].relative_to(temporary)), "sha256": scope_copy["sha256"], "bytes": scope_copy["bytes"]})
        pack_copy = copy_exact(pack_path, temporary / node_metadata / "node_delivery_pack.json")
        support_files.append({"kind": "pack_snapshot", "relative_path": str(pack_copy["path"].relative_to(temporary)), "sha256": pack_copy["sha256"], "bytes": pack_copy["bytes"]})
        warning_path = temporary / node_metadata / WARNING_NAME
        warning_path.write_text(WARNING_TEXT, encoding="utf-8")
        support_files.append({"kind": "non_formal_warning", "relative_path": str(warning_path.relative_to(temporary)), "sha256": sha256(warning_path), "bytes": warning_path.stat().st_size})
        package_artifacts = []
        for artifact_id in sorted(artifacts):
            artifact = artifacts[artifact_id]
            relative = Path(artifact["delivery_name"])
            copied = copy_exact(artifact["source"]["path"], temporary / relative)
            package_checks = []
            for check_index, check in enumerate(artifact["checks"]):
                source = check["binding"]["path"]
                evidence_name = f"{check_index + 1:02d}_{check['kind']}__{source.name}"
                evidence_relative = Path(METADATA_DIR) / artifact["asset_stem"] / "审核证据" / evidence_name
                evidence_copy = copy_exact(source, temporary / evidence_relative)
                package_checks.append({
                    "kind": check["kind"],
                    "relative_path": str(evidence_relative),
                    "sha256": evidence_copy["sha256"],
                    "bytes": evidence_copy["bytes"],
                })
            packaged = {
                "artifact_id": artifact_id,
                "subject_id": artifact["subject_id"],
                "subject_kind": artifact["subject_kind"],
                "semantic_class": artifact["semantic_class"],
                "role": artifact["role"],
                "review_status": artifact["review_status"],
                "selection_basis": artifact["selection_basis"],
                "placement_xy": artifact["placement_xy"],
                "source": {"path": str(artifact["source"]["path"]), "sha256": artifact["source"]["sha256"]},
                "package_file": {"relative_path": str(relative), "sha256": copied["sha256"], "bytes": copied["bytes"]},
                "checks": package_checks,
            }
            candidate_relative = Path(METADATA_DIR) / artifact["asset_stem"] / f"{artifact['asset_stem']}{CANDIDATE_RECORD_SUFFIX}"
            candidate_path = temporary / candidate_relative
            candidate_path.parent.mkdir(parents=True, exist_ok=True)
            candidate_record = {
                "schema": "ndc-prop-node-delivery-candidate/v1",
                "status": artifact["review_status"],
                "formal_pass": False,
                "artifact_id": artifact_id,
                "subject_id": artifact["subject_id"],
                "role": artifact["role"],
                "delivery_file": packaged["package_file"],
                "source": packaged["source"],
                "selection_basis": artifact["selection_basis"],
                "placement_xy": artifact["placement_xy"],
                "checks": package_checks,
            }
            candidate_path.write_text(json.dumps(candidate_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            packaged["candidate_record"] = {
                "relative_path": str(candidate_relative),
                "sha256": sha256(candidate_path),
                "bytes": candidate_path.stat().st_size,
            }
            package_artifacts.append(packaged)
        human_index = temporary / node_metadata / HUMAN_INDEX_NAME
        human_index.write_text(render_human_index(doc_identity, package_artifacts), encoding="utf-8")
        support_files.append({"kind": "human_preview_index", "relative_path": str(human_index.relative_to(temporary)), "sha256": sha256(human_index), "bytes": human_index.stat().st_size})
        human_list = temporary / node_metadata / HUMAN_LIST_NAME
        human_list.write_text(
            render_human_list(doc_identity, package_artifacts, deferred_mainline),
            encoding="utf-8",
        )
        support_files.append({"kind": "human_asset_list", "relative_path": str(human_list.relative_to(temporary)), "sha256": sha256(human_list), "bytes": human_list.stat().st_size})
        hashed_paths = [entry["relative_path"] for entry in support_files]
        for artifact in package_artifacts:
            hashed_paths.append(artifact["package_file"]["relative_path"])
            hashed_paths.append(artifact["candidate_record"]["relative_path"])
            hashed_paths.extend(check["relative_path"] for check in artifact["checks"])
        hashed_paths = sorted(set(hashed_paths))
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "status": READY_STATUS,
            **doc_identity,
            "created_at": pack["created_at"],
            "formal_pass": False,
            "warning": "交付候选式节点审核包，非正式 PASS，不得用于工程接入或正式发布。",
            "package_root": str(target),
            "scope_source": {"path": str(scope_path), "sha256": sha256(scope_path)},
            "mainline_continuation": {
                "required": True,
                "deferred_artifacts": deferred_mainline,
                "rule": "Node delivery is a stage handoff; frozen-scope production continues independently.",
            },
            "support_files": support_files,
            "artifacts": package_artifacts,
            "coverage": {"required": len(expected), "packaged": len(package_artifacts), "missing": [], "extra": []},
            "content_tree_sha256": tree_hash(temporary, hashed_paths),
        }
        manifest_path = temporary / manifest_relative(doc_identity)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.rename(target)
        final_manifest = target / manifest_relative(doc_identity)
        verify_manifest(final_manifest, delivery_root.resolve())
        return final_manifest
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def verify_manifest(manifest_path: Path, delivery_root: Path) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = load(manifest_path)
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("status") != READY_STATUS:
        raise ValueError("node delivery manifest schema or status is invalid")
    doc_identity = identity(manifest, "manifest")
    expected_root = package_target(delivery_root, doc_identity)
    expected_manifest = expected_root / manifest_relative(doc_identity)
    if manifest_path != expected_manifest:
        raise ValueError("manifest is not in <delivery-root>/<Unit>/节点交付/<scene>/_节点资料/_节点/<node-id>")
    if Path(require_text(manifest.get("package_root"), "manifest.package_root")).resolve() != expected_root:
        raise ValueError("manifest.package_root differs from its actual package")
    if manifest.get("formal_pass") is not False:
        raise ValueError("node delivery package must remain explicitly non-formal")
    support = manifest.get("support_files")
    if not isinstance(support, list):
        raise ValueError("manifest.support_files is required")
    support_by_kind = {}
    expected_files = {str(manifest_relative(doc_identity))}
    hashed_paths = []
    for index, entry in enumerate(support):
        if not isinstance(entry, dict):
            raise ValueError(f"manifest.support_files[{index}] must be an object")
        kind = require_text(entry.get("kind"), f"manifest.support_files[{index}].kind")
        relative = require_text(entry.get("relative_path"), f"manifest.support_files[{index}].relative_path")
        if Path(relative).parts[:1] != (METADATA_DIR,):
            raise ValueError(f"manifest.support_files[{index}] must stay under {METADATA_DIR}")
        checked = verify_package_binding(expected_root, relative, entry.get("sha256"), f"manifest.support_files[{index}]")
        if entry.get("bytes") != checked.stat().st_size:
            raise ValueError(f"manifest.support_files[{index}] byte count changed")
        support_by_kind[kind] = checked
        expected_files.add(relative)
        hashed_paths.append(relative)
    for kind in ("scope_snapshot", "pack_snapshot", "non_formal_warning", "human_preview_index", "human_asset_list"):
        if kind not in support_by_kind:
            raise ValueError(f"manifest lacks {kind}")
    if support_by_kind["non_formal_warning"].read_text(encoding="utf-8-sig") != WARNING_TEXT:
        raise ValueError("node warning text changed")
    scope, expected = validate_scope(support_by_kind["scope_snapshot"], verify_external=False)
    if identity(scope, "scope") != doc_identity:
        raise ValueError("packaged scope identity differs from manifest")
    expected_continuation = {
        "required": True,
        "deferred_artifacts": mainline_after_node(scope),
        "rule": "Node delivery is a stage handoff; frozen-scope production continues independently.",
    }
    if manifest.get("mainline_continuation") != expected_continuation:
        raise ValueError("manifest mainline continuation differs from the frozen node scope")
    if manifest.get("scope_source", {}).get("sha256") != sha256(support_by_kind["scope_snapshot"]):
        raise ValueError("manifest scope hash differs from packaged scope snapshot")
    _, packed = validate_pack(support_by_kind["pack_snapshot"], support_by_kind["scope_snapshot"], expected, verify_external=False)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("manifest.artifacts is required")
    seen: set[str] = set()
    for index, entry in enumerate(artifacts):
        label = f"manifest.artifacts[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        artifact_id = require_id(entry.get("artifact_id"), f"{label}.artifact_id")
        if artifact_id in seen or artifact_id not in packed:
            raise ValueError(f"{label}.artifact_id is duplicated or unscoped")
        seen.add(artifact_id)
        expected_entry = packed[artifact_id]
        for key in ("subject_id", "subject_kind", "semantic_class", "role", "review_status", "placement_xy"):
            if entry.get(key) != expected_entry[key]:
                raise ValueError(f"{label}.{key} differs from frozen pack")
        package_file = entry.get("package_file")
        if not isinstance(package_file, dict):
            raise ValueError(f"{label}.package_file is required")
        relative = require_text(package_file.get("relative_path"), f"{label}.package_file.relative_path")
        expected_relative = expected_entry["delivery_name"]
        if Path(relative) != Path(expected_relative) or len(Path(relative).parts) != 1:
            raise ValueError(f"{label}.package_file must be flat in the scene root")
        checked = verify_package_binding(expected_root, relative, package_file.get("sha256"), f"{label}.package_file")
        if package_file.get("bytes") != checked.stat().st_size:
            raise ValueError(f"{label}.package_file byte count changed")
        expected_files.add(relative)
        hashed_paths.append(relative)
        candidate_record = entry.get("candidate_record")
        if not isinstance(candidate_record, dict):
            raise ValueError(f"{label}.candidate_record is required")
        candidate_relative = require_text(candidate_record.get("relative_path"), f"{label}.candidate_record.relative_path")
        expected_candidate_relative = str(
            Path(METADATA_DIR)
            / expected_entry["asset_stem"]
            / f"{expected_entry['asset_stem']}{CANDIDATE_RECORD_SUFFIX}"
        )
        if Path(candidate_relative) != Path(expected_candidate_relative):
            raise ValueError(f"{label}.candidate_record must be grouped in a same-named metadata folder")
        checked_candidate = verify_package_binding(expected_root, candidate_relative, candidate_record.get("sha256"), f"{label}.candidate_record")
        if candidate_record.get("bytes") != checked_candidate.stat().st_size:
            raise ValueError(f"{label}.candidate_record byte count changed")
        candidate_data = load(checked_candidate)
        if (
            candidate_data.get("schema") != "ndc-prop-node-delivery-candidate/v1"
            or candidate_data.get("formal_pass") is not False
            or candidate_data.get("artifact_id") != artifact_id
            or candidate_data.get("subject_id") != expected_entry["subject_id"]
            or candidate_data.get("role") != expected_entry["role"]
            or candidate_data.get("placement_xy") != expected_entry["placement_xy"]
            or candidate_data.get("delivery_file") != package_file
        ):
            raise ValueError(f"{label}.candidate_record does not describe the exact flat-root delivery asset")
        expected_files.add(candidate_relative)
        hashed_paths.append(candidate_relative)
        checks = entry.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"{label}.checks is required")
        for check_index, check in enumerate(checks):
            check_label = f"{label}.checks[{check_index}]"
            relative = require_text(check.get("relative_path"), f"{check_label}.relative_path")
            expected_check_root = Path(METADATA_DIR) / expected_entry["asset_stem"] / "审核证据"
            try:
                Path(relative).relative_to(expected_check_root)
            except ValueError as exc:
                raise ValueError(f"{check_label} is not grouped with its same-named delivery asset") from exc
            checked = verify_package_binding(expected_root, relative, check.get("sha256"), check_label)
            if check.get("bytes") != checked.stat().st_size:
                raise ValueError(f"{check_label} byte count changed")
            expected_files.add(relative)
            hashed_paths.append(relative)
    if seen != set(expected):
        raise ValueError(f"manifest coverage differs from scope; missing={sorted(set(expected) - seen)}, extra={sorted(seen - set(expected))}")
    coverage = manifest.get("coverage")
    if coverage != {"required": len(expected), "packaged": len(seen), "missing": [], "extra": []}:
        raise ValueError("manifest coverage summary is not exact")
    actual_files = {
        str(path.relative_to(expected_root))
        for path in expected_root.rglob("*")
        if path.is_file()
    }
    root_files = {path.name for path in expected_root.iterdir() if path.is_file()}
    if root_files != {entry["package_file"]["relative_path"] for entry in artifacts}:
        raise ValueError("scene root must contain delivery assets only; JSON, guides, candidate records, and review evidence belong under _节点资料")
    root_dirs = {path.name for path in expected_root.iterdir() if path.is_dir()}
    if root_dirs != {METADATA_DIR}:
        raise ValueError("scene root may contain only the _节点资料 directory; per-type and per-artifact delivery folders are forbidden")
    if actual_files != expected_files:
        raise ValueError(f"package contains missing or undeclared files; missing={sorted(expected_files - actual_files)}, extra={sorted(actual_files - expected_files)}")
    if tree_hash(expected_root, sorted(set(hashed_paths))) != manifest.get("content_tree_sha256"):
        raise ValueError("package content tree hash changed")
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "PASS",
        **doc_identity,
        "required": len(expected),
        "packaged": len(seen),
        "content_tree_sha256": manifest["content_tree_sha256"],
    }


def verify_package_binding(root: Path, relative: str, digest_value: object, label: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} escapes the node package") from exc
    digest = require_text(digest_value, f"{label}.sha256").lower()
    if HEX.fullmatch(digest) is None:
        raise ValueError(f"{label}.sha256 is invalid")
    if not candidate.is_file() or candidate.is_symlink():
        raise ValueError(f"{label} is missing or is a symlink")
    if sha256(candidate) != digest:
        raise ValueError(f"{label} does not match frozen package bytes")
    return candidate


def json_contains_sha256(value: object, digest: str) -> bool:
    """Return whether a review document binds the exact current artifact hash."""
    if isinstance(value, str):
        return value.casefold() == digest.casefold()
    if isinstance(value, list):
        return any(json_contains_sha256(item, digest) for item in value)
    if isinstance(value, dict):
        return any(json_contains_sha256(item, digest) for item in value.values())
    return False


def normalized_xy(value: object) -> dict | None:
    if isinstance(value, list) and len(value) == 2 and all(type(item) is int for item in value):
        return {"x": value[0], "y": value[1]}
    if isinstance(value, dict) and type(value.get("x")) is int and type(value.get("y")) is int:
        return {"x": value["x"], "y": value["y"]}
    return None


def expected_hotspot_xy(artifact: dict, review: dict) -> dict | None:
    direct = normalized_xy(artifact.get("coordinate"))
    if direct is not None:
        return direct
    coordinate = review.get("coordinate")
    direct = normalized_xy(coordinate)
    if direct is not None:
        return direct
    if isinstance(coordinate, dict):
        return normalized_xy(coordinate.get("derived_scene_xy"))
    return None


def batch_stage4_pass_hotspots(batch_path: Path, unit: str) -> tuple[dict, list[dict]]:
    batch_path = batch_path.resolve()
    batch = load(batch_path)
    if batch.get("schema") != "ndc-prop-batch/v1":
        raise ValueError(
            "hotspot reconciliation requires the current frozen ndc-prop-batch/v1, "
            "not a summary or active-scope excerpt"
        )
    batch_id = require_text(batch.get("batch_id"), "batch.batch_id")
    if not batch_id.casefold().startswith(unit.casefold()):
        raise ValueError("batch.batch_id does not match the requested Unit")
    scope = batch.get("scope")
    artifacts = batch.get("artifacts")
    if not isinstance(scope, dict) or not isinstance(scope.get("required_artifacts"), list):
        raise ValueError("batch.scope.required_artifacts is required for hotspot reconciliation")
    if not isinstance(artifacts, dict):
        raise ValueError("batch.artifacts is required for hotspot reconciliation")
    required = scope["required_artifacts"]
    if len(required) != len(set(required)):
        raise ValueError("batch.scope.required_artifacts must not contain duplicates")
    missing = sorted(set(required) - set(artifacts))
    if missing:
        raise ValueError(f"batch required artifacts are missing from inventory: {missing}")
    rows = []
    for artifact_id_value in required:
        artifact_id = require_id(artifact_id_value, "batch.scope.required_artifacts[]")
        artifact = artifacts[artifact_id]
        if not isinstance(artifact, dict):
            raise ValueError(f"batch.artifacts[{artifact_id}] must be an object")
        node_role = BATCH_HOTSPOT_ROLE_MAP.get(artifact.get("role"))
        if (
            artifact.get("stage") != 4
            or artifact.get("status") != "PASS"
            or artifact.get("rejected") is not False
            or node_role is None
        ):
            continue
        scene_id = scene_file_prefix(
            require_id(str(artifact.get("scene_id", "")), f"batch.artifacts[{artifact_id}].scene_id")
        )
        item_ids = artifact.get("item_ids")
        if not isinstance(item_ids, list) or not item_ids:
            raise ValueError(f"batch.artifacts[{artifact_id}].item_ids is required")
        subject_ids = [
            require_id(value, f"batch.artifacts[{artifact_id}].item_ids[]") for value in item_ids
        ]
        source = binding(
            {"path": artifact.get("path"), "sha256": artifact.get("sha256")},
            batch_path.parent,
            f"batch.artifacts[{artifact_id}].source",
            verify_file=True,
        )
        if source["path"].suffix.lower() != ".png":
            raise ValueError(f"batch.artifacts[{artifact_id}] PASS hotspot source must be a PNG")
        review_path = resolve(
            batch_path.parent,
            require_text(artifact.get("review"), f"batch.artifacts[{artifact_id}].review"),
        )
        if not review_path.is_file() or review_path.is_symlink():
            raise ValueError(
                f"batch.artifacts[{artifact_id}].review is missing or is a symlink: {review_path}"
            )
        review = load(review_path)
        if review.get("visual_check_status") != "PASS":
            raise ValueError(f"batch.artifacts[{artifact_id}].review is not a visual PASS")
        if not json_contains_sha256(review, source["sha256"]):
            raise ValueError(
                f"batch.artifacts[{artifact_id}].review does not bind the current PNG hash"
            )
        rows.append({
            "artifact_id": artifact_id,
            "scene_id": scene_id,
            "subject_ids": subject_ids,
            "batch_role": artifact["role"],
            "node_role": node_role,
            "source": {"path": str(source["path"]), "sha256": source["sha256"]},
            "review": {"path": str(review_path), "sha256": sha256(review_path)},
            "expected_xy": expected_hotspot_xy(artifact, review),
        })
    return batch, rows


def reconcile_hotspots(
    batch_path: Path,
    delivery_root: Path,
    output_dir: Path,
    unit: str,
    *,
    expected_scene_ids: list[str] | None = None,
) -> dict:
    delivery_root = delivery_root.resolve()
    output_dir = output_dir.resolve()
    if UNIT.fullmatch(unit) is None:
        raise ValueError("unit must look like Unit4")
    if output_dir == delivery_root or output_dir.is_relative_to(delivery_root):
        raise ValueError(
            "hotspot reconciliation reports must stay outside the delivery root, normally under {WORK_ROOT}"
        )
    _, hotspots = batch_stage4_pass_hotspots(batch_path, unit)
    if expected_scene_ids is not None:
        normalized_scene_ids = {
            scene_file_prefix(require_id(value, "expected_scene_ids[]")) for value in expected_scene_ids
        }
        omitted_scenes = sorted({row["scene_id"] for row in hotspots} - normalized_scene_ids)
        if omitted_scenes:
            raise ValueError(
                f"batch Stage4 PASS hotspot scenes are omitted from expected_scene_ids: {omitted_scenes}"
            )
    rows = []
    for hotspot in hotspots:
        scene_root = package_target(
            delivery_root,
            {"unit": unit, "scene_id": hotspot["scene_id"]},
        )
        exact_matches = []
        if scene_root.is_dir():
            for candidate in scene_root.iterdir():
                if (
                    candidate.is_file()
                    and not candidate.is_symlink()
                    and candidate.suffix.lower() == ".png"
                    and sha256(candidate) == hotspot["source"]["sha256"]
                ):
                    exact_matches.append(candidate)
        status = "PACKAGED_EXACT_WITH_XY"
        error = None
        node_file = None
        filename_xy = None
        if not exact_matches:
            status = "MISSING_FROM_NODE"
            error = "current batch PASS hotspot PNG bytes were not found in the correct flat scene root"
        elif len(exact_matches) > 1:
            status = "AMBIGUOUS_DUPLICATE_NODE_COPY"
            error = f"the exact PASS hotspot bytes appear {len(exact_matches)} times in the scene root"
        else:
            match = exact_matches[0]
            node_file = str(match)
            coordinate_match = XY_SUFFIX.search(match.stem)
            if coordinate_match is None:
                status = "PACKAGED_WITHOUT_XY_SUFFIX"
                error = "scene-ready hotspot filename lacks __XY_x<int>_y<int>"
            else:
                filename_xy = {
                    "x": int(coordinate_match.group(1)),
                    "y": int(coordinate_match.group(2)),
                }
                if hotspot["expected_xy"] is not None and filename_xy != hotspot["expected_xy"]:
                    status = "XY_MISMATCH"
                    error = "filename XY differs from the current batch or PASS review coordinate"
        rows.append({
            **hotspot,
            "status": status,
            "node_file": node_file,
            "filename_xy": filename_xy,
            "error": error,
        })
    complete = all(row["status"] == "PACKAGED_EXACT_WITH_XY" for row in rows)
    report = {
        "schema": HOTSPOT_RECONCILIATION_SCHEMA,
        "status": "PASS" if complete else "INCOMPLETE",
        "unit": unit,
        "source_batch": {
            "path": str(batch_path.resolve()),
            "sha256": sha256(batch_path.resolve()),
        },
        "counts": {
            "batch_stage4_pass_hotspots": len(rows),
            "packaged_exact_with_xy": sum(
                row["status"] == "PACKAGED_EXACT_WITH_XY" for row in rows
            ),
            "missing_or_invalid": sum(
                row["status"] != "PACKAGED_EXACT_WITH_XY" for row in rows
            ),
        },
        "hotspots": rows,
        "formal_pass": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{unit}_Stage4_PASS热区反查.json"
    md_path = output_dir / f"{unit}_Stage4_PASS热区反查.md"
    csv_path = output_dir / f"{unit}_Stage4_PASS热区反查.csv"
    report["outputs"] = {
        "json": str(json_path),
        "markdown": str(md_path),
        "csv": str(csv_path),
    }
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md_lines = [
        f"# {unit} Stage4 PASS 热区反查",
        "",
        f"> 状态：{report['status']}；逐项从当前冻结批次反查实际 PNG、审核哈希、节点副本和 XY 文件名。非正式 PASS。",
        "",
        "| 场景 | 道具 | 批次资产 | 角色 | 节点状态 | 节点文件 | 问题 |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row['scene_id']} | {', '.join(row['subject_ids'])} | {row['artifact_id']} | "
            f"{row['batch_role']} | {row['status']} | {row['node_file'] or '-'} | "
            f"{row['error'] or '-'} |"
        )
    if not rows:
        md_lines.append("| - | - | - | - | PASS | 当前冻结批次无 Stage4 PASS 热区 | - |")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8-sig")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "scene_id",
                "subject_ids",
                "artifact_id",
                "batch_role",
                "node_role",
                "status",
                "node_file",
                "error",
            ),
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "scene_id": row["scene_id"],
                "subject_ids": ",".join(row["subject_ids"]),
                "artifact_id": row["artifact_id"],
                "batch_role": row["batch_role"],
                "node_role": row["node_role"],
                "status": row["status"],
                "node_file": row["node_file"],
                "error": row["error"],
            })
    return report


def audit_batch(spec_path: Path, delivery_root: Path, output_dir: Path) -> dict:
    spec_path = spec_path.resolve()
    delivery_root = delivery_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir == delivery_root or output_dir.is_relative_to(delivery_root):
        raise ValueError("batch audit reports must stay outside the delivery root, normally under {WORK_ROOT}")
    spec = load(spec_path)
    if spec.get("schema") != BATCH_AUDIT_SCHEMA:
        raise ValueError(f"batch audit schema must be {BATCH_AUDIT_SCHEMA}")
    unit = require_text(spec.get("unit"), "batch.unit")
    if UNIT.fullmatch(unit) is None:
        raise ValueError("batch.unit must look like Unit4")
    require_timestamp(spec.get("created_at"), "batch.created_at")
    source_batch_scope = binding(spec.get("source_batch_scope"), spec_path.parent, "batch.source_batch_scope", verify_file=True)
    expected_scene_ids = spec.get("expected_scene_ids")
    if (
        not isinstance(expected_scene_ids, list)
        or not expected_scene_ids
        or len(expected_scene_ids) != len(set(expected_scene_ids))
    ):
        raise ValueError("batch.expected_scene_ids must be a non-empty distinct list")
    expected_scene_ids = [require_id(value, "batch.expected_scene_ids[]") for value in expected_scene_ids]
    scenes = spec.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("batch.scenes must describe every expected scene")
    described: dict[str, dict] = {}
    for index, entry in enumerate(scenes):
        label = f"batch.scenes[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        scene_id = require_id(entry.get("scene_id"), f"{label}.scene_id")
        if scene_id in described:
            raise ValueError(f"duplicate batch scene: {scene_id}")
        fake_identity = {
            "unit": unit,
            "scene_id": scene_id,
            "scene_label": entry.get("scene_label"),
            "revision": "batch-audit",
            "node_id": "batch-audit",
        }
        label_value = identity(fake_identity, label)["scene_label"]
        scope_ref = binding(entry.get("scope"), spec_path.parent, f"{label}.scope", verify_file=True)
        scope, expected = validate_scope(scope_ref["path"])
        scope_identity = identity(scope, f"{label}.scope")
        if scope_identity["unit"] != unit or scope_identity["scene_id"] != scene_id or scope_identity["scene_label"] != label_value:
            raise ValueError(f"{label} identity differs from its bound scene scope")
        described[scene_id] = {"scene_label": label_value, "scope": scope_ref, "expected": expected}
    if set(described) != set(expected_scene_ids):
        raise ValueError(
            f"batch.scenes differs from expected_scene_ids; missing={sorted(set(expected_scene_ids)-set(described))}, "
            f"extra={sorted(set(described)-set(expected_scene_ids))}"
        )

    unit_root = delivery_root / unit / "节点交付"
    actual_scene_dirs = {path.name for path in unit_root.iterdir() if path.is_dir()} if unit_root.is_dir() else set()
    unexpected_scene_dirs = sorted(actual_scene_dirs - set(expected_scene_ids))
    scene_rows = []
    artifact_rows = []
    for scene_id in expected_scene_ids:
        entry = described[scene_id]
        scene_root = package_target(delivery_root, {"unit": unit, "scene_id": scene_id})
        manifests = sorted((scene_root / METADATA_DIR / NODE_METADATA_DIR).glob(f"*/{MANIFEST_NAME}")) if scene_root.is_dir() else []
        error = None
        verified = None
        if len(manifests) == 1:
            try:
                verified = verify_manifest(manifests[0], delivery_root)
                if verified["scene_label"] != entry["scene_label"]:
                    raise ValueError("verified manifest scene label differs from the batch label")
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                error = str(exc)
        elif len(manifests) == 0:
            error = "node delivery manifest is missing"
        else:
            error = f"multiple node delivery manifests found: {len(manifests)}"
        status = "VERIFIED_COMPLETE" if verified is not None else ("MISSING_NODE_PACKAGE" if not manifests else "INVALID_NODE_PACKAGE")
        scene_rows.append({
            "scene_id": scene_id,
            **entry["scene_label"],
            "status": status,
            "required_artifact_count": len(entry["expected"]),
            "verified_artifact_count": verified["packaged"] if verified else 0,
            "manifest": str(manifests[0]) if len(manifests) == 1 else None,
            "error": error,
        })
        for artifact_id, expected in sorted(entry["expected"].items()):
            artifact_rows.append({
                "scene_id": scene_id,
                "display_name": entry["scene_label"]["display_name"],
                "location": entry["scene_label"]["location"],
                "time": entry["scene_label"]["time"],
                "artifact_id": artifact_id,
                "subject_id": expected["subject_id"],
                "role": expected["role"],
                "status": "VERIFIED_PRESENT" if verified else "NEEDS_MANUAL_SUPPLY_OR_REPACKAGING",
            })
    complete = all(row["status"] == "VERIFIED_COMPLETE" for row in scene_rows) and not unexpected_scene_dirs
    report = {
        "schema": BATCH_REPORT_SCHEMA,
        "status": "PASS" if complete else "INCOMPLETE",
        "unit": unit,
        "source_batch_scope": {"path": str(source_batch_scope["path"]), "sha256": source_batch_scope["sha256"]},
        "counts": {
            "expected_scenes": len(expected_scene_ids),
            "verified_scenes": sum(row["status"] == "VERIFIED_COMPLETE" for row in scene_rows),
            "missing_or_invalid_scenes": sum(row["status"] != "VERIFIED_COMPLETE" for row in scene_rows),
            "required_artifacts": len(artifact_rows),
            "verified_artifacts": sum(row["status"] == "VERIFIED_PRESENT" for row in artifact_rows),
            "manual_supply_or_repackaging": sum(row["status"] != "VERIFIED_PRESENT" for row in artifact_rows),
        },
        "unexpected_scene_directories": unexpected_scene_dirs,
        "scenes": scene_rows,
        "artifacts": artifact_rows,
        "formal_pass": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{unit}_道具节点交付统计.json"
    md_path = output_dir / f"{unit}_道具节点交付统计.md"
    csv_path = output_dir / f"{unit}_道具节点交付资产对照.csv"
    report["outputs"] = {"json": str(json_path), "markdown": str(md_path), "csv": str(csv_path)}
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        f"# {unit} 道具节点交付统计",
        "",
        f"> 状态：{report['status']}；这是节点覆盖与人工补缺对照，非正式 PASS。",
        "",
        "| SC 代号 | 地点 | 时段 | 节点状态 | 必需资产 | 已验证 | 问题 |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in scene_rows:
        md_lines.append(
            f"| {row['scene_id']} | {row['location']} | {row['time']} | {row['status']} | "
            f"{row['required_artifact_count']} | {row['verified_artifact_count']} | {row['error'] or '-'} |"
        )
    md_lines.extend(["", "## 需要人工补入或重新打包的资产", "", "| SC 代号 | 场景 | 对象 | 资产角色 | 资产 ID |", "|---|---|---|---|---|"])
    missing_rows = [row for row in artifact_rows if row["status"] != "VERIFIED_PRESENT"]
    if missing_rows:
        for row in missing_rows:
            md_lines.append(f"| {row['scene_id']} | {row['display_name']} | {row['subject_id']} | {row['role']} | {row['artifact_id']} |")
    else:
        md_lines.append("| - | - | - | - | 无 |")
    if unexpected_scene_dirs:
        md_lines.extend(["", f">额外场景目录（未在冻结范围）：{', '.join(unexpected_scene_dirs)}"])
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8-sig")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("scene_id", "display_name", "location", "time", "artifact_id", "subject_id", "role", "status"))
        writer.writeheader()
        writer.writerows(artifact_rows)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pack = sub.add_parser("pack")
    pack.add_argument("--scope", required=True, type=Path)
    pack.add_argument("--pack-spec", required=True, type=Path)
    pack.add_argument("--delivery-root", required=True, type=Path, help="Category root, for example {DELIVERY_ROOT}/道具")
    verify = sub.add_parser("verify")
    verify.add_argument("--manifest", required=True, type=Path)
    verify.add_argument("--delivery-root", required=True, type=Path, help="Category root, for example {DELIVERY_ROOT}/道具")
    audit = sub.add_parser("audit-batch")
    audit.add_argument("--batch-spec", required=True, type=Path)
    audit.add_argument("--delivery-root", required=True, type=Path, help="Category root, for example {DELIVERY_ROOT}/道具")
    audit.add_argument("--output-dir", required=True, type=Path, help="Process-report directory outside the delivery root")
    reconcile = sub.add_parser("reconcile-hotspots")
    reconcile.add_argument("--batch", required=True, type=Path)
    reconcile.add_argument("--unit", required=True)
    reconcile.add_argument("--delivery-root", required=True, type=Path, help="Category root, for example {DELIVERY_ROOT}/道具")
    reconcile.add_argument("--output-dir", required=True, type=Path, help="Process-report directory outside the delivery root")
    args = parser.parse_args()
    try:
        if args.command == "pack":
            manifest = build(args.scope, args.pack_spec, args.delivery_root)
            result = verify_manifest(manifest, args.delivery_root.resolve())
            result["manifest"] = str(manifest)
        elif args.command == "verify":
            result = verify_manifest(args.manifest, args.delivery_root.resolve())
        elif args.command == "audit-batch":
            result = audit_batch(args.batch_spec, args.delivery_root, args.output_dir)
        else:
            result = reconcile_hotspots(args.batch, args.delivery_root, args.output_dir, args.unit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("status") != "INCOMPLETE" else 2
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
