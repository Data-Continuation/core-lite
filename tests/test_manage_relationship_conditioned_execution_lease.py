import json
from pathlib import Path

import pytest

from tools.manage_relationship_conditioned_execution_lease import LeaseError, reconcile


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    stage = root / "sandbox/intake/relationship_conditioned_execution"
    _write(stage / "lifecycle_state.json", {
        "package_id": "relationship-conditioned-execution",
        "active_version": "1.0.0-sandbox-candidate",
        "content_sha256": {"manifest": "abc"},
        "sandbox_only": True,
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
    })
    _write(root / "receipts/rce_p0_007_authoritative_validation.json", {
        "task_id": "RCE-P0-007",
        "authoritative_completion_evidence": True,
        "manual_actions_required": [],
    })
    _write(root / "core_lite/tasks/relationship_conditioned_execution_p0_008.json", {
        "activation_dependency": {"satisfied": False},
        "blocked_by": [],
    })
    return root


def test_issues_initial_lease(monkeypatch, tmp_path):
    root = _root(tmp_path)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T08:00:00+00:00")
    result = reconcile(root)
    assert result["decision"] == "ISSUE_SANDBOX_LEASE"
    assert result["manual_actions_required"] == []
    assert result["production_destination_allowed"] is False


def test_renews_unchanged_unexpired_lease(monkeypatch, tmp_path):
    root = _root(tmp_path)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T08:00:00+00:00")
    reconcile(root)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T09:00:00+00:00")
    result = reconcile(root)
    assert result["decision"] == "RENEW_SANDBOX_LEASE"


def test_quarantines_expired_candidate(monkeypatch, tmp_path):
    root = _root(tmp_path)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T08:00:00+00:00")
    reconcile(root)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-16T09:00:00+00:00")
    result = reconcile(root)
    assert result["decision"] == "QUARANTINE_SANDBOX_CANDIDATE"
    assert (root / "sandbox/quarantine/relationship_conditioned_execution").exists()


def test_quarantines_content_drift(monkeypatch, tmp_path):
    root = _root(tmp_path)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T08:00:00+00:00")
    reconcile(root)
    path = root / "sandbox/intake/relationship_conditioned_execution/lifecycle_state.json"
    lifecycle = json.loads(path.read_text())
    lifecycle["content_sha256"] = {"manifest": "changed"}
    _write(path, lifecycle)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T09:00:00+00:00")
    result = reconcile(root)
    assert result["decision"] == "QUARANTINE_SANDBOX_CANDIDATE"


def test_denies_missing_predecessor_authority(monkeypatch, tmp_path):
    root = _root(tmp_path)
    path = root / "receipts/rce_p0_007_authoritative_validation.json"
    receipt = json.loads(path.read_text())
    receipt["authoritative_completion_evidence"] = False
    _write(path, receipt)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T08:00:00+00:00")
    with pytest.raises(LeaseError, match="not authoritatively complete"):
        reconcile(root)


@pytest.mark.parametrize(
    ("field", "unsafe"),
    [
        ("sandbox_only", False),
        ("production_destination_allowed", True),
        ("external_destination_mutation_performed", True),
        ("autonomous_execution_authority", True),
        ("human_harm_authority", True),
    ],
)
def test_denies_authority_expansion(monkeypatch, tmp_path, field, unsafe):
    root = _root(tmp_path)
    path = root / "sandbox/intake/relationship_conditioned_execution/lifecycle_state.json"
    lifecycle = json.loads(path.read_text())
    lifecycle[field] = unsafe
    _write(path, lifecycle)
    monkeypatch.setenv("RCE_OBSERVED_AT", "2026-07-14T08:00:00+00:00")
    with pytest.raises(LeaseError, match="authority boundary invalid"):
        reconcile(root)
