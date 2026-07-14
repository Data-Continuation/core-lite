#!/usr/bin/env python3
"""Verify three-way equivalence between snapshot, live source, and restoration drill."""

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
PREDECESSOR = ROOT / "receipts/rce_p0_011_authoritative_validation.json"
REPORT = ROOT / "reports/rce_p0_012_restoration_equivalence.json"
RECEIPT = ROOT / "receipts/rce_p0_012_authoritative_validation.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_012.json"


class EquivalenceError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EquivalenceError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity() -> dict[str, str]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-restoration-monitor"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def verify(root: Path = ROOT) -> dict[str, Any]:
    predecessor_path = root / PREDECESSOR.relative_to(ROOT)
    snapshot_path = root / SNAPSHOT.relative_to(ROOT)
    restoration_path = root / RESTORATION.relative_to(ROOT)
    report_path = root / REPORT.relative_to(ROOT)
    receipt_path = root / RECEIPT.relative_to(ROOT)
    task_path = root / TASK.relative_to(ROOT)

    predecessor = _load(predecessor_path)
    if predecessor.get("task_id") != "RCE-P0-011":
        raise EquivalenceError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise EquivalenceError("P0-011 is not authoritatively complete")
    if predecessor.get("decision") != "SEALED_SNAPSHOT_RESTORATION_VERIFIED":
        raise EquivalenceError("restoration was not verified")
    if predecessor.get("manual_actions_required") != []:
        raise EquivalenceError("predecessor still requires manual actions")
    if predecessor.get("restoration_manifest_sha256") != _sha(restoration_path):
        raise EquivalenceError("restoration manifest digest mismatch")

    snapshot = _load(snapshot_path)
    restoration = _load(restoration_path)
    if restoration.get("snapshot_root_sha256") != snapshot.get("snapshot_root_sha256"):
        raise EquivalenceError("snapshot root divergence")

    snapshot_entries = snapshot.get("entries")
    restored_entries = restoration.get("entries")
    if not isinstance(snapshot_entries, list) or not isinstance(restored_entries, list):
        raise EquivalenceError("evidence entries missing")
    if len(snapshot_entries) != len(restored_entries):
        raise EquivalenceError("restored evidence count divergence")

    expected = {entry["path"]: entry for entry in snapshot_entries if isinstance(entry, dict) and isinstance(entry.get("path"), str)}
    observed = {entry["source_path"]: entry for entry in restored_entries if isinstance(entry, dict) and isinstance(entry.get("source_path"), str)}
    if set(expected) != set(observed):
        raise EquivalenceError("restored evidence membership divergence")

    comparisons: list[dict[str, Any]] = []
    for relative in sorted(expected):
        source = root / relative
        restored = root / observed[relative]["restored_path"]
        exp = expected[relative]
        if not source.is_file() or not restored.is_file():
            raise EquivalenceError(f"evidence missing: {relative}")
        source_sha = _sha(source)
        restored_sha = _sha(restored)
        source_bytes = source.stat().st_size
        restored_bytes = restored.stat().st_size
        if source_sha != exp.get("sha256") or restored_sha != exp.get("sha256"):
            raise EquivalenceError(f"hash divergence: {relative}")
        if source_bytes != exp.get("bytes") or restored_bytes != exp.get("bytes"):
            raise EquivalenceError(f"byte-count divergence: {relative}")
        if source.read_bytes() != restored.read_bytes():
            raise EquivalenceError(f"byte divergence: {relative}")
        comparisons.append({
            "path": relative,
            "restored_path": observed[relative]["restored_path"],
            "sha256": source_sha,
            "bytes": source_bytes,
            "equivalent": True,
        })

    observed_at = datetime.now(timezone.utc).isoformat()
    report = {
        "schema": "stegverse.rce.restoration_equivalence.v1",
        "task_id": "RCE-P0-012",
        "decision": "RESTORATION_EQUIVALENCE_ATTESTED",
        "snapshot_root_sha256": snapshot["snapshot_root_sha256"],
        "entry_count": len(comparisons),
        "comparisons": comparisons,
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

    identity = _identity()
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-012-equivalence-{identity['run_id']}",
        "task_id": "RCE-P0-012",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_RESTORATION_EQUIVALENCE",
        "authoritative_completion_evidence": True,
        "decision": report["decision"],
        "report": str(report_path.relative_to(root)),
        "report_sha256": _sha(report_path),
        "snapshot_root_sha256": report["snapshot_root_sha256"],
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    _write(receipt_path, receipt)

    task = _load(task_path)
    task["activation_dependency"]["satisfied"] = True
    task["status"] = "COMPLETE"
    task["blocked_by"] = []
    task["completed_at"] = observed_at
    task["successor_task"] = "RCE-P0-013 automated divergence alert and quarantine evidence"
    task["validation"] = {
        "status": "PASS",
        "authoritative_completion_evidence": True,
        "authoritative_receipt": str(receipt_path.relative_to(root)),
        "decision": report["decision"],
        "manual_actions_required": [],
    }
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = verify()
    except (EquivalenceError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"decision": "DENY_RESTORATION_EQUIVALENCE", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "entry_count": result["entry_count"], "manual_actions_required": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
