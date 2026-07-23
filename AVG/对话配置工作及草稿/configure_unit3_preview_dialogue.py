#!/usr/bin/env python3
"""Backfill Unit3 preview dialogue entries from generated AVG files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import assign_unit3_dialogue_ids as assigner


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
AVG_ROOT = PROJECT_ROOT / "AVG" / "EPI03"
TABLE_ROOT = PROJECT_ROOT / "avg_editor_v2" / "data" / "table"
SCENE_CONFIG = TABLE_ROOT / "SceneConfig.json"
CHAPTER_CONFIG = TABLE_ROOT / "ChapterConfig.json"

SCENE_TALKS = {
    (1, "303"): "L1_scene3004_morrison",
    (1, "304"): "L1_scene3005_foster",
    (2, "302"): "L2_scene3013_mary",
    (2, "309"): "L2_scene3007_priest",
    (3, "305"): "L3_scene3008_helen_encounter",
    (3, "306"): "L3_scene3009_bernard",
    (3, "308"): "L3_scene3006_seamus",
    (4, "304"): "L4_scene3005_foster",
    (4, "305"): "L4_scene3008_helen_opening",
    (4, "307"): "L4_scene3010_margaret",
    (5, "305"): "L5_scene3008_helen",
    (5, "306"): "L5_scene3014_bernard",
    (6, "304"): "L6_scene3005_foster",
    (6, "308"): "L6_scene3006_seamus",
}

UNSUPPORTED_SCENE_TALKS = {(5, "301"), (6, "301")}

OPENING_TALKS = {
    1: "L1_opening_mickey",
    2: "L2_opening_talk",
    3: "L3_opening",
    4: "L4_opening",
    5: "L5_opening",
    6: "L6_opening",
}

POST_EXPOSE_TALKS = {
    4: ["L4_postexpose_mickey", "L4_postexpose_mary"],
    6: ["L6_ending_emma", "L6_ending_leonard"],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def talk_path(loop: int, stem: str) -> Path:
    return AVG_ROOT / "Talk" / f"loop{loop}" / f"{stem}.json"


def first_talk_id(loop: int, stem: str) -> str:
    rows = load_json(talk_path(loop, stem))
    if not rows:
        raise ValueError(f"Empty Unit3 Talk file: {stem}")
    return str(rows[0]["id"])


def expose_round_ids(loop: int) -> list[str]:
    sections = assigner.build_numbered_sections(loop)
    expose = next(section for section in sections if section.kind == "Expose")
    round_ids = []
    round_number = 1
    while True:
        label = f"round{round_number}"
        node = next((node for node in expose.nodes if label in node.labels), None)
        if node is None:
            break
        round_ids.append(str(node.id))
        round_number += 1

    generated = load_json(AVG_ROOT / "Expose" / f"{expose.filename}.json")
    generated_ids = {str(row["id"]) for row in generated}
    missing = [talk_id for talk_id in round_ids if talk_id not in generated_ids]
    if missing:
        raise ValueError(f"Expose loop{loop} round IDs missing from JSON: {missing}")
    return round_ids


def apply_scene_configuration(scene_rows: list[dict]) -> None:
    found = set()
    cleared = set()
    for row in scene_rows:
        if row.get("Chapter") != "EPI03":
            continue
        loop = int(row.get("loop") or 0)
        for info in row.get("NPCInfos", []):
            npc_id = str(info.get("NPC", {}).get("id", ""))
            key = (loop, npc_id)
            if key in SCENE_TALKS:
                stem = SCENE_TALKS[key]
                info["TalkInfo"] = {
                    "id": first_talk_id(loop, stem),
                    "videoEpisode": "EPI03",
                    "videoLoop": f"loop{loop}",
                    "videoScene": stem,
                }
                info["LoopTalkInfo"] = {}
                found.add(key)
            elif key in UNSUPPORTED_SCENE_TALKS:
                info["TalkInfo"] = {}
                info["LoopTalkInfo"] = {}
                cleared.add(key)

    missing = set(SCENE_TALKS) - found
    missing_clear = UNSUPPORTED_SCENE_TALKS - cleared
    if missing or missing_clear:
        raise ValueError(
            f"Unit3 SceneConfig targets missing: talks={sorted(missing)}, "
            f"clear={sorted(missing_clear)}"
        )


def apply_chapter_configuration(chapter_rows: list[dict]) -> None:
    by_id = {str(row.get("id")): row for row in chapter_rows}
    for loop in range(1, 7):
        chapter = by_id.get(str(300 + loop))
        if chapter is None:
            raise ValueError(f"ChapterConfig missing Unit3 loop{loop}")

        chapter["initTalk"] = first_talk_id(loop, OPENING_TALKS[loop])
        round_ids = expose_round_ids(loop)
        exposes = chapter.get("exposes", [])
        if len(exposes) != len(round_ids):
            raise ValueError(
                f"Unit3 loop{loop} expose round mismatch: "
                f"ChapterConfig={len(exposes)}, AVG={len(round_ids)}"
            )
        for expose, talk_id in zip(exposes, round_ids):
            expose["talkId"] = talk_id

        stems = POST_EXPOSE_TALKS.get(loop, [])
        segments = chapter.get("postExposeSegments", [])
        if len(segments) != len(stems):
            if stems or segments:
                raise ValueError(
                    f"Unit3 loop{loop} post-expose mismatch: "
                    f"ChapterConfig={len(segments)}, AVG={len(stems)}"
                )
        for segment, stem in zip(segments, stems):
            segment["videoEpisode"] = "EPI03"
            segment["videoLoop"] = f"loop{loop}"
            segment["videoScene"] = stem
            segment["entryTalkId"] = first_talk_id(loop, stem)

        requirement = str(chapter.get("ArtRequirement", ""))
        requirement = requirement.replace(
            "Talk/Expose 入口为 TODO，待 AVG/EPI03 JSON 生成后回填。",
            "Talk/Expose 入口已由 AVG/EPI03 对白配置回填。",
        )
        chapter["ArtRequirement"] = requirement


def apply_configuration(scene_rows: list[dict], chapter_rows: list[dict]) -> None:
    apply_scene_configuration(scene_rows)
    apply_chapter_configuration(chapter_rows)


def write_json(path: Path, rows: list[dict]) -> None:
    path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    scenes = load_json(SCENE_CONFIG)
    chapters = load_json(CHAPTER_CONFIG)
    apply_configuration(scenes, chapters)

    if args.write:
        write_json(SCENE_CONFIG, scenes)
        write_json(CHAPTER_CONFIG, chapters)
        print("[WRITE] Unit3 preview dialogue entries configured")
    else:
        print("[DRY] Unit3 preview dialogue entries validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
