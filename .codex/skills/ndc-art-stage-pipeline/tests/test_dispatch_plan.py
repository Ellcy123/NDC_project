"""Pure app-protocol fixtures: these tests never create or message a Codex task."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from dispatch_plan import DispatchPlanError, build_dispatch_plan, command


class DispatchPlanTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).parent / ".test-data"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="dispatch-", dir=scratch)
        self.root = Path(self.temp.name).resolve()
        self.reservation = {
            "dispatch_id": "dispatch-fixture-01",
            "pipeline_id": "pipeline-fixture",
            "action": "create",
            "status": "RESERVED",
            "target_thread_id": None,
            "packet_path": str(self.root / "immutable-package.json"),
            "packet_sha256": "a" * 64,
            "unit_id": "scene-with-all-views",
            "revision": 1,
            "execution_mode": "validation",
            "database_path": str(self.root / "pipeline.sqlite"),
            "downstream_skill": "ndc-midjourney-operator",
            "work_directory": str(self.root / "worker-output"),
        }
        self.context = {
            "controller_task_id": "controller-fixture",
            "project": {"projectId": "project-fixture", "isGitRepository": False},
            "explicit_new_task_authorized": True,
            "authorization_note": "Synthetic protocol authorization field; the test performs no app call.",
            "art_execution_authorized": False,
        }

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, reservation=None, context=None):
        return build_dispatch_plan(reservation or self.reservation, context or self.context)

    def test_validation_create_parameters_follow_the_real_tool_schema(self):
        plan = self.plan()
        self.assertEqual(plan["tool_call"]["name"], "mcp__codex_app__create_thread")
        args = plan["tool_call"]["arguments"]
        self.assertEqual(args["target"], {"type": "project", "projectId": "project-fixture", "environment": {"type": "local"}})
        self.assertNotIn("model", args)
        self.assertNotIn("thinking", args)
        self.assertEqual(plan["limits"], {"max_active": 2, "upstream": 1, "downstream": 1, "all_views_one_worker": True})
        self.assertFalse(plan["effect_scope"]["real_art_generation"])
        self.assertFalse(plan["effect_scope"]["photoshop"])
        self.assertIn("不调用 Midjourney", args["prompt"])

    def test_create_has_atomic_sent_step_before_the_tool_and_real_response_binding_after_it(self):
        plan = self.plan()
        before = plan["before_tool_call"]["argv"]
        self.assertIn("dispatch-sent", before)
        self.assertEqual(before[-4:], ["--task", "controller-fixture", "--dispatch", "dispatch-fixture-01"])
        after = plan["after_actual_response"]["argv"]
        self.assertIn("bind-dispatch", after)
        self.assertEqual(after[-2:], ["--response", plan["app_response_path"]])
        self.assertIn("dispatch-unknown", plan["on_unknown_result"]["argv"])
        self.assertIn("--reason", plan["on_unknown_result"]["argv"])
        self.assertNotIn("reserve-dispatch", " ".join(before))

    def test_create_and_reuse_bootstrap_real_goal_without_unsupported_tool_fields(self):
        for action in ("create", "send"):
            reservation = copy.deepcopy(self.reservation)
            reservation.update(action=action, target_thread_id="existing-worker" if action == "send" else None)
            args = self.plan(reservation)["tool_call"]["arguments"]
            for instruction in ("get_goal", "create_goal", "不设置 token_budget", "不同目标", "一次性回传"):
                self.assertIn(instruction, args["prompt"])
            self.assertNotIn("goal", args)
            self.assertNotIn("mode", args)

    def test_existing_worker_uses_send_without_creating_one_worker_per_view(self):
        reservation = copy.deepcopy(self.reservation)
        reservation.update(action="send", target_thread_id="actual-worker-fixture")
        plan = self.plan(reservation)
        self.assertEqual(plan["tool_call"]["name"], "mcp__codex_app__send_message_to_thread")
        self.assertEqual(plan["tool_call"]["arguments"]["threadId"], "actual-worker-fixture")
        self.assertNotIn("target", plan["tool_call"]["arguments"])
        self.assertIn("全部 views", plan["tool_call"]["arguments"]["prompt"])

    def test_git_project_defaults_to_worktree_and_local_requires_recorded_explicit_request(self):
        context = copy.deepcopy(self.context)
        context["project"]["isGitRepository"] = True
        self.assertEqual(self.plan(context=context)["tool_call"]["arguments"]["target"]["environment"], {"type": "worktree"})
        context["use_saved_project_directly"] = True
        with self.assertRaises(DispatchPlanError):
            self.plan(context=context)
        context["saved_project_request_note"] = "The user explicitly requested using this saved project directly."
        self.assertEqual(self.plan(context=context)["tool_call"]["arguments"]["target"]["environment"], {"type": "local"})

    def test_maintenance_authorization_does_not_implicitly_create_user_tasks(self):
        context = copy.deepcopy(self.context)
        context["explicit_new_task_authorized"] = False
        plan = self.plan(context=context)
        self.assertEqual(plan["status"], "AUTHORIZATION_REQUIRED")
        self.assertIsNone(plan["tool_call"])
        self.assertIsNotNone(plan["proposed_tool_call"])
        self.assertNotIn("before_tool_call", plan)

    def test_production_needs_both_task_and_art_authority(self):
        reservation = copy.deepcopy(self.reservation)
        reservation["execution_mode"] = "production"
        self.assertEqual(self.plan(reservation)["status"], "AUTHORIZATION_REQUIRED")
        context = copy.deepcopy(self.context)
        context["art_execution_authorized"] = True
        approved = self.plan(reservation, context)
        self.assertTrue(approved["execute_allowed"])
        self.assertTrue(approved["effect_scope"]["real_art_generation"])
        context["explicit_new_task_authorized"] = False
        self.assertFalse(self.plan(reservation, context)["execute_allowed"])

    def test_ui_production_stays_with_approved_master_cropping(self):
        reservation = copy.deepcopy(self.reservation)
        reservation.update(execution_mode="production", downstream_skill="ndc-generate-ui-portraits")
        context = copy.deepcopy(self.context)
        context["art_execution_authorized"] = True
        plan = self.plan(reservation, context)
        self.assertTrue(plan["effect_scope"]["ui_approved_master_crop"])
        self.assertFalse(plan["effect_scope"]["real_art_generation"])
        self.assertFalse(plan["effect_scope"]["automatic_shoulder_completion"])

    def test_unknown_submitting_and_setup_pending_never_generate_a_second_send(self):
        for status in ("UNKNOWN", "SUBMITTING", "SETUP_PENDING", "BOUND"):
            with self.subTest(status=status):
                reservation = copy.deepcopy(self.reservation)
                reservation.update(status=status, clientThreadId="temporary-client-id")
                plan = self.plan(reservation)
                self.assertEqual(plan["status"], "RECONCILE_ONLY")
                self.assertIsNone(plan["tool_call"])
                self.assertIsNone(plan["proposed_tool_call"])
                self.assertNotIn("before_tool_call", plan)
                self.assertEqual(plan["inspection_tool_call"]["name"], "mcp__codex_app__list_threads")

    def test_unknown_send_can_inspect_its_real_target_without_resending(self):
        reservation = copy.deepcopy(self.reservation)
        reservation.update(action="send", status="UNKNOWN", target_thread_id="actual-worker-fixture")
        plan = self.plan(reservation)
        self.assertEqual(plan["inspection_tool_call"], {"name": "mcp__codex_app__wait_threads", "arguments": {"targets": [{"threadId": "actual-worker-fixture"}], "timeoutMs": 0}})
        self.assertIsNone(plan["tool_call"])

    def test_client_thread_id_cannot_be_promoted_to_a_real_target(self):
        reservation = copy.deepcopy(self.reservation)
        reservation.update(action="send", target_thread_id="client-only-id", clientThreadId="client-only-id")
        with self.assertRaisesRegex(DispatchPlanError, "clientThreadId"):
            self.plan(reservation)

    def test_send_without_real_target_and_self_dispatch_are_rejected(self):
        for target in (None, "controller-fixture"):
            reservation = copy.deepcopy(self.reservation)
            reservation.update(action="send", target_thread_id=target)
            with self.assertRaises(DispatchPlanError):
                self.plan(reservation)

    def test_prompt_carries_immutable_version_real_worker_identity_and_manual_return_contract(self):
        prompt = self.plan()["tool_call"]["arguments"]["prompt"]
        metadata_section = prompt.split("\n\n")[2]
        metadata = json.loads(metadata_section[metadata_section.index("{"):])
        self.assertEqual(metadata["packet_path"], self.reservation["packet_path"])
        self.assertEqual(metadata["packet_sha256"], self.reservation["packet_sha256"])
        self.assertEqual(metadata["revision"], self.reservation["revision"])
        for required in ("a" * 64, "revision", "scene-with-all-views", "真实 Codex task/thread ID", "WAITING_FOR_DISPATCH_BINDING", "领取", "guard", "result", "人工 Alpha", "不重复生产", "claim-next", "LOCAL_CONTINUATION", "WAITING_UPSTREAM"):
            self.assertIn(required, prompt)

    def test_planning_is_pure_and_does_not_claim_reserve_or_open_the_database(self):
        path = Path(self.reservation["database_path"])
        path.write_bytes(b"not a database; pure planning must not open it")
        original = path.read_bytes()
        before = sorted(str(p) for p in self.root.rglob("*"))
        one, two = self.plan(), self.plan()
        self.assertEqual(one, two)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(sorted(str(p) for p in self.root.rglob("*")), before)

    def test_invalid_digest_relative_paths_and_revision_are_rejected(self):
        for key, value in (("packet_sha256", "incomplete"), ("packet_sha256", None), ("packet_path", "relative.json"), ("revision", True), ("revision", 0)):
            with self.subTest(key=key, value=value):
                reservation = copy.deepcopy(self.reservation)
                reservation[key] = value
                with self.assertRaises(DispatchPlanError):
                    self.plan(reservation)

    def test_powershell_commands_quote_metacharacters_without_interpolation(self):
        argv = [sys.executable, "a'b $(no_execution).py", "--reason", "Do not execute `anything`."]
        output = command(argv)
        self.assertEqual(output["argv"], argv)
        self.assertIn("'a''b $(no_execution).py'", output["powershell"])
        self.assertIn("'Do not execute `anything`.'", output["powershell"])

    def test_cli_emits_a_plan_file_without_invoking_the_app(self):
        reservation, context, output = [self.root / name for name in ("reservation.json", "context.json", "plan.json")]
        reservation.write_text(json.dumps(self.reservation), encoding="utf-8")
        context.write_text(json.dumps(self.context), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", str(SCRIPTS / "dispatch_plan.py"), "--reservation", str(reservation), "--project-context", str(context), "--out", str(output)], capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertEqual(json.loads(run.stdout)["effect"], "PARAMETERS_ONLY_NO_APP_CALL")
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["dispatch_id"], "dispatch-fixture-01")
        self.assertFalse(Path(self.reservation["database_path"]).exists())


if __name__ == "__main__":
    unittest.main()
