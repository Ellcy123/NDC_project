from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "conservative_matte.py"
SPEC = importlib.util.spec_from_file_location("conservative_matte", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ConservativeMatteTests(unittest.TestCase):
    def test_border_flood_preserves_enclosed_white_prop_and_full_silhouette(self) -> None:
        image = Image.new("RGB", (64, 64), (247, 247, 247))
        draw = ImageDraw.Draw(image)
        draw.rectangle((20, 8, 43, 58), fill=(30, 20, 15))
        draw.rectangle((25, 25, 38, 34), fill=(255, 255, 255))
        mask = MODULE.make_conservative_alpha(MODULE.border_connected_background(image))
        self.assertEqual(mask.getpixel((0, 0)), 0)
        self.assertGreater(mask.getpixel((20, 8)), 0)
        self.assertGreater(mask.getpixel((30, 30)), 0)
        self.assertGreaterEqual(mask.getbbox()[2], 44)
        self.assertGreaterEqual(mask.getbbox()[3], 59)

    def test_expanded_edge_rgb_is_decontaminated_from_light_background(self) -> None:
        image = Image.new("RGB", (24, 24), (247, 247, 247))
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 5, 15, 20), fill=(25, 15, 10))
        core = MODULE.border_connected_background(image)
        alpha = MODULE.make_conservative_alpha(core)
        cutout = MODULE.decontaminate_edge(image, alpha, core)
        edge = cutout.getpixel((7, 10))
        self.assertGreater(edge[3], 0)
        self.assertLess(max(edge[:3]), 100)

    def test_neutral_border_halo_is_removed_but_warm_light_prop_is_preserved(self) -> None:
        image = Image.new("RGB", (32, 32), (247, 247, 247))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 6, 21, 27), fill=(245, 245, 245))
        draw.rectangle((11, 7, 20, 26), fill=(20, 15, 10))
        draw.rectangle((8, 14, 13, 18), fill=(235, 210, 160))
        core = MODULE.border_connected_background(image)
        cleaned = MODULE.suppress_neutral_halo(image, core)
        self.assertEqual(cleaned.getpixel((10, 8)), 0)
        self.assertEqual(cleaned.getpixel((9, 16)), 255)

    def test_large_enclosed_checker_island_is_removed(self) -> None:
        image = Image.new("RGB", (48, 48), (20, 15, 10))
        draw = ImageDraw.Draw(image)
        draw.rectangle((14, 14, 33, 33), fill=(247, 247, 247))
        draw.rectangle((20, 20, 27, 27), fill=(235, 210, 160))
        foreground = Image.new("L", image.size, 255)
        cleaned = MODULE.remove_large_neutral_islands(image, foreground, minimum_area=64)
        self.assertEqual(cleaned.getpixel((16, 16)), 0)
        self.assertEqual(cleaned.getpixel((23, 23)), 255)

    def test_edge_rgb_audit_detects_neutral_fringe_without_eroding_alpha(self) -> None:
        cutout = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(cutout)
        draw.rectangle((8, 6, 23, 27), fill=(30, 20, 15, 255))
        draw.rectangle((7, 5, 24, 28), outline=(185, 185, 185, 255), width=1)
        before_alpha = cutout.getchannel("A").copy()
        audit = MODULE.audit_neutral_edge_contamination(cutout)
        self.assertGreater(audit["neutralContaminatedEdgePixelCount"], 0)
        self.assertEqual(
            list(before_alpha.get_flattened_data()),
            list(cutout.getchannel("A").get_flattened_data()),
        )

    def test_edge_rgb_audit_preserves_legitimate_light_subject_edge(self) -> None:
        cutout = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        ImageDraw.Draw(cutout).rectangle((7, 5, 24, 28), fill=(235, 235, 235, 255))
        audit = MODULE.audit_neutral_edge_contamination(cutout)
        self.assertEqual(audit["neutralContaminatedEdgePixelCount"], 0)


if __name__ == "__main__":
    unittest.main()
