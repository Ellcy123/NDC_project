from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"D:\NDC_project\image\定稿\u4_exp_morrison_study_night_preblast.png")
AUTHOR_JOB = ROOT / "01_4323_environment_a1"
COMPOSE_JOB = ROOT / "01_4323_environment_comp"
COMPOSE_JOB_V2 = ROOT / "01_4323_environment_comp_v2"
CROP_RECT = (384, 384, 1408, 1408)


def main():
    COMPOSE_JOB.mkdir(parents=True, exist_ok=True)
    COMPOSE_JOB_V2.mkdir(parents=True, exist_ok=True)
    source_full = Image.open(SOURCE).convert("RGB")
    source_crop = Image.open(AUTHOR_JOB / "source_crop.png").convert("RGB")
    registered = Image.open(AUTHOR_JOB / "registered.png").convert("RGB")

    composition = Image.new("L", source_full.size, 0)
    ImageDraw.Draw(composition).rounded_rectangle((660, 680, 1140, 940), radius=36, fill=255)
    composition.save(ROOT / "masks" / "4323_environment_composition_mask.png")

    composition_v2 = Image.new("L", source_full.size, 0)
    ImageDraw.Draw(composition_v2).rounded_rectangle((680, 660, 1160, 940), radius=36, fill=255)
    composition_v2.save(ROOT / "masks" / "4323_environment_composition_mask_v2.png")

    delta_full = Image.new("L", source_full.size, 0)
    ImageDraw.Draw(delta_full).rounded_rectangle((730, 720, 1060, 880), radius=24, fill=255)
    delta_full.save(ROOT / "masks" / "4323_environment_scene_delta_mask.png")

    delta_crop = delta_full.crop(CROP_RECT)
    soft_delta = delta_crop.filter(ImageFilter.GaussianBlur(6))
    cleaned_patch = Image.composite(registered, source_crop, soft_delta)
    cleaned_patch.save(COMPOSE_JOB / "cleaned_patch.png")
    registered.save(COMPOSE_JOB_V2 / "candidate_patch.png")

    semantic = Image.new("L", source_full.size, 0)
    semantic_draw = ImageDraw.Draw(semantic)
    semantic_draw.rounded_rectangle((786, 774, 838, 818), radius=9, fill=255)
    semantic_draw.rectangle((798, 760, 826, 783), fill=255)
    semantic_draw.ellipse((795, 755, 829, 768), fill=255)
    semantic_draw.polygon(
        [(846, 779), (944, 781), (967, 815), (963, 838), (852, 842), (846, 817)],
        fill=255,
    )
    semantic_draw.ellipse((973, 807, 1048, 861), fill=255)
    semantic.save(ROOT / "masks" / "4323_environment_semantic_mask.png")

    accepted_scene = Image.open(
        COMPOSE_JOB_V2 / "SC4022_4323_scene_v1.png"
    ).convert("RGB")
    map_layer = Image.new("RGBA", source_full.size, (0, 0, 0, 0))
    map_layer.paste(accepted_scene.convert("RGBA"), (0, 0), semantic)
    map_layer.save(COMPOSE_JOB_V2 / "4323_environment_map_layer.png")

    delivery_scene = source_full.copy()
    delivery_scene.paste(accepted_scene, (0, 0), semantic)
    delivery_scene.save(COMPOSE_JOB_V2 / "SC4022_4323_delivery_scene.png")

    overlay = accepted_scene.convert("RGBA")
    tint = Image.new("RGBA", source_full.size, (255, 0, 220, 0))
    tint.putalpha(semantic.point(lambda value: 112 if value else 0))
    overlay.alpha_composite(tint)
    overlay.save(COMPOSE_JOB_V2 / "4323_environment_semantic_overlay.png")

    diff = ImageChops.difference(source_full, accepted_scene)
    red, green, blue = diff.split()
    max_diff = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    zones = Image.new("L", source_full.size, 0)
    zones_draw = ImageDraw.Draw(zones)
    zones_draw.rectangle((760, 730, 855, 840), fill=255)
    zones_draw.rectangle((820, 760, 985, 855), fill=255)
    zones_draw.ellipse((945, 790, 1060, 875), fill=255)
    for threshold in (8, 16, 24, 32):
        threshold_mask = max_diff.point(
            lambda value, cutoff=threshold: 255 if value >= cutoff else 0
        )
        threshold_mask = ImageChops.multiply(threshold_mask, zones)
        threshold_mask.save(
            COMPOSE_JOB_V2 / f"4323_semantic_threshold_{threshold}.png"
        )
        threshold_overlay = accepted_scene.convert("RGBA")
        threshold_tint = Image.new("RGBA", source_full.size, (0, 255, 180, 0))
        threshold_tint.putalpha(
            threshold_mask.point(lambda value: 132 if value else 0)
        )
        threshold_overlay.alpha_composite(threshold_tint)
        threshold_overlay.save(
            COMPOSE_JOB_V2 / f"4323_semantic_threshold_{threshold}_overlay.png"
        )
        threshold_overlay.crop((680, 680, 1120, 920)).save(
            COMPOSE_JOB_V2 / f"4323_semantic_threshold_{threshold}_close.png"
        )


if __name__ == "__main__":
    main()
