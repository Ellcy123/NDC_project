from pathlib import Path

from PIL import Image


JOB = Path(__file__).resolve().parent
SOURCE = Image.open(JOB / "SC4003_item_4115_icon.png").convert("RGBA")
REVIEW = JOB / "icon_review"
REVIEW.mkdir(parents=True, exist_ok=True)

for size in (100, 120, 150):
    SOURCE.resize((size, size), Image.Resampling.LANCZOS).save(
        REVIEW / f"SC4003_item_4115_icon_{size}px_preview.png"
    )
