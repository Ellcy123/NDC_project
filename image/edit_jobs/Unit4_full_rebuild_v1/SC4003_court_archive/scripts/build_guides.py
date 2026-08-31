from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_court_archive_day.png")
MASKS = ROOT / "masks"
REVIEW = ROOT / "review"


def rect_mask(size, rect, path):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=255)
    mask.save(path)


def main():
    MASKS.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    jobs = [
        ("file cart support", (1210, 760, 1510, 1130), (0, 205, 255, 255)),
        ("4115 ledger intent", (1660, 800, 2070, 940), (255, 210, 0, 255)),
        ("4116 letters intent", (1250, 740, 1470, 900), (255, 75, 140, 255)),
    ]
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for label, rect, color in jobs:
        stem = label.replace(" ", "_")
        rect_mask(source.size, rect, MASKS / f"{stem}.png")
        draw.rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=color[:3] + (55,), outline=color, width=5)
        draw.text((rect[0] + 8, rect[1] + 8), label, fill=color)
    Image.alpha_composite(source, layer).save(REVIEW / "SC4003_planned_intent_overlay.png")
    source.crop((930, 600, 2240, 1250)).save(REVIEW / "SC4003_work_area_crop.png")


if __name__ == "__main__":
    main()
