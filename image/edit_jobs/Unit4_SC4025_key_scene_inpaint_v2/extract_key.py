from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_court_dispatch_night.png")
SCENE_PATH = ROOT / "01_scene_insert" / "scene_candidate.png"
ROI = (1250, 790, 1515, 892)
PAD = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dilate(mask: np.ndarray, radius: int = 1) -> np.ndarray:
    result = mask.copy()
    for _ in range(radius):
        padded = np.pad(result, 1, mode="constant")
        result = np.logical_or.reduce(
            [padded[dy : dy + result.shape[0], dx : dx + result.shape[1]] for dy in range(3) for dx in range(3)]
        )
    return result


def erode(mask: np.ndarray, radius: int = 1) -> np.ndarray:
    result = mask.copy()
    for _ in range(radius):
        padded = np.pad(result, 1, mode="constant", constant_values=True)
        result = np.logical_and.reduce(
            [padded[dy : dy + result.shape[0], dx : dx + result.shape[1]] for dy in range(3) for dx in range(3)]
        )
    return result


def components(mask: np.ndarray) -> list[np.ndarray]:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    groups: list[np.ndarray] = []
    for y, x in zip(*np.where(mask & ~seen)):
        queue = deque([(int(y), int(x))])
        seen[y, x] = True
        points: list[tuple[int, int]] = []
        while queue:
            cy, cx = queue.popleft()
            points.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
        group = np.zeros_like(mask, dtype=bool)
        ys, xs = zip(*points)
        group[np.asarray(ys), np.asarray(xs)] = True
        groups.append(group)
    return groups


