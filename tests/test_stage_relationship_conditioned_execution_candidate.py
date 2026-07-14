import copy
import json
from pathlib import Path

import pytest

import tools.stage_relationship_conditioned_execution_candidate as staging

ROOT = Path(__file__).resolve().parents[1]


def test_safe_relative_rejects_escape():
    with pytest.raises(staging.StagingError, match="unsafe relative path"):
        staging._safe_relative("../escape.json")


def test_authoritative_receipt_required():
    with pytest.raises(staging.StagingError, match="authoritative evidence missing"):
        staging._require_authoritative(
            {"task_id": "RCE-P0-004", "authoritative_completion_evidence": False},
            "RCE-P0-004",
        )


def test_staging_fails_when_p0_004_receipt_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(staging, "P0_004_RECEIPT", tmp_path / "missing.json")
    with pytest.raises(staging.StagingError, match="missing required file"):
        staging.stage_candidate()


def test_staging_fails_closed_on_denied_reconstruction(monkeypatch, tmp_path):
    p003 = tmp_path / "p003.json"
    p004 = tmp_path / "p004.json"
    report = tmp_path / "report.json"
    p003.write_text(json.dumps({
        "task_id": "RCE-P0-003",
        "authoritative_completion_evidence": True,
    }), encoding="utf-8")
    p004.write_text(json.dumps({
        "task_id": "RCE-P0-004",
        "authoritative_completion_evidence": True,
    }), encoding="utf-8")
    report.write_text(json.dumps({
        "decision": "DENY_CANDIDATE_INTAKE",
        "destination_mutation_performed": False,
    }), encoding="utf-8")
    monkeypatch.setattr(staging, "P0_003_RECEIPT", p003)
    monkeypatch.setattr(staging, "P0_004_RECEIPT", p004)
    monkeypatch.setattr(staging, "P0_004_REPORT", report)
    with pytest.raises(staging.StagingError, match="did not allow"):
        staging.stage_candidate()


def test_install_plan_remains_sandbox_only():
    plan = json.loads(
        (ROOT / "bundles/relationship_conditioned_execution/install_plan.json").read_text(encoding="utf-8")
    )
    assert plan["mode"] == "sandbox_only"
    assert plan["destination_root"] == "sandbox/relationship_conditioned_execution"
    assert plan["automatic_destination_mutation"] is False
    assert plan["autonomous_execution_authority"] is False


def test_inventory_targets_remain_under_declared_sandbox_root():
    inventory = json.loads(
        (ROOT / "bundles/relationship_conditioned_execution/source_inventory.json").read_text(encoding="utf-8")
    )
    for entry in inventory["files"]:
        target = Path(entry["target_path"])
        assert target.parts[:2] == ("sandbox", "relationship_conditioned_execution")
        assert ".." not in target.parts
