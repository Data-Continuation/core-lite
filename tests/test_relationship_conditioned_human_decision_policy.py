import copy
import json
from pathlib import Path

import pytest

from tools.validate_relationship_conditioned_human_decision_policy import (
    PolicyValidationError,
    validate_record,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "schemas" / "relationship_conditioned_human_decision_policy.schema.json").read_text(encoding="utf-8")
)
EXAMPLE = json.loads(
    (ROOT / "samples" / "relationship_conditioned_human_decision_policy.example.json").read_text(encoding="utf-8")
)


def test_canonical_example_validates():
    validate_record(copy.deepcopy(EXAMPLE), SCHEMA)


def test_missing_relationship_role_fails_closed_validation():
    record = copy.deepcopy(EXAMPLE)
    del record["relationship"]["role"]
    with pytest.raises(PolicyValidationError, match="relationship role"):
        validate_record(record, None)


def test_history_cannot_create_authority():
    record = copy.deepcopy(EXAMPLE)
    record["authority"]["state"] = "missing"
    record["authority"]["source"] = None
    record["decision"] = "ADVISE"
    with pytest.raises(PolicyValidationError, match="non-valid authority"):
        validate_record(record, None)


def test_uncertainty_acknowledgment_is_not_authorization():
    record = copy.deepcopy(EXAMPLE)
    record["decision"] = "EXECUTE_REVERSIBLE"
    with pytest.raises(PolicyValidationError, match="cannot receive autonomous execution authorization"):
        validate_record(record, None)


def test_irreversible_human_impact_never_returns_autonomous_allow():
    record = copy.deepcopy(EXAMPLE)
    record["decision"] = "EXECUTE_REVERSIBLE"
    with pytest.raises(PolicyValidationError):
        validate_record(record, None)


@pytest.mark.parametrize(
    ("role", "decision"),
    [
        ("advisor", "ADVISE"),
        ("witness", "WITNESS_ONLY"),
        ("guardian", "PROTECTIVE_DELAY"),
        ("delegate", "EXECUTE_REVERSIBLE"),
        ("counterparty", "NEGOTIATE"),
    ],
)
def test_roles_have_distinct_bounded_outputs(role, decision):
    record = copy.deepcopy(EXAMPLE)
    record["relationship"]["role"] = role
    record["human_impact"] = {
        "class": "reversible",
        "irreversible": False,
        "self_sacrificial": False,
        "severe_harm_possible": False,
    }
    record["requested_operation"] = "execute_reversible" if role == "delegate" else "advice"
    record["decision"] = decision
    if role == "delegate":
        record["authority"]["scope"].append("execute_reversible")
    validate_record(record, None)


@pytest.mark.parametrize("authority_state", ["missing", "expired", "revoked", "conflicting", "out_of_scope"])
def test_unknown_or_conflicting_authority_requires_safe_outcome(authority_state):
    record = copy.deepcopy(EXAMPLE)
    record["authority"]["state"] = authority_state
    record["decision"] = "FAIL_CLOSED"
    validate_record(record, None)


def test_present_consent_is_not_final():
    record = copy.deepcopy(EXAMPLE)
    record["temporal_identity"]["present_consent_treated_as_non_final"] = False
    with pytest.raises(PolicyValidationError, match="present consent"):
        validate_record(record, None)
