from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_harrison_outer_office_day.png")
MASKS = ROOT / "masks"
REVIEW = ROOT / "review"


def rect_mask(size, rect, path):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=255)
    mask.save(path)


def overlay(source, jobs, path):
    out = source.convert("RGBA")
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for label, rect, color in jobs:
        fill = color[:3] + (55,)
        edge = color[:3] + (255,)
        draw.rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=fill, outline=edge, width=5)
        draw.text((rect[0] + 8, rect[1] + 8), label, fill=edge)
    Image.alpha_composite(out, layer).save(path)


def main():
    MASKS.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGB")
    jobs = [
        ("4112 receipt intent", (525, 590, 675, 710), (255, 210, 0, 255)),
        ("wastebasket support", (2160, 730, 2370, 1040), (0, 205, 255, 255)),
        ("4113 paper intent", (2185, 725, 2340, 925), (255, 75, 140, 255)),
    ]
    for label, rect, _ in jobs:
        stem = label.replace(" ", "_")
        rect_mask(source.size, rect, MASKS / f"{stem}.png")
    rect_mask(source.size, (2070, 790, 2400, 1140), MASKS / "wastebasket_composition.png")
    rect_mask(source.size, (480, 545, 700, 750), MASKS / "4112_receipt_composition.png")
    overlay(source, jobs, REVIEW / "SC4002_planned_intent_overlay.png")
    source.crop((360, 420, 820, 860)).save(REVIEW / "SC4002_4112_target_crop.png")
    source.crop((1950, 560, 2520, 1160)).save(REVIEW / "SC4002_4113_target_crop.png")


if __name__ == "__main__":
    main()
