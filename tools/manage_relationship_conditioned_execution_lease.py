#!/usr/bin/env python3
"""Manage bounded sandbox lease renewal and fail-closed quarantine for RCE."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "sandbox/intake/relationship_conditioned_execution"
QUARANTINE = ROOT / "sandbox/quarantine/relationship_conditioned_execution"
LIFECYCLE = STAGE / "lifecycle_state.json"
LEASE = STAGE / "lease_state.json"
P0_007_RECEIPT = ROOT / "receipts/rce_p0_007_authoritative_validation.json"
REPORT = ROOT / "reports/rce_p0_008_lease.json"
RECEIPT = ROOT / "receipts/rce_p0_008_authoritative_validation.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_008.json"
LEASE_HOURS = 24


class LeaseError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LeaseError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> datetime:
    raw = os.environ.get("RCE_OBSERVED_AT")
    return datetime.fromisoformat(raw.replace("Z", "+00:00")) if raw else datetime.now(timezone.utc)


def reconcile(root: Path = ROOT) -> dict[str, Any]:
    stage = root / "sandbox/intake/relationship_conditioned_execution"
    quarantine = root / "sandbox/quarantine/relationship_conditioned_execution"
    lifecycle_path = stage / "lifecycle_state.json"
    lease_path = stage / "lease_state.json"
    receipt7_path = root / "receipts/rce_p0_007_authoritative_validation.json"
    report_path = root / "reports/rce_p0_008_lease.json"
    receipt8_path = root / "receipts/rce_p0_008_authoritative_validation.json"
    task_path = root / "core_lite/tasks/relationship_conditioned_execution_p0_008.json"

    predecessor = _load(receipt7_path)
    if predecessor.get("task_id") != "RCE-P0-007" or predecessor.get("authoritative_completion_evidence") is not True:
        raise LeaseError("P0-007 is not authoritatively complete")
    if predecessor.get("manual_actions_required") != []:
        raise LeaseError("predecessor still requires manual actions")

    lifecycle = _load(lifecycle_path)
    safe = all([
        lifecycle.get("sandbox_only") is True,
        lifecycle.get("production_destination_allowed") is False,
        lifecycle.get("external_destination_mutation_performed") is False,
        lifecycle.get("autonomous_execution_authority") is False,
        lifecycle.get("human_harm_authority") is False,
    ])
    if not safe:
        raise LeaseError("lifecycle authority boundary invalid")

    now = _now()
    content = lifecycle.get("content_sha256")
    prior = _load(lease_path) if lease_path.exists() else None
    decision = "ISSUE_SANDBOX_LEASE"
    quarantine_path: str | None = None

    if prior:
        unchanged = (
            prior.get("package_id") == lifecycle.get("package_id")
            and prior.get("active_version") == lifecycle.get("active_version")
            and prior.get("content_sha256") == content
        )
        prior_expiry = datetime.fromisoformat(str(prior["expires_at"]).replace("Z", "+00:00"))
        if unchanged and prior_expiry >= now:
            decision = "RENEW_SANDBOX_LEASE"
        else:
            if quarantine.exists():
                shutil.rmtree(quarantine)
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(stage, quarantine)
            quarantine_path = str(quarantine.relative_to(root))
            decision = "QUARANTINE_SANDBOX_CANDIDATE"

    issued = now
    expires = now + timedelta(hours=LEASE_HOURS)
    lease_state = {
        "schema": "stegverse.rce.sandbox_lease.v1",
        "task_id": "RCE-P0-008",
        "package_id": lifecycle.get("package_id"),
        "active_version": lifecycle.get("active_version"),
        "content_sha256": content,
        "decision": decision,
        "issued_at": issued.isoformat(),
        "expires_at": expires.isoformat(),
        "lease_hours": LEASE_HOURS,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "source_receipt": str(receipt7_path.relative_to(root)),
        "source_receipt_sha256": _sha(receipt7_path),
        "quarantine_path": quarantine_path,
        "manual_actions_required": [],
    }
    _write(lease_path, lease_state)
    _write(report_path, lease_state)

    identity = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-lease"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }
    success = decision in {"ISSUE_SANDBOX_LEASE", "RENEW_SANDBOX_LEASE"}
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-008-lease-{identity['run_id']}",
        "task_id": "RCE-P0-008",
        **identity,
        "observed_at": now.isoformat(),
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_SANDBOX_LEASE",
        "authoritative_completion_evidence": success,
        "decision": decision,
        "lease_state": str(lease_path.relative_to(root)),
        "lease_state_sha256": _sha(lease_path),
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    _write(receipt8_path, receipt)

    task = _load(task_path)
    task["activation_dependency"]["satisfied"] = True
    task["status"] = "COMPLETE" if success else "QUARANTINED"
    task["blocked_by"] = [] if success else ["candidate expired or evidence drifted; quarantined automatically"]
    task["validation"] = {
        "status": "PASS" if success else "FAIL_CLOSED_QUARANTINED",
        "authoritative_completion_evidence": success,
        "authoritative_receipt": str(receipt8_path.relative_to(root)),
        "decision": decision,
        "manual_actions_required": [],
    }
    if success:
        task["completed_at"] = now.isoformat()
        task["successor_task"] = "RCE-P0-009 sandbox health and renewal continuity"
    _write(task_path, task)
    return lease_state


def main() -> int:
    try:
        result = reconcile()
    except (LeaseError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"decision": "DENY_LEASE_TRANSITION", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "manual_actions_required": []}, sort_keys=True))
    return 0 if result["decision"] != "QUARANTINE_SANDBOX_CANDIDATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
