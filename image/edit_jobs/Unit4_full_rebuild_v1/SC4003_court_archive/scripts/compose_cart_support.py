import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_court_archive_day.png")
JOB = ROOT / "00_cart_support"
CROP_RECT = (768, 320, 2016, 1568)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def polygon(draw, points, fill=255):
    draw.polygon(points, fill=fill)


def main():
    source = Image.open(SOURCE).convert("RGBA")
    original_crop = source.crop(CROP_RECT)
    generated = Image.open(JOB / "generated_attempt_1.png").convert("RGBA")
    generated = generated.resize(original_crop.size, Image.Resampling.LANCZOS)
    generated.save(JOB / "generated_attempt_1_registered.png")

    # Object-only silhouette. Open spaces between the cart rails remain sourced
    # from the approved scene so regenerated cabinet/floor pixels cannot leak in.
    obj = Image.new("L", original_crop.size, 0)
    d = ImageDraw.Draw(obj)
    polygon(d, [(447, 554), (614, 539), (855, 574), (850, 610), (481, 627), (446, 608)])
    polygon(d, [(446, 603), (486, 607), (493, 845), (453, 861)])
    polygon(d, [(607, 602), (637, 602), (636, 776), (610, 778)])
    polygon(d, [(812, 600), (850, 589), (846, 827), (814, 833)])
    polygon(d, [(469, 767), (635, 760), (827, 784), (801, 842), (486, 819)])
    polygon(d, [(451, 832), (491, 823), (481, 874), (455, 881)])
    polygon(d, [(689, 812), (727, 815), (719, 889), (686, 890)])
    polygon(d, [(816, 805), (849, 803), (844, 861), (816, 865)])
    d.ellipse((448, 850, 486, 894), fill=255)
    d.ellipse((684, 865, 725, 913), fill=255)
    d.ellipse((812, 837, 849, 880), fill=255)
    obj = obj.filter(ImageFilter.GaussianBlur(1.6))
    obj.save(JOB / "cart_object_mask.png")

    shadow = Image.new("L", original_crop.size, 0)
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((410, 770, 895, 960), fill=72)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    shadow.save(JOB / "cart_shadow_mask.png")
    final_mask = ImageChops.lighter(obj, shadow)
    final_mask.save(JOB / "cart_final_composite_mask.png")

    composed_crop = Image.composite(generated, original_crop, final_mask)
    composed_crop.save(JOB / "cart_composed_crop.png")
    accepted = source.copy()
    accepted.paste(composed_crop, CROP_RECT[:2])
    accepted_path = JOB / "accepted_cart_scene.png"
    accepted.save(accepted_path)

    full_mask = Image.new("L", source.size, 0)
    full_mask.paste(final_mask, CROP_RECT[:2])
    full_mask.save(JOB / "cart_full_scene_composite_mask.png")

    diff = ImageChops.difference(source, accepted)
    outside = Image.composite(Image.new("RGBA", source.size), diff, Image.eval(full_mask, lambda x: 255 - x))
    outside_bbox = outside.getbbox()
    report = {
        "status": "PASS" if outside_bbox is None else "FAIL",
        "source": str(SOURCE),
        "source_sha256": sha256(SOURCE),
        "generated_sha256": sha256(JOB / "generated_attempt_1.png"),
        "accepted_sha256": sha256(accepted_path),
        "crop_rect": list(CROP_RECT),
        "outside_composite_mask_diff_bbox": outside_bbox,
        "note": "Cart is a noninteractive support; no hotspot is created for it.",
    }
    (JOB / "boundary_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
