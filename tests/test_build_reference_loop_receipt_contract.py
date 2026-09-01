from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.build_reference_loop_receipt_contract import (
    ReceiptContractError,
    contract_for,
    digest,
    load_chain,
)


def receipt(task_id: str, previous_hash: str | None, *, decision: str = "COMPLETE", attempt_suffix: str = "1") -> dict:
    body = {
        "receipt_type": "core_lite.reference_loop.task_closure",
        "timestamp": "2026-07-15T00:00:00+00:00",
        "repository": "Data-Continuation/core-lite",
        "task_id": task_id,
        "attempt_id": f"attempt-{task_id}-{attempt_suffix}",
        "decision": decision,
        "execution_exit_code": 0 if decision == "COMPLETE" else 1,
        "remediation_exit_code": None,
        "verification_exit_code": 0 if decision == "COMPLETE" else None,
        "previous_hash": previous_hash,
    }
    return {**body, "hash": digest(body)}


def write_chain(path: Path, receipts: list[dict]) -> None:
    path.write_text("".join(json.dumps(item, sort_keys=True) + "\n" for item in receipts), encoding="utf-8")


def test_builds_read_only_master_records_contract(tmp_path: Path) -> None:
    first = receipt("REF-LOOP-001", None)
    second = receipt("REF-LOOP-002", first["hash"])
    path = tmp_path / "receipts.jsonl"
    write_chain(path, [first, second])
    result = contract_for(load_chain(path))
    assert result["decision"] == "RECEIPT_CONTRACT_VERIFIED"
    assert result["target_repository"] == "master-records/master-records"
    assert result["chain_head"] == second["hash"]
    assert result["authority"]["external_repository_mutation"] is False
    assert result["authority"]["transfer_authorized"] is False


def test_rejects_broken_previous_hash(tmp_path: Path) -> None:
    first = receipt("REF-LOOP-001", None)
    second = receipt("REF-LOOP-002", "wrong")
    path = tmp_path / "receipts.jsonl"
    write_chain(path, [first, second])
    with pytest.raises(ReceiptContractError, match="broken previous_hash"):
        load_chain(path)


def test_rejects_non_zero_completion_evidence(tmp_path: Path) -> None:
    value = receipt("REF-LOOP-001", None)
    value["verification_exit_code"] = 1
    value["hash"] = digest({key: item for key, item in value.items() if key != "hash"})
    path = tmp_path / "receipts.jsonl"
    write_chain(path, [value])
    with pytest.raises(ReceiptContractError, match="non-zero closure evidence"):
        load_chain(path)


def test_preserves_fail_closed_attempt_before_success(tmp_path: Path) -> None:
    first = receipt("REF-LOOP-001", None)
    failed = receipt("REF-LOOP-002", first["hash"], decision="ESCALATE_FAIL_CLOSED", attempt_suffix="failed")
    completed = receipt("REF-LOOP-002", failed["hash"], attempt_suffix="complete")
    path = tmp_path / "receipts.jsonl"
    write_chain(path, [first, failed, completed])
    result = contract_for(load_chain(path))
    assert result["completed_tasks"] == ["REF-LOOP-001", "REF-LOOP-002"]
    assert result["receipt_count"] == 3
    assert result["completed_task_count"] == 2
    assert result["failed_closed_attempt_count"] == 1
    assert result["attempt_history_preserved"] is True
    assert result["chain_head"] == completed["hash"]


def test_rejects_unresolved_terminal_fail_closed_attempt(tmp_path: Path) -> None:
    first = receipt("REF-LOOP-001", None)
    failed = receipt("REF-LOOP-002", first["hash"], decision="ESCALATE_FAIL_CLOSED", attempt_suffix="failed")
    path = tmp_path / "receipts.jsonl"
    write_chain(path, [first, failed])
    with pytest.raises(ReceiptContractError, match="latest task attempts are not complete"):
        contract_for(load_chain(path))
