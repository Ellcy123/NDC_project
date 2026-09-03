from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01_4323_environment_comp_v2" / "SC4022_4323_delivery_scene.png"
MASK_DIR = ROOT / "masks"


def main() -> None:
    MASK_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE)

    intent = Image.new("L", source.size, 0)
    ImageDraw.Draw(intent).polygon(
        [(1060, 815), (1185, 810), (1195, 875), (1060, 888)],
        fill=255,
    )
    intent.save(MASK_DIR / "4312_note_intent_mask_a1.png")

    semantic = Image.new("L", source.size, 0)
    ImageDraw.Draw(semantic).polygon(
        [(1050, 834), (1176, 831), (1206, 862), (1050, 877)],
        fill=255,
    )
    semantic.save(MASK_DIR / "4312_note_semantic_mask_a1.png")


if __name__ == "__main__":
    main()
