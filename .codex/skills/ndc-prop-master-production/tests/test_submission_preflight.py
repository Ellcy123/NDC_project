import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "submission_preflight.py"
SPEC = importlib.util.spec_from_file_location("submission_preflight", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SubmissionPreflightTests(unittest.TestCase):
    def discovery(self, root, scope_sha):
        index = root / "asset-index.json"; index.write_text("{}", encoding="utf-8")
        receipt = {
            "schema": "ndc-asset-discovery-receipt/v1", "status": "CONFIRMED_ABSENT",
            "checked_at": "2026-09-13T12:00:00+08:00",
            "scope": {"domain": "prop", "scene_id": "GLOBAL", "revision": "r1", "item_id": "item-a", "pose_or_state": "default", "artifact_role": "master"},
            "freshness": {"scope_revision_sha256": scope_sha, "asset_index": {"path": str(index), "sha256": MODULE.sha256(index)}},
            "searches": [{"root_role": role, "root_path": str(root), "query_ids": ["item-a"], "aliases": ["item-a"], "completed": True} for role in ("official_runtime", "approved_archive", "formal_delivery")],
            "candidates": [],
        }
        receipt_path = root / "discovery.json"; receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return {"receipt": {"path": str(receipt_path), "sha256": MODULE.sha256(receipt_path)}, "scope": receipt["scope"], "scope_revision_sha256": scope_sha}

    def batch_scope(self, root):
        scope = root / "active-scope.json"; scope.write_text(json.dumps({"execution_required_artifacts": ["a"]}), encoding="utf-8")
        digest = MODULE.sha256(scope)
        return {"path": str(scope), "sha256": digest}, digest

    def test_wrong_scope_and_unknown_submission_are_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt = root / "prompt.txt"
            prompt.write_text("locked prompt", encoding="utf-8")
            pointer, scope_sha = self.batch_scope(root)
            batch = {
                "scope": {"required_artifacts": ["a"]},
                "artifacts": {"a": {"job_id": "a|master||x", "scene_id": ""}},
                "active_delivery_scope_revision": pointer,
            }
            batch_path = root / "batch.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            manifest = {
                "schema": MODULE.SCHEMA,
                "artifact_id": "outside",
                "job_id": "a|master||x",
                "scene_id": "",
                "item_id": "item-a", "pose_or_state": "default", "artifact_role": "master",
                "task_id": "task-x",
                "planned_task_attempt": 1,
                "prompt": {"path": str(prompt), "sha256": MODULE.sha256(prompt)},
                "references": [],
                "target": {"width": 512, "height": 512, "format": "PNG"},
                "backend": "authorized",
                "submission_state": "UNKNOWN",
                "discovery": self.discovery(root, scope_sha),
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            failures = MODULE.validate(manifest_path, batch_path)
            self.assertTrue(any("outside" in item for item in failures))
            self.assertTrue(any("submission" in item for item in failures))

    def test_current_task_attempt_must_match_append_log(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt = root / "prompt.txt"; prompt.write_text("locked", encoding="utf-8")
            log = root / "attempts.jsonl"
            log.write_text(json.dumps({"type": "attempt", "job_id": "a|master||x", "task_id": "task-x"}) + "\n",
                           encoding="utf-8")
            pointer, scope_sha = self.batch_scope(root)
            batch = {
                "scope": {"required_artifacts": ["a"]},
                "artifacts": {"a": {"job_id": "a|master||x", "scene_id": ""}},
                "jobs": {"a|master||x": {"kind": "master"}}, "attempt_log": "attempts.jsonl", "active_delivery_scope_revision": pointer,
            }
            batch_path = root / "batch.json"; batch_path.write_text(json.dumps(batch), encoding="utf-8")
            manifest = {
                "schema": MODULE.SCHEMA, "artifact_id": "a", "job_id": "a|master||x", "scene_id": "",
                "item_id": "item-a", "pose_or_state": "default", "artifact_role": "master",
                "task_id": "task-x", "planned_task_attempt": 2,
                "prompt": {"path": str(prompt), "sha256": MODULE.sha256(prompt)}, "references": [],
                "target": {"width": 512, "height": 512, "format": "PNG"},
                "backend": "authorized", "submission_state": "NOT_SUBMITTED",
                "scope_revision_sha256": scope_sha,
                "discovery": self.discovery(root, scope_sha),
            }
            manifest_path = root / "manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(MODULE.validate(manifest_path, batch_path), [])
            manifest["planned_task_attempt"] = 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(any("planned_task_attempt" in value for value in MODULE.validate(manifest_path, batch_path)))

    def test_discovery_scope_and_chatgpt_web_exception_are_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompt = root / "prompt.txt"; prompt.write_text("locked", encoding="utf-8")
            log = root / "attempts.jsonl"; log.write_text("", encoding="utf-8")
            pointer, scope_sha = self.batch_scope(root)
            batch = {"scope": {"required_artifacts": ["a"]}, "artifacts": {"a": {"job_id": "a|scene||x", "scene_id": "SC1"}},
                     "jobs": {"a|scene||x": {"kind": "scene"}}, "attempt_log": "attempts.jsonl", "active_delivery_scope_revision": pointer}
            batch_path = root / "batch.json"; batch_path.write_text(json.dumps(batch), encoding="utf-8")
            discovery = self.discovery(root, scope_sha)
            discovery["scope"].update(scene_id="SC1", artifact_role="scene_evidence")
            receipt_path = Path(discovery["receipt"]["path"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8")); receipt["scope"].update(scene_id="SC1", artifact_role="scene_evidence")
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8"); discovery["receipt"]["sha256"] = MODULE.sha256(receipt_path)
            manifest = {"schema": MODULE.SCHEMA, "artifact_id": "a", "job_id": "a|scene||x", "scene_id": "SC1", "item_id": "item-a", "pose_or_state": "default", "artifact_role": "scene_evidence",
                        "task_id": "task-x", "planned_task_attempt": 1, "prompt": {"path": str(prompt), "sha256": MODULE.sha256(prompt)}, "references": [],
                        "target": {"width": 512, "height": 512, "format": "PNG"}, "backend": "chatgpt_web", "submission_state": "NOT_SUBMITTED", "scope_revision_sha256": scope_sha, "discovery": discovery}
            manifest_path = root / "manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(MODULE.validate(manifest_path, batch_path), [])
            manifest["artifact_role"] = "master"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(any("discovery.scope" in value or "chatgpt_web" in value for value in MODULE.validate(manifest_path, batch_path)))


if __name__ == "__main__":
    unittest.main()
