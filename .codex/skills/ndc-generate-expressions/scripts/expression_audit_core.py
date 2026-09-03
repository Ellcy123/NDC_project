#!/usr/bin/env python3
"""Shared mechanical-audit helpers for NDC expression assets.

The measurements in this module are screening evidence, not an artistic approval.
Formal delivery remains fail-closed until the receipt validator sees the required
human review gates.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


GREEN = (0, 255, 43)
MASK_THRESHOLD = 5
ALPHA_THRESHOLD = 8
AUDIT_REVISION = 5


PROFILE_SPECS: dict[str, dict[str, Any]] = {
    "greenscreen": {
        "size": (1536, 1024),
        "mode": "RGB",
        "background": "#00FF2B",
        "hard_max": {
            "coverage_pct": 44.420815,
            "bbox_width_pct": 87.890625,
            "bbox_height_pct": 97.949219,
            "bbox_area_pct": 84.378306,
        },
        "default_range": {
            "coverage_pct": (31.767565, 39.055901),
            "bbox_width_pct": (57.369792, 85.494792),
            "bbox_height_pct": (93.925781, 97.421875),
            "top_margin_pct": (2.578125, 6.074219),
            "centroid_x_pct": (47.679247, 50.969388),
        },
        "head_range": {
            "head_bbox_width_pct": (29.922, 40.762),
            "head_bbox_height_pct": (52.158, 66.055),
            "head_bbox_area_pct": (16.015, 27.227),
            "head_actual_coverage_pct": (12.808, 19.208),
            "head_share_subject_pct": (33.433, 53.499),
            "head_subject_bbox_area_pct": (24.887, 42.810),
            "head_center_x_pct": (49.349, 50.889),
            "head_center_y_pct": (29.434, 36.738),
        },
    },
    "transparent": {
        "size": (1164, 916),
        "legacy_size": (1152, 900),
        "mode": "RGBA",
        "background": "alpha_0",
        "hard_max": {
            "coverage_pct": 44.682637,
            "bbox_width_pct": 99.913194,
            "bbox_height_pct": 100.0,
            "bbox_area_pct": 92.364198,
        },
        "default_range": {
            "coverage_pct": (34.0, 44.0),
            "bbox_width_pct": (74.0, 95.0),
            "bbox_height_pct": (88.0, 98.0),
            "top_margin_pct": (2.0, 12.0),
            "centroid_x_pct": (48.5, 50.2),
        },
        "head_range": {
            "head_bbox_width_pct": (35.111, 49.809),
            "head_bbox_height_pct": (57.730, 64.056),
            "head_bbox_area_pct": (20.413, 31.515),
            "head_actual_coverage_pct": (14.700, 22.722),
            "head_share_subject_pct": (39.765, 60.976),
            "head_subject_bbox_area_pct": (25.421, 43.940),
            "head_center_x_pct": (48.501, 50.217),
            "head_center_y_pct": (34.050, 41.439),
        },
    },
}


HEAD_TOLERANCE_PP = {
    "head_bbox_width_pct": 2.0,
    "head_bbox_height_pct": 3.0,
    "head_center_x_pct": 1.5,
    "head_center_y_pct": 2.0,
    "head_actual_coverage_pct": 1.5,
}

# Narrative performances may include the user-approved small coordinated
# posture/head adjustment while retaining the portrait's camera viewpoint.
# Micro expressions and basic emotions keep the strict lock above.
HEAD_TOLERANCE_PP_BY_STATE = {
    "basic_emotion": HEAD_TOLERANCE_PP,
    "micro_expression": HEAD_TOLERANCE_PP,
    "narrative_state": {
        "head_bbox_width_pct": 2.5,
        "head_bbox_height_pct": 5.0,
        "head_center_x_pct": 2.0,
        "head_center_y_pct": 2.5,
        "head_actual_coverage_pct": 2.5,
    },
    "action_state": HEAD_TOLERANCE_PP,
}


SET_SD_LIMITS_PP = {
    "coverage_pct": 1.0,
    "bbox_width_pct": 1.0,
    "bbox_height_pct": 1.5,
}


SET_SD_LIMITS_PERFORMANCE_PP = {
    "coverage_pct": 1.5,
    "bbox_width_pct": 2.0,
    "bbox_height_pct": 1.5,
}


@dataclass(frozen=True)
class AuditMessage:
    gate: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"gate": self.gate, "status": self.status, "detail": self.detail}


def round_floats(value: Any, digits: int = 6) -> Any:
    if isinstance(value, dict):
        return {key: round_floats(item, digits) for key, item in value.items()}
    if isinstance(value, list):
        return [round_floats(item, digits) for item in value]
    if isinstance(value, tuple):
        return [round_floats(item, digits) for item in value]
    if isinstance(value, (float, np.floating)):
        if not math.isfinite(float(value)):
            return None
        return round(float(value), digits)
    if isinstance(value, np.integer):
        return int(value)
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(round_floats(data), handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def expected_size(profile: str, legacy_transparent: bool = False) -> tuple[int, int]:
    if profile not in PROFILE_SPECS:
        raise ValueError(f"Unknown profile: {profile}")
    if profile == "transparent" and legacy_transparent:
        return tuple(PROFILE_SPECS[profile]["legacy_size"])
    return tuple(PROFILE_SPECS[profile]["size"])


def subject_mask(image: Image.Image, profile: str) -> np.ndarray:
    if profile == "transparent":
        rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
        return rgba[:, :, 3] > ALPHA_THRESHOLD
    rgb = np.asarray(image.convert("RGB"), dtype=np.int16)
    green = np.asarray(GREEN, dtype=np.int16)
    return np.max(np.abs(rgb - green), axis=2) > MASK_THRESHOLD


def bottom_continuity_metrics(mask: np.ndarray) -> dict[str, Any]:
    """Screen whether a bust is a solid lower-torso continuation.

    This is deliberately stricter than a one-pixel bottom-contact check.  It
    detects floating oval cutouts and internal transparent wedges, but remains
    screening evidence: semantic anatomy still needs visual approval.
    """
    height, width = mask.shape
    depth = max(8, int(round(height * 0.02)))
    band = mask[-depth:]
    spans: list[int] = []
    holes: list[int] = []
    for row in band:
        xs = np.flatnonzero(row)
        if xs.size == 0:
            spans.append(0)
            holes.append(0)
            continue
        hull = int(xs[-1] - xs[0] + 1)
        spans.append(int(xs.size))
        holes.append(hull - int(xs.size))
    center_left = int(round(width * 0.45))
    center_right = max(center_left + 1, int(round(width * 0.55)))
    center_occupancy = float(band[:, center_left:center_right].mean()) if band.size else 0.0
    bottom_span = spans[-1] if spans else 0
    max_holes = max(holes, default=0)
    allowed_holes = max(2, int(round(width * 0.005)))
    clear = (
        bool(mask[-1].any())
        and 100.0 * bottom_span / width >= 35.0
        and 100.0 * min(spans, default=0) / width >= 30.0
        and max_holes <= allowed_holes
        and center_occupancy >= 0.95
    )
    return {
        "screening_status": "CLEAR" if clear else "SUSPICIOUS",
        "bottom_band_depth_px": depth,
        "touches_bottom": bool(mask[-1].any()),
        "bottom_row_foreground_span_px": bottom_span,
        "bottom_row_foreground_span_pct": 100.0 * bottom_span / width,
        "minimum_band_foreground_span_px": min(spans, default=0),
        "minimum_band_foreground_span_pct": 100.0 * min(spans, default=0) / width,
        "maximum_internal_hole_px": max_holes,
        "allowed_internal_hole_px": allowed_holes,
        "center_band_occupancy_pct": 100.0 * center_occupancy,
    }


def _bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.nonzero(mask)
    if xs.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def mask_metrics(mask: np.ndarray) -> dict[str, Any]:
    height, width = mask.shape
    bbox = _bbox(mask)
    if bbox is None:
        return {
            "pixel_count": 0,
            "coverage_pct": 0.0,
            "bbox": None,
            "bbox_width_pct": 0.0,
            "bbox_height_pct": 0.0,
            "bbox_area_pct": 0.0,
            "left_margin_pct": 100.0,
            "right_margin_pct": 100.0,
            "top_margin_pct": 100.0,
            "bottom_margin_pct": 100.0,
            "centroid_x_pct": None,
            "centroid_y_pct": None,
            "touches": {"left": False, "right": False, "top": False, "bottom": False},
        }
    left, top, right, bottom = bbox
    ys, xs = np.nonzero(mask)
    bbox_width = right - left
    bbox_height = bottom - top
    return {
        "pixel_count": int(mask.sum()),
        "coverage_pct": 100.0 * float(mask.mean()),
        "bbox": [left, top, right, bottom],
        "bbox_width_pct": 100.0 * bbox_width / width,
        "bbox_height_pct": 100.0 * bbox_height / height,
        "bbox_area_pct": 100.0 * bbox_width * bbox_height / (width * height),
        "left_margin_pct": 100.0 * left / width,
        "right_margin_pct": 100.0 * (width - right) / width,
        "top_margin_pct": 100.0 * top / height,
        "bottom_margin_pct": 100.0 * (height - bottom) / height,
        "centroid_x_pct": 100.0 * (float(xs.mean()) + 0.5) / width,
        "centroid_y_pct": 100.0 * (float(ys.mean()) + 0.5) / height,
        "touches": {
            "left": bool(left == 0),
            "right": bool(right == width),
            "top": bool(top == 0),
            "bottom": bool(bottom == height),
        },
    }


def parse_box(value: str | None) -> list[int] | None:
    if value is None:
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("Head box must be x1,y1,x2,y2")
    box = [int(part) for part in parts]
    if box[0] >= box[2] or box[1] >= box[3] or min(box) < 0:
        raise ValueError("Head box must satisfy 0 <= x1 < x2 and 0 <= y1 < y2")
    return box


def _smooth(values: np.ndarray, radius: int) -> np.ndarray:
    radius = max(1, radius)
    padded = np.pad(values.astype(float), (radius, radius), mode="edge")
    kernel = np.ones(radius * 2 + 1, dtype=float) / (radius * 2 + 1)
    return np.convolve(padded, kernel, mode="valid")


def estimate_head_box(mask: np.ndarray) -> tuple[list[int] | None, float, str]:
    """Estimate a head box from upper-body silhouette; deliberately conservative.

    Hats, profile views, hands near the face, telephones, cigarettes, or elaborate
    hair can invalidate this heuristic. Low confidence forces manual review.
    """

    bbox = _bbox(mask)
    if bbox is None:
        return None, 0.0, "empty subject mask"
    left, top, right, bottom = bbox
    subject_height = bottom - top
    subject_width = right - left
    if subject_height < 16 or subject_width < 16:
        return None, 0.0, "subject too small"

    widths = np.zeros(subject_height, dtype=float)
    for local_y, y in enumerate(range(top, bottom)):
        xs = np.where(mask[y])[0]
        if xs.size:
            widths[local_y] = xs.max() - xs.min() + 1
    smooth = _smooth(widths, max(2, round(subject_height * 0.012)))
    start = round(subject_height * 0.42)
    stop = round(subject_height * 0.78)
    lookback = max(5, round(subject_height * 0.05))
    future_start = max(6, round(subject_height * 0.06))
    future_stop = max(future_start + 6, round(subject_height * 0.20))
    candidates: list[tuple[float, int, float]] = []
    for index in range(start, min(stop, subject_height - future_stop - 1)):
        current = float(np.median(smooth[max(0, index - lookback) : index + 1]))
        future = float(np.percentile(smooth[index + future_start : index + future_stop], 80))
        if current <= 0:
            continue
        gain = future / current
        depth = (smooth[max(0, index - lookback)] - smooth[index]) / mask.shape[1]
        q = index / subject_height
        centrality = 1.0 - abs(q - 0.61) * 0.35
        score = gain * centrality + max(0.0, depth) * 0.5
        candidates.append((score, index, gain))
    if candidates:
        _, neck_local, gain = max(candidates)
    else:
        neck_local, gain = round(subject_height * 0.62), 1.0

    cut_y = min(bottom, top + neck_local + 1)
    upper = mask[top:cut_y, :]
    upper_bbox = _bbox(upper)
    if upper_bbox is None:
        return None, 0.0, "empty estimated head region"
    h_left, _, h_right, _ = upper_bbox
    h_bottom = cut_y
    head_box = [max(0, h_left), top, min(mask.shape[1], h_right), h_bottom]

    head_height_ratio = (h_bottom - top) / subject_height
    head_width_ratio = (head_box[2] - head_box[0]) / subject_width
    plausibility = 1.0
    if not 0.30 <= head_height_ratio <= 0.68:
        plausibility *= 0.35
    if not 0.28 <= head_width_ratio <= 0.80:
        plausibility *= 0.45
    confidence = max(0.0, min(1.0, (gain - 1.05) / 0.85)) * plausibility
    return head_box, confidence, "automatic silhouette estimate"


def head_metrics(mask: np.ndarray, box: list[int]) -> dict[str, Any]:
    height, width = mask.shape
    x1, y1, x2, y2 = box
    if x2 > width or y2 > height:
        raise ValueError(f"Head box {box} exceeds image {width}x{height}")
    region = mask[y1:y2, x1:x2]
    subject_pixels = int(mask.sum())
    actual_pixels = int(region.sum())
    subject_bbox = _bbox(mask)
    subject_bbox_area = 0
    if subject_bbox:
        subject_bbox_area = (subject_bbox[2] - subject_bbox[0]) * (subject_bbox[3] - subject_bbox[1])
    box_area = max(1, (x2 - x1) * (y2 - y1))
    return {
        "head_bbox": box,
        "head_bbox_width_pct": 100.0 * (x2 - x1) / width,
        "head_bbox_height_pct": 100.0 * (y2 - y1) / height,
        "head_bbox_area_pct": 100.0 * box_area / (width * height),
        "head_actual_coverage_pct": 100.0 * actual_pixels / (width * height),
        "head_share_subject_pct": 100.0 * actual_pixels / max(1, subject_pixels),
        "head_subject_bbox_area_pct": 100.0 * box_area / max(1, subject_bbox_area),
        "head_center_x_pct": 100.0 * ((x1 + x2) / 2.0) / width,
        "head_center_y_pct": 100.0 * ((y1 + y2) / 2.0) / height,
    }


def _range_messages(values: dict[str, Any], ranges: dict[str, tuple[float, float]], prefix: str) -> list[AuditMessage]:
    messages: list[AuditMessage] = []
    for key, (minimum, maximum) in ranges.items():
        value = values.get(key)
        if value is None:
            continue
        status = "PASS" if minimum <= value <= maximum else "WARN"
        messages.append(
            AuditMessage(
                f"{prefix}.{key}",
                status,
                f"{value:.6f}; reference range {minimum:.6f}..{maximum:.6f}",
            )
        )
    return messages


def _transparent_edge_metrics(image: Image.Image) -> dict[str, float]:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    alpha = rgba[:, :, 3]
    soft = (alpha > 0) & (alpha < 255)
    if not np.any(soft):
        return {"soft_edge_pixel_pct": 0.0, "green_biased_soft_edge_pct": 0.0}
    rgb = rgba[:, :, :3].astype(np.int16)
    green_biased = soft & (rgb[:, :, 1] > rgb[:, :, 0] + 20) & (rgb[:, :, 1] > rgb[:, :, 2] + 20)
    return {
        "soft_edge_pixel_pct": 100.0 * float(soft.mean()),
        "green_biased_soft_edge_pct": 100.0 * float(green_biased.mean()),
    }


def analyze_image(
    path: Path,
    profile: str,
    *,
    legacy_transparent: bool = False,
    manual_head_box: list[int] | None = None,
) -> tuple[dict[str, Any], np.ndarray]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".png":
        raise ValueError(f"Expression asset must be PNG: {path}")
    spec = PROFILE_SPECS[profile]
    with Image.open(path) as opened:
        image = opened.copy()
        original_mode = opened.mode
    width, height = image.size
    mask = subject_mask(image, profile)
    geometry = mask_metrics(mask)
    messages: list[AuditMessage] = []

    wanted_size = expected_size(profile, legacy_transparent)
    messages.append(
        AuditMessage(
            "profile.canvas",
            "PASS" if image.size == wanted_size else "FAIL",
            f"actual {width}x{height}; required {wanted_size[0]}x{wanted_size[1]}",
        )
    )
    messages.append(
        AuditMessage(
            "profile.mode",
            "PASS" if original_mode == spec["mode"] else "FAIL",
            f"actual {original_mode}; required {spec['mode']}",
        )
    )
    messages.append(
        AuditMessage(
            "subject.nonempty",
            "PASS" if geometry["pixel_count"] > 0 else "FAIL",
            f"subject pixels {geometry['pixel_count']}",
        )
    )
    messages.append(
        AuditMessage(
            "subject.bottom_contact",
            "PASS" if geometry["touches"]["bottom"] else "WARN",
            "Bust delivery normally reaches the bottom edge; WARN requires visual confirmation.",
        )
    )

    for key, maximum in spec["hard_max"].items():
        actual = geometry[key]
        messages.append(
            AuditMessage(
                f"historical_hard_max.{key}",
                "PASS" if actual <= maximum + 1e-9 else "FAIL",
                f"{actual:.6f}; maximum {maximum:.6f}",
            )
        )
    messages.extend(_range_messages(geometry, spec["default_range"], "default_reference"))

    background_metrics: dict[str, Any] = {}
    if profile == "greenscreen":
        rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
        corners = [rgb[0, 0], rgb[0, -1], rgb[-1, 0], rgb[-1, -1]]
        exact_corners = sum(bool(np.array_equal(corner, np.asarray(GREEN, dtype=np.uint8))) for corner in corners)
        # The subject mask intentionally ignores pixels within MASK_THRESHOLD of
        # green. Those pixels include the antialiased transition immediately
        # outside the silhouette and must not be misclassified as dirty remote
        # background. Exclude a two-pixel subject fringe from uniformity only;
        # keep the original mask for every geometry measurement.
        expanded_subject = np.asarray(
            Image.fromarray((mask.astype(np.uint8) * 255), mode="L").filter(ImageFilter.MaxFilter(5)),
            dtype=np.uint8,
        ) > 0
        screened_background = ~expanded_subject
        bg_exact = np.all(rgb == np.asarray(GREEN, dtype=np.uint8), axis=2) & screened_background
        background_metrics = {
            "required_rgb": list(GREEN),
            "exact_green_corners": exact_corners,
            "uniformity_subject_fringe_exclusion_px": 2,
            "background_exact_green_pct": 100.0 * float(bg_exact.sum()) / max(1, int(screened_background.sum())),
        }
        messages.append(
            AuditMessage(
                "profile.green_corners",
                "PASS" if exact_corners == 4 else "FAIL",
                f"{exact_corners}/4 corners are exact #00FF2B",
            )
        )
        exact_background = background_metrics["background_exact_green_pct"]
        messages.append(
            AuditMessage(
                "profile.green_background_uniformity",
                "PASS" if exact_background >= 99.8 else "FAIL",
                f"{exact_background:.6f}% of screened background is exact #00FF2B; minimum 99.8% allows only the narrow anti-aliased subject fringe",
            )
        )
    else:
        rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
        alpha = rgba[:, :, 3]
        transparent_pixels = int((alpha == 0).sum())
        background_metrics = {
            "alpha_zero_pct": 100.0 * transparent_pixels / alpha.size,
            **_transparent_edge_metrics(image),
        }
        messages.append(
            AuditMessage(
                "profile.alpha_background",
                "PASS" if transparent_pixels > 0 else "FAIL",
                f"alpha-zero pixels {transparent_pixels}",
            )
        )
        green_edge = background_metrics["green_biased_soft_edge_pct"]
        messages.append(
            AuditMessage(
                "profile.green_spill_screen",
                "PASS" if green_edge <= 0.1 else "WARN",
                f"green-biased soft-edge pixels {green_edge:.6f}% of canvas; visual review remains required",
            )
        )

    head_box_source = "manual"
    head_confidence = 1.0
    head_note = "manual head box"
    box = manual_head_box
    if box is None:
        head_box_source = "automatic"
        box, head_confidence, head_note = estimate_head_box(mask)
    measured_head: dict[str, Any] | None = None
    manual_review_required = False
    if box is not None:
        measured_head = head_metrics(mask, box)
        messages.extend(_range_messages(measured_head, spec["head_range"], "head_reference"))
    if box is None or (head_box_source == "automatic" and head_confidence < 0.35):
        manual_review_required = True
        messages.append(
            AuditMessage(
                "head.manual_review",
                "NOT_CHECKED",
                f"automatic head estimate confidence {head_confidence:.3f}; supply --manual-head-box",
            )
        )
    else:
        messages.append(
            AuditMessage(
                "head.manual_review",
                "PASS" if head_box_source == "manual" else "WARN",
                f"{head_box_source} head box; confidence {head_confidence:.3f}. Hats, profile views, face-adjacent hands, and props still require manual review.",
            )
        )

    statuses = [item.status for item in messages]
    if "FAIL" in statuses:
        mechanical_status = "FAIL"
    elif manual_review_required or "NOT_CHECKED" in statuses:
        mechanical_status = "NOT_CHECKED"
    else:
        mechanical_status = "PASS"

    report = {
        "schema_version": 1,
        "audit_revision": AUDIT_REVISION,
        "asset": str(path),
        "sha256": sha256(path),
        "profile": profile,
        "legacy_transparent": bool(legacy_transparent),
        "profile_spec": {
            "canvas": list(wanted_size),
            "mode": spec["mode"],
            "background": spec["background"],
        },
        "image": {"width": width, "height": height, "mode": original_mode},
        "subject": geometry,
        "background": background_metrics,
        "head": measured_head,
        "head_box_source": head_box_source,
        "head_detection_confidence": head_confidence,
        "head_detection_note": head_note,
        "manual_head_review_required": manual_review_required,
        "checks": [item.as_dict() for item in messages],
        "mechanical_status": mechanical_status,
        "formal_status": "NOT_CHECKED",
        "formal_status_note": "Mechanical screening cannot approve identity, expression semantics, style, or edge quality.",
    }
    return round_floats(report), mask


def compare_to_anchor(
    candidate: dict[str, Any],
    anchor: dict[str, Any],
    *,
    state_class: str,
    pose_exception: bool,
) -> dict[str, Any]:
    checks: list[AuditMessage] = []
    if candidate["profile"] != anchor["profile"]:
        checks.append(AuditMessage("anchor.profile", "FAIL", "Candidate and anchor profiles differ."))
    else:
        checks.append(AuditMessage("anchor.profile", "PASS", candidate["profile"]))
    if candidate["profile_spec"]["canvas"] != anchor["profile_spec"]["canvas"]:
        checks.append(AuditMessage("anchor.canvas", "FAIL", "Candidate and anchor canvas sizes differ."))
    else:
        checks.append(AuditMessage("anchor.canvas", "PASS", str(candidate["profile_spec"]["canvas"])))

    candidate_head = candidate.get("head")
    anchor_head = anchor.get("head")
    if not candidate_head or not anchor_head:
        checks.append(AuditMessage("anchor.head_lock", "NOT_CHECKED", "Candidate or anchor head metrics are unavailable."))
    else:
        head_tolerance = HEAD_TOLERANCE_PP_BY_STATE.get(state_class, HEAD_TOLERANCE_PP)
        for key, tolerance in head_tolerance.items():
            delta = float(candidate_head[key]) - float(anchor_head[key])
            if pose_exception and state_class == "action_state":
                status = "WARN"
                detail = f"delta {delta:+.6f} pp; action-state exception requires recorded manual approval"
            else:
                status = "PASS" if abs(delta) <= tolerance + 1e-9 else "FAIL"
                detail = f"delta {delta:+.6f} pp; tolerance +/-{tolerance:.6f} pp"
            checks.append(AuditMessage(f"anchor.{key}", status, detail))

    body_deltas = {
        key: float(candidate["subject"][key]) - float(anchor["subject"][key])
        for key in ("coverage_pct", "bbox_width_pct", "bbox_height_pct", "centroid_x_pct", "centroid_y_pct")
        if candidate["subject"].get(key) is not None and anchor["subject"].get(key) is not None
    }
    statuses = [item.status for item in checks]
    if "FAIL" in statuses:
        status = "FAIL"
    elif "NOT_CHECKED" in statuses:
        status = "NOT_CHECKED"
    else:
        status = "PASS"
    return round_floats(
        {
            "anchor_asset": anchor["asset"],
            "state_class": state_class,
            "pose_exception": bool(pose_exception),
            "head_tolerance_pp": head_tolerance if candidate_head and anchor_head else HEAD_TOLERANCE_PP_BY_STATE.get(state_class, HEAD_TOLERANCE_PP),
            "body_deltas_pp": body_deltas,
            "checks": [item.as_dict() for item in checks],
            "status": status,
        }
    )


def save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((mask.astype(np.uint8) * 255), mode="L").save(path)


def _font(size: int = 18) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def composite_for_review(image: Image.Image, profile: str, background: tuple[int, int, int] = (228, 228, 228)) -> Image.Image:
    if profile == "transparent":
        base = Image.new("RGBA", image.size, (*background, 255))
        return Image.alpha_composite(base, image.convert("RGBA")).convert("RGB")
    return image.convert("RGB")


def save_overlay(image_path: Path, report: dict[str, Any], path: Path) -> None:
    with Image.open(image_path) as opened:
        review = composite_for_review(opened.copy(), report["profile"])
    draw = ImageDraw.Draw(review)
    bbox = report["subject"].get("bbox")
    if bbox:
        draw.rectangle(bbox, outline=(255, 40, 40), width=max(2, review.width // 500))
    head = report.get("head")
    if head and head.get("head_bbox"):
        draw.rectangle(head["head_bbox"], outline=(40, 120, 255), width=max(2, review.width // 500))
    label = f"{report['profile']} | mechanical {report['mechanical_status']} | head {report['head_box_source']}"
    font = _font(max(14, review.width // 70))
    box = draw.textbbox((0, 0), label, font=font)
    pad = max(6, review.width // 200)
    draw.rectangle((0, 0, box[2] + pad * 2, box[3] + pad * 2), fill=(255, 255, 255))
    draw.text((pad, pad), label, fill=(15, 15, 15), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    review.save(path)


def save_transparent_previews(image_path: Path, output_dir: Path) -> list[str]:
    with Image.open(image_path) as opened:
        image = opened.convert("RGBA")
    results: list[str] = []
    for name, color in (("on_light_gray.png", (225, 225, 225)), ("on_dark_gray.png", (45, 45, 45))):
        base = Image.new("RGBA", image.size, (*color, 255))
        out = Image.alpha_composite(base, image).convert("RGB")
        destination = output_dir / name
        out.save(destination)
        results.append(str(destination.resolve()))
    return results


def aggregate_status(statuses: Iterable[str]) -> str:
    values = list(statuses)
    if "FAIL" in values:
        return "FAIL"
    if "NOT_CHECKED" in values:
        return "NOT_CHECKED"
    if "BLOCKED" in values:
        return "BLOCKED"
    return "PASS"
