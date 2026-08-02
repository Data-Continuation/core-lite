import json
from pathlib import Path

import pytest

import tools.reconcile_rce_canonical_workstream as module


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def seed_stage(root: Path, task_id: str = "RCE-P0-009", authoritative: bool = True) -> str:
    receipt = "receipts/rce_p0_009_authoritative_validation.json"
    write(root / receipt, {
        "task_id": task_id,
        "authoritative_completion_evidence": authoritative,
        "decision": "RECONSTRUCTION_INDEX_VERIFIED",
        "manual_actions_required": [],
        "production_destination_allowed": False,
        "external_destination_mutation_performed": False,
    })
    write(root / "core_lite/tasks/relationship_conditioned_execution_p0_009.json", {
        "task_id": task_id,
        "status": "COMPLETE",
    })
    return receipt


def test_verifies_authoritative_sandbox_stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "ROOT", tmp_path)
    receipt = seed_stage(tmp_path)
    result = module.verify_stage("RCE-P0-009", receipt)
    assert result["status"] == "COMPLETE"
    assert result["decision"] == "RECONSTRUCTION_INDEX_VERIFIED"


def test_rejects_non_authoritative_stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "ROOT", tmp_path)
    receipt = seed_stage(tmp_path, authoritative=False)
    with pytest.raises(module.ReconciliationError, match="non-authoritative"):
        module.verify_stage("RCE-P0-009", receipt)


def test_rejects_manual_action_dependency(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "ROOT", tmp_path)
    receipt = seed_stage(tmp_path)
    path = tmp_path / receipt
    value = json.loads(path.read_text())
    value["manual_actions_required"] = ["operator approval"]
    write(path, value)
    with pytest.raises(module.ReconciliationError, match="manual action"):
        module.verify_stage("RCE-P0-009", receipt)


def test_stage_chain_is_complete_and_ordered() -> None:
    assert [item[0] for item in module.STAGES] == [f"RCE-P0-{index:03d}" for index in range(7, 15)]
    assert all(item[1].startswith("tools/") for item in module.STAGES)
    assert all(item[2].startswith("receipts/") for item in module.STAGES)
