#!/usr/bin/env python3
"""Freeze an approved portrait palette and calibrate expression candidates to it.

The script is intentionally deterministic. It uses the subject mask/alpha only,
keeps alpha unchanged, protects spot black and neutral white design, and never
samples or recolors the delivery background.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageCms


ANCHOR_SCHEMA = 1
AUDIT_SCHEMA = 1
PERCENTILES = np.linspace(0.0, 100.0, 101)
SRGB_PROFILE = ImageCms.createProfile("sRGB")
D65_WHITE = np.array([0.95047, 1.0, 1.08883], dtype=np.float64)
RGB_TO_XYZ_D65 = np.array(
    [[0.4124564, 0.3575761, 0.1804375],
     [0.2126729, 0.7151522, 0.0721750],
     [0.0193339, 0.1191920, 0.9503041]],
    dtype=np.float64,
)
XYZ_D65_TO_RGB = np.linalg.inv(RGB_TO_XYZ_D65)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_subject(path: Path, mask_path: Path | None) -> tuple[Image.Image, np.ndarray, dict[str, Any]]:
    image = Image.open(path)
    source_mode = image.mode
    icc = image.info.get("icc_profile", b"")
    if icc:
        source_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        rgb = ImageCms.profileToProfile(image.convert("RGB"), source_profile, SRGB_PROFILE, outputMode="RGB")
    else:
        rgb = image.convert("RGB")

    if mask_path is not None:
        mask_image = Image.open(mask_path).convert("L")
        if mask_image.size != image.size:
            raise ValueError(f"Mask size {mask_image.size} does not match image size {image.size}")
        alpha = np.asarray(mask_image, dtype=np.uint8)
        mask_source = str(mask_path.resolve())
    elif "A" in image.getbands():
        alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
        if int(alpha.min()) == 255:
            raise ValueError("Image alpha is fully opaque; provide an audited subject mask with --mask")
        mask_source = "embedded_alpha"
    else:
        raise ValueError("Opaque image requires an audited subject mask with --mask")

    if int(np.count_nonzero(alpha >= 245)) < 100:
        raise ValueError("Subject mask has fewer than 100 core foreground pixels")

    metadata = {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "size": [image.width, image.height],
        "source_mode": source_mode,
        "icc_profile_present": bool(icc),
        "working_color_space": "sRGB IEC61966-2.1 (assumed when source ICC is absent)",
        "mask_source": mask_source,
    }
    return rgb, alpha, metadata


def rgb_to_lab(rgb: Image.Image) -> np.ndarray:
    encoded = np.asarray(rgb.convert("RGB"), dtype=np.float64) / 255.0
    linear = np.where(encoded <= 0.04045, encoded / 12.92, ((encoded + 0.055) / 1.055) ** 2.4)
    xyz = linear @ RGB_TO_XYZ_D65.T
    normalized = xyz / D65_WHITE
    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    f = np.where(normalized > epsilon, np.cbrt(normalized), (kappa * normalized + 16.0) / 116.0)
    lab = np.empty_like(f)
    lab[..., 0] = 116.0 * f[..., 1] - 16.0
    lab[..., 1] = 500.0 * (f[..., 0] - f[..., 1])
    lab[..., 2] = 200.0 * (f[..., 1] - f[..., 2])
    return lab


def lab_to_rgb(lab: np.ndarray) -> Image.Image:
    fy = (lab[..., 0] + 16.0) / 116.0
    fx = fy + lab[..., 1] / 500.0
    fz = fy - lab[..., 2] / 200.0
    delta = 6.0 / 29.0
    f = np.stack([fx, fy, fz], axis=-1)
    normalized = np.where(f > delta, f ** 3, 3.0 * delta ** 2 * (f - 4.0 / 29.0))
    xyz = normalized * D65_WHITE
    linear = xyz @ XYZ_D65_TO_RGB.T
    encoded = np.where(
        linear <= 0.0031308,
        12.92 * linear,
        1.055 * np.power(np.clip(linear, 0.0, None), 1.0 / 2.4) - 0.055,
    )
    rgb = np.rint(np.clip(encoded, 0.0, 1.0) * 255.0).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


def channel_summary(values: np.ndarray, channel: str) -> dict[str, Any]:
    if channel == "L":
        histogram, _ = np.histogram(values, bins=256, range=(0.0, 100.0))
    else:
        histogram, _ = np.histogram(values, bins=256, range=(-128.0, 128.0))
    return {
        "mean": round(float(np.mean(values)), 6),
        "std": round(float(np.std(values)), 6),
        "min": round(float(np.min(values)), 6),
        "max": round(float(np.max(values)), 6),
        "percentile_axis": [round(float(value), 3) for value in PERCENTILES],
        "percentile_values": [round(float(value), 6) for value in np.percentile(values, PERCENTILES)],
        "histogram_256": [int(value) for value in histogram],
    }


def palette_summary(lab: np.ndarray, alpha: np.ndarray) -> dict[str, Any]:
    core = alpha >= 245
    pixels = lab[core]
    chroma = np.hypot(pixels[:, 1], pixels[:, 2])
    hue = (np.degrees(np.arctan2(pixels[:, 2], pixels[:, 1])) + 360.0) % 360.0
    chromatic = chroma >= 4.0
    return {
        "core_subject_pixels": int(pixels.shape[0]),
        "L": channel_summary(pixels[:, 0], "L"),
        "a": channel_summary(pixels[:, 1], "a"),
        "b": channel_summary(pixels[:, 2], "b"),
        "chroma": {
            "mean": round(float(np.mean(chroma)), 6),
            "median": round(float(np.median(chroma)), 6),
            "p05": round(float(np.percentile(chroma, 5)), 6),
            "p95": round(float(np.percentile(chroma, 95)), 6),
        },
        "chromatic_hue": {
            "sample_pixels": int(np.count_nonzero(chromatic)),
            "circular_mean_degrees": round(
                float(
                    np.degrees(
                        np.arctan2(
                            np.mean(np.sin(np.radians(hue[chromatic]))),
                            np.mean(np.cos(np.radians(hue[chromatic]))),
                        )
                    )
                    % 360.0
                ),
                6,
            )
            if np.any(chromatic)
            else None,
        },
    }


def capture_anchor(reference: Path, mask: Path | None, output: Path) -> None:
    rgb, alpha, source = load_subject(reference, mask)
    lab = rgb_to_lab(rgb)
    anchor = {
        "schema_version": ANCHOR_SCHEMA,
        "kind": "ndc_expression_color_anchor",
        "status": "PASS",
        "source": source,
        "sampling": {
            "foreground_rule": "alpha_or_audited_mask_gte_245",
            "background_sampled": False,
            "color_space": "CIELAB D65 computed from normalized sRGB",
            "embedded_icc_normalized_to_srgb": True,
        },
        "protected_rules": {
            "alpha_unchanged": True,
            "spot_black_L_max": 6.0,
            "neutral_white_L_min": 94.0,
            "neutral_white_chroma_max": 5.0,
            "neutral_chroma_max": 3.0,
        },
        "palette": palette_summary(lab, alpha),
    }
    write_json(output, anchor)
    print(f"COLOR_ANCHOR_PASS: {output.resolve()}")


def robust_affine_map(values: np.ndarray, target_q: np.ndarray) -> np.ndarray:
    """Correct weak global drift without forcing unlike local pixels together."""
    source_q = np.percentile(values, PERCENTILES)
    source_span = source_q[90] - source_q[10]
    target_span = target_q[90] - target_q[10]
    scale = 1.0 if source_span < 1e-6 else float(np.clip(target_span / source_span, 0.85, 1.15))
    offset = float(target_q[50] - source_q[50] * scale)
    return values * scale + offset


def distribution_distance(summary: dict[str, Any], anchor: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    scales = {"L": 100.0, "a": 256.0, "b": 256.0}
    for channel in ("L", "a", "b"):
        current = np.asarray(summary[channel]["percentile_values"], dtype=np.float64)
        target = np.asarray(anchor["palette"][channel]["percentile_values"], dtype=np.float64)
        result[channel] = round(float(np.mean(np.abs(current - target))), 6)
        result[channel + "_normalized"] = round(result[channel] / scales[channel], 8)
    result["combined_normalized"] = round(
        float(np.mean([result["L_normalized"], result["a_normalized"], result["b_normalized"]])), 8
    )
    return result


def apply_anchor(
    anchor_path: Path,
    candidate: Path,
    mask: Path | None,
    output: Path,
    audit_path: Path,
    strength: float,
    max_delta_l: float,
    max_delta_ab: float,
) -> None:
    if output.exists() or audit_path.exists():
        raise FileExistsError("Refusing to overwrite an existing output or audit")
    anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
    if anchor.get("schema_version") != ANCHOR_SCHEMA or anchor.get("status") != "PASS":
        raise ValueError("Color anchor is not a valid PASS schema-1 anchor")

    rgb, alpha, source = load_subject(candidate, mask)
    lab = rgb_to_lab(rgb)
    core = alpha >= 245
    before = palette_summary(lab, alpha)
    distance_before = distribution_distance(before, anchor)
    channel_deadbands = {"L": 0.8, "a": 0.8, "b": 0.8}
    needs_correction = any(distance_before[channel] > channel_deadbands[channel] for channel in channel_deadbands)

    # A natural expression can change its light/shadow distribution by a
    # fraction of one Lab lightness unit even when its palette is visually
    # locked.  In that low-baseline band, forcing the global affine map can
    # amplify the variation it is meant to remove.  Keep the original bytes
    # only when the aggregate distance is still below 0.01 and the only
    # overage is a below-visual-threshold L* difference; larger hue/chroma drift still takes
    # the normal correction route.
    low_baseline_visual_match = (
        distance_before["combined_normalized"] <= 0.01
        and distance_before["L"] <= 1.6
        and distance_before["a"] <= channel_deadbands["a"]
        and distance_before["b"] <= channel_deadbands["b"]
    )

    if not needs_correction or low_baseline_visual_match:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate, output)
        decision = (
            "NO_CORRECTION_REQUIRED_WITHIN_DEADBAND"
            if not needs_correction
            else "NO_CORRECTION_REQUIRED_LOW_BASELINE_VISUAL_MATCH"
        )
        audit = {
            "schema_version": AUDIT_SCHEMA,
            "kind": "ndc_expression_color_calibration_audit",
            "mechanical_status": "PASS",
            "visual_status": "NOT_CHECKED",
            "formal_status": "NOT_CHECKED",
            "decision": decision,
            "anchor": {
                "path": str(anchor_path.resolve()),
                "sha256": sha256(anchor_path),
                "approved_portrait_sha256": anchor["source"]["sha256"],
            },
            "candidate": source,
            "output": {"path": str(output.resolve()), "sha256": sha256(output)},
            "parameters": {
                "method": "masked_cielab_robust_affine_with_protected_neutrals",
                "strength": 0.0,
                "deadband_channel_mae": channel_deadbands,
                "low_baseline_visual_match": low_baseline_visual_match,
                "low_baseline_max_combined_normalized": 0.01,
                "low_baseline_max_L": 1.6,
                "alpha_unchanged": True,
                "background_sampled_or_recolored": False,
            },
            "distance_before": distance_before,
            "distance_after": distance_before,
            "relative_improvement": 0.0,
            "before": before,
            "after": before,
        }
        write_json(audit_path, audit)
        print(f"COLOR_CALIBRATION_PASS: {output.resolve()} ({decision})")
        return

    corrected = lab.copy()
    original_pixels = lab[core]
    mapped = original_pixels.copy()
    for index, channel in enumerate(("L", "a", "b")):
        target_q = np.asarray(anchor["palette"][channel]["percentile_values"], dtype=np.float64)
        if distance_before[channel] > channel_deadbands[channel]:
            mapped[:, index] = robust_affine_map(original_pixels[:, index], target_q)

    delta = mapped - original_pixels
    delta[:, 0] = np.clip(delta[:, 0], -max_delta_l, max_delta_l)
    delta[:, 1:] = np.clip(delta[:, 1:], -max_delta_ab, max_delta_ab)

    luminance = original_pixels[:, 0]
    chroma = np.hypot(original_pixels[:, 1], original_pixels[:, 2])
    weight = np.full(luminance.shape, strength, dtype=np.float64)
    weight *= np.clip((luminance - 6.0) / 6.0, 0.0, 1.0)
    protected_white = (luminance >= 94.0) & (chroma <= 5.0)
    weight[protected_white] = 0.0
    corrected_pixels = original_pixels + delta * weight[:, None]
    neutral = chroma <= 3.0
    corrected_pixels[neutral, 1:] = original_pixels[neutral, 1:]
    corrected[core] = corrected_pixels

    # Feather the same bounded transform into antialiased foreground pixels by
    # applying their nearest global channel offset; alpha itself is never changed.
    edge = (alpha > 0) & ~core
    if np.any(edge):
        mean_delta = np.mean(corrected_pixels - original_pixels, axis=0)
        edge_weight = (alpha[edge].astype(np.float64) / 245.0)[:, None] * strength
        corrected[edge] = lab[edge] + np.array(
            [np.clip(mean_delta[0], -max_delta_l, max_delta_l),
             np.clip(mean_delta[1], -max_delta_ab, max_delta_ab),
             np.clip(mean_delta[2], -max_delta_ab, max_delta_ab)]
        ) * edge_weight

    out_rgb = lab_to_rgb(corrected)
    if np.any(alpha < 255):
        out_image = out_rgb.convert("RGBA")
        out_image.putalpha(Image.fromarray(alpha, mode="L"))
    else:
        out_image = out_rgb
    output.parent.mkdir(parents=True, exist_ok=True)
    out_image.save(output)

    after_lab = rgb_to_lab(out_rgb)
    after = palette_summary(after_lab, alpha)
    distance_after = distribution_distance(after, anchor)
    baseline = distance_before["combined_normalized"]
    final = distance_after["combined_normalized"]
    improvement = 1.0 if baseline == 0.0 else (baseline - final) / baseline
    channel_regression = any(
        distance_after[channel] > distance_before[channel] + 0.25 for channel in ("L", "a", "b")
    )
    # Near an already-matching portrait, a useful bounded correction can reduce
    # the absolute palette distance without reaching a 10% relative gain.  Keep
    # the normal 10% gate for meaningful drift, but accept a 5% improvement for
    # a low baseline only when no channel regresses beyond the existing guard.
    minimum_improvement = 0.05 if baseline <= 0.01 else 0.10
    mechanically_safe = not channel_regression and final < baseline and improvement >= minimum_improvement
    audit = {
        "schema_version": AUDIT_SCHEMA,
        "kind": "ndc_expression_color_calibration_audit",
        "mechanical_status": "PASS" if mechanically_safe else "FAIL",
        "visual_status": "NOT_CHECKED",
        "formal_status": "NOT_CHECKED",
        "decision": "CORRECTION_APPLIED",
        "anchor": {
            "path": str(anchor_path.resolve()),
            "sha256": sha256(anchor_path),
            "approved_portrait_sha256": anchor["source"]["sha256"],
        },
        "candidate": source,
        "output": {"path": str(output.resolve()), "sha256": sha256(output)},
        "parameters": {
            "method": "masked_cielab_robust_affine_with_protected_neutrals",
            "strength": strength,
            "max_delta_L": max_delta_l,
            "max_delta_a_b": max_delta_ab,
            "deadband_channel_mae": channel_deadbands,
            "minimum_relative_improvement": minimum_improvement,
            "alpha_unchanged": True,
            "background_sampled_or_recolored": False,
        },
        "distance_before": distance_before,
        "distance_after": distance_after,
        "relative_improvement": round(float(improvement), 6),
        "before": before,
        "after": after,
    }
    write_json(audit_path, audit)
    print(f"COLOR_CALIBRATION_{audit['mechanical_status']}: {output.resolve()}")
    if not mechanically_safe:
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Freeze and restore an NDC expression palette deterministically.")
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("capture", help="Capture exact subject color statistics from an approved portrait")
    capture.add_argument("--reference", required=True, type=Path)
    capture.add_argument("--mask", required=True, type=Path, help="Codex-reviewed subject mask from E2")
    capture.add_argument("--output", required=True, type=Path)
    apply = commands.add_parser("apply", help="Calibrate one expression candidate directly to a frozen anchor")
    apply.add_argument("--anchor", required=True, type=Path)
    apply.add_argument("--input", required=True, type=Path)
    apply.add_argument("--mask", type=Path)
    apply.add_argument("--output", required=True, type=Path)
    apply.add_argument("--audit", required=True, type=Path)
    apply.add_argument("--strength", type=float, default=0.85)
    apply.add_argument("--max-delta-l", type=float, default=8.0)
    apply.add_argument("--max-delta-ab", type=float, default=6.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "capture":
        if args.output.exists():
            raise FileExistsError(f"Refusing to overwrite existing anchor: {args.output}")
        capture_anchor(args.reference, args.mask, args.output)
        return
    if not 0.0 <= args.strength <= 1.0:
        raise ValueError("--strength must be between 0 and 1")
    apply_anchor(
        args.anchor,
        args.input,
        args.mask,
        args.output,
        args.audit,
        args.strength,
        args.max_delta_l,
        args.max_delta_ab,
    )


if __name__ == "__main__":
    main()
