#!/usr/bin/env python3
"""Stage validated RCE candidate evidence into a repository-local sandbox area."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "bundles" / "relationship_conditioned_execution"
STAGING_DIR = ROOT / "staging" / "relationship_conditioned_execution"
P0_003_RECEIPT = ROOT / "receipts" / "rce_p0_003_authoritative_validation.json"
P0_004_RECEIPT = ROOT / "receipts" / "rce_p0_004_authoritative_validation.json"
P0_004_REPORT = ROOT / "reports" / "rce_p0_004_reconstruction.json"


class StagingError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise StagingError(f"missing required file: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StagingError(f"JSON object required: {path.relative_to(ROOT)}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_relative(value: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise StagingError(f"unsafe relative path: {value}")
    return path


def _require_authoritative(receipt: dict[str, Any], task_id: str) -> None:
    if receipt.get("task_id") != task_id:
        raise StagingError(f"receipt task mismatch for {task_id}")
    if receipt.get("authoritative_completion_evidence") is not True:
        raise StagingError(f"authoritative evidence missing for {task_id}")


def stage_candidate() -> dict[str, Any]:
    p003 = _load(P0_003_RECEIPT)
    p004 = _load(P0_004_RECEIPT)
    reconstruction = _load(P0_004_REPORT)
    _require_authoritative(p003, "RCE-P0-003")
    _require_authoritative(p004, "RCE-P0-004")
    if reconstruction.get("decision") != "ALLOW_CANDIDATE_INTAKE":
        raise StagingError("P0-004 did not allow candidate intake")
    if reconstruction.get("destination_mutation_performed") is not False:
        raise StagingError("reconstruction report indicates destination mutation")

    manifest = _load(BUNDLE_DIR / "bundle_manifest.json")
    inventory = _load(BUNDLE_DIR / "source_inventory.json")
    install_plan = _load(BUNDLE_DIR / "install_plan.json")
    if manifest.get("candidate_evidence_only") is not True:
        raise StagingError("bundle is not candidate evidence only")
    if manifest.get("autonomous_execution_authority") is not False:
        raise StagingError("bundle claims execution authority")
    if install_plan.get("mode") != "sandbox_only":
        raise StagingError("install plan mode is not sandbox-only")
    destination_root = str(install_plan.get("destination_root", ""))
    if destination_root != "sandbox/relationship_conditioned_execution":
        raise StagingError("unexpected sandbox destination root")
    if install_plan.get("automatic_destination_mutation") is not False:
        raise StagingError("install plan permits automatic destination mutation")

    entries = inventory.get("files")
    if not isinstance(entries, list) or not entries:
        raise StagingError("source inventory files required")

    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    payload_dir = STAGING_DIR / "payload"
    payload_dir.mkdir(parents=True)
    staged: list[dict[str, Any]] = []

    for entry in entries:
        if not isinstance(entry, dict):
            raise StagingError("invalid inventory entry")
        source_rel = _safe_relative(str(entry.get("source_path", "")))
        target_rel = _safe_relative(str(entry.get("target_path", "")))
        if target_rel.parts[:2] != ("sandbox", "relationship_conditioned_execution"):
            raise StagingError(f"target outside declared sandbox root: {target_rel}")
        source = ROOT / source_rel
        if not source.is_file():
            raise StagingError(f"missing source: {source_rel}")
        expected_hash = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        actual_hash = _sha256(source)
        actual_bytes = source.stat().st_size
        if actual_hash != expected_hash or actual_bytes != expected_bytes:
            raise StagingError(f"integrity mismatch: {source_rel}")
        target = payload_dir / target_rel
        resolved = target.resolve()
        if STAGING_DIR.resolve() not in resolved.parents:
            raise StagingError(f"target escapes staging: {target_rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if _sha256(target) != actual_hash or target.stat().st_size != actual_bytes:
            raise StagingError(f"staged copy mismatch: {target_rel}")
        staged.append({
            "source_path": source_rel.as_posix(),
            "staged_path": target.relative_to(ROOT).as_posix(),
            "sha256": actual_hash,
            "bytes": actual_bytes,
        })

    result = {
        "schema": "stegverse.rce.staging.v1",
        "task_id": "RCE-P0-005",
        "decision": "STAGED_CANDIDATE_EVIDENCE",
        "origin": "Data-Continuation/core-lite",
        "destination": "repository-local:staging/relationship_conditioned_execution",
        "destination_class": "repository_local_sandbox",
        "source_package": "bundles/relationship_conditioned_execution",
        "source_package_manifest_sha256": _sha256(BUNDLE_DIR / "bundle_manifest.json"),
        "reconstruction_report": "reports/rce_p0_004_reconstruction.json",
        "reconstruction_report_sha256": _sha256(P0_004_REPORT),
        "receipt_chain": [
            "receipts/rce_p0_003_authoritative_validation.json",
            "receipts/rce_p0_004_authoritative_validation.json",
        ],
        "candidate_evidence_only": True,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "external_destination_mutation_performed": False,
        "staged_files": staged,
        "manual_actions_required": [],
    }
    (STAGING_DIR / "staging_manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    result = stage_candidate()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
