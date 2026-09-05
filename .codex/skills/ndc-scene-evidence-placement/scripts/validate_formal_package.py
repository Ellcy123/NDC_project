#!/usr/bin/env python3
"""Validate the clean, complete boundary of an NDC formal image-asset folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FORBIDDEN_TOKENS = (
    "candidate",
    "checker",
    "debug",
    "history",
    "manifest",
    "mask",
    "old",
    "overlay",
    "rejected",
    "report",
    "superseded",
    "verification",
    "候选",
    "历史",
    "旧版",
    "拒绝",
    "验证",
    "报告",
    "叠图",
)


def parse_xy(path: Path) -> tuple[dict[str, tuple[int, int]], list[str]]:
    entries: dict[str, tuple[int, int]] = {}
    errors: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2 or "," not in parts[1]:
            errors.append(f"XY line {line_number} is not '<stem> x,y'")
            continue
        stem = parts[0]
        pair = parts[1].split(",")
        if len(pair) != 2:
            errors.append(f"XY line {line_number} must contain exactly one comma")
            continue
        try:
            coordinate = (int(pair[0]), int(pair[1]))
        except ValueError:
            errors.append(f"XY line {line_number} has non-integer coordinates")
            continue
        if stem in entries:
            errors.append(f"XY stem is duplicated: {stem}")
        entries[stem] = coordinate
    return entries, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--required-png", action="append", default=[])
    parser.add_argument("--required-xy-stem", action="append", default=[])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    folder = args.folder.resolve()
    failures: list[str] = []
    if not folder.is_dir():
        failures.append(f"formal folder does not exist: {folder}")
        files: list[Path] = []
    else:
        files = sorted(path for path in folder.iterdir() if path.is_file())

    allowed_names = set(args.required_png) | {"XYposition.txt"}
    actual_names = {path.name for path in files}
    missing = sorted(allowed_names - actual_names)
    extra = sorted(actual_names - allowed_names)
    if missing:
        failures.append(f"missing required files: {missing}")
    if extra:
        failures.append(f"unexpected files: {extra}")

    for path in files:
        lowered = path.name.lower()
        if path.name != "XYposition.txt" and path.suffix.lower() != ".png":
            failures.append(f"non-PNG formal image asset: {path.name}")
        matches = [token for token in FORBIDDEN_TOKENS if token in lowered]
        if matches:
            failures.append(f"forbidden formal filename token in {path.name}: {matches}")

    xy_path = folder / "XYposition.txt"
    if xy_path.is_file():
        xy_entries, xy_errors = parse_xy(xy_path)
        failures.extend(xy_errors)
    else:
        xy_entries = {}
    missing_xy = sorted(set(args.required_xy_stem) - set(xy_entries))
    unexpected_xy = sorted(set(xy_entries) - set(args.required_xy_stem))
    if missing_xy:
        failures.append(f"missing XY stems: {missing_xy}")
    if unexpected_xy:
        failures.append(f"unexpected XY stems: {unexpected_xy}")

    payload = {
        "version": 1,
        "kind": "ndc-formal-image-package",
        "folder": str(folder),
        "requiredPng": args.required_png,
        "requiredXyStems": args.required_xy_stem,
        "actualFiles": sorted(actual_names),
        "xyEntries": {stem: list(value) for stem, value in sorted(xy_entries.items())},
        "failures": failures,
        "passed": not failures,
    }
    if args.report:
        args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
        args.report.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
