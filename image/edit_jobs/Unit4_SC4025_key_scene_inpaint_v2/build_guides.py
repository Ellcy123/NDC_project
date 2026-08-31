from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_court_dispatch_night.png")
TARGET_RECT = (1280, 805, 1490, 870)
CROP_RECT = (864, 320, 1888, 1344)


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rectangle(TARGET_RECT, fill=255)
    mask.save(ROOT / "masks" / "4317_placement_rect.png")

    full_overlay = source.copy()
    draw = ImageDraw.Draw(full_overlay, "RGBA")
    draw.rectangle(TARGET_RECT, fill=(255, 208, 0, 42), outline=(255, 230, 40, 255), width=6)
    draw.text((TARGET_RECT[0], TARGET_RECT[1] - 34), "4317 KEY PLACEMENT AREA", fill=(255, 240, 90, 255))
    full_overlay.save(ROOT / "review" / "4317_placement_rect_full.png")

    crop = source.crop(CROP_RECT)
    crop_overlay = crop.copy()
    local = (
        TARGET_RECT[0] - CROP_RECT[0],
        TARGET_RECT[1] - CROP_RECT[1],
        TARGET_RECT[2] - CROP_RECT[0],
        TARGET_RECT[3] - CROP_RECT[1],
    )
    draw = ImageDraw.Draw(crop_overlay, "RGBA")
    draw.rectangle(local, fill=(255, 208, 0, 48), outline=(255, 230, 40, 255), width=6)
    draw.text((local[0], local[1] - 34), "PLACE KEY HERE", fill=(255, 240, 90, 255))
    crop_overlay.save(ROOT / "01_scene_insert" / "placement_guide.png")

    (ROOT / "review" / "geometry.json").write_text(
        json.dumps(
            {
                "source": str(SOURCE),
                "source_size": list(source.size),
                "placement_rect_top_left": list(TARGET_RECT),
                "generation_crop_top_left": list(CROP_RECT),
                "placement_rect_in_crop": list(local),
                "note": "Placement rectangle is generation guidance only; final hotspot comes from the extracted key alpha after scene generation.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
