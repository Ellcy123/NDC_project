#!/usr/bin/env python3
"""Validate an NDC formal image package from a semantic release contract.

Unlike the legacy caller-supplied file-list validator, this gate derives the
formal PNG and XY requirements from classified acquisition records, binds every
coordinate to the current Map hash, and scans non-history replicas for drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image


FORBIDDEN_FORMAL_TOKENS = (
    "candidate", "checker", "debug", "history", "manifest", "mask", "old",
    "overlay", "rejected", "report", "superseded", "verification", "候选",
    "历史", "旧版", "拒绝", "验证", "报告", "叠图",
)
HISTORY_PATH_TOKENS = (
    "history", "legacy", "old", "rejected", "superseded", "历史", "旧版",
    "拒绝", "废弃",
)
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
PARENT_PIXEL_ROLES = {"map", "type6"}
VALID_CLASSES = {
    "scene-pickup", "container-state", "detail-only", "environment",
    "minigame-only",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_xy(path: Path) -> tuple[dict[str, tuple[int, int]], list[str]]:
    entries: dict[str, tuple[int, int]] = {}
    errors: list[str] = []
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2 or parts[1].count(",") != 1:
            errors.append(f"XY line {line_number} is not '<stem> x,y'")
            continue
        stem = parts[0]
        pair = parts[1].split(",")
        try:
            coordinate = (int(pair[0]), int(pair[1]))
        except ValueError:
            errors.append(f"XY line {line_number} has non-integer coordinates")
            continue
        if stem in entries:
            errors.append(f"XY stem is duplicated: {stem}")
        entries[stem] = coordinate
    return entries, errors


def role_contract(delivery_class: str, icon_policy: str) -> tuple[set[str], set[str], set[str], bool]:
    valid_icon_policy = True
    if delivery_class == "scene-pickup":
        required, allowed, positioned = {"map", "big"}, {"map", "big", "icon"}, {"map"}
        if icon_policy == "required":
            required.add("icon")
        elif icon_policy != "omit":
            valid_icon_policy = False
    elif delivery_class == "environment":
        required, allowed, positioned = {"map", "big"}, {"map", "big"}, {"map"}
        valid_icon_policy = icon_policy == "omit"
    elif delivery_class == "detail-only":
        required, allowed, positioned = {"big"}, {"big", "icon"}, set()
        if icon_policy == "required":
            required.add("icon")
        elif icon_policy != "omit":
            valid_icon_policy = False
    elif delivery_class == "container-state":
        required = allowed = {"type6", "type7"}
        positioned = {"type6", "type7"}
        valid_icon_policy = icon_policy == "omit"
    else:
        required = allowed = positioned = set()
        valid_icon_policy = icon_policy == "omit"
    return required, allowed, positioned, valid_icon_policy


def nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(entry, str) and entry.strip() for entry in value
    )


def validate_contract(contract_path: Path) -> dict[str, Any]:
    failures: list[str] = []
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"failures": [f"cannot load release contract: {exc}"]}
    if not isinstance(contract, dict):
        return {"failures": ["release contract root must be an object"]}
    if contract.get("version") != 1:
        failures.append("release contract version must be 1")
    if contract.get("kind") != "ndc-formal-release-contract":
        failures.append("release contract kind must be ndc-formal-release-contract")

    required_png: set[str] = set()
    scene_preview = contract.get("scenePreview")
    if not isinstance(scene_preview, str) or not scene_preview.endswith(".png"):
        failures.append("scenePreview must name one formal PNG")
    else:
        required_png.add(scene_preview)
    additional = contract.get("additionalStateImages", [])
    if not isinstance(additional, list) or not all(
        isinstance(name, str) and name.endswith(".png") for name in additional
    ):
        failures.append("additionalStateImages must be a list of PNG names")
    else:
        required_png.update(additional)

    expected_xy: dict[str, tuple[int, int]] = {}
    position_assets: dict[str, str] = {}
    position_hashes: dict[str, str] = {}
    parent_bindings: dict[str, dict[str, Any]] = {}
    semantic_records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def visit(record: Any, location: str) -> None:
        if not isinstance(record, dict):
            failures.append(f"{location} must be an object")
            return
        record_id = record.get("recordId")
        if not isinstance(record_id, str) or not record_id.strip():
            failures.append(f"{location}.recordId must be a non-empty string")
            record_id = location
        elif record_id in seen_ids:
            failures.append(f"duplicate recordId: {record_id}")
        else:
            seen_ids.add(record_id)

        delivery_class = record.get("deliveryClass")
        if delivery_class not in VALID_CLASSES:
            failures.append(f"{location}.deliveryClass is invalid: {delivery_class}")
            return
        if not isinstance(record.get("classificationReason"), str) or not record["classificationReason"].strip():
            failures.append(f"{location}.classificationReason is required")
        if not nonempty_string_list(record.get("sourceReferences")):
            failures.append(f"{location}.sourceReferences must cite authoritative sources")

        icon_policy = record.get("iconPolicy")
        required_roles, allowed_roles, positioned_roles, icon_policy_valid = role_contract(
            delivery_class, icon_policy
        )
        if not icon_policy_valid:
            failures.append(f"{location}.iconPolicy conflicts with {delivery_class}")
        assets = record.get("assets", {})
        if not isinstance(assets, dict):
            failures.append(f"{location}.assets must be an object")
            assets = {}
        roles = set(assets)
        missing_roles = sorted(required_roles - roles)
        forbidden_roles = sorted(roles - allowed_roles)
        if missing_roles:
            failures.append(f"{location} missing asset roles: {missing_roles}")
        if forbidden_roles:
            failures.append(f"{location} has forbidden asset roles: {forbidden_roles}")
        for role, filename in assets.items():
            if not isinstance(filename, str) or not filename.endswith(".png"):
                failures.append(f"{location}.assets.{role} must name a PNG")
            else:
                required_png.add(filename)

        positions = record.get("positions", [])
        if not isinstance(positions, list):
            failures.append(f"{location}.positions must be a list")
            positions = []
        found_position_roles: set[str] = set()
        for index, position in enumerate(positions):
            label = f"{location}.positions[{index}]"
            if not isinstance(position, dict):
                failures.append(f"{label} must be an object")
                continue
            role = position.get("role")
            if role not in positioned_roles or role in found_position_roles:
                failures.append(f"{label}.role is forbidden or duplicated")
                continue
            found_position_roles.add(role)
            filename = assets.get(role)
            stem = position.get("stem")
            x, y = position.get("x"), position.get("y")
            asset_hash = position.get("assetSha256")
            if not isinstance(filename, str) or not isinstance(stem, str) or Path(filename).stem != stem:
                failures.append(f"{label}.stem must equal its asset stem")
                continue
            if not isinstance(x, int) or isinstance(x, bool) or not isinstance(y, int) or isinstance(y, bool):
                failures.append(f"{label}.x/y must be integers")
                continue
            if not isinstance(asset_hash, str) or not HASH_RE.fullmatch(asset_hash):
                failures.append(f"{label}.assetSha256 must be SHA-256")
                continue
            if stem in expected_xy:
                failures.append(f"duplicate coordinate stem across contract: {stem}")
                continue
            expected_xy[stem] = (x, y)
            position_assets[stem] = filename
            position_hashes[stem] = asset_hash.lower()
            if role in PARENT_PIXEL_ROLES:
                parent_image = position.get("acceptedParentImage")
                parent_hash = position.get("acceptedParentSha256")
                if not isinstance(parent_image, str) or not parent_image.strip():
                    failures.append(f"{label}.acceptedParentImage is required for {role}")
                elif not isinstance(parent_hash, str) or not HASH_RE.fullmatch(parent_hash):
                    failures.append(f"{label}.acceptedParentSha256 must be SHA-256")
                else:
                    parent_path = Path(parent_image)
                    if not parent_path.is_absolute():
                        parent_path = contract_path.parent / parent_path
                    parent_bindings[stem] = {
                        "path": parent_path.resolve(),
                        "sha256": parent_hash.lower(),
                        "role": role,
                    }
        if found_position_roles != positioned_roles:
            failures.append(
                f"{location} position roles must be {sorted(positioned_roles)}, "
                f"got {sorted(found_position_roles)}"
            )

        children = record.get("children", [])
        if not isinstance(children, list):
            failures.append(f"{location}.children must be a list")
            children = []
        if delivery_class == "container-state":
            if record.get("containerGrantMode") not in {"clickable-children", "atomic-grant"}:
                failures.append(f"{location}.containerGrantMode is required")
            if not children:
                failures.append(f"{location} must enumerate all contained records")
        elif children:
            failures.append(f"{location}.children is only valid for container-state")
        for index, child in enumerate(children):
            visit(child, f"{location}.children[{index}]")

        semantic_records.append({
            "recordId": record_id,
            "deliveryClass": delivery_class,
            "assetRoles": sorted(roles),
            "positionRoles": sorted(found_position_roles),
        })

    records = contract.get("records")
    if not isinstance(records, list) or not records:
        failures.append("records must be a non-empty list")
    else:
        for index, record in enumerate(records):
            visit(record, f"records[{index}]")

    raw_hashes = contract.get("artifactSha256")
    artifact_hashes: dict[str, str] = {}
    expected_hash_names = required_png | {"XYposition.txt"}
    if not isinstance(raw_hashes, dict):
        failures.append("artifactSha256 must be an object")
        raw_hashes = {}
    missing_hashes = sorted(expected_hash_names - set(raw_hashes))
    extra_hashes = sorted(set(raw_hashes) - expected_hash_names)
    if missing_hashes:
        failures.append(f"artifactSha256 missing entries: {missing_hashes}")
    if extra_hashes:
        failures.append(f"artifactSha256 has unexpected entries: {extra_hashes}")
    for name, value in raw_hashes.items():
        if not isinstance(value, str) or not HASH_RE.fullmatch(value):
            failures.append(f"artifactSha256[{name}] must be SHA-256")
        else:
            artifact_hashes[name] = value.lower()
    for stem, filename in position_assets.items():
        if artifact_hashes.get(filename) != position_hashes.get(stem):
            failures.append(f"coordinate {stem} is not bound to the current Map hash")

    raw_roots = contract.get("replicaScanRoots")
    replica_roots: list[Path] = []
    if not nonempty_string_list(raw_roots):
        failures.append("replicaScanRoots must enumerate active scene package roots")
    else:
        for raw in raw_roots:
            path = Path(raw)
            if not path.is_absolute():
                path = contract_path.parent / path
            replica_roots.append(path.resolve())

    return {
        "failures": failures,
        "requiredPng": sorted(required_png),
        "expectedXy": expected_xy,
        "positionAssets": position_assets,
        "parentBindings": parent_bindings,
        "artifactSha256": artifact_hashes,
        "replicaScanRoots": replica_roots,
        "semanticRecords": semantic_records,
    }


def verify_parent_pixels(
    folder: Path,
    expected_xy: dict[str, tuple[int, int]],
    position_assets: dict[str, str],
    parent_bindings: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Verify release Map pixels against the hash-bound accepted parent."""
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    for stem, binding in sorted(parent_bindings.items()):
        parent_path = binding["path"]
        asset_path = folder / position_assets[stem]
        item: dict[str, Any] = {
            "stem": stem,
            "role": binding["role"],
            "assetPath": str(asset_path),
            "acceptedParentImage": str(parent_path),
            "passed": True,
        }
        if not parent_path.is_file():
            failures.append(f"accepted parent does not exist for {stem}: {parent_path}")
            item["passed"] = False
            results.append(item)
            continue
        actual_parent_hash = sha256(parent_path).lower()
        item["acceptedParentSha256"] = actual_parent_hash
        if actual_parent_hash != binding["sha256"]:
            failures.append(f"accepted parent hash mismatch for {stem}: {parent_path}")
            item["passed"] = False
        if not asset_path.is_file():
            failures.append(f"parent-pixel check lacks formal asset for {stem}: {asset_path}")
            item["passed"] = False
            results.append(item)
            continue
        try:
            with Image.open(parent_path) as parent_source, Image.open(asset_path) as sprite_source:
                sprite_mode = sprite_source.mode
                parent = parent_source.convert("RGBA")
                sprite = sprite_source.convert("RGBA")
                x, y = expected_xy[stem]
                width, height = sprite.size
                item.update({
                    "position": [x, y],
                    "spriteSize": [width, height],
                    "spriteMode": sprite_mode,
                })
                if sprite_mode != "RGBA":
                    failures.append(f"formal irregular asset is not RGBA for {stem}: {sprite_mode}")
                    item["passed"] = False
                if x < 0 or y < 0 or x + width > parent.width or y + height > parent.height:
                    failures.append(f"formal asset lies outside accepted parent for {stem}")
                    item["passed"] = False
                else:
                    parent_crop = parent.crop((x, y, x + width, y + height))
                    sprite_pixels = list(sprite.getdata())
                    parent_pixels = list(parent_crop.getdata())
                    visible_count = 0
                    visible_mismatches = 0
                    transparent_rgb_nonzero = 0
                    for sprite_pixel, parent_pixel in zip(sprite_pixels, parent_pixels):
                        if sprite_pixel[3] > 0:
                            visible_count += 1
                            if sprite_pixel[:3] != parent_pixel[:3]:
                                visible_mismatches += 1
                        elif sprite_pixel[:3] != (0, 0, 0):
                            transparent_rgb_nonzero += 1
                    item.update({
                        "visiblePixelCount": visible_count,
                        "visibleRgbMismatchCount": visible_mismatches,
                        "transparentRgbNonzeroCount": transparent_rgb_nonzero,
                    })
                    if visible_count == 0:
                        failures.append(f"formal irregular asset has empty Alpha for {stem}")
                        item["passed"] = False
                    if visible_mismatches:
                        failures.append(
                            f"formal asset visible RGB differs from accepted parent for {stem}: "
                            f"{visible_mismatches} pixels"
                        )
                        item["passed"] = False
                    if transparent_rgb_nonzero:
                        failures.append(
                            f"formal asset carries RGB under Alpha 0 for {stem}: "
                            f"{transparent_rgb_nonzero} pixels"
                        )
                        item["passed"] = False
        except (OSError, ValueError) as exc:
            failures.append(f"cannot verify parent pixels for {stem}: {exc}")
            item["passed"] = False
        results.append(item)
    return results, failures


