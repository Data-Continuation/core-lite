#!/usr/bin/env python3
"""Continuously guard attested RCE restoration equivalence.

The guard emits a clean machine-readable status when source, snapshot, and
restored evidence remain equivalent. On divergence it preserves a sandbox-only
alert record and fails closed. It never deletes evidence or targets production.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
RESTORATION = ROOT / "sandbox/restoration_drills/relationship_conditioned_execution/restoration_manifest.json"
PREDECESSOR = ROOT / "receipts/rce_p0_012_authoritative_validation.json"
REPORT = ROOT / "reports/rce_p0_013_divergence_guard.json"
RECEIPT = ROOT / "receipts/rce_p0_013_authoritative_validation.json"
ALERT = ROOT / "sandbox/quarantine/relationship_conditioned_execution/divergence_alert.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_013.json"


class GuardError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GuardError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity() -> dict[str, str]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-divergence-guard"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def guard(root: Path = ROOT) -> dict[str, Any]:
    predecessor_path = root / PREDECESSOR.relative_to(ROOT)
    snapshot_path = root / SNAPSHOT.relative_to(ROOT)
    restoration_path = root / RESTORATION.relative_to(ROOT)
    report_path = root / REPORT.relative_to(ROOT)
    receipt_path = root / RECEIPT.relative_to(ROOT)
    alert_path = root / ALERT.relative_to(ROOT)
    task_path = root / TASK.relative_to(ROOT)

    predecessor = _load(predecessor_path)
    if predecessor.get("task_id") != "RCE-P0-012":
        raise GuardError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise GuardError("P0-012 is not authoritatively complete")
    if predecessor.get("decision") != "RESTORATION_EQUIVALENCE_ATTESTED":
        raise GuardError("restoration equivalence was not attested")
    if predecessor.get("manual_actions_required") != []:
        raise GuardError("predecessor still requires manual actions")

    snapshot = _load(snapshot_path)
    restoration = _load(restoration_path)
    expected_entries = snapshot.get("entries")
    observed_entries = restoration.get("entries")
    if not isinstance(expected_entries, list) or not isinstance(observed_entries, list):
        raise GuardError("evidence entries missing")

    expected = {item["path"]: item for item in expected_entries if isinstance(item, dict) and isinstance(item.get("path"), str)}
    observed = {item["source_path"]: item for item in observed_entries if isinstance(item, dict) and isinstance(item.get("source_path"), str)}
    divergences: list[dict[str, Any]] = []

    for relative in sorted(set(expected) | set(observed)):
        exp = expected.get(relative)
        obs = observed.get(relative)
        if exp is None or obs is None:
            divergences.append({"path": relative, "reason": "membership_divergence"})
            continue
        source = root / relative
        restored = root / str(obs.get("restored_path", ""))
        source_sha = _sha(source) if source.is_file() else None
        restored_sha = _sha(restored) if restored.is_file() else None
        source_bytes = source.stat().st_size if source.is_file() else None
        restored_bytes = restored.stat().st_size if restored.is_file() else None
        expected_sha = exp.get("sha256")
        expected_bytes = exp.get("bytes")
        if source_sha != expected_sha or restored_sha != expected_sha or source_bytes != expected_bytes or restored_bytes != expected_bytes:
            divergences.append({
                "path": relative,
                "reason": "content_divergence",
                "expected_sha256": expected_sha,
                "source_sha256": source_sha,
                "restored_sha256": restored_sha,
                "expected_bytes": expected_bytes,
                "source_bytes": source_bytes,
                "restored_bytes": restored_bytes,
            })

    if restoration.get("snapshot_root_sha256") != snapshot.get("snapshot_root_sha256"):
        divergences.append({"path": str(restoration_path.relative_to(root)), "reason": "snapshot_root_divergence"})

    observed_at = datetime.now(timezone.utc).isoformat()
    decision = "DIVERGENCE_GUARD_ARMED" if not divergences else "EVIDENCE_DIVERGENCE_QUARANTINED"
    report = {
        "schema": "stegverse.rce.divergence_guard.v1",
        "task_id": "RCE-P0-013",
        "decision": decision,
        "snapshot_root_sha256": snapshot.get("snapshot_root_sha256"),
        "checked_entry_count": len(expected),
        "divergence_count": len(divergences),
        "divergences": divergences,
        "source_evidence_modified": False,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "manual_actions_required": [],
        "observed_at": observed_at,
    }
    _write(report_path, report)

    if divergences:
        _write(alert_path, {
            "schema": "stegverse.rce.divergence_alert.v1",
            "task_id": "RCE-P0-013",
            "decision": decision,
            "report": str(report_path.relative_to(root)),
            "report_sha256": _sha(report_path),
            "divergences": divergences,
            "evidence_deleted": False,
            "sandbox_only": True,
            "manual_actions_required": [],
            "observed_at": observed_at,
        })
    elif alert_path.exists():
        alert_path.unlink()

    identity = _identity()
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-013-guard-{identity['run_id']}",
        "task_id": "RCE-P0-013",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_DIVERGENCE_GUARD",
        "authoritative_completion_evidence": not divergences,
        "decision": decision,
        "report": str(report_path.relative_to(root)),
        "report_sha256": _sha(report_path),
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    if divergences:
        receipt["quarantine_alert"] = str(alert_path.relative_to(root))
        receipt["quarantine_alert_sha256"] = _sha(alert_path)
    _write(receipt_path, receipt)

    task = _load(task_path)
    task["activation_dependency"]["satisfied"] = True
    task["status"] = "COMPLETE" if not divergences else "QUARANTINED"
    task["blocked_by"] = [] if not divergences else ["restoration evidence divergence detected"]
    task["validation"] = {
        "status": "PASS" if not divergences else "FAIL_CLOSED",
        "authoritative_completion_evidence": not divergences,
        "authoritative_receipt": str(receipt_path.relative_to(root)),
        "decision": decision,
        "manual_actions_required": [],
    }
    if not divergences:
        task["completed_at"] = observed_at
        task["successor_task"] = "RCE-P0-014 automated continuity checkpoint publication candidate"
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = guard()
    except (GuardError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"decision": "DENY_DIVERGENCE_GUARD", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "divergence_count": result["divergence_count"], "manual_actions_required": []}, sort_keys=True))
    return 0 if result["divergence_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
