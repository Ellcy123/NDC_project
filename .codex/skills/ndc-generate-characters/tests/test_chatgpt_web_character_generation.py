"""Contract tests for NDC character generation packets and receipts; no browser is used."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from build_chatgpt_web_character_packet import build
from validate_chatgpt_web_character_receipt import validate

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CharacterWebGenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("complete character prompt", encoding="utf-8")
        self.inputs = []
        for index, role in enumerate(("approved-mj-stage-fullbody", "same-source-face-anchor", "general-fullbody-style-reference"), start=1):
            path = self.root / f"input-{index}.png"
            path.write_bytes(PNG)
            self.inputs.append({"role": role, "path": str(path.resolve()), "sha256": digest(path)})
        self.contract = {
            "schema": "ndc-chatgpt-web-character-submission-source/v1",
            "character_id": "synthetic-character",
            "production_revision": "identity-r1",
            "asset_mode": "general-style-fullbody",
            "branch": "mj-conversion",
            "revision": 1,
            "conversation_url": "https://chatgpt.com/c/synthetic-character-r1",
            "uploaded_inputs": self.inputs,
            "prompt": {"path": str(self.prompt.resolve()), "sha256": digest(self.prompt)},
        }
        self.contract_path = self.root / "contract.json"
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")

    def test_packet_and_receipt_bind_exact_order(self):
        result = build(self.contract_path, self.root / "packet")
        manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["submission_order"], [item["role"] for item in self.inputs] + ["full-prompt"])
        output = Path(result["packet"]) / "download.png"
        output.write_bytes(PNG)
        receipt_path = Path(result["receipt_draft"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt.update({
            "task_id": "task-1", "submission_id": "submission-1",
            "submitted_at": "2026-09-10T12:00:00+08:00", "completed_at": "2026-09-10T12:01:00+08:00",
            "download": {"path": str(output.resolve()), "sha256": digest(output)},
        })
        self.assertEqual(validate(receipt)["status"], "PASS")

    def test_external_browser_packet_and_receipt_pass(self):
        for browser in ("chrome", "edge"):
            result = build(self.contract_path, self.root / f"packet-{browser}", browser)
            receipt = json.loads(Path(result["receipt_draft"]).read_text(encoding="utf-8"))
            output = Path(result["packet"]) / "download.png"
            output.write_bytes(PNG)
            receipt.update({
                "task_id": "task-1", "submission_id": f"submission-{browser}",
                "submitted_at": "2026-09-10T12:00:00+08:00", "completed_at": "2026-09-10T12:01:00+08:00",
                "download": {"path": str(output.resolve()), "sha256": digest(output)},
            })
            self.assertEqual(receipt["browser"], browser)
            self.assertEqual(validate(receipt)["status"], "PASS")

    def test_legacy_iab_receipt_remains_compatible(self):
        result = build(self.contract_path, self.root / "packet-legacy")
        receipt = json.loads(Path(result["receipt_draft"]).read_text(encoding="utf-8"))
        output = Path(result["packet"]) / "download.png"
        output.write_bytes(PNG)
        receipt.update({
            "submission_tool": "chatgpt_web_iab", "task_id": "task-1", "submission_id": "legacy",
            "submitted_at": "2026-09-10T12:00:00+08:00", "completed_at": "2026-09-10T12:01:00+08:00",
            "download": {"path": str(output.resolve()), "sha256": digest(output)},
        })
        self.assertEqual(validate(receipt)["status"], "PASS")

    def test_wrong_role_order_and_backend_fail(self):
        self.contract["uploaded_inputs"].reverse()
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "roles must be exactly"):
            build(self.contract_path, self.root / "packet")

    def test_non_chatgpt_conversation_fails_before_packet(self):
        self.contract["conversation_url"] = "https://example.com/c/not-chatgpt"
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "chatgpt.com"):
            build(self.contract_path, self.root / "packet")

    def test_mode_specific_contracts(self):
        cases = [
            ("general-style-fullbody", "secondary-direct", ["general-fullbody-style-reference"]),
            ("general-character-card", "default-whole-card", ["approved-general-style-fullbody", "same-source-face-anchor"]),
            ("black-white-red-character-card", "animation-card", ["approved-general-character-card", "black-white-red-style-reference"]),
        ]
        for number, (mode, branch, roles) in enumerate(cases, start=1):
            inputs = []
            for index, role in enumerate(roles, start=1):
                path = self.root / f"case-{number}-{index}.png"
                path.write_bytes(PNG)
                inputs.append({"role": role, "path": str(path.resolve()), "sha256": digest(path)})
            contract = dict(self.contract, asset_mode=mode, branch=branch, uploaded_inputs=inputs)
            path = self.root / f"contract-{number}.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            result = build(path, self.root / f"packet-{number}")
            self.assertTrue(Path(result["manifest"]).is_file())


if __name__ == "__main__":
    unittest.main()
