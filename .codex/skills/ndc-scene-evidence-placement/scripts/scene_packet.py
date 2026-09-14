#!/usr/bin/env python3
"""Build a compact, resumable work packet for one NDC prop scene."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


SCHEMA = "ndc-prop-scene-packet/v1"
PHYSICAL_RELATIONS = {"shared_identity", "state_variant", "container_content"}
ACTIVE_CANDIDATE_STATUSES = {
    "DELIVERY_CANDIDATE_SELECTED", "DELIVERY_CANDIDATE_REVIEWING",
    "DELIVERY_CANDIDATE_PASS_READY", "REVIEW_FAILED_PENDING_MOVE",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def load_active(batch_path: Path, batch: dict) -> tuple[set[str], str | None]:
    pointer = batch.get("active_delivery_scope_revision")
    if pointer is None:
        return set(batch["scope"]["required_artifacts"]), None
    path = resolve(batch_path.parent, pointer["path"])
    actual = sha256(path).lower()
    if actual != pointer["sha256"].lower():
        raise ValueError("active scope revision hash mismatch")
    return set(read_json(path)["execution_required_artifacts"]), actual


def is_ready(artifact: dict) -> bool:
    return artifact.get("status") == "PASS" and artifact.get("rejected") is False


def candidate_index(root: Path | None, required: set[str]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    if root is None:
        return result
    root = root.resolve()
    for path in sorted(root.rglob("candidate_manifest.json")) if root.is_dir() else []:
        data = read_json(path)
        artifact_id = data.get("artifact_id")
        if artifact_id not in required or data.get("status") not in ACTIVE_CANDIDATE_STATUSES:
            continue
        result.setdefault(artifact_id, []).append({
            "manifest": str(path), "manifest_sha256": sha256(path),
            "status": data["status"], "revision": data.get("revision"),
            "selected_reference_count": len(data.get("selected_references", [])),
        })
    return result


def build(batch_path: Path, scene_id: str, candidate_root: Path | None = None) -> dict:
    batch_path = batch_path.resolve()
    batch = read_json(batch_path)
    active, scope_sha = load_active(batch_path, batch)
    pointer = batch.get("scene_release_index")
    if not pointer:
        raise ValueError("scene packet requires the reviewed scene index")
    index_path = resolve(batch_path.parent, pointer["path"])
    if sha256(index_path).lower() != pointer["sha256"].lower():
        raise ValueError("scene index hash mismatch")
    index = read_json(index_path)
    if scene_id not in index.get("scenes", {}):
        raise ValueError("unknown scene")
    scene = index["scenes"][scene_id]
    owned = [artifact_id for artifact_id in scene["artifact_ids"] if artifact_id in active]
    active_items = {item_id for artifact_id in active
                    for item_id in batch["artifacts"][artifact_id].get("item_ids", [])}
    production_items = set(scene.get("item_ids", [])) & active_items
    context_items = set(production_items)
    related: dict[str, dict] = {}
    relation_roots: set[str] = set()
    while True:
        before = (set(production_items), set(context_items), set(related), set(relation_roots))
        for relation in index.get("relations", []):
            physical = relation.get("kind") in PHYSICAL_RELATIONS
            consumers = relation.get("consumer_scene_ids", [])
            applicable = physical or not consumers or scene_id in consumers
            relevant_items = production_items if physical else context_items
            if applicable and set(relation.get("item_ids", [])) & relevant_items:
                related[relation["id"]] = relation
                context_items.update(set(relation.get("item_ids", [])) & active_items)
                if physical:
                    production_items.update(set(relation.get("item_ids", [])) & active_items)
                if scene_id in consumers:
                    relation_roots.update(set(relation.get("artifact_ids", [])) & active)
        if before == (production_items, context_items, set(related), relation_roots):
            break
    stage2_roots = {artifact_id for artifact_id in active
                    if batch["artifacts"][artifact_id].get("stage") == 2
                    and set(batch["artifacts"][artifact_id].get("item_ids", [])) & production_items}
    required: set[str] = set(owned) | relation_roots | stage2_roots
    queue = list(required)
    while queue:
        artifact_id = queue.pop()
        artifact = batch["artifacts"][artifact_id]
        for parent in artifact.get("parents", []):
            if parent in active and parent not in required:
                required.add(parent)
                queue.append(parent)
    ready = sorted(artifact_id for artifact_id in required if is_ready(batch["artifacts"][artifact_id]))
    blocked = sorted(required - set(ready))
    blockers = []
    for artifact_id in blocked:
        artifact = batch["artifacts"][artifact_id]
        missing_parents = [parent for parent in artifact.get("parents", [])
                           if parent in active and not is_ready(batch["artifacts"][parent])]
        blockers.append({
            "artifact_id": artifact_id,
            "status": artifact.get("status", "PENDING"),
            "rejected": artifact.get("rejected") is True,
            "parents_not_ready": missing_parents,
        })
    next_actions = [f"resolve {row['artifact_id']}" for row in blockers if not row["parents_not_ready"]][:3]
    if not next_actions and blockers:
        next_actions = [f"resolve prerequisite {parent}"
                        for parent in blockers[0]["parents_not_ready"][:3]]
    parent_hashes = {artifact_id: batch["artifacts"][artifact_id].get("sha256")
                     for artifact_id in sorted(required)
                     if batch["artifacts"][artifact_id].get("sha256")}
    archive_path = resolve(batch_path.parent, batch["content_archive"])
    archive = read_json(archive_path)
    fact_refs = {f"{item_id}.{field}" for item_id in production_items
                 for field in archive["items"][item_id]["requirements"]}
    fact_refs.update(ref for relation in related.values() for ref in relation.get("fact_refs", []))
    facts = {ref: archive["items"][ref.split(".", 1)[0]]["requirements"][ref.split(".", 1)[1]]
             for ref in sorted(fact_refs)}
    candidates = candidate_index(candidate_root, required)
    return {
        "schema": SCHEMA,
        "batch_id": batch["batch_id"],
        "scene_id": scene_id,
        "scope_revision_sha256": scope_sha,
        "required_artifacts": sorted(required),
        "scene_outputs": owned,
        "production_item_ids": sorted(production_items),
        "context_item_ids": sorted(context_items),
        "relation_ids": sorted(related),
        "context_fact_refs": sorted(fact_refs),
        "facts_sha256": hashlib.sha256(json.dumps(facts, ensure_ascii=False, sort_keys=True,
                                                   separators=(",", ":")).encode("utf-8")).hexdigest(),
        "ready_artifacts": ready,
        "blocked_artifacts": blocked,
        "blockers": blockers,
        "next_actions": next_actions,
        "parent_hashes": parent_hashes,
        "delivery_candidates": candidates,
        "photoshop": {"document_id": "", "recovery_psd": "", "dirty": False},
    }


def write_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".writing")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-root", type=Path)
    args = parser.parse_args()
    try:
        packet = build(args.batch, args.scene, args.candidate_root)
        if args.output:
            write_atomic(args.output.resolve(), packet)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"blocked": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
