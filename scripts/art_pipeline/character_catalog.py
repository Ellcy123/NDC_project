#!/usr/bin/env python3
"""Read-only audit of the character-card registry; never moves or deletes files."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "美术资产交付/角色/角色索引.json"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    registry = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    manifest = json.loads((ROOT / "canon_manifest.json").read_text(encoding="utf-8-sig"))
    units = {c["canonicalUnit"] for c in manifest["chapters"]}
    npcs = {str(n["id"]): n for n in json.loads(
        (ROOT / "avg_editor_v2/data/table/NPCStaticData.json").read_text(encoding="utf-8-sig"))}
    card_root = (CATALOG.parent / "人物").resolve()
    legacy_root = (ROOT / "image/角色卡666").resolve()

    def checked_path(value: str, base: Path = ROOT) -> Path:
        path = (base / value).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError(f"Path escapes planning repository: {value}")
        return path

    identities: set[str] = set()
    asset_ids: set[str] = set()
    paths: set[Path] = set()
    hashes: dict[str, str] = {}
    source_assets: dict[str, tuple[str, str]] = {}
    source_inventory = {s["originalPath"]: s for s in registry["sourceInventory"]}
    if len(source_inventory) != len(registry["sourceInventory"]):
        errors.append("Source inventory contains duplicate original paths")

    for person in registry["characters"]:
        key = person["characterId"]
        if key in identities or not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            errors.append(f"Invalid or duplicate characterId: {key}")
        identities.add(key)
        if not person.get("displayName") or not person.get("identityEvidence"):
            errors.append(f"Missing name or identity evidence: {key}")
        for evidence in person.get("identityEvidence", []):
            if not checked_path(evidence["path"]).is_file():
                errors.append(f"Missing identity evidence: {key}: {evidence['path']}")
        if not set(person["units"]).issubset(units):
            errors.append(f"Unknown Unit in {key}")
        for row in person["npcIds"]:
            npc = npcs.get(str(row["id"]))
            if not npc or npc["Chapter"] != row["episode"] or row["sourceName"] not in npc["Name"]:
                errors.append(f"NPC evidence changed: {key}: {row}")
        variants: set[tuple[str, str]] = set()
        for asset in person["assets"]:
            asset_id = asset["assetId"]
            if asset_id in asset_ids:
                errors.append(f"Duplicate assetId: {asset_id}")
            asset_ids.add(asset_id)
            variant = (asset["variant"], asset["colorMode"])
            if variant in variants:
                errors.append(f"Duplicate person / variant / colorMode: {key}: {variant}")
            variants.add(variant)
            path = checked_path(asset["path"])
            if not path.is_relative_to(card_root / key / "cards") or path in paths:
                errors.append(f"Invalid / duplicate canonical card path: {asset['path']}")
            paths.add(path)
            if not path.is_file() or digest(path) != asset["sha256"]:
                errors.append(f"Canonical image missing or hash mismatch: {asset['path']}")
            if asset["sha256"] in hashes:
                errors.append(f"Duplicate canonical image bytes: {asset_id} / {hashes[asset['sha256']]}")
            hashes[asset["sha256"]] = asset_id
            if asset["approvalStatus"] not in {"unconfirmed", "approved", "rejected"}:
                errors.append(f"Unknown approval status: {asset_id}")
            if asset["approvalStatus"] == "approved" and not asset.get("approvalEvidence"):
                errors.append(f"Approved asset lacks user confirmation evidence: {asset_id}")
            if not asset.get("sources"):
                errors.append(f"Asset lacks original source evidence: {asset_id}")
            for source in asset.get("sources", []):
                original = source["originalPath"]
                if original in source_assets:
                    errors.append(f"Source mapped more than once: {original}")
                source_assets[original] = (asset_id, asset["sha256"])
                if source["sha256"] != asset["sha256"]:
                    errors.append(f"Source bytes differ from canonical image: {original}")

    retained = migrated = unresolved = 0
    for original, source in source_inventory.items():
        path = checked_path(original)
        disposition = source["disposition"]
        if disposition not in {"migrated", "retained_compatibility", "retained_unidentified"}:
            errors.append(f"Unknown source disposition: {original}")
        if disposition == "migrated":
            migrated += 1
            if path.exists():
                warnings.append(f"A migrated source has reappeared; review before deduplication: {original}")
        else:
            retained += 1
            if not path.is_relative_to(legacy_root) or not path.is_file():
                errors.append(f"Compatibility source missing / outside old card root: {original}")
        if path.is_file() and digest(path) != source["sha256"]:
            errors.append(f"Original / compatibility source hash changed: {original}")
        if disposition == "retained_unidentified":
            unresolved += 1
            if source.get("assetId") or original in source_assets or not source.get("reason"):
                errors.append(f"Unidentified source incorrectly assigned or unexplained: {original}")
        elif source_assets.get(original) != (source.get("assetId"), source["sha256"]):
            errors.append(f"Source index and asset provenance disagree: {original}")
    if set(source_assets) - set(source_inventory):
        errors.append("Some asset original sources are missing from sourceInventory")
    for path in card_root.rglob("*.png"):
        if path.resolve() not in paths:
            errors.append(f"Unregistered canonical image: {path.relative_to(ROOT)}")
    for folder in [CATALOG.parent / "汇总未分类", CATALOG.parent / "Unit2", legacy_root]:
        if folder.exists():
            for path in folder.rglob("*.png"):
                if path.relative_to(ROOT).as_posix() not in source_inventory:
                    errors.append(f"New source image requires registration: {path.relative_to(ROOT)}")

    print(json.dumps({
        "ok": not errors,
        "readOnly": True,
        "characters": len(identities),
        "canonicalAssets": len(asset_ids),
        "originalSources": len(source_inventory),
        "migratedSources": migrated,
        "retainedCompatibilitySources": retained - unresolved,
        "unidentifiedSources": unresolved,
        "errors": errors,
        "warnings": warnings,
    }, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True, help="Validate images, hashes, provenance and identity metadata without writing")
    parser.parse_args()
    try:
        raise SystemExit(check())
    except (KeyError, ValueError, OSError) as exc:
        print(json.dumps({"ok": False, "readOnly": True, "errors": [str(exc)]}, ensure_ascii=False))
        raise SystemExit(1)
