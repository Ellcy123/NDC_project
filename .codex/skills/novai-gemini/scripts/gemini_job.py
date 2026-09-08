#!/usr/bin/env python3
"""Submit one durable Gemini request; inspect it without a terminal session ID."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
from urllib.parse import urlsplit
from datetime import datetime, timezone

from ask_gemini import DEFAULT_BASE_URL, DEFAULT_MODEL, extract_text, read_setting, request_completion


TERMINAL = {"succeeded", "failed", "uncertain"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path: Path, text: str) -> None:
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    # Windows readers briefly deny replacement while status is being queried.
    # Retry only the local rename; never repeat the HTTP request.
    for attempt in range(20):
        try:
            os.replace(temp, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.05)


def write_json(path: Path, value: dict) -> None:
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_status(run_dir: Path, state: str, **details) -> None:
    write_json(run_dir / "status.json", {
        "run_id": run_dir.name, "status": state, "updated_at": now(), **details,
    })


def default_runs_dir() -> Path:
    configured = os.environ.get("NOVAI_GEMINI_RUNS_DIR")
    if configured:
        return Path(configured).expanduser()
    codex_dir = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return codex_dir / "novai-gemini" / "runs"


def locate_run(root: Path, run_id: str) -> Path:
    run_id = run_id.lower()
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    if (not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,79}", run_id)
            or run_id.endswith(".") or run_id.split(".")[0] in reserved):
        raise ValueError("run-id must be a safe 1-80 character name using letters, digits, _, . or -.")
    root = root.expanduser().resolve()
    run_dir = (root / run_id).resolve()
    if run_dir.parent != root:
        raise ValueError("Run directory must stay inside runs-dir.")
    return run_dir


def process_alive(pid: int) -> bool | None:
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False if ctypes.get_last_error() == 87 else None
        try:
            code = ctypes.c_ulong()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                return None
            return code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return None


def status(run_dir: Path) -> dict:
    if not run_dir.is_dir():
        raise ValueError(f"Unknown run-id: {run_dir.name}")
    path = run_dir / "status.json"
    value = read_json(path) if path.exists() else {"run_id": run_dir.name, "status": "initializing"}
    if value["status"] not in TERMINAL:
        launcher = run_dir / "launcher.json"
        pid = value.get("pid") or (read_json(launcher).get("pid") if launcher.exists() else None)
        if pid and process_alive(pid) is False:
            # Re-read after the process exits: it may just have committed its result.
            value = read_json(path) if path.exists() else value
            if value["status"] not in TERMINAL:
                value = {**value, "status": "uncertain", "error": {
                    "kind": "worker_exited", "message": "Worker exited without a final status; do not auto-resubmit.",
                }}
    request = run_dir / "request.json"
    if request.exists():
        value["model"] = read_json(request)["model"]
    return {**value, "run_dir": str(run_dir), "answer_file": str(run_dir / "answer.md")}


def submit(args) -> dict:
    run_dir = locate_run(args.runs_dir, args.run_id)
    prompt = args.prompt_file.read_text(encoding="utf-8-sig") if args.prompt_file else args.prompt
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Prompt is empty.")
    if args.timeout <= 0:
        raise ValueError("Timeout must be positive.")
    base_url = (read_setting("NOVAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    url = urlsplit(base_url)
    if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError("NOVAI_BASE_URL must be an HTTP(S) URL without credentials, query or fragment.")
    request = {
        "model": args.model or read_setting("NOVAI_GEMINI_MODEL") or DEFAULT_MODEL,
        "base_url": base_url, "timeout": args.timeout,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
    }
    if run_dir.exists():
        if not (run_dir / "request.json").exists():
            raise ValueError("Run initialization is incomplete. Inspect status; do not create a replacement request.")
        if read_json(run_dir / "request.json") != request:
            raise ValueError("run-id already exists with different inputs. Existing request was not changed or resubmitted.")
        return {**status(run_dir), "reused": True}
    api_key = read_setting("NOVAI_API_KEY")
    if not api_key:
        raise ValueError("NOVAI_API_KEY is not configured.")
    run_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        run_dir.mkdir()  # Exclusive reservation: concurrent submits cannot both launch.
    except FileExistsError:
        raise ValueError("Run was reserved by another submit. Query status for this run-id.") from None
    atomic_write(run_dir / "prompt.md", prompt)
    write_json(run_dir / "request.json", request)
    write_status(run_dir, "queued", submitted_at=now())
    env = dict(os.environ, NOVAI_API_KEY=api_key, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    options = {"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    try:
        with (run_dir / "worker.log").open("ab") as log:
            child = subprocess.Popen(
                [sys.executable, "-B", str(Path(__file__).resolve()), "_worker", "--run-dir", str(run_dir)],
                stdin=subprocess.DEVNULL, stdout=log, stderr=log, env=env, close_fds=True, **options,
            )
    except OSError:
        write_status(run_dir, "failed", error={"kind": "launch_failed", "message": "Could not launch local worker; no request submitted."})
        raise
    # Failure to save this receipt does not mean the already-launched request failed.
    # The worker still writes its own PID and result; query the same run-id to recover.
    write_json(run_dir / "launcher.json", {"pid": child.pid, "launched_at": now()})
    return {**status(run_dir), "reused": False}


def worker(run_dir: Path) -> int:
    try:
        with (run_dir / "worker.lock").open("x", encoding="utf-8") as lock:
            lock.write(str(os.getpid()))
    except FileExistsError:
        return 0
    started = time.monotonic()
    details = {"pid": os.getpid(), "started_at": now()}
    write_status(run_dir, "running", **details)
    try:
        request = read_json(run_dir / "request.json")
        prompt = (run_dir / "prompt.md").read_text(encoding="utf-8")
        if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != request["prompt_sha256"]:
            raise ValueError("Saved prompt changed; request was not submitted.")
        api_key = read_setting("NOVAI_API_KEY")
        if not api_key:
            raise ValueError("NOVAI_API_KEY is not configured; request was not submitted.")
        payload = request_completion(prompt, model=request["model"], base_url=request["base_url"], api_key=api_key, timeout=request["timeout"])
        write_json(run_dir / "response.json", payload)
        answer = extract_text(payload)
        atomic_write(run_dir / "answer.md", answer + "\n")
        usage = payload.get("usage")
        if isinstance(usage, dict):
            write_json(run_dir / "usage.json", usage)
        write_status(run_dir, "succeeded", **details, elapsed_seconds=round(time.monotonic() - started, 3),
                     response_model=payload.get("model"), usage=usage)
        return 0
    except Exception as error:
        if isinstance(error, urllib.error.HTTPError):
            state, kind, message = "failed", "http_error", f"NovAI HTTP {error.code}."
        elif isinstance(error, (TimeoutError, urllib.error.URLError, ConnectionError)):
            state, kind, message = "uncertain", "transport_error", "Connection failed or timed out; provider completion is unknown. Do not auto-resubmit."
        elif isinstance(error, (ValueError, TypeError, KeyError, AttributeError)):
            state, kind, message = "failed", "invalid_response_or_input", "Invalid input, empty, malformed or truncated response. Inspect saved response.json if present."
        else:
            state, kind, message = "uncertain", "local_error", "Local processing failed; inspect saved files before considering another request."
        write_status(run_dir, state, **details, elapsed_seconds=round(time.monotonic() - started, 3), error={"kind": kind, "message": message})
        return 1


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("submit", "status", "result"):
        sub = subs.add_parser(name)
        sub.add_argument("--run-id", required=True)
        sub.add_argument("--runs-dir", type=Path, default=default_runs_dir())
        if name == "submit":
            source = sub.add_mutually_exclusive_group(required=True)
            source.add_argument("--prompt-file", type=Path)
            source.add_argument("--prompt", help="Short literal prompt; use --prompt-file for longer material")
            sub.add_argument("--model")
            sub.add_argument("--timeout", type=int, default=120)
    private = subs.add_parser("_worker", help="Internal background worker; operators use submit/status/result")
    private.add_argument("--run-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        if args.command == "_worker":
            return worker(args.run_dir)
        value = submit(args) if args.command == "submit" else status(locate_run(args.runs_dir, args.run_id))
        if args.command == "result":
            if value["status"] != "succeeded":
                print(json.dumps(value, ensure_ascii=False), file=sys.stderr)
                return 3 if value["status"] in {"initializing", "queued", "running"} else 1
            print(Path(value["answer_file"]).read_text(encoding="utf-8"), end="")
        else:
            print(json.dumps(value, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
