import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import configure_unit3_preview_dialogue as configurer


class ConfigureUnit3PreviewDialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene_rows = json.loads(
            configurer.SCENE_CONFIG.read_text(encoding="utf-8-sig")
        )
        cls.chapter_rows = json.loads(
            configurer.CHAPTER_CONFIG.read_text(encoding="utf-8-sig")
        )

    def configured_tables(self):
        scenes = copy.deepcopy(self.scene_rows)
        chapters = copy.deepcopy(self.chapter_rows)
        configurer.apply_configuration(scenes, chapters)
        return scenes, chapters

    def test_scene_npc_talk_entries_use_generated_files_and_first_ids(self):
        scenes, _ = self.configured_tables()
        expected = {
            (1, "303"): ("L1_scene3004_morrison", "303001001"),
            (1, "304"): ("L1_scene3005_foster", "304001001"),
            (2, "302"): ("L2_scene3013_mary", "302002001"),
            (2, "309"): ("L2_scene3007_priest", "309002001"),
            (3, "305"): ("L3_scene3008_helen_encounter", "305003001"),
            (3, "306"): ("L3_scene3009_bernard", "306003001"),
            (3, "308"): ("L3_scene3006_seamus", "308003001"),
            (4, "304"): ("L4_scene3005_foster", "304004001"),
            (4, "305"): ("L4_scene3008_helen_opening", "305004001"),
            (4, "307"): ("L4_scene3010_margaret", "307004001"),
            (5, "305"): ("L5_scene3008_helen", "305005001"),
            (5, "306"): ("L5_scene3014_bernard", "306005001"),
            (6, "304"): ("L6_scene3005_foster", "304006001"),
            (6, "308"): ("L6_scene3006_seamus", "308006001"),
        }
        actual = {}
        for row in scenes:
            if row.get("Chapter") != "EPI03":
                continue
            for info in row.get("NPCInfos", []):
                npc_id = str(info.get("NPC", {}).get("id", ""))
                if (row.get("loop"), npc_id) in expected:
                    talk = info["TalkInfo"]
                    actual[(row["loop"], npc_id)] = (
                        talk["videoScene"],
                        str(talk["id"]),
                    )
        self.assertEqual(expected, actual)

    def test_mickey_todo_entries_are_cleared_when_no_talk_exists(self):
        scenes, _ = self.configured_tables()
        for row in scenes:
            if row.get("Chapter") != "EPI03" or row.get("loop") not in (5, 6):
                continue
            for info in row.get("NPCInfos", []):
                if str(info.get("NPC", {}).get("id")) == "301":
                    self.assertEqual({}, info.get("TalkInfo"))

    def test_chapter_opening_and_expose_rounds_use_generated_ids(self):
        _, chapters = self.configured_tables()
        by_id = {row["id"]: row for row in chapters}
        self.assertEqual("310001001", by_id["301"]["initTalk"])
        self.assertEqual("310006001", by_id["306"]["initTalk"])
        self.assertEqual(
            ["320007", "320021", "320036"],
            [entry["talkId"] for entry in by_id["302"]["exposes"]],
        )
        self.assertEqual(
            ["360012", "360024", "360036", "360064", "360112"],
            [entry["talkId"] for entry in by_id["306"]["exposes"]],
        )

    def test_post_expose_segments_use_real_dialogue_entries(self):
        _, chapters = self.configured_tables()
        by_id = {row["id"]: row for row in chapters}
        self.assertEqual(
            [
                ("L4_postexpose_mickey", "301004001"),
                ("L4_postexpose_mary", "302004001"),
            ],
            [
                (segment["videoScene"], segment["entryTalkId"])
                for segment in by_id["304"]["postExposeSegments"]
            ],
        )
        self.assertEqual(
            [
                ("L6_ending_emma", "311006001"),
                ("L6_ending_leonard", "314006001"),
            ],
            [
                (segment["videoScene"], segment["entryTalkId"])
                for segment in by_id["306"]["postExposeSegments"]
            ],
        )

    def test_unit3_preview_rows_have_no_dialogue_todos(self):
        scenes, chapters = self.configured_tables()
        unit3_rows = [row for row in scenes if row.get("Chapter") == "EPI03"]
        unit3_rows.extend(
            row for row in chapters if row.get("id") in {str(i) for i in range(301, 307)}
        )
        self.assertNotIn("TODO_L", json.dumps(unit3_rows, ensure_ascii=False))

    def test_written_tables_use_plain_utf8_without_bom(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "table.json"
            configurer.write_json(output, [{"name": "对白"}])
            self.assertNotEqual(b"\xef\xbb\xbf", output.read_bytes()[:3])
            with output.open("r", encoding="utf-8") as handle:
                self.assertEqual([{"name": "对白"}], json.load(handle))


if __name__ == "__main__":
    unittest.main()
