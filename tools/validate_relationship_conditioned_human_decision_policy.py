#!/usr/bin/env python3
"""Validate relationship-conditioned human-decision policy records.

Uses jsonschema when available and always applies StegVerse fail-closed
invariants that must not be weakened by schema-only validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "relationship_conditioned_human_decision_policy.schema.json"
EXAMPLE_PATH = ROOT / "samples" / "relationship_conditioned_human_decision_policy.example.json"

NON_EXECUTION_DECISIONS = {"PROTECTIVE_DELAY", "ESCALATE", "ABSTAIN", "FAIL_CLOSED"}
NONVALID_AUTHORITY_DECISIONS = {"ESCALATE", "ABSTAIN", "FAIL_CLOSED"}


class PolicyValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise PolicyValidationError(f"{path} must contain a JSON object")
    return value


def _require(record: dict[str, Any], key: str) -> Any:
    if key not in record:
        raise PolicyValidationError(f"missing required field: {key}")
    return record[key]


def validate_invariants(record: dict[str, Any]) -> None:
    relationship = _require(record, "relationship")
    authority = _require(record, "authority")
    impact = _require(record, "human_impact")
    uncertainty = _require(record, "uncertainty")
    temporal_identity = _require(record, "temporal_identity")
    decision = _require(record, "decision")
    requested_operation = _require(record, "requested_operation")

    role = relationship.get("role")
    if role not in {"advisor", "witness", "guardian", "delegate", "counterparty"}:
        raise PolicyValidationError("missing or invalid relationship role")

    if relationship.get("history_used_as_context_only") is not True:
        raise PolicyValidationError("relationship history must be context-only")

    if uncertainty.get("acknowledgment_is_not_authorization") is not True:
        raise PolicyValidationError("uncertainty acknowledgment cannot be authorization")

    if temporal_identity.get("present_consent_treated_as_non_final") is not True:
        raise PolicyValidationError("present consent must be treated as non-final")

    authority_state = authority.get("state")
    if authority_state != "valid" and decision not in NONVALID_AUTHORITY_DECISIONS:
        raise PolicyValidationError("non-valid authority must abstain, escalate, or fail closed")

    irreversible_severe = bool(impact.get("irreversible") and impact.get("severe_harm_possible"))
    self_sacrificial = bool(impact.get("self_sacrificial"))
    irreversible_execution = requested_operation == "execute_irreversible"

    if (irreversible_severe or self_sacrificial or irreversible_execution) and decision not in NON_EXECUTION_DECISIONS:
        raise PolicyValidationError("irreversible or self-sacrificial human impact cannot receive autonomous execution authorization")

    if role == "advisor" and decision == "EXECUTE_REVERSIBLE":
        raise PolicyValidationError("advisor role cannot execute")
    if role == "witness" and decision not in {"WITNESS_ONLY", "ESCALATE", "ABSTAIN", "FAIL_CLOSED"}:
        raise PolicyValidationError("witness role exceeded its authority")
    if role == "delegate" and decision == "EXECUTE_REVERSIBLE" and "execute_reversible" not in authority.get("scope", []):
        raise PolicyValidationError("delegate lacks explicit reversible execution scope")


def validate_record(record: dict[str, Any], schema: dict[str, Any] | None = None) -> None:
    if schema is not None:
        try:
            import jsonschema  # type: ignore
        except ImportError:
            jsonschema = None
        if jsonschema is not None:
            jsonschema.Draft202012Validator(schema).validate(record)

    required = {
        "policy_version", "decision_id", "relationship", "authority",
        "human_impact", "uncertainty", "temporal_identity",
        "alternatives_considered", "requested_operation", "decision",
        "reasons", "traceability"
    }
    missing = sorted(required.difference(record))
    if missing:
        raise PolicyValidationError(f"missing required fields: {', '.join(missing)}")

    validate_invariants(record)


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    record = load_json(EXAMPLE_PATH)
    validate_record(record, schema)
    print("RELATIONSHIP_CONDITIONED_POLICY_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
