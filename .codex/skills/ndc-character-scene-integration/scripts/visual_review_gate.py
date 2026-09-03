#!/usr/bin/env python3
"""Build and validate evidence for a human/Codex visual review stage.

This tool never infers artistic correctness from geometry or image metadata. It
only hashes the reviewed images, renders a comparison board, and validates the
reviewer's explicit visual findings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


STAGE_CHECKS = {
    "exact-pose-whitebox": {
        "scalePerspective",
        "headScale",
        "supportContact",
        "environmentResponse",
        "posePerformance",
        "sceneOcclusion",
        "uiSafety",
    },
    "contextual-local-result": {
        "identityStyle",
        "scalePerspective",
        "headScale",
        "supportContact",
        "environmentResponse",
        "posePerformance",
        "sceneIntegration",
        "backgroundPreservation",
    },
    "matte-extraction": {
        "silhouetteCompleteness",
        "edgeContamination",
        "internalDetails",
        "noFixedFurniture",
    },
    "pre-composite-registration": {
        "localScalePreserved",
        "headScale",
        "supportContact",
        "environmentResponse",
        "nearFurnitureScale",
        "farFurnitureScale",
        "castRelativeScale",
        "sceneOcclusion",
    },
    "final-full-composite": {
        "overallSceneScale",
        "headScale",
        "castRelativeScale",
        "supportContact",
        "environmentResponse",
        "sceneOcclusion",
        "castOcclusion",
        "gazeStoryLogic",
        "uiSafety",
        "lightingIntegration",
        "backgroundPreservation",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("Visual review contract must be a JSON object.")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(raw: str, contract_path: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = contract_path.parent / path
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"Reviewed image is missing: {path}")
    return path


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def fit_panel(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    panel = Image.new("RGB", size, (26, 29, 31))
    source = image.convert("RGB")
    source.thumbnail((size[0] - 24, size[1] - 52), Image.Resampling.LANCZOS)
    x = (size[0] - source.width) // 2
    y = 40 + (size[1] - 40 - source.height) // 2
    panel.paste(source, (x, y))
    return panel


def validate_contract(data: dict[str, Any], contract_path: Path) -> tuple[list[dict[str, Any]], str]:
    if data.get("schema") != "ndc-stage-visual-review/v1":
        raise ValueError("schema must be ndc-stage-visual-review/v1.")
    stage = data.get("stage")
    if stage not in STAGE_CHECKS:
        raise ValueError(f"Unsupported visual review stage: {stage!r}")
    if data.get("reviewAuthority") != "codex-self-check":
        raise ValueError("reviewAuthority must be codex-self-check.")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("artifacts must contain at least one reviewed image.")
    loaded: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts):
        if not isinstance(item, dict) or not item.get("role") or not item.get("path"):
            raise ValueError(f"artifacts[{index}] requires role and path.")
        path = resolve(str(item["path"]), contract_path)
        loaded.append({"role": str(item["role"]), "path": str(path), "sha256": sha256(path)})
    checks = data.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("checks must be an object authored after visual inspection.")
    missing = sorted(STAGE_CHECKS[stage] - set(checks))
    if missing:
        raise ValueError(f"Visual review is missing checks: {', '.join(missing)}")
    invalid = sorted(name for name, value in checks.items() if value not in {"pass", "fail"})
    if invalid:
        raise ValueError(f"Visual checks must be pass or fail: {', '.join(invalid)}")
    observations = data.get("observations")
    if not isinstance(observations, list) or not observations or not all(str(v).strip() for v in observations):
        raise ValueError("observations must contain explicit visual findings.")
    decision = data.get("decision")
    if decision not in {"pass", "fail"}:
        raise ValueError("decision must be pass or fail.")
    failed = [name for name in STAGE_CHECKS[stage] if checks.get(name) == "fail"]
    if decision == "pass" and failed:
        raise ValueError(f"decision cannot pass failed visual checks: {', '.join(sorted(failed))}")
    return loaded, stage


def build_review(contract_path: Path, output_dir: Path) -> dict[str, Any]:
    data = load_json(contract_path)
    artifacts, stage = validate_contract(data, contract_path)
    panel_size = (720, 500)
    panels: list[Image.Image] = []
    for item in artifacts:
        image = Image.open(item["path"])
        panel = fit_panel(image, panel_size)
        draw = ImageDraw.Draw(panel)
        draw.text((16, 12), item["role"], fill=(240, 240, 240), font=font(20))
        panels.append(panel)
    primary = Image.open(artifacts[0]["path"]).convert("RGB")
    for tile in data.get("localTiles", []):
        if not isinstance(tile, dict) or not tile.get("id") or not tile.get("bbox"):
            raise ValueError("Each localTiles entry requires id and bbox.")
        bbox = [int(round(value)) for value in tile["bbox"]]
        if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
            raise ValueError(f"Invalid local tile bbox: {bbox}")
        crop = primary.crop(tuple(bbox))
        panel = fit_panel(crop, panel_size)
        ImageDraw.Draw(panel).text((16, 12), f"tile:{tile['id']}", fill=(240, 240, 240), font=font(20))
        panels.append(panel)
    columns = 2
    rows = (len(panels) + columns - 1) // columns
    board = Image.new("RGB", (panel_size[0] * columns, panel_size[1] * rows), (15, 17, 18))
    for index, panel in enumerate(panels):
        board.paste(panel, ((index % columns) * panel_size[0], (index // columns) * panel_size[1]))
    output_dir.mkdir(parents=True, exist_ok=True)
    board_path = output_dir / f"{stage}-visual-review-board.png"
    board.save(board_path)
    failed = sorted(name for name in STAGE_CHECKS[stage] if data["checks"].get(name) == "fail")
    report = {
        "schema": "ndc-stage-visual-review-report/v1",
        "stage": stage,
        "reviewAuthority": "codex-self-check",
        "status": "VISUAL_REVIEW_PASS" if data["decision"] == "pass" else "VISUAL_REVIEW_FAIL",
        "artifacts": artifacts,
        "board": str(board_path.resolve()),
        "boardSha256": sha256(board_path),
        "checks": data["checks"],
        "failedChecks": failed,
        "observations": data["observations"],
        "nextStageAuthorized": data["decision"] == "pass" and not failed,
        "note": "This report records an explicit visual review; no pixel metric or metadata inferred artistic correctness.",
    }
    report_path = output_dir / f"{stage}-visual-review-report.json"
    write_json(report_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    try:
        report = build_review(args.contract, args.output_dir)
        print(f"{report['status']} stage={report['stage']} board={report['board']}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=__import__("sys").stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
