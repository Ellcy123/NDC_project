import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "12_4313_icon_a1"
GENERATED = JOB / "generated_icon_folder.png"
MASTER = JOB / "4313_folder_icon_master_1040.png"
SUBJECT_MASK = JOB / "4313_folder_icon_subject_mask_1040.png"
SHADOW_MASK = JOB / "4313_folder_icon_shadow_mask_1040.png"
REPORT = JOB / "4313_folder_icon_master.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    generated = Image.open(GENERATED).convert("RGB")
    width, height = generated.size
    sx = width / 1254.0
    sy = height / 1254.0

    def pt(x: int, y: int) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    subject = Image.new("L", generated.size, 0)
    ImageDraw.Draw(subject).polygon(
        [pt(225, 385), pt(730, 265), pt(1070, 737), pt(1045, 824),
         pt(500, 990), pt(416, 948), pt(270, 760)],
        fill=255,
    )

    shadow_region = Image.new("L", generated.size, 0)
    ImageDraw.Draw(shadow_region).polygon(
        [pt(174, 500), pt(520, 980), pt(970, 886), pt(870, 1018), pt(260, 1080)],
        fill=255,
    )
    grayscale = generated.convert("L")
    shadow_tone = grayscale.point(
        lambda value: max(0, min(175, round((174 - value) * 2.1)))
    )
    shadow = ImageChops.multiply(shadow_region, shadow_tone)
    shadow = ImageChops.multiply(shadow, ImageChops.invert(subject))

    clean_pixels = []
    for red, green, blue in generated.getdata():
        green = min(green, round(max(red, blue) * 1.05))
        clean_pixels.append((red, green, blue))
    clean_subject = Image.new("RGB", generated.size)
    clean_subject.putdata(clean_pixels)
    subject_rgba = clean_subject.convert("RGBA")
    subject_rgba.putalpha(subject)

    shadow_rgba = Image.new("RGBA", generated.size, (24, 20, 16, 0))
    shadow_rgba.putalpha(shadow)
    isolated = Image.new("RGBA", generated.size, (0, 0, 0, 0))
    isolated.alpha_composite(shadow_rgba)
    isolated.alpha_composite(subject_rgba)

    master = isolated.resize((1040, 1040), Image.Resampling.LANCZOS)
    subject_1040 = subject.resize((1040, 1040), Image.Resampling.LANCZOS)
    shadow_1040 = shadow.resize((1040, 1040), Image.Resampling.LANCZOS)

    master.save(MASTER)
    subject_1040.save(SUBJECT_MASK)
    shadow_1040.save(SHADOW_MASK)

    REPORT.write_text(
        json.dumps(
            {
                "recordId": "4313",
                "stage": "icon-semantic-master",
                "generatedMaster": {
                    "path": str(GENERATED.resolve()),
                    "sha256": sha256(GENERATED),
                    "size": list(generated.size),
                },
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
