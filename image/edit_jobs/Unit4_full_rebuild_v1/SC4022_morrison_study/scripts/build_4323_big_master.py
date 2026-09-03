import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01_4323_environment_comp_v2" / "SC4022_4323_scene_v1.png"
OUTPUT_DIR = ROOT / "02_4323_environment_big"
MASTER = OUTPUT_DIR / "4323_environment_big_master.png"
REPORT = OUTPUT_DIR / "4323_environment_big_master.json"

# Includes the three left-side desk objects, their wear zone, and enough of the
# desk chair to make the reach relationship readable without an answer diagram.
CROP_RECT = (700, 700, 1790, 1160)
CORNER_RADIUS = 70
EDGE_FEATHER = 12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    crop = source.crop(CROP_RECT)

    alpha = Image.new("L", crop.size, 0)
    inset = EDGE_FEATHER * 2
    ImageDraw.Draw(alpha).rounded_rectangle(
        (inset, inset, crop.width - inset - 1, crop.height - inset - 1),
        radius=CORNER_RADIUS,
        fill=255,
    )
    alpha = alpha.filter(ImageFilter.GaussianBlur(EDGE_FEATHER))
    crop.putalpha(alpha)
    crop.save(MASTER)

    REPORT.write_text(
        json.dumps(
            {
                "recordId": "4323",
                "stage": "approved-source-extraction-for-observation-big",
                "source": {
                    "path": str(SOURCE.resolve()),
                    "sha256": sha256(SOURCE),
                },
                "cropRect": list(CROP_RECT),
                "cornerRadius": CORNER_RADIUS,
                "edgeFeather": EDGE_FEATHER,
                "output": {
                    "path": str(MASTER.resolve()),
                    "sha256": sha256(MASTER),
                    "size": list(crop.size),
                    "mode": crop.mode,
                },
                "semanticContract": [
                    "desk seat remains in the same frame as the left-side reach zone",
                    "inkwell, badge case, coaster, and handling wear remain visible",
                    "no handedness label, person label, or gun comparison is introduced",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
