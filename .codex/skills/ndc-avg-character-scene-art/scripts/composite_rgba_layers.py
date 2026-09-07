#!/usr/bin/env python3
"""Bake positioned RGBA actor layers onto an immutable NDC AVG scene."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_layer(values: list[str]) -> tuple[str, Path, int, int]:
    name, path_value, x_value, y_value = values
    if not name.strip():
        raise ValueError("Layer name must not be empty")
    return name, Path(path_value), int(x_value), int(y_value)


def ensure_new_file(path: Path, source: Path) -> None:
    if path.resolve() == source.resolve():
        raise ValueError(f"Refusing to overwrite the source scene: {source}")
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alpha-composite RGBA actor layers and verify zero drift outside their union"
    )
    parser.add_argument("--scene", type=Path, required=True)
    parser.add_argument(
        "--layer",
        action="append",
        nargs=4,
        metavar=("NAME", "PNG", "X", "Y"),
        required=True,
        help="Repeat in back-to-front layer order",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--union-mask", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    scene_path = args.scene.resolve()
    output_path = args.output.resolve()
    mask_path = args.union_mask.resolve()
    report_path = args.report.resolve()
    if len({output_path, mask_path, report_path}) != 3:
        raise ValueError("--output, --union-mask, and --report must be three different files")
    ensure_new_file(output_path, scene_path)
    ensure_new_file(mask_path, scene_path)
    ensure_new_file(report_path, scene_path)

    source = Image.open(scene_path)
    if source.mode not in ("RGB", "RGBA"):
        raise ValueError(f"Scene mode must be RGB or RGBA, got {source.mode}")

    width, height = source.size
    composite = source.convert("RGBA")
    union_alpha = np.zeros((height, width), dtype=np.uint8)
    records: list[dict[str, object]] = []

    for raw_layer in args.layer:
        name, layer_path, x, y = parse_layer(raw_layer)
        layer_path = layer_path.resolve()
        layer = Image.open(layer_path)
        if layer.mode != "RGBA":
            raise ValueError(f"Layer {name} must be RGBA, got {layer.mode}: {layer_path}")

        layer_width, layer_height = layer.size
        if x < 0 or y < 0 or x + layer_width > width or y + layer_height > height:
            raise ValueError(
                f"Layer {name} rectangle {(x, y, x + layer_width, y + layer_height)} "
                f"is outside scene {(width, height)}"
            )

        alpha = np.asarray(layer.getchannel("A"), dtype=np.uint8)
        alpha_bbox = layer.getchannel("A").getbbox()
        if alpha_bbox is None:
            raise ValueError(f"Layer {name} has no visible alpha: {layer_path}")

        target = union_alpha[y : y + layer_height, x : x + layer_width]
        np.maximum(target, alpha, out=target)
        composite.alpha_composite(layer, (x, y))
        records.append(
            {
                "name": name,
                "path": str(layer_path),
                "sha256": sha256(layer_path),
                "canvas_size": [layer_width, layer_height],
                "position": [x, y],
                "alpha_bbox": list(alpha_bbox),
                "scene_alpha_bbox": [
                    x + alpha_bbox[0],
                    y + alpha_bbox[1],
                    x + alpha_bbox[2],
                    y + alpha_bbox[3],
                ],
            }
        )

    result = composite if source.mode == "RGBA" else composite.convert("RGB")
    result.save(output_path)
    Image.fromarray(union_alpha, mode="L").save(mask_path)

    source_array = np.asarray(source, dtype=np.int16)
    output_array = np.asarray(Image.open(output_path).convert(source.mode), dtype=np.int16)
    channel_difference = np.abs(output_array - source_array)
    changed_pixels = np.any(channel_difference != 0, axis=2)
    outside_union = union_alpha == 0
    outside_values = channel_difference[outside_union]
    outside_changed_pixels = int(np.count_nonzero(changed_pixels & outside_union))
    outside_max_difference = int(outside_values.max()) if outside_values.size else 0
    union_bbox = Image.fromarray(union_alpha, mode="L").getbbox()

    report = {
        "source": str(scene_path),
        "source_sha256": sha256(scene_path),
        "output": str(output_path),
        "output_sha256": sha256(output_path),
        "source_size": [width, height],
        "output_size": list(result.size),
        "source_mode": source.mode,
        "output_mode": result.mode,
        "layers": records,
        "union_mask": str(mask_path),
        "union_alpha_bbox": list(union_bbox) if union_bbox is not None else None,
        "changed_pixels_total": int(np.count_nonzero(changed_pixels)),
        "changed_pixels_outside_union": outside_changed_pixels,
        "outside_union_max_channel_difference": outside_max_difference,
        "outside_union_pixels_bit_identical": outside_changed_pixels == 0
        and outside_max_difference == 0,
        "passed": outside_changed_pixels == 0 and outside_max_difference == 0,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not report["passed"]:
        raise RuntimeError("Composite changed pixels outside the RGBA layer union")


if __name__ == "__main__":
    main()
