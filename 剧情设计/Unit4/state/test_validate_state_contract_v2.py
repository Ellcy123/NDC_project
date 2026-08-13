from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = Path(__file__).with_name("validate_state_contract_v2.py")
STATE_RELATIVE = Path("剧情设计/Unit4/state")


def load_validator():
    if not VALIDATOR_PATH.exists():
        raise AssertionError("validate_state_contract_v2.py is missing")

    import importlib.util

    spec = importlib.util.spec_from_file_location("unit4_state_validator_v2", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Unit4StateContractV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="unit4-state-v2-"))
        shutil.copy2(REPO_ROOT / "canon_manifest.json", self.tmpdir / "canon_manifest.json")
        outline_relative = Path("剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md")
        outline_target = self.tmpdir / outline_relative
        outline_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / outline_relative, outline_target)

        source = REPO_ROOT / STATE_RELATIVE
        target = self.tmpdir / STATE_RELATIVE
        target.parent.mkdir(parents=True, exist_ok=True)
        if not source.exists():
            self.fail("Unit4 formal State set is missing")
        shutil.copytree(source, target)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def validate(self):
        validator_module = load_validator()
        return validator_module.Unit4StateV2Validator(
            root=self.tmpdir,
            state_dir=STATE_RELATIVE,
        ).validate()

    def load_state(self, loop_number: int) -> dict:
        path = self.tmpdir / STATE_RELATIVE / f"loop{loop_number}_state.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def save_state(self, loop_number: int, state: dict) -> None:
        path = self.tmpdir / STATE_RELATIVE / f"loop{loop_number}_state.yaml"
        path.write_text(
            yaml.safe_dump(state, allow_unicode=True, sort_keys=False, width=120),
            encoding="utf-8",
        )

    def assert_error_contains(self, fragment: str) -> None:
        errors = self.validate()
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}, got {errors!r}",
        )

    @staticmethod
    def inline_testimonies(value) -> list[dict]:
        entries: list[dict] = []
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "testimony_ids" and isinstance(child, list):
                    entries.extend(
                        entry for entry in child if isinstance(entry, dict)
                    )
                else:
                    entries.extend(Unit4StateContractV2Test.inline_testimonies(child))
        elif isinstance(value, list):
            for child in value:
                entries.extend(Unit4StateContractV2Test.inline_testimonies(child))
        return entries

    @staticmethod
    def contains_key(value, target: str) -> bool:
        if isinstance(value, dict):
            return target in value or any(
                Unit4StateContractV2Test.contains_key(child, target)
                for child in value.values()
            )
        if isinstance(value, list):
            return any(
                Unit4StateContractV2Test.contains_key(child, target)
                for child in value
            )
        return False

    def test_candidate_state_set_satisfies_v2_contract(self) -> None:
        self.assertEqual([], self.validate())

    def test_candidate_state_has_no_deprecated_trap_evidence(self) -> None:
        for loop_number in range(1, 6):
            state = self.load_state(loop_number)
            self.assertFalse(
                self.contains_key(state, "trap_evidence"),
                f"loop{loop_number} still contains deprecated trap_evidence",
            )

    def test_rejects_deprecated_trap_evidence(self) -> None:
        state = self.load_state(5)
        state["expose"]["rounds"][0]["trap_evidence"] = [{"id": 4511}]
        self.save_state(5, state)

        self.assert_error_contains("deprecated State field is forbidden")

    def test_testimonies_are_inline_and_registry_is_absent(self) -> None:
        for loop_number in range(1, 6):
            state = self.load_state(loop_number)
            self.assertNotIn("testimony_registry", state)
            for testimony in self.inline_testimonies(state):
                self.assertIsInstance(testimony.get("id"), int)
                self.assertNotIn(
                    "name",
                    testimony,
                    f"loop{loop_number} testimony {testimony.get('id')} uses redundant name",
                )
                self.assertTrue(
                    str(testimony.get("content", "")).strip(),
                    f"loop{loop_number} testimony {testimony.get('id')} has no content",
                )

    def test_expose_lie_source_semantics_distinguish_round_one(self) -> None:
        for loop_number in range(1, 6):
            state = self.load_state(loop_number)
            semantics = state["expose"]["lie_source_semantics"]
            self.assertTrue(
                semantics["round_1"]["collectible_testimony"],
                f"loop{loop_number} round 1 must be collected before Expose",
            )
            self.assertFalse(
                semantics["later_rounds"]["collectible_testimony"],
                f"loop{loop_number} later retreat lies must stay inside Expose",
            )

    def test_dynamic_expose_lies_are_not_precollectable_testimony_ids(self) -> None:
        for loop_number in range(1, 6):
            state = self.load_state(loop_number)
            for scene in state.get("scenes", []):
                for npc_key, npc in (scene.get("npcs") or {}).items():
                    dynamic_ids = [
                        testimony.get("id")
                        for testimony in (npc.get("testimony_ids") or [])
                        if (
                            isinstance(testimony, dict)
                            and testimony.get("kind") == "expose_dynamic_lie"
                        )
                    ]
                    self.assertEqual(
                        [],
                        dynamic_ids,
                        f"loop{loop_number} {npc_key} pre-collects dynamic lies",
                    )

    def test_rejects_inline_testimony_without_content(self) -> None:
        state = self.load_state(3)
        testimony = next(
            entry
            for entry in self.inline_testimonies(state)
            if entry["id"] == 4063001
        )
        testimony.pop("content", None)
        self.save_state(3, state)

        self.assert_error_contains("inline testimony content")

    def test_rejects_redundant_inline_testimony_name(self) -> None:
        state = self.load_state(1)
        testimony = next(
            entry
            for entry in self.inline_testimonies(state)
            if entry["id"] == 4161001
        )
        testimony["name"] = "Harrison连续调阅旧档案的记录证词"
        self.save_state(1, state)

        self.assert_error_contains("inline testimony fields are forbidden")

    def test_rejects_outline_testimony_without_source_anchor(self) -> None:
        state = self.load_state(2)
        testimony = next(
            entry
            for entry in self.inline_testimonies(state)
            if entry["id"] == 4092004
        )
        testimony.pop("source_anchor", None)
        self.save_state(2, state)

        self.assert_error_contains("outline testimony source anchor")

    def test_rejects_person_named_opening_talk(self) -> None:
        state = self.load_state(3)
        state["opening"]["sequence"][0]["talk"] = "L3_opening_emma"
        self.save_state(3, state)

        self.assert_error_contains("person-named opening talk")

    def test_rejects_runtime_root_that_does_not_match_first_event(self) -> None:
        state = self.load_state(3)
        state["opening"]["runtime_root"]["init_scene"] = 4999
        self.save_state(3, state)

        self.assert_error_contains("runtime root")

    def test_rejects_player_control_before_last_opening_event(self) -> None:
        state = self.load_state(3)
        state["opening"]["player_control_restored_after"] = "broken_call"
        self.save_state(3, state)

        self.assert_error_contains("player control")

    def test_rejects_opening_talk_duplicated_as_free_npc_talk(self) -> None:
        state = self.load_state(3)
        opening_talk = state["opening"]["sequence"][1]["talk"]
        state["scenes"][1]["npcs"]["duplicate_opening"] = {"talk": opening_talk}
        self.save_state(3, state)

        self.assert_error_contains("duplicated as free NPC talk")

    def test_rejects_unapproved_added_outline_beat(self) -> None:
        state = self.load_state(5)
        state["outline_coverage"].append(
            {
                "beat_id": "L5_added_doorman",
                "source_anchor": "none",
                "mapping": "added",
                "primary_landing": "opening.sequence.forty_second_floor_arrival",
            }
        )
        self.save_state(5, state)

        self.assert_error_contains("requires approval")

    def test_rejects_dangling_continuity_handoff(self) -> None:
        state = self.load_state(2)
        state["narrative_continuity"][0]["hands_off_to"] = "missing_unit"
        self.save_state(2, state)

        self.assert_error_contains("dangling handoff")

    def test_rejects_loop5_night_doorman_reintroduction(self) -> None:
        state = self.load_state(5)
        state["opening"]["sequence"][0]["cast"].append("夜班门房")
        self.save_state(5, state)

        self.assert_error_contains("night doorman")

    def test_rejects_analysis_enabled_clue(self) -> None:
        state = self.load_state(5)
        evidence = next(
            entry for entry in state["evidence_registry"] if entry["id"] == 4511
        )
        evidence["type"] = "clue"
        evidence["analysis"] = True
        self.save_state(5, state)

        self.assert_error_contains("clue cannot be analyzed")

    def test_rejects_expose_evidence_not_loaded_by_doubt_or_identity_chain(self) -> None:
        state = self.load_state(1)
        doubt = next(entry for entry in state["doubts"] if entry["id"] == 4102)
        doubt["unlock_condition"] = []
        self.save_state(1, state)

        self.assert_error_contains("Expose usable evidence is not loaded")

    def test_rejects_missing_outline_npc_marker_coverage(self) -> None:
        state = self.load_state(2)
        state["outline_coverage"] = [
            row
            for row in state["outline_coverage"]
            if not row.get("dialogue_required")
        ]
        self.save_state(2, state)

        self.assert_error_contains("outline NPC marker coverage mismatch")

    def test_rejects_npc_marker_without_free_talk_binding(self) -> None:
        state = self.load_state(2)
        marker = next(
            (
                row
                for row in state["outline_coverage"]
                if row.get("marker_id") == "L2_NPC_ROSA"
            ),
            None,
        )
        if marker is None:
            state["outline_coverage"].append(
                {
                    "beat_id": "L2_NPC_ROSA",
                    "marker_id": "L2_NPC_ROSA",
                    "source_anchor": "active outline / Loop2 / 自由探索 / Zack侦探事务所 / NPC Rosa",
                    "mapping": "exact",
                    "primary_landing": "scenes.4011.npcs.L2_scene4011_rosa",
                    "dialogue_required": True,
                    "npc_name": "Rosa",
                    "scene_id": 4011,
                    "npc_key": "L2_scene4011_rosa",
                    "talk": "L2_scene4011_rosa",
                }
            )
        scene = next(entry for entry in state["scenes"] if entry["id"] == 4011)
        scene.setdefault("npcs", {}).pop("L2_scene4011_rosa", None)
        self.save_state(2, state)

        self.assert_error_contains("NPC marker Talk binding")

    def test_rejects_dialogue_evidence_with_wrong_talk_source(self) -> None:
        state = self.load_state(2)
        scene = next(entry for entry in state["scenes"] if entry["id"] == 4011)
        evidence = next(entry for entry in scene["evidence"] if entry["id"] == 4211)
        evidence.setdefault("acquisition", {})["kind"] = "dialogue"
        evidence["acquisition"]["talk"] = "missing_talk"
        self.save_state(2, state)

        self.assert_error_contains("dialogue evidence acquisition")

    def test_rejects_outline_dialogue_evidence_without_binding(self) -> None:
        state = self.load_state(2)
        scene = next(entry for entry in state["scenes"] if entry["id"] == 4013)
        evidence = next(entry for entry in scene["evidence"] if entry["id"] == 4213)
        evidence.pop("acquisition", None)
        registry = next(
            entry for entry in state["evidence_registry"] if entry["id"] == 4213
        )
        registry.pop("acquisition", None)
        self.save_state(2, state)

        self.assert_error_contains("outline dialogue evidence lacks dialogue acquisition")

    def test_rejects_acquired_evidence_without_outline_coverage(self) -> None:
        state = self.load_state(2)
        state["outline_coverage"] = [
            row
            for row in state["outline_coverage"]
            if row.get("evidence_id") != 4215
        ]
        self.save_state(2, state)

        self.assert_error_contains("acquired evidence lacks delivery coverage")

    def test_rejects_invented_dialogue_evidence_source(self) -> None:
        state = self.load_state(2)
        scene = next(entry for entry in state["scenes"] if entry["id"] == 4012)
        evidence = next(entry for entry in scene["evidence"] if entry["id"] == 4216)
        evidence["acquisition"] = {
            "kind": "dialogue",
            "talk": "L2_scene4015_mickey",
        }
        registry = next(
            entry for entry in state["evidence_registry"] if entry["id"] == 4216
        )
        registry["acquisition"] = evidence["acquisition"].copy()
        mickey_scene = next(
            entry for entry in state["scenes"] if entry["id"] == 4015
        )
        mickey_scene["npcs"]["L2_scene4015_mickey"].setdefault(
            "grants_evidence", []
        ).append(4216)
        state["outline_coverage"].append(
            {
                "beat_id": "L2_INVENTED_DIALOGUE_4216",
                "source_anchor": "active outline / Loop2 / 法院会客室",
                "mapping": "exact",
                "primary_landing": "scenes.4012.evidence.4216.acquisition",
                "evidence_delivery_required": True,
                "evidence_id": 4216,
                "acquisition_kind": "dialogue",
                "acquisition_talk": "L2_scene4015_mickey",
            }
        )
        self.save_state(2, state)

        self.assert_error_contains("dialogue acquisition lacks explicit outline source")

    def test_rejects_event_talk_with_duplicate_runtime_entry(self) -> None:
        state = self.load_state(3)
        scene = next(entry for entry in state["scenes"] if entry["id"] == 4023)
        scene.setdefault("event_triggers", []).append(
            {
                "id": "duplicate_evacuation",
                "condition": "first_enter",
                "talk": "L3_opening_mansion_arrival",
                "forced": True,
                "runtime_binding": {
                    "adapter": "ordered_story_event",
                },
            }
        )
        self.save_state(3, state)

        self.assert_error_contains("both chained and independently triggered")

    def test_rejects_ordered_story_event_without_required_talk(self) -> None:
        state = self.load_state(4)
        scene = next(entry for entry in state["scenes"] if entry["id"] == 4033)
        event = next(
            entry
            for entry in scene["event_triggers"]
            if entry["id"] == "stop_order_application_and_delivery"
        )
        event["condition"]["all_of"]["required_talks"] = []
        self.save_state(4, state)

        self.assert_error_contains("ordered story event lacks fixed prerequisites")

    def test_rejects_mickey_as_free_npc_before_forced_return(self) -> None:
        state = self.load_state(5)
        office = next(entry for entry in state["scenes"] if entry["id"] == 4042)
        office["npcs"] = {"mickey": {"talk": "L5_scene4042_mickey"}}
        self.save_state(5, state)

        self.assert_error_contains("Mickey return must not be a free NPC Talk")

    def test_rejects_ending_without_post_expose_entry(self) -> None:
        state = self.load_state(5)
        state["expose"]["post_expose"].pop("runtime_exit", None)
        self.save_state(5, state)

        self.assert_error_contains("ending sequence has no unique post-expose entry")

    def test_rejects_ending_scene_with_free_npc_talk(self) -> None:
        state = self.load_state(5)
        state["ending_sequence"]["scenes"][0]["npcs"] = {
            "emma": {"talk": "L5_ending4043_emma"}
        }
        self.save_state(5, state)

        self.assert_error_contains("ending scene ending_4043 has free NPC Talk data")


if __name__ == "__main__":
    unittest.main()
