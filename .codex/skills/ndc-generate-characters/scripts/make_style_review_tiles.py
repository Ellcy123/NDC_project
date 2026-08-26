#!/usr/bin/env python3
"""Build complete, overlap-safe style-review tiles and overview sheets.

The script never enlarges or shrinks detail tiles. Every source pixel is covered
by at least one tile, and the JSON manifest records exact crop coordinates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def parse_set(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--set must use NAME=PATH")
    name, raw_path = value.split("=", 1)
    name = name.strip()
    path = Path(raw_path.strip()).resolve()
    if not name:
        raise argparse.ArgumentTypeError("set name cannot be empty")
    if not path.exists():
        raise argparse.ArgumentTypeError(f"set path does not exist: {path}")
    return name, path


def axis_starts(length: int, tile_size: int, overlap: int) -> list[int]:
    if length <= tile_size:
        return [0]
    step = tile_size - overlap
    starts = list(range(0, max(1, length - tile_size + 1), step))
    last = length - tile_size
    if starts[-1] != last:
        starts.append(last)
    return starts


def coverage_is_complete(length: int, starts: list[int], tile_size: int) -> bool:
    if not starts or starts[0] != 0:
        return False
    cursor = 0
    for start in starts:
        if start > cursor:
            return False
        cursor = max(cursor, min(length, start + tile_size))
    return cursor >= length


def safe_slug(text: str) -> str:
    allowed = []
    for character in text:
        if character.isalnum() or character in {"-", "_"}:
            allowed.append(character)
        else:
            allowed.append("_")
    slug = "".join(allowed).strip("_")
    return slug[:80] or "image"


def image_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in IMAGE_EXTENSIONS else []
    return sorted(
        item for item in path.rglob("*")
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_overview_sheets(
    records: list[dict], output: Path, cells_per_sheet: int = 12
) -> list[str]:
    overview_dir = output / "overviews"
    overview_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    sheet_paths: list[str] = []
    columns, rows = 4, 3
    cell_w, cell_h = 400, 400
    for sheet_index in range(math.ceil(len(records) / cells_per_sheet)):
        sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
        draw = ImageDraw.Draw(sheet)
        batch = records[
            sheet_index * cells_per_sheet:(sheet_index + 1) * cells_per_sheet
        ]
        for local_index, record in enumerate(batch):
            row, column = divmod(local_index, columns)
            x0, y0 = column * cell_w, row * cell_h
            with Image.open(record["source"]) as image:
                image = image.convert("RGB")
                preview = ImageOps.contain(image, (376, 338))
            px = x0 + (cell_w - preview.width) // 2
            py = y0 + 42 + (338 - preview.height) // 2
            sheet.paste(preview, (px, py))
            draw.text((x0 + 12, y0 + 12), record["id"], fill="black", font=font)
        sheet_path = overview_dir / f"overview_{sheet_index + 1:03d}.png"
        sheet.save(sheet_path, compress_level=1)
        sheet_paths.append(str(sheet_path))
    return sheet_paths


def make_tile_sheets(tile_records: list[dict], output: Path) -> list[str]:
    sheet_dir = output / "review_sheets"
    sheet_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    sheet_paths: list[str] = []
    cell_size = 800
    header = 42
    for sheet_index in range(math.ceil(len(tile_records) / 4)):
        sheet = Image.new("RGB", (1600, 1600), "white")
        draw = ImageDraw.Draw(sheet)
        batch = tile_records[sheet_index * 4:(sheet_index + 1) * 4]
        for local_index, record in enumerate(batch):
            row, column = divmod(local_index, 2)
            x0, y0 = column * cell_size, row * cell_size
            with Image.open(record["tile_path"]) as tile:
                tile = tile.convert("RGB")
            if tile.width > 720 or tile.height > 720:
                raise RuntimeError(f"tile unexpectedly exceeds 720 px: {record}")
            px = x0 + (cell_size - tile.width) // 2
            py = y0 + header + (cell_size - header - tile.height) // 2
            sheet.paste(tile, (px, py))
            label = f'{record["image_id"]} {record["tile_id"]} {record["box"]}'
            draw.text((x0 + 12, y0 + 12), label, fill="black", font=font)
        sheet_path = sheet_dir / f"tiles_{sheet_index + 1:03d}.png"
        sheet.save(sheet_path, compress_level=1)
        sheet_paths.append(str(sheet_path))
    return sheet_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", action="append", required=True, type=parse_set)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tile-size", type=int, default=720)
    parser.add_argument("--overlap", type=int, default=72)
    args = parser.parse_args()

    if not 256 <= args.tile_size <= 720:
        raise SystemExit("--tile-size must be between 256 and 720")
    if not 0 <= args.overlap < args.tile_size:
        raise SystemExit("--overlap must be non-negative and smaller than tile size")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    tiles_root = output / "tiles"
    tiles_root.mkdir(parents=True, exist_ok=True)

    image_records: list[dict] = []
    tile_records: list[dict] = []
    seen_hashes: dict[str, str] = {}
    image_counter = 0

    for set_name, set_path in args.set:
        for source in image_files(set_path):
            image_counter += 1
            image_id = f"I{image_counter:03d}"
            sha256 = file_sha256(source)
            with Image.open(source) as opened:
                image = opened.convert("RGB")
                width, height = image.size
                x_starts = axis_starts(width, args.tile_size, args.overlap)
                y_starts = axis_starts(height, args.tile_size, args.overlap)
                if not coverage_is_complete(width, x_starts, args.tile_size):
                    raise RuntimeError(f"horizontal coverage failed: {source}")
                if not coverage_is_complete(height, y_starts, args.tile_size):
                    raise RuntimeError(f"vertical coverage failed: {source}")

                duplicate_of = seen_hashes.get(sha256)
                record = {
                    "id": image_id,
                    "set": set_name,
                    "source": str(source),
                    "width": width,
                    "height": height,
                    "sha256": sha256,
                    "duplicate_of": duplicate_of,
                    "x_starts": x_starts,
                    "y_starts": y_starts,
                    "coverage_complete": True,
                    "tiles": [],
                }
                image_records.append(record)
                if duplicate_of:
                    continue
                seen_hashes[sha256] = image_id
                image_dir = tiles_root / set_name / f"{image_id}_{safe_slug(source.stem)}"
                image_dir.mkdir(parents=True, exist_ok=True)
                for row, top in enumerate(y_starts):
                    for column, left in enumerate(x_starts):
                        right = min(width, left + args.tile_size)
                        bottom = min(height, top + args.tile_size)
                        tile_id = f"r{row:02d}c{column:02d}"
                        tile_path = image_dir / (
                            f"{tile_id}_x{left}_y{top}_x{right}_y{bottom}.png"
                        )
                        image.crop((left, top, right, bottom)).save(
                            tile_path, compress_level=1
                        )
                        tile_record = {
                            "image_id": image_id,
                            "tile_id": tile_id,
                            "box": [left, top, right, bottom],
                            "tile_path": str(tile_path),
                        }
                        record["tiles"].append(tile_record)
                        tile_records.append(tile_record)

    overview_paths = make_overview_sheets(image_records, output)
    review_sheet_paths = make_tile_sheets(tile_records, output)
    manifest = {
        "protocol": "ndc-style-review-tiles/v1",
        "tile_size": args.tile_size,
        "overlap": args.overlap,
        "image_entries": len(image_records),
        "unique_images": len(seen_hashes),
        "tile_count": len(tile_records),
        "all_sources_covered": all(item["coverage_complete"] for item in image_records),
        "images": image_records,
        "overview_sheets": overview_paths,
        "review_sheets": review_sheet_paths,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Images: {len(image_records)} entries, {len(seen_hashes)} unique")
    print(f"Tiles: {len(tile_records)}; review sheets: {len(review_sheet_paths)}")
    print(f"Coverage complete: {manifest['all_sources_covered']}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
