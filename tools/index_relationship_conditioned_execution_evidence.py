#!/usr/bin/env python3
"""Build a deterministic reconstruction index for authoritative RCE evidence."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rce_p0_009_reconstruction_index.json"
RECEIPT = ROOT / "receipts/rce_p0_009_authoritative_validation.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_009.json"
P0_008 = ROOT / "receipts/rce_p0_008_authoritative_validation.json"


class EvidenceIndexError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceIndexError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _classify(relative: str) -> str:
    if relative.startswith("receipts/"):
        return "authoritative_receipt"
    if relative.startswith("reports/"):
        return "verification_report"
    if relative.startswith("sandbox/archive/"):
        return "sandbox_archive"
    if relative.startswith("sandbox/intake/"):
        return "active_sandbox_evidence"
    if relative.startswith("bundles/"):
        return "source_package"
    return "supporting_evidence"


def _candidate_paths(root: Path) -> list[Path]:
    paths: set[Path] = set()
    for task_no in range(1, 9):
        path = root / f"receipts/rce_p0_{task_no:03d}_authoritative_validation.json"
        if path.is_file():
            paths.add(path)
    # Only bind report evidence that already exists before P0-009. Downstream
    # P0-010+ reports are products of the same reconciliation cycle and must
    # never become source inputs on a retry, or the snapshot becomes
    # self-referential and non-idempotent.
    for task_no in range(1, 9):
        paths.update(
            path
            for path in root.glob(f"reports/rce_p0_{task_no:03d}_*.json")
            if path.is_file()
        )
    for pattern in (
        "bundles/relationship_conditioned_execution/*.json",
        "sandbox/intake/relationship_conditioned_execution/*.json",
        "sandbox/archive/relationship_conditioned_execution/**/*.json",
    ):
        paths.update(path for path in root.glob(pattern) if path.is_file())

    # Generated index outputs must never become inputs to a later index pass.
    # Use the supplied root rather than module-global production paths so
    # temporary repositories and alternate roots remain deterministic.
    paths.discard(root / "reports/rce_p0_009_reconstruction_index.json")
    paths.discard(root / "receipts/rce_p0_009_authoritative_validation.json")
    return sorted(paths, key=lambda p: str(p.relative_to(root)))


def build_index(root: Path = ROOT) -> dict[str, Any]:
    predecessor_path = root / "receipts/rce_p0_008_authoritative_validation.json"
    predecessor = _load(predecessor_path)
    if predecessor.get("task_id") != "RCE-P0-008":
        raise EvidenceIndexError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise EvidenceIndexError("P0-008 is not authoritatively complete")
    if predecessor.get("manual_actions_required") != []:
        raise EvidenceIndexError("predecessor still requires manual actions")

    entries = []
    for path in _candidate_paths(root):
        relative = str(path.relative_to(root))
        entries.append({
            "path": relative,
            "evidence_class": _classify(relative),
            "sha256": _sha(path),
            "bytes": path.stat().st_size,
        })

    required_receipts = [f"receipts/rce_p0_{n:03d}_authoritative_validation.json" for n in range(1, 9)]
    observed = {entry["path"] for entry in entries}
    missing = [path for path in required_receipts if path not in observed]
    if missing:
        raise EvidenceIndexError(f"missing authoritative receipts: {missing}")

    canonical_entries = sorted(entries, key=lambda item: item["path"])
    index_digest = hashlib.sha256(
        (json.dumps(canonical_entries, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    observed_at = datetime.now(timezone.utc).isoformat()
    report = {
        "schema": "stegverse.rce.reconstruction_index.v1",
        "task_id": "RCE-P0-009",
        "decision": "RECONSTRUCTION_INDEX_VERIFIED",
        "entry_count": len(canonical_entries),
        "entries": canonical_entries,
        "index_sha256": index_digest,
        "evidence_deleted": False,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "manual_actions_required": [],
    }
    _write(root / "reports/rce_p0_009_reconstruction_index.json", report)

    identity = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-index"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-009-index-{identity['run_id']}",
        "task_id": "RCE-P0-009",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_RECONSTRUCTION_INDEX",
        "authoritative_completion_evidence": True,
        "decision": report["decision"],
        "report": "reports/rce_p0_009_reconstruction_index.json",
        "report_sha256": _sha(root / "reports/rce_p0_009_reconstruction_index.json"),
        "evidence_deleted": False,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    _write(root / "receipts/rce_p0_009_authoritative_validation.json", receipt)

    task_path = root / "core_lite/tasks/relationship_conditioned_execution_p0_009.json"
    task = _load(task_path)
    task["activation_dependency"]["satisfied"] = True
    task["status"] = "COMPLETE"
    task["blocked_by"] = []
    task["completed_at"] = observed_at
    task["successor_task"] = "RCE-P0-010 automated reconstruction challenge testing"
    task["validation"] = {
        "status": "PASS",
        "authoritative_completion_evidence": True,
        "authoritative_receipt": "receipts/rce_p0_009_authoritative_validation.json",
        "decision": report["decision"],
        "manual_actions_required": [],
    }
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = build_index()
    except (EvidenceIndexError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "DENY_RECONSTRUCTION_INDEX", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "entry_count": result["entry_count"], "manual_actions_required": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
