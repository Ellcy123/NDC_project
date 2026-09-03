#!/usr/bin/env python3
"""End-to-end tests for the schema-12 expression receipt validator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).with_name("validate_expression_receipt.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class ReceiptValidatorTest(unittest.TestCase):
    def build_receipt(self, root: Path) -> Path:
        portrait = root / "portrait.png"
        Image.new("RGB", (16, 16), (120, 80, 60)).save(portrait)

        native = root / "native.png"
        native_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        for x in range(4, 12):
            for y in range(2, 16):
                native_image.putpixel((x, y), (80, 40, 20, 255))
        native_image.save(native)

        profile = root / "transparent.png"
        canvas = Image.new("RGBA", (1164, 916), (0, 0, 0, 0))
        canvas.alpha_composite(native_image, (574, 900))
        canvas.save(profile)

        manifest = root / "manifest.json"
        census = root / "census.json"
        write_json(manifest, {})
        write_json(census, {})

        handoff = root / "pre-alpha.png"
        Image.new("RGB", (16, 16), (244, 242, 237)).save(handoff)
        handoff_manifest = root / "handoff-manifest.json"
        write_json(handoff_manifest, {
            "handoff_status": "PRE_ALPHA_HANDOFF",
            "final_delivery": False,
            "expressions": [{
                "expression_id": "calm",
                "handoff_file": handoff.name,
                "sha256": digest(handoff),
            }],
        })
        previews = {}
        for name in ("white", "mid_gray", "dark_gray", "black", "exact_green"):
            path = root / f"preview-{name}.png"
            Image.new("RGB", (2, 2), (0, 0, 0)).save(path)
            previews[name] = str(path)
        alpha = root / "alpha.png"
        native_image.getchannel("A").save(alpha)
        edge = root / "edge.json"
        write_json(edge, {
            "codex_background_removal_used": False,
            "source": {"path": str(native), "sha256": digest(native)},
            "previews": previews,
            "alpha_visualization": str(alpha),
            "protected_white_status": "PASS",
            "white_fringe_status": "PASS",
            "silhouette_status": "PASS",
            "formal_status": "PASS",
        })

        cross = root / "cross.json"
        guide = root / "guide.json"
        mechanical = root / "mechanical.json"
        write_json(cross, {"formal_status": "PASS", "native_rgba_sha256": digest(native)})
        write_json(guide, {"formal_status": "PASS"})
        write_json(mechanical, {"mechanical_status": "PASS"})

        receipt = root / "receipt.json"
        write_json(receipt, {
            "schema_version": 12,
            "artifact_class": "PROFILE_DELIVERY_RECEIPT",
            "character_id": "test_character",
            "profile": "transparent",
            "profile_spec": {"canvas": [1164, 916], "mode": "RGBA", "background": "alpha_0"},
            "portrait_source": {
                "path": str(portrait), "sha256": digest(portrait),
                "authority": "USER_CONFIRMED_COMPLETED_PORTRAIT",
                "portrait_completion_used": False, "status": "PASS",
            },
            "expression_manifest": str(manifest),
            "approved_asset_census": str(census),
            "expressions": [{
                "expression_id": "calm",
                "profile_asset": str(profile), "profile_asset_sha256": digest(profile),
                "native_rgba": str(native), "native_rgba_sha256": digest(native),
                "manual_alpha_return": {
                    "method": "USER_RETURNED_MANUAL_BACKGROUND_PROCESSING",
                    "processor_authority": "USER_MANUAL_BACKGROUND_PROCESSING",
                    "handoff_edit_mode": "IN_PLACE_OVERWRITE",
                    "codex_background_removal_used": False, "user_returned": True,
                    "handoff_source": {"path": str(handoff), "sha256": digest(handoff)},
                    "returned_native": {"path": str(native), "sha256": digest(native)},
                    "handoff_manifest": str(handoff_manifest), "edge_review": str(edge),
                    "protected_white_status": "PASS", "white_fringe_status": "PASS",
                    "formal_status": "PASS",
                },
                "artistic_status": "PASS", "identity_status": "PASS",
                "viewpoint_status": "PASS", "style_status": "PASS",
                "texture_status": "PASS", "detail_lighting_status": "PASS",
                "expression_status": "PASS", "profile_status": "PASS",
                "cross_profile_source_audit": str(cross),
                "profile_guide_review": str(guide), "mechanical_audit": str(mechanical),
            }],
            "continuity_review": {
                "whole_set_checked": True, "identity": "PASS", "viewpoint": "PASS",
                "style_texture": "PASS", "detail_lighting": "PASS",
                "expression_separability": "PASS", "thumbnail_readability": "PASS",
                "geometry": "PASS",
            },
            "final_status": "FORMAL_PASS",
        })
        return receipt

    def test_formal_pass_and_codex_background_removal_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            receipt = self.build_receipt(Path(directory))
            good = subprocess.run(
                [sys.executable, str(SCRIPT), "--receipt", str(receipt)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            value = json.loads(receipt.read_text(encoding="utf-8"))
            value["expressions"][0]["manual_alpha_return"]["codex_background_removal_used"] = True
            write_json(receipt, value)
            bad = subprocess.run(
                [sys.executable, str(SCRIPT), "--receipt", str(receipt)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
            self.assertIn("codex_background_removal_used: must be false", bad.stdout)


if __name__ == "__main__":
    unittest.main()
