from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont


JOB = Path(__file__).resolve().parent
MASTER = JOB / "detail_master_transparent.png"
TEXT_LAYER = JOB / "detail_exact_text_layer.png"
OUTPUT = JOB / "detail_master_exact.png"
REPORT = JOB / "detail_exact_text_provenance.json"

REGULAR = ImageFont.truetype(r"C:\Windows\Fonts\cour.ttf", 17)
BOLD = ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf", 18)
TITLE = ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf", 22)
INK = (48, 58, 61, 205)

master = Image.open(MASTER).convert("RGBA")
layer = Image.new("RGBA", master.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(layer)

# Exact puzzle-bearing typography only. The generated raster master already
# owns the physical paper, binding, ruled table, wear, and clerk marks.
draw.text((198, 222), "COURT FILE REVIEW INDEX", font=TITLE, fill=INK)
draw.text((170, 268), "CASE NO.", font=BOLD, fill=INK)
draw.text((325, 268), "CHECKED OUT", font=BOLD, fill=INK)
draw.text((510, 268), "RETURNED", font=BOLD, fill=INK)
draw.text((645, 268), "CLERK", font=BOLD, fill=INK)

draw.text((185, 344), "SACRED HEART PROGRAM DISPUTES - 7", font=BOLD, fill=INK)
draw.text((185, 525), "SOUTH SIDE PROPERTY RULINGS - 3", font=BOLD, fill=INK)
draw.text((185, 690), "OLD COMPENSATION RULINGS - 7", font=BOLD, fill=INK)

draw.text((835, 224), "CONTINUED", font=TITLE, fill=INK)
draw.text((812, 268), "CASE NO.", font=BOLD, fill=INK)
draw.text((967, 268), "CHECKED OUT", font=BOLD, fill=INK)
draw.text((1152, 268), "RETURNED", font=BOLD, fill=INK)
draw.text((1287, 268), "CLERK", font=BOLD, fill=INK)

layer.save(TEXT_LAYER)
Image.alpha_composite(master, layer).save(OUTPUT)


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
            "method": "approved-exact-typography-layer-over-illustrated-raster-master",
            "semanticMaster": {"path": str(MASTER), "sha256": sha256(MASTER)},
            "exactTextLayer": {"path": str(TEXT_LAYER), "sha256": sha256(TEXT_LAYER)},
            "output": {"path": str(OUTPUT), "sha256": sha256(OUTPUT)},
            "fontSources": [
                r"C:\Windows\Fonts\cour.ttf",
                r"C:\Windows\Fonts\courbd.ttf",
            ],
            "spoilerExclusions": [
                "No signer identity",
                "No Harrison signature attribution",
                "No total box",
                "No case-detail conclusion",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
