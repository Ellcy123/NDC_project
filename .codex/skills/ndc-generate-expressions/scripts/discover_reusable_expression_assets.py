#!/usr/bin/env python3
"""Discover same-character reusable expression candidates across historical Unit roots.

Discovery is intentionally conservative. It never approves reuse: it only emits
exact or declared-alias candidates for the file-level census and human review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from PIL import Image


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("表情", "")
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "_", value).strip("_")


def normalized_stem(path: Path) -> str:
    name = path.name
    while Path(name).suffix.casefold() in {".png", ".jpg", ".jpeg", ".webp"}:
        name = Path(name).stem
    return normalize(name)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def profile_for(path: Path) -> str:
    parts = [normalize(part) for part in path.parts]
    if any("透明" in part or part == "transparent" for part in parts):
        return "transparent"
    if any("绿幕" in part or part == "greenscreen" for part in parts):
        return "greenscreen"
    return "unknown"


def describe(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {
            "path": str(path.resolve()),
            "sha256": sha256(path),
            "size": list(image.size),
            "mode": image.mode,
            "profile": profile_for(path),
        }


def character_matches(path: Path, aliases: set[str]) -> bool:
    stem = normalized_stem(path)
    parts = {normalize(part) for part in path.parts}
    for alias in aliases:
        if alias in parts or stem == alias or stem.startswith(alias + "_"):
            return True
    return False


def expression_match(path: Path, character_aliases: set[str], expression_id: str, semantic_aliases: set[str]) -> str | None:
    stem = normalized_stem(path)
    exact = normalize(expression_id)
    suffixes = {stem}
    for alias in character_aliases:
        if stem.startswith(alias + "_"):
            suffixes.add(stem[len(alias) + 1 :])
    if exact in suffixes or stem.endswith("_" + exact):
        return "EXACT_EXPRESSION_ID"
    normalized_aliases = {normalize(value) for value in semantic_aliases}
    if any(alias in suffixes or stem.endswith("_" + alias) for alias in normalized_aliases):
        return "DECLARED_SEMANTIC_ALIAS"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    roots = [Path(value).resolve() for value in manifest.get("search_roots", [])]
    characters = manifest.get("characters", [])
    if not roots or not characters:
        raise ValueError("Manifest requires non-empty search_roots and characters")
    for root in roots:
        if not root.is_dir():
            raise FileNotFoundError(root)

    pngs = sorted({path.resolve() for root in roots for path in root.rglob("*.png")})
    rows: list[dict[str, object]] = []
    for character in characters:
        character_id = character["character_id"]
        aliases = {normalize(character_id), *(normalize(value) for value in character.get("aliases", []))}
        semantic_map = character.get("semantic_aliases", {})
        same_character = [path for path in pngs if character_matches(path, aliases)]
        for expression_id in character["requirements"]:
            candidates = []
            for path in same_character:
                match_type = expression_match(
                    path,
                    aliases,
                    expression_id,
                    set(semantic_map.get(expression_id, [])),
                )
                if match_type:
                    candidates.append({"match_type": match_type, **describe(path)})
            profiles = {"transparent": 0, "greenscreen": 0, "unknown": 0}
            for candidate in candidates:
                profiles[str(candidate["profile"])] += 1
            if not candidates:
                status = "NO_CANDIDATE"
            elif profiles["unknown"]:
                status = "REVIEW_REQUIRED_UNKNOWN_PROFILE"
            elif profiles["transparent"] > 1 or profiles["greenscreen"] > 1:
                status = "REVIEW_REQUIRED_MULTIPLE_CANDIDATES"
            elif any(item["match_type"] == "DECLARED_SEMANTIC_ALIAS" for item in candidates):
                status = "REVIEW_REQUIRED_SEMANTIC_ALIAS"
            else:
                status = "EXACT_CANDIDATE_FOUND"
            rows.append(
                {
                    "character_id": character_id,
                    "expression_id": expression_id,
                    "status": status,
                    "profile_candidate_counts": profiles,
                    "candidates": candidates,
                }
            )

    record = {
        "schema_version": 1,
        "kind": "ndc_expression_historical_reuse_discovery",
        "search_roots": [str(root) for root in roots],
        "scope_rule": "same-character candidates only; cross-character same-name files are excluded",
        "approval_rule": "discovery never authorizes reuse; exact profile census, provenance review, and byte hash freeze remain required",
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
