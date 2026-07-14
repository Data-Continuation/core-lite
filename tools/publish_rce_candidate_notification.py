#!/usr/bin/env python3
"""Publish a repository-visible RCE candidate availability notification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENVELOPE = ROOT / "exports" / "relationship_conditioned_execution" / "candidate_envelope.json"
P0_006_RECEIPT = ROOT / "receipts" / "rce_p0_006_authoritative_validation.json"
NOTIFICATION = ROOT / "notifications" / "relationship_conditioned_execution" / "candidate_available.json"


class NotificationError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise NotificationError(f"missing required file: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise NotificationError(f"JSON object required: {path.relative_to(ROOT)}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish_notification() -> dict[str, Any]:
    receipt = _load(P0_006_RECEIPT)
    envelope = _load(ENVELOPE)

    if receipt.get("task_id") != "RCE-P0-006":
        raise NotificationError("P0-006 receipt task mismatch")
    if receipt.get("authoritative_completion_evidence") is not True:
        raise NotificationError("P0-006 authoritative evidence missing")
    if envelope.get("candidate_evidence_only") is not True:
        raise NotificationError("envelope is not candidate evidence only")
    if envelope.get("may_bind_destination_repo_state") is not False:
        raise NotificationError("envelope claims destination binding authority")
    if envelope.get("destination_mutation_performed") is not False:
        raise NotificationError("envelope indicates destination mutation")

    destination = envelope.get("intended_destination")
    if not isinstance(destination, dict):
        raise NotificationError("intended destination contract missing")

    result = {
        "schema": "stegverse.rce.candidate_notification.v1",
        "task_id": "RCE-P0-007",
        "notification_state": "CANDIDATE_AVAILABLE_FOR_DESTINATION_EVALUATION",
        "source_repo": "Data-Continuation/core-lite",
        "candidate_envelope": "exports/relationship_conditioned_execution/candidate_envelope.json",
        "candidate_envelope_sha256": _sha256(ENVELOPE),
        "source_receipt": "receipts/rce_p0_006_authoritative_validation.json",
        "intended_destination": destination,
        "candidate_evidence_only": True,
        "destination_receipt_observed": False,
        "destination_acceptance_claimed": False,
        "destination_mutation_performed": False,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "manual_actions_required": [],
    }
    NOTIFICATION.parent.mkdir(parents=True, exist_ok=True)
    NOTIFICATION.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    print(json.dumps(publish_notification(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
