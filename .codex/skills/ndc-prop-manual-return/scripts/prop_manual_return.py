#!/usr/bin/env python3
"""Validate NDC prop manual-return manifests and verify mechanical exports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


SCHEMA = "ndc-prop-manual-return/v1"
ROLES = {
    "type6",
    "type7",
    "map",
    "scene_carrier",
    "carrier_child_map",
    "big",
    "icon",
}
RENDER_MODES = {"raw_layer", "visual_layer_with_effects", "deterministic_derivative"}
XY_STEM = re.compile(r"__XY_x(?P<x>-?\d+)_y(?P<y>-?\d+)$")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ManifestError(ValueError):
    """A manual-return manifest violates the mechanical export contract."""


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be an object")
    return data


def nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field} must be non-empty text")
    return value.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_info(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        if stream.read(8) != PNG_SIGNATURE:
            raise ManifestError(f"not a PNG: {path.name}")
        length = struct.unpack(">I", stream.read(4))[0]
        kind = stream.read(4)
        payload = stream.read(length)
    if kind != b"IHDR" or len(payload) != 13:
        raise ManifestError(f"missing PNG IHDR: {path.name}")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", payload[:10])
    has_alpha = color_type in {4, 6}
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "has_alpha_channel": has_alpha,
    }


def validate_manifest(data: dict[str, Any]) -> list[dict[str, Any]]:
    if data.get("schema") != SCHEMA:
        raise ManifestError(f"schema must be {SCHEMA}")
    nonempty_text(data.get("unit_id"), "unit_id")
    nonempty_text(data.get("scene_id"), "scene_id")
    if data.get("finalized_by_user") is not True:
        raise ManifestError("finalized_by_user must be true")

    source = data.get("source")
    if not isinstance(source, dict):
        raise ManifestError("source must be an object")
    source_mode = nonempty_text(source.get("mode"), "source.mode")
    if source_mode not in {"saved_psd", "active_photoshop_document"}:
        raise ManifestError("source.mode must be saved_psd or active_photoshop_document")
    nonempty_text(source.get("psd"), "source.psd")
    if source_mode == "saved_psd" and source.get("saved_after_manual_edits") is not True:
        raise ManifestError("source.saved_after_manual_edits must be true for disk-based export")
    if not isinstance(source.get("saved_after_manual_edits"), bool):
        raise ManifestError("source.saved_after_manual_edits must be boolean")
    expected_source_hash = source.get("sha256")
    if expected_source_hash is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", str(expected_source_hash)):
        raise ManifestError("source.sha256 must be null or 64 hexadecimal characters")

    destination = data.get("destination")
    if not isinstance(destination, dict):
        raise ManifestError("destination must be an object")
    nonempty_text(destination.get("directory"), "destination.directory")
    if not isinstance(destination.get("overwrite_authorized"), bool):
        raise ManifestError("destination.overwrite_authorized must be boolean")

    candidate = data.get("candidate_policy")
    if not isinstance(candidate, dict):
        raise ManifestError("candidate_policy must be an object")
    if candidate.get("create_extra_candidate_directory") is not False:
        raise ManifestError("manual return must not create an extra delivery-candidate directory")
    if candidate.get("backup_only_when_needed") is not True:
        raise ManifestError("candidate_policy.backup_only_when_needed must be true")

    xy_config = data.get("xy")
    if not isinstance(xy_config, dict):
        raise ManifestError("xy must be an object")
    if xy_config.get("filename") != "XYposition.txt":
        raise ManifestError("xy.filename must be XYposition.txt")
    if xy_config.get("format") != "fullwidth_brackets":
        raise ManifestError("xy.format must be fullwidth_brackets")

    outputs = data.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ManifestError("outputs must be a non-empty array")

    ids: set[str] = set()
    filenames: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(outputs):
        field = f"outputs[{index}]"
        if not isinstance(raw, dict):
            raise ManifestError(f"{field} must be an object")
        output_id = nonempty_text(raw.get("output_id"), f"{field}.output_id")
        if output_id in ids:
            raise ManifestError(f"duplicate output_id: {output_id}")
        ids.add(output_id)

        layer_path = raw.get("layer_path")
        if not isinstance(layer_path, list) or not layer_path:
            raise ManifestError(f"{field}.layer_path must be a non-empty array")
        for part in layer_path:
            nonempty_text(part, f"{field}.layer_path part")

        role = nonempty_text(raw.get("role"), f"{field}.role")
        if role not in ROLES:
            raise ManifestError(f"unsupported role: {role}")
        filename = nonempty_text(raw.get("filename"), f"{field}.filename")
        if Path(filename).name != filename or Path(filename).suffix.lower() != ".png":
            raise ManifestError(f"{field}.filename must be a PNG basename")
        if filename in filenames:
            raise ManifestError(f"duplicate filename: {filename}")
        filenames.add(filename)

        render_mode = nonempty_text(raw.get("render_mode"), f"{field}.render_mode")
        if render_mode not in RENDER_MODES:
            raise ManifestError(f"unsupported render_mode: {render_mode}")

        coordinate_bearing = raw.get("coordinate_bearing")
        embed_xy = raw.get("embed_xy_in_filename")
        if not isinstance(coordinate_bearing, bool) or not isinstance(embed_xy, bool):
            raise ManifestError(f"{field} coordinate flags must be boolean")
        xy = raw.get("xy")
        if coordinate_bearing:
            if not isinstance(xy, list) or len(xy) != 2 or any(type(value) is not int for value in xy):
                raise ManifestError(f"{field}.xy must contain two integers")
            if role in {"map", "type6", "scene_carrier", "carrier_child_map"} and not embed_xy:
                raise ManifestError(f"{role} must embed XY in its filename")
            if embed_xy:
                match = XY_STEM.search(Path(filename).stem)
                if not match or [int(match.group("x")), int(match.group("y"))] != xy:
                    raise ManifestError(f"{field}.filename XY must match {xy}")
        else:
            if xy is not None or embed_xy:
                raise ManifestError(f"{field} without coordinates must use xy=null and embed_xy_in_filename=false")
            if role not in {"big", "icon"}:
                raise ManifestError(f"role {role} must be coordinate-bearing")

        expected_hash = raw.get("expected_sha256")
        if expected_hash is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", str(expected_hash)):
            raise ManifestError(f"{field}.expected_sha256 must be null or a SHA-256")

        final_profile = raw.get("final_profile")
        target_size = raw.get("target_size")
        if role in {"big", "icon"}:
            if final_profile is not None:
                nonempty_text(final_profile, f"{field}.final_profile")
            if target_size is not None and (
                not isinstance(target_size, list)
                or len(target_size) != 2
                or any(type(value) is not int or value <= 0 for value in target_size)
            ):
                raise ManifestError(f"{field}.target_size must contain two positive integers when recorded")
        elif final_profile is not None or target_size is not None:
            raise ManifestError(f"{field} may only set final_profile/target_size for Big or Icon")

        normalized.append(raw)

    for raw in normalized:
        parent_id = raw.get("parent_id")
        if parent_id is not None:
            if not isinstance(parent_id, str) or parent_id not in ids:
                raise ManifestError(f"unknown parent_id for {raw['output_id']}: {parent_id}")
            if parent_id == raw["output_id"]:
                raise ManifestError(f"output cannot parent itself: {parent_id}")
    return normalized


def expected_xy_text(outputs: list[dict[str, Any]]) -> str:
    lines = [f"{Path(item['filename']).stem}\t【{item['xy'][0]},{item['xy'][1]}】" for item in outputs if item["coordinate_bearing"]]
    return "\n".join(lines) + ("\n" if lines else "")


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def command_validate(args: argparse.Namespace) -> int:
    outputs = validate_manifest(read_json(args.manifest))
    print(json.dumps({"schema": SCHEMA, "valid": True, "output_count": len(outputs)}, ensure_ascii=False))
    return 0


def command_write_xy(args: argparse.Namespace) -> int:
    data = read_json(args.manifest)
    outputs = validate_manifest(data)
    destination = args.output
    if destination.exists():
        if not args.replace:
            raise ManifestError(f"XY file already exists: {destination}")
        if data["destination"]["overwrite_authorized"] is not True:
            raise ManifestError("--replace requires destination.overwrite_authorized=true")
    write_text_atomic(destination, expected_xy_text(outputs))
    print(destination)
    return 0


def command_verify(args: argparse.Namespace) -> int:
    data = read_json(args.manifest)
    outputs = validate_manifest(data)
    delivery_dir = args.delivery_dir.resolve()
    records: list[dict[str, Any]] = []
    for item in outputs:
        path = delivery_dir / item["filename"]
        if not path.is_file():
            raise ManifestError(f"missing output: {item['filename']}")
        actual_hash = sha256(path)
        expected_hash = item.get("expected_sha256")
        if expected_hash and actual_hash.lower() != str(expected_hash).lower():
            raise ManifestError(f"SHA-256 mismatch: {item['filename']}")
        info = png_info(path)
        if not info["has_alpha_channel"]:
            raise ManifestError(f"output is not RGBA/gray-alpha PNG: {item['filename']}")
        target_size = item.get("target_size")
        size_matches_target = target_size is None or [info["width"], info["height"]] == target_size
        records.append({
            "output_id": item["output_id"],
            "filename": item["filename"],
            "sha256": actual_hash,
            "png": info,
            "xy": item.get("xy"),
            "parent_id": item.get("parent_id"),
            "final_profile": item.get("final_profile"),
            "target_size": target_size,
            "size_matches_target": size_matches_target,
        })

    expected_xy = expected_xy_text(outputs)
    actual_xy = args.xy_file.read_text(encoding="utf-8")
    if actual_xy.replace("\r\n", "\n") != expected_xy:
        raise ManifestError("XYposition.txt does not match manifest order, stems, or coordinates")

    source_path = Path(data["source"]["psd"])
    if not source_path.is_absolute():
        source_path = (args.manifest.parent / source_path).resolve()
    source_record: dict[str, Any] = {
        "mode": data["source"]["mode"],
        "path": str(source_path),
        "exists": source_path.is_file(),
    }
    if source_path.is_file():
        source_record["sha256"] = sha256(source_path)
        expected_source_hash = data["source"].get("sha256")
        if expected_source_hash and source_record["sha256"].lower() != str(expected_source_hash).lower():
            raise ManifestError("source PSD SHA-256 mismatch")
    elif data["source"]["mode"] == "saved_psd":
        raise ManifestError(f"saved source PSD does not exist: {source_path}")

    report = {
        "schema": "ndc-prop-manual-return-verification/v1",
        "status": "MECHANICAL_EXPORT_COMPLETE",
        "source": source_record,
        "candidate_directory_created": False,
        "outputs": records,
        "xy_file": {"path": str(args.xy_file), "sha256": sha256(args.xy_file)},
        "formal_pass": False,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        write_text_atomic(args.report, rendered)
    print(rendered, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a manual-return manifest")
    validate.add_argument("--manifest", type=Path, required=True)
    validate.set_defaults(func=command_validate)

    write_xy = subparsers.add_parser("write-xy", help="write canonical XYposition.txt")
    write_xy.add_argument("--manifest", type=Path, required=True)
    write_xy.add_argument("--output", type=Path, required=True)
    write_xy.add_argument("--replace", action="store_true")
    write_xy.set_defaults(func=command_write_xy)

    verify = subparsers.add_parser("verify", help="verify exported PNGs and XYposition.txt")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--delivery-dir", type=Path, required=True)
    verify.add_argument("--xy-file", type=Path, required=True)
    verify.add_argument("--report", type=Path)
    verify.set_defaults(func=command_verify)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (ManifestError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
