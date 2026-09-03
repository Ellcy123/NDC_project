#!/usr/bin/env python3
"""Fail-closed release audit for NDC expression delivery packages.

The registry is intentionally explicit: every requested asset/profile is one row,
and every row carries current-file hashes plus evidence for every required gate.
Completeness and file counts are reported, but can never authorize release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "ndc-expression-delivery-release/v1"
PASS = "PASS"
LEGACY_AMPLITUDE_WAIVER = "WAIVED_BY_USER_LEGACY_AMPLITUDE"
LEGACY_AMPLITUDE_EXCEPTION = "LEGACY_APPROVED_EXPRESSION_AMPLITUDE"
ALLOWED_ROUTES = {
    "GENERATED_CURRENT_SPEC",
    "REUSE_APPROVED_AS_IS",
    "NORMALIZED_CURRENT_PAIR",
}
GENERATED_GATES = (
    "identity_style_viewpoint",
    "expression_signal",
    "calm_separation",
    "pairwise_separability",
    "thumbnail_readability",
    "source_detail_lighting",
    "texture_coherence",
    "semantic_color",
    "lower_bust_structure",
    "profile_guide",
    "mechanical",
    "background_alpha",
    "cross_profile_native_source",
    "set_continuity",
)
REUSE_GATES = GENERATED_GATES + ("approved_reuse_provenance", "inventory_identity")
NORMALIZED_PAIR_GATES = GENERATED_GATES + ("normalization_provenance",)
AMPLITUDE_GATES = {
    "expression_signal",
    "calm_separation",
    "pairwise_separability",
    "thumbnail_readability",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def fail(errors: list[str], asset_key: str, message: str) -> None:
    errors.append(f"{asset_key}: {message}")


def audit(registry_path: Path) -> dict[str, Any]:
    registry = load_json(registry_path)
    registry_base = registry_path.parent
    errors: list[str] = []
    warnings: list[str] = []

    if registry.get("schema") != SCHEMA:
        errors.append(f"registry schema must be {SCHEMA}")

    delivery_root_value = registry.get("delivery_root")
    if not isinstance(delivery_root_value, str) or not delivery_root_value:
        errors.append("delivery_root is required")
        delivery_root = registry_base
    else:
        delivery_root = resolve(registry_base, delivery_root_value).resolve()

    assets = registry.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty list; a completeness summary is not a release registry")
        assets = []

    expected_inventory = registry.get("expected_inventory")
    if not isinstance(expected_inventory, list) or not expected_inventory:
        errors.append("expected_inventory must enumerate every required character/expression/profile row")
        expected_inventory = []

    seen: set[str] = set()
    pairs: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}

    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"assets[{index}] must be an object")
            continue
        character = str(asset.get("character_id", "")).strip()
        expression = str(asset.get("expression_id", "")).strip()
        profile = str(asset.get("profile", "")).strip()
        key = f"{character}/{expression}/{profile}"
        if not character or not expression or profile not in {"greenscreen", "transparent"}:
            fail(errors, key, "character_id, expression_id and valid profile are required")
        if key in seen:
            fail(errors, key, "duplicate registry row")
        seen.add(key)

        route = asset.get("route")
        if route not in ALLOWED_ROUTES:
            fail(errors, key, f"route must be one of {sorted(ALLOWED_ROUTES)}")
            continue

        relative_path = asset.get("relative_path")
        if not isinstance(relative_path, str) or not relative_path:
            fail(errors, key, "relative_path is required")
            continue
        output = resolve(delivery_root, relative_path).resolve()
        try:
            output.relative_to(delivery_root)
        except ValueError:
            fail(errors, key, "relative_path escapes delivery_root")
            continue
        if not output.is_file():
            fail(errors, key, f"missing output file: {output}")
            continue

        recorded_hash = str(asset.get("sha256", "")).lower()
        current_hash = sha256(output)
        if recorded_hash != current_hash:
            fail(errors, key, "output SHA-256 is missing or stale")

        gates = asset.get("gates")
        if not isinstance(gates, dict):
            fail(errors, key, "gates object is required")
            gates = {}
        if route == "GENERATED_CURRENT_SPEC":
            required_gates = GENERATED_GATES
        elif route == "REUSE_APPROVED_AS_IS":
            required_gates = REUSE_GATES
        else:
            required_gates = NORMALIZED_PAIR_GATES
        exceptions = asset.get("current_spec_exceptions", []) if route in {"REUSE_APPROVED_AS_IS", "NORMALIZED_CURRENT_PAIR"} else []
        legacy_amplitude_allowed = (
            route in {"REUSE_APPROVED_AS_IS", "NORMALIZED_CURRENT_PAIR"}
            and asset.get("legacy_approved_source") is True
            and isinstance(exceptions, list)
            and exceptions == [LEGACY_AMPLITUDE_EXCEPTION]
        )
        for gate in required_gates:
            allowed = {PASS}
            if legacy_amplitude_allowed and gate in AMPLITUDE_GATES:
                allowed.add(LEGACY_AMPLITUDE_WAIVER)
            if gates.get(gate) not in allowed:
                fail(errors, key, f"gate {gate} must be explicit PASS (NOT_CHECKED and missing are blocking)")

        evidence = asset.get("evidence")
        if not isinstance(evidence, dict):
            fail(errors, key, "evidence object is required")
            evidence = {}
        for gate in required_gates:
            evidence_value = evidence.get(gate)
            evidence_items = evidence_value if isinstance(evidence_value, list) else [evidence_value]
            evidence_items = [item for item in evidence_items if isinstance(item, str) and item]
            if not evidence_items:
                fail(errors, key, f"gate {gate} has no evidence path")
                continue
            for item in evidence_items:
                evidence_path = resolve(registry_base, item)
                if not evidence_path.is_file():
                    fail(errors, key, f"missing evidence for {gate}: {evidence_path}")

        if route == "REUSE_APPROVED_AS_IS":
            source_value = asset.get("approved_source_path")
            source_hash = str(asset.get("approved_source_sha256", "")).lower()
            exceptions = asset.get("current_spec_exceptions")
            if not isinstance(source_value, str) or not source_value:
                fail(errors, key, "approved_source_path is required for immutable reuse")
            else:
                source = resolve(registry_base, source_value)
                if not source.is_file():
                    fail(errors, key, f"approved reuse source is missing: {source}")
                else:
                    actual_source_hash = sha256(source)
                    if source_hash != actual_source_hash or current_hash != actual_source_hash:
                        fail(errors, key, "reused output must be byte-identical to the approved source and recorded hash")
            if not isinstance(exceptions, list):
                fail(errors, key, "current_spec_exceptions must be an explicit list, including []")
            elif exceptions not in ([], [LEGACY_AMPLITUDE_EXCEPTION]):
                fail(errors, key, "only the explicit legacy approved-expression amplitude exception is release-eligible")
        elif route == "NORMALIZED_CURRENT_PAIR":
            source_value = asset.get("normalization_source_path")
            source_hash = str(asset.get("normalization_source_sha256", "")).lower()
            pair_evidence_value = asset.get("pair_version_evidence")
            pair_evidence_hash = str(asset.get("pair_version_evidence_sha256", "")).lower()
            exceptions = asset.get("current_spec_exceptions")
            if not isinstance(source_value, str) or not source_value:
                fail(errors, key, "normalization_source_path is required")
            else:
                source = resolve(registry_base, source_value)
                if not source.is_file() or source_hash != sha256(source):
                    fail(errors, key, "normalization source is missing or its SHA-256 is stale")
            if not isinstance(pair_evidence_value, str) or not pair_evidence_value:
                fail(errors, key, "pair_version_evidence is required")
            else:
                pair_evidence = resolve(registry_base, pair_evidence_value)
                if not pair_evidence.is_file() or pair_evidence_hash != sha256(pair_evidence):
                    fail(errors, key, "pair-version evidence is missing or its SHA-256 is stale")
            if not isinstance(exceptions, list):
                fail(errors, key, "current_spec_exceptions must be an explicit list, including []")
            elif exceptions not in ([], [LEGACY_AMPLITUDE_EXCEPTION]):
                fail(errors, key, "only the explicit legacy approved-expression amplitude exception is release-eligible")
            if exceptions and asset.get("legacy_approved_source") is not True:
                fail(errors, key, "legacy amplitude waiver requires legacy_approved_source=true")

        pairs.setdefault((character, expression), {})[profile] = asset

    expected_keys = {
        f"{row.get('character_id', '')}/{row.get('expression_id', '')}/{row.get('profile', '')}"
        for row in expected_inventory
        if isinstance(row, dict)
    }
    if expected_keys != seen:
        for key in sorted(expected_keys - seen):
            errors.append(f"missing required registry row: {key}")
        for key in sorted(seen - expected_keys):
            errors.append(f"unexpected registry row not in expected_inventory: {key}")

    required_profiles = registry.get("required_profiles", ["greenscreen", "transparent"])
    if not isinstance(required_profiles, list) or not required_profiles:
        errors.append("required_profiles must be a non-empty list")
        required_profiles = []
    for (character, expression), profiles in pairs.items():
        for profile in required_profiles:
            if profile not in profiles:
                errors.append(f"{character}/{expression}: missing required profile {profile}")
        generated = [row for row in profiles.values() if row.get("route") == "GENERATED_CURRENT_SPEC"]
        if generated:
            native_hashes = {str(row.get("native_source_sha256", "")).lower() for row in generated}
            if "" in native_hashes or len(native_hashes) != 1:
                errors.append(f"{character}/{expression}: generated profile rows must share one native_source_sha256")
        normalized = [row for row in profiles.values() if row.get("route") == "NORMALIZED_CURRENT_PAIR"]
        if normalized:
            pair_hashes = {str(row.get("pair_version_evidence_sha256", "")).lower() for row in normalized}
            if "" in pair_hashes or len(pair_hashes) != 1:
                errors.append(f"{character}/{expression}: normalized profile rows must share one pair-version evidence SHA-256")

    all_pngs = {
        str(path.relative_to(delivery_root)).replace("\\", "/")
        for path in delivery_root.rglob("*.png")
    } if delivery_root.is_dir() else set()
    declared_pngs = {
        str(Path(asset["relative_path"])).replace("\\", "/")
        for asset in assets
        if isinstance(asset, dict) and isinstance(asset.get("relative_path"), str)
    }
    undeclared = sorted(all_pngs - declared_pngs)
    if undeclared:
        errors.append(f"delivery root contains {len(undeclared)} undeclared PNG(s): {undeclared[:10]}")

    release_status = PASS if not errors else "FAIL"
    return {
        "schema": SCHEMA,
        "registry": str(registry_path.resolve()),
        "delivery_root": str(delivery_root),
        "release_status": release_status,
        "asset_rows": len(assets),
        "expected_rows": len(expected_inventory),
        "completeness_status": PASS if expected_keys == seen and bool(expected_keys) else "FAIL",
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = audit(args.registry)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    print(f"RELEASE_STATUS: {result['release_status']}")
    return 0 if result["release_status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
