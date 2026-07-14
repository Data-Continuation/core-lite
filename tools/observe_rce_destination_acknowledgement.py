#!/usr/bin/env python3
"""Observe a destination-owned RCE acknowledgement without fabricating receipt or acceptance."""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "rce_destination_acknowledgement_watch.json"
NOTIFICATION = ROOT / "notifications" / "relationship_conditioned_execution" / "candidate_available.json"
ENVELOPE = ROOT / "exports" / "relationship_conditioned_execution" / "candidate_envelope.json"
REPORT = ROOT / "reports" / "rce_p0_008_destination_acknowledgement.json"


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


def _fetch_json(url: str, timeout: int = 15) -> tuple[str, dict[str, Any] | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "StegVerse-RCE-P0-008/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return "ABSENT", None
        raise ObservationError(f"destination acknowledgement HTTP error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        return "UNREACHABLE", None

    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ObservationError("destination acknowledgement is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ObservationError("destination acknowledgement must be a JSON object")
    return "OBSERVED", value


def _validate_local_inputs(notification: dict[str, Any], envelope: dict[str, Any]) -> None:
    if notification.get("notification_state") != "CANDIDATE_AVAILABLE_FOR_DESTINATION_EVALUATION":
        raise ObservationError("candidate availability notification is not active")
    if notification.get("destination_receipt_observed") is not False:
        raise ObservationError("source notification improperly claims destination receipt")
    if envelope.get("candidate_evidence_only") is not True:
        raise ObservationError("candidate envelope is not candidate evidence only")
    if envelope.get("may_bind_destination_repo_state") is not False:
        raise ObservationError("candidate envelope claims destination-binding authority")
    if envelope.get("destination_mutation_performed") is not False:
        raise ObservationError("candidate envelope indicates destination mutation")


def _validate_acknowledgement(
    acknowledgement: dict[str, Any],
    config: dict[str, Any],
    notification_sha256: str,
    envelope_sha256: str,
) -> None:
    if acknowledgement.get("schema") != config["required_acknowledgement_schema"]:
        raise ObservationError("destination acknowledgement schema mismatch")
    if acknowledgement.get("source_repo") != config["source_repo"]:
        raise ObservationError("destination acknowledgement source repository mismatch")
    if acknowledgement.get("destination_repo") != config["destination_repo"]:
        raise ObservationError("destination acknowledgement destination repository mismatch")
    if acknowledgement.get("candidate_state") != config["required_candidate_state"]:
        raise ObservationError("destination acknowledgement candidate state mismatch")
    if acknowledgement.get("candidate_notification_sha256") != notification_sha256:
        raise ObservationError("destination acknowledgement notification digest mismatch")
    if acknowledgement.get("candidate_envelope_sha256") != envelope_sha256:
        raise ObservationError("destination acknowledgement envelope digest mismatch")
    if acknowledgement.get("destination_acceptance") is not False:
        raise ObservationError("acknowledgement must not claim destination acceptance")
    if acknowledgement.get("production_installation_authority") is not False:
        raise ObservationError("acknowledgement must not grant production installation authority")
    if acknowledgement.get("autonomous_execution_authority") is not False:
        raise ObservationError("acknowledgement must not grant autonomous execution authority")


def observe(fetcher=_fetch_json) -> dict[str, Any]:
    config = _load(CONFIG)
    notification = _load(NOTIFICATION)
    envelope = _load(ENVELOPE)
    _validate_local_inputs(notification, envelope)

    notification_sha256 = _sha256(NOTIFICATION)
    envelope_sha256 = _sha256(ENVELOPE)
    fetch_state, acknowledgement = fetcher(str(config["acknowledgement_url"]))

    state = config["absence_state"]
    acknowledgement_valid = False
    if fetch_state == "OBSERVED":
        if acknowledgement is None:
            raise ObservationError("observed acknowledgement payload missing")
        _validate_acknowledgement(acknowledgement, config, notification_sha256, envelope_sha256)
        state = "DESTINATION_ACKNOWLEDGEMENT_OBSERVED"
        acknowledgement_valid = True
    elif fetch_state not in {"ABSENT", "UNREACHABLE"}:
        raise ObservationError(f"unknown fetch state: {fetch_state}")

    result = {
        "schema": "stegverse.rce.destination_acknowledgement_observation.v1",
        "task_id": "RCE-P0-008",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": config["source_repo"],
        "destination_repo": config["destination_repo"],
        "acknowledgement_url": config["acknowledgement_url"],
        "fetch_state": fetch_state,
        "observation_state": state,
        "acknowledgement_valid": acknowledgement_valid,
        "candidate_notification": config["candidate_notification"],
        "candidate_notification_sha256": notification_sha256,
        "candidate_envelope": config["candidate_envelope"],
        "candidate_envelope_sha256": envelope_sha256,
        "destination_receipt_observed": acknowledgement_valid,
        "destination_acceptance_claimed": False,
        "destination_mutation_performed": False,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "manual_actions_required": [],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    print(json.dumps(observe(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
