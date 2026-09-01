from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import unittest
import uuid
from pathlib import Path

import evidence_publish


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidencePublishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.namespace = Path(tempfile.gettempdir()) / evidence_publish.TEMP_NAMESPACE
        self.work = self.namespace / f"test-{uuid.uuid4().hex}"
        self.work.mkdir(parents=True)
        self.output_parent = Path(tempfile.mkdtemp(prefix="ndc-publish-output-"))
        self.output = self.output_parent / "SC4022_morrison_study"

    def tearDown(self) -> None:
        if self.work.exists():
            import shutil

            shutil.rmtree(self.work)
        if self.output_parent.exists():
            import shutil

            shutil.rmtree(self.output_parent)

    def make_manifest(self, item_id: str, stem: str, x: int, *, icon: bool) -> Path:
        package = self.work / f"delivery-{item_id}"
        package.mkdir()
        scene = package / "scene_with_item.png"
        map_path = package / f"{stem}.png"
        detail_path = package / f"{stem}_big.png"
        scene.write_bytes(f"scene-{item_id}".encode("ascii"))
        map_path.write_bytes(f"map-{item_id}".encode("ascii"))
        detail_path.write_bytes(f"detail-{item_id}".encode("ascii"))
        artifacts = {
            "fullScene": {"path": str(scene), "sha256": digest(scene)},
            "mapSprite": {"path": str(map_path), "sha256": digest(map_path)},
            "detailSprite": {"path": str(detail_path), "sha256": digest(detail_path)},
        }
        unity = {
            "mapSpritePath": stem,
            "desSpritePath": f"{stem}_big",
            "Position": [str(x), "827", "-3"],
        }
        if icon:
            icon_path = package / f"{stem}_icon.png"
            icon_path.write_bytes(f"icon-{item_id}".encode("ascii"))
            artifacts["iconSprite"] = {
                "path": str(icon_path),
                "sha256": digest(icon_path),
            }
            unity["iconPath"] = f"{stem}_icon"
        manifest = {
            "passed": True,
            "item": {"id": item_id, "sceneId": "4022"},
            "unityDraft": unity,
            "icon": {"omitted": not icon},
            "artifacts": artifacts,
        }
        manifest_path = package / "delivery_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def test_publishes_one_xy_and_deletes_verified_temp_job(self) -> None:
        first = self.make_manifest("4323", "SC4022_envir_4323", 782, icon=False)
        second = self.make_manifest("4312", "SC4022_item_4312", 1046, icon=True)
        preview = self.work / "combined.png"
        preview.write_bytes(b"combined-scene")
        status = self.work / "batch.json"
        status.write_text(
            json.dumps(
                {
                    "records": [
                        {"id": "4323", "status": "packaged_pass"},
                        {"id": "4312", "status": "packaged_pass"},
                        {
                            "id": "4311",
                            "status": "skipped_after_3_failed_generations",
                            "reasons": ["attempt 1", "attempt 2", "attempt 3"],
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        args = argparse.Namespace(
            work_dir=self.work,
            output_dir=self.output,
            scene_preview=preview,
            manifest=[first, second],
            status_report=status,
            batch="Unit4_full_rebuild_v1",
            scene_id="4022",
            scene_name="Morrison study",
            cleanup_work_dir=True,
        )

        evidence_publish.publish_scene(args)

        self.assertFalse(self.work.exists())
        self.assertEqual(
            (self.output / "XYposition.txt").read_text(encoding="ascii"),
            "SC4022_envir_4323 782,827\nSC4022_item_4312 1046,827\n",
        )
        self.assertFalse((self.output / "ItemStaticData.patch.json").exists())
        self.assertFalse((self.output / "delivery_manifest.json").exists())
        self.assertTrue((self.output / "assets/SC4022_item_4312_icon.png").exists())
        report = json.loads(
            (self.output / "production_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["status"], "completed_with_skipped_records")
        self.assertEqual(report["skippedOrBlockedRecords"][0]["id"], "4311")
        self.assertTrue(report["temporaryWork"]["cleanupCompleted"])

    def test_rejects_non_namespaced_work_directory(self) -> None:
        outside = self.output_parent / "not-system-temp-work"
        outside.mkdir()
        with self.assertRaises(ValueError):
            evidence_publish.validated_work_dir(outside)

    def test_failed_publication_keeps_temp_job_for_recovery(self) -> None:
        manifest_path = self.make_manifest(
            "4312", "SC4022_item_4312", 1046, icon=True
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"]["mapSprite"]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        preview = self.work / "combined.png"
        preview.write_bytes(b"combined-scene")
        args = argparse.Namespace(
            work_dir=self.work,
            output_dir=self.output,
            scene_preview=preview,
            manifest=[manifest_path],
            status_report=None,
            batch="Unit4_full_rebuild_v1",
            scene_id="4022",
            scene_name="Morrison study",
            cleanup_work_dir=True,
        )

        with self.assertRaises(ValueError):
            evidence_publish.publish_scene(args)

        self.assertTrue(self.work.exists())
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
