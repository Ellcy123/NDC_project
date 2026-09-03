#!/usr/bin/env python3
"""Create normalized same-expression green/transparent comparison sheets."""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def subject_rgba(path: Path, profile: str) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if profile == "greenscreen":
        rgb = image.load()
        alpha = Image.new("L", image.size, 0)
        out = alpha.load()
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, _ = rgb[x, y]
                if (r, g, b) != (0, 255, 43):
                    out[x, y] = 255
        image.putalpha(alpha)
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        raise ValueError(f"No subject in {path}")
    return image.crop(bbox)


def fit_subject(subject: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = min(width / subject.width, height / subject.height)
    resized = subject.resize((round(subject.width * scale), round(subject.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (38, 38, 38, 255))
    canvas.alpha_composite(resized, ((width - resized.width) // 2, height - resized.height))
    return canvas.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--greenscreen-dir", required=True)
    parser.add_argument("--transparent-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    green_dir = Path(args.greenscreen_dir).resolve()
    transparent_dir = Path(args.transparent_dir).resolve()
    output = Path(args.output).resolve()
    green = {p.name: p for p in green_dir.glob("*.png")}
    transparent = {p.name: p for p in transparent_dir.glob("*.png")}
    names = sorted(set(green) & set(transparent))
    if not names:
        raise SystemExit("No same-name PNG pairs")
    cell_w, cell_h, label_h = 360, 300, 34
    sheet = Image.new("RGB", (cell_w * 2, (cell_h + label_h) * len(names)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for row, name in enumerate(names):
        y = row * (cell_h + label_h)
        sheet.paste(fit_subject(subject_rgba(green[name], "greenscreen"), (cell_w, cell_h)), (0, y))
        sheet.paste(fit_subject(subject_rgba(transparent[name], "transparent"), (cell_w, cell_h)), (cell_w, y))
        draw.text((8, y + cell_h + 8), f"GREEN | {name}", fill="black", font=font)
        draw.text((cell_w + 8, y + cell_h + 8), f"TRANSPARENT | {name}", fill="black", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output)


if __name__ == "__main__":
    main()
