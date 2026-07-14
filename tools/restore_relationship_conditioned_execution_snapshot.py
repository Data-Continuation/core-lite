#!/usr/bin/env python3
"""Restore a sealed RCE evidence snapshot into an isolated sandbox drill."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
PREDECESSOR = ROOT / "receipts/rce_p0_010_authoritative_validation.json"
DRILL_ROOT = ROOT / "sandbox/restoration_drills/relationship_conditioned_execution"
REPORT = ROOT / "reports/rce_p0_011_restoration_drill.json"
RECEIPT = ROOT / "receipts/rce_p0_011_authoritative_validation.json"
TASK = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_011.json"


class RestorationError(ValueError):
    """Raised when restoration must fail closed."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RestorationError(f"{path} must contain a JSON object")
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


def _identity() -> dict[str, str]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-restoration-drill"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def restore(root: Path = ROOT) -> dict[str, Any]:
    snapshot_path = root / SNAPSHOT.relative_to(ROOT)
    predecessor_path = root / PREDECESSOR.relative_to(ROOT)
    drill_root = root / DRILL_ROOT.relative_to(ROOT)
    report_path = root / REPORT.relative_to(ROOT)
    receipt_path = root / RECEIPT.relative_to(ROOT)
    task_path = root / TASK.relative_to(ROOT)

    predecessor = _load(predecessor_path)
    if predecessor.get("task_id") != "RCE-P0-010":
        raise RestorationError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise RestorationError("P0-010 is not authoritatively complete")
    if predecessor.get("decision") != "SANDBOX_EVIDENCE_SNAPSHOT_SEALED":
        raise RestorationError("snapshot was not authoritatively sealed")
    if predecessor.get("manual_actions_required") != []:
        raise RestorationError("predecessor still requires manual actions")
    if predecessor.get("snapshot_manifest_sha256") != _sha(snapshot_path):
        raise RestorationError("snapshot manifest digest mismatch")

    snapshot = _load(snapshot_path)
    entries = snapshot.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RestorationError("snapshot entries missing")

    root_material = {
        "index_sha256": snapshot.get("reconstruction_index_sha256"),
        "predecessor_receipt_sha256": snapshot.get("source_receipt_sha256"),
        "entries": entries,
    }
    if _sha_bytes(_canonical(root_material)) != snapshot.get("snapshot_root_sha256"):
        raise RestorationError("snapshot root mismatch")

    allowed_root = (root / "sandbox/restoration_drills").resolve()
    if not drill_root.resolve().is_relative_to(allowed_root):
        raise RestorationError("restoration destination escaped sandbox drill root")
    if drill_root.exists():
        shutil.rmtree(drill_root)
    drill_root.mkdir(parents=True, exist_ok=True)

    restored: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise RestorationError("invalid snapshot entry")
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative:
            raise RestorationError("snapshot entry path missing")
        source = (root / relative).resolve()
        if not source.is_relative_to(root.resolve()) or not source.is_file():
            raise RestorationError(f"invalid source evidence path: {relative}")
        target = (drill_root / relative).resolve()
        if not target.is_relative_to(drill_root.resolve()):
            raise RestorationError(f"restoration path escaped drill root: {relative}")
        if _sha(source) != entry.get("sha256") or source.stat().st_size != entry.get("bytes"):
            raise RestorationError(f"source evidence changed: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if _sha(target) != entry.get("sha256") or target.stat().st_size != entry.get("bytes"):
            raise RestorationError(f"restored evidence mismatch: {relative}")
        restored.append({
            "source_path": relative,
            "restored_path": str(target.relative_to(root)),
            "evidence_class": entry.get("evidence_class"),
            "sha256": entry.get("sha256"),
            "bytes": entry.get("bytes"),
        })

    observed_at = datetime.now(timezone.utc).isoformat()
    restoration_manifest = {
        "schema": "stegverse.rce.restoration_drill.v1",
        "task_id": "RCE-P0-011",
        "decision": "SEALED_SNAPSHOT_RESTORATION_VERIFIED",
        "snapshot_root_sha256": snapshot["snapshot_root_sha256"],
        "snapshot_manifest": str(snapshot_path.relative_to(root)),
        "snapshot_manifest_sha256": _sha(snapshot_path),
        "restored_entry_count": len(restored),
        "entries": restored,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "source_evidence_modified": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "manual_actions_required": [],
    }
    restoration_manifest_path = drill_root / "restoration_manifest.json"
    _write(restoration_manifest_path, restoration_manifest)

    report = {
        **restoration_manifest,
        "restoration_manifest": str(restoration_manifest_path.relative_to(root)),
        "restoration_manifest_sha256": _sha(restoration_manifest_path),
        "observed_at": observed_at,
    }
    _write(report_path, report)

    identity = _identity()
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-011-restoration-{identity['run_id']}",
        "task_id": "RCE-P0-011",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_SNAPSHOT_RESTORATION_DRILL",
        "authoritative_completion_evidence": True,
        "decision": restoration_manifest["decision"],
        "snapshot_root_sha256": snapshot["snapshot_root_sha256"],
        "restoration_manifest": str(restoration_manifest_path.relative_to(root)),
        "restoration_manifest_sha256": _sha(restoration_manifest_path),
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
    task["successor_task"] = "RCE-P0-012 automated restoration divergence monitoring"
    task["validation"] = {
        "status": "PASS",
        "authoritative_completion_evidence": True,
        "authoritative_receipt": str(receipt_path.relative_to(root)),
        "decision": restoration_manifest["decision"],
        "manual_actions_required": [],
    }
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = restore()
    except (RestorationError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "DENY_SNAPSHOT_RESTORATION", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "restored_entry_count": result["restored_entry_count"], "manual_actions_required": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
