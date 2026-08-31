from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "delivery" / "scene_key_4318.png"
CANDIDATE_PATH = ROOT / "03_4319_scene_insert" / "scene_candidate.png"
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

    # Scene-derived semantic silhouette of the new folded newspaper only.
    # The bench, rack, and older upright newspaper remain outside this alpha.
    draw.polygon(
        scaled(
            [
                (2361, 881),
                (2370, 879),
                (2477, 879),
                (2484, 883),
                (2489, 889),
                (2502, 895),
                (2503, 899),
                (2492, 903),
                (2488, 908),
                (2474, 911),
                (2413, 920),
                (2397, 918),
                (2386, 912),
                (2377, 905),
                (2368, 898),
            ]
        ),
        fill=255,
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
    layer.save(ROOT / "extraction" / "4319_newspaper_full_scene_layer.png")
    alpha.save(ROOT / "extraction" / "4319_newspaper_alpha.png")

    composition_mask = np.where(alpha_array > 0, 255, 0).astype(np.uint8)
    Image.fromarray(composition_mask, "L").save(ROOT / "masks" / "4319_composition_mask.png")

    reconstructed = source.copy()
    reconstructed.alpha_composite(layer)
    reconstructed.save(ROOT / "extraction" / "4319_reconstructed_scene.png")
    reconstructed.crop(map_rect).save(ROOT / "extraction" / "4319_reconstructed_crop.png")

    map_sprite = layer.crop(map_rect)
    map_path = ROOT / "delivery" / "4319" / "SC4025_item_4319.png"
    map_sprite.save(map_path)

    close_rect = (2260, 720, 2720, 940)
    reconstructed.crop(close_rect).save(ROOT / "review" / "4319_scene_close.png")

    hotspot_overlay = reconstructed.copy()
    tint = Image.new("RGBA", reconstructed.size, (50, 245, 110, 0))
    tint.putalpha(alpha.point(lambda value: 130 if value >= 128 else 0))
    hotspot_overlay.alpha_composite(tint)
    overlay_draw = ImageDraw.Draw(hotspot_overlay, "RGBA")
    overlay_draw.rectangle(map_rect, outline=(70, 255, 130, 255), width=3)
    overlay_draw.text(
        (map_rect[0], map_rect[1] - 26),
        "4319 HOTSPOT = NEW NEWSPAPER ALPHA",
        fill=(90, 255, 150, 255),
    )
    hotspot_overlay.save(ROOT / "review" / "4319_hotspot_overlay.png")
    hotspot_overlay.crop(close_rect).save(ROOT / "review" / "4319_hotspot_close.png")

    checker = Image.new("RGBA", map_sprite.size, (55, 55, 55, 255))
    checker_draw = ImageDraw.Draw(checker)
    for cy in range(0, map_sprite.height, 8):
        for cx in range(0, map_sprite.width, 8):
            if (cx // 8 + cy // 8) % 2 == 0:
                checker_draw.rectangle((cx, cy, cx + 7, cy + 7), fill=(105, 105, 105, 255))
    checker.alpha_composite(map_sprite)
    checker.resize((map_sprite.width * 4, map_sprite.height * 4), Image.Resampling.NEAREST).save(
        ROOT / "review" / "4319_map_checker_4x.png"
    )
    alpha.crop(map_rect).resize((map_sprite.width * 4, map_sprite.height * 4), Image.Resampling.NEAREST).save(
        ROOT / "review" / "4319_alpha_4x.png"
    )

    report = {
        "stage": "scene-first-then-extract",
        "passed": True,
        "itemId": "4319",
        "sourceScene": {"path": str(SOURCE_PATH), "sha256": sha256(SOURCE_PATH)},
        "acceptedGeneratedScene": {"path": str(CANDIDATE_PATH), "sha256": sha256(CANDIDATE_PATH)},
        "extractionSource": "accepted post-generation full-scene result",
        "independentPropGenerationUsed": False,
        "hotspot": {
            "mode": "extracted-object-alpha",
            "alphaThreshold": 128,
            "target": "new folded newspaper only; bench, rack, and older upright newspaper excluded",
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
            "mapSpritePath": "SC4025_item_4319",
            "Position": [str(map_rect[0]), str(map_rect[1]), "-3"],
        },
    }
    (ROOT / "delivery" / "4319" / "extraction_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "delivery" / "4319" / "XYposition.txt").write_text(
        f"SC4025_item_4319 {map_rect[0]},{map_rect[1]}\n", encoding="utf-8"
    )
    print(json.dumps(report["hotspot"] | report["mapCrop"] | report["unityDraft"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
