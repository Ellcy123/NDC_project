#!/usr/bin/env python3
"""Capture per-material shadow/midtone/highlight swatches from an approved portrait."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from calibrate_expression_color import rgb_to_lab


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize_band(rgb_pixels: np.ndarray, lab_pixels: np.ndarray) -> dict[str, object]:
    rgb = np.rint(np.median(rgb_pixels, axis=0)).astype(np.uint8)
    lab = np.median(lab_pixels, axis=0)
    return {
        "rgb": [int(v) for v in rgb],
        "hex": "#" + "".join(f"{int(v):02X}" for v in rgb),
        "lab_d65": [round(float(v), 4) for v in lab],
        "sample_pixels": int(len(rgb_pixels)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--regions", required=True, type=Path, help="JSON object with regions [{region_id, mask}]")
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-card", required=True, type=Path)
    args = parser.parse_args()

    reference = args.reference.resolve()
    manifest_path = args.regions.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    regions = manifest.get("regions") if isinstance(manifest, dict) else None
    if not isinstance(regions, list) or not regions:
        raise ValueError("Regions manifest requires a non-empty regions array")

    source = Image.open(reference).convert("RGBA")
    rgb_image = source.convert("RGB")
    rgb = np.asarray(rgb_image, dtype=np.uint8)
    lab = rgb_to_lab(rgb_image)
    alpha = np.asarray(source.getchannel("A"), dtype=np.uint8)
    summaries = []
    for item in regions:
        region_id = item.get("region_id") if isinstance(item, dict) else None
        mask_value = item.get("mask") if isinstance(item, dict) else None
        if not isinstance(region_id, str) or not region_id or not isinstance(mask_value, str):
            raise ValueError("Each region requires region_id and mask")
        mask_path = Path(mask_value)
        if not mask_path.is_absolute():
            mask_path = manifest_path.parent / mask_path
        mask_path = mask_path.resolve()
        mask_image = Image.open(mask_path).convert("L")
        if mask_image.size != source.size:
            raise ValueError(f"Mask size mismatch: {mask_path}")
        mask = (np.asarray(mask_image, dtype=np.uint8) > 127) & (alpha >= 245)
        pixels_lab = lab[mask]
        pixels_rgb = rgb[mask]
        if len(pixels_lab) < 96:
            raise ValueError(f"Region has fewer than 96 reviewed pixels: {region_id}")
        order = np.argsort(pixels_lab[:, 0], kind="stable")
        shadow_idx, midtone_idx, highlight_idx = np.array_split(order, 3)
        groups = {
            "shadow": shadow_idx,
            "midtone": midtone_idx,
            "highlight": highlight_idx,
        }
        tones = {name: summarize_band(pixels_rgb[idx], pixels_lab[idx]) for name, idx in groups.items()}
        q1 = float(pixels_lab[shadow_idx[-1], 0])
        q2 = float(pixels_lab[midtone_idx[-1], 0])
        summaries.append({
            "region_id": region_id,
            "mask": str(mask_path),
            "mask_sha256": sha256(mask_path),
            "sample_pixels": int(mask.sum()),
            "luminance_split_lab": [round(float(q1), 4), round(float(q2), 4)],
            "tones": tones,
        })

    card_w, row_h, label_w, swatch_w = 920, 110, 230, 210
    card = Image.new("RGB", (card_w, 70 + row_h * len(summaries)), (38, 40, 43))
    draw = ImageDraw.Draw(card)
    font = ImageFont.load_default()
    draw.text((24, 24), "APPROVED SEMANTIC PALETTE | SHADOW / MIDTONE / HIGHLIGHT", fill=(245, 245, 245), font=font)
    for row, summary in enumerate(summaries):
        y = 70 + row * row_h
        draw.text((24, y + 42), str(summary["region_id"]), fill=(245, 245, 245), font=font)
        for column, tone in enumerate(("shadow", "midtone", "highlight")):
            swatch = summary["tones"][tone]
            x = label_w + column * swatch_w
            draw.rectangle((x, y + 8, x + 178, y + 72), fill=tuple(swatch["rgb"]), outline=(220, 220, 220), width=1)
            lab_values = swatch["lab_d65"]
            draw.text((x, y + 78), f"{tone} {swatch['hex']} L{lab_values[0]:.1f} a{lab_values[1]:.1f} b{lab_values[2]:.1f}", fill=(230, 230, 230), font=font)

    args.output_card.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    card.save(args.output_card)
    record = {
        "schema_version": 1,
        "kind": "ndc_semantic_palette_anchor",
        "status": "PASS",
        "source": {"path": str(reference), "sha256": sha256(reference), "size": list(source.size)},
        "regions_manifest": {"path": str(manifest_path), "sha256": sha256(manifest_path)},
        "palette_card": {"path": str(args.output_card.resolve()), "sha256": sha256(args.output_card.resolve())},
        "color_space": "sRGB with CIELAB D65 numeric swatches",
        "tone_definition": "per-region stable L* ordering split into three equal-count bands; robust median RGB/Lab per band",
        "regions": summaries,
        "formal_note": "Palette capture does not authorize correction; Photoshop mask and before/after review remain required."
    }
    args.output_json.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
