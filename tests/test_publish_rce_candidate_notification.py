import json
from pathlib import Path

import pytest

import tools.publish_rce_candidate_notification as publisher


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def configure(tmp_path, monkeypatch, *, authoritative=True, bind=False, mutated=False):
    envelope = tmp_path / "exports/envelope.json"
    receipt = tmp_path / "receipts/p006.json"
    notification = tmp_path / "notifications/candidate.json"
    write_json(receipt, {
        "task_id": "RCE-P0-006",
        "authoritative_completion_evidence": authoritative,
    })
    write_json(envelope, {
        "candidate_evidence_only": True,
        "may_bind_destination_repo_state": bind,
        "destination_mutation_performed": mutated,
        "intended_destination": {
            "repository": "StegVerse-002/core-lite",
            "incoming_path": "incoming/data_continuation_core_lite/",
            "policy": "config/management_package_intake_policy.json",
        },
    })
    monkeypatch.setattr(publisher, "ROOT", tmp_path)
    monkeypatch.setattr(publisher, "ENVELOPE", envelope)
    monkeypatch.setattr(publisher, "P0_006_RECEIPT", receipt)
    monkeypatch.setattr(publisher, "NOTIFICATION", notification)
    return notification


def test_publishes_notification_without_destination_claims(tmp_path, monkeypatch):
    notification = configure(tmp_path, monkeypatch)
    result = publisher.publish_notification()
    assert result["notification_state"] == "CANDIDATE_AVAILABLE_FOR_DESTINATION_EVALUATION"
    assert result["destination_receipt_observed"] is False
    assert result["destination_acceptance_claimed"] is False
    assert result["destination_mutation_performed"] is False
    assert result["manual_actions_required"] == []
    assert notification.is_file()


def test_missing_authoritative_receipt_fails_closed(tmp_path, monkeypatch):
    configure(tmp_path, monkeypatch, authoritative=False)
    with pytest.raises(publisher.NotificationError, match="authoritative"):
        publisher.publish_notification()


def test_destination_binding_claim_fails_closed(tmp_path, monkeypatch):
    configure(tmp_path, monkeypatch, bind=True)
    with pytest.raises(publisher.NotificationError, match="binding"):
        publisher.publish_notification()


def test_destination_mutation_claim_fails_closed(tmp_path, monkeypatch):
    configure(tmp_path, monkeypatch, mutated=True)
    with pytest.raises(publisher.NotificationError, match="mutation"):
        publisher.publish_notification()
