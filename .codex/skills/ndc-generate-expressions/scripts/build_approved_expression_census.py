#!/usr/bin/env python3
"""Build a fail-closed file-level census before expression generation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {
            "path": str(path.resolve()),
            "sha256": sha256(path),
            "size": list(image.size),
            "mode": image.mode,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", required=True, type=Path, help="JSON array of required expression IDs")
    parser.add_argument("--character-prefix", required=True)
    parser.add_argument("--transparent-dir", type=Path)
    parser.add_argument("--greenscreen-dir", type=Path)
    parser.add_argument(
        "--calm-source",
        type=Path,
        help="User-confirmed original portrait when calm semantically equals that portrait",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    required = json.loads(args.requirements.read_text(encoding="utf-8"))
    if not isinstance(required, list) or not required or any(not isinstance(item, str) or not item for item in required):
        raise ValueError("Requirements must be a non-empty JSON array of expression IDs")
    profile_dirs = {"transparent": args.transparent_dir, "greenscreen": args.greenscreen_dir}
    profile_dirs = {key: value.resolve() for key, value in profile_dirs.items() if value is not None}
    if not profile_dirs:
        raise ValueError("At least one approved profile directory is required")
    for directory in profile_dirs.values():
        if not directory.is_dir():
            raise FileNotFoundError(directory)
    calm_source = args.calm_source.resolve() if args.calm_source else None
    if calm_source is not None and not calm_source.is_file():
        raise FileNotFoundError(calm_source)

    entries = []
    used: set[Path] = set()
    for expression_id in required:
        files: dict[str, object] = {}
        for profile, directory in profile_dirs.items():
            candidate = directory / f"{args.character_prefix}_{expression_id}.png"
            if candidate.is_file():
                files[profile] = describe(candidate)
                used.add(candidate.resolve())
        if len(files) == len(profile_dirs):
            action = "REUSE_APPROVED_AS_IS"
        elif files:
            action = "PARTIAL_PROFILE_GAP"
        elif expression_id == "calm" and calm_source is not None:
            action = "DERIVE_CALM_FROM_APPROVED_PORTRAIT"
        else:
            action = "GENERATE_NEW"
        entry = {"expression_id": expression_id, "production_action": action, "approved_files": files}
        if action == "DERIVE_CALM_FROM_APPROVED_PORTRAIT":
            entry["calm_source"] = describe(calm_source)
            entry["semantic_relation"] = "CALM_EQUALS_APPROVED_PORTRAIT"
        entries.append(entry)

    preserved = []
    for profile, directory in profile_dirs.items():
        for path in sorted(directory.glob(f"{args.character_prefix}_*.png")):
            if path.resolve() not in used:
                preserved.append({"profile": profile, **describe(path)})
    record = {
        "schema_version": 1,
        "kind": "ndc_approved_expression_census",
        "source_authority": "USER_APPROVED_EXISTING_ASSETS",
        "character_prefix": args.character_prefix,
        "required_profiles": list(profile_dirs),
        "requirements": entries,
        "unrequested_approved_assets_preserved": preserved,
        "all_requirements_routed": all(item["production_action"] != "PARTIAL_PROFILE_GAP" for item in entries),
        "warning": "Exact filename matches only. Semantic aliases require explicit reviewed mapping."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if record["all_requirements_routed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
