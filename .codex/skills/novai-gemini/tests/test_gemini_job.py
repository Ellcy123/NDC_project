"""Offline integration tests, including a response beyond the 30-second tool window."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import uuid


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from gemini_job import process_alive


FAKE_KEY = "offline-test-key-not-a-real-credential"
REQUESTS = []
REQUEST_LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = body["messages"][0]["content"]
        with REQUEST_LOCK:
            REQUESTS.append(body)
        mode = prompt.split("|")[0]
        if mode == "slow":
            time.sleep(32)
        elif mode in {"timeout", "interrupted"}:
            time.sleep(2)
        if mode == "disconnect":
            self.close_connection = True
            self.connection.close()
            return
        payload = {"choices": [{"message": {"content": "收到：" + prompt}, "finish_reason": "stop"}],
                   "usage": {"prompt_tokens": 9, "completion_tokens": 4, "total_tokens": 13}}
        if mode == "empty":
            payload["choices"][0]["message"]["content"] = "   "
        if mode == "truncated":
            payload["choices"][0]["finish_reason"] = "length"
        code = 503 if mode == "http-error" else 200
        if mode == "http-error":
            payload = {"error": "Echoed Authorization: Bearer " + FAKE_KEY}
        raw = b"not-json" if mode == "malformed" else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass


class JobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ndc-gemini-test-")
        self.root = Path(self.temp.name).resolve()
        self.runs = self.root / "runs"
        self.env = dict(os.environ, NOVAI_API_KEY=FAKE_KEY,
                        NOVAI_BASE_URL=f"http://127.0.0.1:{self.server.server_port}/v1",
                        NOVAI_GEMINI_MODEL="offline-model", PYTHONDONTWRITEBYTECODE="1")

    def tearDown(self):
        # Only terminate workers created in this test's uniquely owned directory.
        for launcher in self.runs.glob("*/launcher.json"):
            self.assertTrue(launcher.resolve().is_relative_to(self.root))
            pid = json.loads(launcher.read_text())["pid"]
            end = time.monotonic() + 3
            while process_alive(pid) and time.monotonic() < end:
                time.sleep(0.05)
            if process_alive(pid):
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.2)
        self.temp.cleanup()

    def cli(self, command, run_id="test", *extra):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / "gemini_job.py"), command,
                               "--runs-dir", str(self.runs), "--run-id", run_id, *extra],
                              env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=10)

    def launch(self, prompt, run_id="test", timeout=60):
        path = self.root / (run_id + "-input.md")
        path.write_text(prompt, encoding="utf-8-sig")
        result = self.cli("submit", run_id, "--prompt-file", str(path), "--timeout", str(timeout))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), path

    def finish(self, run_id="test", limit=10):
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            result = self.cli("status", run_id)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            if value["status"] in {"succeeded", "failed", "uncertain"}:
                return value
            time.sleep(0.1)
        self.fail("Worker did not reach a terminal state")

    def count(self, prompt):
        with REQUEST_LOCK:
            return sum(r["messages"][0]["content"] == prompt for r in REQUESTS)

    def test_unicode_snapshot_usage_and_reuse(self):
        prompt = "unicode|" + str(uuid.uuid4()) + "\nEmma O'Malley：$HOME `引号` \\\"你好\\\""
        initial, path = self.launch(prompt)
        path.write_text("changed original", encoding="utf-8")
        done = self.finish()
        self.assertEqual(done["status"], "succeeded")
        answer = self.cli("result")
        self.assertEqual(answer.stdout.strip(), "收到：" + prompt)
        self.assertEqual(done["usage"]["total_tokens"], 13)
        run_dir = Path(initial["run_dir"])
        self.assertEqual((run_dir / "prompt.md").read_text(encoding="utf-8"), prompt)
        self.assertTrue((run_dir / "response.json").is_file())
        again = self.cli("submit", "test", "--prompt-file", str(run_dir / "prompt.md"), "--timeout", "60")
        self.assertTrue(json.loads(again.stdout)["reused"])
        self.assertEqual(self.count(prompt), 1)
        collision = self.cli("submit", "test", "--prompt", "different")
        self.assertNotEqual(collision.returncode, 0)
        self.assertEqual(self.count(prompt), 1)
        for file in run_dir.iterdir():
            if file.is_file():
                self.assertNotIn(FAKE_KEY, file.read_text(encoding="utf-8"))

    def test_empty_truncated_malformed_and_http_errors(self):
        for mode in ("empty", "truncated", "malformed", "http-error"):
            with self.subTest(mode=mode):
                prompt = mode + "|" + str(uuid.uuid4())
                initial, path = self.launch(prompt, run_id=mode)
                done = self.finish(mode)
                self.assertEqual(done["status"], "failed", done)
                self.assertFalse((Path(initial["run_dir"]) / "answer.md").exists())
                self.assertNotEqual(self.cli("result", mode).returncode, 0)
                again = self.cli("submit", mode, "--prompt-file", str(path), "--timeout", "60")
                self.assertTrue(json.loads(again.stdout)["reused"])
                self.assertEqual(self.count(prompt), 1)
                self.assertNotIn(FAKE_KEY, json.dumps(done))

    def test_timeout_and_disconnect_are_uncertain_without_retry(self):
        for mode in ("timeout", "disconnect"):
            with self.subTest(mode=mode):
                prompt = mode + "|" + str(uuid.uuid4())
                _, path = self.launch(prompt, run_id=mode, timeout=1)
                self.assertEqual(self.finish(mode)["status"], "uncertain")
                again = self.cli("submit", mode, "--prompt-file", str(path), "--timeout", "1")
                self.assertTrue(json.loads(again.stdout)["reused"])
                self.assertEqual(self.count(prompt), 1)

    def test_interrupted_worker_is_not_restarted(self):
        prompt = "interrupted|" + str(uuid.uuid4())
        initial, path = self.launch(prompt)
        deadline = time.monotonic() + 5
        while self.count(prompt) == 0 and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertEqual(self.count(prompt), 1)
        run_dir = Path(initial["run_dir"])
        pid = json.loads((run_dir / "launcher.json").read_text())["pid"]
        os.kill(pid, signal.SIGTERM)
        done = self.finish()
        self.assertEqual(done["status"], "uncertain")
        self.assertEqual(done["error"]["kind"], "worker_exited")
        self.cli("submit", "test", "--prompt-file", str(path), "--timeout", "60")
        self.assertEqual(self.count(prompt), 1)

    def test_duplicate_worker_cannot_submit_again(self):
        prompt = "unicode|" + str(uuid.uuid4())
        initial, _ = self.launch(prompt)
        self.assertEqual(self.finish()["status"], "succeeded")
        repeated = subprocess.run([sys.executable, "-B", str(SCRIPTS / "gemini_job.py"), "_worker",
                                   "--run-dir", initial["run_dir"]], env=self.env, capture_output=True, timeout=5)
        self.assertEqual(repeated.returncode, 0)
        self.assertEqual(self.count(prompt), 1)

    def test_invalid_paths_and_empty_prompt_do_not_submit(self):
        for run_id in ("../escape", "CON", "a/b", "test."):
            self.assertNotEqual(self.cli("submit", run_id, "--prompt", "unused").returncode, 0)
        self.assertNotEqual(self.cli("submit", "empty-input", "--prompt", "   ").returncode, 0)
        self.assertFalse(self.runs.exists())

    def test_legacy_cli_remains_usable(self):
        prompt = "unicode|legacy-" + str(uuid.uuid4())
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "ask_gemini.py"), prompt],
                                env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "收到：" + prompt)

    def test_z_response_after_30_seconds_survives_submit_exit(self):
        prompt = "slow|" + str(uuid.uuid4())
        started = time.monotonic()
        initial, path = self.launch(prompt)
        self.assertLess(time.monotonic() - started, 8, "submit must not await the HTTP response")
        self.assertIn(initial["status"], {"queued", "running"})
        self.assertEqual(self.cli("result").returncode, 3)
        # Discard the submit output. Recover exclusively with the preassigned run-id.
        again = self.cli("submit", "test", "--prompt-file", str(path), "--timeout", "60")
        self.assertTrue(json.loads(again.stdout)["reused"])
        done = self.finish(limit=45)
        self.assertEqual(done["status"], "succeeded")
        self.assertGreaterEqual(done["elapsed_seconds"], 31)
        self.assertEqual(self.cli("result").stdout.strip(), "收到：" + prompt)
        self.assertEqual(self.count(prompt), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
