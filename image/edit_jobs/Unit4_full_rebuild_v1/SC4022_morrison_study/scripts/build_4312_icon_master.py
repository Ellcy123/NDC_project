import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "07_4312_icon_a1"
GENERATED = JOB / "generated_icon_note.png"
MASTER = JOB / "4312_note_icon_master_1040.png"
SUBJECT_MASK = JOB / "4312_note_icon_subject_mask_1040.png"
SHADOW_MASK = JOB / "4312_note_icon_shadow_mask_1040.png"
REPORT = JOB / "4312_note_icon_master.json"

CROP_RECT = (100, 280, 1020, 1200)
PASTE_OFFSET = (60, 60)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    generated = Image.open(GENERATED).convert("RGB")

    subject_full = Image.new("L", generated.size, 0)
    ImageDraw.Draw(subject_full).polygon(
        [(358, 341), (942, 415), (847, 1053), (178, 951)],
        fill=255,
    )

    shadow_region = Image.new("L", generated.size, 0)
    ImageDraw.Draw(shadow_region).polygon(
        [(146, 914), (860, 1000), (848, 1095), (126, 1012)],
        fill=255,
    )
    grayscale = generated.convert("L")
    shadow_tone = grayscale.point(
        lambda value: max(0, min(180, round((178 - value) * 2.2)))
    )
    shadow_full = ImageChops.multiply(shadow_region, shadow_tone)
    shadow_full = ImageChops.multiply(shadow_full, ImageChops.invert(subject_full))

    subject_rgb = generated.copy()
    clean_pixels = []
    for red, green, blue in subject_rgb.getdata():
        green = min(green, round(max(red, blue) * 1.05))
        clean_pixels.append((red, green, blue))
    subject_rgb.putdata(clean_pixels)
    subject_rgba = subject_rgb.convert("RGBA")
    subject_rgba.putalpha(subject_full)

    shadow_rgba = Image.new("RGBA", generated.size, (24, 20, 16, 0))
    shadow_rgba.putalpha(shadow_full)
    isolated = Image.new("RGBA", generated.size, (0, 0, 0, 0))
    isolated.alpha_composite(shadow_rgba)
    isolated.alpha_composite(subject_rgba)

    subject_crop = subject_full.crop(CROP_RECT)
    shadow_crop = shadow_full.crop(CROP_RECT)
    rgba_crop = isolated.crop(CROP_RECT)

    master = Image.new("RGBA", (1040, 1040), (0, 0, 0, 0))
    subject = Image.new("L", (1040, 1040), 0)
    shadow = Image.new("L", (1040, 1040), 0)
    master.alpha_composite(rgba_crop, PASTE_OFFSET)
    subject.paste(subject_crop, PASTE_OFFSET)
    shadow.paste(shadow_crop, PASTE_OFFSET)

    red, green, blue, alpha = master.split()
    transparent = ImageChops.invert(alpha.point(lambda value: 255 if value else 0))
    red = ImageChops.multiply(red, ImageChops.invert(transparent))
    green = ImageChops.multiply(green, ImageChops.invert(transparent))
    blue = ImageChops.multiply(blue, ImageChops.invert(transparent))
    master = Image.merge("RGBA", (red, green, blue, alpha))

    master.save(MASTER)
    subject.save(SUBJECT_MASK)
    shadow.save(SHADOW_MASK)

    REPORT.write_text(
        json.dumps(
            {
                "recordId": "4312",
                "stage": "icon-semantic-master",
                "generatedMaster": {
                    "path": str(GENERATED.resolve()),
                    "sha256": sha256(GENERATED),
                },
                "cropRect": list(CROP_RECT),
                "pasteOffset": list(PASTE_OFFSET),
                "output": {
                    "path": str(MASTER.resolve()),
                    "sha256": sha256(MASTER),
                    "size": [1040, 1040],
                    "mode": "RGBA",
                },
                "subjectMask": {
                    "path": str(SUBJECT_MASK.resolve()),
                    "sha256": sha256(SUBJECT_MASK),
                },
                "shadowMask": {
                    "path": str(SHADOW_MASK.resolve()),
                    "sha256": sha256(SHADOW_MASK),
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
