"""Regression cases for source-locked inserts with no boundary delta samples."""

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image

import coordinate_patch as patch


class ExactContextBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("NDC_COORDINATE_TEST_TMP_ROOT"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # A textured source makes clear that source gradients are not new seams.
        self.source = np.random.default_rng(42).integers(40, 190, (80, 80, 3), dtype=np.uint8)
        self.registered = self.source[8:72, 8:72].copy()
        self.registered[28:35, 28:35] = [230, 210, 170]
        self.output = self.source.copy()
        self.output[8:72, 8:72] = self.registered
        self.mask = np.zeros((64, 64), dtype=np.uint8)
        self.mask[12:52, 12:52] = 255

    def scan(self, mutate_manifest=None, mode="RGB", registered_mode=None):
        for name, array in [("source", self.source), ("output", self.output), ("registered", self.registered)]:
            save_mode = registered_mode if name == "registered" and registered_mode else mode
            Image.fromarray(array).convert(save_mode).save(self.root / (name + ".png"))
        Image.fromarray(self.mask).save(self.root / "mask.png")
        manifest = {
            "stage": "composed",
            "source": str(self.root / "source.png"),
            "output": str(self.root / "output.png"),
            "source_sha256": patch.sha256(self.root / "source.png"),
            "output_sha256": patch.sha256(self.root / "output.png"),
            "crop_rect_top_left": [8, 8, 72, 72],
            "files": {"registered": str(self.root / "registered.png"), "hard_mask": str(self.root / "mask.png")},
            "artifact_sha256": {"hard_mask": patch.sha256(self.root / "mask.png")},
        }
        if mutate_manifest:
            mutate_manifest(manifest)
        path = self.root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        args = patch.build_parser().parse_args(["scan-boundary", "--manifest", str(path), "--ring", "3", "--allow-fail"])
        with contextlib.redirect_stdout(io.StringIO()):
            patch.scan_boundary(args)
        return json.loads((self.root / "boundary_report.json").read_text(encoding="utf-8"))

    def assertBlocked(self, report):
        self.assertFalse(report["exact_context_proof"]["passed"])
        self.assertFalse(report["passed"])

    def test_real_inner_insert_with_exact_context_passes(self):
        report = self.scan()
        self.assertTrue(report["passed"])
        self.assertFalse(report["informative_coverage_sufficient"])
        self.assertEqual(report["acceptance_method"], "exact_unchanged_context")
        self.assertEqual(report["exact_context_proof"]["interior_changed_pixels"], 49)

    def test_no_op_is_not_an_insert(self):
        self.registered = self.source[8:72, 8:72].copy()
        self.output = self.source.copy()
        self.assertBlocked(self.scan())

    def test_one_changed_boundary_pixel_cannot_use_exact_proof(self):
        self.registered[12, 20] = 255
        self.output[20, 28] = 255
        self.assertBlocked(self.scan())

    def test_change_in_second_inner_ring_is_rejected(self):
        self.registered[16, 20] = 255
        self.output[24, 28] = 255
        self.assertBlocked(self.scan())

    def test_clipped_or_unapplied_interior_is_rejected(self):
        self.output[38, 38] = self.source[38, 38]
        self.assertBlocked(self.scan())

    def test_change_outside_context_crop_is_rejected(self):
        self.output[1, 1] = 255
        report = self.scan()
        self.assertBlocked(report)
        self.assertEqual(report["exact_context_proof"]["changed_pixels_outside_crop"], 1)

    def test_stale_source_hash_is_rejected(self):
        self.assertBlocked(self.scan(lambda m: m.update(source_sha256="stale")))

    def test_stale_output_hash_is_rejected(self):
        self.assertBlocked(self.scan(lambda m: m.update(output_sha256="stale")))

    def test_stale_mask_hash_is_rejected(self):
        self.assertBlocked(self.scan(lambda m: m["artifact_sha256"].update(hard_mask="stale")))

    def add_alpha(self):
        alpha = np.random.default_rng(7).integers(0, 256, (80, 80, 1), dtype=np.uint8)
        self.source = np.concatenate((self.source, alpha), axis=2)
        self.output = np.concatenate((self.output, alpha), axis=2)
        self.registered = np.concatenate((self.registered, alpha[8:72, 8:72]), axis=2)

    def test_rgba_exact_context_preserves_all_alpha(self):
        self.add_alpha()
        report = self.scan(mode="RGBA")
        self.assertTrue(report["passed"])
        self.assertTrue(report["exact_context_proof"]["alpha_preserved_full_scene"])

    def test_rgb_patch_on_rgba_source_preserves_source_alpha(self):
        self.add_alpha()
        self.assertTrue(self.scan(mode="RGBA", registered_mode="RGB")["passed"])

    def test_alpha_only_changes_block_exact_proof_everywhere(self):
        self.add_alpha()
        for y, x in [(38, 38), (20, 28), (1, 1)]:
            with self.subTest(pixel=(y, x)):
                original = int(self.output[y, x, 3])
                self.output[y, x, 3] = (original + 1) % 256
                self.assertBlocked(self.scan(mode="RGBA", registered_mode="RGB"))
                self.output[y, x, 3] = original

    def test_unapplied_registered_alpha_blocks_exact_proof(self):
        self.add_alpha()
        self.registered[30, 30, 3] ^= 1
        self.assertBlocked(self.scan(mode="RGBA"))

    def test_rgba_hidden_rgb_change_still_blocks_context_proof(self):
        self.add_alpha()
        self.source[1, 1, 3] = self.output[1, 1, 3] = 0
        self.output[1, 1, 0] ^= 1
        self.assertBlocked(self.scan(mode="RGBA"))

    def test_existing_sampled_boundary_route_still_passes(self):
        self.registered = self.source[8:72, 8:72].copy() + 12
        crop = self.output[8:72, 8:72]
        crop[:] = self.source[8:72, 8:72]
        crop[self.mask > 0] = self.registered[self.mask > 0]
        report = self.scan()
        self.assertTrue(report["passed"])
        self.assertEqual(report["acceptance_method"], "sampled_boundary")
        self.assertTrue(report["informative_coverage_sufficient"])


if __name__ == "__main__":
    unittest.main()
