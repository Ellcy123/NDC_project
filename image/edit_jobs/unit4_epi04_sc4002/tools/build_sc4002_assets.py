from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(r"D:\NDC_project\image\edit_jobs\unit4_epi04_sc4002")
FINAL_SCENE = ROOT / "03-wastebasket-scene-recompose-v3" / "scene_with_wastebasket_candidate_v3.png"
DRAWER_GENERATED = ROOT / "assets" / "drafts" / "expense_drawer_type7_generated.png"
BIN_GENERATED = ROOT / "assets" / "drafts" / "wastebasket_type7_generated.png"
DELIVERY = ROOT / "delivery"

DRAWER_RECT = (413, 304, 686, 530)
BIN_RECT = (2092, 702, 2353, 977)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "courbd.ttf" if bold else "cour.ttf"
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def paper_document(
    output: Path,
    title: str,
    subtitle: str,
    body: list[str],
    footer: str,
    kind: str,
) -> None:
    canvas = Image.new("RGBA", (1200, 1600), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((118, 104, 1082, 1510), radius=10, fill=(26, 18, 11, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow)

    paper = Image.new("RGB", (940, 1385), (227, 214, 179))
    grain = Image.effect_noise(paper.size, 18).convert("L")
    grain = ImageOps.colorize(grain, (199, 185, 152), (242, 231, 199))
    paper = Image.blend(paper, grain, 0.27)
    sheet = Image.new("RGBA", paper.size, (0, 0, 0, 0))
    sheet.paste(paper, (0, 0))
    d = ImageDraw.Draw(sheet)
    d.rectangle((0, 0, 939, 1384), outline=(82, 67, 49, 255), width=4)
    d.rectangle((26, 26, 913, 1358), outline=(132, 111, 82, 180), width=2)
    for y in range(190, 1280, 52):
        d.line((72, y, 868, y), fill=(111, 127, 126, 115), width=1)
    for y in (233, 563, 867):
        d.line((72, y, 868, y), fill=(68, 70, 67, 205), width=3)
    for y in range(130, 1250, 170):
        d.ellipse((13, y, 31, y + 18), fill=(51, 42, 32, 210))
        d.ellipse((16, y + 2, 27, y + 13), fill=(31, 25, 19, 255))

    if kind == "receipt":
        d.text((72, 66), "CITY BANK OF CHICAGO", fill=(36, 42, 43, 255), font=font(38, True))
        d.text((72, 122), "DEPOSIT RECEIPT  /  ARCHIVE COPY", fill=(57, 65, 66, 255), font=font(25, True))
        d.text((72, 285), "DATE:  APRIL 1919", fill=(28, 35, 37, 255), font=font(28))
        d.text((72, 342), "RECEIVED FROM:", fill=(30, 36, 36, 255), font=font(27, True))
        d.text((340, 342), "1919-A", fill=(23, 31, 34, 255), font=font(32, True))
        d.text((72, 414), "CREDITED TO:", fill=(30, 36, 36, 255), font=font(27, True))
        d.text((300, 414), "HARRISON PERSONAL ACCOUNT", fill=(23, 31, 34, 255), font=font(28, True))
        d.text((72, 625), "MEMO:", fill=(30, 36, 36, 255), font=font(27, True))
        d.text((72, 678), "SACRED HEART COMPENSATION CASES", fill=(23, 31, 34, 255), font=font(27, True))
        d.text((72, 742), "SHC-COMP-1919-04   /   SHC-COMP-1919-12", fill=(23, 31, 34, 255), font=font(24))
        d.text((72, 796), "SHC-COMP-1919-17", fill=(23, 31, 34, 255), font=font(24))
        d.rectangle((72, 930, 868, 1115), outline=(65, 70, 66, 190), width=2)
        d.text((92, 960), "Filed with ordinary income receipts.", fill=(64, 67, 63, 255), font=font(25))
        d.text((92, 1015), "No destruction or cancellation mark.", fill=(64, 67, 63, 255), font=font(25))
    else:
        d.text((72, 66), "HARRISON CHAMBERS", fill=(36, 42, 43, 255), font=font(38, True))
        d.text((72, 122), "UNFINISHED RESIGNATION DRAFT", fill=(57, 65, 66, 255), font=font(25, True))
        d.text((72, 285), "November 27, 1928", fill=(28, 35, 37, 255), font=font(28))
        d.text((72, 340), "To the Clerk of the Court,", fill=(28, 35, 37, 255), font=font(28))
        y = 440
        for line in body:
            d.text((92, y), line, fill=(24, 30, 33, 255), font=font(28))
            y += 58
        d.text((92, 850), "I intend to make these records public...", fill=(24, 30, 33, 255), font=font(28))
        d.text((92, 908), "", fill=(24, 30, 33, 255), font=font(28))
        d.line((92, 1002, 820, 1002), fill=(42, 45, 44, 210), width=2)
        d.text((92, 1030), "Signature:", fill=(45, 49, 48, 255), font=font(27))
        d.line((286, 1050, 755, 1050), fill=(45, 49, 48, 255), width=2)
        d.text((92, 1105), "UNSIGNED  /  NOT FILED", fill=(91, 71, 58, 255), font=font(27, True))

    d.text((72, 1300), footer, fill=(73, 65, 51, 230), font=font(21))
    canvas.alpha_composite(sheet, (130, 105))
    canvas.save(output)


def document_icon(document: Path, output: Path) -> None:
    source = Image.open(document).convert("RGBA")
    alpha = source.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"Empty alpha: {document}")
    object_image = source.crop(bbox)
    object_image.thumbnail((208, 208), Image.Resampling.LANCZOS)
    icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    icon.alpha_composite(object_image, ((256 - object_image.width) // 2, (256 - object_image.height) // 2))
    icon.save(output)


def overlay(scene: Image.Image, records: list[tuple[tuple[int, int, int, int], str, tuple[int, int, int, int]]]) -> Image.Image:
    result = scene.convert("RGBA")
    draw = ImageDraw.Draw(result, "RGBA")
    for rect, label, color in records:
        draw.rectangle(rect, outline=color, width=5)
        draw.rectangle((rect[0], max(0, rect[1] - 25), rect[0] + 235, max(0, rect[1] - 2)), fill=(20, 10, 35, 230))
        draw.text((rect[0] + 6, max(0, rect[1] - 22)), label, fill=(255, 255, 255, 255), font=font(17, True))
    return result


def main() -> None:
    DELIVERY.mkdir(parents=True, exist_ok=True)
    scene = Image.open(FINAL_SCENE).convert("RGB")
    if scene.size != (3060, 1600):
        raise ValueError(f"Unexpected scene size: {scene.size}")
    scene.save(DELIVERY / "scene_with_item.png")

    drawer_1 = scene.crop(DRAWER_RECT)
    bin_1 = scene.crop(BIN_RECT)
    drawer_1.save(DELIVERY / "prop_sc4002_expense_drawer1.png")
    bin_1.save(DELIVERY / "prop_sc4002_typewriter_wastebasket1.png")

    for source, output in (
        (DRAWER_GENERATED, DELIVERY / "prop_sc4002_expense_drawer2_inner.png"),
        (BIN_GENERATED, DELIVERY / "prop_sc4002_typewriter_wastebasket2_inner.png"),
    ):
        inner = Image.open(source).convert("RGB").resize((400, 400), Image.Resampling.LANCZOS)
        inner.save(output)

    receipt = DELIVERY / "SC4002_item_4112_big.png"
    draft = DELIVERY / "SC4002_item_4113_big.png"
    paper_document(
        receipt,
        "CITY BANK OF CHICAGO",
        "DEPOSIT RECEIPT",
        [],
        "Harrison Chambers archival filing / 1919",
        "receipt",
    )
    paper_document(
        draft,
        "HARRISON CHAMBERS",
        "UNFINISHED RESIGNATION DRAFT",
        [
            "I have reviewed the rulings and payments",
            "in which I took part.",
            "We cannot demand that others confess",
            "while continuing to deny our own part.",
        ],
        "Desk draft recovered from ordinary office waste / 1928",
        "draft",
    )
    document_icon(receipt, DELIVERY / "SC4002_item_4112_icon.png")
    document_icon(draft, DELIVERY / "SC4002_item_4113_icon.png")

    check_drawer = ImageChops.difference(drawer_1, scene.crop(DRAWER_RECT)).getbbox() is None
    check_bin = ImageChops.difference(bin_1, scene.crop(BIN_RECT)).getbbox() is None
    if not (check_drawer and check_bin):
        raise ValueError("Type 6 crops are not pixel-exact scene rectangles")

    (DELIVERY / "XYposition.txt").write_text(
        "prop_sc4002_expense_drawer1 413,304\n"
        "prop_sc4002_expense_drawer2 349,263\n"
        "prop_sc4002_typewriter_wastebasket1 2092,702\n"
        "prop_sc4002_typewriter_wastebasket2 2017,615\n",
        encoding="ascii",
    )

    items = {
        "patchVersion": 1,
        "operation": "staged-upserts-only; do-not-apply-to-formal-tables",
        "upserts": [
            {
                "id": "4601", "itemType": "6", "Name": ["Harrison普通费用抽屉", "Harrison Expense Drawer"],
                "ActionParam": "4602", "folderPath": "EPI04\\u4_exp_harrison_outer_office_day",
                "mapSpritePath": "prop_sc4002_expense_drawer1", "desSpritePath": None, "iconPath": None,
                "Position": ["413", "304", "-1"],
            },
            {
                "id": "4602", "itemType": "7", "Name": ["Harrison普通费用抽屉（打开）", "Harrison Expense Drawer (Open)"],
                "ActionParam": "4112", "folderPath": "EPI04\\u4_exp_harrison_outer_office_day",
                "mapSpritePath": "prop_sc4002_expense_drawer2", "desSpritePath": None, "iconPath": None,
                "Position": ["349", "263", "-1"],
            },
            {
                "id": "4603", "itemType": "6", "Name": ["打字机旁废纸篮", "Typewriter-Side Wastepaper Basket"],
                "ActionParam": "4604", "folderPath": "EPI04\\u4_exp_harrison_outer_office_day",
                "mapSpritePath": "prop_sc4002_typewriter_wastebasket1", "desSpritePath": None, "iconPath": None,
                "Position": ["2092", "702", "-1"],
            },
            {
                "id": "4604", "itemType": "7", "Name": ["打字机旁废纸篮（查看）", "Typewriter-Side Wastepaper Basket (Inspect)"],
                "ActionParam": "4113", "folderPath": "EPI04\\u4_exp_harrison_outer_office_day",
                "mapSpritePath": "prop_sc4002_typewriter_wastebasket2", "desSpritePath": None, "iconPath": None,
                "Position": ["2017", "615", "-1"],
            },
            {
                "id": "4112", "folderPath": "EPI04\\u4_exp_harrison_outer_office_day",
                "mapSpritePath": None, "desSpritePath": "SC4002_item_4112_big", "iconPath": "SC4002_item_4112_icon",
                "Position": [],
            },
            {
                "id": "4113", "folderPath": "EPI04\\u4_exp_harrison_outer_office_day",
                "mapSpritePath": None, "desSpritePath": "SC4002_item_4113_big", "iconPath": "SC4002_item_4113_icon",
                "Position": [],
            },
        ],
    }
    (DELIVERY / "ItemStaticData.patch.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scene_patch = {
        "patchVersion": 1,
        "sceneId": "4002",
        "operation": "replace-direct-contained-evidence-entrypoints",
        "ItemIDs": {"remove": ["4112", "4113"], "add": ["4601", "4603"], "final": ["4601", "4603"]},
        "constraint": "Only Type 6 IDs are bound by SceneConfig.",
    }
    (DELIVERY / "SceneConfig.patch.json").write_text(json.dumps(scene_patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    overlay(scene, [(DRAWER_RECT, "4601 Type 6", (255, 0, 220, 255)), (BIN_RECT, "4603 Type 6", (0, 230, 255, 255))]).save(DELIVERY / "container_position_overlay.png")
    contract = {
        "unit": "Unit4", "episode": "EPI04", "loop": 1, "sceneId": "4002",
        "sourceScene": {"path": str(FINAL_SCENE), "sha256": sha256(FINAL_SCENE), "size": list(scene.size), "mode": scene.mode},
        "idReservation": {"status": "allocated-in-staged-patch-only", "range": ["4601", "4604"], "formalTableModified": False},
        "containers": [
            {
                "closedItemId": "4601", "openItemId": "4602", "containedItemIds": ["4112"], "sceneConfigBinds": ["4601"],
                "closed": {"image": "prop_sc4002_expense_drawer1.png", "rect": list(DRAWER_RECT), "x": 413, "y": 304, "z": -1, "width": 273, "height": 226},
                "open": {"innerImage": "prop_sc4002_expense_drawer2_inner.png", "image": "prop_sc4002_expense_drawer2.png", "x": 349, "y": 263, "z": -1, "width": 424, "height": 424, "anchor": {"strategy": "closed-center", "nudgeX": 11, "nudgeY": 58, "centerOffsetX": 11, "centerOffsetY": 58}, "border": {"pixels": 12, "rgba": [255, 255, 255, 255], "appliedAfterFinalResize": True}},
            },
            {
                "closedItemId": "4603", "openItemId": "4604", "containedItemIds": ["4113"], "sceneConfigBinds": ["4603"],
                "closed": {"image": "prop_sc4002_typewriter_wastebasket1.png", "rect": list(BIN_RECT), "x": 2092, "y": 702, "z": -1, "width": 261, "height": 275},
                "open": {"innerImage": "prop_sc4002_typewriter_wastebasket2_inner.png", "image": "prop_sc4002_typewriter_wastebasket2.png", "x": 2017, "y": 615, "z": -1, "width": 424, "height": 424, "anchor": {"strategy": "closed-center", "nudgeX": 7, "nudgeY": -13, "centerOffsetX": 6.5, "centerOffsetY": -12.5}, "border": {"pixels": 12, "rgba": [255, 255, 255, 255], "appliedAfterFinalResize": True}},
            },
        ],
    }
    (DELIVERY / "container_delivery_manifest.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
