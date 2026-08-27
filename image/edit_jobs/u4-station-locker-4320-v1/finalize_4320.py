from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
MASTER_PATH = ROOT / "detail" / "SC4026_item_4320_semantic_master.png"
DETAIL_DIR = ROOT / "detail"
TYPE7_PATH = ROOT / "type7" / "prop_station_locker_214_2.png"


def font_path(name: str) -> Path:
    path = Path("C:/Windows/Fonts") / name
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def rotate_text(text: str, font: ImageFont.FreeTypeFont, angle: float) -> Image.Image:
    bbox = font.getbbox(text, stroke_width=1)
    width = bbox[2] - bbox[0] + 18
    height = bbox[3] - bbox[1] + 18
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(
        (9 - bbox[0], 9 - bbox[1]),
        text,
        font=font,
        fill=(43, 35, 27, 235),
        stroke_width=1,
        stroke_fill=(83, 67, 48, 125),
    )
    return layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def extract_master() -> tuple[Image.Image, Image.Image]:
    rgb = Image.open(MASTER_PATH).convert("RGB")
    arr = np.asarray(rgb, dtype=np.int16)
    spread = arr.max(axis=2) - arr.min(axis=2)
    value = arr.max(axis=2)

    # Image generation returned a baked light checkerboard. The approved prop is
    # brown/cream and materially distinct, so a conservative material mask
    # removes only near-neutral bright squares while keeping paper and shadow.
    foreground = (spread >= 10).astype(np.uint8) * 255
    hard_mask = Image.fromarray(foreground, mode="L")
    hard_mask = hard_mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    foreground = np.asarray(hard_mask, dtype=np.uint8)
    softened = np.asarray(hard_mask.filter(ImageFilter.GaussianBlur(1.1)), dtype=np.uint16)
    # Feather inward only. Never assign alpha to the baked checkerboard outside
    # the confidently detected physical master; this prevents a white fringe.
    inward = (softened * (foreground.astype(np.uint16) // 255)).astype(np.uint8)
    mask = Image.fromarray(inward, mode="L")

    rgba = rgb.convert("RGBA")
    rgba.putalpha(mask)

    exact = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    title_font = ImageFont.truetype(str(font_path("courbd.ttf")), 42)
    body_font = ImageFont.truetype(str(font_path("segoesc.ttf")), 36)
    sign_font = ImageFont.truetype(str(font_path("segoesc.ttf")), 40)

    exact.alpha_composite(rotate_text("FOR ZACK BRENNAN", title_font, 4), (238, 170))
    body_lines = [
        ("Pierce and Whale", (680, 235)),
        ("buried the old cases.", (690, 290)),
        ("I was ordered to", (704, 375)),
        ("surrender my files.", (710, 430)),
        ("Do not call this suicide.", (725, 540)),
    ]
    for text, xy in body_lines:
        exact.alpha_composite(rotate_text(text, body_font, 4), xy)
    exact.alpha_composite(rotate_text("Harold Morrison", sign_font, 4), (915, 700))

    rgba = Image.alpha_composite(rgba, exact)
    rgba_arr = np.asarray(rgba).copy()
    rgba_arr[rgba_arr[:, :, 3] == 0, :3] = 0
    rgba = Image.fromarray(rgba_arr, mode="RGBA")
    return rgba, exact


def make_icon_master(detail: Image.Image) -> tuple[Image.Image, Image.Image, Image.Image]:
    alpha_bbox = detail.getchannel("A").getbbox()
    if alpha_bbox is None:
        raise RuntimeError("detail master has no visible pixels")
    subject = detail.crop(alpha_bbox)
    subject.thumbnail((800, 570), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (1040, 1040), (0, 0, 0, 0))
    subject_mask = Image.new("L", canvas.size, 0)
    x = (1040 - subject.width) // 2
    y = (1040 - subject.height) // 2 - 10
    canvas.alpha_composite(subject, (x, y))
    subject_mask.paste(subject.getchannel("A"), (x, y))

    # Standard NDC short left-down shadow. It is derived from the approved
    # subject silhouette and remains a separate mask for verification.
    shadow_mask = subject_mask.filter(ImageFilter.GaussianBlur(10))
    shifted = Image.new("L", canvas.size, 0)
    shifted.paste(shadow_mask, (-16, 20))
    shadow_rgba = Image.new("RGBA", canvas.size, (15, 12, 9, 0))
    shadow_rgba.putalpha(shifted.point(lambda p: round(p * 0.34)))
    combined = Image.alpha_composite(shadow_rgba, canvas)
    return combined, subject_mask, shifted


def export_child_map() -> None:
    type7 = Image.open(TYPE7_PATH)
    rect = (41, 423, 193, 514)
    type7.crop(rect).save(ROOT / "delivery" / "SC4026_item_4320.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if not args.prepare:
        parser.error("use --prepare")

    DETAIL_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "delivery").mkdir(parents=True, exist_ok=True)

    detail, exact = extract_master()
    detail.save(DETAIL_DIR / "SC4026_item_4320_exact_master.png")
    exact.save(DETAIL_DIR / "SC4026_item_4320_exact_text_layer.png")

    icon, subject_mask, shadow_mask = make_icon_master(detail)
    icon.save(DETAIL_DIR / "SC4026_item_4320_icon_master_1040.png")
    subject_mask.save(DETAIL_DIR / "SC4026_item_4320_icon_subject_mask_1040.png")
    shadow_mask.save(DETAIL_DIR / "SC4026_item_4320_icon_shadow_mask_1040.png")
    export_child_map()


if __name__ == "__main__":
    main()
