from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manual_requirements.py"
SPEC = importlib.util.spec_from_file_location("manual_requirements", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def artifact(
    role: str,
    *,
    requirement: str = "REQUIRED",
    status: str = "EFFECTIVE_PASS",
    action: str = "NONE",
    owner: str = "CODEX",
    profile: str = "",
) -> dict:
    return {
        "role": role,
        "profile": profile,
        "requirement": requirement,
        "current_status": status,
        "manual_action": action,
        "owner": owner,
        "spec": f"{role} specification",
        "reason": f"{role} is part of the frozen requirement",
    }


def valid_payload() -> dict:
    return {
        "schema": MODULE.SCHEMA,
        "chapter": {
            "id": "UnitX",
            "title": "测试章节",
            "revision": "r1",
            "generated_at": "2026-09-15T12:00:00+08:00",
        },
        "scope": {
            "objective": "整理全部道具及人工补缺任务",
            "active_scope_sha256": "a" * 64,
            "item_ids": ["1001"],
            "scene_ids": ["SC1001"],
            "excluded": [],
        },
        "sources": [
            {
                "source_id": "current-content",
                "kind": "content_archive",
                "path": "{WORK_ROOT}/UnitX/content_archive.json",
                "sha256": "b" * 64,
                "authority": "current",
                "note": "锁定 Item 与场景事实",
            }
        ],
        "items": [
            {
                "item_id": "1001",
                "name": "普通道具",
                "semantic_class": "ordinary_prop",
                "acquisition_route": "detail-only",
                "acquisition_event": "剧情详情中展示",
                "source_refs": ["current-content"],
                "content_contract": {
                    "hard_facts": ["身份与文字必须匹配当前剧情"],
                    "allowed_differences": [],
                    "visual_freedom": ["不影响辨识的细微材质变化"],
                },
                "artifacts": [
                    artifact("big", profile="ordinary_big"),
                    artifact("icon", status="CANDIDATE"),
                    artifact("map_hotspot", requirement="NOT_APPLICABLE"),
                    artifact("xy", requirement="NOT_APPLICABLE"),
                    artifact("type6_container", requirement="NOT_APPLICABLE"),
                    artifact("type7_menu", requirement="NOT_APPLICABLE"),
                ],
                "human_tasks": [],
                "open_questions": [],
            }
        ],
        "scene_packages": [
            {
                "scene_id": "SC1001",
                "label": {"location": "测试地点", "time": "白天", "state": "默认"},
                "item_ids": ["1001"],
                "manual_task_ids": [],
                "release_blockers": [],
            }
        ],
        "status_summary": {
            "candidate_count": 1,
            "provisional_count": 0,
            "effective_pass_count": 1,
            "rejected_count": 0,
            "unknown_count": 0,
        },
    }


class ManualRequirementsValidationTests(unittest.TestCase):
    def assert_error_contains(self, report: dict, text: str) -> None:
        self.assertFalse(report["valid"])
        self.assertTrue(
            any(text in error for error in report["errors"]),
            msg=f"expected {text!r} in errors: {report['errors']}",
        )

    def test_valid_payload_passes(self) -> None:
        report = MODULE.validate_data(valid_payload())
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["counts"]["items"], 1)
        self.assertEqual(report["counts"]["semantic_classes"], {"ordinary_prop": 1})

    def test_photo_clue_requires_clue_big_profile(self) -> None:
        data = valid_payload()
        item = data["items"][0]
        item["semantic_class"] = "photo_clue"
        item["artifacts"][0]["profile"] = "ordinary_big"
        report = MODULE.validate_data(data)
        self.assert_error_contains(report, "photo clue requires clue_big_620x620")

    def test_scene_pickup_requires_four_states_map_and_xy(self) -> None:
        data = valid_payload()
        data["items"][0]["acquisition_route"] = "scene-pickup"
        report = MODULE.validate_data(data)
        for role in (
            "scene_original",
            "carrier_without_prop",
            "pickup_layer",
            "scene_before_pickup",
        ):
            self.assert_error_contains(report, f"missing artifact role {role}")
        for role in ("map_hotspot", "xy"):
            self.assert_error_contains(
                report,
                f"artifacts[{role}]: must be REQUIRED for this acquisition route",
            )

    def test_manual_action_requires_covering_human_task(self) -> None:
        data = valid_payload()
        big = data["items"][0]["artifacts"][0]
        big["manual_action"] = "REPAIR"
        big["owner"] = "HUMAN"
        report = MODULE.validate_data(data)
        self.assert_error_contains(report, "manual-action roles without a human task ['big']")

    def test_unresolved_classification_requires_question(self) -> None:
        data = valid_payload()
        data["items"][0]["semantic_class"] = "unresolved"
        report = MODULE.validate_data(data)
        self.assert_error_contains(report, "unresolved classification needs a concrete question")

    def test_duplicate_item_ids_are_rejected(self) -> None:
        data = valid_payload()
        data["items"].append(copy.deepcopy(data["items"][0]))
        report = MODULE.validate_data(data)
        self.assert_error_contains(report, "duplicate item_id values ['1001']")

    def test_init_writes_a_chapter_specific_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "draft.json"
            result = MODULE.command_init(
                Namespace(chapter_id="UnitX", title="测试章节", revision="r2", output=str(output))
            )
            self.assertEqual(result, 0)
            draft = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(draft["chapter"]["id"], "UnitX")
            self.assertEqual(draft["chapter"]["revision"], "r2")

    def test_summary_writes_human_review_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "valid.json"
            output_path = Path(temp_dir) / "summary.md"
            input_path.write_text(
                json.dumps(valid_payload(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            result = MODULE.command_summary(Namespace(input=str(input_path), output=str(output_path)))
            self.assertEqual(result, 0)
            summary = output_path.read_text(encoding="utf-8")
            self.assertIn("资产性质", summary)
            self.assertIn("ordinary_prop", summary)
            self.assertIn("需求清单和人工交接，不等于资产正式 PASS", summary)


if __name__ == "__main__":
    unittest.main()
