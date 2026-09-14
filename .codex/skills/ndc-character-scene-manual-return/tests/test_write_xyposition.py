import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "write_xyposition.py"
SPEC = importlib.util.spec_from_file_location("write_xyposition", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WriteXYPositionTests(unittest.TestCase):
    def test_renders_existing_delivery_format_in_input_order(self):
        value = MODULE.render([
            ("SC2206_Mickey_intro_shadow__XY_x1043_y365.png", 1043, 365),
            ("SC2206_Mickey_intro_character__XY_x1043_y365.png", 1043, 365),
        ])
        self.assertEqual(
            value,
            "SC2206_Mickey_intro_shadow__XY_x1043_y365\t1043,365\n"
            "SC2206_Mickey_intro_character__XY_x1043_y365\t1043,365\n",
        )

    def test_rejects_filename_coordinate_mismatch(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            MODULE.render([("SC2206_Mickey__XY_x10_y20.png", 11, 20)])

    def test_rejects_duplicate_stem(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.render([
                ("SC2206_Mickey__XY_x10_y20.png", 10, 20),
                ("SC2206_Mickey__XY_x10_y20.png", 10, 20),
            ])


if __name__ == "__main__":
    unittest.main()
