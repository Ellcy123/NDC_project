#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from audit_expression_delivery_release import (
    GENERATED_GATES,
    LEGACY_AMPLITUDE_EXCEPTION,
    LEGACY_AMPLITUDE_WAIVER,
    REUSE_GATES,
    SCHEMA,
    audit,
)


class ReleaseAuditTests(unittest.TestCase):
    def make_registry(self, root: Path, gate_status: str = "PASS") -> Path:
        delivery = root / "delivery"
        evidence = root / "evidence"
        output = delivery / "role" / "transparent" / "role_calm.png"
        output.parent.mkdir(parents=True)
        evidence.mkdir()
        output.write_bytes(b"current-asset")
        evidence_file = evidence / "review.json"
        evidence_file.write_text('{"formal_status":"PASS"}\n', encoding="utf-8")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        gates = {gate: gate_status for gate in GENERATED_GATES}
        proofs = {gate: [str(evidence_file)] for gate in GENERATED_GATES}
        row = {
            "character_id": "role",
            "expression_id": "calm",
            "profile": "transparent",
            "relative_path": "role/transparent/role_calm.png",
            "route": "GENERATED_CURRENT_SPEC",
            "sha256": digest,
            "native_source_sha256": "a" * 64,
            "gates": gates,
            "evidence": proofs,
        }
        registry = {
            "schema": SCHEMA,
            "delivery_root": str(delivery),
            "required_profiles": ["transparent"],
            "expected_inventory": [{
                "character_id": "role", "expression_id": "calm", "profile": "transparent"
            }],
            "assets": [row],
        }
        path = root / "registry.json"
        path.write_text(json.dumps(registry), encoding="utf-8")
        return path

    def test_current_complete_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = audit(self.make_registry(Path(temp)))
            self.assertEqual(result["release_status"], "PASS")

    def test_not_checked_blocks_even_when_inventory_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = audit(self.make_registry(Path(temp), "NOT_CHECKED"))
            self.assertEqual(result["completeness_status"], "PASS")
            self.assertEqual(result["release_status"], "FAIL")
            self.assertTrue(any("NOT_CHECKED" in error for error in result["errors"]))

    def test_stale_hash_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_registry(Path(temp))
            registry = json.loads(path.read_text(encoding="utf-8"))
            registry["assets"][0]["sha256"] = "0" * 64
            path.write_text(json.dumps(registry), encoding="utf-8")
            result = audit(path)
            self.assertEqual(result["release_status"], "FAIL")
            self.assertTrue(any("stale" in error for error in result["errors"]))

    def test_reuse_must_pass_current_gates_and_have_no_exceptions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.make_registry(root)
            registry = json.loads(path.read_text(encoding="utf-8"))
            row = registry["assets"][0]
            source = root / "approved.png"
            source.write_bytes((root / "delivery" / row["relative_path"]).read_bytes())
            evidence_file = root / "evidence" / "review.json"
            row.update(
                {
                    "route": "REUSE_APPROVED_AS_IS",
                    "approved_source_path": str(source),
                    "approved_source_sha256": row["sha256"],
                    "legacy_approved_source": True,
                    "current_spec_exceptions": [],
                    "gates": {gate: "PASS" for gate in REUSE_GATES},
                    "evidence": {gate: [str(evidence_file)] for gate in REUSE_GATES},
                }
            )
            path.write_text(json.dumps(registry), encoding="utf-8")
            result = audit(path)
            self.assertEqual(result["release_status"], "PASS")
            row["gates"]["thumbnail_readability"] = LEGACY_AMPLITUDE_WAIVER
            row["current_spec_exceptions"] = [LEGACY_AMPLITUDE_EXCEPTION]
            path.write_text(json.dumps(registry), encoding="utf-8")
            result = audit(path)
            self.assertEqual(result["release_status"], "PASS")
            row["gates"]["identity_style_viewpoint"] = LEGACY_AMPLITUDE_WAIVER
            path.write_text(json.dumps(registry), encoding="utf-8")
            result = audit(path)
            self.assertEqual(result["release_status"], "FAIL")
            self.assertTrue(any("identity_style_viewpoint" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
