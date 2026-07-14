#!/usr/bin/env python3
"""Build a destination-neutral RCE candidate intake envelope."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STAGING_MANIFEST = ROOT / "staging" / "relationship_conditioned_execution" / "staging_manifest.json"
P0_005_RECEIPT = ROOT / "receipts" / "rce_p0_005_authoritative_validation.json"
EXPORT_DIR = ROOT / "exports" / "relationship_conditioned_execution"
EXPORT_PATH = EXPORT_DIR / "candidate_envelope.json"


class EnvelopeError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise EnvelopeError(f"missing required file: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EnvelopeError(f"JSON object required: {path.relative_to(ROOT)}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_envelope() -> dict[str, Any]:
    receipt = _load(P0_005_RECEIPT)
    if receipt.get("task_id") != "RCE-P0-005":
        raise EnvelopeError("P0-005 receipt task mismatch")
    if receipt.get("authoritative_completion_evidence") is not True:
        raise EnvelopeError("P0-005 authoritative evidence missing")

    staging = _load(STAGING_MANIFEST)
    if staging.get("decision") != "STAGED_CANDIDATE_EVIDENCE":
        raise EnvelopeError("staging manifest is not admissible candidate evidence")
    if staging.get("candidate_evidence_only") is not True:
        raise EnvelopeError("staging manifest expanded authority")
    if staging.get("production_installation_authority") is not False:
        raise EnvelopeError("staging manifest claims production authority")
    if staging.get("autonomous_execution_authority") is not False:
        raise EnvelopeError("staging manifest claims execution authority")
    if staging.get("external_destination_mutation_performed") is not False:
        raise EnvelopeError("external destination mutation detected")

    staged_files = staging.get("staged_files")
    if not isinstance(staged_files, list) or not staged_files:
        raise EnvelopeError("staged files required")

    verified: list[dict[str, Any]] = []
    for entry in staged_files:
        path_value = entry.get("staged_path")
        if not isinstance(path_value, str):
            raise EnvelopeError("staged_path required")
        path = Path(path_value)
        if path.is_absolute() or ".." in path.parts:
            raise EnvelopeError("unsafe staged path")
        full = ROOT / path
        if not full.is_file():
            raise EnvelopeError(f"missing staged file: {path_value}")
        actual_hash = _sha256(full)
        actual_bytes = full.stat().st_size
        if actual_hash != entry.get("sha256") or actual_bytes != entry.get("bytes"):
            raise EnvelopeError(f"staged integrity mismatch: {path_value}")
        verified.append({"path": path.as_posix(), "sha256": actual_hash, "bytes": actual_bytes})

    envelope = {
        "schema": "stegverse.rce.candidate_intake_envelope.v1",
        "task_id": "RCE-P0-006",
        "source_repo": "Data-Continuation/core-lite",
        "intended_destination_repo": "StegVerse-002/core-lite",
        "destination_intake_policy": "StegVerse-002/core-lite::config/management_package_intake_policy.json",
        "destination_incoming_path": "StegVerse-002/core-lite::incoming/data_continuation_core_lite/",
        "candidate_evidence_only": True,
        "canonical_authority": False,
        "may_bind_destination_repo_state": False,
        "destination_mutation_performed": False,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "staging_manifest": STAGING_MANIFEST.relative_to(ROOT).as_posix(),
        "staging_manifest_sha256": _sha256(STAGING_MANIFEST),
        "receipt_chain": [
            "receipts/rce_p0_003_authoritative_validation.json",
            "receipts/rce_p0_004_authoritative_validation.json",
            "receipts/rce_p0_005_authoritative_validation.json"
        ],
        "files": verified,
        "requested_destination_result": "MANAGEMENT_PACKAGE_CANDIDATE_EVIDENCE_ACCEPTED",
        "manual_actions_required": []
    }
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return envelope


def main() -> int:
    print(json.dumps(build_envelope(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
