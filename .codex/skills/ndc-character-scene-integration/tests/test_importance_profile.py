import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_importance_profile import HARD_GATES, validate


def valid_profile():
    return {
        "schema": "ndc-visual-importance/v1", "domain": "character_scene",
        "scene_id": "scene-a", "revision": 1,
        "classification_basis": ["runtime composition and approved narrative"],
        "hard_gates": {name: {"applicable": True, "reason": "required by scene contract"} for name in HARD_GATES},
        "regions": [
            {"id":"actor-face","owner":"actor:a","tier":"H1","tolerance_ratio":0.1,
             "criteria":["identity and expression silhouette"],"views":["whole_runtime","whole_100","local_200"],
             "reason":"narrative focus","dependsOn":[]},
            {"id":"far-coat-fold","owner":"actor:a","tier":"H3","tolerance_ratio":0.3,
             "criteria":["minor fold placement"],"views":["whole_runtime"],"reason":"non-semantic finish",
             "low_salience_basis":"small and partly occluded at runtime","dependsOn":["actor-face"]},
        ],
    }


class ImportanceProfileTests(unittest.TestCase):
    def test_valid_profile_passes(self):
        self.assertEqual(validate(valid_profile())["status"], "PASS")

    def test_h1_over_ten_percent_fails(self):
        data = valid_profile(); data["regions"][0]["tolerance_ratio"] = 0.1001
        self.assertEqual(validate(data)["status"], "FAIL")

    def test_h3_requires_low_salience_basis(self):
        data = valid_profile(); data["regions"][1].pop("low_salience_basis")
        self.assertTrue(any("low_salience_basis" in e for e in validate(data)["errors"]))

    def test_unknown_key_and_dependency_fail_closed(self):
        data = valid_profile(); data["regions"][0]["typo"] = True; data["regions"][0]["dependsOn"] = ["missing"]
        result = validate(data)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("unknown keys" in e for e in result["errors"]))
        self.assertTrue(any("unknown region" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
