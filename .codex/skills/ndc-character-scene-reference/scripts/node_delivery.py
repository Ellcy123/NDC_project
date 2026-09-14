#!/usr/bin/env python3
"""Build and verify a user-facing NDC character-scene review-node package."""

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

from PIL import Image


PACK_SCHEMA = "ndc-character-node-delivery-pack/v1"
MANIFEST_SCHEMA = "ndc-character-node-delivery/v1"
BATCH_AUDIT_SCHEMA = "ndc-character-node-delivery-batch-audit/v1"
BATCH_REPORT_SCHEMA = "ndc-character-node-delivery-batch-report/v1"
READY_STATUS = "NODE_DELIVERY_READY_PENDING_USER_REVIEW"
METADATA_DIR = "_节点资料"
NODE_METADATA_DIR = "_节点"
MANIFEST_NAME = "节点交付清单.json"
WARNING_NAME = "README_角色白模节点_非正式PASS.txt"
HUMAN_INDEX_NAME = "请先打开_角色白模节点总览.html"
HUMAN_LIST_NAME = "角色白模节点资产清单.md"
HEX = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID = re.compile(r"^[0-9A-Za-z_.-]+$")
UNIT = re.compile(r"^Unit[0-9A-Za-z_-]+$")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
SOURCE_SUFFIXES = {".psd", ".psb"}
XY_SUFFIX = re.compile(r"__XY_x(-?[0-9]+)_y(-?[0-9]+)$", re.IGNORECASE)
ANATOMY_MODES = {"FULL_IN_FRAME", "SCENE_OCCLUDED", "FRAME_CROPPED_FOREGROUND"}
LEGACY_MIGRATION_ROLES = {"legacy_render_candidate", "legacy_scene_ready_rgba"}
PROXY_ABSENCE_KEYS = {
    "stick_or_joint_figure",
    "programmatic_geometry_blocks",
    "flat_color_silhouette",
    "technical_ruler",
    "combined_scene_preview_as_master",
}
ROOT_ROLES = {
    "complete_anatomy_master": "whitebox-master",
    "final_submission_whitebox": "image1-whitebox",
    "joint_whitebox_preview": "joint-whitebox",
    "actual_ui_clearance_preview": "ui-whitebox",
    "editable_source": "source",
    "legacy_render_candidate": "legacy-candidate",
    "legacy_scene_ready_rgba": "legacy-rgba",
}
ROLE_LABELS = {
    "complete_anatomy_master": "逐角色完整 3D 人体白模母层",
    "final_submission_whitebox": "网页 Image 1 最终生产白模",
    "joint_whitebox_preview": "整场联合站位预览（只供关系审核）",
    "actual_ui_clearance_preview": "真实 UI 避让预览",
    "editable_source": "白模可编辑源文件",
    "legacy_render_candidate": "本次明确分拣的历史生成候选（非普通节点固定内容）",
    "legacy_scene_ready_rgba": "本次明确分拣的历史可入景 RGBA（非普通节点固定内容）",
}

