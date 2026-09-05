#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def parse_size(value: str) -> tuple[int, int]:
    normalized = value.lower().replace("×", "x")
    parts = normalized.split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Expected WIDTHxHEIGHT")
    width, height = (int(part) for part in parts)
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Width and height must be positive")
    return width, height


def parse_pair(value: str) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Expected X,Y")
    return int(parts[0]), int(parts[1])


def parse_rect(value: str) -> tuple[int, int, int, int]:
    parts = value.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("Expected X,Y,WIDTH,HEIGHT")
    x, y, width, height = (int(part) for part in parts)
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Rectangle must be non-negative with positive size")
    return x, y, width, height


def parse_named_state(value: str) -> tuple[str, Path]:
    name, separator, source = value.partition("=")
    if not separator or not name or not source:
        raise argparse.ArgumentTypeError("Expected STATE=PATH")
    if any(not (character.isalnum() or character in "_-") for character in name):
        raise argparse.ArgumentTypeError(
            "State names may contain only letters, digits, underscores, and hyphens"
        )
    return name, Path(source)


def flat_pixels(image: Image.Image) -> list[tuple[int, ...]]:
    getter = getattr(image, "get_flattened_data", None)
    if getter is not None:
        return list(getter())
    return list(image.getdata())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def alpha_corners(image: Image.Image) -> list[int]:
    alpha = image.getchannel("A")
    width, height = image.size
    return [
        alpha.getpixel((0, 0)),
        alpha.getpixel((width - 1, 0)),
        alpha.getpixel((0, height - 1)),
        alpha.getpixel((width - 1, height - 1)),
    ]


def key_functions(key: str) -> tuple[Callable[[int, int, int], bool], Callable[[int, int, int], int]]:
    if key == "green":
        return (
            lambda red, green, blue: green >= 135 and green - red >= 55 and green - blue >= 55,
            lambda red, green, blue: green - max(red, blue),
        )
    return (
        lambda red, green, blue: red >= 135 and blue >= 135 and min(red, blue) - green >= 55,
        lambda red, green, blue: min(red, blue) - green,
    )


