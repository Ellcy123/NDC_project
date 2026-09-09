#!/usr/bin/env python3
"""Audit registered planning art Skills for portable, self-contained support files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


EXECUTABLE_SUFFIXES = {".py", ".mjs", ".js", ".cjs", ".ps1", ".json"}
MACHINE_PATH = re.compile(r"(?i)(?<![a-z])(?:c:\\users\\|[d-z]:[\\/]|/users/[^/]+/)")


def audit(root: Path) -> dict:
    registry_path = root / "production" / "art_pipeline" / "skill_sources.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    checked: list[dict] = []
    names: set[str] = set()
    for row in registry.get("skills", []):
        if row.get("owner_scope") != "planning" or str(row.get("status", "")).startswith(("retired", "removed")):
            continue
        name = row.get("name", "")
        if name in names:
            errors.append(f"duplicate registry name: {name}")
            continue
        names.add(name)
        relative = row.get("path", "")
        skill_root = (root / relative).resolve()
        try:
            skill_root.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{name}: path escapes planning repository: {relative}")
            continue
        if not (skill_root / "SKILL.md").is_file():
            errors.append(f"{name}: missing SKILL.md at {relative}")
            continue
        scripts = []
        script_root = skill_root / "scripts"
        if script_root.is_dir():
            scripts = sorted(path for path in script_root.rglob("*") if path.is_file())
            for path in scripts:
                if path.suffix.lower() in EXECUTABLE_SUFFIXES:
                    text = path.read_text(encoding="utf-8-sig", errors="replace")
                    if MACHINE_PATH.search(text):
                        errors.append(f"{name}: machine-specific absolute path in {path.relative_to(skill_root).as_posix()}")
        checked.append({"name": name, "path": relative, "script_files": len(scripts)})
    return {"schema": "ndc-art-skill-bundle-audit/v1", "ok": not errors,
            "planning_skills": len(checked), "checked": checked, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = audit(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
