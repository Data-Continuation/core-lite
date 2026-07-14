#!/usr/bin/env python3
"""Seal a deterministic sandbox-only snapshot of verified RCE evidence."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "reports/rce_p0_009_reconstruction_index.json"
P0_009_RECEIPT = ROOT / "receipts/rce_p0_009_authoritative_validation.json"
SNAPSHOT_PATH = ROOT / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
REPORT_PATH = ROOT / "reports/rce_p0_010_snapshot_seal.json"
RECEIPT_PATH = ROOT / "receipts/rce_p0_010_authoritative_validation.json"
TASK_PATH = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_010.json"


class SnapshotSealError(ValueError):
    """Raised when snapshot sealing must fail closed."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SnapshotSealError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _identity() -> dict[str, Any]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-snapshot-seal"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def seal(root: Path = ROOT) -> dict[str, Any]:
    index_path = root / "reports/rce_p0_009_reconstruction_index.json"
    predecessor_path = root / "receipts/rce_p0_009_authoritative_validation.json"
    snapshot_path = root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
    report_path = root / "reports/rce_p0_010_snapshot_seal.json"
    receipt_path = root / "receipts/rce_p0_010_authoritative_validation.json"
    task_path = root / "core_lite/tasks/relationship_conditioned_execution_p0_010.json"

    predecessor = _load(predecessor_path)
    if predecessor.get("task_id") != "RCE-P0-009":
        raise SnapshotSealError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise SnapshotSealError("P0-009 is not authoritatively complete")
    if predecessor.get("decision") != "RECONSTRUCTION_INDEX_VERIFIED":
        raise SnapshotSealError("reconstruction index was not verified")
    if predecessor.get("manual_actions_required") != []:
        raise SnapshotSealError("predecessor still requires manual actions")

    index = _load(index_path)
    entries = index.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SnapshotSealError("reconstruction index entries missing")

    bound_entries: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SnapshotSealError("invalid reconstruction index entry")
        relative = entry.get("path")
        expected_sha = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        evidence_class = entry.get("evidence_class")
        if not isinstance(relative, str) or not relative:
            raise SnapshotSealError("indexed path missing")
        path = root / relative
        if not path.is_file():
            raise SnapshotSealError(f"indexed evidence missing: {relative}")
        actual_sha = _sha(path)
        actual_bytes = path.stat().st_size
        if actual_sha != expected_sha or actual_bytes != expected_bytes:
            raise SnapshotSealError(f"indexed evidence changed: {relative}")
        bound_entries.append({
            "path": relative,
            "evidence_class": evidence_class,
            "sha256": actual_sha,
            "bytes": actual_bytes,
        })

    bound_entries.sort(key=lambda item: item["path"])
    root_material = {
        "index_sha256": _sha(index_path),
        "predecessor_receipt_sha256": _sha(predecessor_path),
        "entries": bound_entries,
    }
    snapshot_root_sha256 = _sha_bytes(_canonical(root_material))
    observed_at = datetime.now(timezone.utc).isoformat()

    snapshot = {
        "schema": "stegverse.rce.snapshot_manifest.v1",
        "task_id": "RCE-P0-010",
        "decision": "SANDBOX_EVIDENCE_SNAPSHOT_SEALED",
        "snapshot_root_sha256": snapshot_root_sha256,
        "reconstruction_index": str(index_path.relative_to(root)),
        "reconstruction_index_sha256": root_material["index_sha256"],
        "source_receipt": str(predecessor_path.relative_to(root)),
        "source_receipt_sha256": root_material["predecessor_receipt_sha256"],
        "entry_count": len(bound_entries),
        "entries": bound_entries,
        "sandbox_only": True,
        "candidate_evidence_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "manual_actions_required": [],
    }
    _write(snapshot_path, snapshot)

    report = {
        **snapshot,
        "snapshot_manifest": str(snapshot_path.relative_to(root)),
        "snapshot_manifest_sha256": _sha(snapshot_path),
        "observed_at": observed_at,
        "deterministic_for_unchanged_evidence": True,
    }
    _write(report_path, report)

    identity = _identity()
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-010-snapshot-{identity['run_id']}",
        "task_id": "RCE-P0-010",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_SNAPSHOT_SEAL",
        "authoritative_completion_evidence": True,
        "decision": snapshot["decision"],
        "snapshot_root_sha256": snapshot_root_sha256,
        "snapshot_manifest": str(snapshot_path.relative_to(root)),
        "snapshot_manifest_sha256": _sha(snapshot_path),
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
    task["successor_task"] = "RCE-P0-011 automated snapshot verification and publication candidate"
    task["validation"] = {
        "status": "PASS",
        "authoritative_completion_evidence": True,
        "authoritative_receipt": str(receipt_path.relative_to(root)),
        "decision": snapshot["decision"],
        "snapshot_root_sha256": snapshot_root_sha256,
        "manual_actions_required": [],
    }
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = seal()
    except (SnapshotSealError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "DENY_SNAPSHOT_SEAL", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "snapshot_root_sha256": result["snapshot_root_sha256"], "manual_actions_required": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
