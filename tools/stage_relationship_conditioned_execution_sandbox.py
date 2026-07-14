#!/usr/bin/env python3
"""Stage the validated RCE candidate into a non-production sandbox path.

This tool performs no external destination mutation. It requires a successful
RCE-P0-004 authoritative receipt, verifies the committed bundle files, copies
only candidate evidence into sandbox/intake, and emits a deterministic staging
manifest.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FILES = ("bundle_manifest.json", "install_plan.json", "source_inventory.json")


class StagingError(ValueError):
    """Raised when sandbox staging cannot be admitted safely."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StagingError(f"{path} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_safe_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("task_id") != "RCE-P0-004":
        raise StagingError("unexpected predecessor receipt task")
    if receipt.get("authoritative_completion_evidence") is not True:
        raise StagingError("RCE-P0-004 is not authoritatively complete")
    if receipt.get("decision") != "ALLOW_CANDIDATE_INTAKE":
        raise StagingError("candidate intake was not allowed")
    if receipt.get("destination_mutation_performed") is not False:
        raise StagingError("predecessor performed destination mutation")
    if receipt.get("manual_actions_required") != []:
        raise StagingError("predecessor still requires manual actions")


def _require_safe_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "stegverse.rce.bundle_manifest.v1":
        raise StagingError("unexpected bundle manifest schema")
    if manifest.get("sandbox_only") is not True:
        raise StagingError("bundle is not sandbox only")
    if manifest.get("candidate_evidence_only") is not True:
        raise StagingError("bundle is not candidate evidence only")
    if manifest.get("autonomous_execution_authority") is not False:
        raise StagingError("bundle grants autonomous execution authority")
    if manifest.get("human_harm_authority") is not False:
        raise StagingError("bundle grants human-harm authority")
    if manifest.get("production_destination_allowed") is not False:
        raise StagingError("bundle permits a production destination")
    if manifest.get("receipts_required") is not True:
        raise StagingError("bundle does not require receipts")


def stage(root: Path = ROOT, stage_root: Path | None = None) -> dict[str, Any]:
    bundle_root = root / "bundles" / "relationship_conditioned_execution"
    receipt_path = root / "receipts" / "rce_p0_004_authoritative_validation.json"
    destination = stage_root or (root / "sandbox" / "intake" / "relationship_conditioned_execution")
    sandbox_root = (root / "sandbox" / "intake").resolve()

    if not destination.resolve().is_relative_to(sandbox_root):
        raise StagingError("staging destination escaped sandbox intake")

    receipt = _load_json(receipt_path)
    _require_safe_receipt(receipt)

    manifest = _load_json(bundle_root / "bundle_manifest.json")
    _require_safe_manifest(manifest)

    source_entries: list[dict[str, Any]] = []
    for filename in PACKAGE_FILES:
        source = bundle_root / filename
        if not source.is_file():
            raise StagingError(f"missing package file: {filename}")
        source_entries.append(
            {
                "source_path": str(source.relative_to(root)),
                "target_path": str((destination / filename).relative_to(root)),
                "sha256": _sha256(source),
                "bytes": source.stat().st_size,
            }
        )

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    for filename in PACKAGE_FILES:
        shutil.copyfile(bundle_root / filename, destination / filename)

    staging_manifest = {
        "schema": "stegverse.rce.sandbox_staging.v1",
        "task_id": "RCE-P0-005",
        "source_task": "RCE-P0-004",
        "source_receipt": str(receipt_path.relative_to(root)),
        "source_receipt_sha256": _sha256(receipt_path),
        "source_package_id": manifest.get("package_id"),
        "source_package_version": manifest.get("package_version"),
        "decision": "STAGED_CANDIDATE_EVIDENCE",
        "sandbox_only": True,
        "candidate_evidence_only": True,
        "production_destination_allowed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
        "external_destination_mutation_performed": False,
        "manual_actions_required": [],
        "files": source_entries,
    }
    output = destination / "staging_manifest.json"
    output.write_text(json.dumps(staging_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for entry in source_entries:
        copied = root / entry["target_path"]
        if _sha256(copied) != entry["sha256"] or copied.stat().st_size != entry["bytes"]:
            raise StagingError(f"staged file mismatch: {entry['target_path']}")

    return staging_manifest


def main() -> int:
    result = stage()
    print(result["decision"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