def edge_connected_background(image: Image.Image, key: str) -> tuple[bytearray, float]:
    rgb = image.convert("RGB")
    pixels = flat_pixels(rgb)
    width, height = rgb.size
    predicate, _ = key_functions(key)
    candidate = bytearray(int(predicate(red, green, blue)) for red, green, blue in pixels)
    background = bytearray(width * height)
    queue: deque[int] = deque()

    def enqueue(index: int) -> None:
        if candidate[index] and not background[index]:
            background[index] = 1
            queue.append(index)

    for x in range(width):
        enqueue(x)
        enqueue((height - 1) * width + x)
    for y in range(height):
        enqueue(y * width)
        enqueue(y * width + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width
        y = index // width
        if x > 0:
            enqueue(index - 1)
        if x + 1 < width:
            enqueue(index + 1)
        if y > 0:
            enqueue(index - width)
        if y + 1 < height:
            enqueue(index + width)

    coverage = sum(background) / float(width * height)
    if coverage < 0.15 or coverage > 0.99:
        raise ValueError(f"Implausible edge-connected {key} coverage: {coverage:.4f}")
    return background, coverage


def despill(red: int, green: int, blue: int, key: str) -> tuple[int, int, int]:
    if key == "green" and green > max(red, blue):
        green = max(red, blue)
    elif key == "magenta" and min(red, blue) > green:
        excess = min(red, blue) - green
        red = max(0, round(red - excess * 0.5))
        blue = max(0, round(blue - excess * 0.5))
    return red, green, blue


def extract_keyed_subject(source_path: Path, key: str) -> tuple[Image.Image, dict[str, object]]:
    source = Image.open(source_path).convert("RGBA")
    rgb_pixels = flat_pixels(source.convert("RGB"))
    width, height = source.size
    background, coverage = edge_connected_background(source, key)
    _, dominance = key_functions(key)

    background_image = Image.frombytes(
        "L", source.size, bytes(255 if value else 0 for value in background)
    )
    near_background = flat_pixels(background_image.filter(ImageFilter.MaxFilter(5)))
    output_pixels: list[tuple[int, int, int, int]] = []

    for index, (red, green, blue) in enumerate(rgb_pixels):
        if background[index]:
            alpha_value = 0
        elif near_background[index]:
            score = dominance(red, green, blue)
            alpha_value = max(0, min(255, round(255 - max(0, score - 15) * 1.35)))
        else:
            alpha_value = 255

        if alpha_value == 0:
            output_pixels.append((0, 0, 0, 0))
        else:
            red, green, blue = despill(red, green, blue, key)
            output_pixels.append((red, green, blue, alpha_value))

    output = Image.new("RGBA", source.size)
    output.putdata(output_pixels)
    bbox = output.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError(f"No opaque subject found in {source_path}")
    if bbox[0] == 0 or bbox[1] == 0 or bbox[2] == width or bbox[3] == height:
        raise ValueError(f"Subject touches a source edge in {source_path}; regenerate with more margin")

    return output, {
        "source": str(source_path.resolve()),
        "source_size": [width, height],
        "source_alpha_bbox": list(bbox),
        "key": key,
        "edge_connected_key_coverage": round(coverage, 6),
    }


def shift_to_anchor(
    subject: Image.Image,
    canvas_size: tuple[int, int],
    visible_height: int,
    foot: tuple[int, int],
) -> Image.Image:
    bbox = subject.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("Subject has no alpha bounds")
    cropped = subject.crop(bbox)
    scale = visible_height / float(cropped.height)
    resized_width = max(1, round(cropped.width * scale))
    resized = cropped.resize((resized_width, visible_height), Image.Resampling.LANCZOS)

    canvas_width, canvas_height = canvas_size
    foot_x, foot_y = foot
    x = round(foot_x - resized_width / 2.0)
    y = foot_y - visible_height
    if x < 0 or y < 0 or x + resized_width > canvas_width or foot_y > canvas_height:
        raise ValueError(
            f"Packaged subject does not fit canvas {canvas_size}: "
            f"subject={resized_width}x{visible_height}, origin=({x},{y}), foot={foot}"
        )

    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    canvas.alpha_composite(resized, (x, y))
    current_bbox = canvas.getchannel("A").getbbox()
    if current_bbox is None:
        raise ValueError("Packaged subject has no alpha bounds")

    delta_x = foot_x - round((current_bbox[0] + current_bbox[2]) / 2.0)
    delta_y = foot_y - current_bbox[3]
    if delta_x or delta_y:
        shifted = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        shifted.alpha_composite(canvas, (delta_x, delta_y))
        canvas = shifted

    final_bbox = canvas.getchannel("A").getbbox()
    if final_bbox is None or final_bbox[3] != foot_y:
        raise ValueError(f"Failed to align foot line: bbox={final_bbox}, requested={foot_y}")
    return canvas


def make_shadow(
    canvas_size: tuple[int, int],
    foot: tuple[int, int],
    subject_bbox: tuple[int, int, int, int],
    direction: str,
) -> Image.Image:
    width, _ = canvas_size
    foot_x, foot_y = foot
    subject_width = subject_bbox[2] - subject_bbox[0]
    shadow = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    half_contact = max(16, round(subject_width * 0.38))
    draw.ellipse(
        (foot_x - half_contact, foot_y - 20, foot_x + half_contact, foot_y + 7),
        fill=(0, 0, 0, 68),
    )
    if direction != "none":
        sign = -1 if direction == "left" else 1
        tip_x = max(0, min(width - 1, foot_x + sign * round(subject_width * 0.9)))
        draw.polygon(
            (
                (foot_x - half_contact // 2, foot_y - 10),
                (foot_x + half_contact // 2, foot_y - 4),
                (tip_x, foot_y - 46),
                (tip_x, foot_y - 28),
            ),
            fill=(0, 0, 0, 42),
        )
    return shadow.filter(ImageFilter.GaussianBlur(7))


def save_qa(sprite: Image.Image, output_dir: Path, prefix: str, state: str) -> list[str]:
    paths: list[str] = []
    for label, color in (("dark", (8, 8, 8, 255)), ("light", (235, 220, 230, 255))):
        qa = Image.new("RGBA", sprite.size, color)
        qa.alpha_composite(sprite)
        path = output_dir / f"{prefix}_{state}_qa_{label}.png"
        qa.convert("RGB").save(path)
        paths.append(str(path.resolve()))
    return paths


def bbox_inside(inner: tuple[int, int, int, int] | None, outer: tuple[int, int, int, int]) -> bool:
    if inner is None:
        return False
    return (
        inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def package(args: argparse.Namespace) -> None:
    canvas_size = args.canvas
    canvas_width, canvas_height = canvas_size
    foot_x, foot_y = args.foot
    if not (0 <= foot_x < canvas_width and 0 < foot_y <= canvas_height):
        raise ValueError(f"Foot anchor {args.foot} is outside canvas {canvas_size}")
    if args.visible_height <= 0 or args.visible_height > foot_y:
        raise ValueError("Visible height must be positive and no greater than foot Y")

    if args.named_states:
        if args.idle is not None or args.click is not None:
            raise ValueError("Use either --state entries or the legacy --idle/--click pair, not both")
        state_sources = args.named_states
    else:
        if args.idle is None or args.click is None:
            raise ValueError("Provide at least one --state STATE=PATH or both --idle and --click")
        state_sources = [("idle", args.idle), ("click", args.click)]

    state_names = [name for name, _ in state_sources]
    if len(set(state_names)) != len(state_names):
        raise ValueError(f"Duplicate state names are not allowed: {state_names}")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    states: dict[str, Image.Image] = {}
    manifest: dict[str, object] = {
        "canvas": [canvas_width, canvas_height],
        "visible_height": args.visible_height,
        "foot": [foot_x, foot_y],
        "position": list(args.position) if args.position is not None else None,
        "key": args.key,
        "states": {},
    }

    for state, source_path in state_sources:
        extracted, source_stats = extract_keyed_subject(source_path.resolve(), args.key)
        sprite = shift_to_anchor(extracted, canvas_size, args.visible_height, args.foot)
        output_path = output_dir / f"{args.prefix}_{state}.png"
        sprite.save(output_path)
        bbox = sprite.getchannel("A").getbbox()
        corners = alpha_corners(sprite)
        if corners != [0, 0, 0, 0]:
            raise ValueError(f"{state} sprite corners are not transparent: {corners}")
        states[state] = sprite
        manifest["states"][state] = {
            **source_stats,
            "output": str(output_path.resolve()),
            "output_size": [canvas_width, canvas_height],
            "alpha_bbox": list(bbox) if bbox is not None else None,
            "corner_alpha": corners,
            "sha256": sha256(output_path),
            "qa": save_qa(sprite, output_dir, args.prefix, state),
        }

    state_bboxes = {state: sprite.getchannel("A").getbbox() for state, sprite in states.items()}
    if any(bbox is None for bbox in state_bboxes.values()):
        raise ValueError(f"One or more states have empty alpha bounds: {state_bboxes}")
    foot_lines = {bbox[3] for bbox in state_bboxes.values() if bbox is not None}
    if len(foot_lines) != 1:
        raise ValueError(f"State foot lines do not match: {state_bboxes}")

    first_bbox = next(iter(state_bboxes.values()))
    if first_bbox is None:
        raise ValueError("The first state has empty alpha bounds")

    shadow: Image.Image | None = None
    if args.shadow != "none":
        shadow = make_shadow(canvas_size, args.foot, first_bbox, args.shadow)
        shadow_path = output_dir / f"{args.prefix}_shadow.png"
        shadow.save(shadow_path)
        manifest["shadow"] = {
            "output": str(shadow_path.resolve()),
            "corner_alpha": alpha_corners(shadow),
            "sha256": sha256(shadow_path),
        }

    if args.scene is not None:
        if args.position is None:
            raise ValueError("--position is required when --scene is provided")
        scene = Image.open(args.scene.resolve()).convert("RGBA")
        pos_x, pos_y = args.position
        expected_rect = (pos_x, pos_y, pos_x + canvas_width, pos_y + canvas_height)
        if not bbox_inside(expected_rect, (0, 0, scene.width, scene.height)):
            raise ValueError(f"Sprite rectangle {expected_rect} is outside scene {scene.size}")

        previews: dict[str, object] = {}
        for state, sprite in states.items():
            preview = scene.copy()
            if shadow is not None:
                preview.alpha_composite(shadow, args.position)
            preview.alpha_composite(sprite, args.position)
            preview_path = output_dir / f"{args.prefix}_{state}_full_scene_preview.png"
            preview.save(preview_path)
            diff_bbox = ImageChops.difference(scene.convert("RGB"), preview.convert("RGB")).getbbox()
            if not bbox_inside(diff_bbox, expected_rect):
                raise ValueError(
                    f"{state} preview changed pixels outside {expected_rect}: diff={diff_bbox}"
                )
            previews[state] = {
                "output": str(preview_path.resolve()),
                "scene_size": list(scene.size),
                "rgb_diff_bbox": list(diff_bbox) if diff_bbox is not None else None,
                "diff_inside_sprite_rect": True,
                "sha256": sha256(preview_path),
            }
        manifest["scene"] = {
            "source": str(args.scene.resolve()),
            "source_size": list(scene.size),
            "sprite_rect": list(expected_rect),
            "previews": previews,
        }

    manifest_path = output_dir / f"{args.prefix}_package_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), **manifest}, ensure_ascii=False, indent=2))


def crop_scene(args: argparse.Namespace) -> None:
    scene = Image.open(args.scene.resolve()).convert("RGBA")
    x, y, width, height = args.rect
    if x + width > scene.width or y + height > scene.height:
        raise ValueError(f"Crop {args.rect} is outside scene {scene.size}")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.crop((x, y, x + width, y + height)).save(output)
    print(
        json.dumps(
            {
                "source": str(args.scene.resolve()),
                "source_size": list(scene.size),
                "rect": list(args.rect),
                "output": str(output),
                "output_size": [width, height],
                "sha256": sha256(output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Crop NDC scenes and package aligned transparent character states."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    crop_parser = subparsers.add_parser("crop", help="Create an exact working crop")
    crop_parser.add_argument("--scene", type=Path, required=True)
    crop_parser.add_argument("--rect", type=parse_rect, required=True)
    crop_parser.add_argument("--output", type=Path, required=True)
    crop_parser.set_defaults(handler=crop_scene)

    package_parser = subparsers.add_parser(
        "package", help="Extract and align legacy idle/click or named character states"
    )
    package_parser.add_argument("--idle", type=Path, help="Legacy idle solid-key source")
    package_parser.add_argument("--click", type=Path, help="Legacy click solid-key source")
    package_parser.add_argument(
        "--state",
        dest="named_states",
        action="append",
        type=parse_named_state,
        default=[],
        metavar="STATE=PATH",
        help="Named solid-key source; repeat for AVG entrance/action states",
    )
    package_parser.add_argument("--scene", type=Path, help="Untouched full scene for previews")
    package_parser.add_argument("--output-dir", type=Path, required=True)
    package_parser.add_argument("--prefix", required=True)
    package_parser.add_argument("--canvas", type=parse_size, required=True)
    package_parser.add_argument("--visible-height", type=int, required=True)
    package_parser.add_argument("--foot", type=parse_pair, required=True)
    package_parser.add_argument("--position", type=parse_pair)
    package_parser.add_argument("--key", choices=("green", "magenta"), default="green")
    package_parser.add_argument("--shadow", choices=("none", "left", "right"), default="none")
    package_parser.set_defaults(handler=package)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
