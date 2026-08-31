from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/m4/project/NDC_project/image/定稿/u4_exp_morrison_study_night_preblast.png")


def main():
    (ROOT / "review").mkdir(parents=True, exist_ok=True)
    (ROOT / "masks").mkdir(parents=True, exist_ok=True)
    for name in ["00_4323_environment", "01_4312_scene_insert", "02_4313_scene_insert"]:
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    jobs = [
        ("4323 left-use objects/wear", (930, 700, 1320, 920), (0, 205, 255, 255)),
        ("4312 suicide note", (1220, 760, 1480, 900), (255, 210, 0, 255)),
        ("4313 transfer folder", (1480, 760, 1680, 920), (255, 75, 140, 255)),
    ]
    for label, rect, color in jobs:
        d.rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=color[:3] + (50,), outline=color, width=5)
        d.text((rect[0] + 8, rect[1] + 8), label, fill=color)
    Image.alpha_composite(source, layer).save(ROOT / "review" / "SC4022_planned_intent_overlay.png")
    source.crop((650, 560, 1800, 1050)).save(ROOT / "review" / "SC4022_desk_crop.png")


if __name__ == "__main__":
    main()
