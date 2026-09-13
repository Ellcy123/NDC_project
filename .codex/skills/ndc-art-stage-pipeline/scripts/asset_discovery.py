#!/usr/bin/env python3
"""Validate immutable existing-asset discovery receipts before an art action."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "ndc-asset-discovery-receipt/v1"
ROOT_ROLES = ("official_runtime", "approved_archive", "formal_delivery")
STATUSES = {
    "NOT_SEARCHED",
    "SEARCH_INCOMPLETE",
    "FOUND_UNBOUND",
    "FOUND_USABLE",
    "FOUND_REPAIRABLE",
    "CONFIRMED_ABSENT",
    "BLOCKED",
}
ACTIONS = {"GENERATE", "REPAIR", "REUSE", "PACKAGE"}
HEX = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(base: Path, raw: str) -> Path:
    value = Path(raw)
    return value.resolve() if value.is_absolute() else (base / value).resolve()


def bound(entry: object, base: Path, label: str) -> Path:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
        raise ValueError(f"{label} requires path and sha256")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or HEX.fullmatch(digest.lower()) is None:
        raise ValueError(f"{label} requires a lowercase SHA-256")
    path = resolve(base, entry["path"])
    if not path.is_file():
        raise ValueError(f"{label} file is missing: {path}")
    if sha256(path) != digest.lower():
        raise ValueError(f"{label} hash no longer matches current bytes")
    return path


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value


def timestamp(value: object, label: str) -> None:
    try:
        datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be ISO-8601") from exc


def _scope(data: dict) -> dict:
    scope = data.get("scope")
    if not isinstance(scope, dict):
        raise ValueError("scope is required")
    domain = text(scope.get("domain"), "scope.domain")
    if domain not in {"character_scene", "prop"}:
        raise ValueError("scope.domain must be character_scene or prop")
    text(scope.get("scene_id"), "scope.scene_id")
    revision = scope.get("revision")
    if not isinstance(revision, (str, int)) or isinstance(revision, bool) or str(revision).strip() == "":
        raise ValueError("scope.revision is required")
    actor = scope.get("actor_id")
    item = scope.get("item_id")
    if bool(isinstance(actor, str) and actor.strip()) == bool(isinstance(item, str) and item.strip()):
        raise ValueError("scope needs exactly one of actor_id or item_id")
    text(scope.get("pose_or_state"), "scope.pose_or_state")
    text(scope.get("artifact_role"), "scope.artifact_role")
    return scope


def validate_receipt(
    receipt_path: Path,
    *,
    expected_scope: dict | None = None,
    action: str = "GENERATE",
) -> list[str]:
    """Return semantic failures; raise only for unreadable or malformed contracts."""
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {sorted(ACTIONS)}")
    receipt_path = receipt_path.resolve()
    data = load(receipt_path)
    failures: list[str] = []
    if data.get("schema") != SCHEMA:
        return ["unsupported discovery receipt schema"]
    status = data.get("status")
    if status not in STATUSES:
        failures.append("receipt status is invalid")
    timestamp(data.get("checked_at"), "checked_at")
    scope = _scope(data)
    if expected_scope:
        for key in ("domain", "scene_id", "revision", "actor_id", "item_id", "pose_or_state", "artifact_role"):
            if key in expected_scope and str(scope.get(key, "")) != str(expected_scope[key]):
                failures.append(f"scope mismatch for {key}")

    freshness = data.get("freshness")
    if not isinstance(freshness, dict):
        failures.append("freshness is required")
    else:
        scope_digest = freshness.get("scope_revision_sha256")
        if not isinstance(scope_digest, str) or HEX.fullmatch(scope_digest.lower()) is None:
            failures.append("freshness.scope_revision_sha256 is required")
        elif expected_scope and expected_scope.get("scope_revision_sha256") and scope_digest.lower() != str(expected_scope["scope_revision_sha256"]).lower():
            failures.append("scope revision changed; discovery receipt is stale")
        try:
            bound(freshness.get("asset_index"), receipt_path.parent, "freshness.asset_index")
        except ValueError as exc:
            failures.append(str(exc))

    searches = data.get("searches")
    seen_roots: set[str] = set()
    if not isinstance(searches, list) or not searches:
        failures.append("searches must document every required root")
    else:
        for index, search in enumerate(searches):
            label = f"searches[{index}]"
            if not isinstance(search, dict):
                failures.append(f"{label} must be an object")
                continue
            role = search.get("root_role")
            if role not in ROOT_ROLES or role in seen_roots:
                failures.append(f"{label}.root_role is invalid or duplicated")
            else:
                seen_roots.add(role)
            if not isinstance(search.get("root_path"), str) or not Path(search["root_path"]).is_absolute():
                failures.append(f"{label}.root_path must identify the actual configured root")
            query_ids = search.get("query_ids")
            aliases = search.get("aliases")
            if not isinstance(query_ids, list) or not query_ids or not all(isinstance(v, str) and v for v in query_ids):
                failures.append(f"{label}.query_ids must include the exact ID")
            if not isinstance(aliases, list) or not aliases or not all(isinstance(v, str) and v for v in aliases):
                failures.append(f"{label}.aliases must record actual query names")
            if search.get("completed") is not True:
                failures.append(f"{label} is incomplete")
        missing = set(ROOT_ROLES) - seen_roots
        if missing:
            failures.append("required roots were not searched: " + ", ".join(sorted(missing)))

    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        failures.append("candidates must be a list")
        candidates = []
    for index, candidate in enumerate(candidates):
        label = f"candidates[{index}]"
        if not isinstance(candidate, dict):
            failures.append(f"{label} must be an object")
            continue
        if candidate.get("root_role") not in ROOT_ROLES:
            failures.append(f"{label}.root_role is invalid")
        try:
            bound(candidate, receipt_path.parent, label)
        except ValueError as exc:
            failures.append(str(exc))
        dimensions = candidate.get("dimensions")
        if not isinstance(dimensions, dict) or not all(isinstance(dimensions.get(k), int) and dimensions[k] > 0 for k in ("width", "height")):
            failures.append(f"{label}.dimensions requires positive width and height")

    if status == "CONFIRMED_ABSENT":
        if candidates:
            failures.append("CONFIRMED_ABSENT cannot contain candidates")
        if any(not isinstance(s, dict) or s.get("completed") is not True for s in searches or []):
            failures.append("CONFIRMED_ABSENT requires complete searches of every required root")
    if status in {"FOUND_UNBOUND", "FOUND_USABLE", "FOUND_REPAIRABLE"} and not candidates:
        failures.append(f"{status} requires at least one bound candidate")

    action_errors = {
        "GENERATE": {
            "NOT_SEARCHED": "generation is blocked: discovery was not searched",
            "SEARCH_INCOMPLETE": "generation is blocked: discovery is incomplete",
            "FOUND_UNBOUND": "generation is blocked: found asset is not bound to the requested role",
            "FOUND_USABLE": "generation is blocked: a usable asset must be reused",
            "FOUND_REPAIRABLE": "generation is blocked: a repairable asset must be repaired first",
            "BLOCKED": "generation is blocked by the discovery receipt",
        },
        "REPAIR": {
            "NOT_SEARCHED": "repair is blocked: discovery was not searched",
            "SEARCH_INCOMPLETE": "repair is blocked: discovery is incomplete",
            "FOUND_UNBOUND": "repair is blocked: found asset is not bound to the requested role",
            "FOUND_USABLE": "repair is unnecessary: reuse the usable asset",
            "CONFIRMED_ABSENT": "repair is impossible: no asset was confirmed present",
            "BLOCKED": "repair is blocked by the discovery receipt",
        },
        "REUSE": {
            "NOT_SEARCHED": "reuse is blocked: discovery was not searched",
            "SEARCH_INCOMPLETE": "reuse is blocked: discovery is incomplete",
            "FOUND_UNBOUND": "reuse is blocked: found asset is not bound to the requested role",
            "FOUND_REPAIRABLE": "reuse is blocked: the asset needs repair",
            "CONFIRMED_ABSENT": "reuse is impossible: receipt confirms absence",
            "BLOCKED": "reuse is blocked by the discovery receipt",
        },
        "PACKAGE": {
            "NOT_SEARCHED": "packaging is blocked: discovery was not searched",
            "SEARCH_INCOMPLETE": "packaging is blocked: discovery is incomplete",
            "BLOCKED": "packaging is blocked by the discovery receipt",
        },
    }
    if status in action_errors[action]:
        failures.append(action_errors[action][status])
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", required=True, type=Path)
    verify.add_argument("--action", default="GENERATE", choices=sorted(ACTIONS))
    verify.add_argument("--expected-scope", type=Path)
    invalidate = sub.add_parser("invalidate")
    invalidate.add_argument("--receipt", required=True, type=Path)
    invalidate.add_argument("--out", required=True, type=Path)
    invalidate.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            expected = load(args.expected_scope) if args.expected_scope else None
            failures = validate_receipt(args.receipt, expected_scope=expected, action=args.action)
            result = {"schema": SCHEMA, "status": "PASS" if not failures else "FAIL", "failures": failures}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if not failures else 2
        data = load(args.receipt)
        if data.get("schema") != SCHEMA:
            raise ValueError("unsupported discovery receipt schema")
        if args.out.exists():
            raise ValueError("invalidation output already exists; do not overwrite receipt history")
        data["status"] = "NOT_SEARCHED"
        data["invalidated"] = {
            "at": datetime.now(timezone.utc).isoformat(),
            "reason": text(args.reason, "reason"),
            "prior_receipt": {"path": str(args.receipt.resolve()), "sha256": sha256(args.receipt.resolve())},
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "INVALIDATED", "path": str(args.out.resolve()), "sha256": sha256(args.out)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "failures": [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
