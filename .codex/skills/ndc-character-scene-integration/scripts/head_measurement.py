"""Measure anatomical crown-to-chin length without confusing in-plane rotation with scale."""
from __future__ import annotations
import math

def anatomical_head_height(pose: dict, head_box=None) -> float:
    box = pose["headBox"] if head_box is None else head_box
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        raise ValueError("headBox must contain four coordinates.")
    box = tuple(float(v) for v in box)
    if not all(math.isfinite(v) for v in box) or box[2] <= box[0] or box[3] <= box[1]:
        raise ValueError("headBox must be finite and positive.")
    axis = pose.get("headAxis")
    if axis is None:
        return box[3] - box[1]
    if not isinstance(axis, dict):
        raise ValueError("headAxis must be an object.")
    for field in ("measurementEvidence", "projectionReview"):
        if not isinstance(axis.get(field), str) or not axis[field].strip():
            raise ValueError(f"headAxis.{field} requires a reviewed explanation.")
    points = []
    for name in ("crown", "chin"):
        raw = axis.get(name)
        if not isinstance(raw, (list, tuple)) or len(raw) != 2:
            raise ValueError(f"headAxis.{name} must be an image-space point.")
        point = tuple(float(v) for v in raw)
        if not all(math.isfinite(v) for v in point):
            raise ValueError(f"headAxis.{name} must be finite.")
        if not (box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]):
            raise ValueError(f"headAxis.{name} is outside the anatomical headBox.")
        points.append(point)
    length = math.dist(*points)
    if length <= 0:
        raise ValueError("headAxis crown and chin must be distinct.")
    return length

