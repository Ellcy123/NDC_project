from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01_4112_scene_insert" / "accepted_4112_scene.png"
CANDIDATE = ROOT / "02_4113_scene_insert" / "attempt_1" / "broad_candidate.png"
OUT_DIR = ROOT / "02_4113_scene_insert" / "extraction"
ROI = (2180, 775, 2360, 930)


def largest_component(binary):
    h, w = binary.shape
    seen = np.zeros_like(binary, dtype=bool)
    best = []
    for y in range(h):
        for x in range(w):
            if not binary[y, x] or seen[y, x]:
                continue
            q = deque([(x, y)])
            seen[y, x] = True
            comp = []
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for ny in range(max(0, cy - 1), min(h, cy + 2)):
                    for nx in range(max(0, cx - 1), min(w, cx + 2)):
                        if binary[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((nx, ny))
            if len(comp) > len(best):
                best = comp
    out = np.zeros_like(binary, dtype=bool)
    for x, y in best:
        out[y, x] = True
    return out


def fill_holes(binary):
    h, w = binary.shape
    exterior = np.zeros_like(binary, dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not binary[y, x] and not exterior[y, x]:
                exterior[y, x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not binary[y, x] and not exterior[y, x]:
                exterior[y, x] = True
                q.append((x, y))
    while q:
        cx, cy = q.popleft()
        for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
            if 0 <= nx < w and 0 <= ny < h and not binary[ny, nx] and not exterior[ny, nx]:
                exterior[ny, nx] = True
                q.append((nx, ny))
    return binary | ~exterior


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_im = Image.open(SOURCE).convert("RGB")
    candidate_im = Image.open(CANDIDATE).convert("RGB")
    source = np.asarray(source_im)
    candidate = np.asarray(candidate_im)
    l, t, r, b = ROI
    src_roi = source[t:b, l:r].astype(np.int16)
    dst_roi = candidate[t:b, l:r].astype(np.int16)
    delta = np.max(np.abs(dst_roi - src_roi), axis=2)
    warm_paper = (
        (dst_roi[..., 0] + dst_roi[..., 1] + dst_roi[..., 2] > 260)
        & (dst_roi[..., 0] > dst_roi[..., 2] + 18)
        & (delta > 30)
    )
    paper = fill_holes(largest_component(warm_paper))

    alpha = np.zeros((source.shape[0], source.shape[1]), dtype=np.uint8)
    alpha[t:b, l:r][paper] = 255
    shifted_rgb = np.zeros_like(candidate)
    shifted_alpha = np.zeros_like(alpha)
    shift_y = 14
    shifted_rgb[shift_y:] = candidate[:-shift_y]
    shifted_alpha[shift_y:] = alpha[:-shift_y]

    # Preserve the accepted basket rim/wires in front after the small registration bridge.
    rim = Image.new("L", (source.shape[1], source.shape[0]), 0)
    ImageDraw.Draw(rim).ellipse((2138, 880, 2304, 910), outline=255, width=7)
    wire_region = np.zeros_like(alpha, dtype=bool)
    source_luma = source.mean(axis=2)
    wire_region[880:920, 2130:2310] = source_luma[880:920, 2130:2310] < 78
    shifted_alpha[(np.asarray(rim) > 0) | wire_region] = 0
    component_window = shifted_alpha[790:930, 2150:2350] > 0
    component_window = largest_component(component_window)
    shifted_alpha[:] = 0
    shifted_alpha[790:930, 2150:2350][component_window] = 255
    alpha = shifted_alpha
    ys, xs = np.where(alpha > 0)
    if not len(xs):
        raise RuntimeError("4113 extraction produced an empty mask")

    rgba = np.zeros((source.shape[0], source.shape[1], 4), dtype=np.uint8)
    rgba[..., :3] = shifted_rgb
    rgba[..., 3] = alpha
    rgba[alpha == 0, :3] = 0
    Image.fromarray(rgba, "RGBA").save(OUT_DIR / "4113_scene_derived_source_layer.png")
    Image.fromarray(alpha, "L").save(OUT_DIR / "4113_object_alpha.png")
    Image.fromarray(alpha, "L").save(ROOT / "masks" / "4113_object_alpha.png")

    rebuilt = source.copy()
    rebuilt[alpha > 0] = shifted_rgb[alpha > 0]
    rebuilt_im = Image.fromarray(rebuilt, "RGB")
    rebuilt_im.save(OUT_DIR / "4113_rebuilt_scene.png")

    crop_rect = (2110, 730, 2420, 1010)
    rebuilt_im.crop(crop_rect).save(OUT_DIR / "4113_rebuilt_tight_crop.png")

    overlay = rebuilt_im.convert("RGBA")
    debug = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(debug)
    draw.bitmap((0, 0), Image.fromarray(alpha, "L"), fill=(255, 0, 80, 115))
    draw.rectangle((xs.min(), ys.min(), xs.max(), ys.max()), outline=(255, 230, 0, 255), width=3)
    Image.alpha_composite(overlay, debug).save(OUT_DIR / "4113_hotspot_overlay.png")

    print({
        "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "pixels": int((alpha >= 128).sum()),
        "roi": list(ROI),
        "reinsertCrop": list(crop_rect),
        "registrationBridge": {"dx": 0, "dy": shift_y},
    })


if __name__ == "__main__":
    main()
