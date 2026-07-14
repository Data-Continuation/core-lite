import copy
import json
from pathlib import Path

import pytest

from tools.validate_execution_candidate_manifest import (
    ManifestValidationError,
    derive_decision,
    validate_record,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "execution_candidate_manifest.schema.json").read_text(encoding="utf-8"))
ALLOW = json.loads((ROOT / "samples" / "execution_candidate_manifest.allow.example.json").read_text(encoding="utf-8"))
STALE = json.loads((ROOT / "samples" / "execution_candidate_manifest.stale_state.example.json").read_text(encoding="utf-8"))
SCOPE = json.loads((ROOT / "samples" / "execution_candidate_manifest.scope_leakage.example.json").read_text(encoding="utf-8"))


def test_canonical_allow_fixture_validates():
    assert validate_record(copy.deepcopy(ALLOW), SCHEMA) == "ALLOW"


def test_stale_state_denies():
    assert validate_record(copy.deepcopy(STALE), SCHEMA) == "DENY"


def test_scope_leakage_denies():
    assert validate_record(copy.deepcopy(SCOPE), SCHEMA) == "DENY"


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        (("authority", "rederived_at_commit"), False, "DENY"),
        (("denial", "reachable"), False, "DENY"),
        (("trajectory", "governability_preserved"), False, "DENY"),
        (("recoverability", "preserved"), False, "DENY"),
        (("traceability", "integrity_protected"), False, "DENY"),
        (("effects", "collateral_resolved"), False, "DENY"),
        (("action", "reversible"), False, "DENY"),
        (("action", "severe_human_harm_possible"), True, "DENY"),
    ],
)
def test_fail_closed_invariants(path, value, expected):
    record = copy.deepcopy(ALLOW)
    record[path[0]][path[1]] = value
    assert derive_decision(record) == expected


def test_insufficient_state_abstains():
    record = copy.deepcopy(ALLOW)
    record["live_state"]["sufficient"] = False
    record["declared_decision"] = "ABSTAIN"
    assert validate_record(record, None) == "ABSTAIN"


def test_missing_authority_escalates():
    record = copy.deepcopy(ALLOW)
    record["authority"]["state"] = "missing"
    record["declared_decision"] = "ESCALATE"
    assert validate_record(record, None) == "ESCALATE"


def test_declared_decision_must_match_derived_decision():
    record = copy.deepcopy(STALE)
    record["declared_decision"] = "ALLOW"
    with pytest.raises(ManifestValidationError, match="does not match"):
        validate_record(record, None)


def test_allow_requires_integrity_receipt():
    record = copy.deepcopy(ALLOW)
    record["traceability"]["receipt_ref"] = None
    record["declared_decision"] = "DENY"
    assert validate_record(record, None) == "DENY"
