import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import irregular_map


class IrregularMapTests(unittest.TestCase):
    def test_build_uses_tight_bbox_and_preserves_visible_parent_pixels(self):
        parent_array = np.zeros((12, 16, 4), dtype=np.uint8)
        parent_array[:, :, 0] = np.arange(16, dtype=np.uint8)
        parent_array[:, :, 1] = np.arange(12, dtype=np.uint8)[:, None]
        parent_array[:, :, 2] = 77
        parent_array[:, :, 3] = 255
        parent = Image.fromarray(parent_array, "RGBA")
        points = [(4, 3), (11, 4), (10, 9), (5, 8)]

        sprite, bbox, _ = irregular_map.build_sprite(parent, points, padding=1)

        self.assertEqual((3, 2, 13, 11), bbox)
        self.assertEqual((10, 9), sprite.size)
        checks = irregular_map.verify_sprite(parent, sprite, bbox[0], bbox[1])
        self.assertTrue(checks["passed"])
        self.assertLess(checks["contourCoverageRatio"], 1.0)

    def test_verify_rejects_nonzero_rgb_beneath_zero_alpha(self):
        parent = Image.new("RGBA", (8, 8), (20, 30, 40, 255))
        sprite = Image.new("RGBA", (4, 4), (20, 30, 40, 255))
        array = np.array(sprite)
        array[0, 0] = [255, 0, 0, 0]
        dirty = Image.fromarray(array, "RGBA")

        checks = irregular_map.verify_sprite(parent, dirty, 2, 2)

        self.assertFalse(checks["transparentRgbZero"])
        self.assertFalse(checks["passed"])

    def test_five_pixel_expansion_contains_shadow_union_and_expands_bounds(self):
        base = irregular_map.polygon_mask(
            (30, 30), [(10, 9), (18, 10), (19, 18), (11, 19)]
        )
        expanded = irregular_map.expand_mask(base, 5)
        checks = irregular_map.verify_expansion(base, expanded, 5)
        self.assertTrue(checks["expandedMaskContainsBaseMask"])
        self.assertTrue(checks["boundsExpandedByRequestedPixels"])
        self.assertTrue(checks["passed"])

    def test_disconnected_shadow_island_is_preserved_in_union(self):
        body = [(20, 4), (34, 4), (34, 17), (20, 17)]
        far_shadow = [(2, 13), (11, 13), (11, 17), (2, 17)]
        parent = Image.new("RGBA", (40, 22), (40, 50, 60, 255))

        sprite, bbox, mask = irregular_map.build_sprite(
            parent,
            body,
            padding=0,
            expand=0,
            shadow_polygons=[far_shadow],
        )

        components = irregular_map.connected_component_bounds(mask)

        self.assertEqual((2, 4, 35, 18), bbox)
        self.assertEqual((33, 14), sprite.size)
        self.assertEqual(2, len(components))
        self.assertEqual([20, 4, 35, 18], components[0]["bounds"])
        self.assertEqual([2, 13, 12, 18], components[1]["bounds"])

    def test_final_extrema_gate_rejects_occluder_that_removes_shadow_extreme(self):
        base = irregular_map.polygon_union_mask(
            (40, 22),
            [
                [(20, 4), (34, 4), (34, 17), (20, 17)],
                [(2, 13), (11, 13), (11, 17), (2, 17)],
            ],
        )
        exclusions = irregular_map.exclusion_mask(
            (40, 22), [[(0, 10), (5, 10), (5, 21), (0, 21)]]
        )
        final = irregular_map.apply_exclusions(base, exclusions)
        checks = irregular_map.verify_extreme_points(
            final,
            {
                "top": (20, 4),
                "bottom": (25, 17),
                "left": (2, 15),
                "right": (34, 10),
            },
        )

        self.assertFalse(checks["points"]["left"]["selectedByContour"])
        self.assertFalse(checks["passed"])

    def test_build_parser_defaults_to_three_pixel_expansion(self):
        args = irregular_map.build_parser().parse_args(
            [
                "build",
                "--parent",
                "parent.png",
                "--polygon",
                "0,0;2,0;2,2",
                "--output",
                "output.png",
            ]
        )
        self.assertEqual(3, args.expand)

    def test_cli_build_expansion_policy_and_output_geometry(self):
        # Synthetic fixtures test mechanics, never visual acceptance of real art.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent_path = root / "parent.png"
            Image.new("RGBA", (48, 48), (30, 40, 50, 255)).save(parent_path)
            for expansion in (0, 2, 3, 5):
                with self.subTest(expansion=expansion):
                    output = root / f"map_{expansion}.png"
                    report = root / f"report_{expansion}.json"
                    args = irregular_map.build_parser().parse_args([
                        "build", "--parent", str(parent_path),
                        "--polygon", "15,15;25,15;25,25;15,25",
                        "--extreme-points", "top:20,15;bottom:20,25;left:15,20;right:25,20",
                        "--padding", "0", "--expand", str(expansion),
                        "--output", str(output), "--report", str(report),
                    ])
                    self.assertEqual(0, args.func(args))
                    data = json.loads(report.read_text(encoding="utf-8"))
                    policy = data["expansionPolicy"]
                    self.assertEqual([2, 3], policy["productionDefaultPixels"])
                    self.assertEqual(expansion == 5, policy["fivePixelTrialRequiresAssetSpecificVisualEvidence"])
                    self.assertEqual(expansion == 0, policy["zeroExpansionRequiresAuthoredFinalContour"])
                    self.assertEqual(expansion not in (2, 3), policy["nonDefaultExpansionApprovalRequired"])
                    self.assertTrue(policy["technicalReportDoesNotApproveVisualCompleteness"])
                    with Image.open(output) as result:
                        self.assertEqual((11 + 2 * expansion, 11 + 2 * expansion), result.size)

    def test_extreme_gate_rejects_a_missed_declared_edge(self):
        mask = irregular_map.polygon_mask(
            (20, 20), [(5, 5), (14, 5), (14, 14), (5, 14)]
        )
        checks = irregular_map.verify_extreme_points(
            mask,
            {
                "top": (8, 5),
                "bottom": (8, 14),
                "left": (4, 10),
                "right": (14, 10),
            },
        )
        self.assertFalse(checks["points"]["left"]["selectedByContour"])
        self.assertFalse(checks["passed"])

    def test_foreground_occluder_is_removed_after_expansion(self):
        base = irregular_map.polygon_mask(
            (30, 30), [(8, 8), (21, 8), (21, 21), (8, 21)]
        )
        expanded = irregular_map.expand_mask(base, 3)
        exclusions = irregular_map.exclusion_mask(
            (30, 30), [[(0, 20), (29, 20), (29, 29), (0, 29)]]
        )
        final = irregular_map.apply_exclusions(expanded, exclusions)
        checks = irregular_map.verify_exclusions(expanded, final, exclusions)
        self.assertTrue(checks["finalMaskHasNoForegroundOccluderOverlap"])
        self.assertGreater(checks["excludedPixelCount"], 0)
        self.assertTrue(checks["passed"])

    def test_alpha_only_reference_rebuild_uses_parent_rgb_and_preserves_islands(self):
        rng = np.random.default_rng(4025)
        parent_array = rng.integers(0, 256, size=(42, 64, 4), dtype=np.uint8)
        parent_array[:, :, 3] = 255
        parent = Image.fromarray(parent_array, "RGBA")
        origin_x, origin_y = 23, 14
        reference_array = parent_array[origin_y:origin_y + 16, origin_x:origin_x + 22].copy()
        alpha = np.zeros((16, 22), dtype=np.uint8)
        alpha[1:15, 10:21] = 255
        alpha[11:15, 0:6] = 255
        reference_array[:, :, 3] = alpha
        reference_array[alpha == 0, :3] = [199, 211, 223]
        visible_y, visible_x = np.where(alpha > 0)
        for index in range(0, len(visible_y), 20):
            y, x = int(visible_y[index]), int(visible_x[index])
            reference_array[y, x, 0] ^= 1
        reference = Image.fromarray(reference_array, "RGBA")

        registration = irregular_map.locate_alpha_reference(
            parent, reference, min_similarity=0.9, min_uniqueness_margin=0.02
        )
        sprite, bbox, _ = irregular_map.rebuild_from_alpha_reference(
            parent,
            reference,
            int(registration["origin"][0]),
            int(registration["origin"][1]),
        )

        self.assertEqual([origin_x, origin_y], registration["origin"])
        self.assertGreaterEqual(registration["sampleSimilarity"], 0.9)
        self.assertEqual((origin_x, origin_y + 1, origin_x + 21, origin_y + 15), bbox)
        checks = irregular_map.verify_sprite(parent, sprite, bbox[0], bbox[1])
        self.assertTrue(checks["passed"])
        self.assertEqual(2, len(irregular_map.connected_component_bounds(sprite.getchannel("A"))))

    def test_rebuild_reference_parser_defaults_do_not_expand_reviewed_alpha(self):
        args = irregular_map.build_parser().parse_args(
            [
                "rebuild-reference",
                "--parent",
                "parent.png",
                "--reference",
                "reference.png",
                "--output",
                "output.png",
            ]
        )
        self.assertEqual(0, args.padding)
        self.assertEqual(0.9, args.min_similarity)
        self.assertEqual(0.02, args.min_uniqueness_margin)


if __name__ == "__main__":
    unittest.main()
