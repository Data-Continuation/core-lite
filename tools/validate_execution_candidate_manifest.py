#!/usr/bin/env python3
"""Validate sandbox execution-candidate manifests with fail-closed invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "execution_candidate_manifest.schema.json"


class ManifestValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ManifestValidationError(f"{path} must contain a JSON object")
    return value


def _require(record: dict[str, Any], key: str) -> Any:
    if key not in record:
        raise ManifestValidationError(f"missing required field: {key}")
    return record[key]


def derive_decision(record: dict[str, Any]) -> str:
    action = _require(record, "action")
    live_state = _require(record, "live_state")
    authority = _require(record, "authority")
    effects = _require(record, "effects")
    denial = _require(record, "denial")
    trajectory = _require(record, "trajectory")
    recoverability = _require(record, "recoverability")
    traceability = _require(record, "traceability")

    if action.get("sandbox_only") is not True:
        return "DENY"
    if action.get("reversible") is not True or action.get("severe_human_harm_possible") is True:
        return "DENY"
    if live_state.get("sufficient") is not True:
        return "ABSTAIN"
    if live_state.get("age_seconds", 0) > live_state.get("max_age_seconds", -1):
        return "DENY"
    if authority.get("state") != "valid":
        return "ESCALATE" if authority.get("state") in {"missing", "conflicting"} else "DENY"
    if authority.get("rederived_at_commit") is not True:
        return "DENY"
    if not authority.get("source_refs"):
        return "DENY"
    predicted = set(effects.get("predicted_domains", []))
    authorized = set(effects.get("authorized_domains", []))
    if not predicted or not predicted.issubset(authorized):
        return "DENY"
    if effects.get("collateral_resolved") is not True:
        return "DENY"
    if denial.get("reachable") is not True or not denial.get("mechanisms"):
        return "DENY"
    if trajectory.get("governability_preserved") is not True:
        return "DENY"
    if recoverability.get("preserved") is not True or not recoverability.get("rollback_ref"):
        return "DENY"
    if traceability.get("record_required") is not True:
        return "DENY"
    if traceability.get("integrity_protected") is not True or not traceability.get("receipt_ref"):
        return "DENY"
    return "ALLOW"


def validate_record(record: dict[str, Any], schema: dict[str, Any] | None = None) -> str:
    if schema is not None:
        try:
            import jsonschema  # type: ignore
        except ImportError:
            jsonschema = None
        if jsonschema is not None:
            jsonschema.Draft202012Validator(schema).validate(record)

    required = {
        "schema_version",
        "candidate_id",
        "action",
        "live_state",
        "authority",
        "effects",
        "denial",
        "trajectory",
        "recoverability",
        "traceability",
        "declared_decision",
    }
    missing = sorted(required.difference(record))
    if missing:
        raise ManifestValidationError(f"missing required fields: {', '.join(missing)}")

    derived = derive_decision(record)
    declared = record["declared_decision"]
    if declared != derived:
        raise ManifestValidationError(f"declared decision {declared} does not match derived decision {derived}")
    return derived


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_execution_candidate_manifest.py <manifest.json>", file=sys.stderr)
        return 2
    schema = load_json(SCHEMA_PATH)
    record = load_json(Path(argv[1]))
    decision = validate_record(record, schema)
    print(f"EXECUTION_CANDIDATE_MANIFEST_VALID decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
