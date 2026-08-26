#!/usr/bin/env python3
"""Regression tests for deterministic NDC Big/Icon/Polaroid finalization."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


SCRIPT = Path(__file__).with_name("evidence_art.py")
ASSETS = SCRIPT.parent.parent / "assets"


class EvidenceArtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_context = tempfile.TemporaryDirectory(prefix="ndc-evidence-art-test-")
        self.root = Path(self.temp_context.name)

    def tearDown(self) -> None:
        self.temp_context.cleanup()

    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_finalize_icon_to_fixed_130_safe_rect(self) -> None:
        master = self.root / "icon_master.png"
        subject_mask = self.root / "subject.png"
        shadow_mask = self.root / "shadow.png"
        output = self.root / "icon.png"
        report = self.root / "icon_report.json"

        master_image = Image.new("RGBA", (1040, 1040), (0, 0, 0, 0))
        master_draw = ImageDraw.Draw(master_image)
        master_draw.ellipse((260, 500, 700, 850), fill=(20, 10, 5, 90))
        master_draw.rounded_rectangle(
            (340, 220, 820, 760), radius=80, fill=(170, 92, 38, 255)
        )
        master_image.save(master)

        subject = Image.new("L", master_image.size, 0)
        ImageDraw.Draw(subject).rounded_rectangle((340, 220, 820, 760), 80, fill=255)
        subject.save(subject_mask)
        shadow = Image.new("L", master_image.size, 0)
        ImageDraw.Draw(shadow).ellipse((260, 500, 700, 850), fill=160)
        shadow.save(shadow_mask)

        completed = self.run_script(
            "finalize-icon",
            "--master",
            str(master),
            "--subject-mask",
            str(subject_mask),
            "--shadow-mask",
            str(shadow_mask),
            "--output",
            str(output),
            "--report",
            str(report),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        data = json.loads(report.read_text(encoding="utf-8"))
        self.assertTrue(data["passed"])
        self.assertEqual(data["artifact"]["size"], [130, 130])
        self.assertTrue(data["checks"]["contentInside115SafeRect"])
        self.assertTrue(data["checks"]["shadowFallsLeftAndDown"])

    def test_verify_icon_rejects_256_canvas(self) -> None:
        invalid = self.root / "invalid_256.png"
        Image.new("RGBA", (256, 256), (0, 0, 0, 0)).save(invalid)
        checked = self.run_script("verify-icon", "--input", str(invalid))
        self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)

    def test_finalize_portrait_big_uses_runtime_frame(self) -> None:
        master = self.root / "big_master.png"
        output = self.root / "big.png"
        report = self.root / "big_report.json"
        image = Image.new("RGBA", (900, 1400), (0, 0, 0, 0))
        ImageDraw.Draw(image).rounded_rectangle(
            (270, 220, 630, 1180), radius=30, fill=(220, 205, 160, 255)
        )
        image.save(master)
        completed = self.run_script(
            "finalize-big",
            "--master",
            str(master),
            "--frame",
            "portrait",
            "--rotation-degrees",
            "10",
            "--output",
            str(output),
            "--report",
            str(report),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        with Image.open(output) as finalized:
            self.assertEqual(finalized.size, (571, 1000))
            self.assertEqual(finalized.mode, "RGBA")
        self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["passed"])

    def test_polaroid_preserves_every_pixel_outside_canonical_mask(self) -> None:
        photo = self.root / "photo.png"
        output = self.root / "polaroid.png"
        report = self.root / "polaroid_report.json"
        Image.new("RGB", (1280, 900), (35, 90, 150)).save(photo)
        completed = self.run_script(
            "compose-polaroid",
            "--photo",
            str(photo),
            "--output",
            str(output),
            "--report",
            str(report),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        template = Image.open(ASSETS / "clue_polaroid_frame_620x620.png").convert("RGBA")
        result = Image.open(output).convert("RGBA")
        mask = Image.open(ASSETS / "clue_polaroid_window_mask_620x620.png").convert("L")
        outside = mask.point(lambda value: 255 if value == 0 else 0)
        difference = ImageChops.difference(template, result)
        self.assertIsNone(ImageChops.multiply(difference.getchannel("A"), outside).getbbox())
        for channel in difference.split()[:3]:
            self.assertIsNone(ImageChops.multiply(channel, outside).getbbox())
        self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["passed"])


if __name__ == "__main__":
    unittest.main()
