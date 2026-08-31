from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_court_archive_day.png")
JOB = ROOT / "00_cart_support"
CROP_RECT = (768, 320, 2016, 1568)
AUTH_RECT_FULL = (910, 390, 1810, 1500)


def main():
    JOB.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    crop = source.crop(CROP_RECT)
    crop.save(JOB / "source_crop.png")

    local = (
        AUTH_RECT_FULL[0] - CROP_RECT[0],
        AUTH_RECT_FULL[1] - CROP_RECT[1],
        AUTH_RECT_FULL[2] - CROP_RECT[0],
        AUTH_RECT_FULL[3] - CROP_RECT[1],
    )
    hard = Image.new("L", crop.size, 0)
    ImageDraw.Draw(hard).rectangle((local[0], local[1], local[2] - 1, local[3] - 1), fill=255)
    hard.save(JOB / "authorization_mask_hard.png")
    hard.filter(ImageFilter.GaussianBlur(5)).save(JOB / "authorization_mask_feather5.png")

    overlay = crop.copy()
    ink = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ink)
    draw.rectangle((local[0], local[1], local[2] - 1, local[3] - 1), outline=(0, 205, 255, 255), width=8)
    draw.text((local[0] + 12, local[1] + 12), "AUTHORIZED CART REGION", fill=(0, 205, 255, 255))
    Image.alpha_composite(overlay, ink).save(JOB / "authorization_overlay.png")


if __name__ == "__main__":
    main()
