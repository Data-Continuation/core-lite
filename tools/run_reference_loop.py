#!/usr/bin/env python3
"""Run one bounded repository-local task through claim, execution, verification, receipt, and continuation."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "core_lite/reference_loop.json"
STATE = ROOT / "core_lite/reference_loop_state.json"
REPORT = ROOT / "reports/reference_loop_status.json"
RECEIPTS = ROOT / "receipts/reference_loop_receipts.jsonl"
ESCALATION = ROOT / "reports/reference_loop_escalation.json"
LEASE_SECONDS = 900


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def iso(value: dt.datetime | None = None) -> str:
    return (value or utc_now()).isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def new_state(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "repository": config["repository"],
        "updated_at": iso(),
        "lease": None,
        "recovered_from_receipts": False,
        "tasks": {
            task["id"]: {
                "status": task["status"],
                "attempts": 0,
                "last_result": None,
                "completed_at": None,
            }
            for task in config["tasks"]
        },
    }


def read_receipt_chain(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    receipts: list[dict[str, Any]] = []
    expected_previous = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"Receipt line {line_number} must be an object")
        observed_hash = value.get("hash")
        body = {key: item for key, item in value.items() if key != "hash"}
        if not isinstance(observed_hash, str) or observed_hash != digest(body):
            raise ValueError(f"Receipt hash mismatch at line {line_number}")
        if value.get("previous_hash") != expected_previous:
            raise ValueError(f"Receipt chain mismatch at line {line_number}")
        receipts.append(value)
        expected_previous = observed_hash
    return receipts


def recover_state_from_receipts(
    config: dict[str, Any], state: dict[str, Any], receipts_path: Path
) -> dict[str, Any]:
    receipts = read_receipt_chain(receipts_path)
    if not receipts:
        return state
    known_tasks = {task["id"]: task for task in config["tasks"]}
    recovered = False
    for receipt in receipts:
        task_id = receipt.get("task_id")
        if task_id not in known_tasks or receipt.get("decision") != "COMPLETE":
            continue
        if receipt.get("execution_exit_code") != 0 or receipt.get("verification_exit_code") != 0:
            raise ValueError(f"Completed receipt has non-zero evidence: {task_id}")
        task_state = state["tasks"][task_id]
        task_state["status"] = "complete"
        task_state["attempts"] = max(task_state.get("attempts", 0), 1)
        task_state["last_result"] = "COMPLETE"
        task_state["completed_at"] = receipt.get("timestamp")
        recovered = True
    if recovered:
        state["lease"] = None
        state["recovered_from_receipts"] = True
        state["updated_at"] = iso()
    return state


def load_state(config: dict[str, Any], path: Path, receipts_path: Path) -> dict[str, Any]:
    state = read_json(path) if path.exists() else new_state(config)
    for task in config["tasks"]:
        state.setdefault("tasks", {}).setdefault(
            task["id"],
            {"status": task["status"], "attempts": 0, "last_result": None, "completed_at": None},
        )
    return recover_state_from_receipts(config, state, receipts_path)


def active_lease(state: dict[str, Any]) -> bool:
    lease = state.get("lease")
    if not isinstance(lease, dict):
        return False
    try:
        return dt.datetime.fromisoformat(lease["expires_at"]) > utc_now()
    except (KeyError, TypeError, ValueError):
        return False


def dependencies_complete(task: dict[str, Any], state: dict[str, Any]) -> bool:
    return all(state["tasks"].get(dep, {}).get("status") == "complete" for dep in task.get("blocked_by", []))


def evidence_fingerprint(task: dict[str, Any]) -> str | None:
    paths = task.get("retry_watch_paths", [])
    if not task.get("retry_on_evidence_change") or not isinstance(paths, list) or not paths:
        return None
    evidence: list[dict[str, Any]] = []
    for raw in paths:
        if not isinstance(raw, str) or not raw:
            raise ValueError(f"Invalid retry watch path for {task.get('id')}: {raw!r}")
        path = Path(raw)
        if not path.is_absolute():
            path = ROOT / path
        if path.is_file():
            evidence.append({
                "path": raw,
                "exists": True,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            })
        else:
            evidence.append({"path": raw, "exists": False})
    return digest(evidence)


def select_task(config: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    for task in config["tasks"]:
        current = state["tasks"][task["id"]]
        if current["status"] == "blocked" and dependencies_complete(task, state):
            current["status"] = "ready"
        elif current["status"] == "escalated" and dependencies_complete(task, state):
            fingerprint = evidence_fingerprint(task)
            previous = current.get("retry_evidence_fingerprint")
            if fingerprint is not None and (previous is None or fingerprint != previous):
                current["status"] = "retry"
                current["retry_evidence_fingerprint"] = fingerprint
    eligible = [
        task for task in config["tasks"]
        if state["tasks"][task["id"]]["status"] in {"ready", "retry"}
        and dependencies_complete(task, state)
    ]
    return min(eligible, key=lambda item: (item.get("priority", 9999), item["id"])) if eligible else None


def command(config: dict[str, Any], name: str) -> list[str]:
    value = config.get("commands", {}).get(name)
    if not isinstance(value, list) or not value or not all(isinstance(part, str) and part for part in value):
        raise ValueError(f"Command is not registered: {name}")
    return value


def run(config: dict[str, Any], name: str) -> dict[str, Any]:
    argv = command(config, name)
    started = iso()
    result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "name": name,
        "argv": argv,
        "started_at": started,
        "ended_at": iso(),
        "exit_code": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def append_receipt(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_receipt_chain(path)
    previous_hash = existing[-1]["hash"] if existing else None
    body = {**payload, "previous_hash": previous_hash}
    receipt = {**body, "hash": digest(body)}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def execute(config: dict[str, Any], state: dict[str, Any], task: dict[str, Any]) -> tuple[dict[str, Any], int]:
    task_state = state["tasks"][task["id"]]
    attempt_id = str(uuid.uuid4())
    acquired = utc_now()
    state["lease"] = {
        "task_id": task["id"],
        "attempt_id": attempt_id,
        "acquired_at": iso(acquired),
        "expires_at": iso(acquired + dt.timedelta(seconds=LEASE_SECONDS)),
    }
    task_state["status"] = "running"
    task_state["attempts"] += 1

    first = run(config, task["command"])
    remediation = task.get("remediation", {})
    repaired = None
    if (
        first["exit_code"] != 0
        and remediation.get("strategy") == "rerun_once"
        and first["exit_code"] in remediation.get("eligible_exit_codes", [])
    ):
        repaired = run(config, task["command"])
    effective = repaired or first
    verification = run(config, task["verification_command"]) if effective["exit_code"] == 0 else None
    closed = bool(verification and verification["exit_code"] == 0)
    decision = "COMPLETE" if closed else "ESCALATE_FAIL_CLOSED"

    result = {
        "task_id": task["id"],
        "attempt_id": attempt_id,
        "decision": decision,
        "closed": closed,
        "execution": first,
        "remediation": repaired,
        "verification": verification,
        "done_when": task["done_when"],
        "completed_at": iso(),
    }
    task_state["status"] = "complete" if closed else "escalated"
    task_state["last_result"] = decision
    task_state["completed_at"] = result["completed_at"] if closed else None
    if closed and task.get("next_task") in state["tasks"]:
        successor = state["tasks"][task["next_task"]]
        if successor["status"] == "blocked":
            successor["status"] = "ready"
    state["lease"] = None
    state["updated_at"] = iso()
    return result, 0 if closed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--receipts", type=Path, default=RECEIPTS)
    parser.add_argument("--escalation", type=Path, default=ESCALATION)
    args = parser.parse_args()

    config = read_json(args.config)
    try:
        state = load_state(config, args.state, args.receipts)
    except (ValueError, json.JSONDecodeError) as exc:
        write_json(args.escalation, {
            "generated_at": iso(), "repository": config["repository"],
            "decision": "ESCALATE_FAIL_CLOSED", "reason": str(exc),
            "external_mutation_attempted": False,
        })
        print(f"Receipt recovery failed closed: {exc}")
        return 1
    if active_lease(state):
        print("Active lease exists; duplicate execution suppressed.")
        return 0

    task = select_task(config, state)
    if task is None:
        write_json(args.state, state)
        write_json(args.report, {
            "generated_at": iso(), "repository": config["repository"],
            "decision": "NO_ELIGIBLE_TASK", "state": state, "ecosystem": config["ecosystem"],
        })
        print("No eligible task.")
        return 0

    result, exit_code = execute(config, state, task)
    receipt = append_receipt(args.receipts, {
        "receipt_type": "core_lite.reference_loop.task_closure",
        "timestamp": iso(),
        "repository": config["repository"],
        "task_id": task["id"],
        "attempt_id": result["attempt_id"],
        "decision": result["decision"],
        "execution_exit_code": result["execution"]["exit_code"],
        "remediation_exit_code": result["remediation"]["exit_code"] if result["remediation"] else None,
        "verification_exit_code": result["verification"]["exit_code"] if result["verification"] else None,
    })
    write_json(args.state, state)
    write_json(args.report, {
        "generated_at": iso(), "repository": config["repository"], "mode": config["mode"],
        "authority": config["authority"], "selected_task": task["id"], "result": result,
        "receipt": receipt, "state": state, "ecosystem": config["ecosystem"],
    })
    if exit_code:
        write_json(args.escalation, {
            "generated_at": iso(), "repository": config["repository"], "task_id": task["id"],
            "decision": result["decision"],
            "reason": "Execution or verification remained non-zero after authorized remediation.",
            "external_mutation_attempted": False,
            "report": str(args.report),
        })
    elif args.escalation.exists():
        args.escalation.unlink()
    print(f"Task {task['id']}: {result['decision']}")
    print(f"Receipt: {receipt['hash']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
