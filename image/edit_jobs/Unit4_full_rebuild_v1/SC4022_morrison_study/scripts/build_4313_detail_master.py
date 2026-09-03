import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "11_4313_big_a1"
BLANK = JOB / "generated_blank_folder_notice.png"
TEXT_LAYER = JOB / "4313_notice_text_layer.png"
MASTER = JOB / "4313_folder_notice_big_master.png"
REPORT = JOB / "4313_folder_notice_big_master.json"
FONT = Path(r"C:\Windows\Fonts\courbd.ttf")

TITLE = "SURRENDER OF OLD CASE FILES AND FIREARM RECORDS"
AUTHORITY = "ISSUING AUTHORITY: COMMISSIONER PIERCE"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chroma_key(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    rgba = []
    for red, green, blue in rgb.getdata():
        dominant_green = green > 100 and green > red * 1.35 and green > blue * 1.35
        if dominant_green:
            strength = green - max(red, blue)
            alpha = 0 if strength >= 75 else round(255 * max(0, 75 - strength) / 40)
        else:
            alpha = 255
        if alpha and green > max(red, blue) * 1.15:
            green = min(green, round(max(red, blue) * 1.08))
        rgba.append((red, green, blue, max(0, min(255, alpha))))
    output = Image.new("RGBA", rgb.size)
    output.putdata(rgba)
    return output


def main() -> None:
    blank = Image.open(BLANK)
    physical = chroma_key(blank)

    block = Image.new("RGBA", (700, 205), (0, 0, 0, 0))
    draw = ImageDraw.Draw(block)
    header_font = ImageFont.truetype(str(FONT), 17)
    title_font = ImageFont.truetype(str(FONT), 23)
    body_font = ImageFont.truetype(str(FONT), 16)
    ink = (42, 48, 45, 225)
    blue = (50, 75, 95, 210)

    draw.text((18, 8), "CHICAGO POLICE DEPARTMENT", font=header_font, fill=ink)
    draw.text((18, 30), "RECORDS TRANSFER AUTHORITY", font=header_font, fill=ink)
    draw.text((18, 57), "SURRENDER OF OLD CASE FILES", font=title_font, fill=ink)
    draw.text((18, 85), "AND FIREARM RECORDS", font=title_font, fill=ink)
    draw.text((18, 119), AUTHORITY, font=body_font, fill=ink)
    draw.text((430, 40), "DATE / TIME:", font=body_font, fill=ink)

    blur_marks = Image.new("RGBA", block.size, (0, 0, 0, 0))
    blur_draw = ImageDraw.Draw(blur_marks)
    for x, width in ((548, 25), (579, 18), (603, 27), (636, 20)):
        blur_draw.rounded_rectangle((x, 43, x + width, 52), radius=4, fill=(38, 43, 41, 205))
    blur_marks = blur_marks.filter(ImageFilter.GaussianBlur(5))
    block.alpha_composite(blur_marks)

    draw = ImageDraw.Draw(block)
    draw.text((515, 12), "RECEIVED", font=header_font, fill=blue)
    rotated = block.rotate(10, resample=Image.Resampling.BICUBIC, expand=True)

    text_layer = Image.new("RGBA", physical.size, (0, 0, 0, 0))
    text_layer.alpha_composite(rotated, (430, 135))
    notice_mask = Image.new("L", physical.size, 0)
    ImageDraw.Draw(notice_mask).polygon(
        [(405, 235), (1018, 115), (1060, 302), (454, 392)],
        fill=255,
    )
    clipped_alpha = ImageChops.multiply(text_layer.getchannel("A"), notice_mask)
    text_layer.putalpha(clipped_alpha)
    text_layer.save(TEXT_LAYER)

    master = physical.copy()
    master.alpha_composite(text_layer)
    master.save(MASTER)

    REPORT.write_text(
        json.dumps(
            {
                "recordId": "4313",
                "stage": "detail-big-semantic-master",
                "physicalMaster": {
                    "path": str(BLANK.resolve()),
                    "sha256": sha256(BLANK),
                },
                "textLayer": {
                    "path": str(TEXT_LAYER.resolve()),
                    "sha256": sha256(TEXT_LAYER),
                    "font": str(FONT),
                    "title": TITLE,
                    "issuingAuthority": AUTHORITY,
                    "timestampPolicy": "DATE / TIME labels retained; digit area contains blurred non-numeric marks only.",
                },
                "output": {
                    "path": str(MASTER.resolve()),
                    "sha256": sha256(MASTER),
                    "size": list(master.size),
                    "mode": master.mode,
                },
                "contentBoundary": {
                    "containsSpecificDateOrTime": False,
                    "containsPresenceProofOrMurderOrder": False,
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
