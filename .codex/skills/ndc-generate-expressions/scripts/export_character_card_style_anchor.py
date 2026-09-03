#!/usr/bin/env python3
"""Export the art-style-only paragraph from the locked default character-card prompt."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


START = "并参考以下美术风格提示词确保风格统一："
STYLE_END = "film noir aesthetic, American 1928s era context,"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export the style-only paragraph from the default NDC general-style character-card prompt."
    )
    parser.add_argument("--prompt-library", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.prompt_library.resolve()
    text = source.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(STYLE_END, start)
    if start < 0 or end < 0:
        raise ValueError("Cannot find the locked default character-card style paragraph")
    paragraph = (text[start : end + len(STYLE_END)].rstrip(",") + ".").strip()
    forbidden = (
        "横向 16:9",
        "三个等比例完整全身视图",
        "full-body portrait standing",
        "minimalist pure white background",
        "isolated on white void",
    )
    if any(token in paragraph for token in forbidden):
        raise ValueError("Style extraction leaked character-card layout instructions")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(paragraph + "\n", encoding="utf-8")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"STYLE_ANCHOR_EXPORTED: {args.output.resolve()}")
    print(f"STYLE_ANCHOR_SOURCE: {source}")
    print(f"STYLE_ANCHOR_SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
