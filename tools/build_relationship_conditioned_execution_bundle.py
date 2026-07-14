#!/usr/bin/env python3
"""Build the deterministic sandbox-only RCE ingestion candidate package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "bundles" / "relationship_conditioned_execution"

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


def file_record(order: int, kind: str, source: str) -> dict[str, object]:
    path = ROOT / source
    data = path.read_bytes()
    return {
        "order": order,
        "kind": kind,
        "source_path": source,
        "target_path": f"sandbox/relationship_conditioned_execution/{source}",
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build() -> dict[str, object]:
    records = [file_record(i, kind, source) for i, (kind, source) in enumerate(SOURCES, 1)]
    inventory = {
        "schema": "stegverse.rce.source_inventory.v1",
        "package_id": "relationship-conditioned-execution",
        "candidate_evidence_only": True,
        "autonomous_execution_authority": False,
        "files": records,
    }
    inventory_digest = hashlib.sha256(canonical_bytes(inventory)).hexdigest()

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
                "order": record["order"],
                "operation": "copy_candidate_evidence",
                "source_path": record["source_path"],
                "target_path": record["target_path"],
                "expected_sha256": record["sha256"],
                "expected_bytes": record["bytes"],
            }
            for record in records
        ],
    }
    plan_digest = hashlib.sha256(canonical_bytes(install_plan)).hexdigest()

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
        "source_inventory_sha256": inventory_digest,
        "install_plan_path": "bundles/relationship_conditioned_execution/install_plan.json",
        "install_plan_sha256": plan_digest,
        "file_count": len(records),
        "dependency_order": ["policy", "schema", "validator", "fixture"],
        "receipts_required": True,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "source_inventory.json").write_bytes(canonical_bytes(inventory))
    (OUT / "install_plan.json").write_bytes(canonical_bytes(install_plan))
    (OUT / "bundle_manifest.json").write_bytes(canonical_bytes(manifest))
    return manifest


def main() -> int:
    manifest = build()
    print(f"RCE_BUNDLE_BUILT:{manifest['file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
