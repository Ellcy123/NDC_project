#!/usr/bin/env python3
"""Regression tests for secondary_prop_border.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).with_name("secondary_prop_border.py")


class SecondaryPropBorderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_context = tempfile.TemporaryDirectory(
            prefix="ndc-secondary-prop-border-test-"
        )
        self.root = Path(self.temp_context.name)
        self.inner = self.root / "drawer_inner.png"
        self.output = self.root / "prop_drawer2.png"
        Image.new("RGB", (40, 24), (61, 42, 30)).save(self.inner)

    def tearDown(self) -> None:
        self.temp_context.cleanup()

    def run_command(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                command,
                "--input",
                str(self.inner),
                "--output",
                str(self.output),
                "--border",
                "12",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_adds_and_verifies_exact_border(self) -> None:
        added = self.run_command("add")
        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)

        with Image.open(self.output) as image:
            rgba = image.convert("RGBA")
            self.assertEqual(rgba.size, (64, 48))
            self.assertEqual(rgba.getpixel((0, 0)), (255, 255, 255, 255))
            self.assertEqual(rgba.getpixel((11, 11)), (255, 255, 255, 255))
            self.assertEqual(rgba.getpixel((12, 12)), (61, 42, 30, 255))
            self.assertEqual(rgba.getpixel((51, 35)), (61, 42, 30, 255))
            self.assertEqual(rgba.getpixel((52, 36)), (255, 255, 255, 255))

        verified = self.run_command("verify")
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

    def test_verify_rejects_modified_border(self) -> None:
        added = self.run_command("add")
        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
        with Image.open(self.output) as image:
            rgba = image.convert("RGBA")
        rgba.putpixel((2, 2), (0, 0, 0, 255))
        rgba.save(self.output)

        verified = self.run_command("verify")
        self.assertEqual(verified.returncode, 2)
        self.assertIn("differ", verified.stdout)

    def test_rejects_transparent_inner_source(self) -> None:
        Image.new("RGBA", (40, 24), (61, 42, 30, 0)).save(self.inner)
        added = self.run_command("add")
        self.assertEqual(added.returncode, 2)
        self.assertIn("fully opaque", added.stdout)


if __name__ == "__main__":
    unittest.main()
