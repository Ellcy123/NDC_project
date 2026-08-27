from pathlib import Path

from PIL import Image, ImageDraw


JOB = Path(__file__).resolve().parent
MASK_DIR = JOB / "masks"
MASK_DIR.mkdir(parents=True, exist_ok=True)

# Final composition workspace around the accepted ledger, its contact shadow,
# and the necessary tabletop patch. The accepted ledger's semantic bounds are
# approximately [1655, 813, 1845, 844); this mask leaves at least 64 native
# source pixels on every side and remains inside the parent authorization mask.
COMPOSITION_RECT = (1570, 740, 1930, 920)

mask = Image.new("L", (3140, 1600), 0)
ImageDraw.Draw(mask).rectangle(
    (
        COMPOSITION_RECT[0],
        COMPOSITION_RECT[1],
        COMPOSITION_RECT[2] - 1,
        COMPOSITION_RECT[3] - 1,
    ),
    fill=255,
)
mask.save(MASK_DIR / "composition_mask.png")
