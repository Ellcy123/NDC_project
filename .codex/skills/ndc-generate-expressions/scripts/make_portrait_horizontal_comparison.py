#!/usr/bin/env python3
"""Build a deterministic three-up portrait/master/candidate review sheet.

This script prepares visual evidence only. It never decides identity or style.
All three inputs are shown with the same contain-fit box so framing differences
remain visible instead of being hidden by independent crops.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PANELS = (
    ("APPROVED PORTRAIT", "approved_portrait"),
    ("COMPLETED MASTER", "neutral_master"),
    ("RAW NATIVE CANDIDATE", "native_candidate"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkerboard(size: tuple[int, int], cell: int = 18) -> Image.Image:
    board = Image.new("RGB", size, (214, 214, 214))
    draw = ImageDraw.Draw(board)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(x + cell - 1, size[0] - 1), min(y + cell - 1, size[1] - 1)), fill=(184, 184, 184))
    return board


def render_panel(path: Path, box: tuple[int, int]) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    contained = ImageOps.contain(source, box, Image.Resampling.LANCZOS)
    panel = checkerboard(box).convert("RGBA")
    x = (box[0] - contained.width) // 2
    y = (box[1] - contained.height) // 2
    panel.alpha_composite(contained, (x, y))
    return panel.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-portrait", required=True, type=Path)
    parser.add_argument("--neutral-master", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--expression-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()

    sources = {
        "approved_portrait": args.approved_portrait.resolve(),
        "neutral_master": args.neutral_master.resolve(),
        "native_candidate": args.candidate.resolve(),
    }
    for path in sources.values():
        if not path.is_file():
            raise FileNotFoundError(path)

    panel_w, panel_h = 520, 620
    margin, gap, label_h = 32, 20, 54
    sheet = Image.new("RGB", (margin * 2 + panel_w * 3 + gap * 2, margin * 2 + label_h + panel_h + 36), (37, 39, 42))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, (label, key) in enumerate(PANELS):
        x = margin + index * (panel_w + gap)
        draw.text((x, margin + 14), label, fill=(245, 245, 245), font=font)
        panel = render_panel(sources[key], (panel_w, panel_h))
        sheet.paste(panel, (x, margin + label_h))
        draw.rectangle((x, margin + label_h, x + panel_w - 1, margin + label_h + panel_h - 1), outline=(120, 124, 128), width=2)

    draw.text((margin, sheet.height - 24), f"Expression: {args.expression_id} | Evidence only - identity/style status remains NOT_CHECKED", fill=(220, 220, 220), font=font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)

    audit = {
        "schema_version": 1,
        "kind": "ndc_portrait_horizontal_comparison",
        "expression_id": args.expression_id,
        "sources": {key: {"path": str(path), "sha256": sha256(path)} for key, path in sources.items()},
        "comparison_sheet": {"path": str(args.output.resolve()), "sha256": sha256(args.output.resolve())},
        "matched_display_box": [panel_w, panel_h],
        "identity_vs_portrait": "NOT_CHECKED",
        "style_vs_portrait": "NOT_CHECKED",
        "viewpoint_continuity": "NOT_CHECKED",
        "formal_status": "NOT_CHECKED",
        "warning": "This tool creates evidence only. Codex must review the whole sheet and record identity, style, and viewpoint decisions.",
    }
    args.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
