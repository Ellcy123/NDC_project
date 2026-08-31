from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
BASE_SCENE = Path(
    "/Users/m4/project/NDC_project/image/edit_jobs/Unit4_SC4025_key_scene_inpaint_v2/delivery/scene_with_item.png"
)

PLACEMENTS = {
    "4318": {
        "rect": (1680, 775, 1950, 865),
        "crop": (1280, 320, 2304, 1344),
        "label": "4318 DISPATCH CLIPBOARD",
    },
    "4319": {
        "rect": (2340, 775, 2640, 905),
        "crop": (1984, 320, 3008, 1344),
        "label": "4319 EVENING NEWSPAPER",
    },
}


def build_for(item_id: str, source: Image.Image) -> dict[str, object]:
    data = PLACEMENTS[item_id]
    rect = data["rect"]
    crop_rect = data["crop"]
    label = data["label"]

    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rectangle(rect, fill=255)
    mask.save(ROOT / "masks" / f"{item_id}_placement_rect.png")

    full_overlay = source.copy()
    draw = ImageDraw.Draw(full_overlay, "RGBA")
    draw.rectangle(rect, fill=(255, 208, 0, 42), outline=(255, 230, 40, 255), width=6)
    draw.text((rect[0], rect[1] - 34), label, fill=(255, 240, 90, 255))
    full_overlay.save(ROOT / "review" / f"{item_id}_placement_rect_full.png")

    crop = source.crop(crop_rect)
    crop_overlay = crop.copy()
    local = (
        rect[0] - crop_rect[0],
        rect[1] - crop_rect[1],
        rect[2] - crop_rect[0],
        rect[3] - crop_rect[1],
    )
    draw = ImageDraw.Draw(crop_overlay, "RGBA")
    draw.rectangle(local, fill=(255, 208, 0, 48), outline=(255, 230, 40, 255), width=6)
    draw.text((local[0], local[1] - 34), label, fill=(255, 240, 90, 255))
    crop_overlay.save(ROOT / f"{'01_4318_scene_insert' if item_id == '4318' else '03_4319_scene_insert'}" / "placement_guide.png")

    return {
        "placementRectTopLeft": list(rect),
        "generationCropTopLeft": list(crop_rect),
        "placementRectInCrop": list(local),
    }


def main() -> None:
    source = Image.open(BASE_SCENE).convert("RGBA")
    geometry = {
        "baseScene": str(BASE_SCENE),
        "sourceSize": list(source.size),
        "items": {item_id: build_for(item_id, source) for item_id in PLACEMENTS},
        "note": "Placement rectangles guide scene generation only. Final Maps and hotspots come from post-generation extracted object alpha.",
    }
    (ROOT / "review" / "geometry.json").write_text(
        json.dumps(geometry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
