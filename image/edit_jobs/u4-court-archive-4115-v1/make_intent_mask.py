from pathlib import Path

from PIL import Image, ImageDraw


JOB = Path(__file__).resolve().parent
MASK_DIR = JOB / "masks"
MASK_DIR.mkdir(parents=True, exist_ok=True)

# Tight planning envelope for the proposed ledger on the native 3140 x 1600 scene.
# This is an intent artifact only; the production authorization workspace is
# expanded deterministically by coordinate_patch.py.
INTENT_RECT = (1710, 820, 1960, 890)

mask = Image.new("L", (3140, 1600), 0)
ImageDraw.Draw(mask).rectangle(
    (INTENT_RECT[0], INTENT_RECT[1], INTENT_RECT[2] - 1, INTENT_RECT[3] - 1),
    fill=255,
)
mask.save(MASK_DIR / "intent_mask.png")