def main() -> None:
    source_image = Image.open(SOURCE_PATH).convert("RGBA")
    scene_image = Image.open(SCENE_PATH).convert("RGBA")
    source = np.asarray(source_image, dtype=np.int16)
    scene = np.asarray(scene_image, dtype=np.int16)

    left, top, right, bottom = ROI
    src = source[top:bottom, left:right, :3]
    cur = scene[top:bottom, left:right, :3]
    diff = np.max(np.abs(cur - src), axis=2)
    r, g, b = cur[:, :, 0], cur[:, :, 1], cur[:, :, 2]

    warm = (r - b >= 22) & (g - b >= 6) & (r - g >= 4) & (r >= 72)
    bright = (r + g + b >= 210)
    seed = warm & bright & (diff >= 16)

    # The key is the coherent warm newly generated component inside the chosen tray box.
    seed_groups = [group for group in components(seed) if int(group.sum()) >= 4]
    if not seed_groups:
        raise RuntimeError("No brass key seed was found in the post-generation scene.")
    seed_groups.sort(key=lambda group: int(group.sum()), reverse=True)
    seed_component_report = []
    for index, group in enumerate(seed_groups):
        group_ys, group_xs = np.where(group)
        seed_component_report.append(
            {
                "index": index,
                "pixels": int(group.sum()),
                "bboxGlobal": [
                    int(group_xs.min() + left),
                    int(group_ys.min() + top),
                    int(group_xs.max() + left + 1),
                    int(group_ys.max() + top + 1),
                ],
            }
        )
    (ROOT / "review" / "4317_seed_components.json").write_text(
        json.dumps(seed_component_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    selected_groups = []
    for group in seed_groups:
        group_ys, group_xs = np.where(group)
        bbox_global = (
            int(group_xs.min() + left),
            int(group_ys.min() + top),
            int(group_xs.max() + left + 1),
            int(group_ys.max() + top + 1),
        )
        component_height = bbox_global[3] - bbox_global[1]
        if (
            component_height >= 3
            and bbox_global[0] >= 1325
            and bbox_global[2] <= 1445
            and bbox_global[1] >= 835
            and bbox_global[3] <= 865
        ):
            selected_groups.append(group)
    if not selected_groups:
        raise RuntimeError("No coherent key components survived the tray-glint filter.")
    selected_seed = np.logical_or.reduce(selected_groups)

    Image.fromarray(seed.astype(np.uint8) * 255, "L").resize(
        ((right - left) * 4, (bottom - top) * 4), Image.Resampling.NEAREST
    ).save(ROOT / "review" / "4317_seed_4x.png")
    Image.fromarray(selected_seed.astype(np.uint8) * 255, "L").resize(
        ((right - left) * 4, (bottom - top) * 4), Image.Resampling.NEAREST
    ).save(ROOT / "review" / "4317_selected_seed_4x.png")

    # Grow only two pixels into the changed scene. This retains the dark ink outline
    # and stamped digits while preserving the open center of the key ring.
    support = (diff >= 5) & dilate(selected_seed, 2)
    grown = selected_seed | support
    grown = erode(dilate(grown, 1), 1)

    # Keep only connected pieces carrying an approved key seed; discard tray glints.
    grown_groups = components(grown)
    object_groups = [group for group in grown_groups if np.any(group & selected_seed)]
    object_mask = np.logical_or.reduce(object_groups)

    full_mask = np.zeros(source.shape[:2], dtype=np.uint8)
    full_mask[top:bottom, left:right] = object_mask.astype(np.uint8) * 255
    alpha = Image.fromarray(full_mask, "L").filter(ImageFilter.GaussianBlur(0.55))
    alpha_array = np.asarray(alpha)
    alpha_array = np.where(alpha_array < 10, 0, alpha_array).astype(np.uint8)
    alpha = Image.fromarray(alpha_array, "L")

    ys, xs = np.where(alpha_array >= 128)
    if len(xs) == 0:
        raise RuntimeError("Extracted key mask is empty.")
    object_bounds = (int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1))
    map_rect = (
        max(0, object_bounds[0] - PAD),
        max(0, object_bounds[1] - PAD),
        min(scene.shape[1], object_bounds[2] + PAD),
        min(scene.shape[0], object_bounds[3] + PAD),
    )

    layer_array = np.asarray(scene_image, dtype=np.uint8).copy()
    layer_array[:, :, 3] = alpha_array
    layer_array[alpha_array == 0, :3] = 0
    full_layer = Image.fromarray(layer_array, "RGBA")
    full_layer.save(ROOT / "extraction" / "4317_key_full_scene_layer.png")
    alpha.save(ROOT / "extraction" / "4317_key_alpha.png")

    composition_mask_array = np.where(alpha_array > 0, 255, 0).astype(np.uint8)
    Image.fromarray(composition_mask_array, "L").save(ROOT / "masks" / "4317_composition_mask.png")

    reconstructed_scene = source_image.copy()
    reconstructed_scene.alpha_composite(full_layer)
    reconstructed_scene.save(ROOT / "extraction" / "reconstructed_scene.png")

    map_sprite = full_layer.crop(map_rect)
    map_sprite.save(ROOT / "delivery" / "SC4025_item_4317.png")
    reconstructed_scene.crop(map_rect).save(ROOT / "extraction" / "reconstructed_crop.png")

    checker = Image.new("RGBA", map_sprite.size, (55, 55, 55, 255))
    checker_draw = ImageDraw.Draw(checker)
    for cy in range(0, map_sprite.height, 8):
        for cx in range(0, map_sprite.width, 8):
            if (cx // 8 + cy // 8) % 2 == 0:
                checker_draw.rectangle((cx, cy, cx + 7, cy + 7), fill=(105, 105, 105, 255))
    checker.alpha_composite(map_sprite)
    checker.resize((map_sprite.width * 6, map_sprite.height * 6), Image.Resampling.NEAREST).save(
        ROOT / "review" / "4317_map_checker_6x.png"
    )
    alpha.crop(map_rect).resize((map_sprite.width * 6, map_sprite.height * 6), Image.Resampling.NEAREST).save(
        ROOT / "review" / "4317_alpha_6x.png"
    )

    close_rect = (left - 20, top - 20, right + 20, bottom + 20)
    reconstructed_scene.crop(close_rect).save(ROOT / "review" / "4317_scene_close.png")
    full_layer.crop(close_rect).save(ROOT / "review" / "4317_extracted_close.png")

    hotspot_overlay = reconstructed_scene.copy()
    overlay = Image.new("RGBA", scene_image.size, (0, 0, 0, 0))
    overlay.putalpha(alpha.point(lambda value: 130 if value >= 128 else 0))
    tint = Image.new("RGBA", scene_image.size, (50, 245, 110, 0))
    tint.putalpha(overlay.getchannel("A"))
    hotspot_overlay.alpha_composite(tint)
    draw = ImageDraw.Draw(hotspot_overlay, "RGBA")
    draw.rectangle(map_rect, outline=(70, 255, 130, 255), width=3)
    draw.text((map_rect[0], map_rect[1] - 26), "HOTSPOT = KEY ALPHA", fill=(90, 255, 150, 255))
    hotspot_overlay.save(ROOT / "review" / "4317_hotspot_overlay.png")
    hotspot_overlay.crop(close_rect).save(ROOT / "review" / "4317_hotspot_close.png")

    report = {
        "stage": "scene-first-then-extract",
        "passed": True,
        "sourceScene": {"path": str(SOURCE_PATH), "sha256": sha256(SOURCE_PATH)},
        "acceptedGeneratedScene": {"path": str(SCENE_PATH), "sha256": sha256(SCENE_PATH)},
        "reconstructedScene": {
            "path": str(ROOT / "extraction" / "reconstructed_scene.png"),
            "sha256": sha256(ROOT / "extraction" / "reconstructed_scene.png"),
            "method": "approved source + key layer extracted from the accepted generated scene",
        },
        "extractionSource": "accepted post-generation scene candidate",
        "independentPropGenerationUsed": False,
        "coordinateSystem": {
            "origin": "top-left",
            "xAxis": "right",
            "yAxis": "down",
            "unit": "pixel",
            "sceneWidth": scene.shape[1],
            "sceneHeight": scene.shape[0],
        },
        "hotspot": {
            "mode": "extracted-object-alpha",
            "alphaThreshold": 128,
            "target": "key + ring + 214 tag only",
            "objectBounds": list(object_bounds),
            "pixelCount": int((alpha_array >= 128).sum()),
            "trayPixelsIncludedByDesign": False,
        },
        "mapCrop": {
            "method": "post-generation-extracted-alpha-bounds-plus-4px",
            "x": map_rect[0],
            "y": map_rect[1],
            "width": map_rect[2] - map_rect[0],
            "height": map_rect[3] - map_rect[1],
            "rect": list(map_rect),
        },
        "mapSprite": {
            "path": str(ROOT / "delivery" / "SC4025_item_4317.png"),
            "sha256": sha256(ROOT / "delivery" / "SC4025_item_4317.png"),
            "transparentRgbNonzeroPixels": int(
                np.count_nonzero(np.any(np.asarray(map_sprite)[:, :, :3] != 0, axis=2) & (np.asarray(map_sprite)[:, :, 3] == 0))
            ),
        },
        "unityDraft": {
            "mapSpritePath": "SC4025_item_4317",
            "Position": [str(map_rect[0]), str(map_rect[1]), "-3"],
        },
    }
    (ROOT / "delivery" / "extraction_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "delivery" / "XYposition.txt").write_text(
        f"SC4025_item_4317 {map_rect[0]},{map_rect[1]}\n", encoding="utf-8"
    )
    print(json.dumps(report["hotspot"] | report["mapCrop"] | report["unityDraft"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
