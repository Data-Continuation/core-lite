#!/usr/bin/env python3
"""Observe destination-owned RCE intake decisions without creating destination authority."""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "rce_destination_intake_decision_watch.json"


class ObservationError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ObservationError(f"missing required file: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ObservationError(f"JSON object required: {path.relative_to(ROOT)}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fetch_json(url: str) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        raise ObservationError("destination decision must be a JSON object")
    return value


def observe() -> dict[str, Any]:
    config = _load(CONFIG)
    receipt_path = ROOT / config["source_acknowledgement_receipt"]
    report_path = ROOT / config["source_acknowledgement_report"]
    notification_path = ROOT / config["source_notification"]
    envelope_path = ROOT / config["source_envelope"]

    receipt = _load(receipt_path)
    acknowledgement = _load(report_path)
    if receipt.get("task_id") != "RCE-P0-008" or receipt.get("authoritative_completion_evidence") is not True:
        raise ObservationError("P0-008 authoritative evidence is not complete")
    if acknowledgement.get("state") != "DESTINATION_ACKNOWLEDGEMENT_OBSERVED":
        raise ObservationError("destination acknowledgement has not been observed")

    notification_sha = _sha256(notification_path)
    envelope_sha = _sha256(envelope_path)
    acknowledgement_sha = _sha256(report_path)
    decision = _fetch_json(str(config["decision_url"]))

    base = {
        "schema": "stegverse.rce.intake_decision_observation.v1",
        "task_id": "RCE-P0-009",
        "source_repo": config["source_repo"],
        "destination_repo": config["destination_repo"],
        "notification_sha256": notification_sha,
        "candidate_envelope_sha256": envelope_sha,
        "destination_acknowledgement_sha256": acknowledgement_sha,
        "destination_mutation_performed": False,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "manual_actions_required": [],
    }

    if decision is None:
        return {
            **base,
            "state": "PENDING_DESTINATION_INTAKE_DECISION",
            "destination_decision_observed": False,
            "destination_acceptance_observed": False,
            "destination_rejection_observed": False,
        }

    if decision.get("schema") != config["required_decision_schema"]:
        raise ObservationError("destination decision schema mismatch")
    if decision.get("source_repo") != config["source_repo"] or decision.get("destination_repo") != config["destination_repo"]:
        raise ObservationError("destination decision repository identity mismatch")
    state = decision.get("state")
    if state not in config["allowed_states"]:
        raise ObservationError("unsupported destination decision state")
    if decision.get("notification_sha256") != notification_sha:
        raise ObservationError("destination decision notification digest mismatch")
    if decision.get("candidate_envelope_sha256") != envelope_sha:
        raise ObservationError("destination decision envelope digest mismatch")
    if decision.get("destination_acknowledgement_sha256") != acknowledgement_sha:
        raise ObservationError("destination decision acknowledgement digest mismatch")
    if decision.get("production_installation_authority") is not False:
        raise ObservationError("decision claims production installation authority")
    if decision.get("autonomous_execution_authority") is not False:
        raise ObservationError("decision claims autonomous execution authority")

    return {
        **base,
        "state": state,
        "destination_decision_observed": True,
        "destination_acceptance_observed": state == "CANDIDATE_ACCEPTED_FOR_SANDBOX_INTAKE",
        "destination_rejection_observed": state == "CANDIDATE_REJECTED",
        "evaluation_only": state == "CANDIDATE_UNDER_EVALUATION",
        "destination_decision": decision,
    }


def main() -> int:
    print(json.dumps(observe(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
