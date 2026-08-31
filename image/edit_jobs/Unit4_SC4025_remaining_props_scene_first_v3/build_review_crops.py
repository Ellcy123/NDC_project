from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent


def crop(source: Path, rect: tuple[int, int, int, int], output: Path) -> None:
    Image.open(source).convert("RGBA").crop(rect).save(output)


candidate = Image.open(ROOT / "01_4318_scene_insert" / "scene_candidate.png").convert("RGBA").crop((1620, 730, 2010, 910))
candidate.save(ROOT / "review" / "4318_candidate_close.png")
candidate.resize((1560, 720), Image.Resampling.NEAREST).save(ROOT / "review" / "4318_candidate_close_4x.png")
crop(
    Path("/Users/m4/project/NDC_project/image/edit_jobs/Unit4_SC4025_key_scene_inpaint_v2/delivery/scene_with_item.png"),
    (1620, 730, 2010, 910),
    ROOT / "review" / "4318_source_close.png",
)

candidate_4319 = Image.open(ROOT / "03_4319_scene_insert" / "scene_candidate.png").convert("RGBA").crop(
    (2260, 720, 2720, 940)
)
candidate_4319.save(ROOT / "review" / "4319_candidate_close.png")
candidate_4319.resize((1840, 880), Image.Resampling.NEAREST).save(
    ROOT / "review" / "4319_candidate_close_4x.png"
)
grid = candidate_4319.resize((1840, 880), Image.Resampling.NEAREST)
grid_draw = ImageDraw.Draw(grid, "RGBA")
for local_x in range(0, 461, 20):
    gx = local_x * 4
    grid_draw.line((gx, 0, gx, 880), fill=(255, 80, 80, 135), width=1)
    grid_draw.text((gx + 3, 3), str(2260 + local_x), fill=(255, 180, 180, 255))
for local_y in range(0, 221, 20):
    gy = local_y * 4
    grid_draw.line((0, gy, 1840, gy), fill=(80, 220, 255, 135), width=1)
    grid_draw.text((3, gy + 3), str(720 + local_y), fill=(160, 235, 255, 255))
grid.save(ROOT / "review" / "4319_candidate_grid_4x.png")
crop(
    ROOT / "delivery" / "scene_key_4318.png",
    (2260, 720, 2720, 940),
    ROOT / "review" / "4319_source_close.png",
)
