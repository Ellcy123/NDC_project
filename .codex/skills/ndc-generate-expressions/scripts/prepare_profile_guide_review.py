#!/usr/bin/env python3
"""Prepare fail-closed profile-guide overlays for NDC expression review.

The tool may check explicitly supplied manual landmarks, but it never sets the
visual or formal decision. Stylized hair, hats, ears, and cheek contours remain
Codex-reviewed semantic landmarks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


PASS = "PASS"
FAIL = "FAIL"
NOT_CHECKED = "NOT_CHECKED"
DEFAULT_SPEC = Path(__file__).resolve().parent.parent / "assets" / "profile-guides" / "profile-guide-spec.json"
COMPLETENESS_FIELDS = (
    "head_complete",
    "hair_hat_complete",
    "left_shoulder_complete",
    "right_shoulder_complete",
    "upper_chest_complete",
    "lower_torso_complete",
    "costume_contours_complete",
    "no_internal_bottom_hole",
    "natural_bottom_exit_ready",
    "source_integrity_confirmed_without_repair",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return data


def draw_guides(base: Image.Image, lines: dict[str, Any]) -> Image.Image:
    output = base.convert("RGBA")
    overlay = Image.new("RGBA", output.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for line in lines.values():
        band = line["band"]
        color = tuple(line["rgba"])
        if line["orientation"] == "horizontal":
            draw.rectangle((0, band[0], output.width - 1, band[1]), fill=color)
        else:
            draw.rectangle((band[0], 0, band[1], output.height - 1), fill=color)
    return Image.alpha_composite(output, overlay)


def check_landmarks(profile: str, profile_spec: dict[str, Any], landmarks: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []

    def add(gate: str, passed: bool, detail: str) -> None:
        checks.append({"gate": gate, "status": PASS if passed else FAIL, "detail": detail})

    for field in COMPLETENESS_FIELDS:
        add(f"bust.{field}", landmarks.get(field) is True, f"{field} must be true")

    lines = profile_spec["lines"]
    if profile == "greenscreen":
        top = landmarks.get("head_top_including_hair_hat_y")
        chin = landmarks.get("chin_y")
        add("guide.head_top_including_hair_hat", isinstance(top, (int, float)) and top >= lines["head_top_including_hair_hat"]["band"][0], f"y={top!r}, minimum={lines['head_top_including_hair_hat']['band'][0]}")
        add("guide.chin_max", isinstance(chin, (int, float)) and chin <= lines["chin_max"]["band"][1], f"y={chin!r}, maximum={lines['chin_max']['band'][1]}")
        add("guide.center_axis", landmarks.get("center_axis_aligned") is True, "manual center-axis alignment must be true")
    else:
        top = landmarks.get("skull_top_excluding_hair_hat_y")
        chin = landmarks.get("chin_y")
        eye = landmarks.get("eye_center_y")
        left = landmarks.get("left_cheek_x")
        right = landmarks.get("right_cheek_x")
        eye_center = lines["eye_center"]["center"]
        tolerance = profile_spec["eye_tolerance_px"]
        add("guide.skull_top_excluding_hair_hat", isinstance(top, (int, float)) and top >= lines["skull_top_excluding_hair_hat"]["band"][0], f"y={top!r}, minimum={lines['skull_top_excluding_hair_hat']['band'][0]}")
        add("guide.chin_max", isinstance(chin, (int, float)) and chin <= lines["chin_max"]["band"][1], f"y={chin!r}, maximum={lines['chin_max']['band'][1]}")
        add("guide.eye_center", isinstance(eye, (int, float)) and abs(eye - eye_center) <= tolerance, f"y={eye!r}, target={eye_center}, tolerance={tolerance}")
        add("guide.left_cheek_min", isinstance(left, (int, float)) and left >= lines["left_cheek_min"]["band"][0], f"x={left!r}, minimum={lines['left_cheek_min']['band'][0]}")
        add("guide.right_cheek_max", isinstance(right, (int, float)) and right <= lines["right_cheek_max"]["band"][1], f"x={right!r}, maximum={lines['right_cheek_max']['band'][1]}")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an NDC expression profile-guide review overlay.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=("greenscreen", "transparent"))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--landmarks", type=Path, help="Optional Codex-reviewed manual landmark JSON")
    parser.add_argument("--guide-spec", type=Path, default=DEFAULT_SPEC)
    args = parser.parse_args()

    input_path = args.input.resolve()
    spec_path = args.guide_spec.resolve()
    spec = load_object(spec_path)
    profile_spec = spec["profiles"][args.profile]
    image = Image.open(input_path)
    expected = tuple(profile_spec["canvas"])
    if image.size != expected:
        raise ValueError(f"Canvas mismatch: got {image.size}, expected {expected}")

    if args.profile == "transparent":
        rgba = image.convert("RGBA")
        checker = Image.new("RGBA", image.size, (232, 232, 232, 255))
        checker.alpha_composite(rgba)
        base = checker
    else:
        base = image.convert("RGBA")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    overlay_path = output_dir / f"{input_path.stem}_profile-guide-overlay.png"
    draw_guides(base, profile_spec["lines"]).save(overlay_path)

    landmarks: dict[str, Any] = {}
    checks: list[dict[str, str]] = []
    if args.landmarks:
        landmarks = load_object(args.landmarks.resolve())
        checks = check_landmarks(args.profile, profile_spec, landmarks)
    mechanical = PASS if checks and all(item["status"] == PASS for item in checks) else (FAIL if checks else NOT_CHECKED)
    report = {
        "schema_version": 1,
        "kind": "ndc_expression_profile_guide_review",
        "profile": args.profile,
        "asset": {"path": str(input_path), "sha256": sha256(input_path)},
        "guide_spec": {"path": str(spec_path), "sha256": sha256(spec_path)},
        "source_example": profile_spec["source_example"],
        "overlay": str(overlay_path),
        "reviewer": None,
        "manual_landmarks_complete": bool(args.landmarks),
        "landmarks": landmarks,
        "checks": checks,
        "mechanical_status": mechanical,
        "visual_status": NOT_CHECKED,
        "formal_status": NOT_CHECKED,
        "notes": [],
    }
    report_path = output_dir / f"{input_path.stem}_profile-guide-review.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PROFILE_GUIDE_MECHANICAL_STATUS: {mechanical}")
    print(f"OVERLAY: {overlay_path}")
    print(f"REPORT: {report_path}")
    return 0 if mechanical in (PASS, NOT_CHECKED) else 2


if __name__ == "__main__":
    raise SystemExit(main())
