from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_STATE_DIR = Path("剧情设计/Unit4/state")
PERSON_TOKENS = {
    "zack",
    "emma",
    "mickey",
    "pierce",
    "rosa",
    "doris",
    "margaret",
    "watts",
    "morrison",
    "harold",
    "whitfield",
    "foster",
    "ohara",
}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def scalar_values(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from scalar_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from scalar_values(child)
    elif value is not None:
        yield value


class Unit4StateV2Validator:
    def __init__(self, root: str | Path, state_dir: str | Path = DEFAULT_STATE_DIR):
        self.root = Path(root).resolve()
        self.state_dir = self.root / Path(state_dir)
        self.errors: list[str] = []
        self.contract: dict = {}
        self.states: dict[int, dict] = {}
        self.manifest: dict = {}

    def validate(self) -> list[str]:
        self.errors = []
        self._load()
        if not self.contract or len(self.states) != 5 or not self.manifest:
            return self.errors

        self._validate_contract_and_manifest()
        self._validate_deprecated_fields()
        self._validate_field_policy()
        self._validate_known_facts()
        self._validate_scene_vocab()
        self._validate_openings()
        self._validate_outline_coverage()
        self._validate_outline_npc_markers()
        self._validate_inline_testimonies()
        self._validate_outline_testimony_markers()
        self._validate_dialogue_evidence_acquisition()
        self._validate_evidence_delivery_coverage()
        self._validate_runtime_events()
        self._validate_continuity()
        self._validate_identity_lock()
        self._validate_persistence()
        self._validate_non_progress_records()
        self._validate_ending()
        self._validate_evidence_types()
        self._validate_expose_evidence_coverage()
        self._validate_unit4_specific_content()
        return self.errors

    def _validate_deprecated_fields(self) -> None:
        def walk(value: Any, path: str) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = f"{path}.{key}" if path else str(key)
                    if key == "trap_evidence":
                        self.errors.append(
                            f"deprecated State field is forbidden: {child_path}"
                        )
                    walk(child, child_path)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{path}[{index}]")

        for loop_number, state in self.states.items():
            walk(state, f"loop{loop_number}")

    def _load_yaml(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as stream:
            return yaml.load(stream, Loader=UniqueKeyLoader)

    def _load(self) -> None:
        contract_path = self.state_dir / "state_contract.yaml"
        if not contract_path.exists():
            self.errors.append(f"missing state contract: {contract_path}")
            return
        try:
            self.contract = self._load_yaml(contract_path)
        except (yaml.YAMLError, OSError) as exc:
            self.errors.append(f"invalid state contract YAML: {exc}")
            return

        for loop_number in range(1, 6):
            path = self.state_dir / f"loop{loop_number}_state.yaml"
            if not path.exists():
                self.errors.append(f"missing loop state: {path}")
                continue
            try:
                self.states[loop_number] = self._load_yaml(path)
            except (yaml.YAMLError, OSError) as exc:
                self.errors.append(f"invalid YAML in loop{loop_number}: {exc}")

        manifest_path = self.root / "canon_manifest.json"
        try:
            self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            self.errors.append(f"invalid or missing canon_manifest.json: {exc}")

        if (self.state_dir / "loop6_state.yaml").exists():
            self.errors.append("loop6_state.yaml must not exist for Unit4")

    def _unit4_manifest(self) -> dict | None:
        return next(
            (
                chapter
                for chapter in self.manifest.get("chapters", [])
                if chapter.get("canonicalUnit") == "Unit4"
            ),
            None,
        )

    def _validate_contract_and_manifest(self) -> None:
        if self.contract.get("version") != 2 or self.contract.get("unit") != "Unit4":
            self.errors.append("contract must be Unit4 version 2")

        chapter = self._unit4_manifest()
        if not chapter:
            self.errors.append("canon manifest has no Unit4 chapter")
            return

        canon = self.contract.get("canon_source", {})
        expected = {
            "planning_directory": chapter.get("planningDirectory"),
            "active_outline": chapter.get("sources", {}).get("outline"),
            "episode": chapter.get("unityEpisode"),
            "id_space": "4xxx",
            "expected_loops": chapter.get("maturity", {}).get("state", {}).get("expectedLoops"),
            "structure": chapter.get("maturity", {}).get("structure"),
        }
        for key, value in expected.items():
            if canon.get(key) != value:
                self.errors.append(
                    f"canon source mismatch for {key}: expected {value!r}, got {canon.get(key)!r}"
                )

        id_spaces = chapter.get("idSpaces", [])
        if not any(
            entry.get("range") == canon.get("id_space")
            and entry.get("episode") == canon.get("episode")
            and entry.get("status") == "current"
            for entry in id_spaces
        ):
            self.errors.append("canon source ID space is not the active Unit4 namespace")

        outline_path = self.root / str(canon.get("active_outline", ""))
        if not outline_path.exists():
            self.errors.append("active Unit4 outline is missing")

        required_contracts = (
            "opening_contract",
            "outline_coverage_contract",
            "narrative_continuity_contract",
            "expose_evidence_contract",
            "testimony_contract",
            "runtime_event_contract",
        )
        for key in required_contracts:
            if not isinstance(self.contract.get(key), dict):
                self.errors.append(f"missing {key}")

    def _validate_field_policy(self) -> None:
        policy = self.contract.get("field_policy", {})
        required = {
            "opening": "structural",
            "outline_coverage": "design_only",
            "narrative_continuity": "design_only",
            "scenes": "runtime_source",
            "expose": "runtime_source",
        }
        for key, category in required.items():
            if policy.get(key) != category:
                self.errors.append(f"field policy mismatch: {key} must be {category}")

        allowed = {"runtime_source", "design_only", "special_adapter", "structural"}
        invalid = set(policy.values()) - allowed
        if invalid:
            self.errors.append(f"field policy contains unsupported categories: {sorted(invalid)!r}")

        for loop_number, state in self.states.items():
            for key in state:
                if key not in policy:
                    self.errors.append(
                        f"loop{loop_number} has unclassified top-level field: {key}"
                    )

    def _validate_known_facts(self) -> None:
        inherited: list[Any] = []
        for loop_number, state in self.states.items():
            actual = list(state.get("player_context", {}).get("known_facts") or [])
            if actual != inherited:
                self.errors.append(
                    f"loop{loop_number} known facts inheritance does not match prior post-expose knowledge"
                )
            inherited += list(
                state.get("player_context", {}).get("post_expose_knowledge") or []
            )

    def _validate_scene_vocab(self) -> None:
        allowed_types = set(self.contract.get("scene_types", []))
        allowed_tags = set(self.contract.get("design_tags", []))
        for loop_number, state in self.states.items():
            groups = [("scene", state.get("scenes", []))]
            if loop_number == 5:
                groups.append(
                    ("ending scene", state.get("ending_sequence", {}).get("scenes", []))
                )
            for label, scenes in groups:
                for scene in scenes or []:
                    if scene.get("type") not in allowed_types:
                        self.errors.append(
                            f"loop{loop_number} {label} {scene.get('id')} has unsupported scene type"
                        )
                    for tag in scene.get("design_tags", []) or []:
                        if tag not in allowed_tags:
                            self.errors.append(
                                f"loop{loop_number} {label} {scene.get('id')} has unsupported design tag"
                            )

    def _validate_openings(self) -> None:
        for loop_number, state in self.states.items():
            opening = state.get("opening")
            if not isinstance(opening, dict):
                self.errors.append(f"loop{loop_number} opening is missing")
                continue
            if opening.get("type") != "cutscene_sequence":
                self.errors.append(f"loop{loop_number} opening must be cutscene_sequence")

            runtime_root = opening.get("runtime_root", {})
            sequence = opening.get("sequence")
            if not isinstance(sequence, list) or not sequence:
                self.errors.append(f"loop{loop_number} opening sequence is empty")
                continue

            first = sequence[0]
            if (
                runtime_root.get("table") != "ChapterConfig"
                or runtime_root.get("init_scene") != first.get("scene_id")
                or runtime_root.get("init_talk") != first.get("talk")
            ):
                self.errors.append(f"loop{loop_number} opening runtime root does not match first event")

            event_ids = [event.get("event_id") for event in sequence]
            if None in event_ids or len(event_ids) != len(set(event_ids)):
                self.errors.append(f"loop{loop_number} opening event IDs must be unique")

            if opening.get("player_control_restored_after") != event_ids[-1]:
                self.errors.append(
                    f"loop{loop_number} player control must be restored after the last opening event"
                )

            scene_ids = {scene.get("id") for scene in state.get("scenes", [])}
            opening_talks: set[str] = set()
            for index, event in enumerate(sequence):
                talk = str(event.get("talk", ""))
                opening_talks.add(talk)
                suffix = talk.lower().split("_opening_", 1)[-1]
                suffix_tokens = set(suffix.replace("-", "_").split("_"))
                if "_opening_" not in talk.lower() or suffix_tokens & PERSON_TOKENS:
                    self.errors.append(
                        f"loop{loop_number} person-named opening talk is forbidden: {talk}"
                    )
                if not event.get("source_anchor") or not event.get("required_beats"):
                    self.errors.append(
                        f"loop{loop_number} opening event {event.get('event_id')} lacks outline anchors"
                    )
                if event.get("scene_id") not in scene_ids:
                    self.errors.append(
                        f"loop{loop_number} opening scene {event.get('scene_id')} is missing from scenes"
                    )

                runtime_exit = event.get("runtime_exit", {})
                if index < len(sequence) - 1:
                    next_event = sequence[index + 1]
                    if (
                        runtime_exit.get("action") != "change_scene"
                        or runtime_exit.get("target_scene_id") != next_event.get("scene_id")
                        or runtime_exit.get("continuation") != "next_talk"
                        or runtime_exit.get("next_talk") != next_event.get("talk")
                    ):
                        self.errors.append(
                            f"loop{loop_number} cross-scene opening continuation is incomplete"
                        )
                elif runtime_exit.get("continuation") == "next_talk":
                    self.errors.append(
                        f"loop{loop_number} final opening event must release player control"
                    )

            for scene in state.get("scenes", []):
                if scene.get("first_enter_talk") in opening_talks:
                    self.errors.append(
                        f"loop{loop_number} opening talk duplicated as scene first-enter talk"
                    )
                for npc in (scene.get("npcs") or {}).values():
                    if npc.get("talk") in opening_talks or npc.get("loop_talk") in opening_talks:
                        self.errors.append(
                            f"loop{loop_number} opening talk duplicated as free NPC talk"
                        )

    def _validate_outline_coverage(self) -> None:
        contract = self.contract.get("outline_coverage_contract", {})
        allowed = set(contract.get("allowed_mappings", []))
        approval_required = set(contract.get("require_approval_for", []))
        beat_ids: list[str] = []
        landings: list[str] = []

        for loop_number, state in self.states.items():
            rows = state.get("outline_coverage")
            if not isinstance(rows, list) or not rows:
                self.errors.append(f"loop{loop_number} outline coverage is missing")
                continue
            for row in rows:
                beat_id = row.get("beat_id")
                landing = row.get("primary_landing")
                mapping = row.get("mapping")
                source_anchor = str(row.get("source_anchor", "")).strip()
                if not beat_id or not landing:
                    self.errors.append(f"loop{loop_number} outline coverage row is incomplete")
                beat_ids.append(beat_id)
                if not (
                    row.get("testimony_required") is True
                    and mapping == "merged"
                ):
                    landings.append(landing)
                if mapping not in allowed:
                    self.errors.append(
                        f"loop{loop_number} outline mapping is invalid: {mapping!r}"
                    )
                if not source_anchor or source_anchor.lower() in {"none", "n/a"}:
                    self.errors.append(
                        f"loop{loop_number} outline coverage has an unsourced addition"
                    )
                if mapping == "deferred" and not row.get("deferred_target"):
                    self.errors.append(
                        f"loop{loop_number} deferred outline beat lacks target"
                    )
                if mapping in approval_required and not row.get("approval_id"):
                    self.errors.append(
                        f"loop{loop_number} outline mapping {mapping!r} requires approval"
                    )

        if len(beat_ids) != len(set(beat_ids)):
            self.errors.append("outline beat IDs must be globally unique")
        if len(landings) != len(set(landings)):
            self.errors.append("outline primary landings must be globally unique")

    def _validate_outline_npc_markers(self) -> None:
        outline_relative = self.contract.get("canon_source", {}).get("active_outline")
        outline_path = self.root / str(outline_relative or "")
        if not outline_path.exists():
            return

        expected: list[tuple[int, str]] = []
        current_loop: int | None = None
        for line in outline_path.read_text(encoding="utf-8").splitlines():
            loop_match = re.match(r"^# Loop (\d+)", line)
            if loop_match:
                current_loop = int(loop_match.group(1))
                continue
            marker_match = re.search(r"👤 NPC[：:]\s*(.+?)\s*$", line)
            if current_loop is not None and marker_match:
                expected.append((current_loop, marker_match.group(1).strip()))

        actual: list[tuple[int, str]] = []
        marker_rows: list[tuple[int, dict]] = []
        for loop_number, state in self.states.items():
            for row in state.get("outline_coverage", []):
                if row.get("dialogue_required") is True:
                    actual.append((loop_number, str(row.get("npc_name", "")).strip()))
                    marker_rows.append((loop_number, row))

        if Counter(actual) != Counter(expected):
            missing = list((Counter(expected) - Counter(actual)).elements())
            extra = list((Counter(actual) - Counter(expected)).elements())
            self.errors.append(
                f"outline NPC marker coverage mismatch; missing={missing!r}, extra={extra!r}"
            )

        for loop_number, row in marker_rows:
            state = self.states[loop_number]
            scene = next(
                (
                    entry
                    for entry in state.get("scenes", [])
                    if entry.get("id") == row.get("scene_id")
                ),
                None,
            )
            npc = (scene or {}).get("npcs", {}).get(row.get("npc_key"))
            if (
                not npc
                or not row.get("talk")
                or npc.get("talk") != row.get("talk")
            ):
                self.errors.append(
                    f"loop{loop_number} NPC marker Talk binding is missing or mismatched: {row.get('marker_id')}"
                )

    def _validate_inline_testimonies(self) -> None:
        contract = self.contract.get("testimony_contract", {})
        required_fields = tuple(contract.get("required_inline_fields", []))
        forbidden_fields = tuple(contract.get("forbidden_inline_fields", []))
        for loop_number, state in self.states.items():
            if (
                contract.get("centralized_registry_forbidden") is True
                and "testimony_registry" in state
            ):
                self.errors.append(
                    f"loop{loop_number} centralized testimony registry is forbidden"
                )

            inline_entries: list[dict] = []
            expose_lie_ids: set[int] = set()

            def collect_inline(value: Any) -> None:
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key == "testimony_ids":
                            if not isinstance(child, list):
                                self.errors.append(
                                    f"loop{loop_number} testimony_ids must be a list"
                                )
                                continue
                            for entry in child:
                                if not isinstance(entry, dict):
                                    self.errors.append(
                                        f"loop{loop_number} testimony_ids must contain "
                                        f"inline objects, not {entry!r}"
                                    )
                                    continue
                                inline_entries.append(entry)
                        elif key == "expose_lie_ids":
                            if isinstance(child, list):
                                expose_lie_ids.update(
                                    testimony_id
                                    for testimony_id in child
                                    if isinstance(testimony_id, int)
                                )
                        else:
                            collect_inline(child)
                elif isinstance(value, list):
                    for child in value:
                        collect_inline(child)

            collect_inline(state)

            inline_by_id: dict[int, dict] = {}
            for entry in inline_entries:
                testimony_id = entry.get("id")
                if not isinstance(testimony_id, int):
                    self.errors.append(
                        f"loop{loop_number} inline testimony ID is invalid: "
                        f"{testimony_id!r}"
                    )
                    continue
                if testimony_id in inline_by_id:
                    self.errors.append(
                        f"loop{loop_number} duplicate inline testimony ID: "
                        f"{testimony_id}"
                    )
                inline_by_id[testimony_id] = entry
                missing_fields = [
                    field for field in required_fields if field not in entry
                ]
                if missing_fields:
                    self.errors.append(
                        f"loop{loop_number} inline testimony fields missing for "
                        f"{testimony_id}: {missing_fields!r}"
                    )
                present_forbidden = [
                    field for field in forbidden_fields if field in entry
                ]
                if present_forbidden:
                    self.errors.append(
                        f"loop{loop_number} inline testimony fields are forbidden for "
                        f"{testimony_id}: {present_forbidden!r}"
                    )
                if not str(entry.get("content", "")).strip():
                    self.errors.append(
                        f"loop{loop_number} inline testimony content is missing: "
                        f"{testimony_id}"
                    )
                if (
                    contract.get("collectible_requires_acquisition_talk") is True
                    and not entry.get("acquisition_talk")
                ):
                    self.errors.append(
                        f"loop{loop_number} inline testimony lacks acquisition Talk: "
                        f"{testimony_id}"
                    )
                if entry.get("kind") == "expose_dynamic_lie":
                    self.errors.append(
                        f"loop{loop_number} dynamic Expose lie was pre-collected "
                        f"inside testimony_ids: {testimony_id}"
                    )

            expose = state.get("expose", {})
            rounds = expose.get("rounds")
            if isinstance(rounds, list):
                round_entries = rounds
            else:
                round_entries = [
                    round_entry
                    for key, round_entry in expose.items()
                    if key.startswith("round_")
                    and isinstance(round_entry, dict)
                ]

            for round_index, round_entry in enumerate(round_entries):
                testimony_id = round_entry.get("lie_source")
                if not isinstance(testimony_id, int):
                    continue
                if round_index == 0:
                    testimony = inline_by_id.get(testimony_id)
                    if not testimony:
                        self.errors.append(
                            f"loop{loop_number} round 1 lie_source has no inline "
                            f"testimony: {testimony_id}"
                        )
                    elif testimony.get("kind") != "collectible_lie_anchor":
                        self.errors.append(
                            f"loop{loop_number} round 1 lie_source is not a "
                            f"collectible lie anchor: {testimony_id}"
                        )
                else:
                    if testimony_id in inline_by_id:
                        self.errors.append(
                            f"loop{loop_number} later Expose lie was pre-collected: "
                            f"{testimony_id}"
                        )
                    if testimony_id not in expose_lie_ids:
                        self.errors.append(
                            f"loop{loop_number} later Expose lie_source is missing "
                            f"from expose_lie_ids: {testimony_id}"
                        )
                    if not str(round_entry.get("lie", "")).strip():
                        self.errors.append(
                            f"loop{loop_number} later Expose lie has no inline "
                            f"round text: {testimony_id}"
                        )

            later_lie_sources = {
                round_entry.get("lie_source")
                for round_entry in round_entries[1:]
                if isinstance(round_entry.get("lie_source"), int)
            }
            for testimony_id in sorted(expose_lie_ids - later_lie_sources):
                self.errors.append(
                    f"loop{loop_number} expose_lie_ids contains an unbound "
                    f"dynamic lie: {testimony_id}"
                )

    def _validate_outline_testimony_markers(self) -> None:
        outline_relative = self.contract.get("canon_source", {}).get("active_outline")
        outline_path = self.root / str(outline_relative or "")
        if not outline_path.exists():
            return

        expected: list[tuple[int, str]] = []
        current_loop: int | None = None
        for line in outline_path.read_text(encoding="utf-8").splitlines():
            loop_match = re.match(r"^# Loop (\d+)", line)
            if loop_match:
                current_loop = int(loop_match.group(1))
                continue
            marker_match = re.match(r"^\s*-\s*⚪\s*(.+?)\s*$", line)
            if (
                current_loop is not None
                and marker_match
                and not marker_match.group(1).startswith("证词：")
            ):
                expected.append((current_loop, marker_match.group(1)))

        actual: list[tuple[int, str]] = []
        marker_rows: list[tuple[int, dict]] = []
        for loop_number, state in self.states.items():
            for row in state.get("outline_coverage", []):
                if row.get("testimony_required") is True:
                    source_text = str(row.get("source_text", "")).strip()
                    actual.append((loop_number, source_text))
                    marker_rows.append((loop_number, row))

        if Counter(actual) != Counter(expected):
            missing = list((Counter(expected) - Counter(actual)).elements())
            extra = list((Counter(actual) - Counter(expected)).elements())
            self.errors.append(
                "outline testimony marker coverage mismatch; "
                f"missing={missing!r}, extra={extra!r}"
            )

        for loop_number, row in marker_rows:
            inline_by_id: dict[int, dict] = {}

            def collect_inline(value: Any) -> None:
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key == "testimony_ids" and isinstance(child, list):
                            for entry in child:
                                if (
                                    isinstance(entry, dict)
                                    and isinstance(entry.get("id"), int)
                                ):
                                    inline_by_id[entry["id"]] = entry
                        else:
                            collect_inline(child)
                elif isinstance(value, list):
                    for child in value:
                        collect_inline(child)

            collect_inline(self.states[loop_number])
            testimony = inline_by_id.get(row.get("testimony_id"))
            if not testimony:
                self.errors.append(
                    f"loop{loop_number} outline testimony marker is not bound to "
                    f"an inline testimony: {row.get('marker_id')}"
                )
                continue
            if (
                row.get("verbatim_required") is True
                and str(testimony.get("content", "")).strip()
                != str(row.get("source_text", "")).strip()
            ):
                self.errors.append(
                    f"loop{loop_number} outline testimony content is not verbatim: "
                    f"{row.get('marker_id')}"
                )
            if (
                row.get("mapping") != "merged"
                and str(testimony.get("source_anchor", "")).strip()
                != str(row.get("source_anchor", "")).strip()
            ):
                self.errors.append(
                    f"loop{loop_number} outline testimony source anchor is missing "
                    f"or mismatched: {row.get('marker_id')}"
                )

    def _validate_dialogue_evidence_acquisition(self) -> None:
        for loop_number, state in self.states.items():
            registry = {
                entry.get("id"): entry
                for entry in state.get("evidence_registry", [])
            }
            carriers: dict[str, list[tuple[str, dict]]] = {}

            def add_carrier(talk: Any, carrier: str, data: dict) -> None:
                if talk:
                    carriers.setdefault(str(talk), []).append((carrier, data))

            for event in state.get("opening", {}).get("sequence", []) or []:
                add_carrier(event.get("talk"), "opening", event)
            for scene in state.get("scenes", []):
                npcs = scene.get("npcs", {}) or {}
                for npc in npcs.values():
                    add_carrier(npc.get("talk"), "npc", npc)
                for event in scene.get("event_triggers", []) or []:
                    add_carrier(event.get("talk"), "event_trigger", event)

            post_expose = state.get("expose", {}).get("post_expose", {})
            add_carrier(post_expose.get("talk"), "post_expose", post_expose)

            scene_evidence: dict[int, dict] = {}
            for scene in state.get("scenes", []):
                for evidence in scene.get("evidence", []) or []:
                    evidence_id = evidence.get("id")
                    if isinstance(evidence_id, int):
                        scene_evidence[evidence_id] = evidence
                    acquisition = evidence.get("acquisition", {})
                    if not acquisition:
                        continue
                    # Minigame outputs are created by a gameplay flow rather than
                    # granted by a Talk carrier. Their source contract is checked
                    # separately in the Unit4-specific validation below.
                    if acquisition.get("kind") == "minigame_output":
                        if registry.get(evidence_id, {}).get("acquisition") != acquisition:
                            self.errors.append(
                                f"loop{loop_number} minigame evidence acquisition is mismatched: {evidence_id}"
                            )
                        continue
                    talk = acquisition.get("talk")
                    registry_acquisition = registry.get(evidence_id, {}).get(
                        "acquisition"
                    )
                    matching_carriers = carriers.get(str(talk), [])
                    expected_carrier = acquisition.get("carrier")
                    if expected_carrier:
                        matching_carriers = [
                            pair
                            for pair in matching_carriers
                            if pair[0] == expected_carrier
                        ]
                    if not matching_carriers or not any(
                        evidence_id in (data.get("grants_evidence") or [])
                        for _, data in matching_carriers
                    ) or registry_acquisition != acquisition:
                        self.errors.append(
                            f"loop{loop_number} dialogue evidence acquisition is invalid: {evidence_id}"
                        )

            for evidence_id, entry in registry.items():
                if (
                    isinstance(entry.get("acquisition"), dict)
                    and evidence_id not in scene_evidence
                ):
                    self.errors.append(
                        f"loop{loop_number} registry acquisition has no scene evidence: {evidence_id}"
                    )

    @staticmethod
    def _normalize_evidence_name(value: Any) -> str:
        return re.sub(r"\s+", "", str(value or "")).strip()

    def _outline_dialogue_evidence(self) -> list[tuple[int, str, str]]:
        outline_relative = self.contract.get("canon_source", {}).get("active_outline")
        outline_path = self.root / str(outline_relative or "")
        if not outline_path.exists():
            return []

        results: list[tuple[int, str, str]] = []
        current_loop: int | None = None
        current_evidence: str | None = None
        current_npc: str | None = None
        dialogue_block_actor: str | None = None
        dialogue_block_indent: int | None = None
        evidence_pattern = re.compile(
            r"^\s*(?:#{1,6}\s+|-\s+)(?:[🟢🔵🟣🧪🔒]+\s*)+(.+?)\s*$"
        )
        for line in outline_path.read_text(encoding="utf-8").splitlines():
            indent = len(line) - len(line.lstrip())
            loop_match = re.match(r"^# Loop (\d+)", line)
            if loop_match:
                current_loop = int(loop_match.group(1))
                current_evidence = None
                current_npc = None
                dialogue_block_actor = None
                dialogue_block_indent = None
                continue
            npc_match = re.search(r"👤 NPC[：:]\s*(.+?)\s*$", line)
            if npc_match:
                current_npc = npc_match.group(1).strip()
                current_evidence = None
                dialogue_block_actor = None
                dialogue_block_indent = None
                continue
            if re.search(r"对话获取[：:]\s*$", line):
                dialogue_block_actor = current_npc
                dialogue_block_indent = indent
                current_evidence = None
                continue
            if (
                dialogue_block_indent is not None
                and line.strip()
                and indent <= dialogue_block_indent
            ):
                dialogue_block_actor = None
                dialogue_block_indent = None
            evidence_match = evidence_pattern.match(line)
            if evidence_match:
                current_evidence = evidence_match.group(1).strip()
                if current_loop and dialogue_block_actor:
                    results.append(
                        (current_loop, current_evidence, dialogue_block_actor)
                    )
                continue
            if re.match(r"^\s*(?:#{1,6}\s+|-\s+)(?:⚪|👤|🟡|💡)", line):
                current_evidence = None
                continue
            acquisition_match = re.search(r"获取方式：对话获取｜(.+?)\s*$", line)
            if current_loop and current_evidence and acquisition_match:
                actor = re.split(r"[（(]", acquisition_match.group(1).strip(), 1)[0]
                results.append((current_loop, current_evidence, actor.strip()))
        return results

    def _validate_evidence_delivery_coverage(self) -> None:
        policy = (
            self.contract.get("outline_coverage_contract", {})
            .get("evidence_delivery_policy", {})
        )
        required_fields = set(policy.get("required_fields", []))
        coverage_by_loop: dict[int, dict[int, dict]] = {}

        for loop_number, state in self.states.items():
            rows: dict[int, dict] = {}
            for row in state.get("outline_coverage", []) or []:
                if row.get("evidence_delivery_required") is not True:
                    continue
                missing = sorted(field for field in required_fields if field not in row)
                if missing:
                    self.errors.append(
                        f"loop{loop_number} evidence delivery coverage lacks fields: {missing!r}"
                    )
                evidence_id = row.get("evidence_id")
                if not isinstance(evidence_id, int):
                    self.errors.append(
                        f"loop{loop_number} evidence delivery coverage has invalid ID: {evidence_id!r}"
                    )
                    continue
                if evidence_id in rows:
                    self.errors.append(
                        f"loop{loop_number} duplicate evidence delivery coverage: {evidence_id}"
                    )
                rows[evidence_id] = row
            coverage_by_loop[loop_number] = rows

            registry = {
                entry.get("id"): entry
                for entry in state.get("evidence_registry", [])
            }
            scene_evidence = {
                evidence.get("id"): evidence
                for scene in state.get("scenes", [])
                for evidence in (scene.get("evidence", []) or [])
            }
            for evidence_id, row in rows.items():
                expected = {
                    "kind": row.get("acquisition_kind"),
                    "talk": row.get("acquisition_talk"),
                }
                if row.get("acquisition_carrier"):
                    expected["carrier"] = row.get("acquisition_carrier")
                if (
                    registry.get(evidence_id, {}).get("acquisition") != expected
                    or scene_evidence.get(evidence_id, {}).get("acquisition") != expected
                ):
                    self.errors.append(
                        f"loop{loop_number} evidence delivery coverage does not match acquisition: {evidence_id}"
                    )

            declared_acquisitions = {
                evidence_id
                for evidence_id, evidence in scene_evidence.items()
                if evidence.get("acquisition")
                and evidence.get("acquisition", {}).get("kind") != "minigame_output"
            }
            missing_coverage = sorted(declared_acquisitions - set(rows))
            if missing_coverage:
                self.errors.append(
                    f"loop{loop_number} acquired evidence lacks delivery coverage: {missing_coverage!r}"
                )

        for loop_number, evidence_name, actor in self._outline_dialogue_evidence():
            state = self.states.get(loop_number, {})
            registry = state.get("evidence_registry", []) or []
            normalized = self._normalize_evidence_name(evidence_name)
            entry = next(
                (
                    candidate
                    for candidate in registry
                    if self._normalize_evidence_name(candidate.get("name")) == normalized
                ),
                None,
            )
            if not entry:
                self.errors.append(
                    f"loop{loop_number} outline dialogue evidence is missing from registry: {evidence_name}"
                )
                continue
            evidence_id = entry.get("id")
            acquisition = entry.get("acquisition", {})
            if acquisition.get("kind") != "dialogue" or not acquisition.get("talk"):
                self.errors.append(
                    f"loop{loop_number} outline dialogue evidence lacks dialogue acquisition: {evidence_id} ({actor})"
                )
            if evidence_id not in coverage_by_loop.get(loop_number, {}):
                self.errors.append(
                    f"loop{loop_number} outline dialogue evidence lacks coverage: {evidence_id}"
                )

        expected_names: dict[int, set[str]] = {}
        for loop_number, evidence_name, _ in self._outline_dialogue_evidence():
            expected_names.setdefault(loop_number, set()).add(
                self._normalize_evidence_name(evidence_name)
            )
        for loop_number, state in self.states.items():
            for entry in state.get("evidence_registry", []) or []:
                acquisition = entry.get("acquisition")
                if not isinstance(acquisition, dict) or acquisition.get("kind") != "dialogue":
                    continue
                if self._normalize_evidence_name(entry.get("name")) not in expected_names.get(
                    loop_number, set()
                ):
                    self.errors.append(
                        f"loop{loop_number} dialogue acquisition lacks explicit outline source: {entry.get('id')}"
                    )

    def _validate_runtime_events(self) -> None:
        contract = self.contract.get("runtime_event_contract", {})
        allowed_adapters = set(contract.get("special_adapters", []))
        allowed_actions = set(contract.get("allowed_runtime_actions", []))

        for loop_number, state in self.states.items():
            registry_ids = {
                entry.get("id") for entry in state.get("evidence_registry", [])
            }
            next_talk_sources: dict[str, list[str]] = {}

            def collect_runtime_exits(value: Any, path: str) -> None:
                if isinstance(value, dict):
                    for key, child in value.items():
                        child_path = f"{path}.{key}" if path else str(key)
                        if key == "runtime_exit" and isinstance(child, dict):
                            action = child.get("action")
                            if action and action not in allowed_actions:
                                self.errors.append(
                                    f"loop{loop_number} unsupported runtime action at {child_path}: {action}"
                                )
                            next_talk = child.get("next_talk")
                            if next_talk:
                                next_talk_sources.setdefault(str(next_talk), []).append(
                                    child_path
                                )
                        collect_runtime_exits(child, child_path)
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        collect_runtime_exits(child, f"{path}[{index}]")

            collect_runtime_exits(state, f"loop{loop_number}")

            event_talks: dict[str, list[dict]] = {}
            for scene in state.get("scenes", []) or []:
                if scene.get("type") == "cutscene":
                    for npc in (scene.get("npcs") or {}).values():
                        if npc.get("talk"):
                            self.errors.append(
                                f"loop{loop_number} cutscene {scene.get('id')} has free NPC Talk"
                            )
                for event in scene.get("event_triggers", []) or []:
                    talk = event.get("talk")
                    if talk:
                        event_talks.setdefault(str(talk), []).append(event)
                    if event.get("forced") is True:
                        binding = event.get("runtime_binding", {})
                        adapter = binding.get("adapter")
                        if not adapter:
                            self.errors.append(
                                f"loop{loop_number} forced event lacks runtime binding: {event.get('id')}"
                            )
                        elif adapter == contract.get("scene_enter_adapter"):
                            required_ids = binding.get(
                                contract.get("scene_enter_required_field"), []
                            )
                            if not required_ids or any(
                                evidence_id not in registry_ids
                                for evidence_id in required_ids
                            ):
                                self.errors.append(
                                    f"loop{loop_number} scene-enter event has invalid required item IDs: {event.get('id')}"
                                )
                        elif adapter not in allowed_adapters:
                            self.errors.append(
                                f"loop{loop_number} forced event uses unsupported adapter: {event.get('id')}"
                            )
                        elif adapter == "ordered_story_event":
                            condition = event.get("condition", {})
                            all_of = (
                                condition.get("all_of", {})
                                if isinstance(condition, dict)
                                else {}
                            )
                            if (
                                not all_of.get("required_talks")
                                or not all_of.get("required_item_ids")
                            ):
                                self.errors.append(
                                    f"loop{loop_number} ordered story event lacks fixed prerequisites: {event.get('id')}"
                                )
                        elif adapter == "chained_talk" and not binding.get(
                            "previous_talk"
                        ):
                            self.errors.append(
                                f"loop{loop_number} chained event lacks previous Talk: {event.get('id')}"
                            )

            for talk, events in event_talks.items():
                if len(events) > 1:
                    self.errors.append(
                        f"loop{loop_number} event Talk has multiple trigger entries: {talk}"
                    )
                if talk in next_talk_sources:
                    event = events[0]
                    binding = event.get("runtime_binding", {})
                    if binding.get("adapter") != "chained_talk":
                        self.errors.append(
                            f"loop{loop_number} event Talk is both chained and independently triggered: {talk}"
                        )

            for ending_scene in (
                state.get("ending_sequence", {}).get("scenes", []) or []
            ):
                if ending_scene.get("npcs"):
                    self.errors.append(
                        f"loop{loop_number} ending scene {ending_scene.get('id')} has free NPC Talk data"
                    )


    def _validate_continuity(self) -> None:
        contract = self.contract.get("narrative_continuity_contract", {})
        required_fields = set(contract.get("required_fields", []))
        approved_external = set(contract.get("approved_external_handoffs", []))
        units: list[tuple[int, dict]] = []
        for loop_number, state in self.states.items():
            entries = state.get("narrative_continuity")
            if not isinstance(entries, list) or not entries:
                self.errors.append(f"loop{loop_number} narrative continuity is missing")
                continue
            units.extend((loop_number, unit) for unit in entries)

        ids = [unit.get("id") for _, unit in units]
        if None in ids or len(ids) != len(set(ids)):
            self.errors.append("narrative continuity IDs must be globally unique")
        known_targets = set(ids) | approved_external

        covered_by_loop: dict[int, set[str]] = {loop_number: set() for loop_number in self.states}
        for loop_number, unit in units:
            missing = sorted(field for field in required_fields if field not in unit)
            if missing:
                self.errors.append(
                    f"loop{loop_number} continuity unit {unit.get('id')} lacks fields: {missing!r}"
                )
            handoff = unit.get("hands_off_to")
            if handoff not in known_targets:
                self.errors.append(
                    f"loop{loop_number} dangling handoff from {unit.get('id')} to {handoff}"
                )
            covered_by_loop[loop_number].update(unit.get("covers", []) or [])

        for loop_number, state in self.states.items():
            required = {
                f"opening.sequence.{event.get('event_id')}"
                for event in state.get("opening", {}).get("sequence", [])
            }
            required.update({"expose", "expose.post_expose"})
            if loop_number == 5:
                required.update(
                    f"ending_sequence.{scene.get('id')}"
                    for scene in state.get("ending_sequence", {}).get("scenes", [])
                )
            missing = sorted(required - covered_by_loop[loop_number])
            if missing:
                self.errors.append(
                    f"loop{loop_number} continuity coverage is missing: {missing!r}"
                )

    def _validate_identity_lock(self) -> None:
        expected = self.contract.get("identity_lock", {})
        state = self.states.get(expected.get("loop"), {})
        identity = state.get("special_mechanics", {}).get("identity_lock")
        if not identity:
            self.errors.append("loop5 identity_lock is missing")
            return
        if identity.get("replaces_standard_doubts") is not True or "doubts" in state:
            self.errors.append("loop5 identity_lock must replace ordinary doubts")
        if identity.get("status") != expected.get("status"):
            self.errors.append("identity_lock status mismatch")
        chains = identity.get("chains", [])
        if [chain.get("id") for chain in chains] != expected.get("chain_ids"):
            self.errors.append("identity_lock chain IDs mismatch")
        gate = identity.get("gate_contract", {})
        if (
            gate.get("completion_condition") != expected.get("completion_condition")
            or gate.get("unlocks") != expected.get("unlocks")
            or gate.get("standard_doubt_progress_required")
            != expected.get("standard_doubt_progress_required")
        ):
            self.errors.append("identity_lock gate contract mismatch")
        office = next(
            (scene for scene in state.get("scenes", []) if scene.get("id") == 4042),
            {},
        )
        returns = next(
            (
                trigger
                for trigger in office.get("event_triggers", [])
                if trigger.get("id") == "mickey_returns"
            ),
            {},
        )
        if returns.get("condition") != expected.get("mickey_returns_condition"):
            self.errors.append("mickey_returns condition mismatch")
        if (
            returns.get("talk") != expected.get("mickey_returns_talk")
            or expected.get("mickey_returns_testimony")
            not in (returns.get("grants_testimony") or [])
            or returns.get("runtime_binding", {}).get("adapter") != "identity_lock"
        ):
            self.errors.append("mickey_returns forced Talk contract mismatch")
        if (office.get("npcs") or {}):
            self.errors.append("loop5 Mickey return must not be a free NPC Talk")
        if state.get("expose", {}).get("unlock_condition") != expected.get(
            "expose_unlock_condition"
        ):
            self.errors.append("loop5 expose unlock condition mismatch")

    def _validate_persistence(self) -> None:
        loop5 = self.states.get(5, {})
        for rule in self.contract.get("persistent_inputs", []):
            source = self.states.get(rule.get("source_loop"), {})
            if rule.get("registry") == "inline_testimony":
                inline_entries: list[dict] = []

                def collect_inline(value: Any) -> None:
                    if isinstance(value, dict):
                        for key, child in value.items():
                            if key == "testimony_ids" and isinstance(child, list):
                                inline_entries.extend(
                                    candidate
                                    for candidate in child
                                    if isinstance(candidate, dict)
                                )
                            else:
                                collect_inline(child)
                    elif isinstance(value, list):
                        for child in value:
                            collect_inline(child)

                collect_inline(source)
                entry = next(
                    (
                        candidate
                        for candidate in inline_entries
                        if candidate.get("id") == rule.get("id")
                    ),
                    None,
                )
            else:
                entry = next(
                    (
                        candidate
                        for candidate in source.get(rule.get("registry"), [])
                        if candidate.get("id") == rule.get("id")
                    ),
                    None,
                )
            if not entry:
                self.errors.append(f"persistence source missing: {rule.get('id')}")
                continue
            persistence = entry.get("persistence", {})
            if (
                persistence.get("scope") != "chapter"
                or persistence.get("reset_policy") != "retain_across_loops"
                or persistence.get("required_by") != rule.get("required_by")
            ):
                self.errors.append(f"persistence contract mismatch: {rule.get('id')}")

            inherited = next(
                (
                    candidate
                    for candidate in loop5.get("evidence_registry", [])
                    if candidate.get("id") == rule.get("id")
                ),
                None,
            )
            if not inherited or inherited.get("inherited") is not True:
                self.errors.append(f"loop5 inherited persistence missing: {rule.get('id')}")

    def _validate_non_progress_records(self) -> None:
        rule = self.contract.get("non_progress_records", {})
        loop_number = rule.get("loop")
        state = self.states.get(loop_number, {})
        records = state.get("non_progress_investigation_records", [])
        if [record.get("id") for record in records] != rule.get("ids"):
            self.errors.append("non-progress record IDs mismatch")
        for record in records:
            if record.get("presentation") != rule.get("presentation"):
                self.errors.append(
                    f"non-progress record presentation mismatch: {record.get('id')}"
                )
        if "doubt_progress" in state:
            self.errors.append("non-progress records must not enter ordinary doubt progress")
        prohibited = list(scalar_values([state.get("doubts"), state.get("expose", {}).get("unlock_condition")]))
        for record_id in rule.get("ids", []):
            if record_id in prohibited:
                self.errors.append(
                    f"non-progress record enters ordinary progress: {record_id}"
                )

    def _validate_ending(self) -> None:
        expected = self.contract.get("ending_sequence", {})
        state = self.states.get(expected.get("owner_loop"), {})
        ending = state.get("ending_sequence", {})
        runtime = ending.get("runtime_contract", {})
        checks = {
            "counts_as_loop": expected.get("counts_as_loop"),
            "inherit_loop": expected.get("owner_loop"),
            "chapter_end_after": expected.get("chapter_end_after"),
            "next_unit_entry": expected.get("next_unit_entry"),
        }
        for key, value in checks.items():
            if runtime.get(key) != value:
                self.errors.append(f"ending runtime contract mismatch: {key}")

        scenes = ending.get("scenes", [])
        if [scene.get("id") for scene in scenes] != [
            "ending_4043",
            "ending_4044",
            "ending_4045",
        ]:
            self.errors.append("ending sequence scene order mismatch")
        if len(scenes) == 3:
            post_expose = state.get("expose", {}).get("post_expose", {})
            post_exit = post_expose.get("runtime_exit", {})
            if (
                post_exit.get("action") != "change_scene"
                or post_exit.get("target_scene_id") != scenes[0].get("scene_id")
                or post_exit.get("continuation") != "next_talk"
                or post_exit.get("next_talk") != expected.get("entry_talk")
                or "player_control_restored_after" in post_expose
            ):
                self.errors.append("ending sequence has no unique post-expose entry")
            if scenes[0].get("runtime_exit", {}).get("next_talk") != scenes[1].get("talk"):
                self.errors.append("ending_4043 handoff mismatch")
            if scenes[1].get("runtime_exit", {}).get("next_talk") != scenes[2].get("talk"):
                self.errors.append("ending_4044 handoff mismatch")
            final = scenes[2]
            if (
                final.get("hard_stop") is not True
                or "门外" not in str(final.get("final_frame", ""))
                or final.get("runtime_exit", {}).get("action")
                != expected.get("final_runtime_action")
                or final.get("runtime_exit", {}).get("next_unit_entry")
                != expected.get("next_unit_entry")
            ):
                self.errors.append("ending_4045 must hard-stop outside O'Hara's house")

        if (
            ending.get("unit4_to_unit5_boundary", {}).get("unit5_first_allowed_action")
            != expected.get("unit5_first_allowed_action")
        ):
            self.errors.append("unit5 first allowed action mismatch")

    def _validate_evidence_types(self) -> None:
        for loop_number, state in self.states.items():
            for evidence in state.get("evidence_registry", []):
                if evidence.get("type") == "clue" and evidence.get("analysis") is True:
                    self.errors.append(
                        f"loop{loop_number} clue cannot be analyzed: {evidence.get('id')}"
                    )

    def _validate_expose_evidence_coverage(self) -> None:
        expected = self.contract.get("expose_evidence_contract", {})
        expected_policy = expected.get("lie_source_policy", {})
        for loop_number, state in self.states.items():
            expose = state.get("expose", {})
            semantics = expose.get("lie_source_semantics", {})
            actual_round_1 = semantics.get("round_1", {})
            actual_later = semantics.get("later_rounds", {})
            expected_round_1 = expected_policy.get("round_1", {})
            expected_later = expected_policy.get("later_rounds", {})
            if (
                actual_round_1.get("kind") != expected_round_1.get("kind")
                or actual_round_1.get("collectible_testimony")
                != expected_round_1.get("collectible_testimony")
                or actual_later.get("kind") != expected_later.get("kind")
                or actual_later.get("collectible_testimony")
                != expected_later.get("collectible_testimony")
                or semantics.get("requires_doubt_condition")
                != expected.get("lie_source_requires_doubt_condition")
            ):
                self.errors.append(
                    f"loop{loop_number} Expose lie_source semantics mismatch"
                )

            covered: set[int] = set()
            for doubt in state.get("doubts", []):
                for condition in doubt.get("unlock_condition", []) or []:
                    param = condition.get("param")
                    if str(param).isdigit():
                        covered.add(int(param))
            if loop_number == 5:
                for chain in (
                    state.get("special_mechanics", {})
                    .get("identity_lock", {})
                    .get("chains", [])
                ):
                    covered.update(
                        int(item["id"])
                        for item in chain.get("inputs", [])
                        if str(item.get("id", "")).isdigit()
                    )

            rounds = expose.get("rounds")
            if rounds is None:
                rounds = [expose.get(f"round_{index}") for index in range(1, 4)]
            used = {
                int(item["id"])
                for round_data in rounds
                if round_data
                for item in round_data.get("usable_evidence", [])
                if str(item.get("id", "")).isdigit()
            }
            missing = sorted(used - covered)
            if missing:
                self.errors.append(
                    f"loop{loop_number} Expose usable evidence is not loaded by a doubt or identity chain: {missing!r}"
                )

    def _validate_unit4_specific_content(self) -> None:
        loop1 = self.states.get(1, {})
        loop1_scenes = {scene.get("id"): scene for scene in loop1.get("scenes", [])}
        loop1_registry = {
            entry.get("id"): entry for entry in loop1.get("evidence_registry", [])
        }
        evidence_4111 = loop1_registry.get(4111, {})
        acquisition_4111 = evidence_4111.get("acquisition", {}) or {}
        if evidence_4111.get("first_scene") != 4003 or evidence_4111.get("pickup") is not False:
            self.errors.append("4111 must be a non-pickup minigame result first generated in scene 4003")
        if acquisition_4111.get("kind") != "minigame_output":
            self.errors.append("4111 acquisition must be minigame_output")
        if set(acquisition_4111.get("formal_input_ids", []) or []) != {4115}:
            self.errors.append("4111 minigame must use 4115 as its only formal Item input")
        if set(acquisition_4111.get("auxiliary_page_ids", []) or []) != {4122, 4123}:
            self.errors.append("4111 minigame must keep 4122/4123 as auxiliary pages")
        scene_4002_ids = {
            item.get("id") for item in loop1_scenes.get(4002, {}).get("evidence", []) or []
        }
        scene_4003_ids = {
            item.get("id") for item in loop1_scenes.get(4003, {}).get("evidence", []) or []
        }
        if 4111 in scene_4002_ids or 4111 not in scene_4003_ids:
            self.errors.append("4111 must be generated at the scene 4003 archive table, not scene 4002")
        if {4122, 4123} & set(loop1_registry):
            self.errors.append("4122/4123 must remain minigame-only pages outside evidence_registry")

        loop3 = self.states.get(3, {})
        loop3_scenes = {scene.get("id"): scene for scene in loop3.get("scenes", [])}
        required_loop3_scenes = {4021, 4029, 4027, 4022, 4028, 4023, 4024, 4025, 4026}
        missing_loop3_scenes = sorted(required_loop3_scenes - set(loop3_scenes))
        if missing_loop3_scenes:
            self.errors.append(
                f"loop3 split mansion scene mapping is incomplete: {missing_loop3_scenes!r}"
            )

        kitchen = loop3_scenes.get(4028, {})
        kitchen_gate = set((kitchen.get("access", {}) or {}).get("required_item_ids", []) or [])
        if kitchen_gate != {4311, 4312, 4313, 4314, 4315}:
            self.errors.append("loop3 scene 4028 must be gated by evidence 4311-4315")

        kitchen_events = {
            event.get("id"): event for event in kitchen.get("event_triggers", []) or []
        }
        explosion = kitchen_events.get("mansion_evacuation_and_explosion", {})
        flow_contract = self.contract.get("loop3_flow_contract", {}) or {}
        explosion_all_of = (explosion.get("condition", {}) or {}).get("all_of", {}) or {}
        explosion_items = set(explosion_all_of.get("required_item_ids", []) or [])
        expected_explosion_items = set(
            flow_contract.get(
                "explosion_required_item_ids",
                [4316, 4321, 4322, 4317, 4318, 4319, 4320],
            )
        )
        if explosion_items != expected_explosion_items:
            self.errors.append(
                "loop3 explosion ordered gate must require mansion and all pre-blast external materials"
            )
        explosion_talks = set(explosion_all_of.get("required_talks", []) or [])
        expected_explosion_talks = set(
            flow_contract.get("explosion_required_talks", ["L3_scene4024_operator"])
        )
        if explosion_talks != expected_explosion_talks:
            self.errors.append("loop3 explosion ordered gate must require the scene 4024 operator Talk")
        if (explosion.get("runtime_binding", {}) or {}).get("adapter") != flow_contract.get(
            "explosion_adapter", "ordered_story_event"
        ):
            self.errors.append("loop3 explosion must use the ordered_story_event adapter")
        if "pierce_arrives_outer_perimeter" not in str(explosion.get("condition", {})):
            self.errors.append("loop3 explosion must preserve Pierce's pre-blast arrival state")

        for scene_id in set(flow_contract.get("pre_blast_scene_ids", [4024, 4025, 4026])):
            if "pre_blast" not in set(loop3_scenes.get(scene_id, {}).get("design_tags", []) or []):
                self.errors.append(f"loop3 scene {scene_id} must be marked pre_blast")
        for scene_id in set(flow_contract.get("post_blast_scene_ids", [4023])):
            if "post_blast" not in set(loop3_scenes.get(scene_id, {}).get("design_tags", []) or []):
                self.errors.append(f"loop3 scene {scene_id} must be marked post_blast")

        scene_4023_ids = {
            item.get("id") for item in loop3_scenes.get(4023, {}).get("evidence", []) or []
        }
        scene_4025_items = {
            item.get("id"): item
            for item in loop3_scenes.get(4025, {}).get("evidence", []) or []
        }
        key_item = scene_4025_items.get(4317, {})
        if 4317 in scene_4023_ids or not key_item:
            self.errors.append("loop3 evidence 4317 must be in scene 4025 and absent from scene 4023")
        old_key_phrases = ("爆炸从", "带车站标记", "铁路车站标记", "Morrison 的衣物")
        if any(phrase in str(key_item.get("description", "")) for phrase in old_key_phrases):
            self.errors.append("loop3 evidence 4317 must only show 214 and must not retain blast/station-mark origin")

        station = loop3_scenes.get(4026, {})
        if station.get("unlock_item") is not None or "locked" in set(station.get("design_tags", []) or []):
            self.errors.append("loop3 scene 4026 must stay open; 4317 may lock only the 214 container")
        if not (station.get("access", {}) or {}).get("always_open"):
            self.errors.append("loop3 scene 4026 must declare always_open access")
        locker = next(
            (
                interaction
                for interaction in station.get("interactions", []) or []
                if interaction.get("id")
                == flow_contract.get("locked_container_interaction", "interaction_station_locker_214")
            ),
            {},
        )
        if str(locker.get("visible_number_range", "")) != str(
            flow_contract.get("visible_locker_range", "210-220")
        ):
            self.errors.append("loop3 scene 4026 must preview the continuous 210-220 locker range")
        if set(locker.get("required_item_ids", []) or []) != {4317} or set(
            locker.get("outputs", []) or []
        ) != {4320}:
            self.errors.append("loop3 scene 4026 locker 214 must require 4317 and output 4320")

        pre_doris = (loop3_scenes.get(4027, {}).get("npcs", {}) or {}).get(
            "L3_scene4027_doris", {}
        )
        post_doris = (loop3_scenes.get(4023, {}).get("npcs", {}) or {}).get(
            "L3_scene4023_doris", {}
        )
        pre_doris_ids = {
            entry.get("id") for entry in pre_doris.get("testimony_ids", []) or []
        }
        post_doris_entries = {
            entry.get("id"): entry for entry in post_doris.get("testimony_ids", []) or []
        }
        lie_entry = post_doris_entries.get(4063003, {})
        if 4063003 in pre_doris_ids or not lie_entry:
            self.errors.append("loop3 testimony 4063003 must move from scene 4027 to scene 4023 Doris")
        if lie_entry.get("acquisition_talk") != flow_contract.get(
            "post_blast_lie_talk", "L3_scene4023_doris"
        ):
            self.errors.append("loop3 testimony 4063003 must be acquired in the scene 4023 Doris Talk")

        doubt_4301 = next(
            (doubt for doubt in loop3.get("doubts", []) or [] if doubt.get("id") == 4301),
            {},
        )
        doubt_4301_conditions = {
            int(condition.get("param"))
            for condition in doubt_4301.get("unlock_condition", []) or []
            if str(condition.get("param", "")).isdigit()
        }
        if doubt_4301_conditions != set(
            flow_contract.get("first_doubt_conditions", [4063003, 4153001])
        ):
            self.errors.append("loop3 doubt 4301 must require 4063003 and 4153001")

        loop3_registry = {
            entry.get("id"): entry for entry in loop3.get("evidence_registry", [])
        }
        expected_first_scenes = {
            4314: 4027,
            4315: 4027,
            4316: 4028,
            4317: 4025,
            4321: 4028,
            4322: 4028,
        }
        for evidence_id, scene_id in expected_first_scenes.items():
            if loop3_registry.get(evidence_id, {}).get("first_scene") != scene_id:
                self.errors.append(
                    f"loop3 evidence {evidence_id} must first appear in scene {scene_id}"
                )
        if "静态现场记录" not in str(loop3_registry.get(4316, {}).get("note", "")):
            self.errors.append("4316 must remain a single static pre-blast evidence record")

        loop4 = self.states.get(4, {})
        loop4_scenes = {scene.get("id"): scene for scene in loop4.get("scenes", [])}
        ohara_home = loop4_scenes.get(4033, {})
        stop_event = next(
            (
                event
                for event in ohara_home.get("event_triggers", []) or []
                if event.get("id") == "stop_order_application_and_delivery"
            ),
            {},
        )
        stop_all_of = (stop_event.get("condition", {}) or {}).get("all_of", {}) or {}
        if set(stop_all_of.get("required_talks", []) or []) != {
            "L4_scene4032_ohara",
            "L4_scene4033_sarah",
        }:
            self.errors.append("loop4 stop order must require O'Hara Talk and Sarah Talk")
        if set(stop_all_of.get("required_item_ids", []) or []) != {4411, 4412, 4413}:
            self.errors.append("loop4 stop order must require 4411, 4412, 4413")

        loop5_text = "\n".join(str(value) for value in scalar_values(self.states.get(5, {})))
        if "夜班门房" in loop5_text:
            self.errors.append("loop5 night doorman is forbidden by the active outline")

        loop5 = self.states.get(5, {})
        scene_4041 = next(
            (scene for scene in loop5.get("scenes", []) if scene.get("id") == 4041),
            None,
        )
        if scene_4041 is None:
            self.errors.append("loop5 scene 4041 noninteractive establishing shot is required")
        else:
            if scene_4041.get("type") != "cutscene":
                self.errors.append("loop5 scene 4041 must be a cutscene")
            if scene_4041.get("evidence"):
                self.errors.append("loop5 scene 4041 must not grant evidence")
            if scene_4041.get("npcs"):
                self.errors.append("loop5 scene 4041 must not expose NPC interactions")

        opening = loop5.get("opening", {})
        sequence = opening.get("sequence", []) or []
        first_event = sequence[0] if sequence else {}
        runtime_exit = first_event.get("runtime_exit", {}) or {}
        if opening.get("runtime_root", {}).get("init_scene") != 4041:
            self.errors.append("loop5 opening init_scene must be 4041")
        if first_event.get("scene_id") != 4041:
            self.errors.append("loop5 opening first event must be bound to scene 4041")
        if runtime_exit.get("action") != "change_scene" or runtime_exit.get("target_scene_id") != 4042:
            self.errors.append("loop5 scene 4041 must transition directly to scene 4042")
        if runtime_exit.get("continuation") != "release_to_exploration":
            self.errors.append("loop5 player control must be restored only after entering scene 4042")

        office_4042 = next(
            (scene for scene in loop5.get("scenes", []) if scene.get("id") == 4042),
            {},
        )
        letter_safe = next(
            (
                interaction
                for interaction in office_4042.get("interactions", []) or []
                if interaction.get("id") == "interaction_letter_safe"
            ),
            {},
        )
        if set(letter_safe.get("outputs", []) or []) != {4513, 4514, 4515, 4516}:
            self.errors.append("loop5 letter safe must grant 4513-4516 together")
        if letter_safe.get("atomic_outputs") is not True:
            self.errors.append("loop5 letter safe outputs must be atomic")

        identity_chains = (
            loop5.get("special_mechanics", {}).get("identity_lock", {}).get("chains", [])
        )
        visitor_chain = next(
            (chain for chain in identity_chains if chain.get("id") == 4503),
            {},
        )
        visitor_inputs = {entry.get("id") for entry in visitor_chain.get("inputs", []) or []}
        visitor_context = {
            entry.get("id") for entry in visitor_chain.get("prerequisite_context", []) or []
        }
        if visitor_inputs != {4315, 4512}:
            self.errors.append("loop5 visitor chain submission must contain only 4315 and 4512")
        if 4153001 not in visitor_context:
            self.errors.append("loop5 visitor chain must retain 4153001 as prerequisite context")

        registry = {
            entry.get("id"): entry for entry in loop5.get("evidence_registry", [])
        }
        expected_inherited_types = {
            4315: ("clue", 4027),
            4418: ("key_item", 4034),
            4704: ("derived_memory", 4034),
        }
        for evidence_id, (evidence_type, first_scene) in expected_inherited_types.items():
            entry = registry.get(evidence_id, {})
            if entry.get("type") != evidence_type or entry.get("first_scene") != first_scene:
                self.errors.append(
                    f"loop5 inherited evidence {evidence_id} must remain {evidence_type}/{first_scene}"
                )

        office_evidence = {
            entry.get("id"): entry for entry in office_4042.get("evidence", []) or []
        }
        for evidence_id in (4511, 4512, 4514, 4515):
            if office_evidence.get(evidence_id, {}).get("analysis") is True:
                self.errors.append(f"{evidence_id} must use identity-lock detail views, not standard analysis")
            if registry.get(evidence_id, {}).get("analysis") is True:
                self.errors.append(f"{evidence_id} registry entry must not enable standard analysis")

        if 4517 in registry:
            self.errors.append("4517 must not remain in the Unit4 evidence registry")
        for evidence_id in (4518, 4519):
            if "扣下" not in str(registry.get(evidence_id, {}).get("visibility", "")):
                self.errors.append(f"{evidence_id} concealment boundary is missing")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the formal Unit4 State v2 set")
    parser.add_argument(
        "--state-dir",
        default=str(DEFAULT_STATE_DIR),
        help="state directory relative to repository root",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    errors = Unit4StateV2Validator(root=root, state_dir=args.state_dir).validate()
    if errors:
        print("Unit4 State v2 contract: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS Unit4 State v2 contract validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
