#!/usr/bin/env python3
"""Build or verify a read-only contract for the reference-loop receipt chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts/reference_loop_receipts.jsonl"
REPORT = ROOT / "reports/reference_loop_receipt_contract.json"


class ReceiptContractError(ValueError):
    pass


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_chain(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ReceiptContractError(f"receipt chain missing: {path}")
    receipts = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not receipts:
        raise ReceiptContractError("receipt chain is empty")
    previous = None
    seen_attempts: set[str] = set()
    for index, receipt in enumerate(receipts):
        claimed = receipt.get("hash")
        body = {key: value for key, value in receipt.items() if key != "hash"}
        if claimed != digest(body):
            raise ReceiptContractError(f"invalid receipt hash at index {index}")
        if receipt.get("previous_hash") != previous:
            raise ReceiptContractError(f"broken previous_hash at index {index}")
        task_id = receipt.get("task_id")
        attempt_id = receipt.get("attempt_id")
        if not isinstance(task_id, str) or not task_id:
            raise ReceiptContractError(f"invalid task_id at index {index}")
        if not isinstance(attempt_id, str) or not attempt_id or attempt_id in seen_attempts:
            raise ReceiptContractError(f"invalid or duplicate attempt_id at index {index}")
        decision = receipt.get("decision")
        if decision not in {"COMPLETE", "ESCALATE_FAIL_CLOSED"}:
            raise ReceiptContractError(f"unsupported receipt decision at index {index}: {decision}")
        if decision == "COMPLETE":
            if receipt.get("execution_exit_code") != 0 or receipt.get("verification_exit_code") != 0:
                raise ReceiptContractError(f"non-zero closure evidence at index {index}")
        else:
            if receipt.get("execution_exit_code") == 0:
                raise ReceiptContractError(f"fail-closed receipt has zero execution exit code at index {index}")
        seen_attempts.add(attempt_id)
        previous = claimed
    return receipts


def contract_for(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    latest_by_task: dict[str, dict[str, Any]] = {}
    completed_tasks: list[str] = []
    failed_closed_attempts = 0
    for receipt in receipts:
        task_id = receipt["task_id"]
        latest_by_task[task_id] = receipt
        if receipt["decision"] == "COMPLETE" and task_id not in completed_tasks:
            completed_tasks.append(task_id)
        elif receipt["decision"] == "ESCALATE_FAIL_CLOSED":
            failed_closed_attempts += 1

    unresolved = sorted(
        task_id for task_id, receipt in latest_by_task.items()
        if receipt.get("decision") != "COMPLETE"
    )
    if unresolved:
        raise ReceiptContractError(f"latest task attempts are not complete: {unresolved}")

    return {
        "schema": "stegverse.core_lite.reference_receipt_contract.v1",
        "repository": "Data-Continuation/core-lite",
        "target_repository": "master-records/master-records",
        "relationship": "durable_receipt_and_reconstruction_contract",
        "receipt_count": len(receipts),
        "attempt_count": len(receipts),
        "completed_task_count": len(completed_tasks),
        "completed_tasks": completed_tasks,
        "failed_closed_attempt_count": failed_closed_attempts,
        "attempt_history_preserved": True,
        "chain_head": receipts[-1]["hash"],
        "chain_sha256": digest(receipts),
        "authority": {
            "read_only_contract": True,
            "transfer_authorized": False,
            "external_repository_mutation": False,
            "production_mutation": False,
        },
        "decision": "RECEIPT_CONTRACT_VERIFIED",
        "manual_actions_required": [],
    }


def write_report(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipts", type=Path, default=RECEIPTS)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        expected = contract_for(load_chain(args.receipts))
        if args.verify:
            observed = json.loads(args.report.read_text(encoding="utf-8"))
            if observed != expected:
                raise ReceiptContractError("receipt contract does not match the verified chain")
        else:
            write_report(args.report, expected)
    except (OSError, json.JSONDecodeError, ReceiptContractError) as exc:
        print(json.dumps({"decision": "DENY_RECEIPT_CONTRACT", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"decision": expected["decision"], "chain_head": expected["chain_head"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
