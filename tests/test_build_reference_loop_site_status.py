import json
from pathlib import Path

import pytest

from tools.build_reference_loop_site_status import SiteStatusError, status_for


def _state() -> dict:
    return {
        "schema_version": 1,
        "repository": "Data-Continuation/core-lite",
        "lease": None,
        "updated_at": "2026-07-15T02:28:00+00:00",
        "tasks": {
            "REF-LOOP-001": {"status": "complete"},
            "REF-LOOP-002": {"status": "complete"},
            "REF-LOOP-003": {"status": "complete"},
            "REF-LOOP-004": {"status": "complete"},
        },
    }


def _contract() -> dict:
    return {
        "decision": "RECEIPT_CONTRACT_VERIFIED",
        "chain_head": "a" * 64,
        "chain_sha256": "b" * 64,
        "authority": {"external_repository_mutation": False},
    }


def test_builds_read_only_site_status_contract() -> None:
    result = status_for(_state(), _contract())
    assert result["decision"] == "SITE_STATUS_CONTRACT_VERIFIED"
    assert result["completed_task_count"] == 4
    assert result["target_repository"] == "StegVerse-Labs/Site"
    assert result["authority"] == {
        "read_only_status": True,
        "publication_authorized": False,
        "site_control_authorized": False,
        "external_repository_mutation": False,
        "production_mutation": False,
    }


def test_is_deterministic() -> None:
    assert status_for(_state(), _contract()) == status_for(_state(), _contract())


def test_fails_closed_on_incomplete_task() -> None:
    state = _state()
    state["tasks"]["REF-LOOP-004"]["status"] = "ready"
    with pytest.raises(SiteStatusError, match="incomplete tasks"):
        status_for(state, _contract())


def test_fails_closed_on_unverified_receipt_contract() -> None:
    contract = _contract()
    contract["decision"] = "DENY_RECEIPT_CONTRACT"
    with pytest.raises(SiteStatusError, match="not verified"):
        status_for(_state(), contract)


def test_fails_closed_if_external_mutation_is_not_denied() -> None:
    contract = _contract()
    contract["authority"]["external_repository_mutation"] = True
    with pytest.raises(SiteStatusError, match="not read-only"):
        status_for(_state(), contract)
