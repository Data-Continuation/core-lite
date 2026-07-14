#!/usr/bin/env python3
"""Manage the sandbox-only lifecycle of the RCE candidate package.

The manager is idempotent, denies downgrade and same-version content drift,
and archives superseded sandbox evidence only after authoritative custody
verification. It never targets production or an external destination.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STAGE_ROOT = ROOT / "sandbox/intake/relationship_conditioned_execution"
STATE_PATH = STAGE_ROOT / "lifecycle_state.json"
ARCHIVE_ROOT = ROOT / "sandbox/archive/relationship_conditioned_execution"
P0_006_RECEIPT = ROOT / "receipts/rce_p0_006_authoritative_validation.json"
REPORT_PATH = ROOT / "reports/rce_p0_007_lifecycle.json"
RECEIPT_PATH = ROOT / "receipts/rce_p0_007_authoritative_validation.json"
TASK_PATH = ROOT / "core_lite/tasks/relationship_conditioned_execution_p0_007.json"
MANIFEST_PATH = STAGE_ROOT / "bundle_manifest.json"
STAGING_MANIFEST_PATH = STAGE_ROOT / "staging_manifest.json"


class LifecycleError(ValueError):
    """Raised when lifecycle reconciliation must fail closed."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LifecycleError(f"{path} must contain a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_version(value: str) -> tuple[int, ...]:
    core = value.split("-", 1)[0]
    try:
        return tuple(int(part) for part in core.split("."))
    except ValueError as exc:
        raise LifecycleError(f"invalid semantic version: {value}") from exc


def _identity() -> dict[str, Any]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "Data-Continuation/core-lite"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-lifecycle"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
    }


def reconcile(root: Path = ROOT) -> dict[str, Any]:
    stage_root = root / "sandbox/intake/relationship_conditioned_execution"
    state_path = stage_root / "lifecycle_state.json"
    archive_root = root / "sandbox/archive/relationship_conditioned_execution"
    receipt6_path = root / "receipts/rce_p0_006_authoritative_validation.json"
    report_path = root / "reports/rce_p0_007_lifecycle.json"
    receipt7_path = root / "receipts/rce_p0_007_authoritative_validation.json"
    task_path = root / "core_lite/tasks/relationship_conditioned_execution_p0_007.json"

    predecessor = _load(receipt6_path)
    if predecessor.get("task_id") != "RCE-P0-006":
        raise LifecycleError("unexpected predecessor receipt")
    if predecessor.get("authoritative_completion_evidence") is not True:
        raise LifecycleError("P0-006 is not authoritatively complete")
    if predecessor.get("decision") != "CUSTODY_AND_REPLAY_VERIFIED":
        raise LifecycleError("custody and replay were not verified")
    if predecessor.get("manual_actions_required") != []:
        raise LifecycleError("predecessor still requires manual actions")

    manifest_path = stage_root / "bundle_manifest.json"
    staging_manifest_path = stage_root / "staging_manifest.json"
    manifest = _load(manifest_path)
    staging = _load(staging_manifest_path)

    if manifest.get("sandbox_only") is not True:
        raise LifecycleError("candidate is not sandbox only")
    if manifest.get("production_destination_allowed") is not False:
        raise LifecycleError("candidate permits production destination")
    if manifest.get("autonomous_execution_authority") is not False:
        raise LifecycleError("candidate grants autonomous execution authority")
    if manifest.get("human_harm_authority") is not False:
        raise LifecycleError("candidate grants human-harm authority")
    if staging.get("external_destination_mutation_performed") is not False:
        raise LifecycleError("staging performed external destination mutation")

    package_id = str(manifest.get("package_id", ""))
    version = str(manifest.get("package_version", ""))
    if not package_id or not version:
        raise LifecycleError("package identity or version missing")

    content = {
        "bundle_manifest_sha256": _sha(manifest_path),
        "install_plan_sha256": _sha(stage_root / "install_plan.json"),
        "source_inventory_sha256": _sha(stage_root / "source_inventory.json"),
        "staging_manifest_sha256": _sha(staging_manifest_path),
    }
    observed_at = datetime.now(timezone.utc).isoformat()
    decision = "ACTIVATE_INITIAL_SANDBOX_CANDIDATE"
    archive_path: str | None = None

    if state_path.exists():
        prior = _load(state_path)
        prior_id = str(prior.get("package_id", ""))
        prior_version = str(prior.get("active_version", ""))
        prior_content = prior.get("content_sha256")
        if prior_id != package_id:
            raise LifecycleError("package identity changed")
        if _parse_version(version) < _parse_version(prior_version):
            raise LifecycleError("version downgrade denied")
        if version == prior_version:
            if prior_content != content:
                raise LifecycleError("same-version content drift denied")
            decision = "NO_CHANGE_ACTIVE_CANDIDATE"
        else:
            archive_dir = archive_root / prior_version
            if archive_dir.exists():
                shutil.rmtree(archive_dir)
            archive_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(stage_root, archive_dir, ignore=shutil.ignore_patterns("lifecycle_state.json"))
            archive_path = str(archive_dir.relative_to(root))
            decision = "SUPERSEDE_SANDBOX_CANDIDATE"

    lifecycle_state = {
        "schema": "stegverse.rce.sandbox_lifecycle.v1",
        "task_id": "RCE-P0-007",
        "package_id": package_id,
        "active_version": version,
        "content_sha256": content,
        "decision": decision,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "source_receipt": str(receipt6_path.relative_to(root)),
        "source_receipt_sha256": _sha(receipt6_path),
        "archive_path": archive_path,
        "manual_actions_required": [],
        "observed_at": observed_at,
    }
    _write(state_path, lifecycle_state)

    report = {
        **lifecycle_state,
        "authoritative_custody_verified": True,
        "same_version_idempotent": decision == "NO_CHANGE_ACTIVE_CANDIDATE",
        "supersession_performed": decision == "SUPERSEDE_SANDBOX_CANDIDATE",
    }
    _write(report_path, report)

    identity = _identity()
    receipt = {
        "schema": "stegverse.validation.receipt.v1",
        "receipt_id": f"rce-p0-007-lifecycle-{identity['run_id']}",
        "task_id": "RCE-P0-007",
        **identity,
        "observed_at": observed_at,
        "validation_class": "CORE_LITE_MANAGEMENT_WORKFLOW_SANDBOX_LIFECYCLE",
        "authoritative_completion_evidence": True,
        "decision": decision,
        "lifecycle_state": str(state_path.relative_to(root)),
        "lifecycle_state_sha256": _sha(state_path),
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
    }
    _write(receipt7_path, receipt)

    task = _load(task_path)
    task["status"] = "COMPLETE"
    task["blocked_by"] = []
    task["completed_at"] = observed_at
    task["successor_task"] = "RCE-P0-008 sandbox expiry and renewal automation"
    task["validation"] = {
        "status": "PASS",
        "authoritative_completion_evidence": True,
        "authoritative_receipt": str(receipt7_path.relative_to(root)),
        "decision": decision,
        "manual_actions_required": [],
    }
    _write(task_path, task)
    return report


def main() -> int:
    try:
        result = reconcile()
    except (LifecycleError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "DENY_LIFECYCLE_TRANSITION", "error": str(exc), "manual_actions_required": []}, sort_keys=True))
        return 1
    print(json.dumps({"decision": result["decision"], "manual_actions_required": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
