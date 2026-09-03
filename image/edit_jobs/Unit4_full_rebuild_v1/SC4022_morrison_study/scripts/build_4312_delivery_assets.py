from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "05_4312_scene_comp_v2" / "SC4022_4312_delivery_scene.png"
MASK = ROOT / "masks" / "4312_note_semantic_mask_a1.png"
MAP_LAYER = ROOT / "05_4312_scene_comp_v2" / "4312_note_map_layer.png"


def main() -> None:
    final = Image.open(FINAL).convert("RGBA")
    mask = Image.open(MASK).convert("L")
    layer = Image.new("RGBA", final.size, (0, 0, 0, 0))
    layer.paste(final, (0, 0), mask)
    layer.save(MAP_LAYER)


if __name__ == "__main__":
    main()
