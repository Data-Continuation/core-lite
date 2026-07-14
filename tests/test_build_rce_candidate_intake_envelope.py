import copy
import json
from pathlib import Path

import pytest

import tools.build_rce_candidate_intake_envelope as envelope


def test_missing_p0_005_receipt_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(envelope, "P0_005_RECEIPT", tmp_path / "missing.json")
    with pytest.raises(envelope.EnvelopeError, match="missing required file"):
        envelope.build_envelope()


def test_non_authoritative_receipt_fails(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"task_id": "RCE-P0-005", "authoritative_completion_evidence": False}))
    monkeypatch.setattr(envelope, "P0_005_RECEIPT", receipt)
    with pytest.raises(envelope.EnvelopeError, match="authoritative evidence missing"):
        envelope.build_envelope()


def test_destination_mutation_fails(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"task_id": "RCE-P0-005", "authoritative_completion_evidence": True}))
    staging = tmp_path / "staging.json"
    staging.write_text(json.dumps({
        "decision": "STAGED_CANDIDATE_EVIDENCE",
        "candidate_evidence_only": True,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "external_destination_mutation_performed": True,
        "staged_files": [{"staged_path": "x", "sha256": "x", "bytes": 1}]
    }))
    monkeypatch.setattr(envelope, "P0_005_RECEIPT", receipt)
    monkeypatch.setattr(envelope, "STAGING_MANIFEST", staging)
    with pytest.raises(envelope.EnvelopeError, match="external destination mutation"):
        envelope.build_envelope()


def test_path_escape_fails(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"task_id": "RCE-P0-005", "authoritative_completion_evidence": True}))
    staging = tmp_path / "staging.json"
    staging.write_text(json.dumps({
        "decision": "STAGED_CANDIDATE_EVIDENCE",
        "candidate_evidence_only": True,
        "production_installation_authority": False,
        "autonomous_execution_authority": False,
        "external_destination_mutation_performed": False,
        "staged_files": [{"staged_path": "../escape", "sha256": "x", "bytes": 1}]
    }))
    monkeypatch.setattr(envelope, "P0_005_RECEIPT", receipt)
    monkeypatch.setattr(envelope, "STAGING_MANIFEST", staging)
    with pytest.raises(envelope.EnvelopeError, match="unsafe staged path"):
        envelope.build_envelope()
