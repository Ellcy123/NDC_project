import hashlib
import json
from itertools import combinations
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
BASE = Path(r"D:\NDC_project\image\定稿\u4_exp_morrison_study_night_preblast.png")
FINAL = ROOT / "10_4313_scene_comp" / "SC4022_4313_delivery_scene.png"
OUTPUT = ROOT / "13_SC4022_parent_audit"
REPORT = OUTPUT / "sibling_hotspot_and_reconstruction_audit.json"
RECONSTRUCTED = OUTPUT / "SC4022_reconstructed_from_sibling_layers.png"

RECORDS = {
    "4323": ROOT / "01_4323_environment_comp_v2" / "4323_environment_map_layer.png",
    "4312": ROOT / "05_4312_scene_comp_v2" / "4312_note_map_layer.png",
    "4313": ROOT / "10_4313_scene_comp" / "4313_folder_map_layer.png",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_nonzero(mask: Image.Image) -> int:
    histogram = mask.convert("L").histogram()
    return mask.width * mask.height - histogram[0]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    base = Image.open(BASE).convert("RGBA")
    layers = {record_id: Image.open(path).convert("RGBA") for record_id, path in RECORDS.items()}

    pairwise = []
    for (left_id, left), (right_id, right) in combinations(layers.items(), 2):
        left_hotspot = left.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
        right_hotspot = right.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
        overlap = ImageChops.multiply(left_hotspot, right_hotspot)
        pixels = count_nonzero(overlap)
        pairwise.append(
            {
                "left": left_id,
                "right": right_id,
                "overlapPixels": pixels,
                "overlapBounds": list(overlap.getbbox()) if overlap.getbbox() else None,
                "passed": pixels == 0,
            }
        )

    reconstructed = base
    for record_id in ("4323", "4312", "4313"):
        reconstructed = Image.alpha_composite(reconstructed, layers[record_id])
    reconstructed.convert("RGB").save(RECONSTRUCTED)

    final = Image.open(FINAL).convert("RGB")
    reconstructed_rgb = reconstructed.convert("RGB")
    difference = ImageChops.difference(final, reconstructed_rgb)
    differing_pixels = count_nonzero(difference.convert("L"))
    reconstruction_passed = differing_pixels == 0

    report = {
        "version": 1,
        "sceneId": "4022",
        "alphaThreshold": 128,
        "records": {
            record_id: {
                "path": str(path.resolve()),
                "sha256": sha256(path),
            }
            for record_id, path in RECORDS.items()
        },
        "pairwiseHotspotAudit": pairwise,
        "reconstruction": {
            "base": {"path": str(BASE.resolve()), "sha256": sha256(BASE)},
            "final": {"path": str(FINAL.resolve()), "sha256": sha256(FINAL)},
            "reconstructed": {
                "path": str(RECONSTRUCTED.resolve()),
                "sha256": sha256(RECONSTRUCTED),
            },
            "differingPixels": differing_pixels,
            "passed": reconstruction_passed,
        },
        "passed": all(row["passed"] for row in pairwise) and reconstruction_passed,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SC4022 sibling audit: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"Report: {REPORT}")
    if not report["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
