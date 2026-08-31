from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_hospital_social_service_day.png")
JOB = ROOT / "00_4216_scene_insert"
CROP_RECT = (1024, 32, 3072, 1568)
INTENT_FULL = (1660, 350, 2260, 730)
AUTH_FULL = (1100, 120, 2900, 1260)


def local(rect):
    return (
        rect[0] - CROP_RECT[0], rect[1] - CROP_RECT[1],
        rect[2] - CROP_RECT[0], rect[3] - CROP_RECT[1],
    )


def main():
    JOB.mkdir(parents=True, exist_ok=True)
    (ROOT / "scripts").mkdir(parents=True, exist_ok=True)
    (ROOT / "masks").mkdir(parents=True, exist_ok=True)
    (ROOT / "review").mkdir(parents=True, exist_ok=True)
    (ROOT / "map_stage" / "4216").mkdir(parents=True, exist_ok=True)
    (ROOT / "detail" / "4216" / "generated").mkdir(parents=True, exist_ok=True)
    (ROOT / "detail" / "4216" / "master").mkdir(parents=True, exist_ok=True)
    (ROOT / "detail" / "4216" / "text").mkdir(parents=True, exist_ok=True)
    (ROOT / "detail" / "4216" / "final").mkdir(parents=True, exist_ok=True)
    (ROOT / "detail" / "4216" / "review").mkdir(parents=True, exist_ok=True)
    (ROOT / "delivery" / "4216").mkdir(parents=True, exist_ok=True)

    source = Image.open(SOURCE).convert("RGBA")
    crop = source.crop(CROP_RECT)
    crop.save(JOB / "source_crop.png")
    auth, intent = local(AUTH_FULL), local(INTENT_FULL)
    hard = Image.new("L", crop.size, 0)
    ImageDraw.Draw(hard).rectangle((auth[0], auth[1], auth[2] - 1, auth[3] - 1), fill=255)
    hard.save(JOB / "authorization_mask_hard.png")
    hard.filter(ImageFilter.GaussianBlur(5)).save(JOB / "authorization_mask_feather5.png")
    full_hard = Image.new("L", source.size, 0)
    full_hard.paste(hard, CROP_RECT[:2])
    full_hard.save(JOB / "authorization_mask_full_scene_hard.png")
    layer = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((auth[0], auth[1], auth[2] - 1, auth[3] - 1), outline=(0, 205, 255, 255), width=8)
    d.rectangle((intent[0], intent[1], intent[2] - 1, intent[3] - 1), outline=(255, 210, 0, 255), width=7)
    Image.alpha_composite(crop, layer).save(JOB / "authorization_and_intent_overlay.png")
    source.crop((1450, 220, 2450, 900)).save(ROOT / "review" / "SC4012_existing_display_wall_crop.png")


if __name__ == "__main__":
    main()
