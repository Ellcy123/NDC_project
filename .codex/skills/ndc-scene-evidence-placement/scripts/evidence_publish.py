#!/usr/bin/env python3
"""Publish compact NDC scene-evidence deliveries from a verified temporary job."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any


SCENE_PREVIEW_NAME = "scene_preview.png"
XY_NAME = "XYposition.txt"
REPORT_NAME = "production_report.json"
ASSETS_DIR_NAME = "assets"
TEMP_NAMESPACE = "ndc_art_jobs"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def require_inside(path: Path, parent: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(parent.resolve()):
        raise ValueError(f"{label} must stay inside {parent}: {resolved}")
    return resolved


def validated_work_dir(path: Path) -> Path:
    work_dir = path.resolve()
    namespace = (Path(tempfile.gettempdir()) / TEMP_NAMESPACE).resolve()
    if work_dir == namespace or not work_dir.is_relative_to(namespace):
        raise ValueError(
            f"Work directory must be a child of the system temp namespace: {namespace}"
        )
    if not work_dir.is_dir():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    return work_dir


def verified_artifact(
    manifest: dict[str, Any], key: str, work_dir: Path, *, required: bool = True
) -> Path | None:
    record = (manifest.get("artifacts") or {}).get(key)
    if not record:
        if required:
            raise ValueError(f"Manifest is missing required artifact: {key}")
        return None
    path = require_inside(Path(record["path"]), work_dir, f"Artifact {key}")
    if not path.is_file():
        raise FileNotFoundError(f"Artifact does not exist: {path}")
    expected = record.get("sha256")
    actual = sha256(path)
    if expected != actual:
        raise ValueError(f"Artifact hash mismatch for {key}: {path}")
    return path


def copy_verified(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    source_hash = sha256(source)
    if sha256(destination) != source_hash:
        raise ValueError(f"Published copy hash mismatch: {destination}")
    return source_hash


def compact_skipped_records(status_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not status_report:
        return []
    compact: list[dict[str, Any]] = []
    passing = {"pass", "passed", "packaged_pass", "delivered", "ready"}
    for record in status_report.get("records") or []:
        status = str(record.get("status", "unresolved"))
        if status in passing:
            continue
        reasons = record.get("reasons") or record.get("skipReasons") or []
        compact.append(
            {
                "id": str(
                    record.get("id")
                    or record.get("itemId")
                    or record.get("recordId")
                    or "unassigned"
                ),
                "status": status,
                "reasons": [str(reason) for reason in reasons]
                or ([str(record["reason"])] if record.get("reason") else []),
            }
        )
    return compact


def publish_scene(args: argparse.Namespace) -> Path:
    work_dir = validated_work_dir(args.work_dir)
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(
            f"Final delivery already exists; publish to a new versioned directory: {output_dir}"
        )
    if output_dir.is_relative_to(work_dir):
        raise ValueError("Final delivery must not be placed inside the temporary work directory")

    scene_preview = require_inside(args.scene_preview, work_dir, "Scene preview")
    if not scene_preview.is_file() or scene_preview.suffix.lower() != ".png":
        raise ValueError("Scene preview must be an existing PNG inside the work directory")

    status_report: dict[str, Any] | None = None
    if args.status_report:
        status_path = require_inside(args.status_report, work_dir, "Status report")
        status_report = load_json(status_path)

    manifests: list[tuple[Path, dict[str, Any]]] = []
    for raw_path in args.manifest:
        manifest_path = require_inside(raw_path, work_dir, "Delivery manifest")
        manifest = load_json(manifest_path)
        if not manifest.get("passed"):
            raise ValueError(f"Cannot publish a failing delivery manifest: {manifest_path}")
        if str((manifest.get("item") or {}).get("sceneId")) != str(args.scene_id):
            raise ValueError(f"Manifest sceneId does not match {args.scene_id}: {manifest_path}")
        manifests.append((manifest_path, manifest))
    if not manifests:
        raise ValueError("At least one passing delivery manifest is required")

    stage_dir = output_dir.parent / f".{output_dir.name}.publish-{uuid.uuid4().hex}.tmp"
    stage_dir.mkdir(parents=True, exist_ok=False)
    assets_dir = stage_dir / ASSETS_DIR_NAME
    assets_dir.mkdir()

    published_records: list[dict[str, Any]] = []
    xy_lines: list[str] = []
    used_asset_names: set[str] = set()
    try:
        preview_hash = copy_verified(scene_preview, stage_dir / SCENE_PREVIEW_NAME)
        for _, manifest in manifests:
            item = manifest.get("item") or {}
            unity = manifest.get("unityDraft") or {}
            item_id = str(item.get("id") or "unassigned")
            position = [str(value) for value in unity.get("Position") or []]
            if len(position) != 3:
                raise ValueError(f"Record {item_id} must have a three-value Position")
            int(position[0])
            int(position[1])

            artifact_specs = [
                ("mapSprite", str(unity.get("mapSpritePath") or ""), True),
                ("detailSprite", str(unity.get("desSpritePath") or ""), True),
            ]
            icon_omitted = bool((manifest.get("icon") or {}).get("omitted"))
            artifact_specs.append(
                ("iconSprite", str(unity.get("iconPath") or ""), not icon_omitted)
            )

            published_assets: dict[str, str | None] = {}
            published_hashes: dict[str, str] = {}
            for artifact_key, stem, required in artifact_specs:
                source = verified_artifact(
                    manifest, artifact_key, work_dir, required=required
                )
                field = {
                    "mapSprite": "map",
                    "detailSprite": "detail",
                    "iconSprite": "icon",
                }[artifact_key]
                if source is None:
                    published_assets[field] = None
                    continue
                if not stem:
                    raise ValueError(f"Record {item_id} is missing the stem for {artifact_key}")
                filename = f"{stem}.png"
                if source.name != filename:
                    raise ValueError(
                        f"Record {item_id} artifact/stem mismatch: {source.name} != {filename}"
                    )
                if filename in used_asset_names:
                    raise ValueError(f"Duplicate runtime asset filename: {filename}")
                used_asset_names.add(filename)
                published_hashes[field] = copy_verified(source, assets_dir / filename)
                published_assets[field] = f"{ASSETS_DIR_NAME}/{filename}"

            map_stem = str(unity["mapSpritePath"])
            xy_lines.append(f"{map_stem} {position[0]},{position[1]}")
            published_records.append(
                {
                    "id": item_id,
                    "status": "packaged_pass",
                    "Position": position,
                    "assets": published_assets,
                    "sha256": published_hashes,
                }
            )

        (stage_dir / XY_NAME).write_text(
            "\n".join(xy_lines) + "\n", encoding="ascii"
        )
        skipped_records = compact_skipped_records(status_report)
        report: dict[str, Any] = {
            "version": 1,
            "batch": args.batch,
            "sceneId": str(args.scene_id),
            "sceneName": args.scene_name,
            "status": (
                "completed_with_skipped_records" if skipped_records else "completed"
            ),
            "scenePreview": {
                "path": SCENE_PREVIEW_NAME,
                "sha256": preview_hash,
            },
            "successfulRecords": published_records,
            "skippedOrBlockedRecords": skipped_records,
            "validation": {
                "allInputManifestsPassed": True,
                "allPublishedHashesMatch": True,
                "xyLineCount": len(xy_lines),
                "assetCount": len(used_asset_names),
            },
            "temporaryWork": {
                "cleanupRequested": bool(args.cleanup_work_dir),
                "cleanupCompleted": False,
            },
            "unitySync": "not_performed",
        }
        save_json(stage_dir / REPORT_NAME, report)
        stage_dir.rename(output_dir)
    except Exception:
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        raise

    report_path = output_dir / REPORT_NAME
    report = load_json(report_path)
    if args.cleanup_work_dir:
        try:
            shutil.rmtree(work_dir)
            report["temporaryWork"]["cleanupCompleted"] = True
        except Exception as exc:
            report["temporaryWork"]["cleanupError"] = str(exc)
            save_json(report_path, report)
            raise RuntimeError(
                f"Delivery published, but temporary cleanup failed: {work_dir}"
            ) from exc
    save_json(report_path, report)

    print("Scene evidence publication: PASS")
    print(f"Scene: {args.scene_id}")
    print(f"Records: {len(published_records)}")
    print(f"Output: {output_dir}")
    print(
        "Temporary work: "
        + ("deleted" if args.cleanup_work_dir else "retained for recovery")
    )
    return output_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scene-preview", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, action="append", required=True)
    parser.add_argument("--status-report", type=Path)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--scene-name", required=True)
    parser.add_argument(
        "--cleanup-work-dir",
        action="store_true",
        help=(
            "After publication and hash verification, recursively delete only the exact "
            "job directory beneath the system temp ndc_art_jobs namespace"
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    publish_scene(args)


if __name__ == "__main__":
    main()
