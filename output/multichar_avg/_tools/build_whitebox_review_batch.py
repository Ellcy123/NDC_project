from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\NDC_project\output\multichar_avg\whitebox_review_batch_20260904")
OUT = ROOT / "review"
OUT.mkdir(parents=True, exist_ok=True)


def font(size: int):
    path = Path(r"C:\Windows\Fonts\arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


ITEMS = [
    ("SC2591 combined", "SC2591_combined_whitebox_v1.png", (0.46, 0.02, 1.0, 1.0)),
    ("SC2691 combined v2", "SC2691_combined_whitebox_v2.png", (0.00, 0.10, 0.62, 1.0)),
    ("SC2215 Earl idle", "SC2215_Earl_idle_whitebox_v1.png", (0.22, 0.22, 0.39, 0.69)),
    ("SC2215 Earl clicked", "SC2215_Earl_clicked_whitebox_v1.png", (0.22, 0.22, 0.39, 0.69)),
    ("SC2515 Earl idle", "SC2515_Earl_idle_whitebox_v1.png", (0.22, 0.22, 0.39, 0.69)),
    ("SC2515 Earl clicked", "SC2515_Earl_clicked_whitebox_v1.png", (0.22, 0.22, 0.39, 0.69)),
    ("SC2615 TideWater idle", "SC2615_TideWater_idle_whitebox_v1.png", (0.27, 0.14, 0.50, 0.82)),
    ("SC2615 TideWater clicked", "SC2615_TideWater_clicked_whitebox_v1.png", (0.27, 0.14, 0.50, 0.82)),
]

UI_SIDES = ["left", "right", "right", "right", "right", "right", "right", "right"]


def contain(im: Image.Image, box_w: int, box_h: int):
    copy = im.copy()
    copy.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
    return copy


def make_board(local: bool):
    cell_w = 850
    image_h = 470 if not local else 620
    label_h = 54
    margin = 28
    board = Image.new("RGB", (cell_w * 2 + margin * 3, (image_h + label_h) * 4 + margin * 5), "#202226")
    draw = ImageDraw.Draw(board)
    title_font = font(28)
    for index, (label, filename, crop_frac) in enumerate(ITEMS):
        col = index % 2
        row = index // 2
        x = margin + col * (cell_w + margin)
        y = margin + row * (image_h + label_h + margin)
        im = Image.open(ROOT / filename).convert("RGB")
        if local:
            w, h = im.size
            l, t, r, b = crop_frac
            im = im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
        thumb = contain(im, cell_w, image_h)
        px = x + (cell_w - thumb.width) // 2
        py = y + (image_h - thumb.height) // 2
        board.paste(thumb, (px, py))
        draw.rectangle((x, y, x + cell_w, y + image_h), outline="#70757d", width=2)
        draw.text((x + 8, y + image_h + 10), label, font=title_font, fill="white")
    suffix = "local_200_review" if local else "full_frame_review"
    path = OUT / f"U2_remaining_whiteboxes_{suffix}.png"
    board.save(path)
    return path


def make_ui_board():
    ui_source = Image.open(r"D:\NDC\Assets\Resources\Art\UI\AVG\left_BG.png").convert("RGBA")
    cell_w = 850
    image_h = 470
    label_h = 54
    margin = 28
    board = Image.new("RGB", (cell_w * 2 + margin * 3, (image_h + label_h) * 4 + margin * 5), "#202226")
    draw = ImageDraw.Draw(board)
    title_font = font(28)
    for index, ((label, filename, _), side) in enumerate(zip(ITEMS, UI_SIDES)):
        col = index % 2
        row = index // 2
        x = margin + col * (cell_w + margin)
        y = margin + row * (image_h + label_h + margin)
        im = Image.open(ROOT / filename).convert("RGBA")
        ui_w = round(im.height * ui_source.width / ui_source.height)
        ui = ui_source.resize((ui_w, im.height), Image.Resampling.LANCZOS)
        if side == "right":
            ui = ui.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        overlay.alpha_composite(ui, (0 if side == "left" else im.width - ui_w, 0))
        comp = Image.alpha_composite(im, overlay).convert("RGB")
        out_path = OUT / f"{Path(filename).stem}_ui-{side}-check.png"
        comp.save(out_path)
        thumb = contain(comp, cell_w, image_h)
        px = x + (cell_w - thumb.width) // 2
        py = y + (image_h - thumb.height) // 2
        board.paste(thumb, (px, py))
        draw.rectangle((x, y, x + cell_w, y + image_h), outline="#70757d", width=2)
        draw.text((x + 8, y + image_h + 10), f"{label} / UI {side}", font=title_font, fill="white")
    path = OUT / "U2_remaining_whiteboxes_actual_ui_review.png"
    board.save(path)
    return path


if __name__ == "__main__":
    print(make_board(False))
    print(make_board(True))
    print(make_ui_board())
