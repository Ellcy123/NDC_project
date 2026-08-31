import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
DETAIL = ROOT / "detail" / "4115"
GREEN_SOURCE = DETAIL / "generated" / "4115_dense_ledger_green_attempt_2.png"
FONT = "/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chroma_key(image):
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    score = g - np.maximum(r, b)
    alpha = np.where(g > 90, np.clip((58.0 - score) * 8.0, 0, 255), 255)
    alpha = np.asarray(
        Image.fromarray(alpha.astype(np.uint8), "L").filter(ImageFilter.MinFilter(5)),
        dtype=np.uint8,
    )
    # Remove green spill from antialiased edge pixels without changing the body.
    spill = (alpha > 0) & (alpha < 255)
    arr[..., 1][spill] = np.minimum(arr[..., 1][spill], np.maximum(r[spill], b[spill]) + 8)
    eroded = np.asarray(
        Image.fromarray(alpha, "L").filter(ImageFilter.MinFilter(13)),
        dtype=np.uint8,
    )
    edge = (alpha > eroded) & (alpha > 0)
    edge_green = edge & (arr[..., 1] > np.maximum(arr[..., 0], arr[..., 2]) + 10)
    arr[..., 1][edge_green] = np.maximum(arr[..., 0], arr[..., 2])[edge_green] + 4
    rgba = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(rgba, "RGBA")


def fit_text(draw, text, box, max_size=22, min_size=12):
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(FONT, size)
        bb = draw.textbbox((0, 0), text, font=font)
        if bb[2] - bb[0] <= box[2] - box[0]:
            return font
    return ImageFont.truetype(FONT, min_size)


def center_text(draw, text, box, font, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    x = box[0] + ((box[2] - box[0]) - (bb[2] - bb[0])) // 2
    y = box[1] + ((box[3] - box[1]) - (bb[3] - bb[1])) // 2 - bb[1]
    draw.text((x, y), text, font=font, fill=fill)


def build_exact_text_layer(size):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = (61, 49, 37, 210)
    light_ink = (68, 55, 41, 175)
    title_font = ImageFont.truetype(FONT, 24)
    head_font = ImageFont.truetype(FONT, 15)

    pages = [(112, 232, 604, 1010), (650, 232, 1135, 1010)]
    for page in pages:
        center_text(d, "COURTHOUSE CASE INDEX", (page[0], 205, page[2], 237), title_font, ink)
        y = 245
        columns = [
            (page[0] + 8, page[0] + 133, "CASE NO."),
            (page[0] + 133, page[0] + 270, "CHECKED OUT"),
            (page[0] + 270, page[0] + 388, "RETURNED"),
            (page[0] + 388, page[2] - 6, "CLERK"),
        ]
        for left, right, label in columns:
            center_text(d, label, (left, y, right, y + 28), head_font, light_ink)
        d.line((page[0] + 6, y + 31, page[2] - 6, y + 31), fill=(61, 49, 37, 120), width=2)

    groups = [
        ((128, 451, 590, 491), "SACRED HEART PROGRAM DISPUTES — 7"),
        ((128, 685, 590, 725), "SOUTH SIDE PROPERTY RULINGS — 3"),
        ((667, 451, 1120, 491), "OLD COMPENSATION RULINGS — 7"),
    ]
    for box, text in groups:
        font = fit_text(d, text, box, max_size=22, min_size=14)
        center_text(d, text, box, font, ink)
        d.line((box[0] + 4, box[3] + 4, box[2] - 4, box[3] + 4), fill=(61, 49, 37, 135), width=2)
    return layer


def build_icon_master(semantic):
    alpha = semantic.getchannel("A")
    bbox = alpha.getbbox()
    subject = semantic.crop(bbox)
    subject.thumbnail((820, 650), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (1040, 1040), (0, 0, 0, 0))
    x = (1040 - subject.width) // 2
    y = (1040 - subject.height) // 2 - 20
    subject_mask = Image.new("L", canvas.size, 0)
    subject_mask.paste(subject.getchannel("A"), (x, y))

    shadow_mask = Image.new("L", canvas.size, 0)
    shadow_mask.paste(subject.getchannel("A"), (x - 16, y + 24))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(10)).point(lambda p: int(p * 0.20))
    shadow = Image.new("RGBA", canvas.size, (22, 18, 14, 0))
    shadow.putalpha(shadow_mask)
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.alpha_composite(subject, (x, y))
    return canvas, subject_mask, shadow_mask


def main():
    blank = chroma_key(Image.open(GREEN_SOURCE))
    blank_path = DETAIL / "master" / "4115_blank_ledger_transparent.png"
    blank.save(blank_path)
    text_layer = build_exact_text_layer(blank.size)
    text_path = DETAIL / "text" / "4115_exact_index_text_layer.png"
    text_layer.save(text_path)
    semantic = Image.alpha_composite(blank, text_layer)
    semantic.putalpha(blank.getchannel("A"))
    semantic_path = DETAIL / "master" / "4115_semantic_master_with_exact_index.png"
    semantic.save(semantic_path)

    icon_master, subject_mask, shadow_mask = build_icon_master(semantic)
    icon_master_path = DETAIL / "master" / "4115_icon_master_1040.png"
    subject_path = DETAIL / "master" / "4115_icon_subject_mask_1040.png"
    shadow_path = DETAIL / "master" / "4115_icon_shadow_mask_1040.png"
    icon_master.save(icon_master_path)
    subject_mask.save(subject_path)
    shadow_mask.save(shadow_path)

    provenance = {
        "item_id": "4115",
        "physical_master_source": str(GREEN_SOURCE),
        "physical_master_source_sha256": sha256(GREEN_SOURCE),
        "transparent_blank_master": str(blank_path),
        "transparent_blank_master_sha256": sha256(blank_path),
        "exact_text_layer": str(text_path),
        "exact_text_layer_sha256": sha256(text_path),
        "semantic_master": str(semantic_path),
        "semantic_master_sha256": sha256(semantic_path),
        "exact_locked_facts": [
            "CASE NO.", "CHECKED OUT", "RETURNED", "CLERK",
            "SACRED HEART PROGRAM DISPUTES — 7",
            "SOUTH SIDE PROPERTY RULINGS — 3",
            "OLD COMPENSATION RULINGS — 7",
        ],
        "spoiler_exclusions": [
            "CHILD", "DEATH", "patient names", "diseases", "TOTAL 17", "7+3+7", "Harrison-signed conclusion"
        ],
    }
    (DETAIL / "4115_detail_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
