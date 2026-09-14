"""Test-only builder for a complete character manual-node delivery manifest."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def attach_character_node_delivery(node: dict, node_path: Path, module) -> None:
    """Attach a minimal hash-bound flat package to an otherwise valid test node."""
    base = node_path.parent.resolve()
    node.setdefault("unit", "Unit1")
    node.setdefault("scene_label", {
        "display_name": f"Test Location ({node.get('scene_id')}) (Test Time)",
        "location": f"Test Location ({node.get('scene_id')})",
        "time": "Test Time",
    })
    package = base / "delivery" / "角色融入场景" / node["unit"] / "节点交付" / str(node["scene_id"])
    if package.exists():
        shutil.rmtree(package)
    package.mkdir(parents=True)
    artifacts = []

    def add(actor: str, pose: str, role: str, entry: dict, name: str) -> None:
        source = module.bound(entry, base, f"fixture.{role}")
        destination = package / name
        destination.write_bytes(source.read_bytes())
        stem = destination.stem
        candidate = package / "_节点资料" / stem / f"{stem}_节点候选.json"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("{}", encoding="utf-8")
        artifacts.append({
            "artifact_id": f"fixture-{len(artifacts)}", "actor_id": actor, "pose_id": pose, "role": role,
            "package_file": {"relative_path": destination.name, "sha256": module.sha256(destination)},
            "candidate_record": {"relative_path": str(candidate.relative_to(package)), "sha256": module.sha256(candidate)},
        })

    for whitebox in node["deliverables"]["production_whiteboxes"]:
        actor = str(whitebox["actor_id"])
        pose = str(whitebox["pose_id"])
        add(actor, pose, "complete_anatomy_master", whitebox["complete_anatomy_master"], f"{node['scene_id']}_{actor}_{pose}_whitebox-master.png")
        add(actor, pose, "final_submission_whitebox", whitebox["final_submission_whitebox"], f"{node['scene_id']}_{actor}_{pose}_image1-whitebox.png")
    add("scene", str(node["revision"]), "joint_whitebox_preview", node["deliverables"]["joint_whitebox_preview"], f"{node['scene_id']}_scene_r{node['revision']}_joint-whitebox.png")
    add("scene", str(node["revision"]), "actual_ui_clearance_preview", node["deliverables"]["actual_ui_clearance_preview"], f"{node['scene_id']}_scene_r{node['revision']}_ui-whitebox.png")
    scope = module.bound(node["scope"], base, "fixture.scope")
    manifest_path = package / "_节点资料" / "_节点" / str(node["node_id"]) / "节点交付清单.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = {
        "schema": module.CHARACTER_NODE_DELIVERY_SCHEMA,
        "status": module.CHARACTER_NODE_DELIVERY_STATUS,
        "unit": node["unit"], "node_id": node["node_id"], "scene_id": node["scene_id"], "revision": node["revision"],
        "scene_label": node["scene_label"],
        "legacy_migration_backfill": node.get("legacy_migration_backfill", {"enabled": False, "reason": None, "asset_count": 0}),
        "formal_pass": False, "package_root": str(package),
        "scope_source": {"path": str(scope), "sha256": module.sha256(scope)},
        "coverage": {
            "actor_poses_required": len(node["deliverables"]["production_whiteboxes"]),
            "actor_poses_packaged": len(node["deliverables"]["production_whiteboxes"]),
            "missing": [], "extra": [],
        },
        "support_files": [{"kind": "human_preview_index"}, {"kind": "human_asset_list"}, {"kind": "non_formal_warning"}],
        "artifacts": artifacts,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    node["deliverables"]["node_delivery_manifest"] = {"path": str(manifest_path), "sha256": module.sha256(manifest_path)}
