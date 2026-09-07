"""Regression tests: real Alpha math and explicit PS receipt provenance."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
from compose_profile_asset import place_rgba
from test_validate_expression_receipt import ReceiptValidatorTest, digest, write_json, SCRIPT


class ProfileAlphaTest(unittest.TestCase):
    def test_transparent_alpha_is_not_squared(self):
        patch = Image.new("RGBA", (1, 1), (80, 120, 160, 128))
        result = place_rgba(patch, (3, 3), (1, 1), (0, 0, 0, 0))
        self.assertEqual(result.getpixel((1, 1)), (80, 120, 160, 128))
        self.assertEqual(result.getpixel((0, 0)), (0, 0, 0, 0))

    def test_green_source_over_once(self):
        patch = Image.new("RGBA", (1, 1), (80, 120, 160, 128))
        result = place_rgba(patch, (2, 2), (0, 0), (0, 255, 43, 255))
        self.assertEqual(result.getpixel((0, 0)), (40, 187, 102, 255))
        self.assertEqual(result.getpixel((1, 1)), (0, 255, 43, 255))

    def test_negative_offset_and_bottom_exit(self):
        patch = Image.new("RGBA", (4, 4), (30, 60, 90, 128))
        result = place_rgba(patch, (2, 2), (-1, -1), (0, 0, 0, 0))
        self.assertEqual(list(result.getdata()), [(30, 60, 90, 128)] * 4)


class PhotoshopReceiptTest(unittest.TestCase):
    def build_ps_receipt(self, root):
        path = ReceiptValidatorTest().build_receipt(root)
        data = json.loads(path.read_text())
        data["schema_version"] = 13
        item = data["expressions"][0]
        manual = item.pop("manual_alpha_return")
        native = Path(item["native_rgba"])
        source = root / "before-ps.png"
        source.write_bytes(native.read_bytes())
        psd = root / "recovery.psd"
        psd.write_bytes(b"8BPS\x00\x01" + b"fixture")
        authority = root / "authorization.md"
        authority.write_text("TEST FIXTURE: user explicitly authorizes PS MCP repair")
        operation = root / "operation.json"
        write_json(operation, {"command_id": "layer.apply_image", "ok": True})
        edge_path = Path(manual["edge_review"])
        edge = json.loads(edge_path.read_text())
        edge.update(processor_authority="USER_AUTHORIZED_PHOTOSHOP_MCP", codex_background_removal_used=True, user_returned=False)
        write_json(edge_path, edge)
        stage = root / "stage.json"
        write_json(stage, {"schema": "ndc-stage-visual-self-check/v1", "visual_check_status": "PASS",
                          "outputs": [{"path": str(native), "sha256": digest(native)}],
                          "criteria": [{"name": "test", "applicable": True, "status": "PASS"}],
                          "views": [{"kind": kind, "path": edge["previews"]["white"]} for kind in ("whole_100", "local_200_or_tiles")]})
        item["photoshop_alpha_processing"] = {
            "method": "USER_AUTHORIZED_PHOTOSHOP_MCP", "processor_authority": "USER_AUTHORIZED_PHOTOSHOP_MCP",
            "codex_background_removal_used": True, "user_returned": False, "source_preserved": True,
            "cumulative_native_pixel_contraction": 0,
            "input_source": {"path": str(source), "sha256": digest(source)},
            "output_native": {"path": str(native), "sha256": digest(native)},
            "recovery_psd": {"path": str(psd), "sha256": digest(psd)},
            "authorization_evidence": str(authority), "operation_evidence": str(operation),
            "command_ids": ["layer.apply_image"], "stage_review": str(stage), "edge_review": str(edge_path),
            "protected_white_status": "PASS", "white_fringe_status": "PASS", "formal_status": "PASS"}
        cross = Path(item["cross_profile_source_audit"])
        write_json(cross, {"formal_status": "PASS", "native_source_sha256": digest(native)})
        write_json(path, data)
        return path, data

    def run_validator(self, path):
        return subprocess.run([sys.executable, str(SCRIPT), "--receipt", str(path)], capture_output=True, text=True)

    def test_truthful_ps_pass_and_fail_closed_mutations(self):
        with tempfile.TemporaryDirectory() as directory:
            path, good = self.build_ps_receipt(Path(directory))
            result = self.run_validator(path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for key, value in (("user_returned", True), ("source_preserved", False),
                               ("cumulative_native_pixel_contraction", 3), ("command_ids", []),
                               ("stage_review", "missing.json"), ("recovery_psd", {})):
                with self.subTest(key=key):
                    bad = copy.deepcopy(good)
                    bad["expressions"][0]["photoshop_alpha_processing"][key] = value
                    write_json(path, bad)
                    result = self.run_validator(path)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            bad = copy.deepcopy(good)
            bad["schema_version"] = 12
            write_json(path, bad)
            self.assertEqual(self.run_validator(path).returncode, 1)
            write_json(path, good)
            edge_path = Path(good["expressions"][0]["photoshop_alpha_processing"]["edge_review"])
            edge = json.loads(edge_path.read_text())
            edge["source"]["sha256"] = "0" * 64
            write_json(edge_path, edge)
            self.assertEqual(self.run_validator(path).returncode, 1)


if __name__ == "__main__":
    unittest.main()
