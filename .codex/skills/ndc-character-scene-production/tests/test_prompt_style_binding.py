import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from validate_prompt_style_binding import (  # noqa: E402
    CANONICAL_STYLE_ASSET,
    CANONICAL_STYLE_SHA256,
    validate_contract,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PromptStyleBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ndc-style-binding-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lock = self.root / "style-lock.txt"
        shutil.copy2(CANONICAL_STYLE_ASSET, self.lock)
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_bytes(b"pose and support constraints\n" + self.lock.read_bytes() + b"deliver one complete actor\n")
        self.contract = {
            "schema": "ndc-prompt-style-binding/v2",
            "style_lock_path": str(self.lock),
            "fixed_style_sha256": CANONICAL_STYLE_SHA256,
            "rendered_prompt_path": str(self.prompt),
            "reference_roles": ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"],
            "dynamic_fields": {"character": "actor-a", "visible_action": "stands beside the desk"},
        }
        self.contract_path = self.root / "contract.json"

    def validate(self):
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
        return validate_contract(self.contract_path)

    def test_bundled_style_preserves_original_terminal_nbsp_and_passes(self):
        self.assertEqual(digest(CANONICAL_STYLE_ASSET), CANONICAL_STYLE_SHA256)
        self.assertTrue(CANONICAL_STYLE_ASSET.read_bytes().endswith(b",\xc2\xa0\n"))
        result = self.validate()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["checks"]["original_style_occurrences"], 1)

    def test_modified_parenthetical_fails_even_when_work_hash_is_self_consistent(self):
        changed = self.lock.read_bytes().replace(b" (shirt, jacket, skirt, tie)", b"")
        self.lock.write_bytes(changed)
        self.prompt.write_bytes(b"prefix\n" + changed + b"suffix\n")
        self.contract["fixed_style_sha256"] = digest(self.lock)
        result = self.validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("original user style" in error for error in result["errors"]))

    def test_trimming_original_nbsp_fails(self):
        changed = self.lock.read_bytes().replace(b",\xc2\xa0\n", b",\n")
        self.lock.write_bytes(changed)
        self.prompt.write_bytes(b"prefix\n" + changed)
        result = self.validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("byte-identical" in error for error in result["errors"]))

    def test_second_rewritten_style_description_outside_lock_fails(self):
        self.prompt.write_bytes(
            b"highly stylized graphic illustration but simplified\n"
            + self.lock.read_bytes()
        )
        result = self.validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("second or rewritten" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
