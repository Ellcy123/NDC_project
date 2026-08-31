import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "00_cart_support" / "accepted_cart_scene.png"
JOB = ROOT / "01_4115_scene_insert"
CROP_RECT = (1056, 64, 2592, 1600)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = Image.open(SOURCE).convert("RGBA")
    base_crop = source.crop(CROP_RECT)
    generated = Image.open(JOB / "generated_attempt_1.png").convert("RGBA")
    registered = generated.resize(base_crop.size, Image.Resampling.LANCZOS)
    registered.save(JOB / "generated_attempt_1_registered.png")

    # Post-generation object extraction: only the open ledger is interactive.
    mask = Image.new("L", base_crop.size, 0)
    d = ImageDraw.Draw(mask)
    d.polygon(
        [
            (606, 782), (622, 742), (646, 716), (742, 714),
            (770, 723), (790, 716), (883, 719), (911, 744),
            (934, 783), (900, 794), (790, 786), (770, 792),
            (735, 786), (633, 794),
        ],
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(1.4))
    mask.save(JOB / "4115_object_alpha_crop.png")

    full_mask = Image.new("L", source.size, 0)
    full_mask.paste(mask, CROP_RECT[:2])
    full_mask.save(JOB / "4115_object_alpha.png")

    layer_crop = registered.copy()
    layer_crop.putalpha(mask)
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    layer.paste(layer_crop, CROP_RECT[:2], layer_crop)
    layer.save(JOB / "4115_scene_derived_source_layer.png")

    accepted = Image.alpha_composite(source, layer)
    accepted_path = JOB / "accepted_4115_scene.png"
    accepted.save(accepted_path)

    diff = ImageChops.difference(source, accepted)
    outside = Image.composite(Image.new("RGBA", source.size), diff, Image.eval(full_mask, lambda x: 255 - x))
    bbox = full_mask.getbbox()
    report = {
        "status": "PASS" if outside.getbbox() is None else "FAIL",
        "passed": outside.getbbox() is None,
        "item_id": "4115",
        "route": "direct-scene",
        "source_sha256": sha256(SOURCE),
        "generated_sha256": sha256(JOB / "generated_attempt_1.png"),
        "accepted_sha256": sha256(accepted_path),
        "object_alpha_bbox": list(bbox) if bbox else None,
        "outside_object_alpha_diff_bbox": outside.getbbox(),
        "hotspot_rule": "Only the generated ledger silhouette; table excluded.",
    }
    (JOB / "boundary_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
