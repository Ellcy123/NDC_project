import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_hospital_social_service_day.png")
FINAL = ROOT / "00_4216_scene_insert" / "accepted_4216_scene.png"
LAYER = ROOT / "00_4216_scene_insert" / "4216_scene_derived_source_layer.png"
ALPHA = ROOT / "00_4216_scene_insert" / "4216_object_alpha.png"
OUT = ROOT / "map_stage" / "4216"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    final = Image.open(FINAL).convert("RGB")
    layer = Image.open(LAYER).convert("RGBA")
    alpha = Image.open(ALPHA).convert("L")
    bbox = alpha.getbbox()
    rect = (bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4)
    map_path = OUT / "SC4012_envir_4216.png"
    layer.crop(rect).save(map_path)
    alpha.crop(rect).save(OUT / "SC4012_envir_4216_alpha.png")
    final.crop(rect).save(OUT / "SC4012_envir_4216_scene_reference.png")

    overlay = final.convert("RGBA")
    tint = Image.new("RGBA", overlay.size, (255, 40, 160, 0))
    tint.putalpha(alpha.point(lambda x: 120 if x >= 128 else 0))
    overlay = Image.alpha_composite(overlay, tint)
    d = ImageDraw.Draw(overlay)
    d.rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), outline=(0, 255, 255, 255), width=3)
    overlay.save(OUT / "SC4012_envir_4216_hotspot_overlay.png")

    original = Image.open(SOURCE).convert("RGB")
    diff = ImageChops.difference(original, final)
    outside_zero_alpha = alpha.point(lambda x: 255 if x == 0 else 0)
    outside = Image.composite(diff, Image.new("RGB", original.size), outside_zero_alpha)
    report = {
        "status": "PASS" if outside.getbbox() is None else "FAIL",
        "passed": outside.getbbox() is None,
        "scene": "SC4012",
        "item_id": "4216",
        "route": "environment",
        "object_alpha_bbox": list(bbox),
        "map_rect": list(rect),
        "map_size": [rect[2] - rect[0], rect[3] - rect[1]],
        "position": [str(rect[0]), str(rect[1]), "-3"],
        "map": str(map_path),
        "map_sha256": sha256(map_path),
        "source_size": list(original.size),
        "final_size": list(final.size),
        "source_mode": original.mode,
        "final_mode": final.mode,
        "outside_object_alpha_diff_bbox": outside.getbbox(),
        "hotspot": "Framed display installation only; wall and foreground counter books excluded.",
    }
    (ROOT / "map_stage" / "map_stage_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "SC4012_final_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
