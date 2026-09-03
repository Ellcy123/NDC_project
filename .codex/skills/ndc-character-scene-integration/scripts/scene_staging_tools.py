#!/usr/bin/env python3
"""Deterministic directing and staging helpers for NDC character integration.

The Unity-exported Talk.json and NPCLoopData.json files are JSON-like rather
than reliably strict JSON.  This module deliberately extracts only the fields
needed for cast lifecycle analysis instead of rewriting the source tables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFont


ENTER_SCRIPT = 13
EXIT_SCRIPT = 14
POSE_POINTS = (
    "neck",
    "leftShoulder",
    "rightShoulder",
    "leftElbow",
    "rightElbow",
    "leftHand",
    "rightHand",
    "leftHip",
    "rightHip",
    "leftKnee",
    "rightKnee",
    "leftFoot",
    "rightFoot",
)
CAPABILITY_BY_PLACEMENT = {
    "standing": "stand",
    "seated": "sit",
    "lying": "lie",
    "walking": "walk",
    "leaning": "lean",
}
ZONE_COLORS = {
    "walk": (42, 190, 105, 96),
    "stand": (54, 140, 255, 96),
    "sit": (255, 179, 0, 112),
    "lie": (172, 88, 255, 112),
    "lean": (0, 190, 190, 112),
    "occluder": (230, 64, 64, 112),
    "no-go": (90, 90, 90, 128),
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_fields(data: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")


def resolve_path(raw: str | Path, contract_path: Path | None = None) -> Path:
    path = Path(raw)
    if not path.is_absolute() and contract_path is not None:
        path = contract_path.parent / path
    return path.resolve()


def _record_blocks(text: str) -> list[str]:
    """Split pretty-printed table exports without parsing their malformed strings."""
    lines = text.splitlines()
    starts = [
        index
        for index, line in enumerate(lines)
        if line.strip() == "{" or line.strip() == "[{"
    ]
    blocks: list[str] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        block_lines = lines[start:end]
        if block_lines and block_lines[0].strip() == "[{":
            block_lines[0] = "{"
        blocks.append("\n".join(block_lines))
    return blocks


def _quoted_values(block: str, field: str) -> list[str]:
    pattern = re.compile(
        rf'(?m)^\s*"{re.escape(field)}"\s*:\s*"([^"\r\n]*)"'
    )
    return pattern.findall(block)


def _first_value(block: str, field: str, default: str = "") -> str:
    values = _quoted_values(block, field)
    return values[0] if values else default


def _last_value(block: str, field: str, default: str = "") -> str:
    values = _quoted_values(block, field)
    return values[-1] if values else default


def _section(block: str, field: str, next_fields: Iterable[str]) -> str:
    marker = re.search(rf'(?m)^\s*"{re.escape(field)}"\s*:\s*\{{', block)
    if not marker:
        return ""
    end = len(block)
    for next_field in next_fields:
        next_match = re.search(
            rf'(?m)^\s*"{re.escape(next_field)}"\s*:', block[marker.end() :]
        )
        if next_match:
            end = min(end, marker.end() + next_match.start())
    return block[marker.end() : end]


def _first_array_string(block: str, field: str) -> str:
    match = re.search(
        rf'(?m)^\s*"{re.escape(field)}"\s*:\s*\[\s*"([^"\r\n]*)"', block
    )
    return match.group(1) if match else ""


def parse_talk_table(path: Path) -> dict[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    records: dict[str, dict[str, Any]] = {}
    for block in _record_blocks(text):
        record_id = _first_value(block, "id")
        if not record_id:
            continue
        speaker_section = _section(
            block,
            "Speaker",
            ("Location", "isBlur", "Words", "script", "Parameters", "videoEpisode"),
        )
        parameter_ints = re.findall(
            r'"ParameterInt"\s*:\s*"([^"\r\n]*)"', block
        )
        records[record_id] = {
            "id": record_id,
            "step": _first_value(block, "step"),
            "next": _last_value(block, "next"),
            "script": int(_last_value(block, "script", "0") or 0),
            "parameterInts": parameter_ints,
            "speakerId": _first_value(speaker_section, "id"),
            "words": _first_array_string(block, "Words"),
            "videoScene": _last_value(block, "videoScene"),
            "isRight": _first_value(block, "isRight"),
        }
    return records


def parse_npc_loop_table(path: Path) -> dict[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    records: dict[str, dict[str, Any]] = {}
    for block in _record_blocks(text):
        loop_id = _first_value(block, "id")
        if not loop_id:
            continue
        npc_section = _section(block, "NPC", ("TalkInfo",))
        talk_section = _section(block, "TalkInfo", ("LoopTalkInfo",))
        loop_talk_section = _section(block, "LoopTalkInfo", ("IsinRight",))
        npc_id = _first_value(npc_section, "id")
        records[loop_id] = {
            "loopId": loop_id,
            "npcId": npc_id,
            "actorId": f"npc:{npc_id or loop_id}",
            "name": _first_array_string(npc_section, "Name"),
            "talkId": _first_value(talk_section, "id"),
            "loopTalkId": _first_value(loop_talk_section, "id"),
            "isInRight": _last_value(block, "IsinRight"),
            "resPath": _last_value(block, "ResPath").replace("\\", "/"),
            "clickResPath": _last_value(block, "ClickResPath").replace("\\", "/"),
            "shadowPath": _last_value(block, "ShadowPath").replace("\\", "/"),
            "position": [
                float(_last_value(block, "PosX", "0") or 0),
                float(_last_value(block, "Posy", _last_value(block, "PosY", "0")) or 0),
                float(_last_value(block, "PosZ", "0") or 0),
            ],
        }
    return records


def parse_scene_config_initial_loops(path: Path, scene_id: str) -> list[str]:
    """Extract top-level NPCInfos loop IDs from one JSON-like SceneConfig record."""
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    starts: list[int] = []
    for index, line in enumerate(lines[:-1]):
        if line.strip() not in {"{", "[{"}:
            continue
        next_line = lines[index + 1]
        if re.match(r'^\s*"sceneId"\s*:', next_line):
            starts.append(index)
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end])
        if _first_value(block, "sceneId") != str(scene_id):
            continue
        npc_marker = re.search(r'(?m)^\s*"NPCInfos"\s*:', block)
        if not npc_marker:
            return []
        npc_block = block[npc_marker.start() :]
        return re.findall(
            r'(?:\[\{|\n\{)\s*\n\s*"id"\s*:\s*"([^"\r\n]+)"\s*,\s*\n\s*"NPC"\s*:',
            npc_block,
        )
    raise ValueError(f"SceneConfig sceneId not found: {scene_id}")


def _asset_exists(asset_root: Path | None, res_path: str) -> bool | None:
    if not asset_root or not res_path:
        return None
    normalized = Path(*res_path.split("/"))
    candidates = [asset_root / normalized, asset_root / f"{normalized}.png"]
    return any(candidate.exists() for candidate in candidates)


def extract_timeline(
    talk_path: Path,
    npc_path: Path,
    start_talk_id: str,
    initial_loop_ids: list[str],
    asset_root: Path | None,
    max_nodes: int,
    scene_config_path: Path | None = None,
    scene_id: str = "",
    choice_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    talks = parse_talk_table(talk_path)
    loops = parse_npc_loop_table(npc_path)
    issues: list[dict[str, str]] = []
    present: dict[str, dict[str, Any]] = {}
    actor_catalog: dict[str, dict[str, Any]] = {}

    def spawn(loop_id: str, node_id: str, initial: bool = False) -> None:
        loop = loops.get(loop_id)
        if not loop:
            issues.append(
                {"code": "UNKNOWN_LOOP_ID", "nodeId": node_id, "detail": loop_id}
            )
            return
        actor_id = loop["actorId"]
        if actor_id in present:
            issues.append(
                {"code": "DUPLICATE_ENTER", "nodeId": node_id, "detail": actor_id}
            )
            return
        actor = dict(loop)
        actor.update(
            {
                "entryNode": "initial" if initial else node_id,
                "idleActivePair": bool(loop["clickResPath"])
                and loop["resPath"] != loop["clickResPath"],
                "resAssetExists": _asset_exists(asset_root, loop["resPath"]),
                "clickAssetExists": _asset_exists(asset_root, loop["clickResPath"]),
            }
        )
        present[actor_id] = actor
        actor_catalog[actor_id] = actor

    resolved_initial_ids = list(initial_loop_ids)
    if scene_config_path or scene_id:
        if not scene_config_path or not scene_id:
            raise ValueError("scene_config_path and scene_id must be supplied together.")
        resolved_initial_ids.extend(parse_scene_config_initial_loops(scene_config_path, scene_id))
    resolved_initial_ids = list(dict.fromkeys(resolved_initial_ids))
    for loop_id in resolved_initial_ids:
        spawn(loop_id, "initial", initial=True)

    chain: list[dict[str, Any]] = []
    seen: set[str] = set()
    current = start_talk_id
    choice_map = choice_map or {}
    for _ in range(max_nodes):
        if not current or current == "0":
            break
        if current in seen:
            issues.append({"code": "TALK_CYCLE", "nodeId": current, "detail": current})
            break
        seen.add(current)
        talk = talks.get(current)
        if not talk:
            issues.append({"code": "MISSING_TALK_NODE", "nodeId": current, "detail": current})
            break
        before_ids = list(present)
        event: dict[str, Any] = {"type": "dialogue"}
        if talk["script"] == ENTER_SCRIPT:
            loop_id = talk["parameterInts"][0] if talk["parameterInts"] else ""
            event = {"type": "enter", "loopId": loop_id}
            spawn(loop_id, current)
            if loop_id in loops:
                event["actorId"] = loops[loop_id]["actorId"]
        elif talk["script"] == EXIT_SCRIPT:
            npc_id = talk["parameterInts"][0] if talk["parameterInts"] else ""
            actor_id = f"npc:{npc_id}"
            event = {"type": "exit", "npcId": npc_id, "actorId": actor_id}
            if actor_id not in present:
                issues.append(
                    {"code": "EXIT_ACTOR_NOT_PRESENT", "nodeId": current, "detail": actor_id}
                )
            else:
                present.pop(actor_id)
        after_ids = list(present)
        branch_targets = []
        if talk["script"] not in {ENTER_SCRIPT, EXIT_SCRIPT} and not talk["next"]:
            branch_targets = [target for target in talk["parameterInts"] if target in talks]
        node = {
                "index": len(chain),
                "nodeId": current,
                "step": talk["step"],
                "speakerId": talk["speakerId"],
                "words": talk["words"],
                "videoScene": talk["videoScene"],
                "event": event,
                "beforeCast": before_ids,
                "afterCast": after_ids,
                "frozenActorIds": [actor for actor in before_ids if actor in after_ids],
                "branchTargets": branch_targets,
            }
        chain.append(node)
        if branch_targets:
            selected = choice_map.get(current, "")
            if selected:
                if selected not in branch_targets:
                    issues.append(
                        {
                            "code": "INVALID_BRANCH_SELECTION",
                            "nodeId": current,
                            "detail": f"selected={selected}; allowed={','.join(branch_targets)}",
                        }
                    )
                    break
                node["selectedBranch"] = selected
                current = selected
            elif len(branch_targets) == 1:
                node["selectedBranch"] = branch_targets[0]
                current = branch_targets[0]
            else:
                issues.append(
                    {
                        "code": "UNRESOLVED_BRANCH",
                        "nodeId": current,
                        "detail": ",".join(branch_targets),
                    }
                )
                break
        else:
            current = talk["next"]
    else:
        issues.append(
            {
                "code": "MAX_NODES_REACHED",
                "nodeId": current,
                "detail": str(max_nodes),
            }
        )

    missing_assets = [
        actor_id
        for actor_id, actor in actor_catalog.items()
        if actor["resAssetExists"] is False or actor["clickAssetExists"] is False
    ]
    for actor_id in missing_assets:
        issues.append(
            {"code": "MISSING_NPC_ASSET", "nodeId": "", "detail": actor_id}
        )
    return {
        "schema": "ndc-scene-timeline/v1",
        "source": {
            "talkTable": str(talk_path.resolve()),
            "talkTableSha256": sha256(talk_path),
            "npcLoopTable": str(npc_path.resolve()),
            "npcLoopTableSha256": sha256(npc_path),
            "startTalkId": start_talk_id,
            "initialLoopIds": resolved_initial_ids,
            "sceneConfigTable": str(scene_config_path.resolve()) if scene_config_path else "",
            "sceneConfigTableSha256": sha256(scene_config_path) if scene_config_path else "",
            "sceneId": scene_id,
            "branchSelections": choice_map,
        },
        "summary": {
            "nodeCount": len(chain),
            "actorCount": len(actor_catalog),
            "enterCount": sum(node["event"]["type"] == "enter" for node in chain),
            "exitCount": sum(node["event"]["type"] == "exit" for node in chain),
            "issueCount": len(issues),
        },
        "actors": list(actor_catalog.values()),
        "nodes": chain,
        "issues": issues,
    }


def _gaze_target(actor: dict[str, Any]) -> tuple[str, str]:
    target = actor.get("gazeTarget", {})
    if not isinstance(target, dict):
        raise ValueError(f"{actor.get('actorId', '<actor>')}.gazeTarget must be an object.")
    return str(target.get("type", "")), str(target.get("id", ""))


def validate_directing_timeline(data: dict[str, Any]) -> None:
    require_fields(data, ("schema", "timelineType", "snapshots"), "timeline")
    if data["schema"] != "ndc-directing-timeline/v1":
        raise ValueError("timeline.schema must be ndc-directing-timeline/v1.")
    if data["timelineType"] != "pure-narrative":
        raise ValueError("Directing timeline validator is for pure-narrative scenes.")
    snapshots = data["snapshots"]
    if not snapshots:
        raise ValueError("timeline.snapshots cannot be empty.")
    previous: dict[str, dict[str, Any]] = {}
    generations: dict[str, int] = {}
    for index, snapshot in enumerate(snapshots):
        label = f"snapshots[{index}]"
        require_fields(
            snapshot,
            ("id", "storyBeat", "silentFrameStatement", "event", "actors"),
            label,
        )
        beat = snapshot["storyBeat"]
        require_fields(
            beat,
            ("objective", "conflict", "emotion", "subtext", "actionFocus"),
            f"{label}.storyBeat",
        )
        if not str(snapshot["silentFrameStatement"]).strip():
            raise ValueError(f"{label}.silentFrameStatement cannot be empty.")
        event = snapshot["event"]
        require_fields(event, ("type",), f"{label}.event")
        if event["type"] not in {"initial", "dialogue", "enter", "exit"}:
            raise ValueError(f"{label}.event.type is unsupported: {event['type']}")
        actors: dict[str, dict[str, Any]] = {}
        for actor_index, actor in enumerate(snapshot["actors"]):
            actor_label = f"{label}.actors[{actor_index}]"
            require_fields(
                actor,
                (
                    "actorId",
                    "poseId",
                    "transformId",
                    "placementId",
                    "affordanceZoneId",
                    "gazeTarget",
                    "futureActorDependency",
                    "reciprocityRequired",
                    "performance",
                ),
                actor_label,
            )
            actor_id = str(actor["actorId"])
            if actor_id in actors:
                raise ValueError(f"{label} duplicates actorId {actor_id}.")
            if actor["futureActorDependency"] is not False:
                raise ValueError(f"{actor_label} depends on a future entrant.")
            performance = actor["performance"]
            require_fields(
                performance,
                (
                    "action",
                    "emotion",
                    "energy",
                    "beatEnergy",
                    "silentFrameVerb",
                    "ongoingOccupation",
                    "performanceFamily",
                    "bodyLine",
                    "weightDistribution",
                    "facialExpression",
                    "handBusiness",
                    "gestureMotivation",
                    "namedSupport",
                    "socialTerritory",
                    "costumeState",
                    "holdPoseValidity",
                    "tenSecondHold",
                    "depthHonesty",
                ),
                f"{actor_label}.performance",
            )
            if performance["holdPoseValidity"] != "pass":
                raise ValueError(f"{actor_label} is not valid as a held pose.")
            if performance["tenSecondHold"] != "pass":
                raise ValueError(f"{actor_label} cannot remain natural for a ten-second hold.")
            if performance["depthHonesty"] != "pass":
                raise ValueError(f"{actor_label} enlarges or advances the actor for readability.")
            if performance["beatEnergy"] not in {"still", "low", "medium", "high"}:
                raise ValueError(f"{actor_label}.performance.beatEnergy is unsupported.")
            if performance["performanceFamily"] not in {
                "ongoing-occupation", "supported-hold", "transition", "confrontational-action"
            }:
                raise ValueError(f"{actor_label}.performance.performanceFamily is unsupported.")
            motivation = performance["gestureMotivation"]
            require_fields(
                motivation,
                ("leftHand", "rightHand"),
                f"{actor_label}.performance.gestureMotivation",
            )
            for semantic_field in (
                "silentFrameVerb", "ongoingOccupation", "namedSupport", "socialTerritory"
            ):
                if not str(performance[semantic_field]).strip():
                    raise ValueError(f"{actor_label}.performance.{semantic_field} cannot be empty.")
            actors[actor_id] = actor

        current_ids = set(actors)
        previous_ids = set(previous)
        entered = current_ids - previous_ids
        exited = previous_ids - current_ids
        event_actor = str(event.get("actorId", ""))
        if event["type"] == "enter" and entered != {event_actor}:
            raise ValueError(
                f"{label} enter event must add only {event_actor}; observed {sorted(entered)}."
            )
        if event["type"] == "exit" and exited != {event_actor}:
            raise ValueError(
                f"{label} exit event must remove only {event_actor}; observed {sorted(exited)}."
            )
        if event["type"] in {"initial", "dialogue"} and index > 0 and (entered or exited):
            raise ValueError(f"{label} changes cast without an enter/exit event.")

        for actor_id in entered:
            generations[actor_id] = generations.get(actor_id, 0) + 1
        for actor_id in current_ids & previous_ids:
            current_actor = actors[actor_id]
            prior_actor = previous[actor_id]
            invariant_fields = ("poseId", "transformId", "placementId", "affordanceZoneId")
            drift = [
                field
                for field in invariant_fields
                if current_actor[field] != prior_actor[field]
            ]
            if drift:
                raise ValueError(
                    f"{label} changes uninterrupted actor {actor_id}: {', '.join(drift)}. "
                    "A later entrant cannot alter an existing actor state."
                )
        for actor_id, actor in actors.items():
            gaze_type, gaze_id = _gaze_target(actor)
            if gaze_type not in {"player", "scene-object", "actor", "offscreen", "none"}:
                raise ValueError(f"{label} actor {actor_id} has unsupported gaze type {gaze_type}.")
            if gaze_type == "actor" and gaze_id not in current_ids:
                raise ValueError(
                    f"{label} actor {actor_id} looks at absent/future actor {gaze_id}."
                )
            if actor["reciprocityRequired"]:
                if gaze_type != "actor":
                    raise ValueError(f"{label} actor {actor_id} requires reciprocity without actor gaze.")
                reverse_type, reverse_id = _gaze_target(actors[gaze_id])
                if reverse_type != "actor" or reverse_id != actor_id:
                    raise ValueError(
                        f"{label} reciprocal gaze is incomplete between {actor_id} and {gaze_id}."
                    )
        previous = actors


def _point_in_polygon(point: tuple[float, float], polygon: list[list[float]]) -> bool:
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, vertex in enumerate(polygon):
        xi, yi = float(vertex[0]), float(vertex[1])
        xj, yj = float(polygon[j][0]), float(polygon[j][1])
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def validate_affordance(data: dict[str, Any]) -> None:
    require_fields(data, ("schema", "sceneSize", "zones", "placements"), "affordance")
    if data["schema"] != "ndc-scene-affordance/v1":
        raise ValueError("affordance.schema must be ndc-scene-affordance/v1.")
    width, height = data["sceneSize"]
    if width <= 0 or height <= 0:
        raise ValueError("affordance.sceneSize must be positive.")
    zones: dict[str, dict[str, Any]] = {}
    for index, zone in enumerate(data["zones"]):
        label = f"zones[{index}]"
        require_fields(zone, ("id", "polygon", "capabilities", "depthClass"), label)
        zone_id = str(zone["id"])
        if zone_id in zones:
            raise ValueError(f"Duplicate affordance zone: {zone_id}")
        polygon = zone["polygon"]
        if len(polygon) < 3:
            raise ValueError(f"{label}.polygon requires at least three points.")
        for point in polygon:
            if len(point) != 2 or not (0 <= point[0] <= width and 0 <= point[1] <= height):
                raise ValueError(f"{label}.polygon contains an out-of-canvas point: {point}")
        capabilities = zone["capabilities"]
        if not capabilities:
            raise ValueError(f"{label}.capabilities cannot be empty.")
        if any(capability not in ZONE_COLORS for capability in capabilities):
            raise ValueError(f"{label} contains an unsupported capability.")
        zones[zone_id] = zone
    support_surfaces: dict[str, dict[str, Any]] = {}
    for index, surface in enumerate(data.get("supportSurfaces", [])):
        label = f"supportSurfaces[{index}]"
        require_fields(surface, ("id", "contacts", "evidence", "occupancy"), label)
        surface_id = str(surface["id"])
        if not surface_id or surface_id in support_surfaces:
            raise ValueError(f"{label}.id must be unique and non-empty: {surface_id}")
        if not str(surface["evidence"]).strip():
            raise ValueError(f"{label}.evidence cannot be empty.")
        if not surface["contacts"]:
            raise ValueError(f"{label}.contacts cannot be empty.")
        occupancy = surface["occupancy"]
        require_fields(occupancy, ("status", "evidence"), f"{label}.occupancy")
        if occupancy["status"] not in {"clear", "occupied"}:
            raise ValueError(f"{label}.occupancy.status must be clear or occupied.")
        if not str(occupancy["evidence"]).strip():
            raise ValueError(f"{label}.occupancy.evidence cannot be empty.")
        if occupancy["status"] == "occupied":
            plan = occupancy.get("clearancePlan")
            if not plan:
                raise ValueError(f"{label} is occupied but lacks clearancePlan.")
            require_fields(
                plan,
                ("mode", "item", "destination", "authorizedComponentBBox", "reason"),
                f"{label}.occupancy.clearancePlan",
            )
            if plan["mode"] not in {"relocate-within-component", "remove-within-component", "retain-as-support"}:
                raise ValueError(f"{label}.occupancy.clearancePlan.mode is unsupported.")
            bbox = plan["authorizedComponentBBox"]
            if len(bbox) != 4 or not (0 <= bbox[0] < bbox[2] <= width and 0 <= bbox[1] < bbox[3] <= height):
                raise ValueError(f"{label}.occupancy.clearancePlan.authorizedComponentBBox is invalid.")
        covered_regions: set[str] = set()
        for contact_index, contact in enumerate(surface["contacts"]):
            contact_label = f"{label}.contacts[{contact_index}]"
            require_fields(contact, ("regions", "polyline", "tolerancePx"), contact_label)
            regions = [str(region) for region in contact["regions"]]
            if not regions or any(not region for region in regions):
                raise ValueError(f"{contact_label}.regions cannot be empty.")
            duplicate_regions = covered_regions.intersection(regions)
            if duplicate_regions:
                raise ValueError(
                    f"{contact_label} duplicates contact regions: {sorted(duplicate_regions)}"
                )
            covered_regions.update(regions)
            polyline = contact["polyline"]
            if len(polyline) < 2:
                raise ValueError(f"{contact_label}.polyline requires at least two points.")
            previous_x: float | None = None
            for point in polyline:
                if len(point) != 2 or not (0 <= point[0] <= width and 0 <= point[1] <= height):
                    raise ValueError(f"{contact_label}.polyline has an out-of-canvas point: {point}")
                current_x = float(point[0])
                if previous_x is not None and current_x <= previous_x:
                    raise ValueError(f"{contact_label}.polyline X values must increase strictly.")
                previous_x = current_x
            tolerance = float(contact["tolerancePx"])
            if tolerance < 0 or tolerance > max(width, height) * 0.05:
                raise ValueError(f"{contact_label}.tolerancePx is outside the supported range.")
        support_surfaces[surface_id] = surface

    for index, placement in enumerate(data["placements"]):
        label = f"placements[{index}]"
        require_fields(
            placement,
            ("actorId", "placementClass", "anchor", "zoneId", "supportObjectId"),
            label,
        )
        zone_id = str(placement["zoneId"])
        if zone_id not in zones:
            raise ValueError(f"{label}.zoneId does not exist: {zone_id}")
        placement_class = str(placement["placementClass"])
        capability = CAPABILITY_BY_PLACEMENT.get(placement_class)
        if not capability:
            raise ValueError(f"{label}.placementClass is unsupported: {placement_class}")
        if capability not in zones[zone_id]["capabilities"]:
            raise ValueError(
                f"{label} uses {placement_class} in zone {zone_id} without {capability} capability."
            )
        anchor = tuple(float(value) for value in placement["anchor"])
        if not _point_in_polygon(anchor, zones[zone_id]["polygon"]):
            raise ValueError(f"{label}.anchor is outside zone {zone_id}.")
        if not placement["supportObjectId"]:
            raise ValueError(f"{label} requires a named support object.")
        if str(placement["supportObjectId"]) not in support_surfaces:
            raise ValueError(
                f"{label}.supportObjectId has no authored support surface: "
                f"{placement['supportObjectId']}"
            )
        if placement_class == "lying":
            surface = support_surfaces[str(placement["supportObjectId"])]
            for field in ("supportPolygon", "headRegionPolygon", "footRegionPolygon"):
                polygon = surface.get(field)
                if not isinstance(polygon, list) or len(polygon) < 3:
                    raise ValueError(
                        f"{label} lying support surface requires {field} with at least three points."
                    )
                for point in polygon:
                    if len(point) != 2 or not (0 <= point[0] <= width and 0 <= point[1] <= height):
                        raise ValueError(f"{label}.{field} contains an out-of-canvas point: {point}")


def _support_y_at_x(polyline: list[list[float]], x: float) -> float:
    for start, end in zip(polyline, polyline[1:]):
        x0, y0 = float(start[0]), float(start[1])
        x1, y1 = float(end[0]), float(end[1])
        if x0 <= x <= x1:
            ratio = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * ratio
    raise ValueError(f"Contact X={x:.2f} falls outside the authored support polyline.")


def validate_support_contact(
    affordance_path: Path,
    placement_path: Path,
    report_path: Path | None = None,
    preview_path: Path | None = None,
) -> dict[str, Any]:
    """Compare authored anatomical contacts with scene-authored support lines.

    The support line is evidence authored from the fixed scene/depth model.  It
    deliberately remains independent from the whitebox joints so a floating or
    sunken pose cannot make its own check pass.
    """
    affordance = load_json(affordance_path)
    validate_affordance(affordance)
    placement = load_json(placement_path)
    scene_size = tuple(affordance["sceneSize"])
    if tuple(placement.get("sceneSize", [])) != scene_size:
        raise ValueError("Placement and affordance sceneSize differ.")
    target = placement["target"]
    placement_class = str(target.get("placementClass", "standing"))
    pose_field = {
        "standing": "standingPose",
        "walking": "standingPose",
        "leaning": "standingPose",
        "seated": "seatedPose",
        "lying": "lyingPose",
    }.get(placement_class)
    if not pose_field or pose_field not in target:
        raise ValueError(f"Unsupported or missing pose for support validation: {placement_class}")
    pose = target[pose_field]
    surfaces = {str(surface["id"]): surface for surface in affordance["supportSurfaces"]}
    results: list[dict[str, Any]] = []
    lying_envelope: dict[str, Any] | None = None
    for relation_index, relation in enumerate(target.get("sceneRelations", [])):
        if relation.get("relation") != "supported-by":
            continue
        surface_id = str(relation.get("objectId", ""))
        if surface_id not in surfaces:
            raise ValueError(
                f"target.sceneRelations[{relation_index}] names an unknown support surface: {surface_id}"
            )
        surface = surfaces[surface_id]
        contact_by_region: dict[str, dict[str, Any]] = {}
        for contact in surface["contacts"]:
            for region in contact["regions"]:
                contact_by_region[str(region)] = contact
        for region in relation.get("regions", []):
            region = str(region)
            if region not in pose:
                raise ValueError(f"Support region {region} is missing from {pose_field}.")
            if region not in contact_by_region:
                raise ValueError(f"Support surface {surface_id} has no contact line for {region}.")
            point = pose[region]
            x, y = float(point[0]), float(point[1])
            contact = contact_by_region[region]
            support_y = _support_y_at_x(contact["polyline"], x)
            delta = y - support_y
            tolerance = float(contact["tolerancePx"])
            status = "pass" if abs(delta) <= tolerance else "fail"
            if status == "pass":
                condition = "contact"
            elif delta < 0:
                condition = "floating"
            else:
                condition = "sunken"
            results.append(
                {
                    "region": region,
                    "supportObjectId": surface_id,
                    "point": [x, y],
                    "expectedSupportY": support_y,
                    "verticalDeltaPx": delta,
                    "tolerancePx": tolerance,
                    "condition": condition,
                    "status": status,
                }
            )
    if not results:
        raise ValueError("Placement contains no supported-by contact regions to validate.")
    if placement_class == "lying":
        surface_id = str(pose.get("supportObject", ""))
        if surface_id not in surfaces:
            raise ValueError("Lying pose supportObject is missing from the affordance contract.")
        surface = surfaces[surface_id]
        for field in ("supportPolygon", "headRegionPolygon", "footRegionPolygon"):
            if field not in surface:
                raise ValueError(f"Lying support surface {surface_id} lacks {field}.")
        support_polygon = surface["supportPolygon"]
        head_polygon = surface["headRegionPolygon"]
        foot_polygon = surface["footRegionPolygon"]
        head_box = pose["headBox"]
        head_center = (
            (float(head_box[0]) + float(head_box[2])) / 2,
            (float(head_box[1]) + float(head_box[3])) / 2,
        )
        left_foot = tuple(float(value) for value in pose["leftFoot"])
        right_foot = tuple(float(value) for value in pose["rightFoot"])
        body_axis = [tuple(float(value) for value in point) for point in pose["bodyAxis"]]
        supported_point_names = (
            "leftShoulder", "rightShoulder", "leftElbow", "rightElbow",
            "leftHand", "rightHand", "leftHip", "rightHip", "hip",
            "leftKnee", "rightKnee", "leftFoot", "rightFoot",
        )
        outside = [
            name for name in supported_point_names
            if name in pose and not _point_in_polygon(tuple(float(value) for value in pose[name]), support_polygon)
        ]
        axis_outside = [point for point in body_axis if not _point_in_polygon(point, support_polygon)]
        head_status = _point_in_polygon(head_center, head_polygon)
        left_foot_status = _point_in_polygon(left_foot, foot_polygon)
        right_foot_status = _point_in_polygon(right_foot, foot_polygon)
        axis_head_distance = math.hypot(body_axis[0][0] - head_center[0], body_axis[0][1] - head_center[1])
        foot_center = ((left_foot[0] + right_foot[0]) / 2, (left_foot[1] + right_foot[1]) / 2)
        axis_foot_distance = math.hypot(body_axis[1][0] - foot_center[0], body_axis[1][1] - foot_center[1])
        axis_endpoint_tolerance = float(surface.get("axisEndpointTolerancePx", 80))
        envelope_status = (
            head_status and left_foot_status and right_foot_status
            and not outside and not axis_outside
            and axis_head_distance <= axis_endpoint_tolerance
            and axis_foot_distance <= axis_endpoint_tolerance
        )
        lying_envelope = {
            "supportObjectId": surface_id,
            "headCenter": list(head_center),
            "headInHeadRegion": head_status,
            "leftFootInFootRegion": left_foot_status,
            "rightFootInFootRegion": right_foot_status,
            "outsideSupportPoints": outside,
            "axisOutsideSupportPolygon": [list(point) for point in axis_outside],
            "axisHeadEndpointDistancePx": axis_head_distance,
            "axisFootEndpointDistancePx": axis_foot_distance,
            "axisEndpointTolerancePx": axis_endpoint_tolerance,
            "status": "pass" if envelope_status else "fail",
        }
        if not envelope_status:
            raise ValueError(
                "LYING_SUPPORT_ENVELOPE_FAILED: head must occupy the authored pillow/head region; "
                "both feet must occupy the authored bed-foot region; all anatomical points and both "
                "body-axis endpoints must remain inside the bed support polygon."
            )
    report = {
        "schema": "ndc-support-contact-report/v1",
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "scene": placement["scene"],
        "placementContract": str(placement_path.resolve()),
        "affordanceContract": str(affordance_path.resolve()),
        "actor": placement.get("characterName", ""),
        "poseId": target.get("poseDefinition", {}).get("poseId", ""),
        "contacts": results,
        "lyingSupportEnvelope": lying_envelope,
    }
    if report_path:
        write_json(report_path, report)
    if preview_path:
        scene_path = resolve_path(placement["scene"], placement_path)
        base = Image.open(scene_path).convert("RGBA")
        if base.size != scene_size:
            raise ValueError("Support preview scene size differs from sceneSize.")
        overlay = Image.new("RGBA", scene_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        line_width = max(4, round(scene_size[1] / 260))
        font = _font(max(14, round(scene_size[1] / 65)))
        used_surfaces = {result["supportObjectId"] for result in results}
        for surface_id in used_surfaces:
            for contact in surfaces[surface_id]["contacts"]:
                draw.line(
                    [tuple(point) for point in contact["polyline"]],
                    fill=(0, 220, 255, 235),
                    width=line_width,
                )
        for result in results:
            x, y = result["point"]
            support_y = result["expectedSupportY"]
            color = (30, 220, 90, 255) if result["status"] == "pass" else (255, 45, 45, 255)
            radius = line_width * 2
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            draw.line((x, y, x, support_y), fill=color, width=line_width)
            label = f"{result['region']} {result['condition']} {result['verticalDeltaPx']:+.1f}px"
            draw.text((x + radius + 4, min(y, support_y)), label, fill=color, font=font)
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        Image.alpha_composite(base, overlay).save(preview_path)
    if report["status"] != "pass":
        failures = ", ".join(
            f"{item['region']}={item['condition']}({item['verticalDeltaPx']:+.1f}px)"
            for item in results
            if item["status"] != "pass"
        )
        raise ValueError(f"SUPPORT_CONTACT_FAILED: {failures}")
    return report


def validate_cast_scale(
    contract_path: Path, report_path: Path | None = None
) -> dict[str, Any]:
    """Validate cast body and anatomical-head scale through one depth model.

    Version 1 is retained for historical contracts.  New production must use
    v2, which makes approved-card anatomical head scale a primary gate instead
    of allowing a full-body box to stand in for cast proportion.
    """
    data = load_json(contract_path)
    require_fields(
        data,
        ("schema", "sceneSize", "horizonY", "referenceActorId", "maxDeviationRatio", "actors"),
        "castScale",
    )
    schema = str(data["schema"])
    if schema not in {"ndc-cast-scale/v1", "ndc-cast-scale/v2"}:
        raise ValueError("castScale.schema must be ndc-cast-scale/v1 or v2.")
    head_scale_required = schema == "ndc-cast-scale/v2"
    if head_scale_required and data.get("headScalePriority") is not True:
        raise ValueError("castScale v2 requires headScalePriority: true.")
    horizon_y = float(data["horizonY"])
    tolerance = float(data["maxDeviationRatio"])
    if tolerance <= 0 or tolerance > 0.20:
        raise ValueError("castScale.maxDeviationRatio must be in (0, 0.20].")
    loaded: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(data["actors"]):
        label = f"castScale.actors[{index}]"
        required_entry_fields = ["actorId", "placementContract"]
        if head_scale_required:
            required_entry_fields.append("identityScaleReference")
        require_fields(entry, tuple(required_entry_fields), label)
        actor_id = str(entry["actorId"])
        if not actor_id or actor_id in loaded:
            raise ValueError(f"{label}.actorId must be unique and non-empty.")
        placement_path = resolve_path(entry["placementContract"], contract_path)
        placement = load_json(placement_path)
        if tuple(placement.get("sceneSize", [])) != tuple(data["sceneSize"]):
            raise ValueError(f"{label} sceneSize differs from cast scale sceneSize.")
        target = placement["target"]
        support_y = float(target["foot"][1])
        if support_y <= horizon_y:
            raise ValueError(f"{label} support point must lie below horizonY.")
        placement_class = str(target.get("placementClass", "standing"))
        if placement_class in {"seated", "lying"}:
            standing_px = float(target.get("standingEquivalentHeightPx", 0))
        else:
            standing_px = float(target["visibleHeightPx"])
        if standing_px <= 0:
            raise ValueError(f"{label} lacks a positive standing-equivalent height.")
        actor_record = {
            "actorId": actor_id,
            "characterName": placement.get("characterName", actor_id),
            "characterHeightCm": float(placement["characterHeightCm"]),
            "supportPoint": list(target["foot"]),
            "standingEquivalentHeightPx": standing_px,
            "poseId": target.get("poseDefinition", {}).get("poseId", ""),
            "placementContract": str(placement_path.resolve()),
        }
        if head_scale_required:
            identity = entry["identityScaleReference"]
            require_fields(
                identity,
                (
                    "referenceArtifact",
                    "referenceFullBodyHeightPx",
                    "referenceAnatomicalHeadHeightPx",
                    "measurementMethod",
                    "confidence",
                ),
                f"{label}.identityScaleReference",
            )
            reference_artifact = resolve_path(identity["referenceArtifact"], contract_path)
            if not reference_artifact.is_file():
                raise ValueError(
                    f"{label}.identityScaleReference.referenceArtifact does not exist."
                )
            reference_full_height = float(identity["referenceFullBodyHeightPx"])
            reference_head_height = float(identity["referenceAnatomicalHeadHeightPx"])
            if reference_full_height <= 0 or reference_head_height <= 0:
                raise ValueError(f"{label} identity scale measurements must be positive.")
            head_to_height_ratio = reference_head_height / reference_full_height
            if not 0.09 <= head_to_height_ratio <= 0.18:
                raise ValueError(
                    f"{label} approved-card anatomical head ratio is implausible: "
                    f"{head_to_height_ratio:.4f}."
                )
            pose_key = {
                "standing": "standingPose",
                "seated": "seatedPose",
                "lying": "lyingPose",
            }.get(placement_class)
            if not pose_key or pose_key not in target:
                raise ValueError(f"{label} lacks an exact pose for anatomical head review.")
            measured_head_box = entry.get("measuredHeadBox", target[pose_key]["headBox"])
            if not isinstance(measured_head_box, list) or len(measured_head_box) != 4:
                raise ValueError(f"{label}.measuredHeadBox must be [x1,y1,x2,y2].")
            measured_head_height = float(measured_head_box[3]) - float(measured_head_box[1])
            if measured_head_height <= 0:
                raise ValueError(f"{label}.measuredHeadBox must have positive height.")
            actor_record.update(
                {
                    "identityScaleReference": {
                        **identity,
                        "referenceArtifact": str(reference_artifact.resolve()),
                        "headToHeightRatio": head_to_height_ratio,
                    },
                    "measuredHeadBox": list(measured_head_box),
                    "measuredHeadHeightPx": measured_head_height,
                }
            )
        loaded[actor_id] = actor_record
    reference_id = str(data["referenceActorId"])
    if reference_id not in loaded:
        raise ValueError("castScale.referenceActorId is not present in actors.")
    reference = loaded[reference_id]
    reference_depth = float(reference["supportPoint"][1]) - horizon_y
    reference_ppcm = float(reference["standingEquivalentHeightPx"]) / float(
        reference["characterHeightCm"]
    )
    head_tolerance = float(data.get("maxHeadDeviationRatio", tolerance))
    if head_scale_required and (head_tolerance <= 0 or head_tolerance > 0.15):
        raise ValueError("castScale.maxHeadDeviationRatio must be in (0, 0.15].")
    actor_results: list[dict[str, Any]] = []
    for actor in loaded.values():
        depth_ratio = (float(actor["supportPoint"][1]) - horizon_y) / reference_depth
        expected = float(actor["characterHeightCm"]) * reference_ppcm * depth_ratio
        actual = float(actor["standingEquivalentHeightPx"])
        deviation = (actual - expected) / expected
        result = {
                **actor,
                "expectedStandingEquivalentHeightPx": expected,
                "depthScaleRatioToReference": depth_ratio,
                "bodyDeviationRatio": deviation,
                "bodyStatus": "pass" if abs(deviation) <= tolerance else "fail",
            }
        if head_scale_required:
            expected_head = actual * float(
                actor["identityScaleReference"]["headToHeightRatio"]
            )
            head_deviation = (
                float(actor["measuredHeadHeightPx"]) - expected_head
            ) / expected_head
            result.update(
                {
                    "expectedHeadHeightPx": expected_head,
                    "headDeviationRatio": head_deviation,
                    "headStatus": "pass"
                    if abs(head_deviation) <= head_tolerance
                    else "fail",
                }
            )
        else:
            result["headStatus"] = "not-checked-legacy-v1"
        result["status"] = (
            "pass"
            if result["bodyStatus"] == "pass"
            and (not head_scale_required or result["headStatus"] == "pass")
            else "fail"
        )
        actor_results.append(result)
    pairwise: list[dict[str, Any]] = []
    actors = list(loaded.values())
    for index, actor_a in enumerate(actors):
        for actor_b in actors[index + 1 :]:
            expected_ratio = (
                float(actor_a["characterHeightCm"])
                / float(actor_b["characterHeightCm"])
                * (float(actor_a["supportPoint"][1]) - horizon_y)
                / (float(actor_b["supportPoint"][1]) - horizon_y)
            )
            actual_ratio = float(actor_a["standingEquivalentHeightPx"]) / float(
                actor_b["standingEquivalentHeightPx"]
            )
            deviation = (actual_ratio - expected_ratio) / expected_ratio
            pair_result = {
                    "actorA": actor_a["actorId"],
                    "actorB": actor_b["actorId"],
                    "expectedHeightRatio": expected_ratio,
                    "actualHeightRatio": actual_ratio,
                    "bodyDeviationRatio": deviation,
                    "bodyStatus": "pass"
                    if abs(deviation) <= tolerance * 2
                    else "fail",
                }
            if head_scale_required:
                expected_head_ratio = (
                    actual_ratio
                    * float(actor_a["identityScaleReference"]["headToHeightRatio"])
                    / float(actor_b["identityScaleReference"]["headToHeightRatio"])
                )
                actual_head_ratio = float(actor_a["measuredHeadHeightPx"]) / float(
                    actor_b["measuredHeadHeightPx"]
                )
                head_ratio_deviation = (
                    actual_head_ratio - expected_head_ratio
                ) / expected_head_ratio
                pair_result.update(
                    {
                        "expectedHeadRatio": expected_head_ratio,
                        "actualHeadRatio": actual_head_ratio,
                        "headDeviationRatio": head_ratio_deviation,
                        "headStatus": "pass"
                        if abs(head_ratio_deviation) <= head_tolerance * 2
                        else "fail",
                    }
                )
            else:
                pair_result["headStatus"] = "not-checked-legacy-v1"
            pair_result["status"] = (
                "pass"
                if pair_result["bodyStatus"] == "pass"
                and (not head_scale_required or pair_result["headStatus"] == "pass")
                else "fail"
            )
            pairwise.append(pair_result)
    report = {
        "schema": "ndc-cast-scale-report/v2"
        if head_scale_required
        else "ndc-cast-scale-report/v1",
        "status": "pass"
        if all(item["status"] == "pass" for item in actor_results + pairwise)
        else "fail",
        "horizonY": horizon_y,
        "perspectiveEvidence": data.get("perspectiveEvidence", ""),
        "referenceActorId": reference_id,
        "maxDeviationRatio": tolerance,
        "headScalePriority": head_scale_required,
        "maxHeadDeviationRatio": head_tolerance if head_scale_required else None,
        "actors": actor_results,
        "pairwise": pairwise,
    }
    if report_path:
        write_json(report_path, report)
    if report["status"] != "pass":
        failed = ", ".join(
            f"{item['actorId']}=body:{item['bodyDeviationRatio']:+.3f},"
            f"head:{item.get('headDeviationRatio', 0):+.3f}"
            for item in actor_results
            if item["status"] != "pass"
        )
        raise ValueError(f"CAST_SCALE_FAILED: {failed}")
    return report


def _weighted_median(values: list[tuple[float, float]]) -> float:
    if not values or any(weight <= 0 for _, weight in values):
        raise ValueError("Weighted median requires positive weights.")
    ordered = sorted(values, key=lambda item: item[0])
    threshold = sum(weight for _, weight in ordered) / 2
    running = 0.0
    for value, weight in ordered:
        running += weight
        if running >= threshold:
            return value
    return ordered[-1][0]


def validate_scene_absolute_scale(
    contract_path: Path,
    report_path: Path | None = None,
    preview_path: Path | None = None,
) -> dict[str, Any]:
    """Validate one shared cast scale against fixed-scene objects.

    Cast-scale checks can prove that actors agree with one another while all of
    them are globally too large or too small.  This independent gate measures
    real scene objects, projects each measurement to a named actor plane, and
    reports the shared correction factor before any whitebox is approved.
    """
    data = load_json(contract_path)
    require_fields(
        data,
        ("schema", "scene", "sceneSize", "actors", "anchors", "limits"),
        "sceneAbsoluteScale",
    )
    if data["schema"] != "ndc-scene-absolute-scale/v1":
        raise ValueError("sceneAbsoluteScale.schema must be ndc-scene-absolute-scale/v1.")
    scene_size = tuple(int(value) for value in data["sceneSize"])
    actors: dict[str, dict[str, float]] = {}
    for index, actor in enumerate(data["actors"]):
        label = f"sceneAbsoluteScale.actors[{index}]"
        require_fields(
            actor,
            ("actorId", "characterHeightCm", "standingEquivalentHeightPx"),
            label,
        )
        actor_id = str(actor["actorId"])
        if not actor_id or actor_id in actors:
            raise ValueError(f"{label}.actorId must be unique and non-empty.")
        height_cm = float(actor["characterHeightCm"])
        height_px = float(actor["standingEquivalentHeightPx"])
        if height_cm <= 0 or height_px <= 0:
            raise ValueError(f"{label} heights must be positive.")
        actors[actor_id] = {
            "characterHeightCm": height_cm,
            "standingEquivalentHeightPx": height_px,
        }

    limits = data["limits"]
    require_fields(
        limits,
        ("maxGlobalDeviationRatio", "maxAnchorSpreadRatio", "minimumIndependentAnchors"),
        "sceneAbsoluteScale.limits",
    )
    global_tolerance = float(limits["maxGlobalDeviationRatio"])
    spread_tolerance = float(limits["maxAnchorSpreadRatio"])
    minimum_anchors = int(limits["minimumIndependentAnchors"])
    if not 0 < global_tolerance <= 0.25:
        raise ValueError("maxGlobalDeviationRatio must be in (0, 0.25].")
    if not 0 < spread_tolerance <= 0.35:
        raise ValueError("maxAnchorSpreadRatio must be in (0, 0.35].")
    if minimum_anchors < 3:
        raise ValueError("minimumIndependentAnchors must be at least 3.")

    confidence_weights = {"high": 3.0, "medium": 2.0, "low": 1.0}
    results: list[dict[str, Any]] = []
    weighted_factors: list[tuple[float, float]] = []
    groups: set[str] = set()
    bands: set[str] = set()
    axes: set[str] = set()
    for index, anchor in enumerate(data["anchors"]):
        label = f"sceneAbsoluteScale.anchors[{index}]"
        require_fields(
            anchor,
            (
                "anchorId",
                "actorId",
                "objectId",
                "independenceGroup",
                "axis",
                "depthBand",
                "realWorldRangeCm",
                "assumedCm",
                "measurementLine",
                "projectionScaleToActorPlane",
                "projectionEvidence",
                "confidence",
            ),
            label,
        )
        actor_id = str(anchor["actorId"])
        if actor_id not in actors:
            raise ValueError(f"{label}.actorId is not present in actors.")
        group = str(anchor["independenceGroup"]).strip()
        if not group or group in groups:
            raise ValueError(f"{label}.independenceGroup must be unique and non-empty.")
        groups.add(group)
        axis = str(anchor["axis"])
        if axis not in {"horizontal", "vertical"}:
            raise ValueError(f"{label}.axis must be horizontal or vertical.")
        axes.add(axis)
        depth_band = str(anchor["depthBand"])
        if depth_band not in {"actor-local", "cross-depth"}:
            raise ValueError(f"{label}.depthBand must be actor-local or cross-depth.")
        bands.add(depth_band)
        confidence = str(anchor["confidence"])
        if confidence not in confidence_weights:
            raise ValueError(f"{label}.confidence must be high, medium, or low.")
        line = anchor["measurementLine"]
        if not isinstance(line, list) or len(line) != 2 or any(len(point) != 2 for point in line):
            raise ValueError(f"{label}.measurementLine must contain two [x,y] points.")
        (x1, y1), (x2, y2) = ([float(value) for value in point] for point in line)
        if not all(0 <= x < scene_size[0] and 0 <= y < scene_size[1] for x, y in ((x1, y1), (x2, y2))):
            raise ValueError(f"{label}.measurementLine lies outside sceneSize.")
        measured_px = math.hypot(x2 - x1, y2 - y1)
        if measured_px <= 0:
            raise ValueError(f"{label}.measurementLine has zero length.")
        projection_scale = float(anchor["projectionScaleToActorPlane"])
        if projection_scale <= 0:
            raise ValueError(f"{label}.projectionScaleToActorPlane must be positive.")
        evidence = anchor["projectionEvidence"]
        if not isinstance(evidence, dict) or not evidence.get("perspectiveBasisIds"):
            raise ValueError(f"{label}.projectionEvidence requires perspectiveBasisIds.")
        if depth_band == "cross-depth" and not (
            evidence.get("sourceSupportPoint") and evidence.get("targetSupportPoint")
        ):
            raise ValueError(
                f"{label} cross-depth anchor requires sourceSupportPoint and targetSupportPoint."
            )
        real_range = anchor["realWorldRangeCm"]
        if not isinstance(real_range, list) or len(real_range) != 2:
            raise ValueError(f"{label}.realWorldRangeCm must be [minimum, maximum].")
        real_min, real_max = (float(value) for value in real_range)
        assumed_cm = float(anchor["assumedCm"])
        if not 0 < real_min <= assumed_cm <= real_max:
            raise ValueError(f"{label}.assumedCm must lie inside realWorldRangeCm.")
        actor = actors[actor_id]
        projected_px = measured_px * projection_scale
        expected_px = projected_px * actor["characterHeightCm"] / assumed_cm
        expected_min_px = projected_px * actor["characterHeightCm"] / real_max
        expected_max_px = projected_px * actor["characterHeightCm"] / real_min
        actual_px = actor["standingEquivalentHeightPx"]
        correction = expected_px / actual_px
        weight = confidence_weights[confidence]
        weighted_factors.append((correction, weight))
        results.append(
            {
                "anchorId": str(anchor["anchorId"]),
                "actorId": actor_id,
                "objectId": str(anchor["objectId"]),
                "independenceGroup": group,
                "axis": axis,
                "depthBand": depth_band,
                "confidence": confidence,
                "measurementLine": line,
                "measuredObjectPx": measured_px,
                "projectionScaleToActorPlane": projection_scale,
                "projectedObjectPx": projected_px,
                "expectedActorHeightPx": expected_px,
                "expectedActorHeightRangePx": [expected_min_px, expected_max_px],
                "actualActorHeightPx": actual_px,
                "recommendedScaleFactor": correction,
            }
        )

    if len(groups) < minimum_anchors:
        raise ValueError(
            f"sceneAbsoluteScale requires {minimum_anchors} independent anchors; found {len(groups)}."
        )
    if bands != {"actor-local", "cross-depth"}:
        raise ValueError("sceneAbsoluteScale requires actor-local and cross-depth anchors.")
    if axes != {"horizontal", "vertical"}:
        raise ValueError("sceneAbsoluteScale requires horizontal and vertical object dimensions.")

    global_factor = _weighted_median(weighted_factors)
    factor_values = [value for value, _ in weighted_factors]
    spread_ratio = (max(factor_values) - min(factor_values)) / global_factor
    spread_status = "pass" if spread_ratio <= spread_tolerance else "fail"
    global_status = "pass" if abs(global_factor - 1.0) <= global_tolerance else "fail"
    report = {
        "schema": "ndc-scene-absolute-scale-report/v1",
        "contract": str(contract_path.resolve()),
        "contractSha256": sha256(contract_path),
        "status": "pass" if spread_status == global_status == "pass" else "fail",
        "recommendedGlobalScaleFactor": global_factor,
        "globalDeviationRatio": global_factor - 1.0,
        "globalStatus": global_status,
        "anchorSpreadRatio": spread_ratio,
        "anchorSpreadStatus": spread_status,
        "limits": limits,
        "anchors": results,
        "note": "This gate is independent from actor-to-actor cast scale.",
    }
    if report_path:
        write_json(report_path, report)
    if preview_path:
        scene = Image.open(resolve_path(data["scene"], contract_path)).convert("RGBA")
        if scene.size != scene_size:
            raise ValueError("sceneAbsoluteScale preview scene differs from sceneSize.")
        draw = ImageDraw.Draw(scene)
        font = _font(max(13, round(scene_size[1] / 70)))
        for result in results:
            line = [tuple(point) for point in result["measurementLine"]]
            color = (40, 220, 255, 255) if result["depthBand"] == "actor-local" else (255, 180, 40, 255)
            draw.line(line, fill=color, width=max(3, round(scene_size[1] / 350)))
            draw.text(
                line[0],
                f"{result['anchorId']} {result['axis']} x{result['recommendedScaleFactor']:.3f}",
                fill=color,
                font=font,
            )
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        scene.save(preview_path)
    if report["status"] != "pass":
        raise ValueError(
            "SCENE_ABSOLUTE_SCALE_FAILED: "
            f"recommendedGlobalScaleFactor={global_factor:.4f}, spread={spread_ratio:.4f}; "
            "return to depth geometry and all-cast whiteboxes."
        )
    return report


def validate_gaze_conformance(
    contract_path: Path, report_path: Path | None = None
) -> dict[str, Any]:
    data = load_json(contract_path)
    require_fields(data, ("schema", "sceneSize", "actors"), "gazeConformance")
    if data["schema"] != "ndc-gaze-conformance/v1":
        raise ValueError("gazeConformance.schema must be ndc-gaze-conformance/v1.")
    results: list[dict[str, Any]] = []
    for index, actor in enumerate(data["actors"]):
        label = f"gazeConformance.actors[{index}]"
        require_fields(
            actor,
            ("actorId", "poseId", "eyeCenter", "directionPoint", "gazeTarget", "targetPoint", "maxAngularDeviationDeg"),
            label,
        )
        eye_x, eye_y = (float(value) for value in actor["eyeCenter"])
        direction_x, direction_y = (float(value) for value in actor["directionPoint"])
        target_x, target_y = (float(value) for value in actor["targetPoint"])
        gaze_vector = (direction_x - eye_x, direction_y - eye_y)
        target_vector = (target_x - eye_x, target_y - eye_y)
        gaze_length = math.hypot(*gaze_vector)
        target_length = math.hypot(*target_vector)
        if gaze_length <= 0 or target_length <= 0:
            raise ValueError(f"{label} contains a zero-length gaze or target vector.")
        cosine = max(
            -1.0,
            min(
                1.0,
                (gaze_vector[0] * target_vector[0] + gaze_vector[1] * target_vector[1])
                / (gaze_length * target_length),
            ),
        )
        angle = math.degrees(math.acos(cosine))
        limit = float(actor["maxAngularDeviationDeg"])
        if not 0 < limit <= 45:
            raise ValueError(f"{label}.maxAngularDeviationDeg must be in (0, 45].")
        status = "pass" if angle <= limit else "fail"
        results.append(
            {
                "actorId": str(actor["actorId"]),
                "poseId": str(actor["poseId"]),
                "gazeTarget": actor["gazeTarget"],
                "angularDeviationDeg": angle,
                "maxAngularDeviationDeg": limit,
                "status": status,
            }
        )
    report = {
        "schema": "ndc-gaze-conformance-report/v1",
        "contract": str(contract_path.resolve()),
        "contractSha256": sha256(contract_path),
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "actors": results,
    }
    if report_path:
        write_json(report_path, report)
    if report["status"] != "pass":
        failures = ", ".join(
            f"{item['actorId']}={item['angularDeviationDeg']:.1f}deg"
            for item in results
            if item["status"] != "pass"
        )
        raise ValueError(f"GAZE_CONFORMANCE_FAILED: {failures}")
    return report


def validate_component_policy(
    contract_path: Path, report_path: Path | None = None
) -> dict[str, Any]:
    data = load_json(contract_path)
    require_fields(
        data,
        ("schema", "sourceScene", "structuralSceneObjectIds", "layers", "relocations"),
        "componentPolicy",
    )
    if data["schema"] != "ndc-interaction-component-policy/v1":
        raise ValueError("componentPolicy.schema must be ndc-interaction-component-policy/v1.")
    structural = {str(value) for value in data["structuralSceneObjectIds"]}
    allowed_kinds = {
        "actor",
        "loose-prop-source-repair",
        "loose-prop-relocated",
        "source-occluder",
        "contact-shadow",
    }
    layer_ids: set[str] = set()
    failures: list[str] = []
    for index, layer in enumerate(data["layers"]):
        label = f"componentPolicy.layers[{index}]"
        require_fields(layer, ("layerId", "kind", "contentObjectIds", "sourcePolicy"), label)
        layer_id = str(layer["layerId"])
        if not layer_id or layer_id in layer_ids:
            raise ValueError(f"{label}.layerId must be unique and non-empty.")
        layer_ids.add(layer_id)
        kind = str(layer["kind"])
        if kind not in allowed_kinds:
            raise ValueError(f"{label}.kind is unsupported: {kind}")
        content_ids = {str(value) for value in layer["contentObjectIds"]}
        forbidden = structural & content_ids
        if forbidden and kind != "source-occluder":
            failures.append(
                f"{layer_id} contains fixed structural objects: {', '.join(sorted(forbidden))}"
            )
        if kind == "source-occluder":
            if layer["sourcePolicy"] != "exact-source-pixels" or layer.get("uniformScale", 1) != 1:
                failures.append(f"{layer_id} source occluder is not exact source pixels at scale 1")
        elif layer["sourcePolicy"] == "exact-source-pixels" and kind == "actor":
            failures.append(f"{layer_id} actor layer cannot claim exact source pixels")

    relocation_objects: set[str] = set()
    for index, relocation in enumerate(data["relocations"]):
        label = f"componentPolicy.relocations[{index}]"
        require_fields(
            relocation,
            ("objectId", "sourceRepairLayerId", "destinationLayerId", "originalRegionMask", "destinationRegionMask"),
            label,
        )
        object_id = str(relocation["objectId"])
        if object_id in structural:
            failures.append(f"relocation attempts to move structural object {object_id}")
        if object_id in relocation_objects:
            raise ValueError(f"{label}.objectId must be unique.")
        relocation_objects.add(object_id)
        for field in ("sourceRepairLayerId", "destinationLayerId"):
            if str(relocation[field]) not in layer_ids:
                failures.append(f"{label}.{field} does not reference a declared layer")
        for field in ("originalRegionMask", "destinationRegionMask"):
            path = resolve_path(relocation[field], contract_path)
            if not path.is_file():
                failures.append(f"{label}.{field} is missing: {path}")

    report = {
        "schema": "ndc-interaction-component-policy-report/v1",
        "contract": str(contract_path.resolve()),
        "contractSha256": sha256(contract_path),
        "status": "pass" if not failures else "fail",
        "structuralSceneObjectIds": sorted(structural),
        "layerIds": sorted(layer_ids),
        "relocatedObjectIds": sorted(relocation_objects),
        "failures": failures,
    }
    if report_path:
        write_json(report_path, report)
    if failures:
        raise ValueError("COMPONENT_POLICY_FAILED: " + "; ".join(failures))
    return report


def _font(size: int = 18) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render_affordance(contract_path: Path, output: Path, base_path: Path | None) -> None:
    data = load_json(contract_path)
    validate_affordance(data)
    size = tuple(data["sceneSize"])
    if base_path:
        base = Image.open(base_path).convert("RGBA")
        if base.size != size:
            raise ValueError("Affordance base image size differs from sceneSize.")
    else:
        base = Image.new("RGBA", size, (245, 245, 245, 255))
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _font(max(12, round(size[1] / 70)))
    for zone in data["zones"]:
        capability = zone["capabilities"][0]
        color = ZONE_COLORS[capability]
        polygon = [tuple(point) for point in zone["polygon"]]
        draw.polygon(polygon, fill=color, outline=color[:3] + (255,), width=3)
        cx = sum(point[0] for point in polygon) / len(polygon)
        cy = sum(point[1] for point in polygon) / len(polygon)
        label = f"{zone['id']} | {','.join(zone['capabilities'])} | {zone['depthClass']}"
        draw.text((cx, cy), label, fill=(15, 15, 15, 255), font=font, anchor="mm")
    support_width = max(4, round(size[1] / 260))
    for surface in data.get("supportSurfaces", []):
        for contact in surface["contacts"]:
            points = [tuple(point) for point in contact["polyline"]]
            draw.line(points, fill=(0, 220, 255, 255), width=support_width)
            draw.text(
                points[0],
                f"{surface['id']} | {','.join(contact['regions'])}",
                fill=(0, 235, 255, 255),
                font=font,
            )
    for placement in data["placements"]:
        x, y = placement["anchor"]
        radius = max(5, round(size[1] / 100))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 20, 80, 255))
        draw.text((x + radius + 3, y), str(placement["actorId"]), fill=(10, 10, 10, 255), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(base, overlay).save(output)


def _rect_mask(size: tuple[int, int], bbox: list[float]) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle(tuple(bbox), fill=255)
    return mask


def _obstruction_mask(
    reference: Image.Image, background: tuple[int, int, int], tolerance: int
) -> Image.Image:
    rgb = reference.convert("RGB")
    solid = Image.new("RGB", rgb.size, background)
    difference = ImageChops.difference(rgb, solid).convert("L")
    rgb_mask = difference.point(lambda value: 255 if value > tolerance else 0)
    # Transparent padding can retain arbitrary RGB values (commonly black).
    # It is not visible UI and must not become a false obstruction after an
    # RGBA reference is expanded to a wider scene canvas.
    alpha_mask = reference.getchannel("A").point(lambda value: 255 if value else 0)
    return ImageChops.multiply(rgb_mask, alpha_mask)


def _mask_ratio(mask: Image.Image, area_mask: Image.Image) -> float:
    area_pixels = area_mask.histogram()[255]
    if area_pixels == 0:
        return 0.0
    intersection = ImageChops.multiply(mask, area_mask)
    return intersection.histogram()[255] / area_pixels


def validate_ui_safety(
    contract_path: Path,
    report_path: Path | None = None,
    preview_path: Path | None = None,
) -> dict[str, Any]:
    data = load_json(contract_path)
    require_fields(data, ("schema", "sceneSize", "uiReferences", "actors"), "uiSafety")
    if data["schema"] != "ndc-ui-safety/v1":
        raise ValueError("uiSafety.schema must be ndc-ui-safety/v1.")
    size = tuple(data["sceneSize"])
    threshold = data.get("maskThreshold", {})
    background = tuple(threshold.get("backgroundRgb", [255, 255, 255]))
    tolerance = int(threshold.get("tolerance", 12))
    limits = data.get("limits", {})
    head_limit = float(limits.get("maxHeadOcclusionRatio", 0.0))
    action_limit = float(limits.get("maxActionOcclusionRatio", 0.20))
    references: dict[str, tuple[Image.Image, Image.Image]] = {}
    for side in ("left", "right"):
        raw_path = data["uiReferences"].get(side)
        if not raw_path:
            raise ValueError(f"uiSafety.uiReferences.{side} is required.")
        image = Image.open(resolve_path(raw_path, contract_path)).convert("RGBA")
        if image.size != size:
            raise ValueError(f"UI reference {side} size {image.size} differs from {size}.")
        references[side] = (image, _obstruction_mask(image, background, tolerance))
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    for index, actor in enumerate(data["actors"]):
        label = f"actors[{index}]"
        require_fields(actor, ("actorId", "uiSide", "headBBox", "actionBBox", "criticalPoints"), label)
        side = actor["uiSide"]
        if side not in references:
            raise ValueError(f"{label}.uiSide must be left or right.")
        mask = references[side][1]
        head_ratio = _mask_ratio(mask, _rect_mask(size, actor["headBBox"]))
        action_ratio = _mask_ratio(mask, _rect_mask(size, actor["actionBBox"]))
        blocked_points = []
        for point in actor["criticalPoints"]:
            name = str(point["name"])
            x, y = (round(float(value)) for value in point["point"])
            if not (0 <= x < size[0] and 0 <= y < size[1]):
                raise ValueError(f"{label} critical point {name} is outside sceneSize.")
            if mask.getpixel((x, y)):
                blocked_points.append(name)
        actor_result = {
            "actorId": actor["actorId"],
            "uiSide": side,
            "headOcclusionRatio": round(head_ratio, 6),
            "actionOcclusionRatio": round(action_ratio, 6),
            "blockedCriticalPoints": blocked_points,
            "status": "pass",
        }
        if head_ratio > head_limit or action_ratio > action_limit or blocked_points:
            actor_result["status"] = "fail"
            failures.append(str(actor["actorId"]))
        results.append(actor_result)
    report = {
        "schema": "ndc-ui-safety-report/v1",
        "contract": str(contract_path.resolve()),
        "contractSha256": sha256(contract_path),
        "limits": {
            "maxHeadOcclusionRatio": head_limit,
            "maxActionOcclusionRatio": action_limit,
        },
        "actors": results,
        "status": "fail" if failures else "pass",
    }
    if report_path:
        write_json(report_path, report)
    if preview_path:
        base_raw = data.get("scene")
        if base_raw:
            canvas = Image.open(resolve_path(base_raw, contract_path)).convert("RGBA")
            if canvas.size != size:
                raise ValueError("UI preview scene size differs from sceneSize.")
        else:
            canvas = Image.new("RGBA", size, (242, 242, 242, 255))
        draw = ImageDraw.Draw(canvas)
        for actor in data["actors"]:
            ui_image, mask = references[actor["uiSide"]]
            alpha = mask.point(lambda value: 190 if value else 0)
            overlay = ui_image.copy()
            overlay.putalpha(alpha)
            canvas = Image.alpha_composite(canvas, overlay)
            draw = ImageDraw.Draw(canvas)
            draw.rectangle(tuple(actor["headBBox"]), outline=(0, 220, 80, 255), width=4)
            draw.rectangle(tuple(actor["actionBBox"]), outline=(255, 170, 0, 255), width=4)
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(preview_path)
    if failures:
        raise ValueError(f"UI safety failed for actors: {', '.join(failures)}")
    return report


def _alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("State image has empty alpha.")
    return bbox


def verify_exploration_states(
    contract_path: Path,
    idle_path: Path,
    active_path: Path,
    output_dir: Path | None,
) -> dict[str, Any]:
    data = load_json(contract_path)
    require_fields(
        data,
        (
            "schema",
            "interactionType",
            "assemblyMode",
            "assetCanvasSize",
            "idleAttentionTarget",
            "activeAttentionTarget",
            "supportAnchors",
            "reuseMasterTransform",
            "statesIndependentlyNormalized",
            "stateDeltaScope",
            "visualReview",
        ),
        "interactionState",
    )
    if data["schema"] != "ndc-exploration-state-pair/v1":
        raise ValueError("State schema must be ndc-exploration-state-pair/v1.")
    if data["interactionType"] != "exploration-click-pair":
        raise ValueError("This validator is only for exploration click-state pairs.")
    if data["assemblyMode"] not in {
        "registered-local-patch",
        "exact-master-canvas",
        "registered-complete-state",
    }:
        raise ValueError("Unsupported exploration state assemblyMode.")
    if data["idleAttentionTarget"] == "player":
        raise ValueError("Idle exploration state must not already perform to the player.")
    if data["activeAttentionTarget"] != "player":
        raise ValueError("Active exploration state must visibly engage the player.")
    if data["reuseMasterTransform"] is not True:
        raise ValueError("Exploration states must reuse the accepted idle master transform.")
    if data["statesIndependentlyNormalized"] is not False:
        raise ValueError("Exploration states must never be normalized independently by alpha boxes.")
    delta_scope = data["stateDeltaScope"]
    require_fields(
        delta_scope,
        ("regions", "wholeBodyAuthorized", "reason"),
        "interactionState.stateDeltaScope",
    )
    if not isinstance(delta_scope["regions"], list) or not delta_scope["regions"]:
        raise ValueError("interactionState.stateDeltaScope.regions cannot be empty.")
    if "whole-body" in delta_scope["regions"] and delta_scope["wholeBodyAuthorized"] is not True:
        raise ValueError("A whole-body exploration delta requires wholeBodyAuthorized=true.")
    visual_review = data["visualReview"]
    required_visual_checks = (
        "identityContinuity",
        "supportAndShadowContinuity",
        "stateReadability",
        "edgeContinuity",
        "flicker",
    )
    require_fields(
        visual_review,
        ("reviewAuthority", *required_visual_checks),
        "interactionState.visualReview",
    )
    if visual_review["reviewAuthority"] != "codex-self-check":
        raise ValueError("Exploration visual review authority must be codex-self-check.")
    failed_visual = [name for name in required_visual_checks if visual_review[name] != "pass"]
    if failed_visual:
        raise ValueError("Exploration visual review failed: " + ", ".join(failed_visual))
    idle = Image.open(idle_path).convert("RGBA")
    active = Image.open(active_path).convert("RGBA")
    expected_size = tuple(data["assetCanvasSize"])
    if idle.size != expected_size or active.size != expected_size:
        raise ValueError(
            f"State canvas mismatch: idle={idle.size}, active={active.size}, expected={expected_size}."
        )
    for label, image in (("idle", idle), ("active", active)):
        alpha = image.getchannel("A")
        corners = (
            alpha.getpixel((0, 0)),
            alpha.getpixel((image.width - 1, 0)),
            alpha.getpixel((0, image.height - 1)),
            alpha.getpixel((image.width - 1, image.height - 1)),
        )
        if corners != (0, 0, 0, 0):
            raise ValueError(f"{label} state has nontransparent corners.")
    anchor_results = []
    for index, anchor in enumerate(data["supportAnchors"]):
        require_fields(anchor, ("name", "idle", "active", "tolerancePx"), f"supportAnchors[{index}]")
        dx = float(anchor["active"][0]) - float(anchor["idle"][0])
        dy = float(anchor["active"][1]) - float(anchor["idle"][1])
        distance = math.hypot(dx, dy)
        tolerance = float(anchor["tolerancePx"])
        if distance > tolerance:
            raise ValueError(
                f"Support anchor {anchor['name']} shifted {distance:.2f}px; tolerance={tolerance:.2f}px."
            )
        anchor_results.append(
            {"name": anchor["name"], "shiftPx": round(distance, 4), "tolerancePx": tolerance}
        )
    if not anchor_results:
        raise ValueError("At least one support anchor is required.")
    for rectangle in data.get("frozenRectangles", []):
        box = tuple(int(value) for value in rectangle)
        if ImageChops.difference(idle.crop(box), active.crop(box)).getbbox() is not None:
            raise ValueError(f"Frozen exploration-state rectangle changed: {box}")
    idle_bbox = _alpha_bbox(idle)
    active_bbox = _alpha_bbox(active)
    max_support_drift = float(data.get("maxAlphaSupportDriftPx", 4.0))
    alpha_bottom_drift = abs(active_bbox[3] - idle_bbox[3])
    if alpha_bottom_drift > max_support_drift:
        raise ValueError(
            f"Alpha support bottom drifted {alpha_bottom_drift}px; limit={max_support_drift}px."
        )
    raw_difference = ImageChops.difference(idle, active)
    difference_bands = raw_difference.split()
    difference_mask = difference_bands[0]
    for band in difference_bands[1:]:
        difference_mask = ImageChops.lighter(difference_mask, band)
    difference_mask = difference_mask.point(lambda value: 255 if value > 6 else 0)
    changed_pixels = difference_mask.histogram()[255]
    outside_allowed_change_pixels = 0
    allowed_change_masks = data.get("allowedChangeMasks", [])
    if data["assemblyMode"] in {"registered-local-patch", "exact-master-canvas"}:
        if not isinstance(allowed_change_masks, list) or not allowed_change_masks:
            raise ValueError(
                "Patch and exact-master exploration states require allowedChangeMasks."
            )
        allowed = Image.new("L", idle.size, 0)
        allowed_draw = ImageDraw.Draw(allowed)
        for index, item in enumerate(allowed_change_masks):
            require_fields(item, ("label", "bbox"), f"allowedChangeMasks[{index}]")
            bbox = tuple(int(round(float(value))) for value in item["bbox"])
            if len(bbox) != 4 or not (0 <= bbox[0] < bbox[2] <= idle.width and 0 <= bbox[1] < bbox[3] <= idle.height):
                raise ValueError(f"allowedChangeMasks[{index}].bbox is invalid: {bbox}")
            allowed_draw.rectangle(bbox, fill=255)
        outside = ImageChops.multiply(difference_mask, ImageChops.invert(allowed))
        outside_allowed_change_pixels = outside.histogram()[255]
        if outside_allowed_change_pixels:
            raise ValueError(
                "Exploration state changed pixels outside allowedChangeMasks: "
                f"{outside_allowed_change_pixels}."
            )
    report = {
        "schema": "ndc-exploration-state-report/v1",
        "contract": str(contract_path.resolve()),
        "idle": str(idle_path.resolve()),
        "active": str(active_path.resolve()),
        "idleSha256": sha256(idle_path),
        "activeSha256": sha256(active_path),
        "assemblyMode": data["assemblyMode"],
        "idleAlphaBBox": idle_bbox,
        "activeAlphaBBox": active_bbox,
        "alphaSupportBottomDriftPx": alpha_bottom_drift,
        "stateDeltaScope": delta_scope,
        "changedPixelRatio": round(changed_pixels / (idle.width * idle.height), 6),
        "changedBBox": difference_mask.getbbox(),
        "outsideAllowedChangePixels": outside_allowed_change_pixels,
        "supportAnchors": anchor_results,
        "status": "pass",
        "visualReview": visual_review,
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        overlay = Image.blend(idle, active, 0.5)
        overlay.save(output_dir / "state-overlay.png")
        diff = ImageChops.difference(idle, active)
        diff.save(output_dir / "state-difference.png")
        idle.convert("P", palette=Image.Palette.ADAPTIVE).save(
            output_dir / "state-flicker.gif",
            save_all=True,
            append_images=[active.convert("P", palette=Image.Palette.ADAPTIVE)],
            duration=[500, 500],
            loop=0,
            disposal=2,
        )
        write_json(output_dir / "state-report.json", report)
    return report


def _ui_overlay(reference: Image.Image, tolerance: int = 12) -> Image.Image:
    mask = _obstruction_mask(reference, (255, 255, 255), tolerance)
    overlay = reference.convert("RGBA")
    overlay.putalpha(mask)
    return overlay


def render_timeline_board(contract_path: Path, output_dir: Path) -> None:
    data = load_json(contract_path)
    require_fields(data, ("schema", "sceneSize", "uiReferences", "snapshots"), "timelineBoard")
    if data["schema"] != "ndc-timeline-board/v1":
        raise ValueError("timelineBoard.schema must be ndc-timeline-board/v1.")
    size = tuple(data["sceneSize"])
    output_dir.mkdir(parents=True, exist_ok=True)
    ui_refs = {
        side: Image.open(resolve_path(path, contract_path)).convert("RGBA")
        for side, path in data["uiReferences"].items()
    }
    for side, image in ui_refs.items():
        if image.size != size:
            raise ValueError(f"Timeline-board UI {side} size differs from sceneSize.")
    frames: list[Image.Image] = []
    for index, snapshot in enumerate(data["snapshots"]):
        require_fields(snapshot, ("id", "image", "uiSide", "caption"), f"snapshots[{index}]")
        frame = Image.open(resolve_path(snapshot["image"], contract_path)).convert("RGBA")
        if frame.size != size:
            raise ValueError(f"Snapshot {snapshot['id']} size differs from sceneSize.")
        side = snapshot["uiSide"]
        if side not in ui_refs:
            raise ValueError(f"Snapshot {snapshot['id']} references unknown UI side {side}.")
        frame = Image.alpha_composite(frame, _ui_overlay(ui_refs[side]))
        label_h = max(44, round(size[1] * 0.05))
        draw = ImageDraw.Draw(frame)
        draw.rectangle((0, 0, size[0], label_h), fill=(0, 0, 0, 190))
        draw.text(
            (16, label_h / 2),
            f"{index + 1:02d} {snapshot['id']} | {snapshot['caption']}",
            fill=(255, 255, 255, 255),
            font=_font(max(14, round(label_h * 0.42))),
            anchor="lm",
        )
        frame_path = output_dir / f"{index + 1:02d}_{snapshot['id']}.png"
        frame.save(frame_path)
        frames.append(frame)
    if not frames:
        raise ValueError("timelineBoard.snapshots cannot be empty.")
    columns = min(2, len(frames))
    rows = math.ceil(len(frames) / columns)
    thumb_width = min(1280, size[0])
    thumb_height = round(size[1] * thumb_width / size[0])
    sheet = Image.new("RGBA", (thumb_width * columns, thumb_height * rows), (24, 24, 24, 255))
    for index, frame in enumerate(frames):
        thumb = frame.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        sheet.alpha_composite(thumb, ((index % columns) * thumb_width, (index // columns) * thumb_height))
    sheet.save(output_dir / "timeline-contact-sheet.png")


def _zone_candidate_anchors(zone: dict[str, Any], limit: int) -> list[list[float]]:
    polygon = zone["polygon"]
    min_x = min(float(point[0]) for point in polygon)
    max_x = max(float(point[0]) for point in polygon)
    min_y = min(float(point[1]) for point in polygon)
    max_y = max(float(point[1]) for point in polygon)
    anchors: list[list[float]] = []
    # Prefer lower/support-facing portions of a zone before its geometric center.
    for y_ratio in (0.82, 0.68, 0.54, 0.40):
        for x_ratio in (0.50, 0.32, 0.68, 0.20, 0.80):
            point = [min_x + (max_x - min_x) * x_ratio, min_y + (max_y - min_y) * y_ratio]
            if _point_in_polygon((point[0], point[1]), polygon):
                rounded = [round(point[0], 2), round(point[1], 2)]
                if rounded not in anchors:
                    anchors.append(rounded)
            if len(anchors) >= limit:
                return anchors
    centroid = [
        sum(float(point[0]) for point in polygon) / len(polygon),
        sum(float(point[1]) for point in polygon) / len(polygon),
    ]
    if _point_in_polygon((centroid[0], centroid[1]), polygon) and centroid not in anchors:
        anchors.append(centroid)
    return anchors[:limit]


def _approach(origin: list[float], target: list[float], distance: float) -> list[float]:
    dx = float(target[0]) - float(origin[0])
    dy = float(target[1]) - float(origin[1])
    length = math.hypot(dx, dy) or 1.0
    return [origin[0] + dx / length * distance, origin[1] + dy / length * distance]


def synthesize_pose(
    placement_class: str,
    preset: str,
    anchor: list[float],
    height: float,
    facing_sign: int,
    action_target: list[float],
) -> dict[str, Any]:
    """Create reproducible anatomical landmarks from a semantic pose preset."""
    x, y = (float(value) for value in anchor)
    sign = 1 if facing_sign >= 0 else -1
    if placement_class in {"standing", "walking", "leaning"}:
        top = y - height
        head_h = height * 0.125
        head_w = head_h * 0.78
        torso_shift = 0.0
        if preset in {"lean-observe", "reach-target"}:
            torso_shift = sign * height * 0.045
        head_cx = x + torso_shift + sign * height * 0.018
        points = {
            "neck": [x + torso_shift, top + height * 0.155],
            "leftShoulder": [x - height * 0.115 + torso_shift, top + height * 0.205],
            "rightShoulder": [x + height * 0.125 + torso_shift, top + height * 0.192],
            "leftHip": [x - height * 0.070, top + height * 0.545],
            "rightHip": [x + height * 0.074, top + height * 0.555],
            "leftKnee": [x - height * 0.082, top + height * 0.765],
            "rightKnee": [x + height * 0.055, top + height * 0.785],
            "leftFoot": [x - height * 0.090, y],
            "rightFoot": [x + height * 0.095, y - height * 0.008],
        }
        if preset == "guarded-hold":
            points.update(
                {
                    "leftElbow": [x - height * 0.145, top + height * 0.385],
                    "rightElbow": [x + height * 0.145, top + height * 0.370],
                    "leftHand": [x - height * 0.055, top + height * 0.445],
                    "rightHand": [x + height * 0.045, top + height * 0.430],
                }
            )
        elif preset == "reach-target":
            shoulder_name = "rightShoulder" if sign > 0 else "leftShoulder"
            reach_shoulder = points[shoulder_name]
            elbow = _approach(reach_shoulder, action_target, height * 0.23)
            hand = _approach(reach_shoulder, action_target, height * 0.39)
            if sign > 0:
                points.update(
                    {
                        "rightElbow": elbow,
                        "rightHand": hand,
                        "leftElbow": [x - height * 0.155, top + height * 0.405],
                        "leftHand": [x - height * 0.085, top + height * 0.515],
                    }
                )
            else:
                points.update(
                    {
                        "leftElbow": elbow,
                        "leftHand": hand,
                        "rightElbow": [x + height * 0.155, top + height * 0.405],
                        "rightHand": [x + height * 0.085, top + height * 0.515],
                    }
                )
        elif preset == "enter-walk":
            points.update(
                {
                    "leftElbow": [x - height * 0.130, top + height * 0.360],
                    "rightElbow": [x + height * 0.165, top + height * 0.375],
                    "leftHand": [x - height * 0.045, top + height * 0.490],
                    "rightHand": [x + height * 0.095, top + height * 0.515],
                    "leftKnee": [x - sign * height * 0.125, top + height * 0.755],
                    "rightKnee": [x + sign * height * 0.105, top + height * 0.805],
                    "leftFoot": [x - sign * height * 0.175, y - height * 0.008],
                    "rightFoot": [x + sign * height * 0.145, y],
                }
            )
        elif preset == "lean-observe":
            support_hand = _approach(points["rightShoulder" if sign > 0 else "leftShoulder"], action_target, height * 0.34)
            points.update(
                {
                    "leftElbow": [x - height * 0.155 + torso_shift, top + height * 0.385],
                    "rightElbow": [x + height * 0.150 + torso_shift, top + height * 0.365],
                    "leftHand": [x - height * 0.075 + torso_shift, top + height * 0.505],
                    "rightHand": [x + height * 0.075 + torso_shift, top + height * 0.490],
                }
            )
            points["rightHand" if sign > 0 else "leftHand"] = support_hand
        else:  # attentive-task and any explicitly permitted restrained variation
            points.update(
                {
                    "leftElbow": [x - height * 0.145, top + height * 0.365],
                    "rightElbow": [x + height * 0.155, top + height * 0.405],
                    "leftHand": [x - height * 0.085, top + height * 0.500],
                    "rightHand": [x + height * 0.045, top + height * 0.525],
                }
            )
        return {
            "headBox": [
                head_cx - head_w / 2,
                top,
                head_cx + head_w / 2,
                top + head_h,
            ],
            **points,
        }

    if placement_class == "seated":
        top = y - height * 0.72
        head_h = height * 0.125
        head_w = head_h * 0.78
        hip_y = y - height * 0.34
        points = {
            "neck": [x + sign * height * 0.025, top + height * 0.150],
            "leftShoulder": [x - height * 0.115, top + height * 0.200],
            "rightShoulder": [x + height * 0.125, top + height * 0.188],
            "leftElbow": [x - height * 0.150, top + height * 0.355],
            "rightElbow": [x + height * 0.145, top + height * 0.375],
            "leftHand": [x - height * 0.045, top + height * 0.455],
            "rightHand": [x + height * 0.065, top + height * 0.445],
            "leftHip": [x - height * 0.075, hip_y],
            "rightHip": [x + height * 0.075, hip_y + height * 0.008],
            "leftKnee": [x - height * 0.120, y - height * 0.175],
            "rightKnee": [x + height * 0.145, y - height * 0.155],
            "leftFoot": [x - height * 0.160, y],
            "rightFoot": [x + height * 0.175, y - height * 0.006],
            "hipSeat": [x, hip_y + height * 0.015],
        }
        if preset == "seated-engage":
            shoulder = points["rightShoulder" if sign > 0 else "leftShoulder"]
            elbow = _approach(shoulder, action_target, height * 0.20)
            hand = _approach(shoulder, action_target, height * 0.34)
            points["rightElbow" if sign > 0 else "leftElbow"] = elbow
            points["rightHand" if sign > 0 else "leftHand"] = hand
        return {
            "headBox": [
                x - head_w / 2 + sign * height * 0.025,
                top,
                x + head_w / 2 + sign * height * 0.025,
                top + head_h,
            ],
            **points,
        }

    if placement_class == "lying":
        direction = sign
        head_h = height * 0.125
        head_cx = x - direction * height * 0.39
        base_y = y - height * 0.13
        points = {
            "neck": [head_cx + direction * height * 0.09, base_y - height * 0.01],
            "leftShoulder": [head_cx + direction * height * 0.14, base_y - height * 0.07],
            "rightShoulder": [head_cx + direction * height * 0.15, base_y + height * 0.055],
            "leftElbow": [x - direction * height * 0.08, base_y - height * 0.11],
            "rightElbow": [x - direction * height * 0.05, base_y + height * 0.10],
            "leftHand": [x + direction * height * 0.04, base_y - height * 0.08],
            "rightHand": [x + direction * height * 0.07, base_y + height * 0.08],
            "leftHip": [x + direction * height * 0.10, base_y - height * 0.04],
            "rightHip": [x + direction * height * 0.11, base_y + height * 0.05],
            "leftKnee": [x + direction * height * 0.29, base_y - height * 0.02],
            "rightKnee": [x + direction * height * 0.30, base_y + height * 0.06],
            "leftFoot": [x + direction * height * 0.48, base_y - height * 0.015],
            "rightFoot": [x + direction * height * 0.47, base_y + height * 0.065],
            "hip": [x + direction * height * 0.105, base_y],
            "bodyAxis": [[head_cx, base_y], [x + direction * height * 0.48, base_y]],
        }
        return {
            "headBox": [
                head_cx - head_h * 0.55,
                base_y - head_h * 0.50,
                head_cx + head_h * 0.55,
                base_y + head_h * 0.50,
            ],
            **points,
        }
    raise ValueError(f"Cannot synthesize unsupported placementClass: {placement_class}")


def _pose_outer_bbox(pose: dict[str, Any], margin: float, size: tuple[int, int]) -> list[float]:
    points = [pose[name] for name in POSE_POINTS if name in pose]
    head = pose["headBox"]
    xs = [float(point[0]) for point in points] + [float(head[0]), float(head[2])]
    ys = [float(point[1]) for point in points] + [float(head[1]), float(head[3])]
    return [
        max(0.0, min(xs) - margin),
        max(0.0, min(ys) - margin),
        min(float(size[0]), max(xs) + margin),
        min(float(size[1]), max(ys) + margin),
    ]


def _draw_pose(frame: Image.Image, pose: dict[str, Any], outer_bbox: list[float], label: str) -> None:
    draw = ImageDraw.Draw(frame)
    bone_pairs = (
        ("neck", "leftShoulder"), ("neck", "rightShoulder"),
        ("leftShoulder", "leftElbow"), ("leftElbow", "leftHand"),
        ("rightShoulder", "rightElbow"), ("rightElbow", "rightHand"),
        ("leftShoulder", "leftHip"), ("rightShoulder", "rightHip"),
        ("leftHip", "rightHip"), ("leftHip", "leftKnee"),
        ("leftKnee", "leftFoot"), ("rightHip", "rightKnee"),
        ("rightKnee", "rightFoot"),
    )
    width = max(3, round(frame.height / 220))
    radius = max(4, round(frame.height / 170))
    for first, second in bone_pairs:
        if first in pose and second in pose:
            draw.line((tuple(pose[first]), tuple(pose[second])), fill=(255, 45, 78, 255), width=width)
    for name in POSE_POINTS:
        if name in pose:
            x, y = pose[name]
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 45, 78, 255))
    draw.rectangle(tuple(pose["headBox"]), outline=(255, 45, 78, 255), width=width)
    draw.rectangle(tuple(outer_bbox), outline=(255, 202, 40, 255), width=width)
    draw.text((outer_bbox[0], max(0, outer_bbox[1] - 22)), label, fill=(255, 255, 255, 255), font=_font(18))


def build_blocking_candidates(contract_path: Path, output_dir: Path) -> dict[str, Any]:
    data = load_json(contract_path)
    require_fields(
        data,
        (
            "schema", "scene", "sceneSize", "actorId", "placementClass",
            "standingEquivalentHeightPx", "affordanceContract", "zoneId",
            "posePresets", "facing", "gazePoint", "actionTarget", "uiSide",
            "uiReferences", "performance",
        ),
        "blockingRequest",
    )
    if data["schema"] != "ndc-blocking-request/v1":
        raise ValueError("blockingRequest.schema must be ndc-blocking-request/v1.")
    require_fields(
        data["performance"],
        (
            "action", "gazeTarget", "leftHandAction", "rightHandAction", "supportObject",
            "beatEnergy", "silentFrameVerb", "ongoingOccupation", "performanceFamily",
            "gestureMotivation", "namedSupport", "socialTerritory", "tenSecondHold",
            "depthHonesty",
        ),
        "blockingRequest.performance",
    )
    performance = data["performance"]
    if performance["beatEnergy"] not in {"still", "low", "medium", "high"}:
        raise ValueError("blockingRequest.performance.beatEnergy is unsupported.")
    if performance["performanceFamily"] not in {
        "ongoing-occupation", "supported-hold", "transition", "confrontational-action"
    }:
        raise ValueError("blockingRequest.performance.performanceFamily is unsupported.")
    if performance["tenSecondHold"] != "pass" or performance["depthHonesty"] != "pass":
        raise ValueError("Blocking requires tenSecondHold=pass and depthHonesty=pass.")
    require_fields(
        performance["gestureMotivation"],
        ("leftHand", "rightHand"),
        "blockingRequest.performance.gestureMotivation",
    )
    size = tuple(data["sceneSize"])
    height = float(data["standingEquivalentHeightPx"])
    if height <= 0:
        raise ValueError("standingEquivalentHeightPx must be positive.")
    affordance_path = resolve_path(data["affordanceContract"], contract_path)
    affordance = load_json(affordance_path)
    validate_affordance(affordance)
    if tuple(affordance["sceneSize"]) != size:
        raise ValueError("Blocking and affordance sceneSize differ.")
    zones = {str(zone["id"]): zone for zone in affordance["zones"]}
    zone = zones.get(str(data["zoneId"]))
    if not zone:
        raise ValueError(f"Unknown blocking zoneId: {data['zoneId']}")
    capability = CAPABILITY_BY_PLACEMENT.get(data["placementClass"])
    if capability not in zone["capabilities"]:
        raise ValueError("Blocking placementClass is incompatible with the selected affordance zone.")
    max_candidates = int(data.get("maxCandidates", 12))
    raw_anchors = data.get("candidateAnchors") or _zone_candidate_anchors(zone, max_candidates)
    anchors = [
        [float(point[0]), float(point[1])]
        for point in raw_anchors
        if _point_in_polygon((float(point[0]), float(point[1])), zone["polygon"])
    ]
    if not anchors:
        raise ValueError("No candidate anchor falls inside the selected affordance zone.")
    facing_sign = 1 if data["facing"] == "right" else -1
    ui_side = str(data["uiSide"])
    if ui_side not in data["uiReferences"]:
        raise ValueError("Blocking uiSide has no matching uiReferences entry.")
    ui_image = Image.open(resolve_path(data["uiReferences"][ui_side], contract_path)).convert("RGBA")
    if ui_image.size != size:
        raise ValueError("Blocking UI reference size differs from sceneSize.")
    ui_mask = _obstruction_mask(ui_image, (255, 255, 255), int(data.get("uiTolerance", 12)))
    action_target = [float(value) for value in data["actionTarget"]]
    margin = height * float(data.get("outerMarginRatio", 0.04))
    candidates: list[dict[str, Any]] = []
    for anchor_index, anchor in enumerate(anchors):
        for preset_index, preset in enumerate(data["posePresets"]):
            pose = synthesize_pose(
                str(data["placementClass"]), str(preset), anchor, height, facing_sign, action_target
            )
            outer = _pose_outer_bbox(pose, margin, size)
            head_ratio = _mask_ratio(ui_mask, _rect_mask(size, pose["headBox"]))
            action_ratio = _mask_ratio(ui_mask, _rect_mask(size, outer))
            critical_blocked = []
            for name in ("leftHand", "rightHand"):
                px, py = (round(float(value)) for value in pose[name])
                if not (0 <= px < size[0] and 0 <= py < size[1]) or ui_mask.getpixel((px, py)):
                    critical_blocked.append(name)
            center_distance = math.hypot(anchor[0] - action_target[0], anchor[1] - action_target[1])
            # UI and face/hand readability dominate. Distance only breaks physically valid ties.
            score = (
                head_ratio * 10000
                + len(critical_blocked) * 1000
                + action_ratio * 500
                + center_distance / max(size) * 25
                + anchor_index * 0.01
                + preset_index * 0.001
            )
            pose_key = (
                "seatedPose" if data["placementClass"] == "seated"
                else "lyingPose" if data["placementClass"] == "lying"
                else "standingPose"
            )
            fragment = {
                "schema": "ndc-auto-blocking-candidate/v1",
                "actorId": data["actorId"],
                "sceneSize": list(size),
                "target": {
                    "placementClass": data["placementClass"],
                    "depthClass": zone["depthClass"],
                    "affordanceZoneId": data["zoneId"],
                    **({"contactPoint": anchor} if data["placementClass"] == "lying" else {"foot": anchor}),
                    "standingEquivalentHeightPx": height,
                    "outerBBox": [round(value, 2) for value in outer],
                    "poseDefinition": {
                        "poseId": f"{data['actorId']}-{preset}-a{anchor_index + 1}",
                        "action": data["performance"]["action"],
                        "facing": data["facing"],
                        "gazeTarget": data["performance"]["gazeTarget"],
                        "leftHandAction": data["performance"]["leftHandAction"],
                        "rightHandAction": data["performance"]["rightHandAction"],
                        "requiredProps": data["performance"].get("requiredProps", []),
                        "beatEnergy": data["performance"]["beatEnergy"],
                        "silentFrameVerb": data["performance"]["silentFrameVerb"],
                        "ongoingOccupation": data["performance"]["ongoingOccupation"],
                        "performanceFamily": data["performance"]["performanceFamily"],
                        "gestureMotivation": data["performance"]["gestureMotivation"],
                        "namedSupport": data["performance"]["namedSupport"],
                        "socialTerritory": data["performance"]["socialTerritory"],
                        "preset": preset,
                    },
                    pose_key: {
                        **{
                            key: [round(float(value), 2) for value in point]
                            for key, point in pose.items()
                            if key != "bodyAxis"
                        },
                        **(
                            {"bodyAxis": [[round(float(value), 2) for value in point] for point in pose["bodyAxis"]]}
                            if "bodyAxis" in pose else {}
                        ),
                        "supportObject": data["performance"]["supportObject"],
                    },
                },
                "gazePoint": data["gazePoint"],
                "automaticScore": {
                    "lowerIsBetter": True,
                    "value": round(score, 6),
                    "headUiOcclusionRatio": round(head_ratio, 6),
                    "actionUiOcclusionRatio": round(action_ratio, 6),
                    "blockedCriticalLandmarks": critical_blocked,
                    "actionTargetDistancePx": round(center_distance, 2),
                },
            }
            candidates.append({"score": score, "pose": pose, "outer": outer, "fragment": fragment})
    candidates.sort(key=lambda candidate: candidate["score"])
    candidates = candidates[:max_candidates]
    output_dir.mkdir(parents=True, exist_ok=True)
    base = Image.open(resolve_path(data["scene"], contract_path)).convert("RGBA")
    if base.size != size:
        raise ValueError("Blocking scene size differs from sceneSize.")
    overlay = _ui_overlay(ui_image)
    preview_frames: list[Image.Image] = []
    report_candidates = []
    for rank, candidate in enumerate(candidates, start=1):
        fragment = candidate["fragment"]
        fragment_path = output_dir / f"candidate-{rank:02d}.json"
        write_json(fragment_path, fragment)
        frame = Image.alpha_composite(base.copy(), overlay)
        _draw_pose(
            frame,
            candidate["pose"],
            candidate["outer"],
            f"#{rank} {fragment['target']['poseDefinition']['preset']}",
        )
        frame.save(output_dir / f"candidate-{rank:02d}.png")
        preview_frames.append(frame)
        report_candidates.append(
            {
                "rank": rank,
                "contract": fragment_path.name,
                "preview": f"candidate-{rank:02d}.png",
                "poseId": fragment["target"]["poseDefinition"]["poseId"],
                "automaticScore": fragment["automaticScore"],
            }
        )
    columns = min(2, len(preview_frames))
    rows = math.ceil(len(preview_frames) / columns)
    thumb_w = min(960, size[0])
    thumb_h = round(size[1] * thumb_w / size[0])
    sheet = Image.new("RGBA", (thumb_w * columns, thumb_h * rows), (20, 20, 20, 255))
    for index, frame in enumerate(preview_frames):
        thumb = frame.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.alpha_composite(thumb, ((index % columns) * thumb_w, (index // columns) * thumb_h))
    sheet.save(output_dir / "blocking-candidates.png")
    report = {
        "schema": "ndc-blocking-candidate-report/v1",
        "request": str(contract_path.resolve()),
        "requestSha256": sha256(contract_path),
        "rankingRule": "UI face/hands, action-envelope UI ratio, then action-target distance; lower is better",
        "candidateCount": len(report_candidates),
        "candidates": report_candidates,
        "status": "review-required",
        "codexReviewRequired": [
            "story-beat and silent-frame readability",
            "performance naturalism, motivated hands, and ten-second hold",
            "ongoing occupation, named support, and social territory",
            "beat-energy compatibility and depth honesty",
            "support/contact correctness",
            "perspective and scale-anchor conformance",
            "occlusion and entrance-path logic",
        ],
    }
    write_json(output_dir / "blocking-report.json", report)
    return report


def prepare_local_generation_handoff(contract_path: Path, output_dir: Path) -> dict[str, Any]:
    """Crop a locked full-scene whitebox into a reproducible local generation handoff."""
    data = load_json(contract_path)
    require_fields(
        data,
        (
            "schema", "actorId", "poseId", "scene", "whiteboxComposite",
            "characterCard", "actorBBox", "cropPaddingPx", "generationAspectRatio",
            "outputMode", "generationPrompt",
        ),
        "localGenerationHandoff",
    )
    if data["schema"] != "ndc-local-generation-handoff/v1":
        raise ValueError("localGenerationHandoff.schema must be ndc-local-generation-handoff/v1.")
    if data["outputMode"] != "contextual-local-replacement":
        raise ValueError(
            "localGenerationHandoff.outputMode must be contextual-local-replacement for the first pass."
        )
    scene_path = resolve_path(data["scene"], contract_path)
    whitebox_path = resolve_path(data["whiteboxComposite"], contract_path)
    card_path = resolve_path(data["characterCard"], contract_path)
    for label, path in (("scene", scene_path), ("whiteboxComposite", whitebox_path), ("characterCard", card_path)):
        if not path.is_file():
            raise ValueError(f"localGenerationHandoff.{label} does not exist: {path}")
    scene = Image.open(scene_path).convert("RGBA")
    whitebox = Image.open(whitebox_path).convert("RGBA")
    if whitebox.size != scene.size:
        raise ValueError("Scene and whiteboxComposite must share the original scene canvas.")
    if len(data["actorBBox"]) != 4:
        raise ValueError("localGenerationHandoff.actorBBox must contain four coordinates.")
    left, top, right, bottom = (int(round(float(value))) for value in data["actorBBox"])
    width, height = scene.size
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError("localGenerationHandoff.actorBBox must be inside the scene canvas.")
    padding = int(data["cropPaddingPx"])
    if padding < 0:
        raise ValueError("localGenerationHandoff.cropPaddingPx cannot be negative.")
    base_crop_box = (
        max(0, left - padding),
        max(0, top - padding),
        min(width, right + padding),
        min(height, bottom + padding),
    )
    aspect = data["generationAspectRatio"]
    if not isinstance(aspect, list) or len(aspect) != 2:
        raise ValueError("localGenerationHandoff.generationAspectRatio must contain [width, height].")
    aspect_w, aspect_h = (float(value) for value in aspect)
    if aspect_w <= 0 or aspect_h <= 0:
        raise ValueError("localGenerationHandoff.generationAspectRatio values must be positive.")
    requested_ratio = aspect_w / aspect_h
    base_left, base_top, base_right, base_bottom = base_crop_box
    base_width = base_right - base_left
    base_height = base_bottom - base_top
    target_width, target_height = base_width, base_height
    if base_width / base_height < requested_ratio:
        target_width = int(math.ceil(base_height * requested_ratio))
    else:
        target_height = int(math.ceil(base_width / requested_ratio))
    if target_width > width or target_height > height:
        raise ValueError(
            "Requested generationAspectRatio cannot contain the padded actor region inside the scene."
        )
    center_x = (base_left + base_right) / 2
    center_y = (base_top + base_bottom) / 2
    crop_left = min(max(0, int(round(center_x - target_width / 2))), width - target_width)
    crop_top = min(max(0, int(round(center_y - target_height / 2))), height - target_height)
    crop_box = (crop_left, crop_top, crop_left + target_width, crop_top + target_height)
    if not (
        crop_box[0] <= base_left
        and crop_box[1] <= base_top
        and crop_box[2] >= base_right
        and crop_box[3] >= base_bottom
    ):
        raise ValueError("Aspect-ratio expansion failed to retain the padded actor region.")
    output_dir.mkdir(parents=True, exist_ok=True)
    local_whitebox_path = output_dir / "image-1-local-whitebox.png"
    local_clean_path = output_dir / "local-clean-reference.png"
    whitebox.crop(crop_box).save(local_whitebox_path)
    scene.crop(crop_box).save(local_clean_path)
    report = {
        "schema": "ndc-local-generation-handoff-report/v1",
        "actorId": data["actorId"],
        "poseId": data["poseId"],
        "roles": {
            "image1": str(local_whitebox_path.resolve()),
            "image2": str(scene_path.resolve()),
            "image3": str(card_path.resolve()),
        },
        "localCleanReference": str(local_clean_path.resolve()),
        "originalSceneSize": list(scene.size),
        "cropBBox": list(crop_box),
        "basePaddedCropBBox": list(base_crop_box),
        "generationAspectRatio": [aspect_w, aspect_h],
        "actualCropAspectRatio": round(target_width / target_height, 6),
        "cropPolicy": "expand-original-pixels-no-resize",
        "outputMode": data["outputMode"],
        "actorBBoxOriginal": [left, top, right, bottom],
        "actorBBoxLocal": [left - crop_box[0], top - crop_box[1], right - crop_box[0], bottom - crop_box[1]],
        "photoshopPasteTopLeft": [crop_box[0], crop_box[1]],
        "sourceHashes": {
            "scene": sha256(scene_path),
            "whiteboxComposite": sha256(whitebox_path),
            "characterCard": sha256(card_path),
        },
        "generationPrompt": data["generationPrompt"],
        "status": "READY_FOR_CONTEXTUAL_LOCAL_GENERATION",
        "postGenerationRequired": [
            "approve the in-place contextual local replacement before any extraction",
            "identity-style comparison against image3",
            "pose-contact comparison against image1",
            "uniform-only registration after pose and contact pass",
            "exact source occluder masks including holes",
            "untouched full-scene reconstruction",
        ],
    }
    write_json(output_dir / "local-generation-handoff.json", report)
    return report


def _resolve_resource_asset(asset_root: Path, resource_path: str) -> Path:
    normalized = Path(*resource_path.replace("\\", "/").split("/"))
    path = asset_root / normalized
    if path.suffix:
        return path
    return path.with_suffix(".png")


def _image_metadata(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    with Image.open(path) as image:
        mode = image.mode
        size = list(image.size)
        has_alpha = "A" in image.getbands()
        transparent_corners = None
        if has_alpha:
            alpha = image.convert("RGBA").getchannel("A")
            transparent_corners = all(
                alpha.getpixel(point) == 0
                for point in ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1))
            )
    return {
        "path": str(path.resolve()),
        "exists": True,
        "sha256": sha256(path),
        "size": size,
        "mode": mode,
        "hasAlpha": has_alpha,
        "transparentCorners": transparent_corners,
    }


def _baseline_index(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for pair in report.get("npcPairs", []):
        index[f"npc:{pair['loopId']}"] = {
            "resPath": pair["resPath"],
            "clickResPath": pair["clickResPath"],
            "idleSha256": pair["idle"].get("sha256", ""),
            "activeSha256": pair["active"].get("sha256", ""),
            "idleSize": pair["idle"].get("size"),
            "activeSize": pair["active"].get("size"),
        }
    for background in report.get("backgrounds", []):
        index[f"background:{background['relativePath']}"] = {
            "sha256": background.get("sha256", ""),
            "size": background.get("size"),
        }
    for side, metadata in report.get("uiReferences", {}).items():
        index[f"ui:{side}"] = {
            "sha256": metadata.get("sha256", ""),
            "size": metadata.get("size"),
            "obstructionBBox": metadata.get("obstructionBBox"),
        }
    return index


def audit_project_assets(
    npc_loop_table: Path,
    asset_root: Path,
    background_root: Path,
    ui_left: Path,
    ui_right: Path,
    baseline_path: Path | None,
) -> dict[str, Any]:
    loops = parse_npc_loop_table(npc_loop_table)
    pairs = []
    issues: list[dict[str, str]] = []
    for loop_id in sorted(
        loops,
        key=lambda value: (0, int(value)) if value.isdigit() else (1, value),
    ):
        loop = loops[loop_id]
        idle_path = _resolve_resource_asset(asset_root, loop["resPath"])
        active_path = _resolve_resource_asset(asset_root, loop["clickResPath"])
        idle = _image_metadata(idle_path)
        active = _image_metadata(active_path)
        if not idle["exists"] or not active["exists"]:
            issues.append({"code": "MISSING_NPC_PAIR_ASSET", "detail": loop_id})
        elif idle["size"] != active["size"]:
            issues.append({"code": "NPC_PAIR_CANVAS_MISMATCH", "detail": loop_id})
        pairs.append(
            {
                "loopId": loop_id,
                "npcId": loop["npcId"],
                "name": loop["name"],
                "resPath": loop["resPath"],
                "clickResPath": loop["clickResPath"],
                "distinctStateAssets": loop["resPath"] != loop["clickResPath"],
                "position": loop["position"],
                "idle": idle,
                "active": active,
            }
        )
    backgrounds = []
    for path in sorted(background_root.rglob("*.png"), key=lambda item: str(item).lower()):
        metadata = _image_metadata(path)
        metadata["relativePath"] = path.relative_to(background_root).as_posix()
        backgrounds.append(metadata)
    ui_references = {}
    for side, path in (("left", ui_left), ("right", ui_right)):
        metadata = _image_metadata(path)
        if not metadata["exists"]:
            issues.append({"code": "MISSING_UI_REFERENCE", "detail": side})
        else:
            with Image.open(path) as image:
                mask = _obstruction_mask(image.convert("RGBA"), (255, 255, 255), 12)
                bbox = mask.getbbox()
                blocked = mask.histogram()[255]
                metadata["obstructionBBox"] = list(bbox) if bbox else None
                metadata["obstructionRatio"] = round(blocked / (image.width * image.height), 8)
        ui_references[side] = metadata
    report = {
        "schema": "ndc-project-asset-baseline/v1",
        "source": {
            "npcLoopTable": str(npc_loop_table.resolve()),
            "npcLoopTableSha256": sha256(npc_loop_table),
            "assetRoot": str(asset_root.resolve()),
            "backgroundRoot": str(background_root.resolve()),
        },
        "summary": {
            "npcLoopCount": len(pairs),
            "distinctStatePairCount": sum(pair["distinctStateAssets"] for pair in pairs),
            "backgroundCount": len(backgrounds),
            "issueCount": len(issues),
        },
        "npcPairs": pairs,
        "backgrounds": backgrounds,
        "uiReferences": ui_references,
        "issues": issues,
        "baselineComparison": None,
    }
    if baseline_path:
        baseline = load_json(baseline_path)
        if baseline.get("schema") != "ndc-project-asset-baseline/v1":
            raise ValueError("Baseline must use ndc-project-asset-baseline/v1.")
        old = _baseline_index(baseline)
        new = _baseline_index(report)
        added = sorted(set(new) - set(old))
        removed = sorted(set(old) - set(new))
        modified = sorted(key for key in set(old) & set(new) if old[key] != new[key])
        report["baselineComparison"] = {
            "baseline": str(baseline_path.resolve()),
            "baselineSha256": sha256(baseline_path),
            "status": "changed" if added or removed or modified else "unchanged",
            "added": added,
            "removed": removed,
            "modified": modified,
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract-timeline")
    extract.add_argument("--talk-table", type=Path, required=True)
    extract.add_argument("--npc-loop-table", type=Path, required=True)
    extract.add_argument("--start-talk-id", required=True)
    extract.add_argument("--initial-loop-id", action="append", default=[])
    extract.add_argument("--scene-config-table", type=Path)
    extract.add_argument("--scene-id", default="")
    extract.add_argument(
        "--choice",
        action="append",
        default=[],
        metavar="NODE_ID=TARGET_ID",
        help="Resolve a dialogue branch; repeat for multiple branch nodes.",
    )
    extract.add_argument("--asset-root", type=Path)
    extract.add_argument("--max-nodes", type=int, default=1000)
    extract.add_argument("--output", type=Path, required=True)
    extract.add_argument("--strict", action="store_true")

    timeline = subparsers.add_parser("validate-directing-timeline")
    timeline.add_argument("contract", type=Path)

    affordance = subparsers.add_parser("validate-affordance")
    affordance.add_argument("contract", type=Path)
    render_map = subparsers.add_parser("render-affordance")
    render_map.add_argument("contract", type=Path)
    render_map.add_argument("output", type=Path)
    render_map.add_argument("--base", type=Path)
    support = subparsers.add_parser("validate-support-contact")
    support.add_argument("affordance", type=Path)
    support.add_argument("placement", type=Path)
    support.add_argument("--report", type=Path)
    support.add_argument("--preview", type=Path)
    cast_scale = subparsers.add_parser("validate-cast-scale")
    cast_scale.add_argument("contract", type=Path)
    cast_scale.add_argument("--report", type=Path)

    scene_scale = subparsers.add_parser("validate-scene-absolute-scale")
    scene_scale.add_argument("contract", type=Path)
    scene_scale.add_argument("--report", type=Path)
    scene_scale.add_argument("--preview", type=Path)

    gaze = subparsers.add_parser("validate-gaze-conformance")
    gaze.add_argument("contract", type=Path)
    gaze.add_argument("--report", type=Path)

    component = subparsers.add_parser("validate-component-policy")
    component.add_argument("contract", type=Path)
    component.add_argument("--report", type=Path)

    ui = subparsers.add_parser("validate-ui-safety")
    ui.add_argument("contract", type=Path)
    ui.add_argument("--report", type=Path)
    ui.add_argument("--preview", type=Path)

    states = subparsers.add_parser("verify-exploration-states")
    states.add_argument("contract", type=Path)
    states.add_argument("idle", type=Path)
    states.add_argument("active", type=Path)
    states.add_argument("--output-dir", type=Path)

    board = subparsers.add_parser("render-timeline-board")
    board.add_argument("contract", type=Path)
    board.add_argument("output_dir", type=Path)

    blocking = subparsers.add_parser("build-blocking-candidates")
    blocking.add_argument("contract", type=Path)
    blocking.add_argument("output_dir", type=Path)

    local_handoff = subparsers.add_parser("prepare-local-generation-handoff")
    local_handoff.add_argument("contract", type=Path)
    local_handoff.add_argument("output_dir", type=Path)

    audit = subparsers.add_parser("audit-project-assets")
    audit.add_argument("--npc-loop-table", type=Path, required=True)
    audit.add_argument("--asset-root", type=Path, required=True)
    audit.add_argument("--background-root", type=Path, required=True)
    audit.add_argument("--ui-left", type=Path, required=True)
    audit.add_argument("--ui-right", type=Path, required=True)
    audit.add_argument("--baseline", type=Path)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument("--strict", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "extract-timeline":
            choices: dict[str, str] = {}
            for raw_choice in args.choice:
                if "=" not in raw_choice:
                    raise ValueError("--choice must use NODE_ID=TARGET_ID.")
                node_id, target_id = raw_choice.split("=", 1)
                if not node_id or not target_id or node_id in choices:
                    raise ValueError("Each --choice requires one unique non-empty node and target.")
                choices[node_id] = target_id
            result = extract_timeline(
                args.talk_table,
                args.npc_loop_table,
                args.start_talk_id,
                args.initial_loop_id,
                args.asset_root,
                args.max_nodes,
                args.scene_config_table,
                args.scene_id,
                choices,
            )
            write_json(args.output, result)
            print(
                "TIMELINE_EXTRACT_OK "
                f"nodes={result['summary']['nodeCount']} "
                f"actors={result['summary']['actorCount']} "
                f"issues={result['summary']['issueCount']} output={args.output}"
            )
            if args.strict and result["issues"]:
                raise ValueError("Extracted timeline contains issues; inspect the written report.")
        elif args.command == "validate-directing-timeline":
            validate_directing_timeline(load_json(args.contract))
            print("DIRECTING_TIMELINE_OK")
        elif args.command == "validate-affordance":
            validate_affordance(load_json(args.contract))
            print("AFFORDANCE_OK")
        elif args.command == "render-affordance":
            render_affordance(args.contract, args.output, args.base)
            print(f"AFFORDANCE_RENDER_OK output={args.output}")
        elif args.command == "validate-support-contact":
            result = validate_support_contact(
                args.affordance, args.placement, args.report, args.preview
            )
            print(
                f"SUPPORT_CONTACT_OK actor={result['actor']} contacts={len(result['contacts'])}"
            )
        elif args.command == "validate-cast-scale":
            result = validate_cast_scale(args.contract, args.report)
            print(
                f"CAST_SCALE_OK actors={len(result['actors'])} pairs={len(result['pairwise'])}"
            )
        elif args.command == "validate-scene-absolute-scale":
            result = validate_scene_absolute_scale(args.contract, args.report, args.preview)
            print(
                "SCENE_ABSOLUTE_SCALE_OK "
                f"anchors={len(result['anchors'])} factor={result['recommendedGlobalScaleFactor']:.4f}"
            )
        elif args.command == "validate-gaze-conformance":
            result = validate_gaze_conformance(args.contract, args.report)
            print(f"GAZE_CONFORMANCE_OK actors={len(result['actors'])}")
        elif args.command == "validate-component-policy":
            result = validate_component_policy(args.contract, args.report)
            print(f"COMPONENT_POLICY_OK layers={len(result['layerIds'])}")
        elif args.command == "validate-ui-safety":
            validate_ui_safety(args.contract, args.report, args.preview)
            print("UI_SAFETY_OK")
        elif args.command == "verify-exploration-states":
            verify_exploration_states(args.contract, args.idle, args.active, args.output_dir)
            print("EXPLORATION_STATES_OK")
        elif args.command == "render-timeline-board":
            render_timeline_board(args.contract, args.output_dir)
            print(f"TIMELINE_BOARD_OK output={args.output_dir}")
        elif args.command == "build-blocking-candidates":
            result = build_blocking_candidates(args.contract, args.output_dir)
            print(
                f"BLOCKING_CANDIDATES_OK candidates={result['candidateCount']} "
                f"output={args.output_dir}"
            )
        elif args.command == "prepare-local-generation-handoff":
            result = prepare_local_generation_handoff(args.contract, args.output_dir)
            print(
                "LOCAL_GENERATION_HANDOFF_OK "
                f"actor={result['actorId']} output={args.output_dir}"
            )
        elif args.command == "audit-project-assets":
            result = audit_project_assets(
                args.npc_loop_table,
                args.asset_root,
                args.background_root,
                args.ui_left,
                args.ui_right,
                args.baseline,
            )
            write_json(args.output, result)
            print(
                "PROJECT_ASSET_AUDIT_OK "
                f"npcLoops={result['summary']['npcLoopCount']} "
                f"backgrounds={result['summary']['backgroundCount']} "
                f"issues={result['summary']['issueCount']} output={args.output}"
            )
            if args.strict and result["issues"]:
                raise ValueError("Project asset audit contains issues; inspect the written report.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
