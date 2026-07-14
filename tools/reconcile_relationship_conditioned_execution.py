#!/usr/bin/env python3
"""Idempotently reconcile RCE-P0-004 and RCE-P0-005.

Runs inside the established Core-Lite management workflow. It independently
reviews the committed sandbox candidate, persists an authoritative local
workflow receipt, updates task state, and stages candidate evidence only when
all predecessor and policy checks pass. It never targets production or an
external destination.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from reconstruct_relationship_conditioned_execution_bundle import review
from stage_relationship_conditioned_execution_sandbox import StagingError, stage

ROOT = Path(__file__).resolve().parents[1]
P0_004_TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_004.json"
P0_005_TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_005.json"
P0_004_RECEIPT = ROOT / "receipts/rce_p0_004_authoritative_validation.json"
P0_005_RECEIPT = ROOT / "receipts/rce_p0_005_authoritative_validation.json"
STATUS_PATH = ROOT / "reports/rce_automation_status.json"


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


def _run_identity() -> dict[str, Any]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-reconciliation"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def reconcile() -> dict[str, Any]:
    observed_at = datetime.now(timezone.utc).isoformat()
    identity = _run_identity()

    reconstruction = review()
    p0_004_success = (
        reconstruction.get("decision") == "ALLOW_CANDIDATE_INTAKE"
        and reconstruction.get("destination_mutation_performed") is False
        and reconstruction.get("manual_actions_required") == []
    )

    p0_004_receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-004-reconciler-{identity['run_id']}",
        "task_id": "RCE-P0-004",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_RECONSTRUCTION",
        "authoritative_completion_evidence": p0_004_success,
        "decision": reconstruction.get("decision", "DENY_CANDIDATE_INTAKE"),
        "destination_mutation_performed": False,
        "manual_actions_required": [],
        "report": "reports/rce_p0_004_reconstruction.json",
        "report_sha256": _sha(ROOT / "reports/rce_p0_004_reconstruction.json"),
    }
    _write(P0_004_RECEIPT, p0_004_receipt)

    p0_004_task = _load(P0_004_TASK)
    p0_004_task["status"] = "COMPLETE" if p0_004_success else "VALIDATION_FAILED"
    p0_004_task["validation"] = {
        "status": "PASS" if p0_004_success else "FAIL",
        "reconciler": "tools/reconcile_relationship_conditioned_execution.py",
        "authoritative_receipt": str(P0_004_RECEIPT.relative_to(ROOT)),
        "authoritative_completion_evidence": p0_004_success,
        "decision": p0_004_receipt["decision"],
        "destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    p0_004_task["blocked_by"] = [] if p0_004_success else ["reconstruction_or_policy_validation_failed"]
    if p0_004_success:
        p0_004_task["completed_at"] = observed_at
        p0_004_task["successor_task"] = "RCE-P0-005"
    _write(P0_004_TASK, p0_004_task)

    p0_005_success = False
    staging_manifest: dict[str, Any] = {}
    staging_error: str | None = None
    if p0_004_success:
        try:
            staging_manifest = stage(ROOT)
            p0_005_success = (
                staging_manifest.get("decision") == "STAGED_CANDIDATE_EVIDENCE"
                and staging_manifest.get("sandbox_only") is True
                and staging_manifest.get("candidate_evidence_only") is True
                and staging_manifest.get("production_destination_allowed") is False
                and staging_manifest.get("autonomous_execution_authority") is False
                and staging_manifest.get("human_harm_authority") is False
                and staging_manifest.get("external_destination_mutation_performed") is False
                and staging_manifest.get("manual_actions_required") == []
            )
        except (StagingError, OSError, ValueError, json.JSONDecodeError) as exc:
            staging_error = str(exc)

    p0_005_receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-005-reconciler-{identity['run_id']}",
        "task_id": "RCE-P0-005",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_SANDBOX_STAGING",
        "authoritative_completion_evidence": p0_005_success,
        "decision": "STAGED_CANDIDATE_EVIDENCE" if p0_005_success else "DENY_SANDBOX_STAGING",
        "source_receipt": str(P0_004_RECEIPT.relative_to(ROOT)),
        "source_receipt_sha256": _sha(P0_004_RECEIPT),
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
        "staging_error": staging_error,
    }
    if p0_005_success:
        stage_path = ROOT / "sandbox/intake/relationship_conditioned_execution/staging_manifest.json"
        p0_005_receipt["staging_manifest"] = str(stage_path.relative_to(ROOT))
        p0_005_receipt["staging_manifest_sha256"] = _sha(stage_path)
    _write(P0_005_RECEIPT, p0_005_receipt)

    p0_005_task = _load(P0_005_TASK)
    p0_005_task["activation_dependency"]["satisfied"] = p0_004_success
    p0_005_task["status"] = "COMPLETE" if p0_005_success else (
        "VALIDATION_FAILED" if p0_004_success else "WAITING_AUTOMATED_PREDECESSOR"
    )
    p0_005_task["blocked_by"] = [] if p0_005_success else [
        staging_error or "RCE-P0-004 authoritative ALLOW_CANDIDATE_INTAKE receipt not available"
    ]
    p0_005_task["validation"] = {
        "status": "PASS" if p0_005_success else "PENDING_OR_FAIL",
        "reconciler": "tools/reconcile_relationship_conditioned_execution.py",
        "authoritative_receipt": str(P0_005_RECEIPT.relative_to(ROOT)),
        "authoritative_completion_evidence": p0_005_success,
        "manual_actions_required": [],
    }
    if p0_005_success:
        p0_005_task["completed_at"] = observed_at
        p0_005_task["successor_task"] = "RCE-P0-006 sandbox custody and replay verification"
    _write(P0_005_TASK, p0_005_task)

    status = _load(STATUS_PATH) if STATUS_PATH.exists() else {}
    status.update({
        "schema": "stegverse.rce.automation_status.v1",
        **identity,
        "observed_at": observed_at,
        "manual_actions_required": [],
        "rce_p0_004": {
            "status": p0_004_task["status"],
            "decision": p0_004_receipt["decision"],
            "receipt": str(P0_004_RECEIPT.relative_to(ROOT)),
        },
        "rce_p0_005": {
            "status": p0_005_task["status"],
            "decision": p0_005_receipt["decision"],
            "receipt": str(P0_005_RECEIPT.relative_to(ROOT)),
        },
        "next_goal_candidate": (
            "RCE-P0-006 sandbox custody and replay verification"
            if p0_005_success else "repair_or_retry_automatically"
        ),
    })
    _write(STATUS_PATH, status)

    result = {
        "rce_p0_004": p0_004_task["status"],
        "rce_p0_005": p0_005_task["status"],
        "manual_actions_required": [],
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    result = reconcile()
    return 0 if result["rce_p0_004"] == "COMPLETE" and result["rce_p0_005"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
