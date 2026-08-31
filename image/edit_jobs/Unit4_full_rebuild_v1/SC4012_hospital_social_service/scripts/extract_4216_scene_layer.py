import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_hospital_social_service_day.png")
JOB = ROOT / "00_4216_scene_insert"
CROP_RECT = (1024, 32, 3072, 1568)
BOARD_LOCAL = (666, 310, 1230, 688)
BOARD_FULL_ORIGIN = (CROP_RECT[0] + BOARD_LOCAL[0], CROP_RECT[1] + BOARD_LOCAL[1])
FONT = "/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_font(draw, text, width, max_size=18, min_size=10):
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(FONT, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= width:
            return font
    return ImageFont.truetype(FONT, min_size)


def main():
    source = Image.open(SOURCE).convert("RGB")
    source_rgba = source.convert("RGBA")
    source_crop = source_rgba.crop(CROP_RECT)
    registered = Image.open(JOB / "generated_attempt_1_registered.png").convert("RGBA")
    board = registered.crop(BOARD_LOCAL)

    exact = Image.new("RGBA", board.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(exact)
    text = "MILLER ACCIDENT FUND CHARITY PROGRAM"
    font = fit_font(d, text, 440)
    bb = d.textbbox((0, 0), text, font=font)
    x = (board.width - (bb[2] - bb[0])) // 2
    y = 83 - bb[1]
    d.text((x + 1, y + 1), text, font=font, fill=(214, 174, 87, 135))
    d.text((x, y), text, font=font, fill=(45, 35, 20, 245))
    exact_path = ROOT / "detail" / "4216" / "text" / "4216_exact_scene_plaque_text_layer.png"
    exact.save(exact_path)
    board = Image.alpha_composite(board, exact)
    board.save(ROOT / "review" / "4216_board_with_exact_scene_text.png")

    # The full board and its frame are one environmental observation. Wall and
    # counter foreground remain outside the alpha-owned hotspot.
    mask = Image.new("L", board.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((5, 17, 559, 374), radius=5, fill=255)
    md.ellipse((231, -6, 333, 91), fill=255)
    # Existing counter books physically occlude the lower-left board corner.
    md.polygon([(0, 270), (113, 270), (113, 378), (0, 378)], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(0.8))
    mask.save(JOB / "4216_object_alpha_board_crop.png")

    full_mask = Image.new("L", source.size, 0)
    full_mask.paste(mask, BOARD_FULL_ORIGIN)
    full_mask.save(JOB / "4216_object_alpha.png")

    board.putalpha(mask)
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    layer.paste(board, BOARD_FULL_ORIGIN, board)
    layer.save(JOB / "4216_scene_derived_source_layer.png")
    accepted_rgba = Image.alpha_composite(source_rgba, layer)
    accepted = accepted_rgba.convert("RGB")
    accepted_path = JOB / "accepted_4216_scene.png"
    accepted.save(accepted_path)

    auth = Image.open(JOB / "authorization_mask_full_scene_hard.png").convert("L")
    diff = ImageChops.difference(source.convert("RGBA"), accepted.convert("RGBA"))
    outside_auth = Image.composite(Image.new("RGBA", source.size), diff, Image.eval(auth, lambda x: 255 - x))
    bbox = full_mask.getbbox()
    report = {
        "status": "PASS" if outside_auth.getbbox() is None else "FAIL",
        "passed": outside_auth.getbbox() is None,
        "item_id": "4216",
        "route": "environment",
        "source_mode": source.mode,
        "accepted_mode": accepted.mode,
        "source_sha256": sha256(SOURCE),
        "generated_sha256": sha256(JOB / "generated_attempt_1.png"),
        "exact_scene_text_layer_sha256": sha256(exact_path),
        "accepted_sha256": sha256(accepted_path),
        "object_alpha_bbox": list(bbox) if bbox else None,
        "outside_authorization_diff_bbox": outside_auth.getbbox(),
        "hotspot_rule": "Framed plaque/register installation only; wall and foreground counter books excluded.",
    }
    (JOB / "boundary_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
