from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MASTER_HASH_RECORDS_PATH = Path(".stegverse/master_hash_records.jsonl")
VALIDATION_REPORT_PATH = Path(".stegverse/master_hash_validation_report.json")
TRANSITION_TABLE_PATH = Path("schemas/ingestion_transition_table.json")
VALIDATION_RULES_PATH = Path("schemas/validation_rules.json")
HASH_IDENTITY_TYPES_PATH = Path("schemas/hash_identity_types.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def load_json(repo_root: Path, relative_path: Path) -> Dict[str, Any]:
    path = repo_root / relative_path
    if not path.exists():
        raise FileNotFoundError(f"required file not found: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")
    return payload


def latest_local_event_hash(repo_root: Path) -> Optional[str]:
    path = repo_root / MASTER_HASH_RECORDS_PATH
    if not path.exists():
        return None
    last = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            last = json.loads(line)
    return None if last is None else last.get("event_hash")


def transition_map(repo_root: Path) -> Dict[str, Dict[str, Any]]:
    table = load_json(repo_root, TRANSITION_TABLE_PATH)
    if table.get("schema") != "stegverse_ingestion_transition_table.v1":
        raise ValueError("unsupported ingestion transition table schema")
    return {
        item["transition_id"]: item
        for item in table.get("transition_classes", [])
        if isinstance(item, dict) and isinstance(item.get("transition_id"), str)
    }


def known_identity_types(repo_root: Path) -> set[str]:
    payload = load_json(repo_root, HASH_IDENTITY_TYPES_PATH)
    return {
        item["type"]
        for item in payload.get("identity_types", [])
        if isinstance(item, dict) and isinstance(item.get("type"), str)
    }


def validate_identity_hashes(repo_root: Path, identity_hashes: Dict[str, str]) -> List[str]:
    allowed = known_identity_types(repo_root)
    errors: List[str] = []
    for identity_type, value in identity_hashes.items():
        if identity_type not in allowed:
            errors.append(f"unknown hash identity type: {identity_type}")
        if not isinstance(value, str) or not value.startswith("sha256:"):
            errors.append(f"{identity_type} must be a sha256: hash")
    return errors


def validate_event(repo_root: Path, event: Dict[str, Any]) -> Dict[str, Any]:
    transitions = transition_map(repo_root)
    transition_id = str(event.get("transition_id", ""))
    transition = transitions.get(transition_id)

    errors: List[str] = []
    warnings: List[str] = []

    if transition is None:
        errors.append(f"unknown transition_id: {transition_id}")
    else:
        if event.get("outcome") not in transition.get("allowed_outcomes", []):
            errors.append(f"outcome {event.get('outcome')} not allowed for transition {transition_id}")

        if transition.get("parent_event_hash_required") is True and not event.get("parent_event_hash"):
            errors.append("parent_event_hash required for this transition")

        identity_hashes = event.get("identity_hashes", {})
        for field in transition.get("required_fields", []):
            if field in {"bundle_hash", "manifest_hash", "file_hash", "event_hash", "receipt_hash", "state_hash", "fingerprint_hash"}:
                if field not in identity_hashes:
                    errors.append(f"missing identity hash required by transition: {field}")
            elif field not in event and field not in identity_hashes:
                warnings.append(f"transition required field not present on event payload: {field}")

    identity_hashes = event.get("identity_hashes", {})
    if not isinstance(identity_hashes, dict):
        errors.append("identity_hashes must be an object")
    else:
        errors.extend(validate_identity_hashes(repo_root, identity_hashes))

    return {
        "schema": "stegverse_master_hash_event_validation.v1",
        "generated_at": utc_now(),
        "transition_id": transition_id,
        "success": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def make_event(
    repo_root: Path,
    transition_id: str,
    layer: str,
    source: str,
    outcome: str,
    identity_hashes: Dict[str, str],
    entrypoint_class: str = "",
    parent_event_hash: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    confirmation_status: str = "pending",
) -> Dict[str, Any]:
    rules = load_json(repo_root, VALIDATION_RULES_PATH)
    body = {
        "schema": "stegverse_master_hash_event.v1",
        "generated_at": utc_now(),
        "parent_event_hash": parent_event_hash,
        "previous_local_event_hash": latest_local_event_hash(repo_root),
        "transition_id": transition_id,
        "layer": layer,
        "source": source,
        "entrypoint_class": entrypoint_class,
        "outcome": outcome,
        "identity_hashes": identity_hashes,
        "validation_rule_version": str(rules.get("version", "unknown")),
        "confirmation_status": confirmation_status,
        "payload": payload or {},
    }
    event = {**body, "event_hash": stable_hash(body)}
    event["validation"] = validate_event(repo_root, event)
    return event


def append_event(repo_root: Path, event: Dict[str, Any]) -> Dict[str, Any]:
    event["validation"] = validate_event(repo_root, event)
    path = repo_root / MASTER_HASH_RECORDS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    (repo_root / VALIDATION_REPORT_PATH).write_text(json.dumps(event["validation"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return event["validation"]
