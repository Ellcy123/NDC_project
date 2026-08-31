import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01_4115_scene_insert" / "accepted_4115_scene.png"
JOB = ROOT / "02_4116_scene_insert"
CROP_RECT = (896, 400, 1920, 1424)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = Image.open(SOURCE).convert("RGBA")
    base_crop = source.crop(CROP_RECT)
    generated = Image.open(JOB / "generated_attempt_1.png").convert("RGBA")
    registered = generated.resize(base_crop.size, Image.Resampling.LANCZOS)
    registered.save(JOB / "generated_attempt_1_registered.png")

    # Extract only the three-letter bundle and its clip after scene acceptance.
    mask = Image.new("L", base_crop.size, 0)
    d = ImageDraw.Draw(mask)
    d.polygon(
        [(418, 499), (429, 474), (472, 466), (638, 493),
         (634, 515), (518, 531), (446, 517)],
        fill=255,
    )
    d.polygon(
        [(407, 473), (417, 465), (441, 468), (451, 484),
         (443, 491), (421, 486)],
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    mask.save(JOB / "4116_object_alpha_crop.png")
    full_mask = Image.new("L", source.size, 0)
    full_mask.paste(mask, CROP_RECT[:2])
    full_mask.save(JOB / "4116_object_alpha.png")

    layer_crop = registered.copy()
    layer_crop.putalpha(mask)
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    layer.paste(layer_crop, CROP_RECT[:2], layer_crop)
    layer.save(JOB / "4116_scene_derived_source_layer.png")
    accepted = Image.alpha_composite(source, layer)
    accepted_path = JOB / "accepted_4116_scene.png"
    accepted.save(accepted_path)

    diff = ImageChops.difference(source, accepted)
    outside = Image.composite(Image.new("RGBA", source.size), diff, Image.eval(full_mask, lambda x: 255 - x))
    bbox = full_mask.getbbox()
    report = {
        "status": "PASS" if outside.getbbox() is None else "FAIL",
        "item_id": "4116",
        "route": "direct-scene",
        "source_sha256": sha256(SOURCE),
        "generated_sha256": sha256(JOB / "generated_attempt_1.png"),
        "accepted_sha256": sha256(accepted_path),
        "object_alpha_bbox": list(bbox) if bbox else None,
        "outside_object_alpha_diff_bbox": outside.getbbox(),
        "hotspot_rule": "Only the three-letter bundle and metal clip; cart excluded.",
        "detail_status": "BLOCKED_PENDING_LOCKED_THIRD_SUBMISSION_DATE",
    }
    (JOB / "boundary_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
