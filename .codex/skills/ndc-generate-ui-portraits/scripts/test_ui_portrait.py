"""Synthetic technical regression tests, not visual approval of production assets."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageDraw
import ui_portrait as ui


class CropTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "母图.png"
        im = Image.new("RGB", (900, 1200), (28, 20, 13))
        d = ImageDraw.Draw(im)
        d.rectangle((150, 300, 750, 900), fill=(145, 115, 80))
        d.line((0, 450, 899, 450), fill=(0, 255, 0), width=9)
        d.line((0, 750, 899, 750), fill=(255, 255, 0), width=9)
        im.save(self.source)
        self.marks = {"source_sha256": ui.sha(self.source), "left_eye": [410, 450],
                      "right_eye": [490, 450], "chin": [450, 750],
                      "reviewer": "synthetic-test", "note": "Synthetic geometry, not a human review"}
        self.landmarks = self.root / "坐标.json"
        self.save_marks()
        self.output = self.root / "角色 测试"

    def save_marks(self):
        self.landmarks.write_text(json.dumps(self.marks), encoding="utf-8")

    def compose(self):
        return ui.compose(self.source, self.landmarks, "Anna 测试", self.output)

    def test_pair_geometry_and_audit(self):
        receipt = self.compose()
        checked = ui.audit(self.output / "composition.json")
        self.assertEqual(checked["visual_status"], "NOT_CHECKED")
        self.assertNotEqual(receipt["profiles"]["big"]["source_box"], receipt["profiles"]["small"]["source_box"])
        for key, p in ui.profiles().items():
            with Image.open(self.output / receipt["profiles"][key]["path"]) as im:
                # Independent pixel evidence: synthetic source eye/chin bands land on each guide.
                column = [im.getpixel((im.width // 2, y)) for y in range(im.height)]
                # A half-pixel guide can split a thin band across two output rows.
                eye_row = max(range(im.height), key=lambda y: column[y][1] - column[y][0])
                chin_row = max(range(im.height), key=lambda y: min(column[y][:2]) - column[y][2])
                self.assertLessEqual(abs(eye_row - p["eye_y"]), 1)
                self.assertLessEqual(abs(chin_row - p["chin_y"]), 1)
                self.assertGreater(column[eye_row][1] - column[eye_row][0], 80)
                self.assertEqual(im.size, tuple(p["size"]))

    def test_stale_source_rejected(self):
        self.marks["source_sha256"] = "0" * 64
        self.save_marks()
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.compose()
        self.assertFalse(self.output.exists())

    def test_outside_crop_preflight_leaves_no_partial_pair(self):
        self.marks["face_center_x"] = 20
        self.save_marks()
        with self.assertRaisesRegex(ValueError, "outside"):
            self.compose()
        self.assertFalse(self.output.exists())

    def test_no_upscale(self):
        self.marks["chin"] = [450, 480]
        self.save_marks()
        with self.assertRaisesRegex(ValueError, "Upscaling"):
            self.compose()

    def test_no_overwrite(self):
        self.compose()
        before = ui.sha(self.output / "composition.json")
        with self.assertRaisesRegex(ValueError, "exists"):
            self.compose()
        self.assertEqual(before, ui.sha(self.output / "composition.json"))

    def test_tampered_pixels_even_with_rehashed_receipt_fail(self):
        receipt = self.compose()
        target = self.output / receipt["profiles"]["small"]["path"]
        with Image.open(target) as old:
            im = old.copy()
        im.putpixel((2, 2), (255, 0, 255))
        im.save(target)
        receipt["profiles"]["small"]["sha256"] = ui.sha(target)
        (self.output / "composition.json").write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Pixels differ"):
            ui.audit(self.output / "composition.json")

    def test_transparent_source_rejected(self):
        Image.new("RGBA", (900, 1200), (20, 20, 20, 0)).save(self.source)
        self.marks["source_sha256"] = ui.sha(self.source)
        self.save_marks()
        with self.assertRaisesRegex(ValueError, "opaque"):
            self.compose()

    def test_profile_missing_fails(self):
        receipt = self.compose()
        del receipt["profiles"]["small"]
        (self.output / "composition.json").write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Both"):
            ui.audit(self.output / "composition.json")

    def test_reject_path_escape(self):
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            ui.compose(self.source, self.landmarks, "../escape", self.output)

    def test_reject_output_in_repo(self):
        repo = self.root / "fake_repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "repositories"):
            ui.compose(self.source, self.landmarks, "Anna", repo / "output")

    def test_invalid_landmarks(self):
        for key, value in (("left_eye", [-1, 450]), ("right_eye", [490, float('nan')]), ("chin", [450, 400])):
            with self.subTest(key=key):
                original = self.marks[key]
                self.marks[key] = value
                self.save_marks()
                with self.assertRaises(ValueError):
                    self.compose()
                self.marks[key] = original


if __name__ == "__main__":
    unittest.main()