WARNING_TEXT = """角色入景白模节点交付包 - 非正式 PASS

场景目录根层只平铺本场可直接打开的真实 3D 白模 PNG/JPG 与 PSD/PSB 源文件；不得按角色、类型或 revision 再拆资产文件夹。
逐 actor/pose 必须同时包含完整人体白模母层和实际作为网页版 ChatGPT Image 1 的最终局部白模。联合站位图与 UI 预览只供整场审核，不能冒充逐角色生产白模。
所有 JSON、提示词、说明、候选状态、审核证据与清单统一放在“_节点资料”中，并按对应交付文件的同名 stem 归组。
只有用户明确要求分拣旧冗余资产并显式开启 legacy_migration_backfill，才可额外附历史候选／已抠图 RGBA；它们只供用户判断可复用性，不是普通节点固定内容，也不替代生产白模。
本包只代表等待用户节点审核，不代表正式资产 PASS、正式角色生产完成或允许工程同步。任何文件变化都必须建立新 revision。
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value.strip()


def safe_id(value: object, label: str) -> str:
    result = text(value, label)
    if SAFE_ID.fullmatch(result) is None or result in {".", ".."}:
        raise ValueError(f"{label} must use letters, digits, dot, underscore, or hyphen")
    return result


def segment(value: object, label: str) -> str:
    result = text(value, label)
    if Path(result).name != result or result in {".", ".."} or any(char in result for char in '<>:"/\\|?*'):
        raise ValueError(f"{label} must be one safe filename")
    return result


def timestamp(value: object, label: str) -> str:
    result = text(value, label)
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


def binding(entry: object, base: Path, label: str, *, verify: bool = True) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(f"{label} must be a file binding")
    raw = text(entry.get("path"), f"{label}.path")
    digest = text(entry.get("sha256"), f"{label}.sha256").lower()
    if HEX.fullmatch(digest) is None:
        raise ValueError(f"{label}.sha256 is invalid")
    path = resolve(base, raw)
    if verify:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"{label} is missing or a symlink: {path}")
        if sha256(path) != digest:
            raise ValueError(f"{label} does not match frozen bytes")
    return {"path": path, "sha256": digest}


def identity(document: dict, label: str) -> dict:
    unit = text(document.get("unit"), f"{label}.unit")
    if UNIT.fullmatch(unit) is None:
        raise ValueError(f"{label}.unit must look like Unit2")
    scene_id = safe_id(document.get("scene_id"), f"{label}.scene_id")
    scene_label = document.get("scene_label")
    if not isinstance(scene_label, dict):
        raise ValueError(f"{label}.scene_label must identify display_name, location, and time")
    display_name = text(scene_label.get("display_name"), f"{label}.scene_label.display_name")
    location = text(scene_label.get("location"), f"{label}.scene_label.location")
    time_label = text(scene_label.get("time"), f"{label}.scene_label.time")
    if display_name.casefold() == scene_id.casefold():
        raise ValueError(f"{label}.scene_label.display_name cannot be only the scene code")
    if location.casefold() not in display_name.casefold() or time_label.casefold() not in display_name.casefold():
        raise ValueError(f"{label}.scene_label.display_name must include both location and time")
    return {
        "unit": unit,
        "scene_id": scene_id,
        "scene_label": {"display_name": display_name, "location": location, "time": time_label},
        "revision": safe_id(str(document.get("revision", "")), f"{label}.revision"),
        "node_id": safe_id(document.get("node_id"), f"{label}.node_id"),
    }


def scope_actor_poses(scope_path: Path) -> set[tuple[str, str]]:
    scope = load(scope_path)
    cases = scope.get("scope", {}).get("cases") if isinstance(scope.get("scope"), dict) else scope.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("character scope must contain cases")
    result: set[tuple[str, str]] = set()
    for case_index, case in enumerate(cases):
        snapshots = case.get("snapshots") if isinstance(case, dict) else None
        if not isinstance(snapshots, list) or not snapshots:
            raise ValueError(f"scope case {case_index} requires snapshots")
        for snapshot_index, snapshot in enumerate(snapshots):
            mapping = snapshot.get("actor_pose_ids") if isinstance(snapshot, dict) else None
            if not isinstance(mapping, dict) or not mapping:
                raise ValueError(f"scope case {case_index} snapshot {snapshot_index} requires actor_pose_ids")
            for actor, pose in mapping.items():
                result.add((safe_id(actor, "actor_id"), safe_id(pose, "pose_id")))
    return result


def validate_image(path: Path, label: str, *, rgba: bool = False, dimensional: bool = False) -> None:
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"{label} must be a directly viewable image")
    try:
        with Image.open(path) as image:
            image.load()
            if image.width < 128 or image.height < 128:
                raise ValueError(f"{label} is too small")
            if rgba:
                if image.mode != "RGBA" or image.getchannel("A").getbbox() is None or image.getchannel("A").getextrema() == (255, 255):
                    raise ValueError(f"{label} must be a real mixed-alpha RGBA image")
            if dimensional:
                colors: set[tuple[int, int, int]] = set()
                luminance: list[int] = []
                pixels = image.convert("RGBA")
                values = pixels.get_flattened_data() if hasattr(pixels, "get_flattened_data") else pixels.getdata()
                for red, green, blue, alpha in values:
                    if alpha >= 192:
                        colors.add((red // 16, green // 16, blue // 16))
                        luminance.append((red * 299 + green * 587 + blue * 114) // 1000)
                        if len(colors) >= 16 and max(luminance) - min(luminance) >= 32:
                            break
                if len(colors) < 16 or not luminance or max(luminance) - min(luminance) < 32:
                    raise ValueError(f"{label} looks like a flat block/stick proxy, not a shaded 3D anatomical mannequin")
    except OSError as exc:
        raise ValueError(f"{label} cannot be opened: {exc}") from exc


def validate_name(name: str, scene_id: str, actor: str, pose: str, role: str, label: str) -> tuple[str, dict | None]:
    filename = segment(name, label)
    suffix = Path(filename).suffix.lower()
    if role == "editable_source":
        if suffix not in SOURCE_SUFFIXES:
            raise ValueError(f"{label} editable_source must be PSD or PSB")
    elif suffix not in IMAGE_SUFFIXES:
        raise ValueError(f"{label} must be a viewable image")
    scene = scene_id if scene_id.upper().startswith("SC") else f"SC{scene_id}"
    stem = Path(filename).stem
    coordinate_match = XY_SUFFIX.search(stem)
    placement = None
    role_stem = stem
    if role == "legacy_scene_ready_rgba":
        if suffix != ".png" or coordinate_match is None:
            raise ValueError(f"{label} scene-ready migration PNG must end with __XY_x<int>_y<int>")
        placement = {"x": int(coordinate_match.group(1)), "y": int(coordinate_match.group(2))}
        role_stem = stem[: coordinate_match.start()]
    elif coordinate_match is not None:
        raise ValueError(f"{label} may use an XY filename suffix only for a scene-ready migration RGBA")
    required_end = f"_{ROOT_ROLES[role]}"
    if role in {"complete_anatomy_master", "final_submission_whitebox", *LEGACY_MIGRATION_ROLES}:
        required_start = f"{scene}_{actor}_{pose}_"
    elif role in {"joint_whitebox_preview", "actual_ui_clearance_preview"}:
        required_start = f"{scene}_scene_"
    else:
        required_start = f"{scene}_"
    if not role_stem.casefold().startswith(required_start.casefold()) or not role_stem.casefold().endswith(required_end.casefold()):
        raise ValueError(f"{label} must use {required_start}[optional-state]{required_end}{suffix}")
    return stem, placement


def normalize_artifact(
    entry: object,
    base: Path,
    scene_id: str,
    actor: str,
    pose: str,
    role: str,
    label: str,
    *,
    checks: list[dict] | None = None,
) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(f"{label} must be an object")
    source = binding(entry.get("source"), base, f"{label}.source")
    name = segment(entry.get("delivery_name"), f"{label}.delivery_name")
    stem, placement = validate_name(name, scene_id, actor, pose, role, f"{label}.delivery_name")
    if role == "complete_anatomy_master":
        validate_image(source["path"], f"{label}.source", rgba=True, dimensional=True)
    elif role != "editable_source":
        validate_image(source["path"], f"{label}.source", rgba=role == "legacy_scene_ready_rgba")
    normalized_checks = checks or []
    return {
        "artifact_id": safe_id(entry.get("artifact_id"), f"{label}.artifact_id"),
        "actor_id": actor,
        "pose_id": pose,
        "role": role,
        "source": source,
        "delivery_name": name,
        "asset_stem": stem,
        "review_status": text(entry.get("review_status"), f"{label}.review_status"),
        "selection_basis": text(entry.get("selection_basis"), f"{label}.selection_basis"),
        "placement_xy": placement,
        "checks": normalized_checks,
    }


def normalize_checks(entry: dict, base: Path, label: str) -> list[dict]:
    result = []
    for kind in ("technical_review", "visual_review", "discovery_receipt"):
        result.append({"kind": kind, "binding": binding(entry.get(kind), base, f"{label}.{kind}")})
    return result


def normalize_legacy_checks(entry: dict, base: Path, label: str) -> list[dict]:
    result = []
    for kind in ("technical_review", "visual_review", "provenance_receipt"):
        result.append({"kind": kind, "binding": binding(entry.get(kind), base, f"{label}.{kind}")})
    return result


def validate_pack(path: Path, *, verify: bool = True, scope_override: Path | None = None) -> tuple[dict, list[dict]]:
    path = path.resolve()
    pack = load(path)
    if pack.get("schema") != PACK_SCHEMA:
        raise ValueError(f"pack schema must be {PACK_SCHEMA}")
    doc_id = identity(pack, "pack")
    timestamp(pack.get("created_at"), "pack.created_at")
    scope = binding(pack.get("scope"), path.parent, "pack.scope", verify=verify)
    source_index = binding(pack.get("source_index"), path.parent, "pack.source_index", verify=verify)
    handoff = binding(pack.get("handoff_document"), path.parent, "pack.handoff_document", verify=verify)
    names = binding(pack.get("naming_table"), path.parent, "pack.naming_table", verify=verify)
    prompt = binding(pack.get("web_prompt"), path.parent, "pack.web_prompt", verify=verify)
    scope_for_coverage = scope["path"]
    if scope_override is not None:
        scope_for_coverage = scope_override.resolve()
        if not scope_for_coverage.is_file() or sha256(scope_for_coverage) != scope["sha256"]:
            raise ValueError("pack.scope does not match the packaged scope snapshot")
    required = scope_actor_poses(scope_for_coverage)
    entries = pack.get("production_whiteboxes")
    if not isinstance(entries, list) or not entries:
        raise ValueError("pack.production_whiteboxes must contain every actor/pose")
    artifacts: list[dict] = []
    actual: set[tuple[str, str]] = set()
    protected_hashes: set[str] = set()
    for role in ("joint_whitebox_preview", "actual_ui_clearance_preview"):
        raw = pack.get(role)
        artifact = normalize_artifact(raw, path.parent, doc_id["scene_id"], "scene", doc_id["revision"], role, f"pack.{role}")
        artifacts.append(artifact)
        protected_hashes.add(artifact["source"]["sha256"])
    if len(protected_hashes) != 2:
        raise ValueError("joint whitebox and actual UI preview must be different files")
    for index, entry in enumerate(entries):
        label = f"pack.production_whiteboxes[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        actor = safe_id(entry.get("actor_id"), f"{label}.actor_id")
        pose = safe_id(entry.get("pose_id"), f"{label}.pose_id")
        key = (actor, pose)
        if key in actual:
            raise ValueError(f"duplicate actor/pose: {key}")
        actual.add(key)
        if entry.get("anatomy_mode") not in ANATOMY_MODES:
            raise ValueError(f"{label}.anatomy_mode is invalid")
        if entry.get("whitebox_kind") != "3d-anatomical-mannequin-exact-pose":
            raise ValueError(f"{label} is not a final 3D anatomical production whitebox")
        absence = entry.get("prohibited_proxy_types_absent")
        if not isinstance(absence, dict) or set(absence) != PROXY_ABSENCE_KEYS or any(value is not True for value in absence.values()):
            raise ValueError(f"{label} must explicitly reject all prohibited proxy types")
        checks = normalize_checks(entry, path.parent, label)
        master = normalize_artifact(entry.get("complete_anatomy_master"), path.parent, doc_id["scene_id"], actor, pose, "complete_anatomy_master", f"{label}.complete_anatomy_master", checks=checks)
        image1 = normalize_artifact(entry.get("final_submission_whitebox"), path.parent, doc_id["scene_id"], actor, pose, "final_submission_whitebox", f"{label}.final_submission_whitebox", checks=checks)
        if master["source"]["sha256"] == image1["source"]["sha256"]:
            raise ValueError(f"{label} must separate complete master from Image 1")
        if master["source"]["sha256"] in protected_hashes or image1["source"]["sha256"] in protected_hashes:
            raise ValueError(f"{label} cannot use a joint/UI preview as a production whitebox")
        artifacts.extend((master, image1))
    if actual != required:
        raise ValueError(f"whitebox coverage differs from frozen scope; missing={sorted(required-actual)}, extra={sorted(actual-required)}")
    editable = pack.get("editable_sources", [])
    if not isinstance(editable, list):
        raise ValueError("pack.editable_sources must be a list")
    for index, entry in enumerate(editable):
        artifacts.append(normalize_artifact(entry, path.parent, doc_id["scene_id"], "scene", doc_id["revision"], "editable_source", f"pack.editable_sources[{index}]"))
    migration = pack.get("legacy_migration_backfill", {"enabled": False})
    if not isinstance(migration, dict) or not isinstance(migration.get("enabled"), bool):
        raise ValueError("pack.legacy_migration_backfill must declare enabled=true or false")
    legacy_entries = pack.get("legacy_review_assets", [])
    if not isinstance(legacy_entries, list):
        raise ValueError("pack.legacy_review_assets must be a list")
    legacy_inventory = None
    if migration["enabled"]:
        reason = text(migration.get("reason"), "pack.legacy_migration_backfill.reason")
        legacy_inventory = binding(migration.get("source_inventory"), path.parent, "pack.legacy_migration_backfill.source_inventory", verify=verify)
        if not legacy_entries:
            raise ValueError("enabled legacy migration backfill requires at least one historical review asset")
        for index, entry in enumerate(legacy_entries):
            label = f"pack.legacy_review_assets[{index}]"
            if not isinstance(entry, dict):
                raise ValueError(f"{label} must be an object")
            role = entry.get("role")
            if role not in LEGACY_MIGRATION_ROLES:
                raise ValueError(f"{label}.role must be a legacy migration review role")
            actor = safe_id(entry.get("actor_id"), f"{label}.actor_id")
            pose = safe_id(entry.get("pose_id"), f"{label}.pose_id")
            artifacts.append(normalize_artifact(
                entry, path.parent, doc_id["scene_id"], actor, pose, role, label,
                checks=normalize_legacy_checks(entry, path.parent, label),
            ))
    elif legacy_entries:
        raise ValueError("legacy review assets are allowed only when legacy_migration_backfill.enabled=true")
    ids = [item["artifact_id"].casefold() for item in artifacts]
    names_seen = [item["delivery_name"].casefold() for item in artifacts]
    stems = [item["asset_stem"].casefold() for item in artifacts]
    if len(ids) != len(set(ids)):
        raise ValueError("artifact_id values must be unique")
    if len(names_seen) != len(set(names_seen)) or len(stems) != len(set(stems)):
        raise ValueError("flat delivery filenames and stems must be unique")
    pack["_normalized"] = {
        "identity": doc_id,
        "scope": scope,
        "source_index": source_index,
        "handoff_document": handoff,
        "naming_table": names,
        "web_prompt": prompt,
        "legacy_migration": {
            "enabled": migration["enabled"],
            "reason": migration.get("reason") if migration["enabled"] else None,
            "source_inventory": legacy_inventory,
            "asset_count": len(legacy_entries),
        },
    }
    return pack, artifacts


def copy_exact(source: Path, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    digest = sha256(destination)
    if digest != sha256(source):
        raise ValueError(f"copy hash mismatch: {destination}")
    return {"relative_path": "", "sha256": digest, "bytes": destination.stat().st_size}


def tree_hash(root: Path, relative_paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(relative_paths):
        path = root / relative
        digest.update(relative.replace("\\", "/").encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def package_target(delivery_root: Path, doc_id: dict) -> Path:
    return delivery_root.resolve() / doc_id["unit"] / "节点交付" / doc_id["scene_id"]


def manifest_relative(doc_id: dict) -> Path:
    return Path(METADATA_DIR) / NODE_METADATA_DIR / doc_id["node_id"] / MANIFEST_NAME


def human_index(doc_id: dict, artifacts: list[dict]) -> str:
    cards = []
    for item in artifacts:
        relative = item["package_file"]["relative_path"].replace("\\", "/")
        href = quote(f"../../../{relative}", safe="/")
        if Path(relative).suffix.lower() in IMAGE_SUFFIXES:
            preview = f'<a href="{href}"><img src="{href}" alt="{html.escape(relative)}"></a>'
        else:
            preview = f'<a class="source" href="{href}">打开 PSD/PSB 源文件</a>'
        cards.append(
            f'<article><h2>{html.escape(ROLE_LABELS[item["role"]])}</h2>{preview}'
            f'<p>{html.escape(item["actor_id"])} / {html.escape(item["pose_id"])}</p>'
            f'<p><a href="{href}">{html.escape(relative)}</a></p></article>'
        )
    scene = doc_id["scene_label"]
    title = html.escape(f'{doc_id["unit"]} {doc_id["scene_id"]} {scene["display_name"]} 角色白模节点')
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>
body{{margin:0;background:#171717;color:#f4f4f4;font-family:"Microsoft YaHei",sans-serif}}header{{padding:20px 28px;background:#242424;border-bottom:3px solid #e34b4b}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;padding:24px}}article{{background:#242424;border:1px solid #444;border-radius:10px;padding:16px}}img{{width:100%;height:280px;object-fit:contain;background:#101010}}a{{color:#8ecbff}}.source{{display:flex;min-height:150px;align-items:center;justify-content:center;border:1px dashed #8ecbff}}</style></head><body><header><h1>{title}</h1><p>地点：{html.escape(scene['location'])}；时段：{html.escape(scene['time'])}。逐角色完整母层和实际 Image 1 均为根层真实文件；联合预览不能代替它们。本包非正式 PASS。</p></header><main>{''.join(cards)}</main></body></html>'''


def human_list(doc_id: dict, artifacts: list[dict]) -> str:
    scene = doc_id["scene_label"]
    lines = [f'# {doc_id["unit"]} / {doc_id["scene_id"]} / {scene["display_name"]} 角色白模节点资产清单', "", f'> 地点：{scene["location"]}；时段：{scene["time"]}。', "", "> 根层是实际图片／源文件；本包待用户节点审核，非正式 PASS。", "", "| 角色/场景 | 姿态 | 类型 | 文件 |", "|---|---|---|---|"]
    for item in artifacts:
        relative = item["package_file"]["relative_path"].replace("\\", "/")
        lines.append(f'| {item["actor_id"]} | {item["pose_id"]} | {ROLE_LABELS[item["role"]]} | [{relative}](<../../../{relative}>) |')
    lines.append("")
    return "\n".join(lines)


def build(pack_path: Path, delivery_root: Path) -> Path:
    pack_path = pack_path.resolve()
    pack, artifacts = validate_pack(pack_path)
    normalized = pack["_normalized"]
    doc_id = normalized["identity"]
    target = package_target(delivery_root, doc_id)
    if target.exists():
        raise ValueError(f"node package already exists; preserve it and create a new revision: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f'.{doc_id["node_id"]}.building-', dir=target.parent))
    try:
        node_meta = Path(METADATA_DIR) / NODE_METADATA_DIR / doc_id["node_id"]
        support = []
        sources = [
            ("pack_snapshot", pack_path, "character_node_delivery_pack.json"),
            ("scope_snapshot", normalized["scope"]["path"], "frozen_scope.json"),
            ("source_index", normalized["source_index"]["path"], "source_index" + normalized["source_index"]["path"].suffix),
            ("handoff_document", normalized["handoff_document"]["path"], "handoff_document" + normalized["handoff_document"]["path"].suffix),
            ("naming_table", normalized["naming_table"]["path"], "naming_table" + normalized["naming_table"]["path"].suffix),
            ("web_prompt", normalized["web_prompt"]["path"], "web_prompt" + normalized["web_prompt"]["path"].suffix),
        ]
        if normalized["legacy_migration"]["enabled"]:
            legacy_source = normalized["legacy_migration"]["source_inventory"]["path"]
            sources.append(("legacy_migration_source_inventory", legacy_source, "legacy_migration_source_inventory" + legacy_source.suffix))
        for kind, source, name in sources:
            relative = node_meta / name
            copied = copy_exact(source, temporary / relative)
            copied["relative_path"] = str(relative)
            support.append({"kind": kind, **copied})
        warning = temporary / node_meta / WARNING_NAME
        warning.write_text(WARNING_TEXT, encoding="utf-8")
        support.append({"kind": "non_formal_warning", "relative_path": str(warning.relative_to(temporary)), "sha256": sha256(warning), "bytes": warning.stat().st_size})
        packaged = []
        for item in artifacts:
            relative = Path(item["delivery_name"])
            copied = copy_exact(item["source"]["path"], temporary / relative)
            copied["relative_path"] = str(relative)
            checks = []
            for index, check in enumerate(item["checks"]):
                source = check["binding"]["path"]
                evidence_relative = Path(METADATA_DIR) / item["asset_stem"] / "审核证据" / f'{index+1:02d}_{check["kind"]}__{source.name}'
                evidence = copy_exact(source, temporary / evidence_relative)
                evidence["relative_path"] = str(evidence_relative)
                checks.append({"kind": check["kind"], **evidence})
            record = {
                "artifact_id": item["artifact_id"], "actor_id": item["actor_id"], "pose_id": item["pose_id"],
                "role": item["role"], "review_status": item["review_status"], "selection_basis": item["selection_basis"],
                "placement_xy": item["placement_xy"],
                "source": {"path": str(item["source"]["path"]), "sha256": item["source"]["sha256"]},
                "package_file": copied, "checks": checks,
            }
            candidate_relative = Path(METADATA_DIR) / item["asset_stem"] / f'{item["asset_stem"]}_节点候选.json'
            candidate = temporary / candidate_relative
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate_data = {
                "schema": "ndc-character-node-delivery-candidate/v1", "status": item["review_status"], "formal_pass": False,
                "artifact_id": item["artifact_id"], "actor_id": item["actor_id"], "pose_id": item["pose_id"], "role": item["role"],
                "delivery_file": copied, "source": record["source"], "selection_basis": item["selection_basis"], "placement_xy": item["placement_xy"], "checks": checks,
            }
            candidate.write_text(json.dumps(candidate_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            record["candidate_record"] = {"relative_path": str(candidate_relative), "sha256": sha256(candidate), "bytes": candidate.stat().st_size}
            packaged.append(record)
        index = temporary / node_meta / HUMAN_INDEX_NAME
        index.write_text(human_index(doc_id, packaged), encoding="utf-8")
        support.append({"kind": "human_preview_index", "relative_path": str(index.relative_to(temporary)), "sha256": sha256(index), "bytes": index.stat().st_size})
        listing = temporary / node_meta / HUMAN_LIST_NAME
        listing.write_text(human_list(doc_id, packaged), encoding="utf-8")
        support.append({"kind": "human_asset_list", "relative_path": str(listing.relative_to(temporary)), "sha256": sha256(listing), "bytes": listing.stat().st_size})
        hashed = [entry["relative_path"] for entry in support]
        for item in packaged:
            hashed.extend([item["package_file"]["relative_path"], item["candidate_record"]["relative_path"]])
            hashed.extend(check["relative_path"] for check in item["checks"])
        manifest = {
            "schema": MANIFEST_SCHEMA, "status": READY_STATUS, **doc_id, "created_at": pack["created_at"],
            "formal_pass": False, "package_root": str(target),
            "scope_source": {"path": str(normalized["scope"]["path"]), "sha256": normalized["scope"]["sha256"]},
            "legacy_migration_backfill": {
                "enabled": normalized["legacy_migration"]["enabled"],
                "reason": normalized["legacy_migration"]["reason"],
                "asset_count": normalized["legacy_migration"]["asset_count"],
            },
            "support_files": support, "artifacts": packaged,
            "coverage": {"actor_poses_required": len(scope_actor_poses(normalized["scope"]["path"])), "actor_poses_packaged": len(scope_actor_poses(normalized["scope"]["path"])), "missing": [], "extra": []},
            "content_tree_sha256": tree_hash(temporary, sorted(set(hashed))),
        }
        manifest_path = temporary / manifest_relative(doc_id)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.rename(target)
        final_manifest = target / manifest_relative(doc_id)
        verify_manifest(final_manifest, delivery_root.resolve())
        return final_manifest
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def verify_binding(root: Path, relative: str, digest: object, label: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} escapes package") from exc
    expected = text(digest, f"{label}.sha256").lower()
    if HEX.fullmatch(expected) is None or not path.is_file() or path.is_symlink() or sha256(path) != expected:
        raise ValueError(f"{label} does not match frozen package bytes")
    return path


def verify_manifest(manifest_path: Path, delivery_root: Path) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = load(manifest_path)
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("status") != READY_STATUS:
        raise ValueError("character node delivery manifest schema or status is invalid")
    doc_id = identity(manifest, "manifest")
    root = package_target(delivery_root, doc_id)
    if manifest_path != root / manifest_relative(doc_id):
        raise ValueError("manifest must be under <角色融入场景>/<Unit>/节点交付/<scene>/_节点资料/_节点/<node-id>")
    if Path(text(manifest.get("package_root"), "manifest.package_root")).resolve() != root or manifest.get("formal_pass") is not False:
        raise ValueError("manifest package root or non-formal status is invalid")
    support = manifest.get("support_files")
    if not isinstance(support, list):
        raise ValueError("manifest.support_files is required")
    support_by_kind: dict[str, Path] = {}
    expected_files = {str(manifest_relative(doc_id))}
    hashed = []
    for index, entry in enumerate(support):
        if not isinstance(entry, dict):
            raise ValueError(f"support_files[{index}] must be an object")
        kind = text(entry.get("kind"), f"support_files[{index}].kind")
        relative = text(entry.get("relative_path"), f"support_files[{index}].relative_path")
        if Path(relative).parts[:1] != (METADATA_DIR,):
            raise ValueError("support files must stay under _节点资料")
        path = verify_binding(root, relative, entry.get("sha256"), f"support_files[{index}]")
        if entry.get("bytes") != path.stat().st_size:
            raise ValueError("support file byte count changed")
        support_by_kind[kind] = path
        expected_files.add(relative); hashed.append(relative)
    for kind in ("pack_snapshot", "scope_snapshot", "source_index", "handoff_document", "naming_table", "web_prompt", "non_formal_warning", "human_preview_index", "human_asset_list"):
        if kind not in support_by_kind:
            raise ValueError(f"manifest lacks {kind}")
    if support_by_kind["non_formal_warning"].read_text(encoding="utf-8-sig") != WARNING_TEXT:
        raise ValueError("warning text changed")
    pack, frozen = validate_pack(
        support_by_kind["pack_snapshot"],
        verify=False,
        scope_override=support_by_kind["scope_snapshot"],
    )
    if identity(pack, "pack") != doc_id:
        raise ValueError("pack identity differs from manifest")
    expected_migration = {
        "enabled": pack["_normalized"]["legacy_migration"]["enabled"],
        "reason": pack["_normalized"]["legacy_migration"]["reason"],
        "asset_count": pack["_normalized"]["legacy_migration"]["asset_count"],
    }
    if manifest.get("legacy_migration_backfill", {"enabled": False, "reason": None, "asset_count": 0}) != expected_migration:
        raise ValueError("manifest legacy migration backfill differs from the frozen pack")
    if expected_migration["enabled"] and "legacy_migration_source_inventory" not in support_by_kind:
        raise ValueError("manifest lacks the legacy migration source inventory")
    if (
        expected_migration["enabled"]
        and sha256(support_by_kind["legacy_migration_source_inventory"])
        != pack["_normalized"]["legacy_migration"]["source_inventory"]["sha256"]
    ):
        raise ValueError("packaged legacy migration source inventory differs from the frozen binding")
    if manifest.get("scope_source", {}).get("sha256") != sha256(support_by_kind["scope_snapshot"]):
        raise ValueError("manifest scope hash differs from packaged scope")
    expected_by_id = {item["artifact_id"]: item for item in frozen}
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_by_id):
        raise ValueError("manifest artifact coverage is incomplete")
    seen = set()
    for index, item in enumerate(artifacts):
        label = f"artifacts[{index}]"
        artifact_id = safe_id(item.get("artifact_id"), f"{label}.artifact_id")
        if artifact_id in seen or artifact_id not in expected_by_id:
            raise ValueError(f"{label} is duplicate or unscoped")
        seen.add(artifact_id)
        frozen_item = expected_by_id[artifact_id]
        for key in ("actor_id", "pose_id", "role", "review_status", "selection_basis", "placement_xy"):
            if item.get(key) != frozen_item[key]:
                raise ValueError(f"{label}.{key} differs from pack")
        package_file = item.get("package_file")
        relative = text(package_file.get("relative_path") if isinstance(package_file, dict) else None, f"{label}.package_file.relative_path")
        if len(Path(relative).parts) != 1 or relative != frozen_item["delivery_name"]:
            raise ValueError(f"{label} is not a flat-root asset")
        checked = verify_binding(root, relative, package_file.get("sha256"), f"{label}.package_file")
        if package_file.get("bytes") != checked.stat().st_size or package_file.get("sha256") != frozen_item["source"]["sha256"]:
            raise ValueError(f"{label}.package_file differs from source")
        expected_files.add(relative); hashed.append(relative)
        candidate = item.get("candidate_record")
        candidate_relative = text(candidate.get("relative_path") if isinstance(candidate, dict) else None, f"{label}.candidate_record.relative_path")
        expected_candidate = str(Path(METADATA_DIR) / frozen_item["asset_stem"] / f'{frozen_item["asset_stem"]}_节点候选.json')
        if candidate_relative != expected_candidate:
            raise ValueError(f"{label}.candidate_record is not grouped by the same asset name")
        candidate_path = verify_binding(root, candidate_relative, candidate.get("sha256"), f"{label}.candidate_record")
        expected_files.add(candidate_relative); hashed.append(candidate_relative)
        candidate_data = load(candidate_path)
        if (
            candidate_data.get("formal_pass") is not False
            or candidate_data.get("delivery_file") != package_file
            or candidate_data.get("role") != frozen_item["role"]
            or candidate_data.get("placement_xy") != frozen_item["placement_xy"]
        ):
            raise ValueError(f"{label}.candidate_record does not bind the exact delivery file")
        checks = item.get("checks")
        if not isinstance(checks, list):
            raise ValueError(f"{label}.checks is required")
        for check_index, check in enumerate(checks):
            check_relative = text(check.get("relative_path"), f"{label}.checks[{check_index}].relative_path")
            try:
                Path(check_relative).relative_to(Path(METADATA_DIR) / frozen_item["asset_stem"] / "审核证据")
            except ValueError as exc:
                raise ValueError(f"{label}.checks are not grouped by the same asset name") from exc
            verify_binding(root, check_relative, check.get("sha256"), f"{label}.checks[{check_index}]")
            expected_files.add(check_relative); hashed.append(check_relative)
    if seen != set(expected_by_id):
        raise ValueError("manifest artifact coverage differs from pack")
    required_pairs = scope_actor_poses(support_by_kind["scope_snapshot"])
    coverage = manifest.get("coverage")
    if coverage != {"actor_poses_required": len(required_pairs), "actor_poses_packaged": len(required_pairs), "missing": [], "extra": []}:
        raise ValueError("manifest actor/pose coverage is incomplete")
    root_files = {path.name for path in root.iterdir() if path.is_file()}
    if root_files != {item["package_file"]["relative_path"] for item in artifacts}:
        raise ValueError("scene root must contain actual whitebox/source assets only")
    root_dirs = {path.name for path in root.iterdir() if path.is_dir()}
    if root_dirs != {METADATA_DIR}:
        raise ValueError("scene root may contain only _节点资料; role/actor/revision asset folders are forbidden")
    actual_files = {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        raise ValueError(f"package has missing or undeclared files; missing={sorted(expected_files-actual_files)}, extra={sorted(actual_files-expected_files)}")
    if tree_hash(root, sorted(set(hashed))) != manifest.get("content_tree_sha256"):
        raise ValueError("package content tree hash changed")
    migration_assets = [
        {
            "actor_id": item["actor_id"], "pose_id": item["pose_id"], "role": item["role"],
            "review_status": item["review_status"], "placement_xy": item["placement_xy"],
            "file": item["package_file"]["relative_path"],
        }
        for item in artifacts if item["role"] in LEGACY_MIGRATION_ROLES
    ]
    return {
        "schema": MANIFEST_SCHEMA, "status": "PASS", **doc_id, "artifacts": len(artifacts),
        "actor_poses": len(required_pairs), "legacy_migration_assets": migration_assets,
        "content_tree_sha256": manifest["content_tree_sha256"],
    }


def audit_batch(spec_path: Path, delivery_root: Path, output_dir: Path) -> dict:
    spec_path = spec_path.resolve()
    delivery_root = delivery_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir == delivery_root or output_dir.is_relative_to(delivery_root):
        raise ValueError("batch audit reports must stay outside the delivery root, normally under {WORK_ROOT}")
    spec = load(spec_path)
    if spec.get("schema") != BATCH_AUDIT_SCHEMA:
        raise ValueError(f"batch audit schema must be {BATCH_AUDIT_SCHEMA}")
    unit = text(spec.get("unit"), "batch.unit")
    if UNIT.fullmatch(unit) is None:
        raise ValueError("batch.unit must look like Unit2")
    timestamp(spec.get("created_at"), "batch.created_at")
    source_batch_scope = binding(spec.get("source_batch_scope"), spec_path.parent, "batch.source_batch_scope")
    expected_scene_ids = spec.get("expected_scene_ids")
    if (
        not isinstance(expected_scene_ids, list)
        or not expected_scene_ids
        or len(expected_scene_ids) != len(set(expected_scene_ids))
    ):
        raise ValueError("batch.expected_scene_ids must be a non-empty distinct list")
    expected_scene_ids = [safe_id(value, "batch.expected_scene_ids[]") for value in expected_scene_ids]
    scenes = spec.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("batch.scenes must describe every expected scene")
    described: dict[str, dict] = {}
    for index, entry in enumerate(scenes):
        label = f"batch.scenes[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        scene_id = safe_id(entry.get("scene_id"), f"{label}.scene_id")
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
        scope_ref = binding(entry.get("scope"), spec_path.parent, f"{label}.scope")
        actor_poses = scope_actor_poses(scope_ref["path"])
        described[scene_id] = {"scene_label": label_value, "scope": scope_ref, "actor_poses": actor_poses}
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
                if verified["actor_poses"] != len(entry["actor_poses"]):
                    raise ValueError("verified actor/pose coverage differs from the batch scene scope")
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                error = str(exc)
        elif len(manifests) == 0:
            error = "node delivery manifest is missing"
        else:
            error = f"multiple node delivery manifests found: {len(manifests)}"
        status = "VERIFIED_COMPLETE" if verified is not None else ("MISSING_NODE_PACKAGE" if not manifests else "INVALID_NODE_PACKAGE")
        required_count = len(entry["actor_poses"]) * 2 + 2
        scene_rows.append({
            "scene_id": scene_id,
            **entry["scene_label"],
            "status": status,
            "required_actor_pose_count": len(entry["actor_poses"]),
            "required_artifact_count": required_count,
            "verified_artifact_count": required_count if verified else 0,
            "packaged_artifact_count_including_optional_sources": verified["artifacts"] if verified else 0,
            "legacy_migration_review_asset_count": len(verified["legacy_migration_assets"]) if verified else 0,
            "manifest": str(manifests[0]) if len(manifests) == 1 else None,
            "error": error,
        })
        requirements = [("scene", "scene", "joint_whitebox_preview"), ("scene", "scene", "actual_ui_clearance_preview")]
        for actor, pose in sorted(entry["actor_poses"]):
            requirements.extend(((actor, pose, "complete_anatomy_master"), (actor, pose, "final_submission_whitebox")))
        for actor, pose, role in requirements:
            artifact_rows.append({
                "scene_id": scene_id,
                "display_name": entry["scene_label"]["display_name"],
                "location": entry["scene_label"]["location"],
                "time": entry["scene_label"]["time"],
                "actor_id": actor,
                "pose_id": pose,
                "role": role,
                "file": "",
                "status": "VERIFIED_PRESENT" if verified else "NEEDS_MANUAL_SUPPLY_OR_REPACKAGING",
            })
        if verified:
            for migration_asset in verified["legacy_migration_assets"]:
                artifact_rows.append({
                    "scene_id": scene_id,
                    "display_name": entry["scene_label"]["display_name"],
                    "location": entry["scene_label"]["location"],
                    "time": entry["scene_label"]["time"],
                    "actor_id": migration_asset["actor_id"],
                    "pose_id": migration_asset["pose_id"],
                    "role": migration_asset["role"],
                    "file": migration_asset["file"],
                    "status": "MIGRATION_REVIEW_COPY_PRESENT",
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
            "required_artifacts": sum(row["status"] != "MIGRATION_REVIEW_COPY_PRESENT" for row in artifact_rows),
            "verified_artifacts": sum(row["status"] == "VERIFIED_PRESENT" for row in artifact_rows),
            "manual_supply_or_repackaging": sum(row["status"] == "NEEDS_MANUAL_SUPPLY_OR_REPACKAGING" for row in artifact_rows),
            "migration_review_assets": sum(row["status"] == "MIGRATION_REVIEW_COPY_PRESENT" for row in artifact_rows),
        },
        "unexpected_scene_directories": unexpected_scene_dirs,
        "scenes": scene_rows,
        "artifacts": artifact_rows,
        "formal_pass": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{unit}_角色白模节点交付统计.json"
    md_path = output_dir / f"{unit}_角色白模节点交付统计.md"
    csv_path = output_dir / f"{unit}_角色白模节点交付资产对照.csv"
    report["outputs"] = {"json": str(json_path), "markdown": str(md_path), "csv": str(csv_path)}
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        f"# {unit} 角色白模节点交付统计",
        "",
        f"> 状态：{report['status']}；这是节点覆盖与人工补缺对照，非正式 PASS。",
        "",
        "| SC 代号 | 地点 | 时段 | 节点状态 | 角色/姿态 | 必需资产 | 已验证 | 问题 |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in scene_rows:
        md_lines.append(
            f"| {row['scene_id']} | {row['location']} | {row['time']} | {row['status']} | "
            f"{row['required_actor_pose_count']} | {row['required_artifact_count']} | {row['verified_artifact_count']} | {row['error'] or '-'} |"
        )
    md_lines.extend(["", "## 需要人工补入或重新打包的资产", "", "| SC 代号 | 场景 | 角色 | 姿态 | 资产角色 |", "|---|---|---|---|---|"])
    missing_rows = [row for row in artifact_rows if row["status"] == "NEEDS_MANUAL_SUPPLY_OR_REPACKAGING"]
    if missing_rows:
        for row in missing_rows:
            md_lines.append(f"| {row['scene_id']} | {row['display_name']} | {row['actor_id']} | {row['pose_id']} | {row['role']} |")
    else:
        md_lines.append("| - | - | - | - | 无 |")
    migration_rows = [row for row in artifact_rows if row["status"] == "MIGRATION_REVIEW_COPY_PRESENT"]
    md_lines.extend(["", "## 本次明确分拣的历史审阅副本", "", "| SC 代号 | 场景 | 角色 | 姿态 | 类型 | 文件 |", "|---|---|---|---|---|---|"])
    if migration_rows:
        for row in migration_rows:
            md_lines.append(
                f"| {row['scene_id']} | {row['display_name']} | {row['actor_id']} | {row['pose_id']} | {row['role']} | {row['file']} |"
            )
    else:
        md_lines.append("| - | - | - | - | 未启用迁移回填 | - |")
    if unexpected_scene_dirs:
        md_lines.extend(["", f">额外场景目录（未在冻结范围）：{', '.join(unexpected_scene_dirs)}"])
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8-sig")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("scene_id", "display_name", "location", "time", "actor_id", "pose_id", "role", "file", "status"))
        writer.writeheader()
        writer.writerows(artifact_rows)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pack = sub.add_parser("pack")
    pack.add_argument("--pack-spec", required=True, type=Path)
    pack.add_argument("--delivery-root", required=True, type=Path, help="Resolved {DELIVERY_ROOT}/角色融入场景")
    verify = sub.add_parser("verify")
    verify.add_argument("--manifest", required=True, type=Path)
    verify.add_argument("--delivery-root", required=True, type=Path, help="Resolved {DELIVERY_ROOT}/角色融入场景")
    audit = sub.add_parser("audit-batch")
    audit.add_argument("--batch-spec", required=True, type=Path)
    audit.add_argument("--delivery-root", required=True, type=Path, help="Resolved {DELIVERY_ROOT}/角色融入场景")
    audit.add_argument("--output-dir", required=True, type=Path, help="Process-report directory outside the delivery root")
    args = parser.parse_args()
    try:
        if args.command == "pack":
            manifest = build(args.pack_spec, args.delivery_root)
            result = verify_manifest(manifest, args.delivery_root.resolve())
            result["manifest"] = str(manifest)
        elif args.command == "verify":
            result = verify_manifest(args.manifest, args.delivery_root.resolve())
        else:
            result = audit_batch(args.batch_spec, args.delivery_root, args.output_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("status") != "INCOMPLETE" else 2
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
