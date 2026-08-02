#!/usr/bin/env python3
"""Run or verify the canonical repository-local RCE continuation.

This adapter transfers RCE-P0-007 through RCE-P0-014 into the repository's
reference closure loop. It invokes only committed, sandbox-bounded tools and
then verifies their durable receipts and task states. It grants no external,
production, publication, installation, autonomous-execution, or human-harm
authority.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rce_session_reconciliation.json"

STAGES = [
    ("RCE-P0-007", "tools/manage_relationship_conditioned_execution_lifecycle.py", "receipts/rce_p0_007_authoritative_validation.json"),
    ("RCE-P0-008", "tools/manage_relationship_conditioned_execution_lease.py", "receipts/rce_p0_008_authoritative_validation.json"),
    ("RCE-P0-009", "tools/index_relationship_conditioned_execution_evidence.py", "receipts/rce_p0_009_authoritative_validation.json"),
    ("RCE-P0-010", "tools/seal_relationship_conditioned_execution_snapshot.py", "receipts/rce_p0_010_authoritative_validation.json"),
    ("RCE-P0-011", "tools/restore_relationship_conditioned_execution_snapshot.py", "receipts/rce_p0_011_authoritative_validation.json"),
    ("RCE-P0-012", "tools/monitor_relationship_conditioned_execution_restoration.py", "receipts/rce_p0_012_authoritative_validation.json"),
    ("RCE-P0-013", "tools/guard_relationship_conditioned_execution_restoration.py", "receipts/rce_p0_013_authoritative_validation.json"),
    ("RCE-P0-014", "tools/build_relationship_conditioned_execution_checkpoint.py", "receipts/rce_p0_014_authoritative_validation.json"),
]

EXPECTED_DECISIONS = {
    "RCE-P0-009": {"RECONSTRUCTION_INDEX_VERIFIED"},
    "RCE-P0-010": {"SANDBOX_EVIDENCE_SNAPSHOT_SEALED"},
    "RCE-P0-011": {"SEALED_SNAPSHOT_RESTORATION_VERIFIED"},
    "RCE-P0-012": {"RESTORATION_EQUIVALENCE_ATTESTED"},
    "RCE-P0-013": {"DIVERGENCE_GUARD_ARMED"},
    "RCE-P0-014": {"CONTINUITY_CHECKPOINT_CANDIDATE_READY"},
}

class ReconciliationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReconciliationError(f"JSON root must be an object: {path}")
    return value


def verify_stage(task_id: str, receipt_relative: str) -> dict[str, Any]:
    receipt_path = ROOT / receipt_relative
    if not receipt_path.is_file():
        raise ReconciliationError(f"missing authoritative receipt: {receipt_relative}")
    receipt = load(receipt_path)
    if receipt.get("task_id") != task_id:
        raise ReconciliationError(f"unexpected task id in {receipt_relative}")
    if receipt.get("authoritative_completion_evidence") is not True:
        raise ReconciliationError(f"non-authoritative completion evidence: {task_id}")
    if receipt.get("manual_actions_required") != []:
        raise ReconciliationError(f"manual action remains: {task_id}")
    if receipt.get("production_destination_allowed") is True:
        raise ReconciliationError(f"production authority expansion: {task_id}")
    if receipt.get("external_destination_mutation_performed") is True:
        raise ReconciliationError(f"external destination mutation: {task_id}")
    expected = EXPECTED_DECISIONS.get(task_id)
    if expected and receipt.get("decision") not in expected:
        raise ReconciliationError(f"unexpected decision for {task_id}: {receipt.get('decision')}")
    task_path = ROOT / "core_lite/tasks" / f"relationship_conditioned_execution_p0_{int(task_id.rsplit('-', 1)[1]):03d}.json"
    task = load(task_path)
    if task.get("status") != "COMPLETE":
        raise ReconciliationError(f"task is not complete: {task_id}")
    return {
        "task_id": task_id,
        "decision": receipt.get("decision"),
        "receipt": receipt_relative,
        "status": "COMPLETE",
    }


def reconcile(verify_only: bool = False) -> dict[str, Any]:
    executions: list[dict[str, Any]] = []
    if not verify_only:
        for task_id, tool_relative, _ in STAGES:
            tool = ROOT / tool_relative
            if not tool.is_file():
                raise ReconciliationError(f"missing stage tool: {tool_relative}")
            result = subprocess.run(
                [sys.executable, str(tool)], cwd=ROOT, text=True,
                capture_output=True, check=False,
            )
            executions.append({
                "task_id": task_id,
                "tool": tool_relative,
                "exit_code": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            })
            if result.returncode != 0:
                raise ReconciliationError(f"{task_id} failed closed with exit code {result.returncode}")

    verified = [verify_stage(task_id, receipt) for task_id, _, receipt in STAGES]
    report = {
        "schema": "stegverse.core_lite.rce_session_reconciliation.v1",
        "repository": "Data-Continuation/core-lite",
        "canonical_owner": "core_lite_reference_loop",
        "canonical_task": "REF-LOOP-007",
        "decision": "RCE_CANONICAL_WORKSTREAM_RECONCILED",
        "verified_stages": verified,
        "executions": executions,
        "sandbox_only": True,
        "external_repository_mutation": False,
        "production_mutation": False,
        "publication_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "manual_actions_required": [],
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        report = reconcile(verify_only=args.verify)
    except (OSError, json.JSONDecodeError, ReconciliationError) as exc:
        print(json.dumps({
            "decision": "ESCALATE_RCE_RECONCILIATION_FAIL_CLOSED",
            "error": str(exc),
            "external_repository_mutation": False,
            "manual_actions_required": [],
        }, sort_keys=True))
        return 1
    print(json.dumps({
        "decision": report["decision"],
        "verified_stage_count": len(report["verified_stages"]),
        "manual_actions_required": [],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
