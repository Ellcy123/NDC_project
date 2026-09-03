#!/usr/bin/env python3
"""Compose a complete RGBA bust into one NDC delivery profile.

Only uniform scale, translation, and background composition are permitted.
Upscaling is refused: a delivery profile may consume native detail once through
one final downsample, but it may not invent detail by enlarging a smaller source.
Top or side subject clipping is refused. Bottom exit is recorded because a
complete master may naturally continue below the final dialogue-portrait frame.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from expression_audit_core import bottom_continuity_metrics


SPECS = {
    "transparent": {"size": (1164, 916), "mode": "RGBA", "background": (0, 0, 0, 0)},
    "greenscreen": {"size": (1536, 1024), "mode": "RGB", "background": (0, 255, 43, 255)},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose an NDC expression profile asset.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=tuple(SPECS))
    parser.add_argument("--scale", required=True, type=float)
    parser.add_argument("--offset-x", required=True, type=float)
    parser.add_argument("--offset-y", required=True, type=float)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()

    source = args.input.resolve()
    output = args.output.resolve()
    audit = args.audit.resolve()
    if not source.is_file():
        raise SystemExit(f"Missing input: {source}")
    if args.scale <= 0:
        raise SystemExit("Scale must be positive")
    if args.scale > 1.0:
        raise SystemExit(
            "REFUSED_PROFILE_UPSCALE: uniform scale must be <= 1.0. "
            "Return to a higher-resolution neutral/native source instead of enlarging delivery pixels."
        )

    image = Image.open(source).convert("RGBA")
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    source_bottom = bottom_continuity_metrics(alpha > 8)
    if source_bottom["screening_status"] != "CLEAR":
        raise SystemExit(
            "REFUSED_INCOMPLETE_SOURCE_BOTTOM: native source is floating, hollow, "
            f"or lacks a continuous lower torso: {source_bottom}"
        )
    ys, xs = np.nonzero(alpha > 8)
    if not len(xs):
        raise SystemExit("No foreground detected")
    width, height = SPECS[args.profile]["size"]
    new_size = (max(1, int(round(image.width * args.scale))), max(1, int(round(image.height * args.scale))))
    offset_x = int(round(args.offset_x))
    offset_y = int(round(args.offset_y))
    transformed_bbox = [
        int(round(xs.min() * args.scale + offset_x)),
        int(round(ys.min() * args.scale + offset_y)),
        int(round((xs.max() + 1) * args.scale + offset_x - 1)),
        int(round((ys.max() + 1) * args.scale + offset_y - 1)),
    ]
    if transformed_bbox[0] < 0 or transformed_bbox[2] >= width or transformed_bbox[1] < 0:
        raise SystemExit(f"REFUSED_TOP_OR_SIDE_CLIP: transformed bbox {transformed_bbox}, canvas {(width, height)}")

    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), SPECS[args.profile]["background"])
    canvas.paste(resized, (offset_x, offset_y), resized)
    if args.profile == "transparent":
        result = canvas
    else:
        background = Image.new("RGBA", (width, height), SPECS[args.profile]["background"])
        result = Image.alpha_composite(background, canvas).convert("RGB")

    output.parent.mkdir(parents=True, exist_ok=True)
    audit.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    record = {
        "schema_version": 1,
        "kind": "ndc_expression_profile_composition",
        "source": {"path": str(source), "sha256": sha256(source), "size": list(image.size)},
        "source_bottom_continuity": source_bottom,
        "output": {"path": str(output), "sha256": sha256(output), "size": [width, height], "profile": args.profile},
        "transform": {
            "uniform_scale": args.scale,
            "offset_xy": [offset_x, offset_y],
            "upscale_used": False,
            "resample_count": 1,
            "resampling_filter": "LANCZOS",
        },
        "transformed_foreground_bbox_xyxy": transformed_bbox,
        "top_or_side_subject_clipping": False,
        "bottom_exit_px": max(0, transformed_bbox[3] - (height - 1)),
        "interior_pixels_regenerated": False,
        "formal_status": "NOT_CHECKED",
    }
    audit.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
