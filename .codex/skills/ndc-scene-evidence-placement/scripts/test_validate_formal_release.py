#!/usr/bin/env python3
"""Regression tests for validate_formal_release.py."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).with_name("validate_formal_release.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FormalReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = tempfile.TemporaryDirectory(prefix="ndc-formal-release-test-")
        self.root = Path(self.context.name)
        self.formal = self.root / "formal"
        self.stage = self.root / "formal_stage"
        self.formal.mkdir()
        self.stage.mkdir()
        self.names = {
            "preview": "SC4002_scene_preview.png",
            "map": "SC4002_item_4112.png",
            "big": "SC4002_item_4112_big.png",
            "icon": "SC4002_item_4112_icon.png",
        }
        self.parent = self.root / "accepted_parent.png"
        Image.new("RGBA", (40, 40), (7, 8, 9, 255)).save(self.parent)
        for index, name in enumerate(self.names.values(), 1):
            Image.new("RGBA", (12, 12), (index * 20, 30, 40, 255)).save(
                self.formal / name
            )
        with Image.open(self.formal / self.names["map"]) as map_source:
            map_image = map_source.convert("RGBA")
        with Image.open(self.parent) as parent_source:
            parent_image = parent_source.convert("RGBA")
        parent_image.paste(map_image, (12, 13))
        parent_image.save(self.parent)
        (self.formal / "XYposition.txt").write_text(
            "SC4002_item_4112 12,13\n", encoding="ascii"
        )
        shutil.copy2(self.formal / self.names["map"], self.stage / self.names["map"])
        shutil.copy2(self.formal / "XYposition.txt", self.stage / "XYposition.txt")
        hashes = {
            path.name: digest(path)
            for path in self.formal.iterdir()
            if path.is_file()
        }
        self.contract = {
            "version": 1,
            "kind": "ndc-formal-release-contract",
            "scenePreview": self.names["preview"],
            "additionalStateImages": [],
            "records": [
                {
                    "recordId": "4112",
                    "deliveryClass": "scene-pickup",
                    "classificationReason": "Clicked in the base exploration scene",
                    "sourceReferences": ["state/loop1_state.yaml", "ItemStaticData:4112"],
                    "iconPolicy": "required",
                    "assets": {
                        "map": self.names["map"],
                        "big": self.names["big"],
                        "icon": self.names["icon"],
                    },
                    "positions": [
                        {
                            "role": "map",
                            "stem": "SC4002_item_4112",
                            "x": 12,
                            "y": 13,
                            "assetSha256": hashes[self.names["map"]],
                            "acceptedParentImage": str(self.parent),
                            "acceptedParentSha256": digest(self.parent),
                        }
                    ],
                }
            ],
            "artifactSha256": hashes,
            "replicaScanRoots": [str(self.root)],
        }
        self.contract_path = self.root / "release_contract.json"
        self.write_contract()

    def tearDown(self) -> None:
        self.context.cleanup()

    def write_contract(self) -> None:
        self.contract_path.write_text(
            json.dumps(self.contract, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--folder",
                str(self.formal),
                "--release-contract",
                str(self.contract_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_contract_binds_roles_hashes_coordinates_and_replicas(self):
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["passed"])
        self.assertTrue(report["productionEligible"])
        self.assertEqual(2, len(report["activeReplicaChecks"]))

    def test_stale_active_replica_coordinate_blocks_release(self):
        (self.stage / "XYposition.txt").write_text(
            "SC4002_item_4112 99,88\n", encoding="ascii"
        )
        result = self.run_validator()
        self.assertEqual(2, result.returncode)
        self.assertIn("stale active replica coordinate", result.stdout)

    def test_visible_rgb_drift_with_unchanged_alpha_blocks_release(self):
        path = self.formal / self.names["map"]
        with Image.open(path) as source:
            image = source.convert("RGBA")
        alpha = image.getpixel((4, 5))[3]
        image.putpixel((4, 5), (255, 255, 255, alpha))
        image.save(path)
        changed_hash = digest(path)
        self.contract["artifactSha256"][self.names["map"]] = changed_hash
        self.contract["records"][0]["positions"][0]["assetSha256"] = changed_hash
        shutil.copy2(path, self.stage / self.names["map"])
        self.write_contract()
        result = self.run_validator()
        self.assertEqual(2, result.returncode)
        self.assertIn("visible RGB differs from accepted parent", result.stdout)

    def test_minigame_only_record_cannot_whitelist_evidence_assets(self):
        record = self.contract["records"][0]
        record["deliveryClass"] = "minigame-only"
        record["iconPolicy"] = "omit"
        self.write_contract()
        result = self.run_validator()
        self.assertEqual(2, result.returncode)
        self.assertIn("forbidden asset roles", result.stdout)

    def test_environment_record_forbids_icon(self):
        record = self.contract["records"][0]
        record["deliveryClass"] = "environment"
        record["iconPolicy"] = "omit"
        self.write_contract()
        result = self.run_validator()
        self.assertEqual(2, result.returncode)
        self.assertIn("forbidden asset roles", result.stdout)


if __name__ == "__main__":
    unittest.main()
