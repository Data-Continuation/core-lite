from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

MASTER_HASH_RECORDS_PATH = Path(".stegverse/master_hash_records.jsonl")
SOURCE_STATE_INDEX_PATH = Path(".stegverse/source_state_index.json")
TERMINAL_BLOCKING_OUTCOMES = {"FAIL_CLOSED", "QUARANTINE", "HASH_MISMATCH", "FORK_DETECTED", "AUTHORITY_ESCALATION_REJECTED", "STALE_PENDING", "REVOKE", "INVALIDATE"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_events(repo_root: Path) -> List[Dict[str, Any]]:
    path = repo_root / MASTER_HASH_RECORDS_PATH
    if not path.exists(): return []
    events: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            payload = json.loads(line)
            if isinstance(payload, dict): events.append(payload)
    return events

def event_is_validated(event: Dict[str, Any]) -> bool:
    validation = event.get("validation", {})
    return bool(validation.get("success")) and event.get("outcome") not in TERMINAL_BLOCKING_OUTCOMES

def source_scope(event: Dict[str, Any]) -> str:
    payload = event.get("payload", {})
    if isinstance(payload, dict) and payload.get("scope"): return str(payload["scope"])
    identity_hashes = event.get("identity_hashes", {})
    if isinstance(identity_hashes, dict):
        for name in ["bundle_hash", "manifest_hash", "state_hash", "fingerprint_hash"]:
            if identity_hashes.get(name): return f"{name}:{identity_hashes[name]}"
    return str(event.get("transition_id", "global"))

def validate_local_chain(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    missing_links: List[Dict[str, Any]] = []
    previous_hash: Optional[str] = None
    for index, event in enumerate(events):
        actual = event.get("previous_local_event_hash")
        if index == 0:
            if actual not in {None, ""}: missing_links.append({"index": index, "event_hash": event.get("event_hash"), "reason": "first event should not require previous_local_event_hash", "actual": actual})
        elif actual != previous_hash:
            missing_links.append({"index": index, "event_hash": event.get("event_hash"), "reason": "previous_local_event_hash mismatch", "expected": previous_hash, "actual": actual})
        previous_hash = event.get("event_hash")
    return {"valid": not missing_links, "event_count": len(events), "missing_links": missing_links}

def validate_parent_links(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    hashes = {e.get("event_hash") for e in events if e.get("event_hash")}
    missing = [{"event_hash": e.get("event_hash"), "parent_event_hash": e.get("parent_event_hash"), "status": "not_found_locally"} for e in events if e.get("parent_event_hash") and e.get("parent_event_hash") not in hashes]
    return {"valid_locally": not missing, "missing_parent_count": len(missing), "missing_parents": missing}

def build_latest_validated_sources(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    latest: Dict[str, Any] = {}
    for index, event in enumerate(events):
        scope = source_scope(event)
        status = {"event_hash": event.get("event_hash"), "transition_id": event.get("transition_id"), "outcome": event.get("outcome"), "source": event.get("source"), "layer": event.get("layer"), "generated_at": event.get("generated_at"), "index": index, "validated": event_is_validated(event), "confirmation_status": event.get("confirmation_status")}
        if event_is_validated(event): latest[scope] = status
        elif event.get("outcome") in TERMINAL_BLOCKING_OUTCOMES: latest[scope] = {**status, "blocking": True}
    return latest

def can_allow_for_scope(index: Dict[str, Any], scope: str) -> Dict[str, Any]:
    latest = index.get("latest_validated_sources", {}).get(scope)
    local_chain = index.get("chain_status", {}).get("local_chain", {})
    parent_chain = index.get("chain_status", {}).get("parent_links", {})
    if latest is None: return {"scope": scope, "allow": False, "reason": "no validated source for scope"}
    if latest.get("blocking"): return {"scope": scope, "allow": False, "reason": f"latest source is blocking outcome {latest.get('outcome')}", "latest": latest}
    if not local_chain.get("valid"): return {"scope": scope, "allow": False, "reason": "local chain invalid", "latest": latest}
    if not parent_chain.get("valid_locally"): return {"scope": scope, "allow": False, "reason": "parent chain has unresolved local parents", "latest": latest}
    return {"scope": scope, "allow": True, "reason": "latest source is validated and chains are locally coherent", "latest": latest}

def generate_source_state_index(repo_root: Path, repository: str = "unknown/unknown") -> Dict[str, Any]:
    events = load_events(repo_root)
    latest = build_latest_validated_sources(events)
    index = {"schema": "stegverse_source_state_index.v1", "generated_at": utc_now(), "repository": repository, "event_count": len(events), "latest_validated_sources": latest, "chain_status": {"local_chain": validate_local_chain(events), "parent_links": validate_parent_links(events)}, "allow_status": {}}
    for scope in sorted(latest): index["allow_status"][scope] = can_allow_for_scope(index, scope)
    output = repo_root / SOURCE_STATE_INDEX_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return index
