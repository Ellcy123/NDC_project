import hashlib
import os
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
import zlib

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from download_receipt import (  # noqa: E402
    DEFAULT_LOCK,
    begin,
    complete_event,
    release_lock,
    settle,
    verify,
)


def png_bytes(width: int, height: int, value: int = 0) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    row = bytes([0]) + bytes([value, value, value, 255]) * width
    payload = zlib.compress(row * height)
    return signature + chunk(b"IHDR", ihdr) + chunk(b"IDAT", payload) + chunk(b"IEND", b"")


class DownloadReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="download-receipt-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.downloads = self.root / "downloads"
        self.downloads.mkdir()
        self.snapshot = self.root / "snapshot.json"
        self.receipt = self.root / "receipt.json"

    def arm(self):
        return begin(self.downloads, self.snapshot, "test-owner")

    def test_snapshot_timestamps_are_timezone_aware_and_lock_is_exclusive(self):
        snapshot = self.arm()
        self.assertTrue(snapshot["captured_at_utc"].endswith("Z"))
        self.assertRegex(snapshot["captured_at_local"], r"[+-][0-9]{2}:[0-9]{2}$")
        with self.assertRaisesRegex(RuntimeError, "already locked"):
            begin(self.downloads, self.root / "second.json", "other-owner")
        release_lock(snapshot)
        self.assertFalse((self.downloads / DEFAULT_LOCK).exists())

    def test_stale_preexisting_file_is_never_selected(self):
        stale = self.downloads / "old.png"
        stale.write_bytes(png_bytes(2, 2))
        os.utime(stale, (time.time() - 3600, time.time() - 3600))
        self.arm()
        result = settle(self.snapshot, self.receipt, 0.05, 0.01)
        self.assertEqual(result["status"], "NO_NEW_FILE_OBSERVED")
        self.assertIsNone(result["selected"])

    def test_unique_new_file_is_selected_and_verified(self):
        self.arm()
        target = self.downloads / "new.png"
        target.write_bytes(png_bytes(3, 4, 10))
        result = settle(self.snapshot, self.receipt, 0.15, 0.01, expected_width=3, expected_height=4)
        self.assertEqual(result["status"], "UNIQUE_DIRECTORY_DELTA")
        self.assertEqual(result["selected"]["width"], 3)
        self.assertTrue(verify(self.receipt)["verified"])

    def test_two_new_files_are_ambiguous(self):
        self.arm()
        (self.downloads / "a.png").write_bytes(png_bytes(1, 1, 1))
        (self.downloads / "b.png").write_bytes(png_bytes(1, 1, 2))
        result = settle(self.snapshot, self.receipt, 0.15, 0.01)
        self.assertEqual(result["status"], "AMBIGUOUS_DIRECTORY_DELTA")
        self.assertIsNone(result["selected"])

    def test_same_filename_overwrite_is_detected_by_identity_change(self):
        target = self.downloads / "same.png"
        target.write_bytes(png_bytes(2, 2, 1))
        self.arm()
        time.sleep(0.01)
        target.write_bytes(png_bytes(5, 6, 2))
        os.utime(target, None)
        result = settle(self.snapshot, self.receipt, 0.15, 0.01, expected_width=5, expected_height=6)
        self.assertEqual(result["status"], "UNIQUE_DIRECTORY_DELTA")

    def test_expected_hash_mismatch_fails_validation(self):
        self.arm()
        (self.downloads / "new.png").write_bytes(png_bytes(2, 3))
        result = settle(self.snapshot, self.receipt, 0.15, 0.01, expected_sha256="0" * 64)
        self.assertEqual(result["status"], "CANDIDATE_VALIDATION_FAILED")
        self.assertIn("sha256 mismatch", result["selected"]["validation_errors"])

    def test_event_path_uses_only_path_and_can_copy_to_packet(self):
        self.arm()
        event_path = self.root / "playwright-temp.png"
        event_path.write_bytes(png_bytes(7, 8, 3))
        destination = self.root / "packet" / "scene-r1-pose-attempt001-candidate01.png"
        result = complete_event(self.snapshot, event_path, self.receipt, destination, 7, 8)
        self.assertEqual(result["status"], "EVENT_PATH_VERIFIED")
        self.assertEqual(result["selected"]["sha256"], hashlib.sha256(destination.read_bytes()).hexdigest())
        self.assertTrue(verify(self.receipt)["verified"])


if __name__ == "__main__":
    unittest.main()
