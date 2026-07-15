#!/usr/bin/env python3
"""Build or verify a read-only portability manifest for the reference loop."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "core_lite/reference_loop_state.json"
RECEIPT_CONTRACT = ROOT / "reports/reference_loop_receipt_contract.json"
SITE_STATUS = ROOT / "reports/reference_loop_site_status.json"
REPORT = ROOT / "reports/reference_loop_portability_manifest.json"


class PortabilityManifestError(ValueError):
    pass


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise PortabilityManifestError(f"required evidence missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PortabilityManifestError(f"required evidence is not an object: {path}")
    return value


def manifest_for(state: dict[str, Any], receipt_contract: dict[str, Any], site_status: dict[str, Any]) -> dict[str, Any]:
    tasks = state.get("tasks")
    if not isinstance(tasks, dict):
        raise PortabilityManifestError("reference state has no task ledger")
    required = [f"REF-LOOP-{index:03d}" for index in range(1, 6)]
    incomplete = [task_id for task_id in required if tasks.get(task_id, {}).get("status") != "complete"]
    if incomplete:
        raise PortabilityManifestError(f"incomplete tasks: {', '.join(incomplete)}")
    if receipt_contract.get("decision") != "RECEIPT_CONTRACT_VERIFIED":
        raise PortabilityManifestError("receipt contract is not verified")
    if site_status.get("decision") != "SITE_STATUS_CONTRACT_VERIFIED":
        raise PortabilityManifestError("Site status contract is not verified")
    if receipt_contract.get("authority", {}).get("external_repository_mutation") is not False:
        raise PortabilityManifestError("receipt contract does not deny external mutation")
    if site_status.get("authority", {}).get("external_repository_mutation") is not False:
        raise PortabilityManifestError("Site status contract does not deny external mutation")

    return {
        "schema": "stegverse.core_lite.reference_portability_manifest.v1",
        "source_repository": "Data-Continuation/core-lite",
        "target_repository": "StegVerse-org/demo_ingest_engine",
        "relationship": "read_only_portability_and_intake_compatibility_contract",
        "completed_tasks": required,
        "source_evidence": {
            "reference_state_sha256": digest(state),
            "receipt_contract_sha256": digest(receipt_contract),
            "site_status_sha256": digest(site_status),
            "receipt_chain_head": receipt_contract.get("chain_head"),
            "receipt_chain_sha256": receipt_contract.get("chain_sha256"),
        },
        "required_consumer_capabilities": [
            "accept_manifest_without_execution",
            "verify_source_evidence_digests",
            "preserve_origin_repository_identity",
            "preserve_receipt_chain_head",
            "deny_installation_without_separate_authority",
        ],
        "authority": {
            "read_only_manifest": True,
            "installation_authorized": False,
            "ingestion_authorized": False,
            "publication_authorized": False,
            "external_repository_mutation": False,
            "production_mutation": False,
        },
        "decision": "PORTABILITY_MANIFEST_VERIFIED",
        "manual_actions_required": [],
    }


def write_report(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--receipt-contract", type=Path, default=RECEIPT_CONTRACT)
    parser.add_argument("--site-status", type=Path, default=SITE_STATUS)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        expected = manifest_for(load_json(args.state), load_json(args.receipt_contract), load_json(args.site_status))
        if args.verify:
            observed = load_json(args.report)
            if observed != expected:
                raise PortabilityManifestError("portability manifest does not match verified source evidence")
        else:
            write_report(args.report, expected)
    except (OSError, json.JSONDecodeError, PortabilityManifestError) as exc:
        print(json.dumps({"decision": "DENY_PORTABILITY_MANIFEST", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"decision": expected["decision"], "target_repository": expected["target_repository"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
