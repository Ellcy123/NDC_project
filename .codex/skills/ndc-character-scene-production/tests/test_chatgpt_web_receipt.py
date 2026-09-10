"""Contract tests for ChatGPT web generation receipts; no browser or generation is used."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_chatgpt_web_receipt import validate


ROOT = Path(r"D:\Codex\NDC\工作过程文件")
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ChatGptWebReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chatgpt-web-receipt-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        prompt = self.root / "prompt.txt"
        prompt.write_text("synthetic contract test only", encoding="utf-8")
        inputs = []
        for index, role in enumerate(("local-whitebox-crop", "untouched-full-scene", "approved-character-card"), start=1):
            path = self.root / f"input-{index}.png"
            path.write_bytes(PNG)
            inputs.append({"role": role, "path": str(path), "sha256": digest(path)})
        output = self.root / "download.png"
        output.write_bytes(PNG)
        self.receipt = {
            "schema": "ndc-chatgpt-web-generation-receipt/v2",
            "backend": "chatgpt_web",
            "browser": "iab",
            "submission_tool": "chatgpt_web_browser",
            "submission_operation": "generate_image",
            "codex_image_generation_used": False,
            "task_id": "synthetic-task",
            "scene_id": "synthetic-scene",
            "revision": 1,
            "pose_ids": ["pose-a"],
            "submission_id": "synthetic-submission",
            "submitted_at": "2026-09-10T12:00:00+08:00",
            "completed_at": "2026-09-10T12:01:00+08:00",
            "conversation_url": "https://chatgpt.com/c/synthetic-contract-test",
            "candidate_index": 0,
            "work_directory": str(self.root),
            "prompt": {"path": str(prompt), "sha256": digest(prompt)},
            "importance_profile": {"path": str(self.root / "importance.json"), "sha256": ""},
            "uploaded_inputs": inputs,
            "download": {"path": str(output), "sha256": digest(output)},
        }
        profile = self.root / "importance.json"
        profile.write_text('{"schema":"ndc-visual-importance/v1"}', encoding="utf-8")
        self.receipt["importance_profile"]["sha256"] = digest(profile)
        manifest = {
            "schema":"ndc-chatgpt-web-submission-packet/v1", "scene_id":"synthetic-scene", "revision":1,
            "pose_ids":["pose-a"], "submission_order":["local-whitebox-crop","untouched-full-scene","approved-character-card","full-prompt"],
            "prompt":self.receipt["prompt"], "importance_profile":self.receipt["importance_profile"],
            "uploaded_inputs":inputs,
        }
        manifest_path = self.root / "submission-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.receipt["submission_manifest"] = {"path":str(manifest_path), "sha256":digest(manifest_path)}

    def test_valid_web_receipt_passes(self):
        self.assertEqual(validate(self.receipt)["status"], "PASS")

    def test_external_browser_receipt_passes(self):
        for browser in ("chrome", "edge"):
            self.receipt["browser"] = browser
            self.receipt["submission_tool"] = "chatgpt_web_browser"
            self.assertEqual(validate(self.receipt)["status"], "PASS")

    def test_legacy_iab_receipt_remains_compatible(self):
        self.receipt["submission_tool"] = "chatgpt_web_iab"
        self.assertEqual(validate(self.receipt)["status"], "PASS")
        self.receipt["browser"] = "chrome"
        self.assertEqual(validate(self.receipt)["status"], "FAIL")

    def test_codex_backend_or_wrong_reference_order_fails(self):
        self.receipt["codex_image_generation_used"] = True
        self.receipt["uploaded_inputs"].reverse()
        result = validate(self.receipt)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("codex_image_generation_used" in item for item in result["errors"]))
        self.assertTrue(any("exact order" in item for item in result["errors"]))

    def test_screenshot_wrapper_and_external_download_fail(self):
        outside = self.root.parent / (self.root.name + "-outside.txt")
        outside.write_text("not an image", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        self.receipt["download"] = {"path": str(outside), "sha256": digest(outside)}
        result = validate(self.receipt)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("original PNG" in item for item in result["errors"]))
        self.assertTrue(any("work_directory" in item for item in result["errors"]))

    def test_manifest_drift_and_legacy_default_fail(self):
        self.receipt["pose_ids"] = ["different"]
        self.assertTrue(any("submission_manifest" in item for item in validate(self.receipt)["errors"]))
        self.receipt["schema"] = "ndc-chatgpt-web-generation-receipt/v1"
        self.assertEqual(validate(self.receipt)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
