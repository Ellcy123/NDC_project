#!/usr/bin/env python3
"""Run the shared NDC style-reference tiling helper."""

from pathlib import Path
import runpy


target = (
    Path(__file__).resolve().parents[2]
    / "ndc-generate-characters"
    / "scripts"
    / "make_style_review_tiles.py"
)
if not target.is_file():
    raise SystemExit(f"Shared tiling helper is missing: {target}")
runpy.run_path(str(target), run_name="__main__")
