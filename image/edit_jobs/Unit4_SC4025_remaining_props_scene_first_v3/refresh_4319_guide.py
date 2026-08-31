from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "delivery" / "scene_key_4318.png"
CROP_RECT = (1984, 320, 3008, 1344)
PLACEMENT_RECT = (2340, 775, 2640, 905)


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    crop = source.crop(CROP_RECT)
    local = (
        PLACEMENT_RECT[0] - CROP_RECT[0],
        PLACEMENT_RECT[1] - CROP_RECT[1],
        PLACEMENT_RECT[2] - CROP_RECT[0],
        PLACEMENT_RECT[3] - CROP_RECT[1],
    )
    guide = crop.copy()
    draw = ImageDraw.Draw(guide, "RGBA")
    draw.rectangle(local, fill=(255, 208, 0, 48), outline=(255, 230, 40, 255), width=6)
    draw.text((local[0], local[1] - 34), "4319 EVENING NEWSPAPER", fill=(255, 240, 90, 255))
    guide.save(ROOT / "03_4319_scene_insert" / "placement_guide.png")


if __name__ == "__main__":
    main()
