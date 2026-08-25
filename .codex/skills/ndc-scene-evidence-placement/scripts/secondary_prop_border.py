#!/usr/bin/env python3
"""Add or verify the final opaque 12 px frame for NDC Type 7 prop art.

This helper performs only deterministic raster work. Generation, cleanup, and
resizing must be complete before ``add`` is run. The input is retained as the
pixel-identity source for ``verify``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


WHITE = (255, 255, 255, 255)


def load_opaque(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema() != (255, 255):
        raise ValueError(
            f"Type 7 borderless source must be fully opaque before framing: {path}"
        )
    return rgba


def validate_border(border: int) -> None:
    if border <= 0:
        raise ValueError("--border must be a positive integer")


def framed_image(inner: Image.Image, border: int) -> Image.Image:
    validate_border(border)
    framed = Image.new(
        "RGBA",
        (inner.width + border * 2, inner.height + border * 2),
        WHITE,
    )
    framed.paste(inner, (border, border))
    return framed


def add_border(input_path: Path, output_path: Path, border: int) -> dict[str, object]:
    if output_path.exists():
        raise FileExistsError(f"Output already exists: {output_path}")
    if output_path.suffix.lower() != ".png":
        raise ValueError("Type 7 runtime output must use .png")
    inner = load_opaque(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    framed = framed_image(inner, border)
    framed.save(output_path)
    return {
        "passed": True,
        "input": str(input_path.resolve()),
        "output": str(output_path.resolve()),
        "border": border,
        "innerSize": [inner.width, inner.height],
        "outputSize": [framed.width, framed.height],
        "borderRGBA": list(WHITE),
    }


def verify_border(input_path: Path, output_path: Path, border: int) -> dict[str, object]:
    validate_border(border)
    inner = load_opaque(input_path)
    if not output_path.is_file():
        raise FileNotFoundError(output_path)
    with Image.open(output_path) as image:
        actual = image.convert("RGBA")
    expected = framed_image(inner, border)
    failures: list[str] = []

    if actual.size != expected.size:
        failures.append(
            f"Final size {actual.size} does not equal inner size plus "
            f"{border * 2}px: {expected.size}"
        )
    elif actual.tobytes() != expected.tobytes():
        failures.append(
            "Output pixels differ from the approved inner image plus the exact "
            "opaque white border"
        )

    return {
        "passed": not failures,
        "input": str(input_path.resolve()),
        "output": str(output_path.resolve()),
        "border": border,
        "innerSize": [inner.width, inner.height],
        "expectedOutputSize": [expected.width, expected.height],
        "actualOutputSize": [actual.width, actual.height],
        "borderRGBA": list(WHITE),
        "failures": failures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add or verify an opaque rectangular border for an NDC Type 7 prop"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("add", "verify"):
        child = subparsers.add_parser(command)
        child.add_argument("--input", required=True, type=Path)
        child.add_argument("--output", required=True, type=Path)
        child.add_argument("--border", type=int, default=12)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "add":
            report = add_border(args.input, args.output, args.border)
        else:
            report = verify_border(args.input, args.output, args.border)
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as error:
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=False))
        return 2

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    sys.exit(main())
