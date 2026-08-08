#!/usr/bin/env python3
"""Ask a Gemini model through NovAI's OpenAI-compatible chat endpoint."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "https://us.novaiapi.com/v1"
DEFAULT_MODEL = "gemini-3.1-pro-preview"


def read_setting(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value

    if os.name != "nt":
        return None

    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value) if value else None
    except (FileNotFoundError, OSError):
        return None


def resolve_api_key() -> str | None:
    api_key = read_setting("NOVAI_API_KEY")
    if api_key:
        return api_key

    if not sys.stdin.isatty():
        return None

    return getpass.getpass("NOVAI_API_KEY: ").strip() or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call Gemini through the NovAI OpenAI-compatible API."
    )
    parser.add_argument("prompt", nargs="*", help="Prompt text")
    parser.add_argument("--prompt-file", type=Path, help="UTF-8 text file to use as the prompt")
    parser.add_argument("--model", help="Override NOVAI_GEMINI_MODEL")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout in seconds")
    return parser.parse_args()


def load_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file and args.prompt:
        raise ValueError("Use either prompt text or --prompt-file, not both.")

    if args.prompt_file:
        return args.prompt_file.read_text(encoding="utf-8").strip()

    if args.prompt:
        return " ".join(args.prompt).strip()

    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    raise ValueError("Provide prompt text, --prompt-file, or stdin input.")


def extract_text(payload: dict) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("NovAI returned no choices.")

    content = (choices[0].get("message") or {}).get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()

    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict)]
        text = "".join(parts).strip()
        if text:
            return text

    raise ValueError("NovAI returned an empty or unsupported message payload.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    args = parse_args()
    api_key = resolve_api_key()
    if not api_key:
        print(
            "NOVAI_API_KEY is not configured and no key was entered.",
            file=sys.stderr,
        )
        return 2

    try:
        prompt = load_prompt(args)
        if not prompt:
            raise ValueError("Prompt is empty.")
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    base_url = (read_setting("NOVAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    model = args.model or read_setting("NOVAI_GEMINI_MODEL") or DEFAULT_MODEL
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ndc-codex-novai-gemini/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        print(extract_text(payload))
        return 0
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:2000]
        print(f"NovAI HTTP {error.code}: {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as error:
        print(f"NovAI request failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
