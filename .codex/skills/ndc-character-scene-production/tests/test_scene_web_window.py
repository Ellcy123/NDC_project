import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from manage_scene_web_window import (  # noqa: E402
    bind_packet,
    cancel_prepared,
    close_window,
    confirm_uploads,
    create_window,
    mark_submitted,
    record_browser_health,
    record_canary,
    register_unit,
    resolve_attempt,
    resume_entry,
    supersede_workspace,
    validate_state,
)

AT = "2026-09-11T23:00:00+08:00"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SceneWebWindowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ndc-scene-window-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        created = create_window(
            self.root / "window", "SC-test", 3, "chrome", "scene-SC-test-r3",
            "🎬 SC-test r3", AT, "profile-a",
        )
        self.state = Path(created["state"])
        self.identity = Path(created["identity"])
        self.refs = []
        for index in range(3):
            path = self.root / f"ref-{index}.png"
            path.write_bytes(b"ref" + bytes([index]))
            self.refs.append(path)
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("full prompt")
        record_browser_health(self.state, "healthy", AT, "tabs and session are reachable")
        record_canary(self.state, "pass", AT, "one DOM and attachment-entry canary passed")

    def register(self, unit_id: str, actor_id: str, pose_id: str, suffix: str, supersedes=None):
        return register_unit(
            self.state, unit_id, actor_id, [pose_id],
            f"https://chatgpt.com/c/{suffix}", AT, supersedes,
        )

    def packet(self, unit_id: str, actor_id: str, pose_id: str, suffix: str, *, scene_id="SC-test", attempt=1) -> Path:
        path = self.root / f"{unit_id}-attempt-{attempt}-manifest.json"
        value = {
            "schema": "ndc-chatgpt-web-submission-packet/v3",
            "scene_id": scene_id,
            "revision": 3,
            "browser": "chrome",
            "generation_unit_id": unit_id,
            "actor_id": actor_id,
            "pose_ids": [pose_id],
            "conversation_url": f"https://chatgpt.com/c/{suffix}",
            "scene_window": {"path": str(self.identity), "sha256": digest(self.identity)},
            "uploaded_inputs": [
                {"role": role, "path": str(self.refs[index]), "sha256": digest(self.refs[index])}
                for index, role in enumerate(("local-whitebox-crop", "untouched-full-scene", "approved-character-card"))
            ],
            "prompt": {"path": str(self.prompt), "sha256": digest(self.prompt)},
        }
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def prepare_and_submit(self, unit_id: str, actor_id: str, pose_id: str, suffix: str):
        self.register(unit_id, actor_id, pose_id, suffix)
        bind_packet(self.state, unit_id, self.packet(unit_id, actor_id, pose_id, suffix), AT)
        confirm_uploads(self.state, unit_id, AT, "three independent thumbnails and full prompt verified")
        return mark_submitted(self.state, unit_id, f"submission-{unit_id}", AT)

    def test_two_actor_conversations_may_be_pending_in_one_scene_window(self):
        self.prepare_and_submit("mickey-intro", "Mickey", "intro", "mickey")
        result = self.prepare_and_submit("emma-observe", "Emma", "observe", "emma")
        self.assertEqual(result["parallel_unresolved_count"], 2)
        self.assertEqual(set(result["unresolved_units"]), {"mickey-intro", "emma-observe"})
        self.assertTrue(result["parallel_unresolved_allowed"])

    def test_same_actor_different_poses_may_be_pending_concurrently(self):
        self.prepare_and_submit("mickey-intro", "Mickey", "intro", "mickey-intro")
        result = self.prepare_and_submit("mickey-point", "Mickey", "point", "mickey-point")
        self.assertEqual(result["parallel_unresolved_count"], 2)

    def test_same_conversation_rejects_duplicate_while_unresolved_then_allows_next_attempt(self):
        self.prepare_and_submit("mickey-intro", "Mickey", "intro", "mickey")
        with self.assertRaisesRegex(ValueError, "unresolved"):
            bind_packet(
                self.state, "mickey-intro",
                self.packet("mickey-intro", "Mickey", "intro", "mickey", attempt=2), AT,
            )
        resolve_attempt(self.state, "mickey-intro", "failed", AT, "reviewable failure")
        result = bind_packet(
            self.state, "mickey-intro",
            self.packet("mickey-intro", "Mickey", "intro", "mickey", attempt=2), AT,
        )
        self.assertEqual(result["parallel_unresolved_count"], 1)

    def test_same_actor_pose_cannot_be_claimed_by_another_conversation(self):
        self.register("mickey-a", "Mickey", "intro", "mickey-a")
        with self.assertRaisesRegex(ValueError, "already belongs"):
            self.register("mickey-b", "Mickey", "intro", "mickey-b")
        self.assertEqual(validate_state(self.state)["report"]["conversation_units"], 1)

    def test_packet_from_another_scene_cannot_bind(self):
        self.register("mickey", "Mickey", "intro", "mickey")
        with self.assertRaisesRegex(ValueError, "scene_id"):
            bind_packet(self.state, "mickey", self.packet("mickey", "Mickey", "intro", "mickey", scene_id="SC-other"), AT)

    def test_account_unavailable_allows_explicit_replacement_conversation_only(self):
        self.prepare_and_submit("mickey-old", "Mickey", "intro", "mickey-old")
        resolve_attempt(self.state, "mickey-old", "account_record_unavailable", AT, "old account cannot access the conversation")
        result = self.register("mickey-new", "Mickey", "intro", "mickey-new", supersedes="mickey-old")
        self.assertEqual(result["conversation_units"], 2)
        with self.assertRaisesRegex(ValueError, "branch or bypass"):
            self.register("mickey-third", "Mickey", "intro", "mickey-third", supersedes="mickey-old")
        bind_packet(self.state, "mickey-new", self.packet("mickey-new", "Mickey", "intro", "mickey-new"), AT)
        confirm_uploads(self.state, "mickey-new", AT, "three independent thumbnails and full prompt verified")
        mark_submitted(self.state, "mickey-new", "submission-mickey-new", AT)
        resolve_attempt(self.state, "mickey-new", "account_record_unavailable", AT, "second account also lost access")
        result = self.register("mickey-third", "Mickey", "intro", "mickey-third", supersedes="mickey-new")
        self.assertEqual(result["conversation_units"], 3)

    def test_cancelled_prepared_packet_frees_conversation_without_fake_submission(self):
        self.register("mickey", "Mickey", "intro", "mickey")
        bind_packet(self.state, "mickey", self.packet("mickey", "Mickey", "intro", "mickey"), AT)
        result = cancel_prepared(self.state, "mickey", AT, "browser failed before submit")
        self.assertEqual(result["parallel_unresolved_count"], 0)
        bind_packet(self.state, "mickey", self.packet("mickey", "Mickey", "intro", "mickey", attempt=2), AT)

    def test_window_closes_only_after_every_conversation_is_resolved(self):
        self.prepare_and_submit("mickey", "Mickey", "intro", "mickey")
        with self.assertRaisesRegex(ValueError, "unresolved"):
            close_window(self.state, AT)
        resolve_attempt(self.state, "mickey", "produced", AT, "original download frozen")
        result = close_window(self.state, AT)
        self.assertEqual(result["parallel_unresolved_count"], 0)
        self.assertEqual(result["window_status"], "CLOSED")
        self.assertEqual(validate_state(self.state)["state"]["status"], "CLOSED")

    def test_only_concrete_chatgpt_conversation_urls_register(self):
        with self.assertRaisesRegex(ValueError, "/c/<conversation-id>"):
            register_unit(self.state, "mickey", "Mickey", ["intro"], "https://chatgpt.com/g/gpt", AT)
        with self.assertRaisesRegex(ValueError, "https://chatgpt.com"):
            register_unit(self.state, "mickey", "Mickey", ["intro"], "https://user@chatgpt.com/c/id", AT)

    def test_workspace_needs_health_and_one_canary_before_packet_binding(self):
        created = create_window(self.root / "draft", "SC-draft", 1, "iab", "draft", "draft", AT)
        state = Path(created["state"])
        identity = Path(created["identity"])
        register_unit(state, "unit", "Actor", ["pose"], "https://chatgpt.com/c/draft", AT)
        packet = self.packet("unit", "Actor", "pose", "draft", scene_id="SC-draft")
        value = json.loads(packet.read_text())
        value["revision"] = 1
        value["browser"] = "iab"
        value["scene_window"] = {"path": str(identity), "sha256": digest(identity)}
        packet.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "READY"):
            bind_packet(state, "unit", packet, AT)
        record_browser_health(state, "healthy", AT, "browser responds")
        self.assertFalse(validate_state(state)["report"]["ready"])
        record_canary(state, "pass", AT, "real canary passed")
        self.assertTrue(validate_state(state)["report"]["ready"])

    def test_submission_requires_atomic_three_upload_confirmation(self):
        self.register("mickey", "Mickey", "intro", "mickey")
        bind_packet(self.state, "mickey", self.packet("mickey", "Mickey", "intro", "mickey"), AT)
        with self.assertRaisesRegex(ValueError, "three independently confirmed"):
            mark_submitted(self.state, "mickey", "submission", AT)
        confirm_uploads(self.state, "mickey", AT, "three thumbnails visible in order")
        self.assertEqual(mark_submitted(self.state, "mickey", "submission", AT)["parallel_unresolved_count"], 1)

    def test_wip_limit_blocks_fourth_open_packet(self):
        for index in range(3):
            self.register(f"u{index}", f"A{index}", f"p{index}", f"u{index}")
            bind_packet(self.state, f"u{index}", self.packet(f"u{index}", f"A{index}", f"p{index}", f"u{index}"), AT)
        self.register("u3", "A3", "p3", "u3")
        with self.assertRaisesRegex(ValueError, "WIP limit"):
            bind_packet(self.state, "u3", self.packet("u3", "A3", "p3", "u3"), AT)

    def test_new_revision_supersedes_prepared_work_and_fences_submission(self):
        self.register("mickey", "Mickey", "intro", "mickey")
        bind_packet(self.state, "mickey", self.packet("mickey", "Mickey", "intro", "mickey"), AT)
        report = supersede_workspace(self.state, 4, AT, "reference revision 4 published")
        self.assertEqual(report["workspace_status"], "SUPERSEDED")
        attempt = validate_state(self.state)["state"]["units"][0]["attempts"][-1]
        self.assertEqual(attempt["status"], "CANCELLED_BEFORE_SUBMISSION")
        with self.assertRaisesRegex(ValueError, "READY"):
            bind_packet(self.state, "mickey", self.packet("mickey", "Mickey", "intro", "mickey", attempt=2), AT)
        self.assertEqual(resume_entry(self.state)["next_action"], "use replacement revision only")


if __name__ == "__main__":
    unittest.main()
