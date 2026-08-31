from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "delivery" / "scene_with_items.png"
ALPHAS = {
    "4317": Path(
        "/Users/m4/project/NDC_project/image/edit_jobs/Unit4_SC4025_key_scene_inpaint_v2/extraction/4317_key_alpha.png"
    ),
    "4318": ROOT / "extraction" / "4318_dispatch_alpha.png",
    "4319": ROOT / "extraction" / "4319_newspaper_alpha.png",
}
MAPS = {
    "4317": Path(
        "/Users/m4/project/NDC_project/image/edit_jobs/Unit4_SC4025_key_scene_inpaint_v2/delivery/SC4025_item_4317.png"
    ),
    "4318": ROOT / "delivery" / "4318" / "SC4025_item_4318.png",
    "4319": ROOT / "delivery" / "4319" / "SC4025_item_4319.png",
}
COLORS = {
    "4317": (255, 205, 55, 145),
    "4318": (55, 235, 120, 145),
    "4319": (65, 175, 255, 145),
}
CLOSE_RECT = (1160, 720, 2640, 980)


def bounds(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)


def main() -> None:
    final = Image.open(FINAL).convert("RGBA")
    binary: dict[str, np.ndarray] = {}

    overlay = final.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    item_bounds: dict[str, list[int]] = {}
    for item_id, path in ALPHAS.items():
        alpha = Image.open(path).convert("L")
        mask = np.asarray(alpha, dtype=np.uint8) >= 128
        binary[item_id] = mask
        rect = bounds(mask)
        item_bounds[item_id] = list(rect)

        tint = Image.new("RGBA", final.size, COLORS[item_id][0:3] + (0,))
        tint.putalpha(alpha.point(lambda value, opacity=COLORS[item_id][3]: opacity if value >= 128 else 0))
        overlay.alpha_composite(tint)
        draw.rectangle(rect, outline=COLORS[item_id][0:3] + (255,), width=3)
        draw.text((rect[0], rect[1] - 24), item_id, fill=COLORS[item_id][0:3] + (255,))

    intersections: dict[str, int] = {}
    for left, right in combinations(binary, 2):
        intersections[f"{left}_{right}"] = int(np.logical_and(binary[left], binary[right]).sum())

    overlay.save(ROOT / "review" / "final_hotspot_overlay.png")
    overlay.crop(CLOSE_RECT).resize((2960, 520), Image.Resampling.NEAREST).save(
        ROOT / "review" / "final_hotspot_close_2x.png"
    )
    final.crop(CLOSE_RECT).resize((2960, 520), Image.Resampling.LANCZOS).save(
        ROOT / "review" / "final_items_close_2x.png"
    )

    cells: list[tuple[str, Image.Image]] = []
    for item_id, path in MAPS.items():
        sprite = Image.open(path).convert("RGBA")
        scale = min(4.0, 520 / max(sprite.width, 1), 260 / max(sprite.height, 1))
        shown = sprite.resize(
            (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
            Image.Resampling.NEAREST,
        )
        cells.append((item_id, shown))

    sheet = Image.new("RGBA", (1800, 360), (35, 35, 35, 255))
    sheet_draw = ImageDraw.Draw(sheet)
    for y in range(0, sheet.height, 16):
        for x in range(0, sheet.width, 16):
            if (x // 16 + y // 16) % 2 == 0:
                sheet_draw.rectangle((x, y, x + 15, y + 15), fill=(75, 75, 75, 255))
    for index, (item_id, sprite) in enumerate(cells):
        slot_x = index * 600
        x = slot_x + (600 - sprite.width) // 2
        y = 60 + (260 - sprite.height) // 2
        sheet.alpha_composite(sprite, (x, y))
        sheet_draw.text((slot_x + 20, 20), f"{item_id}  {MAPS[item_id].name}", fill=(255, 255, 255, 255))
    sheet.save(ROOT / "review" / "final_map_contact_sheet.png")

    audit = {
        "passed": all(count == 0 for count in intersections.values()),
        "alphaThreshold": 128,
        "itemBounds": item_bounds,
        "pairwiseHotspotIntersectionPixels": intersections,
        "finalScene": str(FINAL),
    }
    (ROOT / "delivery" / "hotspot_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
