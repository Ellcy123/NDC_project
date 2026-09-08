#!/usr/bin/env python3
"""Export or verify immutable prompt blocks from the NDC prompt library."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROMPT_IDS = ("character-card-default", "portrait", "portrait-single-reference")
PORTRAIT_REFERENCE_ROLES = {
    "portrait": ["identity", "style_only"],
    "portrait-single-reference": ["identity"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-library", required=True, type=Path)
    parser.add_argument("--prompt-id", required=True, choices=PROMPT_IDS)
    parser.add_argument("--reference-manifest", type=Path,
                        help="Validate ordered portrait image roles and current source hashes; old text-only calls remain supported")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--export", type=Path)
    action.add_argument("--verify", type=Path)
    return parser.parse_args()


def normalize(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip("\n")


def extract_prompt(library: Path, prompt_id: str) -> str:
    text = library.read_text(encoding="utf-8")
    begin = f"<!-- LOCKED_PROMPT:{prompt_id}:BEGIN -->"
    end = f"<!-- LOCKED_PROMPT:{prompt_id}:END -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError(f"Expected exactly one marker pair for {prompt_id}")
    segment = text.split(begin, 1)[1].split(end, 1)[0].strip()
    lines = segment.splitlines()
    if len(lines) < 3 or lines[0].strip() != "```text" or lines[-1].strip() != "```":
        raise ValueError(f"Locked block for {prompt_id} must contain one fenced text block")
    return normalize("\n".join(lines[1:-1]))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_reference_manifest(manifest_path: Path, prompt_id: str) -> None:
    """Bind a portrait prompt branch to the actual ordered, immutable image inputs."""
    expected = PORTRAIT_REFERENCE_ROLES.get(prompt_id)
    if expected is None:
        raise ValueError("Reference manifest validation is defined for portrait branches only")
    manifest_path = manifest_path.resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("prompt_id") != prompt_id:
        raise ValueError("Reference manifest prompt_id does not match the locked branch")
    rows = data.get("references")
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError(f"Expected exactly {len(expected)} reference image(s) for {prompt_id}")
    for index, (row, role) in enumerate(zip(rows, expected), start=1):
        if not isinstance(row, dict) or row.get("role") != role:
            raise ValueError(f"Reference {index} must have role {role}")
        path_value = row.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            raise ValueError(f"Reference {index} has no path")
        path = Path(path_value)
        if not path.is_absolute():
            path = manifest_path.parent / path
        if not path.is_file():
            raise ValueError(f"Reference {index} is not a file: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if row.get("sha256") != actual:
            raise ValueError(f"Reference {index} SHA-256 does not match current file")


def main() -> None:
    args = parse_args()
    library = args.prompt_library.resolve()
    source = extract_prompt(library, args.prompt_id)

    if args.export:
        target = args.export.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source + "\n", encoding="utf-8", newline="\n")
        print(f"PROMPT_EXPORTED: {target}")
        print(f"PROMPT_SHA256: {digest(source)}")
        return

    submitted = normalize(args.verify.resolve().read_text(encoding="utf-8"))
    if submitted != source:
        print(f"PROMPT_LOCK_FAIL: {args.prompt_id}")
        print(f"EXPECTED_SHA256: {digest(source)}")
        print(f"ACTUAL_SHA256: {digest(submitted)}")
        raise SystemExit(1)
    if args.reference_manifest:
        try:
            verify_reference_manifest(args.reference_manifest, args.prompt_id)
        except (ValueError, OSError, TypeError) as exc:
            print(f"REFERENCE_LOCK_FAIL: {exc}")
            raise SystemExit(1) from exc
        print(f"REFERENCE_LOCK_PASS: {args.prompt_id}")
    print(f"PROMPT_LOCK_PASS: {args.prompt_id}")
    print(f"PROMPT_SHA256: {digest(source)}")


if __name__ == "__main__":
    main()
