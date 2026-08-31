import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageChops


ROOT = Path(__file__).resolve().parents[1]
APPROVED_SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_court_archive_day.png")
FINAL_SCENE = ROOT / "02_4116_scene_insert" / "accepted_4116_scene.png"
MAP_STAGE = ROOT / "map_stage"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pad_bbox(bbox, pad, size):
    return (
        max(0, bbox[0] - pad), max(0, bbox[1] - pad),
        min(size[0], bbox[2] + pad), min(size[1], bbox[3] + pad),
    )


def build_item(item_id, layer_path, alpha_path, final_scene):
    out = MAP_STAGE / item_id
    out.mkdir(parents=True, exist_ok=True)
    layer = Image.open(layer_path).convert("RGBA")
    alpha = Image.open(alpha_path).convert("L")
    bbox = alpha.getbbox()
    rect = pad_bbox(bbox, 4, final_scene.size)
    map_path = out / f"SC4003_item_{item_id}.png"
    layer.crop(rect).save(map_path)
    alpha.crop(rect).save(out / f"SC4003_item_{item_id}_alpha.png")
    final_scene.crop(rect).save(out / f"SC4003_item_{item_id}_scene_reference.png")

    overlay = final_scene.copy()
    tint = Image.new("RGBA", final_scene.size, (255, 40, 160, 0))
    tint.putalpha(alpha.point(lambda x: 120 if x else 0))
    overlay = Image.alpha_composite(overlay, tint)
    d = ImageDraw.Draw(overlay)
    d.rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), outline=(0, 255, 255, 255), width=3)
    overlay.save(out / f"SC4003_item_{item_id}_hotspot_overlay.png")
    return {
        "item_id": item_id,
        "route": "direct-scene",
        "object_alpha_bbox": list(bbox),
        "map_rect": list(rect),
        "map_size": [rect[2] - rect[0], rect[3] - rect[1]],
        "position": [str(rect[0]), str(rect[1]), "-3"],
        "map": str(map_path),
        "map_sha256": sha256(map_path),
        "hotspot": "object alpha only",
    }


def main():
    MAP_STAGE.mkdir(parents=True, exist_ok=True)
    original = Image.open(APPROVED_SOURCE).convert("RGBA")
    final_scene = Image.open(FINAL_SCENE).convert("RGBA")
    items = [
        build_item(
            "4115",
            ROOT / "01_4115_scene_insert" / "4115_scene_derived_source_layer.png",
            ROOT / "01_4115_scene_insert" / "4115_object_alpha.png",
            final_scene,
        ),
        build_item(
            "4116",
            ROOT / "02_4116_scene_insert" / "4116_scene_derived_source_layer.png",
            ROOT / "02_4116_scene_insert" / "4116_object_alpha.png",
            final_scene,
        ),
    ]
    manifest = {
        "scene": "SC4003",
        "source": str(APPROVED_SOURCE),
        "final_scene": str(FINAL_SCENE),
        "z_note": "-3 is staging convention only; no formal table was written.",
        "items": items,
    }
    (MAP_STAGE / "map_stage_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    union = Image.open(ROOT / "00_cart_support" / "cart_full_scene_composite_mask.png").convert("L")
    for path in [
        ROOT / "01_4115_scene_insert" / "4115_object_alpha.png",
        ROOT / "02_4116_scene_insert" / "4116_object_alpha.png",
    ]:
        union = ImageChops.lighter(union, Image.open(path).convert("L"))
    union.save(ROOT / "masks" / "SC4003_final_union_mask.png")
    diff = ImageChops.difference(original, final_scene)
    outside = Image.composite(Image.new("RGBA", original.size), diff, Image.eval(union, lambda x: 255 - x))
    sibling = ImageChops.multiply(
        Image.open(ROOT / "01_4115_scene_insert" / "4115_object_alpha.png").convert("L"),
        Image.open(ROOT / "02_4116_scene_insert" / "4116_object_alpha.png").convert("L"),
    )
    verify = {
        "status": "PASS" if outside.getbbox() is None and sibling.getbbox() is None else "FAIL",
        "source_size": list(original.size),
        "final_size": list(final_scene.size),
        "source_mode": original.mode,
        "final_mode": final_scene.mode,
        "outside_union_diff_bbox": outside.getbbox(),
        "4115_4116_hotspot_overlap_bbox": sibling.getbbox(),
        "source_sha256": sha256(APPROVED_SOURCE),
        "final_sha256": sha256(FINAL_SCENE),
    }
    (ROOT / "SC4003_final_verification.json").write_text(json.dumps(verify, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
