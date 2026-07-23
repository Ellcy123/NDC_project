import sys
import re
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import assign_unit3_dialogue_ids as assigner
import sync_unit3_to_json as syncer


class Unit3DialoguePipelineTests(unittest.TestCase):
    FREE_INQUIRY_MENUS = {
        1: [
            ("L1_scene3005_foster", "foster_questions", "foster_questions_menu", "foster_merge", 3),
            ("L1_scene3004_morrison", "morrison_questions", "morrison_questions_menu", "morrison_merge", 2),
        ],
        2: [
            ("L2_scene3013_mary", "询问方向", "mary_questions_menu", "merge", 4),
            ("L2_scene3007_priest", "询问方向", "priest_questions_menu", "merge", 3),
        ],
        3: [
            ("L3_scene3008_helen_encounter", "询问方向", "helen_encounter_menu", "helen_encounter_merge", 2),
            ("L3_scene3008_helen_room", "helen_room_questions", "helen_room_questions_menu", "helen_room_merge", 2),
            ("L3_scene3009_bernard", "询问方式", "bernard_questions_menu", "bernard_merge", 3),
            ("L3_scene3006_seamus", "seamus_questions", "seamus_questions_menu", "seamus_merge", 3),
        ],
        4: [
            ("L4_scene3010_margaret", "margaret_followup", "margaret_questions_menu", "margaret_merge", 2),
            ("L4_scene3008_helen_opening", "补充追问", "helen_questions_menu", "helen_merge", 2),
        ],
        5: [
            ("L5_scene3014_bernard", "bernard_opening", "bernard_questions_menu", "bernard_opening_merge", 2),
            ("L5_scene3008_helen", "helen_consult_questions", "helen_questions_menu", "helen_merge", 2),
        ],
        6: [
            ("L6_scene3005_foster", "foster_questions", "foster_questions_menu", "foster_merge", 2),
            ("L6_scene3006_seamus", "seamus_oil_questions", "seamus_questions_menu", "seamus_merge", 2),
        ],
    }

    @staticmethod
    def source_section(loop, filename):
        source = assigner.UNIT_DIR / f"Loop{loop}_生成草稿.md"
        text = source.read_text(encoding="utf-8")
        marker = f"## Talk: {filename}.json"
        start = text.index(marker)
        next_header = re.search(r"^## (?:Talk|Expose):", text[start + len(marker):], re.M)
        end = (
            start + len(marker) + next_header.start()
            if next_header
            else len(text)
        )
        return text[start:end]

    def test_expected_section_counts(self):
        expected = {1: 4, 2: 4, 3: 6, 4: 7, 5: 5, 6: 6}
        for loop, count in expected.items():
            sections = assigner.build_numbered_sections(loop)
            self.assertEqual(count, len(sections), f"Loop{loop}")

    def test_expose_ids_use_unit3_prefix(self):
        self.assertEqual(310001, assigner.make_expose_id(1, 1))
        self.assertEqual(367001, assigner.make_expose_id(6, 7001))

    def test_expose_filenames_match_editor_loader(self):
        for loop in range(1, 7):
            sections = assigner.build_numbered_sections(loop)
            expose = [section for section in sections if section.kind == "Expose"]
            self.assertEqual(1, len(expose), f"Loop{loop}")
            self.assertTrue(
                expose[0].filename.startswith(f"Expose_L{loop}_"),
                expose[0].filename,
            )

    def test_all_generated_ids_are_unique(self):
        seen = set()
        for loop in range(1, 7):
            for section in assigner.build_numbered_sections(loop):
                for node in section.nodes:
                    self.assertNotIn(node.id, seen, f"duplicate id {node.id}")
                    seen.add(node.id)

    def test_helen_encounter_and_room_have_distinct_groups(self):
        sections = assigner.build_numbered_sections(3)
        starts = {
            section.filename: section.nodes[0].id
            for section in sections
            if section.kind == "Talk"
        }
        self.assertEqual(305003001, starts["L3_scene3008_helen_encounter"])
        self.assertEqual(305103001, starts["L3_scene3008_helen_room"])

    def test_all_speaker_headers_have_unit3_mapping(self):
        for loop in range(1, 7):
            source = assigner.UNIT_DIR / f"Loop{loop}_生成草稿.md"
            unknown = syncer.unknown_speakers(source)
            self.assertEqual([], unknown, f"Loop{loop}: {unknown}")

    def test_source_has_no_quoted_speaker_headers(self):
        malformed = []
        for loop in range(1, 7):
            source = assigner.UNIT_DIR / f"Loop{loop}_生成草稿.md"
            malformed.extend(syncer.quoted_speaker_headers(source))
        self.assertEqual([], malformed)

    def test_numbered_drafts_hide_descriptive_expose_headings(self):
        pattern = re.compile(
            r"^##\s+(?:§\d+\.?\s*)?Expose\s*[—\-–]+",
            flags=re.M,
        )
        for loop in range(1, 7):
            sections = assigner.build_numbered_sections(loop)
            rendered = assigner.render_numbered(loop, sections)
            self.assertIsNone(pattern.search(rendered), f"Loop{loop}")

    def test_free_inquiry_paths_return_to_menu_and_have_exit_option(self):
        for loop, menus in self.FREE_INQUIRY_MENUS.items():
            for filename, branch, menu, exit_label, topic_count in menus:
                section = self.source_section(loop, filename)
                self.assertIn(f"@branch {branch}", section, filename)
                self.assertIn(f"@label {menu}", section, filename)
                self.assertIn(
                    f'@opt "暂时没有别的问题了。" -> {exit_label}',
                    section,
                    filename,
                )
                self.assertEqual(
                    topic_count,
                    section.count(f"@goto {menu}"),
                    filename,
                )
                numbered = next(
                    item
                    for item in assigner.build_numbered_sections(loop)
                    if item.filename == filename
                )
                menu_node = next(
                    node for node in numbered.nodes if menu in node.labels
                )
                self.assertTrue(menu_node.branch_options, filename)
                self.assertEqual(
                    "暂时没有别的问题了。",
                    menu_node.branch_options[-1].text,
                    filename,
                )
                self.assertEqual(
                    topic_count + 1,
                    len(menu_node.branch_options),
                    filename,
                )

    def test_free_inquiry_menus_do_not_use_pagination_prompts(self):
        pagination_prompts = (
            "还有别的问题。",
            "继续问其他问题。",
            "返回前面的问题。",
            "返回问题列表。",
        )
        for loop, menus in self.FREE_INQUIRY_MENUS.items():
            for filename, _branch, _menu, _exit_label, _topic_count in menus:
                section = self.source_section(loop, filename)
                for prompt in pagination_prompts:
                    self.assertNotIn(prompt, section, filename)

    def test_l6_wrong_reasoning_returns_to_the_choice_prompt(self):
        section = next(
            section
            for section in assigner.build_numbered_sections(6)
            if section.filename == "L6_scene3005_foster"
        )
        prompt = next(
            node
            for node in section.nodes
            if "helen_lie_reason_prompt" in node.labels
        )
        self.assertTrue(prompt.branch_options)

    def test_variable_branch_parameters_preserve_every_option(self):
        expected_counts = {
            (1, "L1_scene3005_foster"): 4,
            (2, "L2_scene3013_mary"): 5,
        }
        for (loop, filename), expected_count in expected_counts.items():
            section = next(
                item
                for item in assigner.build_numbered_sections(loop)
                if item.filename == filename
            )
            parameters_by_id = syncer.branch_parameters_for_section(section)
            menu_node = next(node for node in section.nodes if node.branch_options)
            self.assertEqual(expected_count, len(parameters_by_id[str(menu_node.id)]))

    def test_generated_free_inquiry_paths_return_to_menu(self):
        avg_dir = SCRIPT_DIR.parent / "EPI03" / "Talk"
        for loop, menus in self.FREE_INQUIRY_MENUS.items():
            sections = {
                section.filename: section
                for section in assigner.build_numbered_sections(loop)
            }
            for filename, _branch, menu, _exit_label, topic_count in menus:
                section = sections[filename]
                menu_node = next(node for node in section.nodes if menu in node.labels)
                rows = {
                    str(row["id"]): row
                    for row in __import__("json").loads(
                        (avg_dir / f"loop{loop}" / f"{filename}.json").read_text(
                            encoding="utf-8"
                        )
                    )
                }
                returning_nodes = [node for node in section.nodes if node.goto == menu]
                self.assertEqual(topic_count, len(returning_nodes), filename)
                for node in returning_nodes:
                    self.assertEqual(
                        str(menu_node.id),
                        str(rows[str(node.id)]["next"]),
                        f"{filename} Talk {node.id}",
                    )

    def test_editor_prefers_variable_parameters_array(self):
        editor = (SCRIPT_DIR.parents[1] / "avg_editor_v2" / "index.html").read_text(
            encoding="utf-8"
        )
        array_reader = "Array.isArray(entry.Parameters)"
        legacy_reader = "entry[`ParameterStr${i}`]"
        self.assertIn(array_reader, editor)
        self.assertLess(editor.index(array_reader), editor.index(legacy_reader))


if __name__ == "__main__":
    unittest.main()
