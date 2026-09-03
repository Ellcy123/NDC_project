from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageFilter


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def is_neutral_background(pixel: tuple[int, int, int], minimum: int, spread: int) -> bool:
    return min(pixel) >= minimum and max(pixel) - min(pixel) <= spread


def border_connected_background(image: Image.Image, minimum: int = 232, spread: int = 14) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    visited = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if visited[index] or not is_neutral_background(pixels[x, y], minimum, spread):
            return
        visited[index] = 1
        queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    mask = Image.new("L", (width, height), 255)
    output = mask.load()
    for index, value in enumerate(visited):
        if value:
            output[index % width, index // width] = 0
    return mask


def remove_large_neutral_islands(
    source: Image.Image,
    foreground_mask: Image.Image,
    minimum: int = 232,
    spread: int = 14,
    minimum_area: int = 64,
) -> Image.Image:
    rgb = source.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    mask = foreground_mask.copy()
    output = mask.load()
    visited = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if visited[index] or not is_neutral_background(pixels[x, y], minimum, spread):
                continue
            visited[index] = 1
            queue = deque([(x, y)])
            component: list[tuple[int, int]] = []
            while queue:
                px, py = queue.popleft()
                component.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    neighbor = ny * width + nx
                    if visited[neighbor] or not is_neutral_background(pixels[nx, ny], minimum, spread):
                        continue
                    visited[neighbor] = 1
                    queue.append((nx, ny))
            if len(component) >= minimum_area:
                for px, py in component:
                    output[px, py] = 0
    return mask


def suppress_neutral_halo(
    source: Image.Image,
    foreground_mask: Image.Image,
    minimum: int = 190,
    spread: int = 12,
    rounds: int = 12,
) -> Image.Image:
    rgb = source.convert("RGB")
    pixels = rgb.load()
    mask = foreground_mask.copy()
    width, height = mask.size
    for _ in range(rounds):
        current = mask.load()
        remove: list[tuple[int, int]] = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if current[x, y] == 0 or not is_neutral_background(pixels[x, y], minimum, spread):
                    continue
                if any(current[x + dx, y + dy] == 0 for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    remove.append((x, y))
        for x, y in remove:
            current[x, y] = 0
    return mask


def restore_enclosed_foreground_holes(foreground_mask: Image.Image) -> tuple[Image.Image, int]:
    """Restore transparent regions fully enclosed by the actor silhouette.

    Checker extraction may classify white hair, shirts, pearls, or paper as
    neutral background.  True exterior gaps (for example between the legs)
    remain connected to the canvas border; only enclosed transparent regions
    are restored here.
    """
    mask = foreground_mask.copy()
    pixels = mask.load()
    width, height = mask.size
    exterior = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if exterior[index] or pixels[x, y] > 16:
            return
        exterior[index] = 1
        queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)
    while queue:
        x, y = queue.popleft()
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    restored = 0
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if pixels[x, y] <= 16 and not exterior[index]:
                pixels[x, y] = 255
                restored += 1
    return mask, restored


def keep_significant_foreground_components(
    foreground_mask: Image.Image,
    minimum_area: int = 256,
) -> tuple[Image.Image, int]:
    """Discard isolated checker remnants without assuming one rigid component."""
    mask = foreground_mask.copy()
    pixels = mask.load()
    width, height = mask.size
    visited = bytearray(width * height)
    removed = 0
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if visited[index] or pixels[x, y] <= 16:
                continue
            visited[index] = 1
            queue = deque([(x, y)])
            component: list[tuple[int, int]] = []
            while queue:
                px, py = queue.popleft()
                component.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    neighbor = ny * width + nx
                    if visited[neighbor] or pixels[nx, ny] <= 16:
                        continue
                    visited[neighbor] = 1
                    queue.append((nx, ny))
            if len(component) < minimum_area:
                for px, py in component:
                    pixels[px, py] = 0
                removed += len(component)
    return mask, removed


def make_conservative_alpha(background_mask: Image.Image) -> Image.Image:
    # Expand foreground instead of eroding it so fine silhouette content is
    # never sacrificed to hide a halo.
    expanded = background_mask.filter(ImageFilter.MaxFilter(3))
    return expanded.filter(ImageFilter.GaussianBlur(0.55))


def decontaminate_edge(source: Image.Image, alpha: Image.Image, core_mask: Image.Image) -> Image.Image:
    rgba = source.convert("RGBA")
    pixels = rgba.load()
    alpha_pixels = alpha.load()
    core = core_mask.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            if not 0 < alpha_pixels[x, y] < 255:
                continue
            replacement = None
            for radius in range(1, 5):
                candidates = []
                for py in range(max(0, y - radius), min(height, y + radius + 1)):
                    for px in range(max(0, x - radius), min(width, x + radius + 1)):
                        if max(abs(px - x), abs(py - y)) == radius and core[px, py] == 255:
                            candidates.append((abs(px - x) + abs(py - y), px, py))
                if candidates:
                    _, px, py = min(candidates)
                    replacement = pixels[px, py][:3]
                    break
            if replacement is not None:
                pixels[x, y] = (*replacement, pixels[x, y][3])
    rgba.putalpha(alpha)
    return rgba


def audit_neutral_edge_contamination(
    cutout: Image.Image,
    neutral_minimum: int = 120,
    neutral_spread: int = 45,
    interior_dark_maximum: int = 105,
) -> dict[str, float | int]:
    """Detect retained gray/white RGB rims without changing alpha coverage.

    A correct alpha can still carry checker/background color in its straight
    RGB edge pixels.  Count only neutral exterior-edge pixels that sit beside a
    materially darker or chromatic interior, which avoids treating an actual
    white shirt or sheet of paper as a fringe merely because it reaches the
    silhouette.
    """
    rgba = cutout.convert("RGBA")
    pixels = rgba.load()
    alpha = rgba.getchannel("A")
    alpha_pixels = alpha.load()
    width, height = rgba.size
    edge_pixels = 0
    contaminated = 0
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if alpha_pixels[x, y] <= 16:
                continue
            near_exterior = any(
                alpha_pixels[px, py] <= 16
                for radius in (1, 2, 3)
                for py in range(max(0, y - radius), min(height, y + radius + 1))
                for px in range(max(0, x - radius), min(width, x + radius + 1))
                if max(abs(px - x), abs(py - y)) == radius
            )
            if not near_exterior:
                continue
            edge_pixels += 1
            rgb = pixels[x, y][:3]
            if min(rgb) < neutral_minimum or max(rgb) - min(rgb) > neutral_spread:
                continue
            has_dark_or_chromatic_interior = False
            for radius in (1, 2, 3):
                for py in range(max(0, y - radius), min(height, y + radius + 1)):
                    for px in range(max(0, x - radius), min(width, x + radius + 1)):
                        if max(abs(px - x), abs(py - y)) != radius or alpha_pixels[px, py] < 245:
                            continue
                        interior_rgb = pixels[px, py][:3]
                        if min(interior_rgb) <= interior_dark_maximum or max(interior_rgb) - min(interior_rgb) > neutral_spread:
                            has_dark_or_chromatic_interior = True
                            break
                    if has_dark_or_chromatic_interior:
                        break
                if has_dark_or_chromatic_interior:
                    break
            if has_dark_or_chromatic_interior:
                contaminated += 1
    ratio = contaminated / edge_pixels if edge_pixels else 0.0
    return {
        "edgePixelCount": edge_pixels,
        "neutralContaminatedEdgePixelCount": contaminated,
        "neutralContaminatedEdgeRatio": ratio,
    }


def validate_coverage(alpha: Image.Image, contract: dict | None) -> list[str]:
    failures: list[str] = []
    bbox = alpha.getbbox()
    if bbox is None:
        return ["empty alpha"]
    if not contract:
        return failures
    pixels = alpha.load()
    width, height = alpha.size
    for item in contract.get("protectedPoints", []):
        name = item["name"]
        x, y = (int(round(value)) for value in item["point"])
        radius = int(item.get("radius", 3))
        if not any(
            pixels[px, py] > 16
            for py in range(max(0, y - radius), min(height, y + radius + 1))
            for px in range(max(0, x - radius), min(width, x + radius + 1))
        ):
            failures.append(f"protected point missing: {name}")
    bounds = contract.get("minimumAlphaBounds")
    if bounds:
        left, top, right, bottom = bbox
        if left > bounds[0]:
            failures.append(f"alpha left edge inset: {left} > {bounds[0]}")
        if top > bounds[1]:
            failures.append(f"alpha top edge inset: {top} > {bounds[1]}")
        if right < bounds[2]:
            failures.append(f"alpha right edge inset: {right} < {bounds[2]}")
        if bottom < bounds[3]:
            failures.append(f"alpha bottom edge inset: {bottom} < {bounds[3]}")
    return failures


def composite_preview(cutout: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    background = Image.new("RGBA", cutout.size, color)
    background.alpha_composite(cutout)
    return background


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a conservative alpha from a border-connected neutral checker background.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--preview-prefix", type=Path, required=True)
    parser.add_argument("--coverage-contract", type=Path)
    parser.add_argument("--minimum", type=int, default=232)
    parser.add_argument("--spread", type=int, default=14)
    parser.add_argument("--max-neutral-edge-ratio", type=float, default=0.001)
    parser.add_argument("--minimum-foreground-component-area", type=int, default=256)
    args = parser.parse_args()

    opened = Image.open(args.input)
    source_mode = opened.mode
    source = opened.convert("RGBA")
    base_alpha = border_connected_background(source, args.minimum, args.spread)
    without_islands = remove_large_neutral_islands(source, base_alpha, args.minimum, args.spread)
    without_gray_islands = remove_large_neutral_islands(source, without_islands, 180, 20, 64)
    clean_core = suppress_neutral_halo(source, without_gray_islands, 100, 45, 8)
    clean_core, restored_hole_pixels = restore_enclosed_foreground_holes(clean_core)
    clean_core, removed_fragment_pixels = keep_significant_foreground_components(
        clean_core,
        args.minimum_foreground_component_area,
    )
    alpha = make_conservative_alpha(clean_core)
    contract = json.loads(args.coverage_contract.read_text(encoding="utf-8")) if args.coverage_contract else None
    failures = validate_coverage(alpha, contract)

    cutout = decontaminate_edge(source, alpha, clean_core)
    edge_audit = audit_neutral_edge_contamination(cutout)
    if edge_audit["neutralContaminatedEdgeRatio"] > args.max_neutral_edge_ratio:
        failures.append(
            "neutral RGB fringe remains: "
            f"{edge_audit['neutralContaminatedEdgeRatio']:.4f} > {args.max_neutral_edge_ratio:.4f}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cutout.save(args.output)
    args.preview_prefix.parent.mkdir(parents=True, exist_ok=True)
    black_path = args.preview_prefix.with_name(args.preview_prefix.name + "-black.png")
    white_path = args.preview_prefix.with_name(args.preview_prefix.name + "-white.png")
    scene_tone_path = args.preview_prefix.with_name(args.preview_prefix.name + "-scene-tone.png")
    composite_preview(cutout, (0, 0, 0, 255)).save(black_path)
    composite_preview(cutout, (255, 255, 255, 255)).save(white_path)
    composite_preview(cutout, (24, 31, 29, 255)).save(scene_tone_path)

    report = {
        "schema": "ndc-conservative-matte-report/v2",
        "status": "TECHNICAL_FILE_PASS" if not failures else "TECHNICAL_FILE_FAIL",
        "source": str(args.input.resolve()),
        "sourceSha256": digest(args.input),
        "output": str(args.output.resolve()),
        "outputSha256": digest(args.output),
        "sourceMode": source_mode,
        "alphaBBox": list(alpha.getbbox() or ()),
        "neutralMinimum": args.minimum,
        "neutralSpread": args.spread,
        "foregroundPolicy": "border-connected neutral removal, enclosed foreground restoration, fragment rejection, and one-pixel conservative foreground expansion",
        "restoredEnclosedHolePixels": restored_hole_pixels,
        "removedFragmentPixels": removed_fragment_pixels,
        "minimumForegroundComponentArea": args.minimum_foreground_component_area,
        "blackPreview": str(black_path.resolve()),
        "whitePreview": str(white_path.resolve()),
        "sceneTonePreview": str(scene_tone_path.resolve()),
        "edgeRgbAudit": edge_audit,
        "maxNeutralEdgeRatio": args.max_neutral_edge_ratio,
        "failures": failures,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("MATTE_TECHNICAL_FILE_FAIL: " + "; ".join(failures))
    print("CONSERVATIVE_MATTE_TECHNICAL_FILE_PASS")


if __name__ == "__main__":
    main()
