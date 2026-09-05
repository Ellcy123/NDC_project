"""Exercise real job closure and destructive-boundary behavior in isolated folders."""
import argparse
import contextlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import art_workspace as workspace
from art_paths import load_art_paths


class WorkspaceLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ndc-art-lifecycle-")
        self.root = Path(self.temp.name)
        self.engine = self.root / "engine"
        self.engine.mkdir()
        self.work = self.root / "work"
        self.config = self.root / "paths.json"
        self.data = {"schema": "ndc-art-workspace/v1", "engine_root": str(self.engine),
                     "work_root": str(self.work), "character_registry": "registry.json",
                     "quota_gib": 1, "minimum_free_gib": 0}
        self.config.write_text(json.dumps(self.data), encoding="utf-8")
        self.environ = patch.dict(os.environ, {"NDC_ART_PATHS_CONFIG": str(self.config)})
        self.environ.start()
        self.override = patch.dict(os.environ)
        self.override.start()
        os.environ.pop("NDC_ART_WORK_ROOT", None)
        os.environ.pop("NDC_ENGINE_ROOT", None)
        self.paths = load_art_paths()

    def tearDown(self):
        self.override.stop()
        self.environ.stop()
        self.temp.cleanup()

    def call(self, command, **kwargs):
        return workspace.run(argparse.Namespace(command=command, **kwargs))

    def job(self):
        return Path(self.call("create", name="角色测试", kind="test")["job"])

    def source(self, job, name="result.png"):
        path = job / "payload" / name
        path.write_bytes(b"a small opaque stand-in; no real art")
        return path

    def approve(self, job):
        self.call("approve", job=job, asset=["result.png"], note="isolated user-selection fixture")

    def copy(self, job, source, destination, kind="delivery"):
        destination.write_bytes(source.read_bytes())
        self.call("record-copy", job=job, source=source.name, destination=destination, kind=kind)

    def test_confirmed_delivery_cleans_payload_only(self):
        job = self.job()
        source = self.source(job)
        self.approve(job)
        destination = self.engine / "result.png"
        self.copy(job, source, destination)
        self.call("close", job=job, result="delivered", note="verified isolated delivery")
        self.assertFalse((job / "payload").exists())
        self.assertTrue((job / "job.json").is_file())
        self.assertEqual(destination.read_bytes(), b"a small opaque stand-in; no real art")

    def test_waiting_job_and_unmanaged_files_are_never_cleaned(self):
        job = self.job()
        source = self.source(job)
        self.call("ready", job=job)
        legacy = self.work / "old-unclassified"
        legacy.mkdir()
        (legacy / "keep.png").write_bytes(b"keep")
        self.call("cleanup", job=None, apply=True)
        self.assertTrue(source.exists())
        self.assertTrue((legacy / "keep.png").exists())

    def test_changed_delivery_prevents_closure_and_cleanup(self):
        job = self.job()
        source = self.source(job)
        self.approve(job)
        destination = self.engine / "result.png"
        self.copy(job, source, destination)
        destination.write_bytes(b"modified after copy")
        with self.assertRaises(ValueError):
            self.call("close", job=job, result="delivered", note="attempt closure")
        self.assertTrue(source.exists())
        self.assertEqual(json.loads((job / "job.json").read_text())["state"], "approved")

    def test_unretained_master_blocks_cancel_cleanup(self):
        job = self.job()
        source = self.source(job, "master.psd")
        self.call("mark-master", job=job, source="master.psd")
        with self.assertRaises(ValueError):
            self.call("close", job=job, result="cancelled", note="user abandons draft")
        self.copy(job, source, self.root / "durable-master.psd", kind="master")
        self.call("close", job=job, result="cancelled", note="user abandons draft")
        self.assertTrue((self.root / "durable-master.psd").exists())
        self.assertFalse((job / "payload").exists())

    def test_other_temporary_job_is_not_durable_retention(self):
        job, other = self.job(), self.job()
        source = self.source(job)
        destination = other / "payload" / "copy.png"
        with self.assertRaises(ValueError):
            self.copy(job, source, destination, kind="master")

    def test_arbitrary_folder_cannot_be_purged(self):
        with self.assertRaises(ValueError):
            self.call("cleanup", job=self.engine, apply=True)
        self.assertTrue(self.engine.exists())

    def test_new_job_does_not_evict_active_jobs_under_quota_pressure(self):
        job = self.job()
        source = self.source(job)
        self.data["quota_gib"] = 0.000000001
        self.config.write_text(json.dumps(self.data), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.job()
        self.assertTrue(source.exists())

    def test_nested_repository_work_root_is_rejected(self):
        self.data["work_root"] = str(self.engine / "art-output")
        self.config.write_text(json.dumps(self.data), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_art_paths()

    def test_changed_selected_source_requires_new_approval(self):
        job = self.job()
        source = self.source(job)
        self.approve(job)
        source.write_bytes(b"new pixels")
        with self.assertRaises(ValueError):
            self.copy(job, source, self.engine / "result.png")

    def test_interrupted_cleanup_can_resume_after_source_was_removed(self):
        job = self.job()
        source = self.source(job)
        remaining = self.source(job, "large-process.dat")
        self.approve(job)
        self.copy(job, source, self.engine / "result.png")
        def interrupted_delete(payload):
            source.unlink()
            raise PermissionError("simulated Windows file lock")
        with patch.object(workspace.shutil, "rmtree", side_effect=interrupted_delete):
            with self.assertRaises(PermissionError):
                self.call("close", job=job, result="delivered", note="confirmed copied result")
        self.assertTrue(remaining.exists())
        self.call("cleanup", job=job, apply=True)
        self.assertFalse((job / "payload").exists())
        self.assertTrue((self.engine / "result.png").exists())

    def test_cleanup_retry_retains_files_created_after_cleanup_started(self):
        job = self.job()
        self.source(job)
        with patch.object(workspace.shutil, "rmtree", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                self.call("close", job=job, result="cancelled", note="cancelled isolated task")
        new_file = self.source(job, "late-result.png")
        with self.assertRaises(ValueError):
            self.call("cleanup", job=job, apply=True)
        self.assertTrue(new_file.exists())

    def test_linked_payload_blocks_cleanup_without_touching_target(self):
        job = self.job()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep")
        link = job / "payload" / "linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Host does not permit test symlinks")
        try:
            with self.assertRaises(ValueError):
                self.call("close", job=job, result="cancelled", note="cancel linked fixture")
            self.assertTrue((outside / "keep.txt").exists())
        finally:
            link.unlink()


if __name__ == "__main__":
    unittest.main()
