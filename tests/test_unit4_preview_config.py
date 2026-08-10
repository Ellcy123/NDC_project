from __future__ import annotations

import json
import unittest
from pathlib import Path

from avg_editor_v2 import bootstrap_unit4_preview


REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = REPO_ROOT / "avg_editor_v2" / "data" / "table"


class Unit4PreviewBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows, cls.risks = bootstrap_unit4_preview.build_rows()

    def test_expected_row_counts(self) -> None:
        self.assertEqual(
            {
                "ChapterConfig": 5,
                "SceneConfig": 27,
                "ItemStaticData": 56,
                "NPCStaticData": 16,
                "NPCLoopData": 14,
                "TestimonyItem": 20,
                "DoubtConfig": 12,
                "ArtAssetConfig": 28,
            },
            {name: len(rows) for name, rows in self.rows.items()},
        )

    def test_generated_ids_do_not_collide_with_existing_non_unit4_rows(self) -> None:
        for table_name, incoming in self.rows.items():
            key = bootstrap_unit4_preview.TABLE_KEYS[table_name]
            existing = json.loads((TABLE_DIR / f"{table_name}.json").read_text(encoding="utf-8"))
            incoming_ids = {str(row[key]) for row in incoming}
            existing_u4 = {
                str(row[key])
                for row in existing
                if row.get("Chapter") == "EPI04"
                or str(row.get(key, "")).startswith("4")
                or "EPI04" in str(row.get(key, ""))
            }
            self.assertFalse(incoming_ids & ({str(row[key]) for row in existing} - existing_u4))

    def test_merge_is_idempotent(self) -> None:
        incoming = self.rows["ChapterConfig"]
        merged_once = bootstrap_unit4_preview.merge_rows([], incoming, "id")
        merged_twice = bootstrap_unit4_preview.merge_rows(merged_once, incoming, "id")
        self.assertEqual(merged_once, merged_twice)

    def test_all_cross_table_references_exist(self) -> None:
        items = {str(row["id"]) for row in self.rows["ItemStaticData"]}
        testimonies = {str(row["id"]) for row in self.rows["TestimonyItem"]}
        doubts = {str(row["id"]) for row in self.rows["DoubtConfig"]}
        scenes = {str(row["sceneId"]) for row in self.rows["SceneConfig"]}
        npcs = {str(row["id"]) for row in self.rows["NPCStaticData"]}

        for scene in self.rows["SceneConfig"]:
            self.assertTrue(set(scene.get("ItemIDs") or []) <= items)
            for info in scene.get("NPCInfos") or []:
                self.assertIn(str(info["NPC"]["id"]), npcs)

        for doubt in self.rows["DoubtConfig"]:
            for condition in doubt["condition"]:
                target = str(condition["param"])
                if str(condition["type"]) == "1":
                    self.assertIn(target, items)
                else:
                    self.assertIn(target, testimonies)

        for chapter in self.rows["ChapterConfig"]:
            self.assertIn(str(chapter["initScene"]), scenes)
            self.assertIn(str(chapter["explorationEntryScene"]), scenes)
            self.assertIn(str(chapter["exposeScene"]), scenes)
            self.assertIn(str(chapter["exposeNpcId"]), npcs)
            self.assertTrue({str(row["id"]) for row in chapter["doubts"]} <= doubts)
            for expose in chapter["exposes"]:
                if expose["testimony"] != "0":
                    self.assertIn(str(expose["testimony"]), testimonies)
                for material in expose["item"]:
                    self.assertIn(str(material), items | testimonies)

    def test_only_real_timeline_testimony_uses_timeline_enum(self) -> None:
        rows = {str(row["id"]): row for row in self.rows["TestimonyItem"]}
        self.assertEqual("Timeline", rows["4153001"]["triggerType"])
        self.assertEqual("415,4024,2236,2315", rows["4153001"]["triggerParam"])
        for testimony_id in ("4041001", "4114001", "4114002"):
            self.assertEqual("None", rows[testimony_id]["triggerType"])

        conditions = {
            str(condition["param"]): str(condition["type"])
            for doubt in self.rows["DoubtConfig"]
            for condition in doubt["condition"]
            if str(condition["param"]) in rows
        }
        self.assertEqual("3", conditions["4153001"])
        self.assertEqual("4", conditions["4041001"])
        self.assertEqual("4", conditions["4114001"])
        self.assertEqual("4", conditions["4114002"])

    def test_loop5_has_identity_lock_and_non_loop_finale(self) -> None:
        loop5 = next(row for row in self.rows["ChapterConfig"] if row["id"] == "405")
        self.assertEqual([], loop5["doubts"])
        identity = loop5["specialMechanics"]["identityLock"]
        self.assertTrue(identity["replacesStandardDoubts"])
        self.assertEqual(["4501", "4502", "4503"], [chain["id"] for chain in identity["chains"]])
        self.assertEqual("all_chains_completed", identity["completionCondition"])
        self.assertEqual("expose", identity["unlocks"])

        finale = loop5["endingSequence"]
        self.assertFalse(finale["countsAsLoop"])
        self.assertEqual(5, finale["inheritLoop"])
        self.assertEqual("ending_4045", finale["chapterEndAfter"])
        self.assertEqual("enter_ohara_house", finale["nextUnitEntry"])
        self.assertEqual(["4043", "4044", "4045"], [scene["sceneId"] for scene in finale["scenes"]])

    def test_resolved_source_drift_is_not_reported(self) -> None:
        risk_text = "\n".join(self.risks)
        self.assertNotIn("4315", risk_text)
        self.assertNotIn("4418", risk_text)
        self.assertNotIn("4704", risk_text)

    def test_scene_art_requirements_follow_unit3_asset_card_style(self) -> None:
        banned = (
            "正式背景、环境音效与人物坐标待美术配置",
            "环境音：待音频配置",
            "人物精确坐标：待演出联调",
        )
        for scene in self.rows["SceneConfig"]:
            with self.subTest(scene_id=scene["sceneId"]):
                requirement = scene["ArtRequirement"]
                self.assertTrue(
                    requirement.startswith("【探索场景底图】")
                    or requirement.startswith("【完整 AVG 场景图】")
                )
                self.assertIn("- 时间版本：", requirement)
                self.assertIn("背景资源：u4_", requirement)
                self.assertIn("- 资产性质：", requirement)
                for phrase in banned:
                    self.assertNotIn(phrase, requirement)

    def test_special_scene_art_requirements_keep_multi_composition_boundaries(self) -> None:
        scenes = {str(row["sceneId"]): row for row in self.rows["SceneConfig"]}
        office = scenes["4042"]["ArtRequirement"]
        self.assertIn("u4_exp_mickey_office_night", office)
        self.assertIn("AVG 高潮演出补充", office)
        self.assertIn("不展示落地尸体", office)

        finale = scenes["4043"]["ArtRequirement"]
        self.assertIn("构图 A", finale)
        self.assertIn("构图 B", finale)
        self.assertIn("u4_l5_end_stairs_pickup_night", finale)
        self.assertIn("u4_l5_end_archive_van_night", finale)

    def test_scene_backgrounds_and_expose_backgrounds_are_preconfigured(self) -> None:
        scenes = {str(row["sceneId"]): row for row in self.rows["SceneConfig"]}
        art_ids = {str(row["id"]) for row in self.rows["ArtAssetConfig"]}
        for scene_id, scene in scenes.items():
            with self.subTest(scene_id=scene_id):
                background = scene["location"]["backgroundImage"]
                self.assertTrue(background.startswith("Art\\Scene\\Backgrounds\\EPI04\\u4_"))
                self.assertNotIn("PENDING", background)
                self.assertIn(background, art_ids)
                for extra_background in scene.get("previewBackgroundImages") or []:
                    self.assertIn(extra_background, art_ids)

        finale_backgrounds = scenes["4043"]["previewBackgroundImages"]
        self.assertEqual(2, len(finale_backgrounds))
        self.assertTrue(any("stairs_pickup" in value for value in finale_backgrounds))
        self.assertTrue(any("archive_van" in value for value in finale_backgrounds))

        for chapter in self.rows["ChapterConfig"]:
            with self.subTest(chapter=chapter["id"]):
                self.assertIn(chapter["topBg"], art_ids)
                self.assertEqual(
                    scenes[str(chapter["exposeScene"])]["location"]["backgroundImage"],
                    chapter["topBg"],
                )

    def test_art_asset_name_is_human_label_and_display_name_is_resource_name(self) -> None:
        assets = self.rows["ArtAssetConfig"]
        by_resource = {str(row["displayName"]): row for row in assets}
        for asset in assets:
            with self.subTest(asset_id=asset["id"]):
                resource_name = str(asset["id"]).rsplit("\\", 1)[-1]
                self.assertEqual(resource_name, asset["displayName"])
                self.assertNotEqual(asset["Name"], asset["displayName"])

        self.assertEqual("车站 214 号寄存区", by_resource["u4_exp_station_locker_night"]["Name"])
        self.assertEqual(
            "离开四十二层 / 法院档案车 · 构图 A",
            by_resource["u4_l5_end_stairs_pickup_night"]["Name"],
        )

    def test_npc_art_resources_are_preconfigured(self) -> None:
        for npc in self.rows["NPCStaticData"]:
            with self.subTest(npc=npc["id"]):
                self.assertTrue(str(npc["IconSmall"]).endswith("_small"))
                self.assertTrue(str(npc["IconLarge"]).endswith("_big"))

        for row in self.rows["NPCLoopData"]:
            with self.subTest(npc_loop=row["id"]):
                self.assertTrue(str(row["ResPath"]).startswith("Art\\Scene\\NPC\\EPI04\\SC"))
                self.assertTrue(str(row["ResPath"]).endswith("1"))
                self.assertTrue(str(row["ClickResPath"]).endswith("2"))

    def test_item_art_requirements_are_imported_from_production_cards(self) -> None:
        items = self.rows["ItemStaticData"]
        self.assertEqual(56, len(items))
        for item in items:
            with self.subTest(item_id=item["id"]):
                self.assertEqual(2, len(item["Name"]))
                self.assertEqual(2, len(item["Describe"]))
                self.assertEqual(2, len(item["ShortDescribe"]))
                self.assertTrue(all(str(value).strip() for value in item["Name"]))
                self.assertTrue(all(str(value).strip() for value in item["Describe"]))
                self.assertTrue(all(str(value).strip() for value in item["ShortDescribe"]))
                self.assertFalse(str(item["Name"][1]).startswith("u4_item_"))
                requirement = str(item["ArtRequirement"])
                self.assertTrue(requirement.startswith("【信息表达必不可少】\n"))
                self.assertIn("\n【风格参考】\n", requirement)
                self.assertNotIn("Unit4 预览占位", requirement)

        item_map = {str(item["id"]): item for item in items}
        item_4316 = item_map["4316"]
        self.assertNotIn("previewEvidenceStates", item_4316)
        self.assertIn("爆炸前", item_4316["ArtRequirement"])
        self.assertIn("不制作成 4316 的第二套详情状态", item_4316["ArtRequirement"])

        item_4111 = item_map["4111"]
        self.assertEqual("4003", item_4111["sourceScene"])
        self.assertEqual("minigame_output", item_4111["obtainMethod"])
        self.assertNotIn("4122", item_map)
        self.assertNotIn("4123", item_map)

        self.assertEqual("clue", item_map["4315"]["sourceStateType"])
        self.assertEqual("4027", item_map["4315"]["sourceScene"])
        self.assertEqual("key_item", item_map["4418"]["sourceStateType"])
        self.assertEqual("3", item_map["4418"]["itemType"])
        self.assertEqual("derived_memory", item_map["4704"]["sourceStateType"])

        for item_id in ("4511", "4512", "4514", "4515"):
            with self.subTest(identity_lock_input=item_id):
                self.assertEqual("false", item_map[item_id]["canAnalyzed"])
                self.assertEqual("manual", item_map[item_id]["obtainMethod"])
                self.assertNotIn("previewAnalysisRequired", item_map[item_id])

        for item_id in ("4117", "4118", "4212", "4213", "4214", "4703"):
            with self.subTest(batch_item=item_id):
                self.assertIn("SHC-28-B17", item_map[item_id]["ArtRequirement"])

    def test_standard_item_art_paths_and_special_dispositions_are_explicit(self) -> None:
        items = {str(item["id"]): item for item in self.rows["ItemStaticData"]}
        special_ids = {"4516", "4704", "4705", "4706", "4707", "4708", "4709"}
        for item_id, item in items.items():
            with self.subTest(item_id=item_id):
                if item_id in special_ids:
                    self.assertEqual("", item["folderPath"])
                    self.assertEqual("", item["desSpritePath"])
                    self.assertEqual("", item["mapSpritePath"])
                    self.assertEqual("", item["iconPath"])
                    self.assertIn(item["previewAssetMode"], {"minigame", "narrative_discovery"})
                    self.assertTrue(item["previewAssetNote"])
                    continue
                self.assertTrue(item["folderPath"].startswith("EPI04\\u4_"))
                self.assertTrue(item["desSpritePath"].endswith("_big"))
                self.assertTrue(item["mapSpritePath"].startswith(f"SC{item['sourceScene']}_"))
                self.assertEqual(f"{item['mapSpritePath']}_icon", item["iconPath"])

        for item_id in ("4704", "4705", "4706", "4707", "4708", "4709"):
            self.assertEqual("minigame", items[item_id]["previewAssetMode"])
        self.assertEqual("narrative_discovery", items["4516"]["previewAssetMode"])

    def test_identity_lock_inputs_keep_pre_acknowledgment_spoiler_boundary(self) -> None:
        items = {str(item["id"]): item for item in self.rows["ItemStaticData"]}
        for item_id in ("4513", "4515", "4516"):
            item = items[item_id]
            visible_text = "\n".join([*item["Name"], *item["Describe"], *item["ShortDescribe"]])
            with self.subTest(item_id=item_id):
                self.assertNotIn("Mickey", visible_text)
                self.assertNotIn("Michael F. Donnelly", visible_text)

        self.assertEqual("手写功业簿", items["4515"]["Name"][0])
        self.assertIn("W / Whale", items["4513"]["Describe"][0])
        self.assertIn("W / Whale", items["4516"]["Describe"][0])
        self.assertNotIn("接管人 Michael F. Donnelly", items["4513"]["ArtRequirement"])
        self.assertNotIn("Mickey 正式接管", items["4513"]["ArtRequirement"])


if __name__ == "__main__":
    unittest.main()