def is_history_path(path: Path) -> bool:
    return any(
        token in part.lower()
        for part in path.parts
        for token in HISTORY_PATH_TOKENS
    )


def scan_replicas(
    roots: list[Path],
    expected_xy: dict[str, tuple[int, int]],
    position_assets: dict[str, str],
    artifact_hashes: dict[str, str],
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    visited: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            failures.append(f"replica scan root does not exist: {root}")
            continue
        for xy_path in root.rglob("XYposition.txt"):
            resolved = xy_path.resolve()
            if resolved in visited or is_history_path(xy_path):
                continue
            visited.add(resolved)
            entries, xy_errors = parse_xy(xy_path)
            stems = sorted(set(entries) & set(expected_xy))
            if not stems:
                continue
            item = {"xyPath": str(resolved), "stems": stems, "passed": True}
            for error in xy_errors:
                failures.append(f"{resolved}: {error}")
                item["passed"] = False
            for stem in stems:
                if entries[stem] != expected_xy[stem]:
                    failures.append(
                        f"stale active replica coordinate {stem} in {resolved}: "
                        f"{entries[stem]} != {expected_xy[stem]}"
                    )
                    item["passed"] = False
                filename = position_assets[stem]
                asset_path = xy_path.parent / filename
                if not asset_path.is_file():
                    failures.append(f"active replica {resolved} lacks {filename}")
                    item["passed"] = False
                elif sha256(asset_path).lower() != artifact_hashes.get(filename):
                    failures.append(f"stale active replica asset: {asset_path}")
                    item["passed"] = False
            results.append(item)
    return results, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--release-contract", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    folder = args.folder.resolve()
    contract_path = args.release_contract.resolve()
    contract = validate_contract(contract_path)
    failures = list(contract.get("failures", []))
    required_png = contract.get("requiredPng", [])
    expected_xy = contract.get("expectedXy", {})
    artifact_hashes = contract.get("artifactSha256", {})

    files = sorted(folder.iterdir()) if folder.is_dir() else []
    if not folder.is_dir():
        failures.append(f"formal folder does not exist: {folder}")
    actual_files = [path for path in files if path.is_file()]
    actual_names = {path.name for path in actual_files}
    allowed_names = set(required_png) | {"XYposition.txt"}
    missing = sorted(allowed_names - actual_names)
    extra = sorted(actual_names - allowed_names)
    if missing:
        failures.append(f"missing required files: {missing}")
    if extra:
        failures.append(f"unexpected files: {extra}")
    for path in actual_files:
        lowered = path.name.lower()
        if path.name != "XYposition.txt" and path.suffix.lower() != ".png":
            failures.append(f"non-PNG formal image asset: {path.name}")
        tokens = [token for token in FORBIDDEN_FORMAL_TOKENS if token in lowered]
        if tokens:
            failures.append(f"forbidden formal filename token in {path.name}: {tokens}")
        expected_hash = artifact_hashes.get(path.name)
        if expected_hash and sha256(path).lower() != expected_hash:
            failures.append(f"formal artifact hash mismatch: {path.name}")

    xy_path = folder / "XYposition.txt"
    if xy_path.is_file():
        xy_entries, xy_errors = parse_xy(xy_path)
        failures.extend(xy_errors)
    else:
        xy_entries = {}
    if set(xy_entries) != set(expected_xy):
        failures.append(
            f"XY stem set mismatch: actual={sorted(xy_entries)}, "
            f"expected={sorted(expected_xy)}"
        )
    for stem, coordinate in expected_xy.items():
        if stem in xy_entries and xy_entries[stem] != coordinate:
            failures.append(
                f"formal XY coordinate mismatch for {stem}: "
                f"{xy_entries[stem]} != {coordinate}"
            )

    replica_results, replica_failures = scan_replicas(
        contract.get("replicaScanRoots", []),
        expected_xy,
        contract.get("positionAssets", {}),
        artifact_hashes,
    )
    failures.extend(replica_failures)
    parent_pixel_results, parent_pixel_failures = verify_parent_pixels(
        folder,
        expected_xy,
        contract.get("positionAssets", {}),
        contract.get("parentBindings", {}),
    )
    failures.extend(parent_pixel_failures)
    passed = not failures
    payload = {
        "version": 1,
        "kind": "ndc-semantic-formal-release-verification",
        "folder": str(folder),
        "releaseContract": str(contract_path),
        "requiredPng": required_png,
        "expectedXy": {stem: list(value) for stem, value in sorted(expected_xy.items())},
        "semanticRecords": contract.get("semanticRecords", []),
        "activeReplicaChecks": replica_results,
        "acceptedParentPixelChecks": parent_pixel_results,
        "failures": failures,
        "passed": passed,
        "productionEligible": passed,
    }
    if args.report:
        args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
        args.report.resolve().write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
