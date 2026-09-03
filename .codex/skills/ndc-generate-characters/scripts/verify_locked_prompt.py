#!/usr/bin/env python3
"""Export or verify immutable prompt blocks from the NDC prompt library."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PROMPT_IDS = ("character-card-default", "portrait")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-library", required=True, type=Path)
    parser.add_argument("--prompt-id", required=True, choices=PROMPT_IDS)
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
    print(f"PROMPT_LOCK_PASS: {args.prompt_id}")
    print(f"PROMPT_SHA256: {digest(source)}")


if __name__ == "__main__":
    main()
