from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(r"D:\NDC_project\image\edit_jobs\unit4_epi04_sc4002")
DELIVERY = ROOT / "delivery"
ORIGINAL = Path(r"D:\NDC_project\image\定稿\u4_exp_harrison_outer_office_day.png")
FINAL = ROOT / "03-wastebasket-scene-recompose-v3" / "scene_with_wastebasket_candidate_v3.png"
BASE_REPORT = ROOT / "03-wastebasket-scene-recompose-v3" / "final_verification.json"
DRAWER_RECT = (413, 304, 686, 530)
BIN_RECT = (2092, 702, 2353, 977)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def equal(first: Image.Image, second: Image.Image) -> bool:
    return first.size == second.size and first.mode == second.mode and ImageChops.difference(first, second).getbbox() is None


def border_result(inner_path: Path, output_path: Path) -> dict[str, object]:
    inner = Image.open(inner_path).convert("RGBA")
    output = Image.open(output_path).convert("RGBA")
    expected = Image.new("RGBA", (inner.width + 24, inner.height + 24), (255, 255, 255, 255))
    expected.alpha_composite(inner, (12, 12))
    return {
        "passed": equal(expected, output),
        "innerSize": list(inner.size),
        "outputSize": list(output.size),
        "expectedBorderPixels": 12,
        "borderRGBA": [255, 255, 255, 255],
    }


def paste_reconstruct(base: Image.Image, crop: Image.Image, rect: tuple[int, int, int, int], expected: Image.Image) -> bool:
    composite = base.copy()
    composite.paste(crop, (rect[0], rect[1]))
    return equal(composite, expected)


def main() -> None:
    final = Image.open(FINAL).convert("RGB")
    original = Image.open(ORIGINAL).convert("RGB")
    scene_delivery = Image.open(DELIVERY / "scene_with_item.png").convert("RGB")
    drawer = Image.open(DELIVERY / "prop_sc4002_expense_drawer1.png").convert("RGB")
    wastebasket = Image.open(DELIVERY / "prop_sc4002_typewriter_wastebasket1.png").convert("RGB")
    base_report = json.loads(BASE_REPORT.read_text(encoding="utf-8"))
    manifest = json.loads((DELIVERY / "container_delivery_manifest.json").read_text(encoding="utf-8"))
    item_patch = json.loads((DELIVERY / "ItemStaticData.patch.json").read_text(encoding="utf-8"))
    scene_patch = json.loads((DELIVERY / "SceneConfig.patch.json").read_text(encoding="utf-8"))

    drawer_open = manifest["containers"][0]["open"]
    bin_open = manifest["containers"][1]["open"]
    draw_x = round(DRAWER_RECT[0] + (DRAWER_RECT[2] - DRAWER_RECT[0]) / 2 - drawer_open["width"] / 2) + drawer_open["anchor"]["nudgeX"]
    draw_y = round(DRAWER_RECT[1] + (DRAWER_RECT[3] - DRAWER_RECT[1]) / 2 - drawer_open["height"] / 2) + drawer_open["anchor"]["nudgeY"]
    bin_x = round(BIN_RECT[0] + (BIN_RECT[2] - BIN_RECT[0]) / 2 - bin_open["width"] / 2) + bin_open["anchor"]["nudgeX"]
    bin_y = round(BIN_RECT[1] + (BIN_RECT[3] - BIN_RECT[1]) / 2 - bin_open["height"] / 2) + bin_open["anchor"]["nudgeY"]

    assets = [path for path in DELIVERY.iterdir() if path.is_file() and path.name not in {"container_delivery_verification.json"}]
    hash_records = {path.name: {"path": str(path), "sha256": sha256(path)} for path in assets}
    chain_ids = {row["id"]: row for row in item_patch["upserts"]}
    checks = {
        "sourceAndFinalSizeModeMatch": original.size == final.size and original.mode == final.mode,
        "baseCoordinateVerificationPassed": base_report.get("outside_union_pixels_bit_identical") is True and base_report.get("manifest_chain_passed") is True and base_report.get("all_scan_reports_passed") is True,
        "deliveredSceneMatchesAcceptedFinal": equal(scene_delivery, final),
        "drawerType6ExactNativeCrop": equal(drawer, final.crop(DRAWER_RECT)),
        "wastebasketType6ExactNativeCrop": equal(wastebasket, final.crop(BIN_RECT)),
        "drawerType6PasteMatchesAcceptedFinal": paste_reconstruct(final, drawer, DRAWER_RECT, final),
        "wastebasketType6ReconstructsFinalFromCleanSource": paste_reconstruct(original, wastebasket, BIN_RECT, final),
        "drawerType7Border": border_result(DELIVERY / "prop_sc4002_expense_drawer2_inner.png", DELIVERY / "prop_sc4002_expense_drawer2.png"),
        "wastebasketType7Border": border_result(DELIVERY / "prop_sc4002_typewriter_wastebasket2_inner.png", DELIVERY / "prop_sc4002_typewriter_wastebasket2.png"),
        "drawerType7CoordinateDerivedFromCenterAnchor": [draw_x, draw_y] == [drawer_open["x"], drawer_open["y"]],
        "wastebasketType7CoordinateDerivedFromCenterAnchor": [bin_x, bin_y] == [bin_open["x"], bin_open["y"]],
        "drawerType7WithinScene": 0 <= drawer_open["x"] and 0 <= drawer_open["y"] and drawer_open["x"] + drawer_open["width"] <= final.width and drawer_open["y"] + drawer_open["height"] <= final.height,
        "wastebasketType7WithinScene": 0 <= bin_open["x"] and 0 <= bin_open["y"] and bin_open["x"] + bin_open["width"] <= final.width and bin_open["y"] + bin_open["height"] <= final.height,
        "runtimeChainComplete": chain_ids["4601"]["ActionParam"] == "4602" and chain_ids["4602"]["ActionParam"] == "4112" and chain_ids["4603"]["ActionParam"] == "4604" and chain_ids["4604"]["ActionParam"] == "4113",
        "sceneConfigBindsOnlyType6": scene_patch["ItemIDs"]["final"] == ["4601", "4603"] and "4602" not in scene_patch["ItemIDs"]["final"] and "4604" not in scene_patch["ItemIDs"]["final"],
        "containedItemsHaveNoFakeScenePosition": chain_ids["4112"]["Position"] == [] and chain_ids["4113"]["Position"] == [] and chain_ids["4112"]["mapSpritePath"] is None and chain_ids["4113"]["mapSpritePath"] is None,
        "bigAndIconAssetsExist": all((DELIVERY / name).is_file() for name in ["SC4002_item_4112_big.png", "SC4002_item_4112_icon.png", "SC4002_item_4113_big.png", "SC4002_item_4113_icon.png"]),
    }
    passed = all(value if isinstance(value, bool) else value.get("passed", False) for value in checks.values())
    report = {
        "version": 1,
        "deliveryClass": "container-state",
        "passed": passed,
        "source": {"path": str(ORIGINAL), "sha256": sha256(ORIGINAL), "size": list(original.size), "mode": original.mode},
        "acceptedFinalScene": {"path": str(FINAL), "sha256": sha256(FINAL), "size": list(final.size), "mode": final.mode},
        "checks": checks,
        "artifacts": hash_records,
        "officialAssetsUntouched": True,
    }
    (DELIVERY / "container_delivery_verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "checks": checks}, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
