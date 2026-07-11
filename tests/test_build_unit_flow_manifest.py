from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from avg_editor_v2 import build_unit_flow


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "canon_manifest.json"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class UnitFlowManifestTests(unittest.TestCase):
    def test_unit_labels_come_from_manifest(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        labels = build_unit_flow.unit_labels_from_manifest(manifest)
        self.assertEqual({"1", "2"}, set(labels))
        self.assertEqual("Unit1", labels["1"]["key"])
        self.assertEqual("黑哨之夜", labels["1"]["title"])
        self.assertEqual("EPI01", labels["1"]["chapter"])
        self.assertEqual("Unit2", labels["2"]["key"])
        self.assertEqual("EPI02", labels["2"]["chapter"])

    def test_flow_alias_preserves_every_business_id(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        units = {
            "Unit1": {
                "unit": "Unit1",
                "formalUnit": "Unit1",
                "chapter": "EPI01",
                "title": "黑哨之夜",
                "loops": [
                    {
                        "id": "loop1",
                        "chapterId": "101",
                        "initTalk": "101001001",
                        "initScene": "1103",
                        "doubts": [{"id": "1101"}],
                    }
                ],
            }
        }
        result = build_unit_flow.apply_flow_aliases(units, manifest)
        self.assertEqual("Unit1", result["Unit9"]["formalUnit"])
        self.assertEqual("EPI01", result["Unit9"]["chapter"])
        self.assertEqual("101001001", result["Unit9"]["loops"][0]["initTalk"])
        self.assertEqual("1103", result["Unit9"]["loops"][0]["initScene"])
        self.assertEqual("1101", result["Unit9"]["loops"][0]["doubts"][0]["id"])
        self.assertNotIn("Unit10", result)

    def test_build_uses_temp_output_and_keeps_ids(self) -> None:
        formal_output = Path(build_unit_flow.OUT_PATH)
        before = formal_output.read_bytes() if formal_output.exists() else None
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            table_dir = temp / "table"
            table_dir.mkdir()
            write_json(
                table_dir / "ChapterConfig.json",
                [
                    {
                        "id": "101",
                        "chapterTitle": ["Fixture Loop"],
                        "initTalk": "101001001",
                        "initScene": "1103",
                        "doubts": [],
                        "exposes": [],
                        "postExposeSegments": [],
                    }
                ],
            )
            for table_name in (
                "SceneConfig",
                "ItemStaticData",
                "TestimonyItem",
                "ArtAssetConfig",
            ):
                write_json(table_dir / f"{table_name}.json", [])
            temp_output = temp / "unit_flow.json"
            payload = build_unit_flow.build(
                table_dir=str(table_dir),
                out_path=str(temp_output),
                manifest_path=str(MANIFEST_PATH),
            )
            self.assertTrue(temp_output.exists())
            self.assertEqual(
                "101001001", payload["units"]["Unit1"]["loops"][0]["initTalk"]
            )
            self.assertEqual(
                "101001001", payload["units"]["Unit9"]["loops"][0]["initTalk"]
            )
            self.assertEqual(
                "1103", payload["units"]["Unit9"]["loops"][0]["initScene"]
            )
        after = formal_output.read_bytes() if formal_output.exists() else None
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
