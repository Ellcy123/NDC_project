from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01_4115_scene_insert" / "accepted_4115_scene.png"
JOB = ROOT / "02_4116_scene_insert"
CROP_RECT = (896, 400, 1920, 1424)
INTENT_FULL = (1280, 850, 1550, 950)
AUTH_FULL = (1010, 750, 1820, 1050)


def local(rect):
    return (
        rect[0] - CROP_RECT[0], rect[1] - CROP_RECT[1],
        rect[2] - CROP_RECT[0], rect[3] - CROP_RECT[1],
    )


def main():
    JOB.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    crop = source.crop(CROP_RECT)
    crop.save(JOB / "source_crop.png")
    auth = local(AUTH_FULL)
    intent = local(INTENT_FULL)
    hard = Image.new("L", crop.size, 0)
    ImageDraw.Draw(hard).rectangle((auth[0], auth[1], auth[2] - 1, auth[3] - 1), fill=255)
    hard.save(JOB / "authorization_mask_hard.png")
    hard.filter(ImageFilter.GaussianBlur(5)).save(JOB / "authorization_mask_feather5.png")
    layer = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((auth[0], auth[1], auth[2] - 1, auth[3] - 1), outline=(0, 205, 255, 255), width=8)
    d.rectangle((intent[0], intent[1], intent[2] - 1, intent[3] - 1), outline=(255, 75, 140, 255), width=7)
    Image.alpha_composite(crop, layer).save(JOB / "authorization_and_intent_overlay.png")


if __name__ == "__main__":
    main()
