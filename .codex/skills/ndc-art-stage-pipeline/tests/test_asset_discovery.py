import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "asset_discovery.py"
SPEC = importlib.util.spec_from_file_location("asset_discovery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssetDiscoveryTests(unittest.TestCase):
    def receipt(self, root, status="CONFIRMED_ABSENT"):
        index = root / "asset-index.json"
        index.write_text("{}", encoding="utf-8")
        return {
            "schema": MODULE.SCHEMA,
            "status": status,
            "checked_at": "2026-09-13T12:00:00+08:00",
            "scope": {
                "domain": "prop", "scene_id": "SC1", "revision": "r1",
                "item_id": "item-1", "pose_or_state": "default", "artifact_role": "master",
            },
            "freshness": {
                "scope_revision_sha256": "a" * 64,
                "asset_index": {"path": str(index), "sha256": MODULE.sha256(index)},
            },
            "searches": [
                {"root_role": role, "root_path": str(root), "query_ids": ["item-1"], "aliases": ["item-1"], "completed": True}
                for role in MODULE.ROOT_ROLES
            ],
            "candidates": [],
        }

    def test_complete_absence_allows_generation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = self.receipt(root)
            path = root / "receipt.json"; path.write_text(json.dumps(receipt), encoding="utf-8")
            self.assertEqual(MODULE.validate_receipt(path, expected_scope={**receipt["scope"], "scope_revision_sha256": "a" * 64}), [])

    def test_one_arbitrary_root_cannot_prove_absence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = self.receipt(root)
            receipt["searches"] = receipt["searches"][:1]
            path = root / "receipt.json"; path.write_text(json.dumps(receipt), encoding="utf-8")
            failures = MODULE.validate_receipt(path)
            self.assertTrue(any("required roots" in failure for failure in failures))

    def test_index_change_invalidates_absence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = self.receipt(root)
            path = root / "receipt.json"; path.write_text(json.dumps(receipt), encoding="utf-8")
            (root / "asset-index.json").write_text('{"new_candidate": true}', encoding="utf-8")
            failures = MODULE.validate_receipt(path)
            self.assertTrue(any("asset_index" in failure for failure in failures))

    def test_usable_candidate_blocks_regeneration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate.png"; candidate.write_bytes(b"image")
            receipt = self.receipt(root, "FOUND_USABLE")
            receipt["candidates"] = [{"root_role": "formal_delivery", "path": str(candidate), "sha256": MODULE.sha256(candidate), "dimensions": {"width": 10, "height": 20}}]
            path = root / "receipt.json"; path.write_text(json.dumps(receipt), encoding="utf-8")
            failures = MODULE.validate_receipt(path)
            self.assertTrue(any("must be reused" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
