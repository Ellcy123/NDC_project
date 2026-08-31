from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = Path(
    "/Users/m4/project/NDC_project/image/edit_jobs/Unit4_SC4025_key_scene_inpaint_v2/delivery/scene_with_item.png"
)
CANDIDATE_PATH = ROOT / "01_4318_scene_insert" / "scene_candidate.png"
PAD = 4
SCALE = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scaled(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return [(x * SCALE, y * SCALE) for x, y in points]


def main() -> None:
    source = Image.open(SOURCE_PATH).convert("RGBA")
    candidate = Image.open(CANDIDATE_PATH).convert("RGBA")

    large_mask = Image.new("L", (source.width * SCALE, source.height * SCALE), 0)
    draw = ImageDraw.Draw(large_mask)

    # Scene-derived semantic silhouette: board and paper stack.
    draw.polygon(
        scaled(
            [
                (1740, 814),
                (1776, 810),
                (1878, 829),
                (1882, 837),
                (1760, 838),
                (1740, 825),
            ]
        ),
        fill=255,
    )
    # Raised metal clip is a thin arch; keep the wall visible through its open center.
    draw.line(
        scaled([(1774, 813), (1778, 804), (1785, 799), (1795, 799), (1803, 805), (1806, 813)]),
        fill=255,
        width=3 * SCALE,
        joint="curve",
    )

    alpha = large_mask.resize(source.size, Image.Resampling.LANCZOS)
    alpha_array = np.asarray(alpha, dtype=np.uint8)
    alpha_array = np.where(alpha_array < 10, 0, alpha_array).astype(np.uint8)
    alpha = Image.fromarray(alpha_array, "L")

    ys, xs = np.where(alpha_array >= 128)
    object_bounds = (int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1))
    map_rect = (
        max(0, object_bounds[0] - PAD),
        max(0, object_bounds[1] - PAD),
        min(source.width, object_bounds[2] + PAD),
        min(source.height, object_bounds[3] + PAD),
    )

    candidate_array = np.asarray(candidate, dtype=np.uint8).copy()
    candidate_array[:, :, 3] = alpha_array
    candidate_array[alpha_array == 0, :3] = 0
    layer = Image.fromarray(candidate_array, "RGBA")
    layer.save(ROOT / "extraction" / "4318_dispatch_full_scene_layer.png")
    alpha.save(ROOT / "extraction" / "4318_dispatch_alpha.png")

    composition_mask = np.where(alpha_array > 0, 255, 0).astype(np.uint8)
    Image.fromarray(composition_mask, "L").save(ROOT / "masks" / "4318_composition_mask.png")

    reconstructed = source.copy()
    reconstructed.alpha_composite(layer)
    reconstructed.save(ROOT / "extraction" / "4318_reconstructed_scene.png")
    reconstructed.crop(map_rect).save(ROOT / "extraction" / "4318_reconstructed_crop.png")

    map_sprite = layer.crop(map_rect)
    map_path = ROOT / "delivery" / "4318" / "SC4025_item_4318.png"
    map_sprite.save(map_path)

    close_rect = (1620, 730, 2010, 910)
    reconstructed.crop(close_rect).save(ROOT / "review" / "4318_scene_close.png")

    hotspot_overlay = reconstructed.copy()
    tint = Image.new("RGBA", reconstructed.size, (50, 245, 110, 0))
    tint.putalpha(alpha.point(lambda value: 130 if value >= 128 else 0))
    hotspot_overlay.alpha_composite(tint)
    overlay_draw = ImageDraw.Draw(hotspot_overlay, "RGBA")
    overlay_draw.rectangle(map_rect, outline=(70, 255, 130, 255), width=3)
    overlay_draw.text((map_rect[0], map_rect[1] - 26), "4318 HOTSPOT = CLIPBOARD ALPHA", fill=(90, 255, 150, 255))
    hotspot_overlay.save(ROOT / "review" / "4318_hotspot_overlay.png")
    hotspot_overlay.crop(close_rect).save(ROOT / "review" / "4318_hotspot_close.png")

    checker = Image.new("RGBA", map_sprite.size, (55, 55, 55, 255))
    checker_draw = ImageDraw.Draw(checker)
    for cy in range(0, map_sprite.height, 8):
        for cx in range(0, map_sprite.width, 8):
            if (cx // 8 + cy // 8) % 2 == 0:
                checker_draw.rectangle((cx, cy, cx + 7, cy + 7), fill=(105, 105, 105, 255))
    checker.alpha_composite(map_sprite)
    checker.resize((map_sprite.width * 4, map_sprite.height * 4), Image.Resampling.NEAREST).save(
        ROOT / "review" / "4318_map_checker_4x.png"
    )
    alpha.crop(map_rect).resize((map_sprite.width * 4, map_sprite.height * 4), Image.Resampling.NEAREST).save(
        ROOT / "review" / "4318_alpha_4x.png"
    )

    report = {
        "stage": "scene-first-then-extract",
        "passed": True,
        "itemId": "4318",
        "sourceScene": {"path": str(SOURCE_PATH), "sha256": sha256(SOURCE_PATH)},
        "acceptedGeneratedScene": {"path": str(CANDIDATE_PATH), "sha256": sha256(CANDIDATE_PATH)},
        "extractionSource": "accepted post-generation full-scene result",
        "independentPropGenerationUsed": False,
        "hotspot": {
            "mode": "extracted-object-alpha",
            "alphaThreshold": 128,
            "target": "clipboard + metal clip + papers only; desk excluded",
            "objectBounds": list(object_bounds),
            "pixelCount": int((alpha_array >= 128).sum()),
        },
        "mapCrop": {
            "x": map_rect[0],
            "y": map_rect[1],
            "width": map_rect[2] - map_rect[0],
            "height": map_rect[3] - map_rect[1],
            "rect": list(map_rect),
        },
        "mapSprite": {"path": str(map_path), "sha256": sha256(map_path)},
        "unityDraft": {
            "mapSpritePath": "SC4025_item_4318",
            "Position": [str(map_rect[0]), str(map_rect[1]), "-3"],
        },
    }
    (ROOT / "delivery" / "4318" / "extraction_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "delivery" / "4318" / "XYposition.txt").write_text(
        f"SC4025_item_4318 {map_rect[0]},{map_rect[1]}\n", encoding="utf-8"
    )
    print(json.dumps(report["hotspot"] | report["mapCrop"] | report["unityDraft"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
