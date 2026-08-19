#!/usr/bin/env python3
"""Split, own, merge, and verify high-resolution clean-plate tiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat


def parse_cuts(raw: str | None, limit: int, parts: int) -> list[int]:
    if raw:
        inner = [int(value.strip()) for value in raw.split(",") if value.strip()]
        if len(inner) != parts - 1:
            raise ValueError(f"expected {parts - 1} inner cuts, got {len(inner)}")
        cuts = [0, *inner, limit]
    else:
        cuts = [round(index * limit / parts) for index in range(parts + 1)]
    if cuts[0] != 0 or cuts[-1] != limit or any(a >= b for a, b in zip(cuts, cuts[1:])):
        raise ValueError(f"cuts must increase strictly from 0 to {limit}: {cuts}")
    return cuts


def as_box(raw: str) -> tuple[int, int, int, int]:
    values = tuple(int(value.strip()) for value in raw.split(","))
    if len(values) != 4 or values[0] >= values[2] or values[1] >= values[3]:
        raise ValueError("bbox must be left,top,right,bottom")
    return values


def split(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        width, height = image.size
        x_cuts = parse_cuts(args.x_cuts, width, args.cols)
        y_cuts = parse_cuts(args.y_cuts, height, args.rows)
        tiles = []
        for row in range(args.rows):
            for col in range(args.cols):
                core = [x_cuts[col], y_cuts[row], x_cuts[col + 1], y_cuts[row + 1]]
                crop = [
                    max(0, core[0] - args.overlap),
                    max(0, core[1] - args.overlap),
                    min(width, core[2] + args.overlap),
                    min(height, core[3] + args.overlap),
                ]
                name = f"tile_r{row + 1}_c{col + 1}.png"
                image.crop(crop).save(out_dir / name)
                tiles.append({"name": name, "row": row + 1, "col": col + 1, "core": core, "crop": crop})
    manifest = {
        "source": str(source),
        "size": [width, height],
        "cols": args.cols,
        "rows": args.rows,
        "overlap": args.overlap,
        "x_cuts": x_cuts,
        "y_cuts": y_cuts,
        "tiles": tiles,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(tiles)} tiles and {out_dir / 'manifest.json'}")


def load_manifest(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def contains_with_margin(core: Iterable[int], box: Iterable[int], margin: int) -> bool:
    left, top, right, bottom = core
    b_left, b_top, b_right, b_bottom = box
    return (
        b_left >= left + margin
        and b_top >= top + margin
        and b_right <= right - margin
        and b_bottom <= bottom - margin
    )


def owner(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    box = as_box(args.bbox)
    candidates = [tile for tile in manifest["tiles"] if contains_with_margin(tile["core"], box, args.margin)]
    if len(candidates) == 1:
        print(f"SAFE owner={candidates[0]['name']} core={candidates[0]['core']}")
        return
    touching = []
    for tile in manifest["tiles"]:
        left, top, right, bottom = tile["core"]
        if box[0] < right and box[2] > left and box[1] < bottom and box[3] > top:
            touching.append(tile["name"])
    print("UNSAFE: move x/y cuts or use one bridge crop; touching=" + ",".join(touching))
    raise SystemExit(2)


def feather_mask(size: tuple[int, int], feather: int, edges: tuple[bool, bool, bool, bool]) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 255)
    pixels = mask.load()
    left_edge, top_edge, right_edge, bottom_edge = edges
    if feather <= 0:
        return mask
    for y in range(height):
        for x in range(width):
            weight = 255
            if left_edge and x < feather:
                weight = min(weight, round(255 * x / feather))
            if right_edge and width - 1 - x < feather:
                weight = min(weight, round(255 * (width - 1 - x) / feather))
            if top_edge and y < feather:
                weight = min(weight, round(255 * y / feather))
            if bottom_edge and height - 1 - y < feather:
                weight = min(weight, round(255 * (height - 1 - y) / feather))
            pixels[x, y] = max(0, weight)
    return mask


def parse_regions(values: list[str] | None) -> dict[str, list[tuple[int, int, int, int]]]:
    regions: dict[str, list[tuple[int, int, int, int]]] = {}
    for value in values or []:
        try:
            name, raw_box = value.split(":", 1)
        except ValueError as error:
            raise ValueError("region must be tile-name:left,top,right,bottom") from error
        regions.setdefault(name, []).append(as_box(raw_box))
    return regions


def local_region_mask(
    core: list[int], regions: list[tuple[int, int, int, int]], feather: int
) -> Image.Image:
    core_left, core_top, core_right, core_bottom = core
    mask = Image.new("L", (core_right - core_left, core_bottom - core_top), 0)
    draw = ImageDraw.Draw(mask)
    for box in regions:
        if not contains_with_margin(core, box, 0):
            raise ValueError(f"edit region {box} is not wholly owned by core {core}")
        draw.rectangle(
            (box[0] - core_left, box[1] - core_top, box[2] - core_left, box[3] - core_top),
            fill=255,
        )
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather / 2))
    return mask


def load_reconstructed_crop(tile: dict, tiles_dir: Path) -> np.ndarray:
    edited_path = tiles_dir / tile["name"]
    if not edited_path.exists():
        raise FileNotFoundError(f"missing reconstructed tile: {edited_path}")
    crop_left, crop_top, crop_right, crop_bottom = tile["crop"]
    crop_size = (crop_right - crop_left, crop_bottom - crop_top)
    with Image.open(edited_path) as edited_image:
        edited = edited_image.convert("RGB")
        if edited.size != crop_size:
            edited = edited.resize(crop_size, Image.Resampling.LANCZOS)
        return np.asarray(edited, dtype=np.float32)


def overlap_box(first: dict, second: dict) -> tuple[int, int, int, int] | None:
    left = max(first["crop"][0], second["crop"][0])
    top = max(first["crop"][1], second["crop"][1])
    right = min(first["crop"][2], second["crop"][2])
    bottom = min(first["crop"][3], second["crop"][3])
    if left >= right or top >= bottom:
        return None
    return left, top, right, bottom


def overlap_slice(tile: dict, box: tuple[int, int, int, int]) -> tuple[slice, slice]:
    crop_left, crop_top, _, _ = tile["crop"]
    left, top, right, bottom = box
    return slice(top - crop_top, bottom - crop_top), slice(left - crop_left, right - crop_left)


def fit_crop_color_to_left_neighbor(current: np.ndarray, current_tile: dict, left: np.ndarray, left_tile: dict) -> tuple[np.ndarray, list[float]]:
    box = overlap_box(left_tile, current_tile)
    if box is None:
        return current, [1.0, 1.0, 1.0]
    left_y, left_x = overlap_slice(left_tile, box)
    current_y, current_x = overlap_slice(current_tile, box)
    left_mean = left[left_y, left_x].mean(axis=(0, 1))
    current_mean = current[current_y, current_x].mean(axis=(0, 1))
    gain = np.clip(left_mean / np.maximum(current_mean, 1.0), 0.82, 1.18)
    return np.clip(current * gain.reshape(1, 1, 3), 0, 255), [float(value) for value in gain]


def select_vertical_seam(left: np.ndarray, left_tile: dict, right: np.ndarray, right_tile: dict) -> int:
    box = overlap_box(left_tile, right_tile)
    if box is None:
        raise ValueError(f"neighboring crops do not overlap: {left_tile['name']} / {right_tile['name']}")
    start, _, end, _ = box
    left_y, left_x = overlap_slice(left_tile, box)
    right_y, right_x = overlap_slice(right_tile, box)
    difference = np.abs(left[left_y, left_x] - right[right_y, right_x]).mean(axis=(0, 2))
    guard = min(24, max(4, (end - start) // 8))
    candidates = difference[guard:-guard] if difference.size > 2 * guard else difference
    offset = int(np.argmin(candidates)) + (guard if difference.size > 2 * guard else 0)
    return start + offset


def merge_full_reconstruction(manifest: dict, tiles_dir: Path, output: Path, color_fit: bool = True) -> None:
    if manifest["rows"] != 1 or manifest["cols"] != 3:
        raise ValueError("--full-reconstruction requires exactly three full-height vertical crops (3x1)")
    tiles = sorted(manifest["tiles"], key=lambda item: (item["row"], item["col"]))
    reconstructed: list[np.ndarray] = []
    gains: list[list[float]] = []
    for index, tile in enumerate(tiles):
        image = load_reconstructed_crop(tile, tiles_dir)
        if index and color_fit:
            image, gain = fit_crop_color_to_left_neighbor(image, tile, reconstructed[index - 1], tiles[index - 1])
            gains.append(gain)
        elif index:
            gains.append([1.0, 1.0, 1.0])
        reconstructed.append(image)

    seams = [select_vertical_seam(reconstructed[index - 1], tiles[index - 1], reconstructed[index], tiles[index]) for index in range(1, len(tiles))]
    width, height = manifest["size"]
    merged = np.zeros((height, width, 3), dtype=np.uint8)
    boundaries = [0, *seams, width]
    for index, (tile, image) in enumerate(zip(tiles, reconstructed)):
        crop_left, crop_top, crop_right, crop_bottom = tile["crop"]
        left = max(boundaries[index], crop_left)
        right = min(boundaries[index + 1], crop_right)
        if left >= right:
            raise ValueError(f"selected seam does not leave a usable span for {tile['name']}")
        merged[crop_top:crop_bottom, left:right] = image[:, left - crop_left:right - crop_left].astype(np.uint8)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(merged, mode="RGB").save(output)
    rounded = [[round(value, 4) for value in gain] for gain in gains]
    print(f"merged {len(tiles)} full reconstruction crops with overlap seam selection: {output}; seams={seams}; gains={rounded}")


def merge(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    tiles_dir = Path(args.tiles_dir)
    output = Path(args.output)
    if args.full_reconstruction:
        if args.region:
            raise ValueError("--region cannot be combined with --full-reconstruction")
        merge_full_reconstruction(manifest, tiles_dir, output, color_fit=not args.no_color_fit)
        return
    regions = parse_regions(args.region)
    source = Path(manifest["source"])
    with Image.open(source) as original:
        canvas = original.convert("RGBA")
    processed = 0
    for tile in manifest["tiles"]:
        edited_path = tiles_dir / tile["name"]
        if not edited_path.exists():
            continue
        crop_left, crop_top, crop_right, crop_bottom = tile["crop"]
        crop_size = (crop_right - crop_left, crop_bottom - crop_top)
        with Image.open(edited_path) as edited_image:
            edited = edited_image.convert("RGBA")
            if edited.size != crop_size:
                edited = edited.resize(crop_size, Image.Resampling.LANCZOS)
        core_left, core_top, core_right, core_bottom = tile["core"]
        local_core = (
            core_left - crop_left,
            core_top - crop_top,
            core_right - crop_left,
            core_bottom - crop_top,
        )
        patch = edited.crop(local_core)
        if regions:
            tile_regions = regions.get(tile["name"], [])
            if not tile_regions:
                continue
            mask = local_region_mask(tile["core"], tile_regions, args.feather)
        else:
            edges = (core_left > 0, core_top > 0, core_right < manifest["size"][0], core_bottom < manifest["size"][1])
            mask = feather_mask(patch.size, args.feather, edges)
        canvas.paste(patch, (core_left, core_top), mask)
        processed += 1
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output)
    print(f"merged {processed} processed owner tiles onto source pixels: {output}")


def verify(args: argparse.Namespace) -> None:
    with Image.open(args.source) as source_image, Image.open(args.output) as output_image:
        source = source_image.convert("RGB")
        output = output_image.convert("RGB")
        if source.size != output.size:
            raise SystemExit(f"FAIL size {source.size} -> {output.size}")
        difference = ImageChops.difference(source, output)
        stats = ImageStat.Stat(difference)
        mean = sum(stats.mean) / len(stats.mean)
        extrema = difference.getextrema()
        maximum = max(channel[1] for channel in extrema)
        changed = difference.getbbox() is not None
        print(f"PASS size={source.size[0]}x{source.size[1]} changed={changed} mean_abs_diff={mean:.4f} max_diff={maximum}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    split_cmd = commands.add_parser("split")
    split_cmd.add_argument("source")
    split_cmd.add_argument("--out-dir", required=True)
    split_cmd.add_argument("--cols", type=int, default=3)
    split_cmd.add_argument("--rows", type=int, default=2)
    split_cmd.add_argument("--overlap", type=int, default=160)
    split_cmd.add_argument("--x-cuts", help="comma-separated inner x cut positions")
    split_cmd.add_argument("--y-cuts", help="comma-separated inner y cut positions")
    split_cmd.set_defaults(func=split)

    owner_cmd = commands.add_parser("owner")
    owner_cmd.add_argument("manifest")
    owner_cmd.add_argument("--bbox", required=True)
    owner_cmd.add_argument("--margin", type=int, default=48)
    owner_cmd.set_defaults(func=owner)

    merge_cmd = commands.add_parser("merge")
    merge_cmd.add_argument("manifest")
    merge_cmd.add_argument("--tiles-dir", required=True)
    merge_cmd.add_argument("--output", required=True)
    merge_cmd.add_argument(
        "--region",
        action="append",
        help="repeatable source-coordinate region tile.png:left,top,right,bottom; only these areas are composited",
    )
    merge_cmd.add_argument("--feather", type=int, default=24)
    merge_cmd.add_argument(
        "--full-reconstruction",
        action="store_true",
        help="fit and seam-select exactly three full-height reconstructed crops across their overlaps instead of compositing local regions",
    )
    merge_cmd.add_argument(
        "--no-color-fit",
        action="store_true",
        help="with --full-reconstruction, preserve each conditioned crop's native colour and select only a hard overlap seam",
    )
    merge_cmd.set_defaults(func=merge)

    verify_cmd = commands.add_parser("verify")
    verify_cmd.add_argument("source")
    verify_cmd.add_argument("output")
    verify_cmd.set_defaults(func=verify)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
