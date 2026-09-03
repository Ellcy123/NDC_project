#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).with_name("remove_expression_background.py")


class RemoveExpressionBackgroundTests(unittest.TestCase):
    def test_preserves_enclosed_white_and_decontaminates_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            output = root / "output.png"
            audit = root / "audit.json"

            image = Image.new("RGB", (64, 64), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.ellipse((12, 8, 52, 60), fill=(30, 40, 50), outline=(205, 205, 205), width=2)
            draw.rectangle((26, 28, 38, 42), fill=(255, 255, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--audit",
                    str(audit),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            rgba = Image.open(output).convert("RGBA")
            self.assertEqual(rgba.getpixel((0, 0))[3], 0)
            self.assertEqual(rgba.getpixel((32, 35)), (255, 255, 255, 255))
            edge = rgba.getpixel((12, 32))
            self.assertGreater(edge[3], 0)
            self.assertLess(edge[3], 255)
            self.assertLess(max(edge[:3]), 200)
            record = json.loads(audit.read_text(encoding="utf-8"))
            self.assertFalse(record["image_model_used"])
            self.assertEqual(record["formal_status"], "NOT_CHECKED")


if __name__ == "__main__":
    unittest.main()
