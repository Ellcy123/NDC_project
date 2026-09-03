from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "10_4313_scene_comp" / "SC4022_4313_delivery_scene.png"
MASK = ROOT / "masks" / "4313_folder_semantic_mask_a1.png"
MAP_LAYER = ROOT / "10_4313_scene_comp" / "4313_folder_map_layer.png"


def main() -> None:
    final = Image.open(FINAL).convert("RGBA")
    mask = Image.open(MASK).convert("L")
    layer = Image.new("RGBA", final.size, (0, 0, 0, 0))
    layer.paste(final, (0, 0), mask)
    layer.save(MAP_LAYER)


if __name__ == "__main__":
    main()
