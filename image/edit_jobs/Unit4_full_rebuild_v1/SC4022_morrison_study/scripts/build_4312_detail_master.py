import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "06_4312_big_a1"
BLANK = JOB / "generated_blank_note.png"
TEXT_LAYER = JOB / "4312_note_text_layer.png"
MASTER = JOB / "4312_note_big_master.png"
REPORT = JOB / "4312_note_big_master.json"
FONT = Path(r"C:\Windows\Fonts\Inkfree.ttf")

EXACT_TEXT = [
    "I took the money.",
    "I buried the old cases.",
    "I did it for myself.",
    "Now the files are coming out,",
    "and I cannot face what I have done.",
    "This is the only answer.",
]
SIGNATURE = "H. Morrison"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chroma_key(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    pixels = list(rgb.getdata())
    rgba = []
    for red, green, blue in pixels:
        strength = green - max(red, blue)
        if strength >= 95:
            alpha = 0
        elif strength <= 28:
            alpha = 255
        else:
            alpha = round(255 * (95 - strength) / (95 - 28))
        if alpha:
            green = min(green, round(max(red, blue) * 1.08))
        rgba.append((red, green, blue, alpha))
    output = Image.new("RGBA", rgb.size)
    output.putdata(rgba)
    return output


def main() -> None:
    blank = Image.open(BLANK)
    paper = chroma_key(blank)

    text_layer = Image.new("RGBA", paper.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    font_size = max(34, round(paper.height * 0.032))
    body_font = ImageFont.truetype(str(FONT), font_size)
    signature_font = ImageFont.truetype(str(FONT), round(font_size * 1.12))
    ink = (39, 44, 42, 222)

    start_x = round(paper.width * 0.18)
    start_y = round(paper.height * 0.22)
    line_step = round(font_size * 1.55)
    for index, line in enumerate(EXACT_TEXT):
        draw.text((start_x, start_y + index * line_step), line, font=body_font, fill=ink)
    draw.text(
        (round(paper.width * 0.57), start_y + round(7.4 * line_step)),
        SIGNATURE,
        font=signature_font,
        fill=ink,
    )
    text_layer.save(TEXT_LAYER)

    master = paper.copy()
    master.alpha_composite(text_layer)
    master.save(MASTER)

    REPORT.write_text(
        json.dumps(
            {
                "recordId": "4312",
                "stage": "detail-big-semantic-master",
                "physicalMaster": {
                    "path": str(BLANK.resolve()),
                    "sha256": sha256(BLANK),
                },
                "textLayer": {
                    "path": str(TEXT_LAYER.resolve()),
                    "sha256": sha256(TEXT_LAYER),
                    "font": str(FONT),
                    "text": EXACT_TEXT,
                    "signature": SIGNATURE,
                },
                "output": {
                    "path": str(MASTER.resolve()),
                    "sha256": sha256(MASTER),
                    "size": list(master.size),
                    "mode": master.mode,
                },
                "contentBoundary": {
                    "firstPersonGuiltAndCollapse": True,
                    "mentionsGasExplosionOrAttack": False,
                    "containsForgedLabel": False,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
