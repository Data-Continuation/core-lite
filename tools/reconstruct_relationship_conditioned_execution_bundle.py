#!/usr/bin/env python3
"""Independently reconstruct and review the committed RCE sandbox bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "bundles" / "relationship_conditioned_execution"
REPORT = ROOT / "reports" / "rce_p0_004_reconstruction.json"

SOURCES = [
    ("policy", "docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md"),
    ("schema", "schemas/relationship_conditioned_human_decision_policy.schema.json"),
    ("schema", "schemas/execution_candidate_manifest.schema.json"),
    ("validator", "tools/validate_relationship_conditioned_human_decision_policy.py"),
    ("validator", "tools/validate_execution_candidate_manifest.py"),
    ("fixture", "samples/relationship_conditioned_human_decision_policy.example.json"),
    ("fixture", "samples/execution_candidate_manifest.allow.example.json"),
    ("fixture", "samples/execution_candidate_manifest.stale_state.example.json"),
    ("fixture", "samples/execution_candidate_manifest.scope_leakage.example.json"),
]


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reconstruct() -> tuple[dict, dict, dict]:
    files = []
    for order, (kind, source) in enumerate(SOURCES, 1):
        data = (ROOT / source).read_bytes()
        files.append({
            "order": order,
            "kind": kind,
            "source_path": source,
            "target_path": f"sandbox/relationship_conditioned_execution/{source}",
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })

    inventory = {
        "schema": "stegverse.rce.source_inventory.v1",
        "package_id": "relationship-conditioned-execution",
        "candidate_evidence_only": True,
        "autonomous_execution_authority": False,
        "files": files,
    }
    install_plan = {
        "schema": "stegverse.rce.install_plan.v1",
        "package_id": "relationship-conditioned-execution",
        "mode": "sandbox_only",
        "candidate_evidence_only": True,
        "automatic_destination_mutation": False,
        "autonomous_execution_authority": False,
        "destination_root": "sandbox/relationship_conditioned_execution",
        "operations": [
            {
                "order": item["order"],
                "operation": "copy_candidate_evidence",
                "source_path": item["source_path"],
                "target_path": item["target_path"],
                "expected_sha256": item["sha256"],
                "expected_bytes": item["bytes"],
            }
            for item in files
        ],
    }
    manifest = {
        "schema": "stegverse.rce.bundle_manifest.v1",
        "package_id": "relationship-conditioned-execution",
        "package_version": "1.0.0-sandbox-candidate",
        "candidate_evidence_only": True,
        "sandbox_only": True,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "production_destination_allowed": False,
        "source_inventory_path": "bundles/relationship_conditioned_execution/source_inventory.json",
        "source_inventory_sha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
        "install_plan_path": "bundles/relationship_conditioned_execution/install_plan.json",
        "install_plan_sha256": hashlib.sha256(canonical_bytes(install_plan)).hexdigest(),
        "file_count": len(files),
        "dependency_order": ["policy", "schema", "validator", "fixture"],
        "receipts_required": True,
    }
    return manifest, inventory, install_plan


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def review() -> dict:
    expected_manifest, expected_inventory, expected_plan = reconstruct()
    committed = {
        "bundle_manifest.json": (BUNDLE / "bundle_manifest.json").read_bytes(),
        "source_inventory.json": (BUNDLE / "source_inventory.json").read_bytes(),
        "install_plan.json": (BUNDLE / "install_plan.json").read_bytes(),
    }
    expected = {
        "bundle_manifest.json": canonical_bytes(expected_manifest),
        "source_inventory.json": canonical_bytes(expected_inventory),
        "install_plan.json": canonical_bytes(expected_plan),
    }
    matches = {name: committed[name] == expected[name] for name in committed}

    receipt = load_json(ROOT / "receipts" / "rce_p0_003_authoritative_validation.json")
    receipt_valid = (
        receipt.get("task_id") == "RCE-P0-003"
        and receipt.get("authoritative_completion_evidence") is True
    )
    policy_valid = all([
        expected_manifest["candidate_evidence_only"] is True,
        expected_manifest["sandbox_only"] is True,
        expected_manifest["autonomous_execution_authority"] is False,
        expected_manifest["human_harm_authority"] is False,
        expected_manifest["production_destination_allowed"] is False,
        expected_plan["automatic_destination_mutation"] is False,
    ])
    allow = all(matches.values()) and receipt_valid and policy_valid

    report = {
        "schema": "stegverse.rce.reconstruction_report.v1",
        "task_id": "RCE-P0-004",
        "package_id": "relationship-conditioned-execution",
        "independent_reconstruction": True,
        "builder_imported": False,
        "byte_matches": matches,
        "p0_003_authoritative_receipt_valid": receipt_valid,
        "sandbox_policy_valid": policy_valid,
        "decision": "ALLOW_CANDIDATE_INTAKE" if allow else "DENY_CANDIDATE_INTAKE",
        "candidate_intake_only": True,
        "destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "manual_actions_required": [],
    }
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_bytes(canonical_bytes(report))
    return report


def main() -> int:
    report = review()
    print(report["decision"])
    return 0 if report["decision"] == "ALLOW_CANDIDATE_INTAKE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
