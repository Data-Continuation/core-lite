#!/usr/bin/env python3
"""Run one bounded repository-local Core-Lite task to verified closure.

The runner deliberately has no external-repository or production authority. It:
- loads the authoritative local task ledger and ecosystem relationship map;
- selects the highest-priority eligible task;
- acquires a time-bounded lease;
- executes only commands registered in the ledger;
- applies only the declared bounded remediation strategy;
- verifies the result;
- writes a hash-chained receipt and status report;
- advances the next task when the current task closes;
- records an escalation instead of guessing when closure is not authorized.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "core_lite" / "reference_loop.json"
DEFAULT_STATE = ROOT / "core_lite" / "reference_loop_state.json"
DEFAULT_REPORT = ROOT / "reports" / "reference_loop_status.json"
DEFAULT_RECEIPTS = ROOT / "receipts" / "reference_loop_receipts.jsonl"
DEFAULT_ESCALATION = ROOT / "reports" / "reference_loop_escalation.json"
LEASE_SECONDS = 15 * 60


def now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def iso(value: dt.datetime | None = None) -> str:
    return (value or now()).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def initial_state(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "repository": config["repository"],
        "updated_at": iso(),
        "lease": None,
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


def load_state(config: dict[str, Any], path: Path) -> dict[str, Any]:
    state = read_json(path) if path.exists() else initial_state(config)
    for task in config["tasks"]:
        state.setdefault("tasks", {}).setdefault(
            task["id"],
            {"status": task["status"], "attempts": 0, "last_result": None, "completed_at": None},
        )
    return state


def lease_is_active(lease: Any, current: dt.datetime) -> bool:
    if not isinstance(lease, dict) or not lease.get("expires_at"):
        return False
    try:
        expiry = dt.datetime.fromisoformat(lease["expires_at"])
    except (TypeError, ValueError):
        return False
    return expiry > current


def task_by_id(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in config["tasks"]}


def dependencies_complete(task: dict[str, Any], state: dict[str, Any]) -> bool:
    return all(state["tasks"].get(dep, {}).get("status") == "complete" for dep in task.get("blocked_by", []))


def activate_unblocked_tasks(config: dict[str, Any], state: dict[str, Any]) -> None:
    for task in config["tasks"]:
        task_state = state["tasks"][task["id"]]
        if task_state["status"] == "blocked" and dependencies_complete(task, state):
            task_state["status"] = "ready"


def select_task(config: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    activate_unblocked_tasks(config, state)
    eligible = [
        task
        for task in config["tasks"]
        if state["tasks"][task["id"]]["status"] in {"ready", "retry"}
        and dependencies_complete(task, state)
    ]
    return min(eligible, key=lambda item: (item.get("priority", 9999), item["id"])) if eligible else None


def registered_command(config: dict[str, Any], command_name: str) -> list[str]:
    command = config.get("commands", {}).get(command_name)
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
        raise ValueError(f"Unregistered or invalid command: {command_name}")
    return command


def run_command(config: dict[str, Any], command_name: str) -> dict[str, Any]:
    command = registered_command(config, command_name)
    started = now()
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    ended = now()
    return {
        "name": command_name,
        "argv": command,
        "started_at": iso(started),
        "ended_at": iso(ended),
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-12000:],
    }


def append_receipt(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = None
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            previous_hash = json.loads(lines[-1]).get("hash")
    body = {**payload, "previous_hash": previous_hash}
    receipt = {**body, "hash": stable_hash(body)}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def execute_task(config: dict[str, Any], state: dict[str, Any], task: dict[str, Any]) -> tuple[dict[str, Any], int]:
    task_id = task["id"]
    task_state = state["tasks"][task_id]
    attempt_id = str(uuid.uuid4())
    current = now()
    state["lease"] = {
        "task_id": task_id,
        "attempt_id": attempt_id,
        "acquired_at": iso(current),
        "expires_at": iso(current + dt.timedelta(seconds=LEASE_SECONDS)),
    }
    task_state["status"] = "running"
    task_state["attempts"] += 1
    task_state["last_result"] = None

    execution = run_command(config, task["command"])
    remediation_result = None
    remediation = task.get("remediation", {"strategy": "none", "eligible_exit_codes": []})
    if (
        execution["exit_code"] != 0
        and remediation.get("strategy") == "rerun_once"
        and execution["exit_code"] in remediation.get("eligible_exit_codes", [])
    ):
        remediation_result = run_command(config, task["command"])

    effective_execution = remediation_result or execution
    verification = run_command(config, task["verification_command"]) if effective_execution["exit_code"] == 0 else None
    closed = effective_execution["exit_code"] == 0 and verification is not None and verification["exit_code"] == 0

    result = {
        "task_id": task_id,
        "attempt_id": attempt_id,
        "closed": closed,
        "decision": "COMPLETE" if closed else "ESCALATE_FAIL_CLOSED",
        "execution": execution,
        "remediation": remediation_result,
        "verification": verification,
        "done_when": task["done_when"],
        "completed_at": iso(),
    }

    if closed:
        task_state["status"] = "complete"
        task_state["completed_at"] = result["completed_at"]
        next_task = task.get("next_task")
        if next_task and next_task in state["tasks"] and state["tasks"][next_task]["status"] == "blocked":
            state["tasks"][next_task]["status"] = "ready"
    else:
        task_state["status"] = "escalated"

    task_state["last_result"] = result["decision"]
    state["lease"] = None
    state["updated_at"] = iso()
    return result, 0 if closed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one bounded Core-Lite reference-loop task.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    parser.add_argument("--escalation", type=Path, default=DEFAULT_ESCALATION)
    args = parser.parse_args()

    config = read_json(args.config)
    state = load_state(config, args.state)
    current = now()
    if lease_is_active(state.get("lease"), current):
        print("Reference loop already has an active lease; exiting without duplicate execution.")
        return 0

    task = select_task(config, state)
    if task is None:
        report = {
            "generated_at": iso(),
            "repository": config["repository"],
            "decision": "NO_ELIGIBLE_TASK",
            "state": state,
            "ecosystem": config["ecosystem"],
        }
        write_json(args.state, state)
        write_json(args.report, report)
        print("No eligible task.")
        return 0

    result, exit_code = execute_task(config, state, task)
    receipt = append_receipt(
        args.receipts,
        {
            "receipt_type": "core_lite.reference_loop.task_closure",
            "timestamp": iso(),
            "repository": config["repository"],
            "task_id": task["id"],
            "attempt_id": result["attempt_id"],
            "decision": result["decision"],
            "execution_exit_code": result["execution"]["exit_code"],
            "remediation_exit_code": result["remediation"]["exit_code"] if result["remediation"] else None,
            "verification_exit_code": result["verification"]["exit_code"] if result["verification"] else None,
        },
    )
    report = {
        "generated_at": iso(),
        "repository": config["repository"],
        "mode": config["mode"],
        "authority": config["authority"],
        "selected_task": task["id"],
        "result": result,
        "receipt": receipt,
        "state": state,
        "ecosystem": config["ecosystem"],
    }
    write_json(args.state, state)
    write_json(args.report, report)
    if exit_code:
        write_json(
            args.escalation,
            {
                "generated_at": iso(),
                "repository": config["repository"],
                "task_id": task["id"],
                "decision": result["decision"],
                "reason": "Execution or verification remained non-zero after the authorized remediation policy.",
                "external_mutation_attempted": false,
                "report": args.report.relative_to(ROOT).as_posix() if args.report.is_relative_to(ROOT) else str(args.report),
            },
        )
    elif args.escalation.exists():
        args.escalation.unlink()

    print(f"Task {task['id']}: {result['decision']}")
    print(f"Receipt: {receipt['hash']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
