#!/usr/bin/env python3
"""Screen a cutout for continuous lower-torso contact at the canvas bottom."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from expression_audit_core import bottom_continuity_metrics


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mask", type=Path, help="Reviewed grayscale mask for an opaque source")
    args = parser.parse_args()

    source = args.input.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    image = Image.open(source).convert("RGBA")
    if args.mask:
        mask_path = args.mask.resolve()
        mask_image = Image.open(mask_path).convert("L")
        if mask_image.size != image.size:
            raise ValueError("Mask size must match input")
        mask = np.asarray(mask_image, dtype=np.uint8) > 127
        mask_source = str(mask_path)
    else:
        alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
        if int((alpha < 255).sum()) == 0:
            raise ValueError("Opaque input requires --mask; RGB color must not infer the subject")
        mask = alpha > 8
        mask_source = "embedded_alpha_screening_only"

    metrics = bottom_continuity_metrics(mask)
    record = {
        "schema_version": 1,
        "kind": "ndc_bust_bottom_continuity_screen",
        "asset": {"path": str(source), "sha256": sha256(source), "size": list(image.size)},
        "mask_source": mask_source,
        "metrics": metrics,
        "screening_status": metrics["screening_status"],
        "semantic_status": "NOT_CHECKED",
        "manual_review": {
            "reviewer": None,
            "lower_torso_complete": None,
            "no_floating_oval_cutout": None,
            "no_internal_transparent_wedge": None,
            "natural_bottom_exit_ready": None,
            "status": "NOT_CHECKED"
        },
        "warning": "CLEAR is screening-only and never proves anatomical completeness."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"BOTTOM_CONTINUITY_SCREEN: {record['screening_status']}")
    return 0 if record["screening_status"] == "CLEAR" else 2


if __name__ == "__main__":
    raise SystemExit(main())
