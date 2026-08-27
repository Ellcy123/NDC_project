from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


JOB = Path(__file__).resolve().parent
SOURCE = JOB / "detail_master_raw.png"
OUTPUT = JOB / "detail_master_transparent.png"
MASK = JOB / "detail_master_alpha_mask.png"
REPORT = JOB / "detail_master_extraction.json"

rgb_image = Image.open(SOURCE).convert("RGB")
rgb = np.asarray(rgb_image, dtype=np.float32)
value = rgb.mean(axis=2)
chroma = rgb.max(axis=2) - rgb.min(axis=2)

# The ledger is a single solid object. Authorize its observed outer contour,
# preserve that contour's eroded interior at full opacity, and use the known
# near-white neutral checker palette only in a narrow outer antialias band.
# This avoids turning harmless checker noise into alpha residue while retaining
# the generated paper, binding, wear, rules, and signatures byte-for-byte.
outer_points = [
    (123, 191),
    (650, 176),
    (705, 179),
    (758, 198),
    (806, 183),
    (852, 178),
    (1405, 190),
    (1420, 209),
    (1489, 883),
    (1472, 890),
    (832, 898),
    (786, 892),
    (748, 900),
    (56, 890),
    (49, 881),
]
outer = Image.new("L", rgb_image.size, 0)
ImageDraw.Draw(outer).polygon(outer_points, fill=255)
inner = outer.filter(ImageFilter.MinFilter(15))

outer_array = np.asarray(outer, dtype=np.float32) / 255.0
inner_array = np.asarray(inner, dtype=np.float32) / 255.0
edge_band = np.clip(outer_array - inner_array, 0.0, 1.0)

neutral = np.clip(1.0 - np.maximum(chroma - 4.0, 0.0) / 10.0, 0.0, 1.0)
bright = np.clip((value - 224.0) / 19.0, 0.0, 1.0)
edge_foreground = 1.0 - neutral * bright
alpha_float = np.maximum(inner_array, edge_band * edge_foreground)

# Remove the last baked-checker highlights immediately below the dark lower
# binding. This is limited to the observed bottom contour; beige page layers
# and the charcoal binding remain because they are materially darker and/or
# more chromatic than the neutral checker.
row_index = np.arange(rgb_image.height, dtype=np.float32)[:, None]
bottom_checker_residue = (row_index >= 870) & (value >= 226.0) & (chroma <= 12.0)
alpha_float[bottom_checker_residue] = 0.0

alpha_image = Image.fromarray(
    np.clip(np.rint(alpha_float * 255.0), 0, 255).astype(np.uint8), "L"
).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.6))
alpha = np.asarray(alpha_image, dtype=np.uint8)

# Decontaminate semitransparent fringe RGB by propagating the nearest opaque
# ledger-edge colors outward. This prevents the baked white checker from
# producing a light halo when the RGBA master is viewed on a dark background.
rgb_u8 = rgb.astype(np.uint8)
clean_rgb = rgb_u8.copy()
known = alpha >= 250
pending = (alpha > 0) & ~known

for _ in range(24):
    if not pending.any():
        break
    color_sum = np.zeros_like(clean_rgb, dtype=np.uint32)
    count = np.zeros(alpha.shape, dtype=np.uint16)

    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        src_y = slice(max(0, -dy), min(alpha.shape[0], alpha.shape[0] - dy))
        src_x = slice(max(0, -dx), min(alpha.shape[1], alpha.shape[1] - dx))
        dst_y = slice(max(0, dy), min(alpha.shape[0], alpha.shape[0] + dy))
        dst_x = slice(max(0, dx), min(alpha.shape[1], alpha.shape[1] + dx))
        neighbor_known = known[src_y, src_x]
        color_sum[dst_y, dst_x] += clean_rgb[src_y, src_x] * neighbor_known[..., None]
        count[dst_y, dst_x] += neighbor_known.astype(np.uint16)

    fill = pending & (count > 0)
    if not fill.any():
        break
    clean_rgb[fill] = np.rint(
        color_sum[fill] / count[fill][:, None]
    ).astype(np.uint8)
    known[fill] = True
    pending[fill] = False

rgba = np.dstack([clean_rgb, alpha])
rgba[alpha == 0, :3] = 0
Image.fromarray(rgba, "RGBA").save(OUTPUT)
Image.fromarray(alpha, "L").save(MASK)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


bbox = Image.fromarray(alpha, "L").getbbox()
REPORT.write_text(
    json.dumps(
        {
            "version": 1,
            "method": "deterministic-neutral-checkerboard-alpha-recovery",
            "source": str(SOURCE),
            "sourceSha256": sha256(SOURCE),
            "output": str(OUTPUT),
            "outputSha256": sha256(OUTPUT),
            "mask": str(MASK),
            "maskSha256": sha256(MASK),
            "size": list(rgb_image.size),
            "mode": "RGBA",
            "alphaBounds": list(bbox) if bbox else None,
            "transparentRgbZeroed": True,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
