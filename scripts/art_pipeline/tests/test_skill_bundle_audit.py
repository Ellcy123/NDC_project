import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_skill_bundles import audit


class SkillBundleAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill-bundle-audit-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        registry = self.root / "production" / "art_pipeline" / "skill_sources.json"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            json.dumps(
                {
                    "layout_policy": {"grandfathered_skills": ["demo"]},
                    "skills": [
                        {
                            "name": "demo",
                            "status": "centralized",
                            "owner_scope": "planning",
                            "path": ".codex/skills/demo",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.skill = self.root / ".codex" / "skills" / "demo"
        (self.skill / "references").mkdir(parents=True)
        (self.skill / "tests").mkdir()
        (self.skill / "agents").mkdir()
        (self.skill / "assets").mkdir()
        (self.skill / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    def test_historical_provenance_path_is_allowed_only_when_non_executable(self):
        reference = self.skill / "references" / "history.md"
        reference.write_text(
            "Historical provenance-only path, not executable: `D:/old/work/item.png`.\n",
            encoding="utf-8",
        )
        result = audit(self.root)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["historical_provenance_paths"]), 1)

        reference.write_text("Current input: `D:/old/work/item.png`.\n", encoding="utf-8")
        result = audit(self.root)
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["current_document_machine_paths"]), 1)

    def test_test_fixture_machine_path_is_a_hard_failure(self):
        (self.skill / "tests" / "test_demo.py").write_text(
            'ROOT = r"D:\\personal\\work"\n', encoding="utf-8"
        )
        result = audit(self.root)
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["test_fixture_machine_paths"]), 1)
        self.assertTrue(any("test fixture" in item for item in result["errors"]))

    def test_agents_and_asset_text_resources_are_scanned(self):
        (self.skill / "agents" / "openai.yaml").write_text(
            'instructions: "read C:/personal/instructions.md"\n', encoding="utf-8"
        )
        (self.skill / "assets" / "template.txt").write_text(
            "source=/Users/person/project/template.png\n", encoding="utf-8"
        )
        result = audit(self.root)
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["support_file_machine_paths"]), 2)
        self.assertTrue(all("support file" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
