#!/usr/bin/env python3
"""Regression tests for evidence_delivery.py."""

from __future__ import annotations

import json
import hashlib
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
        self.broad_mask = self.root / "broad_authorization.png"
        self.base_report = self.root / "base_verification.json"
        self.icon = self.root / "approved_icon.png"
        self.icon_report = self.root / "approved_icon_verification.json"

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

        broad_mask = Image.new("L", (64, 64), 0)
        ImageDraw.Draw(broad_mask).rectangle((8, 10, 54, 50), fill=255)
        broad_mask.save(self.broad_mask)

        self.base_report.write_text(
            json.dumps({"passed": True}) + "\n", encoding="utf-8"
        )

        icon = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
        ImageDraw.Draw(icon).rounded_rectangle(
            (24, 18, 106, 111), radius=8, fill=(160, 90, 35, 255)
        )
        icon.save(self.icon)
        icon_hash = hashlib.sha256(self.icon.read_bytes()).hexdigest()
        self.icon_report.write_text(
            json.dumps(
                {
                    "version": 1,
                    "kind": "ndc-icon",
                    "artifact": {
                        "path": str(self.icon),
                        "sha256": icon_hash,
                        "size": [130, 130],
                        "mode": "RGBA",
                    },
                    "passed": True,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_context.cleanup()

    def command(
        self, final: Path, output: Path, authorization_mask: Path | None = None
    ) -> list[str]:
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
            str(authorization_mask or self.mask),
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
            "--icon-image",
            str(self.icon),
            "--icon-verification",
            str(self.icon_report),
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

    def test_broad_authorization_does_not_inflate_map_crop(self) -> None:
        output = self.root / "broad_delivery"
        packaged = subprocess.run(
            self.command(self.final, output, self.broad_mask),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(packaged.returncode, 0, packaged.stdout + packaged.stderr)
        manifest = json.loads(
            (output / "delivery_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["mapCrop"]["method"], "changed-pixel-bounds")
        self.assertEqual(manifest["mapCrop"]["rect"], [20, 22, 32, 30])
        self.assertFalse(manifest["checks"]["authorizationContainedByMapRect"])
        self.assertTrue(manifest["checks"]["changedPixelsContainedByMapRect"])

    def test_rejects_approved_icon_without_matching_report(self) -> None:
        output = self.root / "missing_icon_report"
        command = self.command(self.final, output)
        report_index = command.index("--icon-verification")
        del command[report_index : report_index + 2]
        packaged = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(packaged.returncode, 0)
        self.assertIn(
            "require --icon-verification", packaged.stdout + packaged.stderr
        )

    def test_omit_icon_removes_path_and_artifacts(self) -> None:
        output = self.root / "iconless_delivery"
        command = self.command(self.final, output)
        for option in ("--icon-stem", "--icon-image", "--icon-verification"):
            index = command.index(option)
            del command[index : index + 2]
        command.extend(["--omit-icon"])
        packaged = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(packaged.returncode, 0, packaged.stdout + packaged.stderr)
        manifest = json.loads(
            (output / "delivery_manifest.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("iconPath", manifest["unityDraft"])
        self.assertNotIn("iconSprite", manifest["artifacts"])
        self.assertTrue(manifest["icon"]["omitted"])


if __name__ == "__main__":
    unittest.main()
