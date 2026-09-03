from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"D:\NDC_project\image\定稿\u4_exp_morrison_study_night_preblast.png")


def main():
    (ROOT / "review").mkdir(parents=True, exist_ok=True)
    (ROOT / "masks").mkdir(parents=True, exist_ok=True)
    for name in ["00_4311_body_and_gun", "00_4311_body_and_gun_v2", "00_4311_body_and_gun_v3", "01_4323_environment", "01_4323_environment_a1", "02_4312_scene_insert", "03_4313_scene_insert"]:
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    layer = Image.new("RGBA", source.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    jobs = [
        ("4311 Harold body + loose right-hand pistol", (1680, 1040, 2880, 1520), (255, 80, 60, 255)),
        ("4323 left-use objects/wear", (700, 730, 1000, 860), (0, 205, 255, 255)),
        ("4312 suicide note", (1220, 760, 1480, 900), (255, 210, 0, 255)),
        ("4313 transfer folder", (1480, 760, 1680, 920), (255, 75, 140, 255)),
    ]
    for label, rect, color in jobs:
        d.rectangle((rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=color[:3] + (50,), outline=color, width=5)
        d.text((rect[0] + 8, rect[1] + 8), label, fill=color)
    Image.alpha_composite(source, layer).save(ROOT / "review" / "SC4022_planned_intent_overlay.png")
    source.crop((650, 560, 1800, 1050)).save(ROOT / "review" / "SC4022_desk_crop.png")
    source.crop((1248, 576, 3168, 1600)).save(ROOT / "review" / "SC4022_body_context_crop.png")

    body_intent = Image.new("L", source.size, 0)
    ImageDraw.Draw(body_intent).polygon(
        [(1700, 1120), (1910, 1040), (2200, 1120), (2470, 1260), (2880, 1410),
         (2850, 1520), (2360, 1510), (2050, 1430), (1740, 1390), (1620, 1260)],
        fill=255,
    )
    body_intent.save(ROOT / "masks" / "4311_body_intent_mask.png")

    body_authorization = Image.new("L", source.size, 0)
    ImageDraw.Draw(body_authorization).polygon(
        [(1400, 960), (2260, 900), (3030, 1080), (3130, 1600),
         (1280, 1600), (1260, 1210)],
        fill=255,
    )
    body_authorization.save(ROOT / "masks" / "4311_body_authorization_mask.png")

    body_authorization_v2 = Image.new("L", source.size, 0)
    ImageDraw.Draw(body_authorization_v2).polygon(
        [(1400, 960), (2260, 900), (2920, 1080), (2990, 1600),
         (1280, 1600), (1260, 1210)],
        fill=255,
    )
    body_authorization_v2.save(ROOT / "masks" / "4311_body_authorization_mask_v2.png")

    body_authorization_v3 = Image.new("L", source.size, 0)
    ImageDraw.Draw(body_authorization_v3).polygon(
        [(1330, 900), (1840, 860), (2230, 1040), (2270, 1600),
         (1290, 1600), (1280, 1160)],
        fill=255,
    )
    body_authorization_v3.save(ROOT / "masks" / "4311_body_authorization_mask_v3.png")

    environment_4323_intent = Image.new("L", source.size, 0)
    environment_draw = ImageDraw.Draw(environment_4323_intent)
    environment_draw.rounded_rectangle((710, 750, 780, 830), radius=10, fill=255)
    environment_draw.rounded_rectangle((800, 770, 900, 835), radius=12, fill=255)
    environment_draw.ellipse((915, 750, 995, 835), fill=255)
    environment_4323_intent.save(ROOT / "masks" / "4323_environment_intent_mask_a1.png")

    desk_grid = source.crop((512, 384, 1536, 1408)).copy()
    grid_draw = ImageDraw.Draw(desk_grid)
    for x in range(600, 1501, 100):
        local_x = x - 512
        grid_draw.line((local_x, 0, local_x, 1024), fill=(0, 220, 255, 150), width=1)
        grid_draw.text((local_x + 3, 4), str(x), fill=(0, 220, 255, 255))
    for y in range(400, 1401, 100):
        local_y = y - 384
        grid_draw.line((0, local_y, 1024, local_y), fill=(255, 190, 0, 150), width=1)
        grid_draw.text((4, local_y + 3), str(y), fill=(255, 190, 0, 255))
    desk_grid.save(ROOT / "review" / "SC4022_desk_coordinate_grid.png")


if __name__ == "__main__":
    main()
