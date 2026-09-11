"""Shared, side-effect-free paths for NDC art tools."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
import math


LOCAL_SCHEMA = "ndc-machine-paths/v1"
RULES_SCHEMA = "ndc-art-workspace/v2"
CONFIGURE_HINT = ("Run python scripts/art_pipeline/ndc_art.py configure "
                  "--planning-root ABS --engine-root ABS --work-root ABS")
OVERRIDE_ENV = "NDC_ART_ALLOW_CONFIG_ROOT_OVERRIDE"

EXPRESSION_SOURCE_KEYS = (
    "unit3_portrait_root",
    "unit1_expression_root",
    "unit2_expression_root",
)
STYLE_LIBRARY_KEYS = (
    "general_character_card",
    "general_portrait",
    "black_white_red_character_card",
)


@dataclass(frozen=True)
class ArtPaths:
    planning_root: Path
    engine_root: Path
    work_root: Path
    delivery_root: Path
    character_registry: Path
    expression_sources: dict[str, Path]
    style_check_libraries: dict[str, Path]
    quota_gib: float
    minimum_free_gib: float


def contained(path: Path, root: Path, *, allow_root: bool = False) -> bool:
    path, root = path.resolve(), root.resolve()
    return (allow_root and path == root) or (path != root and path.is_relative_to(root))


def absolute_root(value: str | Path | None, label: str) -> Path:
    if value is None or not str(value).strip():
        raise ValueError(f"Missing {label}. {CONFIGURE_HINT}")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError(f"{label} must be an absolute path. {CONFIGURE_HINT}")
    return path.resolve()


def validate_roots(planning: Path, engine: Path, work: Path,
                   delivery: Path | None = None) -> None:
    if planning == engine:
        raise ValueError("Planning and engine roots must identify distinct checkouts")
    if work == Path(work.anchor):
        raise ValueError("work_root must be a dedicated directory, never a drive root")
    for protected in (planning, engine):
        if work == protected or work.is_relative_to(protected) or protected.is_relative_to(work):
            raise ValueError("work_root must be outside and must not contain either project")
    if delivery is not None:
        if delivery == Path(delivery.anchor):
            raise ValueError("delivery_root must be a dedicated directory, never a drive root")
        if delivery.name != "最终交付":
            raise ValueError("delivery_root folder name must remain 最终交付")
        if delivery == work or delivery.is_relative_to(work) or work.is_relative_to(delivery):
            raise ValueError("delivery_root and work_root must not contain one another")
        if delivery == engine or delivery.is_relative_to(engine) or engine.is_relative_to(delivery):
            raise ValueError("delivery_root must stay outside the read-only engine checkout")


def default_delivery_root(planning: Path) -> Path:
    """Keep the formal folder beside the planning checkout on a new device."""
    return (planning.parent / "最终交付").resolve()


def optional_path_map(data: dict, field: str, keys: tuple[str, ...]) -> dict[str, Path]:
    raw = data.get(field, {})
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"{field} must be an object in ndc.local.json")
    resolved = {}
    for key in keys:
        value = raw.get(key)
        if value is not None and str(value).strip():
            resolved[key] = absolute_root(value, f"{field}.{key}")
    return resolved


def read_local_paths(root: Path) -> dict:
    local = root / "ndc.local.json"
    if not local.exists():
        return {}
    data = json.loads(local.read_text(encoding="utf-8-sig"))
    if data.get("schema") != LOCAL_SCHEMA:
        raise ValueError(f"Unsupported machine path configuration: {local}")
    return data


def guard_config_drift(local: dict, resolved: dict[str, Path]) -> None:
    """Reject silent disagreement between a checkout config and active roots."""
    if not local:
        return
    mismatches = []
    for key, actual in resolved.items():
        configured = local.get(key)
        if configured and absolute_root(configured, key) != actual:
            mismatches.append(f"{key}: configured={configured!r}, active={str(actual)!r}")
    if mismatches and os.environ.get(OVERRIDE_ENV) != "1":
        raise ValueError(
            "Machine path configuration disagrees with the active checkout/environment: "
            + "; ".join(mismatches)
            + f". Re-run configure for this checkout pair, or set {OVERRIDE_ENV}=1 "
              "only for an intentional one-session override."
        )


def load_art_paths(config_path: str | Path | None = None) -> ArtPaths:
    # This implementation lives only in the planning checkout. Never infer the
    # other checkout from its directory name, drive, or relationship to this one.
    planning = absolute_root(os.environ.get("NDC_PLANNING_ROOT") or
                             Path(__file__).resolve().parents[2], "planning_root")
    explicit = config_path or os.environ.get("NDC_ART_PATHS_CONFIG")
    config = Path(explicit) if explicit else planning / "production/art_pipeline/paths.json"
    data = json.loads(config.read_text(encoding="utf-8-sig"))
    legacy = bool(explicit) and data.get("schema") == "ndc-art-workspace/v1"
    if data.get("schema") != RULES_SCHEMA and not legacy:
        raise ValueError("Unsupported art workspace configuration")
    local = read_local_paths(planning)
    machine = data if legacy else local
    engine = absolute_root(os.environ.get("NDC_ENGINE_ROOT") or machine.get("engine_root"), "engine_root")
    work = absolute_root(os.environ.get("NDC_ART_WORK_ROOT") or machine.get("work_root"), "work_root")
    delivery = absolute_root(
        os.environ.get("NDC_ART_DELIVERY_ROOT") or machine.get("delivery_root")
        or default_delivery_root(planning),
        "delivery_root",
    )
    if not legacy:
        guard_config_drift(local, {"planning_root": planning, "engine_root": engine,
                                   "work_root": work, "delivery_root": delivery})
    validate_roots(planning, engine, work, delivery)
    registry = Path(data["character_registry"])
    if not legacy and (registry.is_absolute() or registry.drive or ".." in registry.parts):
        raise ValueError("Shared character_registry must be relative to the planning checkout")
    registry = registry if registry.is_absolute() else planning / registry
    quota = float(data.get("quota_gib", 50))
    free = float(data.get("minimum_free_gib", 10))
    if not math.isfinite(quota) or not math.isfinite(free) or quota <= 0 or free < 0:
        raise ValueError("Invalid art workspace storage budget")
    expression_sources = {} if legacy else optional_path_map(
        local, "expression_sources", EXPRESSION_SOURCE_KEYS)
    style_libraries = {} if legacy else optional_path_map(
        local, "style_check_libraries", STYLE_LIBRARY_KEYS)
    return ArtPaths(planning, engine, work, delivery, registry.resolve(),
                    expression_sources, style_libraries, quota, free)


if __name__ == "__main__":
    from dataclasses import asdict
    print(json.dumps(asdict(load_art_paths()), ensure_ascii=False, indent=2, default=str))
