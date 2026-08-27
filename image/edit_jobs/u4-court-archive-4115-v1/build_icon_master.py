from pathlib import Path
import hashlib
import json

from PIL import Image, ImageFilter


JOB = Path(__file__).resolve().parent
SOURCE = JOB / "detail_master_exact.png"
MASTER_OUT = JOB / "icon_master_1040.png"
SUBJECT_MASK_OUT = JOB / "icon_subject_mask_1040.png"
SHADOW_MASK_OUT = JOB / "icon_shadow_mask_1040.png"
REPORT = JOB / "icon_master_provenance.json"

CANVAS_SIZE = (1040, 1040)
TARGET_WIDTH = 800
SHADOW_OFFSET = (-22, 30)
SHADOW_BLUR = 16

source = Image.open(SOURCE).convert("RGBA")
bbox = source.getchannel("A").getbbox()
if bbox is None:
    raise ValueError("Approved ledger master is empty")
subject = source.crop(bbox)
target_height = round(subject.height * TARGET_WIDTH / subject.width)
subject = subject.resize((TARGET_WIDTH, target_height), Image.Resampling.LANCZOS)

subject_x = round((CANVAS_SIZE[0] - subject.width) / 2)
subject_y = round((CANVAS_SIZE[1] - subject.height) / 2) - 12

subject_layer = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
subject_layer.alpha_composite(subject, (subject_x, subject_y))
subject_mask = subject_layer.getchannel("A")

shadow_mask = Image.new("L", CANVAS_SIZE, 0)
shadow_mask.paste(
    subject.getchannel("A"),
    (subject_x + SHADOW_OFFSET[0], subject_y + SHADOW_OFFSET[1]),
)
shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
shadow_mask = shadow_mask.point(lambda value: round(value * 0.34))

shadow_layer = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
shadow_layer.putalpha(shadow_mask)
combined = Image.alpha_composite(shadow_layer, subject_layer)

# Fully transparent pixels carry zero RGB before the canonical finalizer.
pixels = combined.load()
for y in range(combined.height):
    for x in range(combined.width):
        if pixels[x, y][3] == 0:
            pixels[x, y] = (0, 0, 0, 0)

combined.save(MASTER_OUT)
subject_mask.save(SUBJECT_MASK_OUT)
shadow_mask.save(SHADOW_MASK_OUT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


REPORT.write_text(
    json.dumps(
        {
            "version": 1,
            "method": "deterministic-flat-paper-icon-layout-from-approved-ledger-master",
            "source": {"path": str(SOURCE), "sha256": sha256(SOURCE)},
            "master": {"path": str(MASTER_OUT), "sha256": sha256(MASTER_OUT)},
            "subjectMask": {
                "path": str(SUBJECT_MASK_OUT),
                "sha256": sha256(SUBJECT_MASK_OUT),
            },
            "shadowMask": {
                "path": str(SHADOW_MASK_OUT),
                "sha256": sha256(SHADOW_MASK_OUT),
            },
            "canvasSize": list(CANVAS_SIZE),
            "subjectPlacement": [subject_x, subject_y, subject.width, subject.height],
            "shadowOffset": list(SHADOW_OFFSET),
            "shadowBlur": SHADOW_BLUR,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
