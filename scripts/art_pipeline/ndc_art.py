#!/usr/bin/env python3
"""Portable NDC art entrypoint; shared implementation maintained in planning."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import stat
import subprocess
import sys

from art_paths import (LOCAL_SCHEMA, absolute_root, load_art_paths,
                       validate_roots)


TOOLS = {"stage": "validate_stage_visual_self_check.py",
         "texture": "validate_texture_gate.py",
         "final": "validate_final_visual_record_presence.py"}


def inside(root: Path, relative: str, *, directory: bool = False) -> Path:
    """Resolve a registered file without traversing a link or escaping its root."""
    posix = PurePosixPath(relative)
    if (not relative or "\\" in relative or posix.is_absolute()
            or PureWindowsPath(relative).drive or any(x in {"", ".", ".."} for x in relative.split("/"))):
        raise ValueError(f"Expected a safe relative path: {relative!r}")
    root = root.resolve()
    path = root.joinpath(*posix.parts)
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Path escapes its registered root: {relative}")
    for item in [root, *[root.joinpath(*posix.parts[:n]) for n in range(1, len(posix.parts) + 1)]]:
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Linked scripts and skill paths are not supported: {relative}")
    if directory:
        if not path.is_dir():
            raise ValueError(f"Expected a skill directory: {relative}")
    elif not path.is_file():
        raise ValueError(f"Expected a script or skill file: {relative}")
    return path


def resolve_skill(name: str, paths) -> dict:
    source = inside(paths.planning_root, "production/art_pipeline/skill_sources.json")
    registry = json.loads(source.read_text(encoding="utf-8-sig"))
    if registry.get("schema") != "ndc-art-skill-sources/v2":
        raise ValueError("Skill registry must use ndc-art-skill-sources/v2")
    matches = [row for row in registry["skills"] if row.get("name") == name]
    if len(matches) != 1:
        raise ValueError(f"Unknown or ambiguous art skill: {name}")
    skill = matches[0]
    owner = skill["owner_scope"]
    if owner not in {"planning", "engine"} or str(skill.get("status", "")).startswith(("retired", "removed")):
        raise ValueError(f"Skill has no active supported owner: {name}")
    root = paths.planning_root if owner == "planning" else paths.engine_root
    skill_root = inside(root, skill["path"], directory=True)
    main = inside(skill_root, "SKILL.md")
    return {"name": name, "owner": owner, "path": str(main), "skill_root": str(skill_root)}


def configured_environment(paths) -> dict:
    environment = dict(os.environ)
    environment.update({"NDC_PLANNING_ROOT": str(paths.planning_root),
                        "NDC_ENGINE_ROOT": str(paths.engine_root),
                        "NDC_ART_WORK_ROOT": str(paths.work_root),
                        "PYTHONIOENCODING": "utf-8"})
    return environment


def managed_output(value: str, paths) -> Path:
    """Keep protected legacy packagers within an existing managed job payload."""
    from art_workspace import CLOSED, load_job, reparse

    raw = Path(value).absolute()
    try:
        relative = raw.relative_to(paths.work_root)
    except ValueError as exc:
        raise ValueError("Output directory must be in a managed job payload") from exc
    if len(relative.parts) < 3 or relative.parts[0] != "jobs" or relative.parts[2] != "payload":
        raise ValueError("Output directory must be under work_root/jobs/<job>/payload")
    job, record = load_job(paths.work_root / "jobs" / relative.parts[1], paths)
    if record.get("state") in CLOSED or record.get("cleanup"):
        raise ValueError("Output job is closed; create a new job")
    payload = job / "payload"
    if not payload.is_dir() or not raw.resolve().is_relative_to(payload):
        raise ValueError("Output directory escapes its managed payload")
    for item in [raw, *raw.parents]:
        if item == job:
            break
        if item.is_symlink() or (item.exists() and reparse(item)):
            raise ValueError("Linked output paths are forbidden")
    return raw


def check_legacy_output(script: Path, arguments: list[str], paths) -> None:
    # The colleague-owned packager has an old machine-specific Unity guard.
    # Adapt its dispatch without rewriting that actively edited implementation.
    values = arguments[1:] if arguments[:1] == ["--"] else arguments
    if script.name != "evidence_delivery.py" or values[:1] != ["package"] or any(x in values for x in ("--help", "-h")):
        return
    for value in values[1:]:
        option = value.split("=", 1)[0]
        if (option.startswith("--") and option != "--" and option != "--output-dir"
                and "--output-dir".startswith(option)):
            raise ValueError("Use the full --output-dir option; abbreviated output options are not supported")
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--output-dir", required=True)
    selected, _ = parser.parse_known_args(values[1:])
    managed_output(selected.output_dir, paths)


def run_script(script: Path, arguments: list[str], paths) -> int:
    extension = script.suffix.lower()
    if extension == ".py":
        command = [sys.executable, "-B", str(script)]
    elif extension == ".ps1":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            raise ValueError("PowerShell is required to run this script")
        command = [shell, "-NoLogo", "-NoProfile", "-File", str(script)]
    elif extension in {".js", ".cjs", ".mjs"}:
        node = shutil.which("node")
        if not node:
            raise ValueError("Node.js is required to run this script")
        command = [node, str(script)]
    else:
        raise ValueError(f"Unsupported script type: {extension}; use py, ps1, js, cjs, or mjs")
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    # Relative data arguments retain the caller's meaning; resources internal to
    # a script should be resolved from that script's __file__, not from cwd.
    return subprocess.run(command + arguments, env=configured_environment(paths)).returncode


def configure(args) -> dict:
    planning = absolute_root(args.planning_root, "planning_root")
    engine = absolute_root(args.engine_root, "engine_root")
    work = absolute_root(args.work_root, "work_root")
    validate_roots(planning, engine, work)
    for root in (planning, engine):
        inside(root, "scripts/art_pipeline/ndc_art.py")
    inside(planning, "production/art_pipeline/paths.json")
    content = json.dumps({"schema": LOCAL_SCHEMA, "planning_root": str(planning),
                          "engine_root": str(engine), "work_root": str(work)},
                         ensure_ascii=False, indent=2) + "\n"
    snapshots = {}
    staged = []
    replaced = []
    try:
        for root in (planning, engine):
            target = root / "ndc.local.json"
            if target.is_symlink() or (target.exists() and getattr(target.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError(f"Machine configuration must not be a link: {target}")
            snapshots[target] = target.read_bytes() if target.exists() else None
            temporary = root / "ndc.local.json.tmp"
            # Never overwrite an unrelated or interrupted writer's staging file.
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            staged.append((temporary, target))
        for temporary, target in staged:
            current = target.read_bytes() if target.exists() else None
            if current != snapshots[target]:
                raise ValueError(f"Machine configuration changed during configure: {target}")
            temporary.replace(target)
            replaced.append(target)
    except Exception:
        for target in reversed(replaced):
            before = snapshots[target]
            if before is None:
                target.unlink()
            else:
                target.write_bytes(before)
        raise
    finally:
        for temporary, _ in staged:
            if temporary.exists():
                temporary.unlink()
    return {"status": "configured", "planning_root": str(planning), "engine_root": str(engine),
            "work_root": str(work), "local_files": [str(root / "ndc.local.json") for root in (planning, engine)]}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("configure", help="Save machine paths in both ignored ndc.local.json files")
    for name in ("planning", "engine", "work"):
        setup.add_argument(f"--{name}-root", required=True)
    sub.add_parser("paths", help="Show resolved checkout, work, and reference paths")
    skill = sub.add_parser("skill", help="Resolve a main skill from the shared registry")
    skill.add_argument("name")
    run = sub.add_parser("run", help="Run a registered skill's own script")
    run.add_argument("name")
    run.add_argument("script")
    run.add_argument("arguments", nargs=argparse.REMAINDER)
    workspace = sub.add_parser("workspace", help="Forward arguments to the planning workspace manager")
    workspace.add_argument("arguments", nargs=argparse.REMAINDER)
    tool = sub.add_parser("tool", help="Run a shared evidence-record validator")
    tool.add_argument("name", choices=TOOLS)
    tool.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.command == "configure":
            result = configure(args)
        else:
            paths = load_art_paths()
            if args.command == "paths":
                result = asdict(paths)
            elif args.command == "skill":
                result = resolve_skill(args.name, paths)
            elif args.command == "run":
                resolved = resolve_skill(args.name, paths)
                script = inside(Path(resolved["skill_root"]), "scripts/" + args.script)
                check_legacy_output(script, args.arguments, paths)
                return run_script(script, args.arguments, paths)
            else:
                filename = "art_workspace.py" if args.command == "workspace" else TOOLS[args.name]
                script = inside(paths.planning_root, "scripts/art_pipeline/" + filename)
                return run_script(script, args.arguments, paths)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
