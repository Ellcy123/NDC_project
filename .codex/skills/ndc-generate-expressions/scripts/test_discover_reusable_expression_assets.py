#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).with_name("discover_reusable_expression_assets.py")


class DiscoveryTests(unittest.TestCase):
    def test_same_character_exact_assets_are_found_and_cross_character_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for profile, mode in (("透明", "RGBA"), ("绿幕", "RGB")):
                target = root / "Unit2表情" / profile / "mickey"
                target.mkdir(parents=True)
                Image.new(mode, (16, 16), (1, 2, 3, 0) if mode == "RGBA" else (0, 255, 43)).save(target / "mickey_authoritative.png")
            other = root / "Unit2表情" / "透明" / "lula"
            other.mkdir(parents=True)
            Image.new("RGBA", (16, 16)).save(other / "lula_authoritative.png")
            repeated = root / "Unit2表情" / "绿幕" / "emma表情"
            repeated.mkdir(parents=True)
            Image.new("RGB", (16, 16), (0, 255, 43)).save(repeated / "emma_calm.png.png")
            manifest = root / "manifest.json"
            output = root / "out.json"
            manifest.write_text(
                json.dumps(
                    {
                        "search_roots": [str(root)],
                        "characters": [
                            {
                                "character_id": "mickey_donnelly",
                                "aliases": ["mickey"],
                                "requirements": ["authoritative"],
                            },
                            {"character_id": "emma", "aliases": ["emma"], "requirements": ["calm"]}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(manifest), "--output", str(output)], check=True)
            row = json.loads(output.read_text(encoding="utf-8"))["rows"][0]
            self.assertEqual(row["status"], "EXACT_CANDIDATE_FOUND")
            self.assertEqual(len(row["candidates"]), 2)
            self.assertTrue(all("lula" not in item["path"] for item in row["candidates"]))
            emma = json.loads(output.read_text(encoding="utf-8"))["rows"][1]
            self.assertEqual(emma["status"], "EXACT_CANDIDATE_FOUND")
            self.assertEqual(len(emma["candidates"]), 1)


if __name__ == "__main__":
    unittest.main()
