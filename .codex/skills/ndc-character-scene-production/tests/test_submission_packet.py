import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from build_chatgpt_web_submission_packet import build  # noqa: E402
from manage_scene_web_window import (  # noqa: E402
    create_window, record_browser_health, record_canary, register_unit, validate_state,
)
from validate_prompt_style_binding import (  # noqa: E402
    CANONICAL_STYLE_ASSET,
    CANONICAL_STYLE_SHA256,
    validate_contract,
)
SHARED_PIPELINE = SKILL_ROOT.parent / "ndc-art-stage-pipeline" / "scripts"
sys.path.insert(0, str(SHARED_PIPELINE))
import manual_review_node as manual_node  # noqa: E402
from manual_review_node import approval_for  # noqa: E402
PIPELINE_TESTS = SKILL_ROOT.parent / "ndc-art-stage-pipeline" / "tests"
sys.path.insert(0, str(PIPELINE_TESTS))
from character_node_fixture import attach_character_node_delivery  # noqa: E402

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")
AT = "2026-09-11T23:00:00+08:00"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SubmissionPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.style_lock = self.root / "style-lock.txt"
        shutil.copy2(CANONICAL_STYLE_ASSET, self.style_lock)
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_bytes(b"complete actor with approved pose\n" + self.style_lock.read_bytes())
        self.profile = self.root / "importance.json"
        self.profile.write_text("{}")
        binding_contract = self.root / "binding-source.json"
        binding_contract.write_text(json.dumps({
            "schema": "ndc-prompt-style-binding/v2",
            "style_lock_path": str(self.style_lock),
            "fixed_style_sha256": CANONICAL_STYLE_SHA256,
            "rendered_prompt_path": str(self.prompt),
            "reference_roles": ["local-whitebox-crop", "untouched-full-scene", "approved-character-card"],
            "dynamic_fields": {"character": "actor-a"},
        }))
        self.binding = self.root / "binding.json"
        self.binding.write_text(json.dumps(validate_contract(binding_contract)))
        self.importance = self.root / "importance-gate.json"
        self.importance.write_text(json.dumps({"status": "PASS", "profile_sha256": digest(self.profile)}))
        inputs = []
        for number, role in enumerate(("local-whitebox-crop", "untouched-full-scene", "approved-character-card"), 1):
            path = self.root / f"input-{number}.png"
            path.write_bytes(PNG)
            inputs.append({"role": role, "path": str(path.resolve()), "sha256": digest(path)})
        window = create_window(self.root / "window", "scene-s", 1, "iab", "scene-s-r1", "🎬 scene-s r1", AT)
        self.state = Path(window["state"])
        record_browser_health(self.state, "healthy", AT, "browser responds")
        record_canary(self.state, "pass", AT, "one real canary passed")
        register_unit(self.state, "actor-a-pose", "actor-a", ["pose-a"], "https://chatgpt.com/c/scene-s-r1-actor-a", AT)
        self.asset_index = self.root / "asset-index.json"; self.asset_index.write_text("{}")
        self.node_scope = self.root / "node-scope.json"
        self.node_scope.write_text(json.dumps({"scope": {"cases": [{"snapshots": [{"actor_pose_ids": {"actor-a": "pose-a"}}]}]}}))
        self.node_workspace = self.root / "node-workspace.json"; self.node_workspace.write_text("{}")
        node_files = {}
        for name in ("node-handoff.md", "node-names.json", "node-web-prompt.md", "node-discovery.json"):
            path = self.root / name; path.write_bytes(name.encode()); node_files[name] = path
        for name, rgba in (("node-master.png", True), ("node-whitebox.png", False), ("node-joint.png", False), ("node-ui.png", False)):
            path = self.root / name
            mode = "RGBA" if rgba else "RGB"
            image = Image.new(mode, (256, 256), (0, 0, 0, 0) if rgba else (20, 30, 40))
            draw = ImageDraw.Draw(image)
            variant = sum(name.encode("utf-8")) % 24
            for offset in range(96):
                color = (40 + offset * 2, 70 + offset, 126 + variant - offset, 255) if rgba else (40 + offset * 2, 70 + offset, 126 + variant - offset)
                draw.line((80 + offset, 20, 80 + offset, 235), fill=color)
            image.save(path)
            node_files[name] = path
        def node_ref(path):
            return {"path": str(path.resolve()), "sha256": digest(path)}
        self.node_path = self.root / "manual-node.json"
        anatomy = {part: True for part in manual_node.ANATOMY_PARTS}
        absent = {part: True for part in manual_node.PROXY_ABSENCE_KEYS}
        node = {
            "schema": "ndc-manual-review-node/v1", "status": "NODE_DELIVERABLE_READY", "node_id": "scene-s-r1-node",
            "unit": "Unit1", "domain": "character_scene", "scene_id": "scene-s", "revision": 1, "created_at": AT,
            "scope": node_ref(self.node_scope), "source_index": node_ref(self.asset_index), "handoff_document": node_ref(node_files["node-handoff.md"]),
            "naming_table": node_ref(node_files["node-names.json"]), "web_prompt": node_ref(node_files["node-web-prompt.md"]),
            "deliverables": {
                "production_whiteboxes": [{
                    "actor_id": "actor-a", "pose_id": "pose-a", "anatomy_mode": "FULL_IN_FRAME",
                    "whitebox_kind": "3d-anatomical-mannequin-exact-pose",
                    "complete_anatomy_master": node_ref(node_files["node-master.png"]),
                    "final_submission_whitebox": node_ref(node_files["node-whitebox.png"]),
                    "final_submission_authority": True, "anatomy_coverage": anatomy,
                    "prohibited_proxy_types_absent": absent,
                    "technical_review": node_ref(node_files["node-discovery.json"]),
                    "visual_review": node_ref(node_files["node-discovery.json"]),
                    "discovery_receipt": node_ref(node_files["node-discovery.json"]),
                }],
                "joint_whitebox_preview": node_ref(node_files["node-joint.png"]),
                "actual_ui_clearance_preview": node_ref(node_files["node-ui.png"]),
                "discovery_receipts": [node_ref(node_files["node-discovery.json"])],
            },
            "user_review_focus": ["proportion", "narrative_pose", "landing_plausibility", "ui_clearance"], "manual_return_workspace": node_ref(self.node_workspace),
        }
        attach_character_node_delivery(node, self.node_path, manual_node)
        self.node_path.write_text(json.dumps(node))
        self.approval_path = self.root / "manual-approval.json"
        self.approval_path.write_text(json.dumps(approval_for(self.node_path, AT, "用户明确通过节点")))
        self.revision_gate = self.root / "revision-gate.json"
        self.revision_gate.write_text(json.dumps({
            "schema": "ndc-character-scene-ready-revision-gate/v1",
            "status": "CURRENT", "unit_id": "scene-s", "revision": 1, "checked_at": AT, "scope_sha256": "a" * 64,
            "manual_review_node": node_ref(self.node_path), "manual_review_approval": node_ref(self.approval_path),
        }))
        self.discovery = self.root / "discovery.json"
        self.discovery.write_text(json.dumps({
            "schema": "ndc-asset-discovery-receipt/v1", "status": "CONFIRMED_ABSENT", "checked_at": AT,
            "scope": {"domain": "character_scene", "scene_id": "scene-s", "revision": 1, "actor_id": "actor-a", "pose_or_state": "pose-a", "artifact_role": "formal_rgba"},
            "freshness": {"scope_revision_sha256": "a" * 64, "asset_index": {"path": str(self.asset_index), "sha256": digest(self.asset_index)}},
            "searches": [{"root_role": role, "root_path": str(self.root), "query_ids": ["actor-a"], "aliases": ["actor-a"], "completed": True} for role in ("official_runtime", "approved_archive", "formal_delivery")],
            "candidates": [],
        }))
        self.contract = {
            "schema": "ndc-chatgpt-web-submission-source/v3",
            "scene_window_state_path": str(self.state),
            "scene_id": "scene-s",
            "revision": 1,
            "generation_unit_id": "actor-a-pose",
            "actor_id": "actor-a",
            "pose_ids": ["pose-a"],
            "prepared_at": AT,
            "revision_gate": {"path": str(self.revision_gate.resolve()), "sha256": digest(self.revision_gate)},
            "retry_control": {"attempt_number": 1, "defect_tier": "INITIAL", "consecutive_same_defect_count": 0, "method_changed": False},
            "uploaded_inputs": inputs,
            "prompt": {"path": str(self.prompt.resolve()), "sha256": digest(self.prompt)},
            "prompt_binding_gate": {"path": str(self.binding.resolve()), "sha256": digest(self.binding)},
            "importance_profile": {"path": str(self.profile.resolve()), "sha256": digest(self.profile)},
            "importance_gate": {"path": str(self.importance.resolve()), "sha256": digest(self.importance)},
            "artifact_role": "formal_rgba",
            "discovery": {"receipt": {"path": str(self.discovery.resolve()), "sha256": digest(self.discovery)}, "scope_revision_sha256": "a" * 64},
        }
        self.contract_path = self.root / "contract.json"
        self.contract_path.write_text(json.dumps(self.contract))

    def test_builds_scene_window_bound_packet_and_prepares_unit(self):
        result = build(self.contract_path, self.root / "packet")
        manifest = json.loads(Path(result["manifest"]).read_text())
        self.assertEqual(manifest["schema"], "ndc-chatgpt-web-submission-packet/v3")
        self.assertEqual(manifest["submission_order"], ["local-whitebox-crop", "untouched-full-scene", "approved-character-card", "full-prompt"])
        self.assertEqual(manifest["generation_unit_id"], "actor-a-pose")
        self.assertEqual(manifest["actor_id"], "actor-a")
        self.assertEqual(manifest["style_lock"]["sha256"], CANONICAL_STYLE_SHA256)
        self.assertEqual(len(manifest["uploaded_inputs"]), 3)
        self.assertEqual(manifest["revision_gate"]["sha256"], digest(Path(manifest["revision_gate"]["path"])))
        self.assertTrue(Path(result["receipt_draft"]).is_file())
        state = validate_state(self.state)["state"]
        self.assertEqual(state["units"][0]["attempts"][-1]["status"], "PREPARED")

    def test_parallel_manual_return_branch_does_not_require_approval(self):
        gate = json.loads(self.revision_gate.read_text())
        gate.pop("manual_review_approval")
        gate["manual_review_branch"] = {
            "mode": "PARALLEL_NONBLOCKING",
            "blocks_mainline": False,
            "approval": None,
        }
        self.revision_gate.write_text(json.dumps(gate))
        self.contract["revision_gate"] = {
            "path": str(self.revision_gate.resolve()),
            "sha256": digest(self.revision_gate),
        }
        self.contract_path.write_text(json.dumps(self.contract))
        result = build(self.contract_path, self.root / "packet-parallel")
        self.assertTrue(Path(result["manifest"]).is_file())

    def test_stale_prompt_gate_fails(self):
        self.prompt.write_text("changed")
        with self.assertRaisesRegex(ValueError, "hash"):
            build(self.contract_path, self.root / "packet")

    def test_unregistered_actor_or_wrong_browser_fails(self):
        self.contract["generation_unit_id"] = "missing"
        self.contract_path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(ValueError, "not registered"):
            build(self.contract_path, self.root / "packet")
        self.contract["generation_unit_id"] = "actor-a-pose"
        self.contract_path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(ValueError, "dedicated scene window"):
            build(self.contract_path, self.root / "packet2", browser="edge")

    def test_uploaded_reference_must_be_an_actual_image(self):
        fake = Path(self.contract["uploaded_inputs"][0]["path"])
        fake.write_text("not an image", encoding="utf-8")
        self.contract["uploaded_inputs"][0]["sha256"] = digest(fake)
        self.contract_path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(ValueError, "PNG, JPEG or WebP"):
            build(self.contract_path, self.root / "packet")

    def test_attempts_four_to_six_are_reserved_for_h0(self):
        self.contract["retry_control"].update(attempt_number=4, defect_tier="H2")
        self.contract_path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(ValueError, "reserved for H0"):
            build(self.contract_path, self.root / "packet")

    def test_repeated_same_defect_requires_method_change(self):
        self.contract["retry_control"].update(
            attempt_number=3, defect_tier="H0", defect_id="wrong-face",
            consecutive_same_defect_count=2, method_changed=False,
        )
        self.contract_path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(ValueError, "change method"):
            build(self.contract_path, self.root / "packet")


if __name__ == "__main__":
    unittest.main()
