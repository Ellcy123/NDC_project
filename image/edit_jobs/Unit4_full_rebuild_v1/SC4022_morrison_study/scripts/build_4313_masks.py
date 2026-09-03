from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "05_4312_scene_comp_v2" / "SC4022_4312_delivery_scene.png"
MASK_DIR = ROOT / "masks"


def main() -> None:
    MASK_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE)

    intent = Image.new("L", source.size, 0)
    ImageDraw.Draw(intent).polygon(
        [(1475, 792), (1695, 785), (1732, 882), (1490, 902)],
        fill=255,
    )
    intent.save(MASK_DIR / "4313_folder_intent_mask_a1.png")

    semantic = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(semantic)
    draw.polygon(
        [(1380, 770), (1514, 767), (1548, 797), (1403, 815)],
        fill=255,
    )
    draw.polygon(
        [(1388, 796), (1538, 793), (1578, 821), (1546, 844), (1420, 848), (1385, 822)],
        fill=255,
    )
    draw.line([(1500, 810), (1545, 826), (1576, 848)], fill=255, width=12)
    draw.ellipse((1562, 837, 1594, 860), fill=255)
    semantic.save(MASK_DIR / "4313_folder_semantic_mask_a1.png")


if __name__ == "__main__":
    main()
