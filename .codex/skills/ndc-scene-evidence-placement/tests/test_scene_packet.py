import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scene_packet.py"
SPEC = importlib.util.spec_from_file_location("scene_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ScenePacketTests(unittest.TestCase):
    def test_packet_contains_only_scene_and_parent_closure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            content = {"items": {
                "p": {"requirements": {"identity": {"level": "A", "value": "paper", "source": "canon"}}},
                "q": {"requirements": {"identity": {"level": "A", "value": "safe", "source": "canon"}}},
            }}
            content_path = root / "content.json"
            content_path.write_text(json.dumps(content), encoding="utf-8")
            index = {
                "scenes": {"s": {"artifact_ids": ["scene"], "item_ids": ["p"]}},
                "relations": [{"id": "shared", "kind": "shared_identity", "item_ids": ["p", "q"],
                               "artifact_ids": [], "consumer_scene_ids": [], "fact_refs": []}],
            }
            index_path = root / "index.json"
            index_path.write_text(json.dumps(index), encoding="utf-8")
            batch = {
                "batch_id": "x",
                "content_archive": "content.json",
                "scope": {"required_artifacts": ["master", "q_master", "scene", "other"]},
                "artifacts": {
                    "master": {"item_ids": ["p"], "stage": 2, "status": "PASS", "rejected": False, "parents": [], "sha256": "a" * 64},
                    "q_master": {"item_ids": ["q"], "stage": 2, "status": "PASS", "rejected": False, "parents": [], "sha256": "b" * 64},
                    "scene": {"item_ids": ["p"], "stage": 3, "status": "PENDING", "rejected": False, "parents": ["master"]},
                    "other": {"item_ids": ["q"], "stage": 3, "status": "PENDING", "rejected": False, "parents": []},
                },
                "scene_release_index": {"path": str(index_path), "sha256": MODULE.sha256(index_path)},
            }
            batch_path = root / "batch.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            result = MODULE.build(batch_path, "s")
            self.assertEqual(result["required_artifacts"], ["master", "q_master", "scene"])
            self.assertNotIn("other", result["blocked_artifacts"])
            self.assertEqual(result["next_actions"], ["resolve scene"])
            self.assertEqual(result["production_item_ids"], ["p", "q"])
            self.assertEqual(result["relation_ids"], ["shared"])


if __name__ == "__main__":
    unittest.main()
