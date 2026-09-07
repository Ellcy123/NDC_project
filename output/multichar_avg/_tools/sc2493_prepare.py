from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np


SOURCE = Path(r"D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2420_bg_FrankHome_Bathroom.png")
OUT = Path(r"D:\NDC_project\output\multichar_avg\SC2493_avg_DannyBathroomWindowWaiver")
JOB = Path(r"C:\Users\Ellcy\AppData\Local\Temp\ndc_art_jobs\SC2493-window-695e04557d7d48de987e46047fad5f67")
ACCEPTED_WINDOW = JOB / "03-window-composition" / "SC2493_source_with_window.png"
WHITEBOX_GENERATED = Path(r"C:\Users\Ellcy\.codex\generated_images\01a0658c-06c7-7d20-a27e-fcd480637f9d\exec-0621a502-63af-49a3-88c3-1a7b77b71739.png")


def main() -> None:
    for name in ("whitebox", "handoff", "candidates", "cutouts", "final", "review"):
        (OUT / name).mkdir(parents=True, exist_ok=True)
    (OUT / "scene_patch").mkdir(parents=True, exist_ok=True)
    (JOB / "masks").mkdir(parents=True, exist_ok=True)

    source = Image.open(SOURCE).convert("RGB")
    if source.size != (2560, 1600):
        raise ValueError(f"unexpected source size: {source.size}")

    # Broad authorization workspace for one 30 x 40 cm ventilation window on
    # the upper-right rear wall.  Coordinates are half-open source-canvas px.
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rectangle((1488, 0, 2207, 703), fill=255)
    mask.save(JOB / "masks" / "window_authorization.png")

    composition = Image.new("L", source.size, 0)
    ImageDraw.Draw(composition).rectangle((1700, 32, 2149, 559), fill=255)
    composition.save(JOB / "masks" / "window_composition.png")

    composition_v3 = Image.new("L", source.size, 0)
    ImageDraw.Draw(composition_v3).rectangle((1660, 160, 2009, 569), fill=255)
    composition_v3.save(JOB / "masks" / "window_composition_v3.png")

    overlay = source.convert("RGBA")
    shade = Image.new("RGBA", source.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle((1488, 0, 2208, 704), fill=(0, 200, 255, 70), outline=(0, 255, 255, 255), width=8)
    overlay.alpha_composite(shade)
    overlay.save(JOB / "window_authorization_overlay.png")

    # Fixed-canvas calibration image for whitebox generation.
    fitted = source.resize((1536, 960), Image.Resampling.LANCZOS)
    letter = Image.new("RGB", (1536, 1024), (224, 224, 224))
    letter.paste(fitted, (0, 32))
    letter.save(OUT / "whitebox" / "SC2493_source_letterbox_1536x1024.png")

    if ACCEPTED_WINDOW.exists():
        patched = Image.open(ACCEPTED_WINDOW).convert("RGB")
        patched.save(OUT / "scene_patch" / "SC2493_source_with_window_v1.png")
        local = patched.crop((1560, 96, 2100, 650))
        local.resize((local.width * 2, local.height * 2), Image.Resampling.NEAREST).save(
            OUT / "review" / "SC2493_window_patch_local_200.png"
        )
        fitted = patched.resize((1536, 960), Image.Resampling.LANCZOS)
        patched_letter = Image.new("RGB", (1536, 1024), (224, 224, 224))
        patched_letter.paste(fitted, (0, 32))
        patched_letter.save(OUT / "whitebox" / "SC2493_source_with_window_letterbox_1536x1024.png")

        lula_candidate = OUT / "candidates" / "SC2493_Lula_contextual_candidate_v1_raw.png"
        if lula_candidate.exists():
            Image.open(lula_candidate).convert("RGBA").crop((370, 270, 700, 650)).save(OUT / "cutouts" / "SC2493_Lula_tight_extract_input.png")
        mickey_candidate = OUT / "candidates" / "SC2493_Mickey_contextual_candidate_v1_raw.png"
        if mickey_candidate.exists():
            Image.open(mickey_candidate).convert("RGBA").crop((145, 430, 330, 755)).save(OUT / "cutouts" / "SC2493_Mickey_tight_extract_input.png")

        if WHITEBOX_GENERATED.exists():
            generated = Image.open(WHITEBOX_GENERATED).convert("RGB")
            generated.save(OUT / "whitebox" / "SC2493_combined_whitebox_v1_generated_1536x1024.png")
            content = generated.crop((0, 32, 1536, 992)).resize((2560, 1600), Image.Resampling.LANCZOS)
            content.crop((700, 350, 1780, 1600)).save(OUT / "whitebox" / "SC2493_Zack_whitebox_extract_input.png")
            rgb = np.asarray(content).astype(np.float32) / 255.0
            mx = rgb.max(axis=2)
            mn = rgb.min(axis=2)
            d = mx - mn
            sat = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
            hue = np.zeros_like(mx)
            nz = d > 1e-6
            r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
            sel = nz & (mx == r)
            hue[sel] = ((g[sel] - b[sel]) / d[sel]) % 6
            sel = nz & (mx == g)
            hue[sel] = (b[sel] - r[sel]) / d[sel] + 2
            sel = nz & (mx == b)
            hue[sel] = (r[sel] - g[sel]) / d[sel] + 4
            hue *= 60.0
            yy, xx = np.mgrid[0:1600, 0:2560]

            specs = {
                "Zack": ((hue >= 10) & (hue <= 85) & (sat > 0.18) & (mx > 0.34) & (xx > 820) & (xx < 1900) & (yy > 360)),
                "Danny": (((hue <= 28) | (hue >= 338)) & (sat > 0.22) & (mx > 0.28) & (xx > 1640) & (xx < 2350) & (yy < 1270)),
                "Lula": ((hue >= 255) & (hue <= 330) & (sat > 0.18) & (xx > 1540) & (xx < 1970) & (yy < 540)),
                "Mickey": ((hue >= 175) & (hue <= 245) & (sat > 0.15) & (xx > 1740) & (xx < 2120) & (yy < 520)),
            }

            base = patched.convert("RGBA")
            combined = base.copy()
            for name in ("Mickey", "Lula", "Danny", "Zack"):
                extracted_zack = OUT / "whitebox" / "SC2493_Zack_whitebox_extracted.png"
                if name == "Zack" and extracted_zack.exists():
                    actor = Image.new("RGBA", base.size, (0, 0, 0, 0))
                    actor.alpha_composite(Image.open(extracted_zack).convert("RGBA"), (700, 350))
                else:
                    raw = Image.fromarray((specs[name].astype(np.uint8) * 255), "L")
                    raw = raw.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MinFilter(13)).filter(ImageFilter.MaxFilter(5))
                    flood = raw.copy()
                    ImageDraw.floodfill(flood, (0, 0), 128, thresh=0)
                    flood_arr = np.asarray(flood)
                    filled = np.where(flood_arr == 128, 0, 255).astype(np.uint8)
                    raw = Image.fromarray(filled, "L").filter(ImageFilter.GaussianBlur(0.8))
                    actor = content.convert("RGBA")
                    actor.putalpha(raw)
                if name in ("Lula", "Mickey"):
                    shifted = Image.new("RGBA", actor.size, (0, 0, 0, 0))
                    shifted.alpha_composite(actor, (0, 120))
                    actor = shifted
                actor.save(OUT / "whitebox" / f"SC2493_{name}_whitebox_overlay_v1.png")
                isolated = base.copy()
                isolated.alpha_composite(actor)
                isolated.save(OUT / "whitebox" / f"SC2493_{name}_isolated_whitebox_v1_2560x1600.png")
                combined.alpha_composite(actor)
            combined.save(OUT / "whitebox" / "SC2493_combined_whitebox_v1_2560x1600.png")
            ui = Image.open(r"D:\NDC\Assets\Resources\Art\UI\AVG\left_BG.png").convert("RGBA")
            ui_check = combined.copy()
            ui_check.alpha_composite(ui, (0, 0))
            ui_check.save(OUT / "review" / "SC2493_whitebox_v1_ui-left-check.png")


if __name__ == "__main__":
    main()
