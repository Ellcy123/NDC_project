import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FINAL_SCENE = ROOT / "02_4113_scene_insert" / "accepted_4113_scene.png"
STAGE = ROOT / "map_stage"
PADDING = 4

RECORDS = [
    {
        "itemId": "4112",
        "stem": "SC4002_item_4112",
        "layer": ROOT / "01_4112_scene_insert" / "extraction" / "4112_scene_derived_source_layer.png",
        "z": "-3",
    },
    {
        "itemId": "4113",
        "stem": "SC4002_item_4113",
        "layer": ROOT / "02_4113_scene_insert" / "extraction" / "4113_scene_derived_source_layer.png",
        "z": "-3",
    },
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    final_scene = Image.open(FINAL_SCENE).convert("RGB")
    masks = []
    manifest = {
        "sceneId": "4002",
        "sourceSceneSize": list(final_scene.size),
        "origin": "top-left",
        "alphaThreshold": 128,
        "padding": PADDING,
        "records": [],
    }

    for record in RECORDS:
        rgba = Image.open(record["layer"]).convert("RGBA")
        arr = np.asarray(rgba)
        alpha = arr[..., 3]
        ys, xs = np.where(alpha > 0)
        if not len(xs):
            raise RuntimeError(f"empty layer: {record['itemId']}")
        l = max(0, int(xs.min()) - PADDING)
        t = max(0, int(ys.min()) - PADDING)
        r = min(rgba.width, int(xs.max()) + 1 + PADDING)
        b = min(rgba.height, int(ys.max()) + 1 + PADDING)
        out_dir = STAGE / record["itemId"]
        out_dir.mkdir(parents=True, exist_ok=True)
        map_path = out_dir / f"{record['stem']}.png"
        rgba.crop((l, t, r, b)).save(map_path)

        overlay = final_scene.convert("RGBA")
        debug = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(debug)
        threshold = Image.fromarray(np.where(alpha >= 128, 255, 0).astype(np.uint8), "L")
        draw.bitmap((0, 0), threshold, fill=(255, 0, 80, 120))
        draw.rectangle((l, t, r - 1, b - 1), outline=(255, 230, 0, 255), width=3)
        Image.alpha_composite(overlay, debug).save(out_dir / f"{record['stem']}_hotspot_overlay.png")

        reference_rect = (max(0, l - 40), max(0, t - 40), min(rgba.width, r + 40), min(rgba.height, b + 40))
        rgba.crop(reference_rect).save(out_dir / f"{record['stem']}_scene_reference.png")
        masks.append(alpha >= 128)
        manifest["records"].append({
            "itemId": record["itemId"],
            "map": str(map_path.relative_to(ROOT)),
            "mapSha256": sha256(map_path),
            "rect": [l, t, r, b],
            "width": r - l,
            "height": b - t,
            "Position": [str(l), str(t), record["z"]],
            "hotspotPixels": int((alpha >= 128).sum()),
            "hotspotTarget": f"item {record['itemId']} paper only",
        })

    overlap = np.logical_and(masks[0], masks[1])
    manifest["siblingOverlapPixels"] = int(overlap.sum())
    if manifest["siblingOverlapPixels"] != 0:
        raise RuntimeError("SC4002 sibling hotspots overlap")
    with open(STAGE / "map_stage_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
