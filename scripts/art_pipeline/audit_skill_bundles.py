#!/usr/bin/env python3
"""Audit registered planning art Skills for portable, self-contained support files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote


EXECUTABLE_SUFFIXES = {".py", ".mjs", ".js", ".cjs", ".ps1", ".json", ".html"}
TEXT_SUFFIXES = EXECUTABLE_SUFFIXES | {".md", ".yaml", ".yml", ".toml", ".txt", ".csv", ".tsv"}
MACHINE_PATH = re.compile(r"(?i)(?<![a-z])(?:[a-z]:[\\/]|/users/[^/]+/)")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
LAYOUT_SCHEMA = "ndc-skill-layout/v1"
REQUIRED_LAYOUT_DIRS = ("references", "assets", "scripts", "tests")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def provenance_only(line: str) -> bool:
    lower = line.lower()
    provenance = "provenance" in lower or "historical" in lower or "历史" in line
    non_executable = ("not executable" in lower or "不可复制" in line or
                      "不可执行" in line or "不是可执行" in line)
    return provenance and non_executable


def markdown_target(raw: str) -> str | None:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1:value.index(">")]
    elif " " in value:
        value = value.split(" ", 1)[0]
    value = unquote(value.split("#", 1)[0])
    if not value or value.startswith(("http://", "https://", "mailto:", "#", "{")):
        return None
    return value


def local_configuration(root: Path, errors: list[str]) -> dict:
    local_path = root / "ndc.local.json"
    if not local_path.is_file():
        return {"status": "unconfigured"}
    try:
        planning = json.loads(local_path.read_text(encoding="utf-8-sig"))
        if planning.get("schema") != "ndc-machine-paths/v1":
            raise ValueError("unsupported schema")
        configured_planning = Path(planning["planning_root"]).expanduser().resolve()
        if configured_planning != root.resolve():
            errors.append("ndc.local.json planning_root does not identify this checkout")
        engine = Path(planning["engine_root"]).expanduser().resolve()
        engine_local = engine / "ndc.local.json"
        if not engine_local.is_file():
            return {"status": "planning-only", "engine_root": str(engine)}
        peer = json.loads(engine_local.read_text(encoding="utf-8-sig"))
        for field in ("planning_root", "engine_root", "work_root"):
            if Path(peer[field]).expanduser().resolve() != Path(planning[field]).expanduser().resolve():
                errors.append(f"planning and engine ndc.local.json disagree on {field}")
        return {"status": "paired", "engine_root": str(engine),
                "engine_config": str(engine_local)}
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid local machine configuration: {exc}")
        return {"status": "invalid"}


def audit(root: Path) -> dict:
    registry_path = root / "production" / "art_pipeline" / "skill_sources.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    checked: list[dict] = []
    current_doc_paths: list[str] = []
    historical_paths: list[str] = []
    test_fixture_paths: list[str] = []
    support_file_paths: list[str] = []
    missing_links: list[str] = []
    verified_assets: list[str] = []
    names: set[str] = set()
    policy = registry.get("layout_policy", {})
    grandfathered = set(policy.get("grandfathered_skills", []))
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
        documents = [skill_root / "SKILL.md"]
        reference_root = skill_root / "references"
        if reference_root.is_dir():
            documents.extend(sorted(reference_root.rglob("*.md")))
        for path in documents:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            local = path.relative_to(skill_root).as_posix()
            for number, line in enumerate(text.splitlines(), start=1):
                if MACHINE_PATH.search(line):
                    finding = f"{name}:{local}:{number}"
                    if provenance_only(line):
                        historical_paths.append(finding)
                    else:
                        current_doc_paths.append(finding)
                        errors.append(f"{finding}: current documentation contains a machine-specific path")
            for match in MARKDOWN_LINK.finditer(text):
                target = markdown_target(match.group(1))
                if target is None:
                    continue
                resolved = (path.parent / Path(target)).resolve()
                try:
                    resolved.relative_to(root)
                except ValueError:
                    missing_links.append(f"{name}:{local}: link escapes registered repositories: {target}")
                    continue
                if not resolved.exists():
                    missing_links.append(f"{name}:{local}: missing link target: {target}")
        tests = skill_root / "tests"
        if tests.is_dir():
            for path in sorted(item for item in tests.rglob("*") if item.is_file()):
                if path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                text = path.read_text(encoding="utf-8-sig", errors="replace")
                for number, line in enumerate(text.splitlines(), start=1):
                    if MACHINE_PATH.search(line):
                        finding = f"{name}:{path.relative_to(skill_root).as_posix()}:{number}"
                        test_fixture_paths.append(finding)
                        errors.append(f"{finding}: test fixture contains a machine-specific path")
        for support_name in ("agents", "assets"):
            support_root = skill_root / support_name
            if not support_root.is_dir():
                continue
            for path in sorted(item for item in support_root.rglob("*") if item.is_file()):
                if path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                text = path.read_text(encoding="utf-8-sig", errors="replace")
                for number, line in enumerate(text.splitlines(), start=1):
                    if MACHINE_PATH.search(line):
                        finding = f"{name}:{path.relative_to(skill_root).as_posix()}:{number}"
                        support_file_paths.append(finding)
                        errors.append(f"{finding}: support file contains a machine-specific path")
        for manifest in sorted((skill_root / "assets").rglob("manifest.json")) if (skill_root / "assets").is_dir() else []:
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            if data.get("schema") != "ndc-skill-ui-reference-assets/v1":
                continue
            for asset in data.get("assets", []):
                target = (skill_root / asset.get("path", "")).resolve()
                try:
                    target.relative_to(skill_root)
                except ValueError:
                    errors.append(f"{name}: registered asset escapes Skill bundle: {asset.get('path')}")
                    continue
                if not target.is_file():
                    errors.append(f"{name}: missing registered asset: {asset.get('path')}")
                elif sha256(target).lower() != str(asset.get("sha256", "")).lower():
                    errors.append(f"{name}: registered asset hash mismatch: {asset.get('path')}")
                else:
                    verified_assets.append(f"{name}:{asset.get('path')}")
        if name not in grandfathered:
            if row.get("layout_schema") != LAYOUT_SCHEMA:
                errors.append(f"{name}: new Skill must declare layout_schema={LAYOUT_SCHEMA}")
            for directory in REQUIRED_LAYOUT_DIRS:
                folder = skill_root / directory
                if not folder.is_dir() or not any(item.is_file() for item in folder.rglob("*")):
                    errors.append(f"{name}: new Skill requires a non-empty {directory}/ directory")
        checked.append({"name": name, "path": relative, "script_files": len(scripts),
                        "document_files": len(documents)})
    errors.extend(missing_links)
    configuration = local_configuration(root, errors)
    return {"schema": "ndc-art-skill-bundle-audit/v2", "ok": not errors,
            "planning_skills": len(checked), "checked": checked,
            "current_document_machine_paths": current_doc_paths,
            "historical_provenance_paths": historical_paths,
            "test_fixture_machine_paths": test_fixture_paths,
            "support_file_machine_paths": support_file_paths,
            "missing_relative_links": missing_links,
            "verified_registered_assets": verified_assets,
            "configuration": configuration, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = audit(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
