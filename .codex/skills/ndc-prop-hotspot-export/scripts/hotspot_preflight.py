#!/usr/bin/env python3
"""Validate semantic target annotations before Photoshop path work starts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "ndc-prop-hotspot-annotation/v1"
REGIONS = {"BODY", "PROP_SHADOW", "KEEP_CARRIER", "EXCLUDE_FOREGROUND"}
EXTREMA = {"top", "bottom", "left", "right"}
DIRECT_INPUTS = {"original_scene", "carrier_without_prop", "pickup_layer", "scene_before_pickup"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def check_binding(binding: object, base: Path, label: str, failures: list[str]) -> None:
    if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
        failures.append(f"{label}: path and sha256 are required")
        return
    path = resolve(base, binding["path"])
    if not path.is_file():
        failures.append(f"{label}: file is missing")
    elif sha256(path).lower() != str(binding["sha256"]).lower():
        failures.append(f"{label}: hash mismatch")


def validate(path: Path) -> list[str]:
    path = path.resolve()
    data = read_json(path)
    failures: list[str] = []
    if data.get("schema") != SCHEMA:
        failures.append("unsupported annotation schema")
    parent = data.get("parent", {})
    check_binding(parent, path.parent, "parent", failures)
    width, height = parent.get("width"), parent.get("height")
    if type(width) is not int or width <= 0 or type(height) is not int or height <= 0:
        failures.append("parent width and height must be positive integers")
        width = height = 0
    regions = data.get("regions")
    if not isinstance(regions, dict) or set(regions) != REGIONS:
        failures.append("regions must define BODY, PROP_SHADOW, KEEP_CARRIER and EXCLUDE_FOREGROUND")
    else:
        for name in sorted(REGIONS):
            value = regions[name]
            if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
                failures.append(f"regions.{name} requires at least one concrete note")
    extrema = data.get("extrema")
    if not isinstance(extrema, dict) or set(extrema) != EXTREMA:
        failures.append("extrema must define top, bottom, left and right")
    else:
        for name, point in extrema.items():
            if (not isinstance(point, list) or len(point) != 2
                    or any(type(v) is not int for v in point)
                    or not (0 <= point[0] < width and 0 <= point[1] < height)):
                failures.append(f"extrema.{name} is outside the parent canvas")
    if data.get("direct_pickup") is True:
        inputs = data.get("direct_pickup_inputs")
        if not isinstance(inputs, dict) or set(inputs) != DIRECT_INPUTS:
            failures.append("direct pickup requires the four-state input set")
        else:
            for name in sorted(DIRECT_INPUTS):
                check_binding(inputs[name], path.parent, f"direct_pickup_inputs.{name}", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", type=Path, required=True)
    args = parser.parse_args()
    try:
        failures = validate(args.annotation)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
    print(json.dumps({"hotspot_preflight_valid": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
