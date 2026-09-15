from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prop_manual_return.py"
SPEC = importlib.util.spec_from_file_location("prop_manual_return", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_rgba_png(path: Path, width: int = 2, height: int = 2) -> None:
    raw = b"".join(b"\x00" + (b"\xff\x00\x00\xff" * width) for _ in range(height))
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    data += png_chunk(b"IDAT", zlib.compress(raw))
    data += png_chunk(b"IEND", b"")
    path.write_bytes(data)


def base_manifest(outputs: list[dict]) -> dict:
    return {
        "schema": "ndc-prop-manual-return/v1",
        "unit_id": "Unit4",
        "scene_id": "SCtest",
        "finalized_by_user": True,
        "source": {"mode": "saved_psd", "psd": "source.psd", "saved_after_manual_edits": True, "sha256": None},
        "destination": {"directory": "delivery", "overwrite_authorized": False},
        "candidate_policy": {"create_extra_candidate_directory": False, "backup_only_when_needed": True},
        "xy": {"filename": "XYposition.txt", "format": "fullwidth_brackets"},
        "outputs": outputs,
    }


def output(
    output_id: str,
    role: str,
    filename: str,
    xy,
    *,
    parent_id=None,
    embed=True,
    mode="raw_layer",
    final_profile=None,
    target_size=None,
) -> dict:
    return {
        "output_id": output_id,
        "layer_path": ["item", output_id],
        "role": role,
        "filename": filename,
        "render_mode": mode,
        "coordinate_bearing": xy is not None,
        "embed_xy_in_filename": embed if xy is not None else False,
        "xy": xy,
        "parent_id": parent_id,
        "final_profile": final_profile,
        "target_size": target_size,
        "expected_sha256": None,
    }


class ManualReturnTests(unittest.TestCase):
    def test_sc4002_style_type6_type7_map_xy(self) -> None:
        manifest = base_manifest([
            output("type6", "type6", "SCtest_item_prop_type6__XY_x1959_y970.png", [1959, 970]),
            output("type7", "type7", "SCtest_item_prop_type7.png", [1940, 854], parent_id="type6", embed=False, mode="visual_layer_with_effects"),
            output("map", "map", "SCtest_item_map__XY_x2079_y997.png", [2079, 997], parent_id="type7"),
        ])
        outputs = MODULE.validate_manifest(manifest)
        self.assertEqual(
            MODULE.expected_xy_text(outputs),
            "SCtest_item_prop_type6__XY_x1959_y970\t【1959,970】\n"
            "SCtest_item_prop_type7\t【1940,854】\n"
            "SCtest_item_map__XY_x2079_y997\t【2079,997】\n",
        )

    def test_sc4003_style_map1_map2_and_big(self) -> None:
        manifest = base_manifest([
            output("map1", "scene_carrier", "SCtest_item_map1__XY_x1579_y756.png", [1579, 756]),
            output("map2", "carrier_child_map", "SCtest_item_map2__XY_x1655_y781.png", [1655, 781], parent_id="map1"),
            output("big", "big", "SCtest_clue_big.png", None, embed=False, final_profile="clue_polaroid", target_size=[620, 620]),
            output("icon", "icon", "SCtest_clue_icon.png", None, embed=False, mode="deterministic_derivative", final_profile="icon", target_size=[130, 130]),
        ])
        outputs = MODULE.validate_manifest(manifest)
        self.assertEqual(len(outputs), 4)
        self.assertNotIn("big", MODULE.expected_xy_text(outputs))
        self.assertIn("map2__XY_x1655_y781", MODULE.expected_xy_text(outputs))

    def test_rejects_coordinate_filename_mismatch(self) -> None:
        manifest = base_manifest([
            output("map", "map", "SCtest_item_map__XY_x10_y20.png", [11, 20]),
        ])
        with self.assertRaises(MODULE.ManifestError):
            MODULE.validate_manifest(manifest)

    def test_accepts_big_without_standalone_spec_gate(self) -> None:
        manifest = base_manifest([
            output("big", "big", "SCtest_big.png", None, embed=False),
        ])
        outputs = MODULE.validate_manifest(manifest)
        self.assertEqual(outputs[0]["role"], "big")

    def test_verify_reports_missed_routine_big_adjustment_without_gate(self) -> None:
        manifest = base_manifest([
            output("big", "big", "SCtest_big.png", None, embed=False, final_profile="clue_polaroid", target_size=[4, 4]),
        ])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (root / "source.psd").write_bytes(b"test source")
            write_rgba_png(root / "SCtest_big.png", width=2, height=2)
            xy = root / "XYposition.txt"
            xy.write_text("", encoding="utf-8")
            args = type("Args", (), {"manifest": manifest_path, "delivery_dir": root, "xy_file": xy, "report": None})()
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                self.assertEqual(MODULE.command_verify(args), 0)
            report = json.loads(output_buffer.getvalue())
            self.assertFalse(report["outputs"][0]["size_matches_target"])

    def test_verify_delivery(self) -> None:
        manifest = base_manifest([
            output("map1", "scene_carrier", "SCtest_item_map1__XY_x10_y20.png", [10, 20]),
            output("map2", "carrier_child_map", "SCtest_item_map2__XY_x12_y24.png", [12, 24], parent_id="map1"),
        ])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (root / "source.psd").write_bytes(b"test source")
            for item in manifest["outputs"]:
                write_rgba_png(root / item["filename"])
            xy = root / "XYposition.txt"
            xy.write_text(MODULE.expected_xy_text(manifest["outputs"]), encoding="utf-8")

            args = type("Args", (), {"manifest": manifest_path, "delivery_dir": root, "xy_file": xy, "report": None})()
            self.assertEqual(MODULE.command_verify(args), 0)


if __name__ == "__main__":
    unittest.main()
