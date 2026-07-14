#!/usr/bin/env python3
"""Verify RCE sandbox custody, receipt chaining, and deterministic replay."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from reconstruct_relationship_conditioned_execution_bundle import review

ROOT = Path(__file__).resolve().parents[1]
STAGE_MANIFEST = ROOT / "sandbox/intake/relationship_conditioned_execution/staging_manifest.json"
P0_004_RECEIPT = ROOT / "receipts/rce_p0_004_authoritative_validation.json"
P0_005_RECEIPT = ROOT / "receipts/rce_p0_005_authoritative_validation.json"
REPORT = ROOT / "reports/rce_p0_006_custody_replay.json"
RECEIPT = ROOT / "receipts/rce_p0_006_authoritative_validation.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_006.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, Any]:
    observed_at = datetime.now(timezone.utc).isoformat()
    stage_manifest = _load(STAGE_MANIFEST)
    p0_004 = _load(P0_004_RECEIPT)
    p0_005 = _load(P0_005_RECEIPT)

    predecessor_receipt_valid = (
        p0_005.get("task_id") == "RCE-P0-005"
        and p0_005.get("authoritative_completion_evidence") is True
        and p0_005.get("decision") == "STAGED_CANDIDATE_EVIDENCE"
        and p0_005.get("external_destination_mutation_performed") is False
        and p0_005.get("manual_actions_required") == []
    )
    receipt_chain_valid = (
        p0_005.get("source_receipt") == str(P0_004_RECEIPT.relative_to(ROOT))
        and p0_005.get("source_receipt_sha256") == _sha(P0_004_RECEIPT)
        and p0_004.get("authoritative_completion_evidence") is True
        and p0_004.get("decision") == "ALLOW_CANDIDATE_INTAKE"
    )

    file_results: list[dict[str, Any]] = []
    for entry in stage_manifest.get("files", []):
        source = ROOT / entry["source_path"]
        target = ROOT / entry["target_path"]
        source_exists = source.is_file()
        target_exists = target.is_file()
        source_hash = _sha(source) if source_exists else None
        target_hash = _sha(target) if target_exists else None
        source_bytes = source.stat().st_size if source_exists else None
        target_bytes = target.stat().st_size if target_exists else None
        valid = all([
            source_exists,
            target_exists,
            source_hash == entry.get("sha256"),
            target_hash == entry.get("sha256"),
            source_bytes == entry.get("bytes"),
            target_bytes == entry.get("bytes"),
            source.read_bytes() == target.read_bytes() if source_exists and target_exists else False,
        ])
        file_results.append({
            "source_path": entry.get("source_path"),
            "target_path": entry.get("target_path"),
            "sha256": entry.get("sha256"),
            "bytes": entry.get("bytes"),
            "valid": valid,
        })

    replay = review()
    replay_valid = replay.get("decision") == "ALLOW_CANDIDATE_INTAKE"
    policy_valid = all([
        stage_manifest.get("sandbox_only") is True,
        stage_manifest.get("candidate_evidence_only") is True,
        stage_manifest.get("production_destination_allowed") is False,
        stage_manifest.get("autonomous_execution_authority") is False,
        stage_manifest.get("human_harm_authority") is False,
        stage_manifest.get("external_destination_mutation_performed") is False,
        stage_manifest.get("manual_actions_required") == [],
    ])

    success = all([
        predecessor_receipt_valid,
        receipt_chain_valid,
        bool(file_results),
        all(item["valid"] for item in file_results),
        replay_valid,
        policy_valid,
    ])

    report = {
        "schema": "stegverse.rce.custody_replay_report.v1",
        "task_id": "RCE-P0-006",
        "observed_at": observed_at,
        "decision": "CUSTODY_AND_REPLAY_VERIFIED" if success else "DENY_CUSTODY_OR_REPLAY",
        "predecessor_receipt_valid": predecessor_receipt_valid,
        "receipt_chain_valid": receipt_chain_valid,
        "staged_files": file_results,
        "deterministic_replay_valid": replay_valid,
        "sandbox_policy_valid": policy_valid,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    _write(REPORT, report)

    identity = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-verification"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-006-custody-replay-{identity['run_id']}",
        "task_id": "RCE-P0-006",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_CUSTODY_REPLAY",
        "authoritative_completion_evidence": success,
        "decision": report["decision"],
        "source_receipt": str(P0_005_RECEIPT.relative_to(ROOT)),
        "source_receipt_sha256": _sha(P0_005_RECEIPT),
        "report": str(REPORT.relative_to(ROOT)),
        "report_sha256": _sha(REPORT),
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    _write(RECEIPT, receipt)

    task = _load(TASK)
    task["status"] = "COMPLETE" if success else "VALIDATION_FAILED"
    task["blocked_by"] = [] if success else ["custody_or_replay_verification_failed"]
    task["validation"] = {
        "status": "PASS" if success else "FAIL",
        "authoritative_receipt": str(RECEIPT.relative_to(ROOT)),
        "authoritative_completion_evidence": success,
        "decision": report["decision"],
        "manual_actions_required": [],
    }
    if success:
        task["completed_at"] = observed_at
        task["successor_task"] = "RCE-P0-007 sandbox lifecycle and supersession automation"
    _write(TASK, task)

    print(report["decision"])
    return report


def main() -> int:
    return 0 if verify()["decision"] == "CUSTODY_AND_REPLAY_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
