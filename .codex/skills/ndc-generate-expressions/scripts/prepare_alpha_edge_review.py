#!/usr/bin/env python3
"""Prepare review-only previews for a user-returned native RGBA foreground."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


BACKGROUNDS = {
    "white": (255, 255, 255, 255),
    "mid_gray": (128, 128, 128, 255),
    "dark_gray": (48, 48, 48, 255),
    "black": (0, 0, 0, 255),
    "exact_green": (0, 255, 43, 255),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create edge-review previews. Evidence only; never assigns PASS."
    )
    parser.add_argument("--input", required=True, type=Path, help="RGBA foreground candidate")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    if not input_path.is_file():
        raise SystemExit(f"Missing input: {input_path}")

    cutout = Image.open(input_path).convert("RGBA")
    low, high = cutout.getchannel("A").getextrema()
    if low == high == 255:
        raise SystemExit("SOURCE_HAS_NO_TRANSPARENCY")
    if high == 0:
        raise SystemExit("SOURCE_ALPHA_IS_EMPTY")

    output_dir.mkdir(parents=True, exist_ok=True)
    previews: dict[str, str] = {}
    for name, color in BACKGROUNDS.items():
        background = Image.new("RGBA", cutout.size, color)
        preview = Image.alpha_composite(background, cutout).convert("RGB")
        path = output_dir / f"on-{name.replace('_', '-')}.png"
        preview.save(path)
        previews[name] = str(path)

    alpha_path = output_dir / "alpha-visualization.png"
    cutout.getchannel("A").save(alpha_path)
    evidence = {
        "schema_version": 2,
        "kind": "ndc_expression_alpha_edge_review_evidence",
        "source": {"path": str(input_path), "sha256": sha256(input_path)},
        "previews": previews,
        "alpha_visualization": str(alpha_path),
        "processor_authority": "USER_MANUAL_BACKGROUND_PROCESSING",
        "codex_background_removal_used": False,
        "protected_white_status": "NOT_CHECKED",
        "white_fringe_status": "NOT_CHECKED",
        "silhouette_status": "NOT_CHECKED",
        "formal_status": "NOT_CHECKED",
        "required_next_action": "Codex visual review at native 100% and nearest 200%; return failures to the user without Alpha repair.",
    }
    manifest_path = output_dir / "alpha-edge-review-evidence.json"
    manifest_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ALPHA_EDGE_REVIEW_PREPARED: {manifest_path}")
    print("FORMAL_STATUS: NOT_CHECKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
