import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
DETAIL = ROOT / "detail" / "4216"
GREEN_SOURCE = DETAIL / "generated" / "4216_display_wall_green_attempt_1.png"
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
    eroded = np.asarray(
        Image.fromarray(alpha, "L").filter(ImageFilter.MinFilter(13)),
        dtype=np.uint8,
    )
    edge = (alpha > eroded) & (alpha > 0)
    edge_green = edge & (arr[..., 1] > np.maximum(arr[..., 0], arr[..., 2]) + 10)
    arr[..., 1][edge_green] = np.maximum(arr[..., 0], arr[..., 2])[edge_green] + 4
    spill = (alpha > 0) & (alpha < 255)
    arr[..., 1][spill] = np.minimum(arr[..., 1][spill], np.maximum(arr[..., 0], arr[..., 2])[spill] + 8)
    return Image.fromarray(np.dstack([arr.astype(np.uint8), alpha]), "RGBA")


def center(draw, text, box, font, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    x = box[0] + ((box[2] - box[0]) - (bb[2] - bb[0])) // 2
    y = box[1] + ((box[3] - box[1]) - (bb[3] - bb[1])) // 2 - bb[1]
    draw.text((x + 2, y + 2), text, font=font, fill=(215, 174, 88, 115))
    draw.text((x, y), text, font=font, fill=fill)


def main():
    blank = chroma_key(Image.open(GREEN_SOURCE))
    blank_path = DETAIL / "master" / "4216_display_wall_transparent.png"
    blank.save(blank_path)
    exact = Image.new("RGBA", blank.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(exact)
    font1 = ImageFont.truetype(FONT, 31)
    font2 = ImageFont.truetype(FONT, 27)
    ink = (45, 34, 18, 245)
    center(d, "MILLER ACCIDENT FUND", (220, 270, 1035, 309), font1, ink)
    center(d, "CHARITY PROGRAM", (330, 310, 925, 347), font2, ink)
    exact_path = DETAIL / "text" / "4216_exact_plaque_text_layer.png"
    exact.save(exact_path)
    semantic = Image.alpha_composite(blank, exact)
    semantic.putalpha(blank.getchannel("A"))
    semantic_path = DETAIL / "master" / "4216_semantic_master_with_exact_plaque.png"
    semantic.save(semantic_path)
    provenance = {
        "item_id": "4216",
        "item_type": "2/envir",
        "icon_policy": "OMIT",
        "physical_master_source": str(GREEN_SOURCE),
        "physical_master_source_sha256": sha256(GREEN_SOURCE),
        "transparent_master": str(blank_path),
        "transparent_master_sha256": sha256(blank_path),
        "exact_text_layer": str(exact_path),
        "exact_text_layer_sha256": sha256(exact_path),
        "semantic_master": str(semantic_path),
        "semantic_master_sha256": sha256(semantic_path),
        "locked_text": "MILLER ACCIDENT FUND CHARITY PROGRAM",
        "spoiler_exclusions": ["death list", "problem batch", "patient names", "diseases", "fake-charity implication"],
    }
    (DETAIL / "4216_detail_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
