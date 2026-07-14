#!/usr/bin/env python3
"""Build a deterministic local-only RCE continuity checkpoint candidate."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "receipts/rce_p0_013_authoritative_validation.json"
SNAPSHOT = ROOT / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
EQUIVALENCE = ROOT / "reports/rce_p0_012_restoration_equivalence.json"
CHECKPOINT = ROOT / "sandbox/publication_candidates/relationship_conditioned_execution/checkpoint.json"
REPORT = ROOT / "reports/rce_p0_014_checkpoint_candidate.json"
RECEIPT = ROOT / "receipts/rce_p0_014_authoritative_validation.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_014.json"


class CheckpointError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CheckpointError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _identity() -> dict[str, str]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-checkpoint-candidate"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    predecessor_path = root / PREDECESSOR.relative_to(ROOT)
    snapshot_path = root / SNAPSHOT.relative_to(ROOT)
    equivalence_path = root / EQUIVALENCE.relative_to(ROOT)
    checkpoint_path = root / CHECKPOINT.relative_to(ROOT)
    report_path = root / REPORT.relative_to(ROOT)
    receipt_path = root / RECEIPT.relative_to(ROOT)
    task_path = root / TASK.relative_to(ROOT)

    predecessor = _load(predecessor_path)
    if predecessor.get("task_id") != "RCE-P0-013":
        raise CheckpointError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise CheckpointError("P0-013 is not authoritatively complete")
    if predecessor.get("decision") != "DIVERGENCE_GUARD_ARMED":
        raise CheckpointError("divergence guard is not cleanly armed")
    if predecessor.get("manual_actions_required") != []:
        raise CheckpointError("predecessor still requires manual actions")

    snapshot = _load(snapshot_path)
    equivalence = _load(equivalence_path)
    if equivalence.get("decision") != "RESTORATION_EQUIVALENCE_ATTESTED":
        raise CheckpointError("restoration equivalence is not attested")
    if equivalence.get("snapshot_root_sha256") != snapshot.get("snapshot_root_sha256"):
        raise CheckpointError("snapshot root mismatch")

    receipt_entries: list[dict[str, Any]] = []
    for number in range(1, 14):
        path = root / f"receipts/rce_p0_{number:03d}_authoritative_validation.json"
        if not path.is_file():
            raise CheckpointError(f"authoritative receipt missing: {path.relative_to(root)}")
        value = _load(path)
        if value.get("authoritative_completion_evidence") is not True:
            raise CheckpointError(f"receipt is not authoritative: {path.relative_to(root)}")
        receipt_entries.append({
            "task_id": value.get("task_id"),
            "path": str(path.relative_to(root)),
            "sha256": _sha(path),
            "bytes": path.stat().st_size,
        })

    receipt_entries.sort(key=lambda item: item["path"])
    root_material = {
        "snapshot_root_sha256": snapshot.get("snapshot_root_sha256"),
        "equivalence_report_sha256": _sha(equivalence_path),
        "guard_receipt_sha256": _sha(predecessor_path),
        "receipts": receipt_entries,
    }
    checkpoint_root_sha256 = hashlib.sha256(_canonical(root_material)).hexdigest()
    observed_at = datetime.now(timezone.utc).isoformat()

    checkpoint = {
        "schema": "stegverse.rce.continuity_checkpoint_candidate.v1",
        "task_id": "RCE-P0-014",
        "decision": "CONTINUITY_CHECKPOINT_CANDIDATE_READY",
        "checkpoint_root_sha256": checkpoint_root_sha256,
        "snapshot_root_sha256": root_material["snapshot_root_sha256"],
        "equivalence_report": str(equivalence_path.relative_to(root)),
        "equivalence_report_sha256": root_material["equivalence_report_sha256"],
        "source_guard_receipt": str(predecessor_path.relative_to(root)),
        "source_guard_receipt_sha256": root_material["guard_receipt_sha256"],
        "receipt_count": len(receipt_entries),
        "receipts": receipt_entries,
        "local_candidate_only": True,
        "publication_performed": False,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "manual_actions_required": [],
    }
    _write(checkpoint_path, checkpoint)

    report = {
        **checkpoint,
        "checkpoint": str(checkpoint_path.relative_to(root)),
        "checkpoint_sha256": _sha(checkpoint_path),
        "observed_at": observed_at,
        "deterministic_for_unchanged_evidence": True,
    }
    _write(report_path, report)

    identity = _identity()
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-014-checkpoint-{identity['run_id']}",
        "task_id": "RCE-P0-014",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_CONTINUITY_CHECKPOINT_CANDIDATE",
        "authoritative_completion_evidence": True,
        "decision": checkpoint["decision"],
        "checkpoint_root_sha256": checkpoint_root_sha256,
        "checkpoint": str(checkpoint_path.relative_to(root)),
        "checkpoint_sha256": _sha(checkpoint_path),
        "publication_performed": False,
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
    task["successor_task"] = "RCE-P0-015 automated checkpoint verification and release-readiness boundary"
    task["validation"] = {
        "status": "PASS",
        "authoritative_completion_evidence": True,
        "authoritative_receipt": str(receipt_path.relative_to(root)),
        "decision": checkpoint["decision"],
        "checkpoint_root_sha256": checkpoint_root_sha256,
        "manual_actions_required": [],
    }
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = build()
    except (CheckpointError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "DENY_CONTINUITY_CHECKPOINT_CANDIDATE", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "checkpoint_root_sha256": result["checkpoint_root_sha256"], "manual_actions_required": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
