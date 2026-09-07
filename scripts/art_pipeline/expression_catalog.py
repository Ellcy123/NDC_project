#!/usr/bin/env python3
"""Read-only expression-catalog audit; no image edits or visual approval."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "美术资产交付/角色表情/表情索引.json"


def relative_name(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Expected a repository-relative forward-slash path: {value!r}")
    path = PurePosixPath(value)
    if (path.is_absolute() or PureWindowsPath(value).drive
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ValueError(f"Unsafe relative path: {value}")
    return path


def linked(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def safe_path(value: str, root: Path = ROOT, *, directory: bool = False) -> Path:
    parts = relative_name(value).parts
    path = root.joinpath(*parts)
    for component in [root, *[root.joinpath(*parts[:n]) for n in range(1, len(parts) + 1)]]:
        if linked(component):
            raise ValueError(f"Linked path is forbidden: {value}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes the planning repository: {value}")
    if directory:
        if not path.is_dir():
            raise ValueError(f"Expected a directory: {value}")
    elif not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"Expected a regular file: {value}")
    return path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git_tree(commit: str) -> dict[str, tuple[str, str]]:
    if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        raise ValueError("sourceCommit must be a full lowercase Git object ID")
    kind = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-t", commit],
                          capture_output=True, check=True).stdout.strip()
    if kind != b"commit":
        raise ValueError("sourceCommit is not a Git commit")
    output = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-rz", "--full-tree", commit],
                            capture_output=True, check=True).stdout
    result = {}
    for entry in output.split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, object_type, blob = metadata.decode("ascii").split()
        if object_type == "blob":
            result[name.decode("utf-8")] = (mode, blob)
    return result


def png_inventory(directory: Path, errors: list[str]) -> set[str]:
    found = set()
    for current, dirs, files in os.walk(directory, followlinks=False):
        for name in list(dirs):
            path = Path(current) / name
            if linked(path):
                dirs.remove(name)
                errors.append(f"Linked directory in expression library: {path.relative_to(ROOT).as_posix()}")
        for name in files:
            path = Path(current) / name
            relative = path.relative_to(ROOT).as_posix()
            if linked(path) or not stat.S_ISREG(path.stat().st_mode):
                errors.append(f"Linked or non-regular library file: {relative}")
            elif path.suffix.lower() == ".png":
                found.add(relative)
    return found


def check_catalog(catalog: Path = CATALOG) -> dict:
    errors: list[str] = []
    catalog = safe_path(catalog.absolute().relative_to(ROOT).as_posix())
    data = read_json(catalog)
    if data.get("schemaVersion") != 1 or data.get("kind") != "ndc-expression-catalog":
        raise ValueError("Unsupported expression catalog schema")
    manifest = read_json(safe_path("canon_manifest.json"))
    chapters = {row["canonicalUnit"]: row for row in manifest["chapters"]}
    unit, episode = data.get("unit"), data.get("episode")
    if unit not in chapters or chapters[unit]["unityEpisode"] != episode:
        raise ValueError("Catalog Unit/Episode does not match canon_manifest.json")
    registry = read_json(safe_path(data["characterCardRegistry"]))
    cards = {row["characterId"]: row for row in registry["characters"]}
    if len(cards) != len(registry["characters"]):
        errors.append("Character-card registry contains duplicate identities")
    tree = git_tree(data["sourceCommit"])
    hash_algorithm = "sha1" if len(data["sourceCommit"]) == 40 else "sha256"
    library = catalog.parent
    library_relative = library.relative_to(ROOT).as_posix()
    safe_path(library_relative, directory=True)
    unit_relative = f"{library_relative}/{unit}"
    people, folders, pair_ids = set(), set(), set()
    paths, folded_paths, sources = set(), set(), set()
    pairs = references = assets = 0
    npc_sources = {}

    def asset_check(asset: dict, folder: str, surface: str, label: str) -> str | None:
        nonlocal assets
        assets += 1
        try:
            if not isinstance(asset, dict):
                raise ValueError("Asset must be an object")
            relative = relative_name(asset["path"])
            name = relative.name
            expected = f"{unit_relative}/{surface}/{folder}/{name}"
            if relative.as_posix() != expected or not name.lower().endswith(".png") or name.lower().endswith(".png.png"):
                raise ValueError(f"Noncanonical {surface} path: {asset['path']}")
            if asset["path"].casefold() in folded_paths:
                errors.append(f"Duplicate asset path: {asset['path']}")
            paths.add(asset["path"])
            folded_paths.add(asset["path"].casefold())
            original = relative_name(asset["originalPath"]).as_posix()
            if original in sources:
                errors.append(f"Duplicate original source: {original}")
            sources.add(original)
            source_entry = tree.get(original)
            if not source_entry or source_entry[0] not in {"100644", "100755"}:
                raise ValueError(f"Original PNG is not a regular blob in sourceCommit: {original}")
            if source_entry[1] != asset["gitBlob"]:
                errors.append(f"Source Git blob mismatch: {original}")
            raw = safe_path(asset["path"]).read_bytes()
            if not re.fullmatch(r"[0-9a-f]{64}", str(asset["sha256"])) or hashlib.sha256(raw).hexdigest() != asset["sha256"]:
                errors.append(f"SHA-256 mismatch: {asset['path']}")
            blob = hashlib.new(hash_algorithm, b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
            if blob != asset["gitBlob"] or blob != source_entry[1]:
                errors.append(f"Current bytes differ from original Git blob: {asset['path']}")
            with Image.open(io.BytesIO(raw)) as image:
                if image.format != "PNG":
                    raise ValueError("Image content is not PNG")
                image.verify()
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                if asset.get("mode") not in {"RGB", "RGBA"} or image.mode != asset["mode"]:
                    errors.append(f"Image mode mismatch: {asset['path']}")
                size = asset.get("size")
                if (not isinstance(size, list) or len(size) != 2
                        or any(type(n) is not int or n <= 0 for n in size) or list(image.size) != size):
                    errors.append(f"Image dimensions mismatch: {asset['path']}")
                if surface == "透明":
                    if image.mode != "RGBA":
                        errors.append(f"Transparent image has no RGBA channel: {asset['path']}")
                    else:
                        low, high = image.getchannel("A").getextrema()
                        if low == 255 or high == 0:
                            errors.append(f"Transparent image lacks visible content or actual transparency: {asset['path']}")
            return name
        except (OSError, ValueError, KeyError, TypeError, SyntaxError) as exc:
            errors.append(f"{label}: {exc}")
            return None

    characters = data.get("characters")
    if not isinstance(characters, list) or not characters:
        raise ValueError("characters must be a nonempty list")
    for person in characters:
        try:
            key = person["characterId"]
            if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", key) or key in people:
                raise ValueError(f"Invalid or duplicate characterId: {key}")
            people.add(key)
            folder = person["folder"]
            if len(relative_name(folder).parts) != 1 or folder.casefold() in folders:
                raise ValueError(f"Invalid or duplicate person folder: {folder}")
            folders.add(folder.casefold())
            if not isinstance(person.get("displayName"), str) or not person["displayName"].strip():
                errors.append(f"Missing display name: {key}")
            card_id = person["cardCharacterId"]
            if card_id is not None and card_id not in cards:
                errors.append(f"Unknown cardCharacterId: {key}: {card_id}")
            evidence = person.get("identityEvidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"Missing identity evidence: {key}")
            else:
                for item in evidence:
                    safe_path(item["path"])
                    if not isinstance(item.get("basis"), str) or not item["basis"].strip():
                        errors.append(f"Missing identity-evidence basis: {key}")
            for npc in person["npcIds"]:
                source_path = safe_path(npc["source"])
                if npc["source"] not in npc_sources:
                    npc_sources[npc["source"]] = {str(row["id"]): row for row in read_json(source_path)}
                row = npc_sources[npc["source"]].get(str(npc["id"]))
                names = row.get("Name") if row else None
                if isinstance(names, str):
                    names = [names]
                if not row or row.get("Chapter") != npc["episode"] or npc["sourceName"] not in (names or []):
                    errors.append(f"NPC identity evidence mismatch: {key}: {npc['id']}")
            expressions = person["expressions"]
            if not isinstance(expressions, list):
                raise ValueError(f"expressions must be a list: {key}")
            expression_ids = set()
            for expression in expressions:
                pairs += 1
                expression_id, pair_id = expression["expressionId"], expression["pairId"]
                if not isinstance(expression_id, str) or not expression_id or expression_id in expression_ids:
                    errors.append(f"Invalid or duplicate expressionId: {key}: {expression_id}")
                expression_ids.add(expression_id)
                if not isinstance(pair_id, str) or not pair_id or pair_id in pair_ids:
                    errors.append(f"Invalid or duplicate pairId: {pair_id}")
                pair_ids.add(pair_id)
                if (expression.get("approvalStatus") not in {"unconfirmed", "approved", "rejected"}
                        or (expression.get("approvalStatus") == "approved" and not expression.get("approvalEvidence"))):
                    errors.append(f"Invalid approval state or missing approval evidence: {pair_id}")
                green = asset_check(expression["greenscreen"], folder, "绿幕", f"{pair_id}:greenscreen")
                transparent = asset_check(expression["transparent"], folder, "透明", f"{pair_id}:transparent")
                if green is not None and transparent is not None and green != transparent:
                    errors.append(f"Pair filenames differ: {pair_id}: {green} / {transparent}")
            for reference in person["references"]:
                references += 1
                if (reference.get("kind") != "reference_base"
                        or reference.get("approvalStatus") not in {"unconfirmed", "approved", "rejected"}
                        or (reference.get("approvalStatus") == "approved" and not reference.get("approvalEvidence"))):
                    errors.append(f"Invalid reference-base classification or approval state: {key}")
                asset_check(reference, folder, "参考底图", f"{key}:reference_base")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"Character record: {exc}")

    actual = png_inventory(library, errors)
    original_pngs = {name for name in tree if name.startswith(library_relative + "/") and name.lower().endswith(".png")}
    for missing in sorted(paths - actual):
        errors.append(f"Indexed PNG is missing from library: {missing}")
    for extra in sorted(actual - paths):
        errors.append(f"Unindexed PNG in library: {extra}")
    for missing in sorted(original_pngs - sources):
        errors.append(f"Source-commit PNG is not accounted for: {missing}")
    for extra in sorted(sources - original_pngs):
        errors.append(f"Indexed original source is outside the committed expression library: {extra}")
    source_count = data.get("sourceCount")
    if (type(source_count) is not int or source_count != assets or source_count != len(actual)
            or source_count != len(sources) or source_count != len(original_pngs)):
        errors.append("sourceCount differs from indexed assets, actual PNGs, unique sources, or source-commit PNGs")
    return {"status": "error" if errors else "ok", "scope": "metadata-bytes-paths-only",
            "unit": unit, "episode": episode, "characters": len(people), "pairs": pairs,
            "references": references, "assets": assets, "actualPng": len(actual),
            "sourcePng": len(original_pngs), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True, help="Audit without changing any file")
    parser.add_argument("--catalog", type=Path, default=CATALOG, help="Catalog within the planning repository")
    args = parser.parse_args()
    try:
        result = check_catalog(args.catalog)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        result = {"status": "error", "scope": "metadata-bytes-paths-only", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
