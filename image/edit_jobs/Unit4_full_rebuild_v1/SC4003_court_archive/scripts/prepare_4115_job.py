from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "00_cart_support" / "accepted_cart_scene.png"
JOB = ROOT / "01_4115_scene_insert"
CROP_RECT = (1056, 64, 2592, 1600)
INTENT_FULL = (1660, 800, 2070, 940)
AUTH_FULL = (1250, 650, 2480, 1070)


def main():
    JOB.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    crop = source.crop(CROP_RECT)
    crop.save(JOB / "source_crop.png")
    local = tuple(v - CROP_RECT[i % 2] for i, v in enumerate(AUTH_FULL))
    intent = tuple(v - CROP_RECT[i % 2] for i, v in enumerate(INTENT_FULL))
    hard = Image.new("L", crop.size, 0)
    ImageDraw.Draw(hard).rectangle((local[0], local[1], local[2] - 1, local[3] - 1), fill=255)
    hard.save(JOB / "authorization_mask_hard.png")
    hard.filter(ImageFilter.GaussianBlur(5)).save(JOB / "authorization_mask_feather5.png")
    full_hard = Image.new("L", source.size, 0)
    full_hard.paste(hard, CROP_RECT[:2])
    full_hard.save(JOB / "authorization_mask_full_scene_hard.png")
    overlay = crop.copy()
    layer = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((local[0], local[1], local[2] - 1, local[3] - 1), outline=(0, 205, 255, 255), width=8)
    d.rectangle((intent[0], intent[1], intent[2] - 1, intent[3] - 1), outline=(255, 210, 0, 255), width=7)
    Image.alpha_composite(overlay, layer).save(JOB / "authorization_and_intent_overlay.png")


if __name__ == "__main__":
    main()
