import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "hotspot_preflight.py"
SPEC = importlib.util.spec_from_file_location("hotspot_preflight", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HotspotPreflightTests(unittest.TestCase):
    def test_direct_pickup_requires_four_state_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent = root / "parent.png"
            parent.write_bytes(b"png")
            annotation = {
                "schema": MODULE.SCHEMA,
                "artifact_id": "a.map",
                "parent": {"path": str(parent), "sha256": MODULE.sha256(parent), "width": 10, "height": 10},
                "regions": {name: [name] for name in MODULE.REGIONS},
                "extrema": {"top": [5, 1], "bottom": [5, 8], "left": [1, 5], "right": [8, 5]},
                "direct_pickup": True,
                "direct_pickup_inputs": None,
            }
            path = root / "annotation.json"
            path.write_text(json.dumps(annotation), encoding="utf-8")
            failures = MODULE.validate(path)
            self.assertTrue(any("four-state" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
