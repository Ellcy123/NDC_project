"""Contract tests for scene-window ChatGPT web receipts; no browser or generation is used."""
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from validate_chatgpt_web_receipt import validate  # noqa: E402
from validate_prompt_style_binding import CANONICAL_STYLE_ASSET, CANONICAL_STYLE_SHA256  # noqa: E402

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ChatGptWebReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chatgpt-web-receipt-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        prompt = self.root / "prompt.txt"
        prompt.write_bytes(b"synthetic contract test only\n" + CANONICAL_STYLE_ASSET.read_bytes())
        style = self.root / "style.txt"
        shutil.copy2(CANONICAL_STYLE_ASSET, style)
        profile = self.root / "importance.json"
        profile.write_text('{"schema":"ndc-visual-importance/v1"}', encoding="utf-8")
        binding_gate = self.root / "prompt-binding-gate.json"
        binding_gate.write_text(json.dumps({
            "schema": "ndc-prompt-style-binding-gate/v2",
            "status": "PASS",
            "checks": {
                "rendered_prompt_sha256": digest(prompt),
                "canonical_style_sha256": CANONICAL_STYLE_SHA256,
                "style_lock_sha256": CANONICAL_STYLE_SHA256,
                "style_lock_matches_canonical_bytes": True,
                "original_style_occurrences": 1,
            },
        }), encoding="utf-8")
        importance_gate = self.root / "importance-gate.json"
        importance_gate.write_text(json.dumps({
            "status": "PASS",
            "profile_sha256": digest(profile),
        }), encoding="utf-8")
        window = self.root / "scene-window.json"
        window.write_text(json.dumps({
            "schema": "ndc-chatgpt-web-scene-workspace-identity/v2",
            "scene_id": "synthetic-scene",
            "revision": 1,
            "browser": "iab",
            "window_id": "scene-synthetic-r1",
            "window_label": "synthetic",
            "workspace_kind": "logical_scene_revision",
            "physical_window_required": False,
            "created_at": "2026-09-11T12:00:00+08:00",
            "account_profile_label": None,
        }), encoding="utf-8")
        inputs = []
        for index, role in enumerate(("local-whitebox-crop", "untouched-full-scene", "approved-character-card"), start=1):
            path = self.root / f"input-{index}.png"
            path.write_bytes(PNG)
            inputs.append({"role": role, "path": str(path), "sha256": digest(path)})
        output = self.root / "download.png"
        output.write_bytes(PNG)
        revision_gate = self.root / "revision-gate.json"
        revision_gate.write_text(json.dumps({
            "schema": "ndc-character-scene-ready-revision-gate/v1", "status": "CURRENT",
            "unit_id": "synthetic-scene", "revision": 1,
            "checked_at": "2026-09-11T11:58:00+08:00",
        }))
        self.manifest = {
            "schema": "ndc-chatgpt-web-submission-packet/v3",
            "scene_id": "synthetic-scene",
            "revision": 1,
            "browser": "iab",
            "generation_unit_id": "actor-a-pose",
            "actor_id": "actor-a",
            "pose_ids": ["pose-a"],
            "conversation_url": "https://chatgpt.com/c/synthetic-contract-test",
            "prepared_at": "2026-09-11T11:59:00+08:00",
            "submission_order": ["local-whitebox-crop", "untouched-full-scene", "approved-character-card", "full-prompt"],
            "scene_window": {"path": str(window), "sha256": digest(window)},
            "prompt": {"path": str(prompt), "sha256": digest(prompt)},
            "style_lock": {"path": str(style), "sha256": digest(style)},
            "importance_profile": {"path": str(profile), "sha256": digest(profile)},
            "prompt_binding_gate": {"path": str(binding_gate), "sha256": digest(binding_gate)},
            "importance_gate": {"path": str(importance_gate), "sha256": digest(importance_gate)},
            "revision_gate": {"path": str(revision_gate), "sha256": digest(revision_gate)},
            "retry_control": {"attempt_number": 1, "defect_tier": "INITIAL", "consecutive_same_defect_count": 0, "method_changed": False},
            "uploaded_inputs": inputs,
        }
        self.manifest_path = self.root / "submission-manifest.json"
        self.write_manifest()
        self.receipt = {
            "schema": "ndc-chatgpt-web-generation-receipt/v4",
            "backend": "chatgpt_web",
            "browser": "iab",
            "submission_tool": "chatgpt_web_browser",
            "submission_operation": "generate_image",
            "codex_image_generation_used": False,
            "task_id": "synthetic-task",
            "scene_id": "synthetic-scene",
            "revision": 1,
            "generation_unit_id": "actor-a-pose",
            "actor_id": "actor-a",
            "pose_ids": ["pose-a"],
            "submission_id": "synthetic-submission",
            "submitted_at": "2026-09-11T12:00:00+08:00",
            "completed_at": "2026-09-11T12:01:00+08:00",
            "conversation_url": "https://chatgpt.com/c/synthetic-contract-test",
            "candidate_index": 0,
            "work_directory": str(self.root),
            "scene_window": self.manifest["scene_window"],
            "submission_manifest": {"path": str(self.manifest_path), "sha256": digest(self.manifest_path)},
            "prompt": self.manifest["prompt"],
            "style_lock": self.manifest["style_lock"],
            "importance_profile": self.manifest["importance_profile"],
            "revision_gate": self.manifest["revision_gate"],
            "retry_control": self.manifest["retry_control"],
            "uploaded_inputs": inputs,
            "download": {"path": str(output), "sha256": digest(output)},
        }

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def refresh_manifest_binding(self):
        self.write_manifest()
        self.receipt["submission_manifest"] = {"path": str(self.manifest_path), "sha256": digest(self.manifest_path)}

    def test_valid_scene_window_receipt_passes(self):
        result = validate(self.receipt)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["checks"]["original_style_sha256"], CANONICAL_STYLE_SHA256)
        self.assertEqual(result["checks"]["scene_window_id"], "scene-synthetic-r1")

    def test_external_browser_receipt_passes_when_window_and_manifest_match(self):
        window_path = Path(self.receipt["scene_window"]["path"])
        window = json.loads(window_path.read_text())
        for browser in ("chrome", "edge"):
            window["browser"] = browser
            window_path.write_text(json.dumps(window))
            window_ref = {"path": str(window_path), "sha256": digest(window_path)}
            self.receipt["browser"] = browser
            self.receipt["scene_window"] = window_ref
            self.manifest["browser"] = browser
            self.manifest["scene_window"] = window_ref
            self.refresh_manifest_binding()
            self.assertEqual(validate(self.receipt)["status"], "PASS")

    def test_legacy_v2_requires_explicit_audit_allowance(self):
        self.receipt["schema"] = "ndc-chatgpt-web-generation-receipt/v2"
        self.receipt["submission_tool"] = "chatgpt_web_iab"
        for key in ("generation_unit_id", "actor_id", "scene_window", "style_lock", "revision_gate", "retry_control"):
            self.receipt.pop(key)
            self.manifest.pop(key)
        self.manifest.pop("browser")
        self.manifest["schema"] = "ndc-chatgpt-web-submission-packet/v1"
        self.refresh_manifest_binding()
        self.assertEqual(validate(self.receipt)["status"], "FAIL")
        self.assertEqual(validate(self.receipt, allow_legacy_v2=True)["status"], "PASS")

    def test_legacy_v3_requires_explicit_audit_allowance(self):
        self.receipt["schema"] = "ndc-chatgpt-web-generation-receipt/v3"
        self.receipt.pop("revision_gate")
        self.receipt.pop("retry_control")
        self.manifest.pop("revision_gate")
        self.manifest.pop("retry_control")
        self.manifest["schema"] = "ndc-chatgpt-web-submission-packet/v2"
        window_path = Path(self.receipt["scene_window"]["path"])
        window = json.loads(window_path.read_text())
        window["schema"] = "ndc-chatgpt-web-scene-window-identity/v1"
        window.pop("workspace_kind")
        window.pop("physical_window_required")
        window_path.write_text(json.dumps(window))
        window_ref = {"path": str(window_path), "sha256": digest(window_path)}
        self.receipt["scene_window"] = window_ref
        self.manifest["scene_window"] = window_ref
        self.refresh_manifest_binding()
        self.assertEqual(validate(self.receipt)["status"], "FAIL")
        self.assertEqual(validate(self.receipt, allow_legacy_v3=True)["status"], "PASS")

    def test_codex_backend_or_wrong_reference_order_fails(self):
        self.receipt["codex_image_generation_used"] = True
        self.receipt["uploaded_inputs"].reverse()
        result = validate(self.receipt)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("codex_image_generation_used" in item for item in result["errors"]))
        self.assertTrue(any("exact order" in item for item in result["errors"]))

    def test_manifest_or_scene_window_drift_fails(self):
        self.receipt["actor_id"] = "different"
        self.assertTrue(any("submission_manifest" in item for item in validate(self.receipt)["errors"]))
        self.receipt["actor_id"] = "actor-a"
        self.receipt["scene_id"] = "other-scene"
        errors = validate(self.receipt)["errors"]
        self.assertTrue(any("scene_window" in item or "submission_manifest" in item for item in errors))

    def test_style_or_download_substitution_fails(self):
        style = Path(self.receipt["style_lock"]["path"])
        style.write_text("modified style", encoding="utf-8")
        outside = self.root.parent / (self.root.name + "-outside.txt")
        outside.write_text("not an image", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        self.receipt["download"] = {"path": str(outside), "sha256": digest(outside)}
        result = validate(self.receipt)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("style_lock" in item for item in result["errors"]))
        self.assertTrue(any("original PNG" in item for item in result["errors"]))
        self.assertTrue(any("work_directory" in item for item in result["errors"]))

    def test_prompt_must_contain_original_style_exactly_once_even_if_manifest_is_rebound(self):
        prompt = Path(self.receipt["prompt"]["path"])
        prompt.write_text("style omitted", encoding="utf-8")
        self.receipt["prompt"]["sha256"] = digest(prompt)
        self.manifest["prompt"] = self.receipt["prompt"]
        self.refresh_manifest_binding()
        errors = validate(self.receipt)["errors"]
        self.assertTrue(any("exact original user style bytes once" in item for item in errors))

    def test_current_receipt_requires_real_timestamps_and_conversation_url(self):
        self.receipt["submitted_at"] = "FILL_AFTER_SUBMISSION"
        self.receipt["conversation_url"] = "https://chatgpt.com/g/custom"
        errors = validate(self.receipt)["errors"]
        self.assertTrue(any("ISO-8601" in item for item in errors))
        self.assertTrue(any("concrete" in item for item in errors))

    def test_uploaded_reference_must_be_an_actual_image(self):
        reference = Path(self.receipt["uploaded_inputs"][0]["path"])
        reference.write_text("not an image", encoding="utf-8")
        self.receipt["uploaded_inputs"][0]["sha256"] = digest(reference)
        self.manifest["uploaded_inputs"] = self.receipt["uploaded_inputs"]
        self.refresh_manifest_binding()
        self.assertTrue(any("PNG, JPEG or WebP" in item for item in validate(self.receipt)["errors"]))


if __name__ == "__main__":
    unittest.main()
