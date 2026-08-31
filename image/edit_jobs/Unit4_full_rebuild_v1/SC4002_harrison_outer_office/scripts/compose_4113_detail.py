import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DETAIL = ROOT / "detail" / "4113"
MASTER_DIR = DETAIL / "master"
TEXT_DIR = DETAIL / "text"
FINAL_DIR = DETAIL / "final"
BLANK = MASTER_DIR / "4113_blank_paper_attempt2_cleanup.png"
FONT = Path("/System/Library/Fonts/Supplemental/Courier New.ttf")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def draw_typewriter_layer(size):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    body_font = ImageFont.truetype(str(FONT), 29)
    small_font = ImageFont.truetype(str(FONT), 26)
    title_font = ImageFont.truetype(str(FONT), 32)
    ink = (31, 34, 31, 224)

    draw.text((568, 196), "November 27, 1928", font=small_font, fill=ink)
    draw.text((218, 266), "DRAFT - RESIGNATION", font=title_font, fill=(28, 31, 29, 230))

    lines = [
        "To the Chief Justice:",
        "",
        "I can no longer continue in office without",
        "accounting for the rulings I issued and the",
        "payments I accepted.",
        "",
        "We cannot demand that others confess while",
        "continuing to deny our own part.",
        "",
        "I intend to make these records public...",
    ]
    x_jitter = [0, 1, -1, 0, 2, 0, -1, 1, 0, -1]
    y = 358
    for i, line in enumerate(lines):
        if line:
            opacity = 216 if i in (2, 6, 9) else 224
            draw.text((174 + x_jitter[i], y), line, font=body_font, fill=(31, 34, 31, opacity))
        y += 52

    draw.text((532, 1092), "Respectfully,", font=small_font, fill=(31, 34, 31, 214))
    draw.text((532, 1144), "________________________", font=small_font, fill=(31, 34, 31, 205))
    return layer


def make_icon_master(subject):
    bbox = subject.getbbox()
    cropped = subject.crop(bbox)
    max_h = 800
    max_w = 620
    scale = min(max_w / cropped.width, max_h / cropped.height)
    resized = cropped.resize((round(cropped.width * scale), round(cropped.height * scale)), Image.Resampling.LANCZOS)
    rotated = resized.rotate(-8, resample=Image.Resampling.BICUBIC, expand=True)

    subject_canvas = Image.new("RGBA", (1040, 1040), (0, 0, 0, 0))
    x = round(520 - rotated.width / 2)
    y = round(500 - rotated.height / 2)
    subject_canvas.alpha_composite(rotated, (x, y))
    subject_mask = subject_canvas.getchannel("A")

    shadow_mask = subject_mask.filter(ImageFilter.GaussianBlur(10))
    shifted = Image.new("L", (1040, 1040), 0)
    shifted.paste(shadow_mask, (-20, 24))
    shadow_mask = shifted.point(lambda p: round(p * 0.30))
    shadow_rgba = Image.new("RGBA", (1040, 1040), (28, 24, 20, 0))
    shadow_rgba.putalpha(shadow_mask)
    combined = Image.alpha_composite(shadow_rgba, subject_canvas)
    return combined, subject_mask, shadow_mask


def main():
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    blank = Image.open(BLANK).convert("RGBA")
    text_layer = draw_typewriter_layer(blank.size)
    clipped_alpha = ImageChops.multiply(text_layer.getchannel("A"), blank.getchannel("A"))
    text_layer.putalpha(clipped_alpha)

    text_path = TEXT_DIR / "4113_exact_typewriter_text_layer.png"
    master_path = MASTER_DIR / "4113_semantic_master_with_exact_text.png"
    text_layer.save(text_path)
    master = Image.alpha_composite(blank, text_layer)
    master.save(master_path)

    combined, subject_mask, shadow_mask = make_icon_master(master)
    combined_path = MASTER_DIR / "4113_icon_master_1040.png"
    subject_mask_path = MASTER_DIR / "4113_icon_subject_mask_1040.png"
    shadow_mask_path = MASTER_DIR / "4113_icon_shadow_mask_1040.png"
    combined.save(combined_path)
    subject_mask.save(subject_mask_path)
    shadow_mask.save(shadow_mask_path)

    provenance = {
        "itemId": "4113",
        "authoringMode": "built-in image generation blank physical master plus deterministic approved exact-text layer",
        "blankMaster": {"path": str(BLANK.relative_to(ROOT)), "sha256": sha256(BLANK)},
        "exactTextLayer": {"path": str(text_path.relative_to(ROOT)), "sha256": sha256(text_path)},
        "semanticMaster": {"path": str(master_path.relative_to(ROOT)), "sha256": sha256(master_path)},
        "font": str(FONT),
        "requiredText": [
            "November 27, 1928",
            "We cannot demand that others confess while continuing to deny our own part.",
            "I intend to make these records public..."
        ],
        "signature": "blank line only",
        "iconMaster": {"path": str(combined_path.relative_to(ROOT)), "sha256": sha256(combined_path)}
    }
    with open(DETAIL / "4113_detail_provenance.json", "w", encoding="utf-8") as f:
        json.dump(provenance, f, ensure_ascii=False, indent=2)
    print(json.dumps(provenance, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
