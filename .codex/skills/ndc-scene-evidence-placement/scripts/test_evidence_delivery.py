#!/usr/bin/env python3
"""Regression tests for evidence_delivery.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).with_name("evidence_delivery.py")


class EvidenceDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_context = tempfile.TemporaryDirectory(
            prefix="ndc-evidence-delivery-test-"
        )
        self.root = Path(self.temp_context.name)
        self.source = self.root / "source.png"
        self.final = self.root / "final.png"
        self.bad_final = self.root / "bad_final.png"
        self.mask = self.root / "authorization.png"
        self.base_report = self.root / "base_verification.json"

        source = Image.new("RGB", (64, 64), (40, 50, 60))
        source.save(self.source)

        final = source.copy()
        ImageDraw.Draw(final).rectangle((20, 22, 31, 29), fill=(180, 40, 25))
        final.save(self.final)

        bad_final = final.copy()
        bad_final.putpixel((2, 2), (255, 255, 255))
        bad_final.save(self.bad_final)

        mask = Image.new("L", (64, 64), 0)
        ImageDraw.Draw(mask).rectangle((20, 22, 31, 29), fill=255)
        mask.save(self.mask)

        self.base_report.write_text(
            json.dumps({"passed": True}) + "\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_context.cleanup()

    def command(self, final: Path, output: Path) -> list[str]:
        return [
            sys.executable,
            "-B",
            str(SCRIPT),
            "package",
            "--source-scene",
            str(self.source),
            "--final-scene",
            str(final),
            "--authorization-mask",
            str(self.mask),
            "--base-verification",
            str(self.base_report),
            "--map-padding",
            "0",
            "--item-id",
            "4317",
            "--scene-id",
            "4025",
            "--folder-path",
            r"EPI04\u4_exp_court_dispatch_night",
            "--map-stem",
            "SC4025_item_4317",
            "--detail-stem",
            "SC4025_item_4317_big",
            "--icon-stem",
            "SC4025_item_4317_icon",
            "--cutout-mask",
            str(self.mask),
            "--z=-3",
            "--output-dir",
            str(output),
        ]

    def test_auto_coordinates_package_and_verify(self) -> None:
        output = self.root / "delivery"
        packaged = subprocess.run(
            self.command(self.final, output),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(packaged.returncode, 0, packaged.stdout + packaged.stderr)

        manifest_path = output / "delivery_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertTrue(manifest["passed"])
        self.assertEqual(manifest["mapCrop"]["rect"], [20, 22, 32, 30])
        self.assertEqual(
            manifest["unityDraft"]["Position"], ["20", "22", "-3"]
        )

        with Image.open(self.final) as final, Image.open(
            output / "SC4025_item_4317.png"
        ) as map_sprite:
            expected = final.crop((20, 22, 32, 30)).convert("RGBA")
            actual = map_sprite.convert("RGBA")
            self.assertEqual(expected.size, actual.size)
            self.assertEqual(expected.tobytes(), actual.tobytes())

        verified = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "verify",
                "--manifest",
                str(manifest_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

        repeated = subprocess.run(
            self.command(self.final, output),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("already exist", repeated.stdout + repeated.stderr)

    def test_rejects_change_outside_authorization(self) -> None:
        output = self.root / "bad_delivery"
        packaged = subprocess.run(
            self.command(self.bad_final, output),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(packaged.returncode, 2, packaged.stdout + packaged.stderr)
        report = json.loads(
            (output / "delivery_verification.json").read_text(encoding="utf-8")
        )
        self.assertFalse(report["passed"])
        self.assertIn(
            "Original scene/package verification did not pass", report["failures"]
        )


if __name__ == "__main__":
    unittest.main()
