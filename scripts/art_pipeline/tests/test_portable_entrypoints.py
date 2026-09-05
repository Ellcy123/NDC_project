"""Run the real entrypoints after relocating both checkouts independently."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from art_paths import load_art_paths


class PortableEntrypoints(unittest.TestCase):
    def setUp(self):
        try:
            configured = load_art_paths()
        except (OSError, ValueError) as exc:
            self.skipTest(f"Configure the two source checkouts before this integration suite: {exc}")
        self.temp = tempfile.TemporaryDirectory(prefix="ndc portable check ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.planning = self.root / "authors and designers" / "任意策划 checkout"
        self.engine = self.root / "separate location" / "games" / "另一个工程 checkout"
        self.work = self.root / "项目外 scratch"
        self.caller = self.root / "operator current directory"
        self.caller.mkdir()
        self.environment = {key: value for key, value in os.environ.items()
                            if key not in {"NDC_PLANNING_ROOT", "NDC_ENGINE_ROOT",
                                           "NDC_ART_WORK_ROOT", "NDC_ART_PATHS_CONFIG",
                                           "PYTHONUTF8", "PYTHONIOENCODING"}}
        for root in (self.planning, self.engine):
            (root / "scripts/art_pipeline").mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        for filename in ("ndc_art.py", "art_paths.py", "art_workspace.py",
                         "validate_stage_visual_self_check.py", "validate_texture_gate.py",
                         "validate_final_visual_record_presence.py"):
            shutil.copy2(SOURCE / filename, self.planning / "scripts/art_pipeline" / filename)
        shutil.copy2(configured.engine_root / "scripts/art_pipeline/ndc_art.py",
                     self.engine / "scripts/art_pipeline/ndc_art.py")
        for source, target in ((configured.planning_root, self.planning),
                               (configured.engine_root, self.engine)):
            for filename in (".gitignore", "ndc.local.example.json"):
                shutil.copy2(source / filename, target / filename)
        rules = self.planning / "production/art_pipeline"
        rules.mkdir(parents=True)
        self.write(rules / "paths.json", {
            "schema": "ndc-art-workspace/v2", "character_registry": "refs/cards.json",
            "quota_gib": 1, "minimum_free_gib": 0,
        })
        registry = {"schema": "ndc-art-skill-sources/v2", "skills": []}
        for name, owner, filename in (("engine-probe", "engine", "probe.py"),
                                      ("planning-probe", "planning", "probe.py"),
                                      ("ndc-scene-evidence-placement", "planning", "evidence_delivery.py")):
            checkout = self.planning if owner == "planning" else self.engine
            skill = checkout / ".codex/skills" / name
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: " + name + "\ndescription: Integration fixture\n---\n", encoding="utf-8")
            (skill / "scripts" / filename).write_text(
                "import json, os, sys\nfrom pathlib import Path\n"
                "print(json.dumps({'cwd':str(Path.cwd()),'args':sys.argv[1:],"
                "'planning':os.environ['NDC_PLANNING_ROOT'],"
                "'engine':os.environ['NDC_ENGINE_ROOT'],"
                "'work':os.environ['NDC_ART_WORK_ROOT']}))\n", encoding="utf-8")
            registry["skills"].append({"name": name, "owner_scope": owner,
                                       "path": ".codex/skills/" + name, "status": "centralized"})
        self.write(rules / "skill_sources.json", registry)

    @staticmethod
    def write(path, data):
        path.write_text(json.dumps(data), encoding="utf-8")

    def call(self, owner, *arguments, expected=0, environment=None):
        root = self.planning if owner == "planning" else self.engine
        result = subprocess.run([sys.executable, "-B",
                                 str(root / "scripts/art_pipeline/ndc_art.py"), *map(str, arguments)],
                                cwd=self.caller, env=environment or self.environment,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def configure(self):
        return self.call("engine", "configure", "--planning-root", self.planning,
                         "--engine-root", self.engine, "--work-root", self.work)

    def test_real_configuration_resolution_and_child_execution_after_relocation(self):
        self.configure()
        for owner in ("planning", "engine"):
            paths = json.loads(self.call(owner, "paths").stdout)
            self.assertEqual(Path(paths["planning_root"]), self.planning)
            self.assertEqual(Path(paths["engine_root"]), self.engine)
            self.assertEqual(Path(paths["work_root"]), self.work)
            selected = json.loads(self.call(owner, "skill", "engine-probe").stdout)
            self.assertEqual(selected["owner"], "engine")
            self.assertEqual(Path(selected["path"]), self.engine / ".codex/skills/engine-probe/SKILL.md")
            child = json.loads(self.call(owner, "run", "planning-probe", "probe.py", "space and $ literal").stdout)
            self.assertEqual(Path(child["cwd"]), self.caller)
            self.assertEqual(child["args"], ["space and $ literal"])
            self.assertEqual(Path(child["engine"]), self.engine)
            self.assertEqual(Path(child["planning"]), self.planning)
            self.assertEqual(Path(child["work"]), self.work)

    def test_missing_configuration_reports_actionable_error_without_guessing(self):
        for owner in ("planning", "engine"):
            result = self.call(owner, "paths", expected=1)
            self.assertIn("configure", result.stderr)
            self.assertIn("Missing", result.stderr)
            self.call(owner, "--help")
            for option in ("--help", "-h"):
                help_text = self.call(owner, "configure", option).stdout
                for root in ("planning", "engine", "work"):
                    self.assertIn(f"--{root}-root", help_text)
            self.assertFalse((self.planning / "ndc.local.json").exists())
            self.assertFalse((self.engine / "ndc.local.json").exists())

    def test_environment_overrides_machine_configuration(self):
        self.configure()
        environment = dict(self.environment, NDC_ENGINE_ROOT=str(self.root / "override engine"),
                           NDC_ART_WORK_ROOT=str(self.root / "override scratch"))
        paths = json.loads(self.call("planning", "paths", environment=environment).stdout)
        self.assertEqual(paths["engine_root"], environment["NDC_ENGINE_ROOT"])
        self.assertEqual(paths["work_root"], environment["NDC_ART_WORK_ROOT"])

    def test_machine_files_are_ignored_while_scripts_and_examples_are_visible_to_git(self):
        self.configure()
        for root in (self.planning, self.engine):
            for relative, ignored in (("ndc.local.json", True), (".venv/example.py", True),
                                      ("ndc.local.example.json", False),
                                      ("scripts/art_pipeline/ndc_art.py", False)):
                result = subprocess.run(["git", "-C", str(root), "check-ignore", "--no-index", "--quiet", "--", relative])
                self.assertEqual(result.returncode, 0 if ignored else 1, relative)
        result = subprocess.run(["git", "-C", str(self.engine), "check-ignore", "--no-index", "--quiet", "--",
                                 ".codex/skills/engine-probe/scripts/probe.py"])
        self.assertEqual(result.returncode, 1)

    def test_dispatch_rejects_escape_and_protects_legacy_packager_output(self):
        self.configure()
        for script in ("../SKILL.md", "../../../outside.py", str(self.root / "outside.py")):
            self.call("planning", "run", "engine-probe", script, expected=1)
        created = json.loads(self.call("engine", "workspace", "create", "--name", "portable-check", "--kind", "check").stdout)
        output = Path(created["output"])
        self.assertEqual(output.parent.parent, self.work / "jobs")
        for rejected in (self.engine / "Assets", self.planning / "outputs",
                         self.work / "jobs/unregistered/payload"):
            self.call("engine", "run", "ndc-scene-evidence-placement", "evidence_delivery.py",
                      "package", "--output-dir", rejected, expected=1)
        accepted = json.loads(self.call("engine", "run", "ndc-scene-evidence-placement", "evidence_delivery.py",
                                       "package", "--output-dir", output / "packaged").stdout)
        self.assertEqual(accepted["args"][-1], str(output / "packaged"))
        forbidden = self.engine / "Assets"
        for arguments in (("--output-dir", output, "--output-dir", forbidden),
                          (f"--output-dir={output}", f"--output-dir={forbidden}"),
                          ("--output-dir", output, "--output-d", forbidden),
                          (f"--output-dir={output}", f"--output-d={forbidden}"),
                          ("--output-d", output)):
            self.call("engine", "run", "ndc-scene-evidence-placement", "evidence_delivery.py",
                      "package", *arguments, expected=1)
        for arguments in ((f"--output-dir={output}",),
                          ("--output-dir", forbidden, "--output-dir", output)):
            self.call("engine", "run", "ndc-scene-evidence-placement", "evidence_delivery.py",
                      "package", *arguments)
        self.assertFalse(forbidden.exists())
        self.call("engine", "workspace", "ready", "--job", created["job"])
        self.assertEqual(json.loads((output.parent / "job.json").read_text())["state"], "waiting-for-user")
        self.call("engine", "tool", "stage", "--help")


if __name__ == "__main__":
    unittest.main()
