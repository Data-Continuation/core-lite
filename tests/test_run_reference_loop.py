from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_reference_loop.py"


def _digest(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_config(path: Path, command: list[str], remediation: str = "none", two_tasks: bool = False) -> None:
    tasks = [
        {
            "id": "TEST-001",
            "status": "ready",
            "priority": 1,
            "command": "task",
            "verification_command": "verify",
            "remediation": {"strategy": remediation, "eligible_exit_codes": [1]},
            "done_when": "test command and verification exit zero",
            "next_task": "TEST-002" if two_tasks else None,
        }
    ]
    if two_tasks:
        tasks.append(
            {
                "id": "TEST-002",
                "status": "blocked",
                "priority": 2,
                "blocked_by": ["TEST-001"],
                "command": "task",
                "verification_command": "verify",
                "remediation": {"strategy": "none", "eligible_exit_codes": []},
                "done_when": "second command and verification exit zero",
                "next_task": None,
            }
        )
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repository": "Data-Continuation/core-lite",
                "mode": "repository_local_reference_loop",
                "authority": {
                    "external_repository_mutation": False,
                    "production_mutation": False,
                },
                "ecosystem": [],
                "commands": {"task": command, "verify": command},
                "tasks": tasks,
            }
        ),
        encoding="utf-8",
    )


def invoke(tmp_path: Path, config: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--config",
            str(config),
            "--state",
            str(tmp_path / "state.json"),
            "--report",
            str(tmp_path / "report.json"),
            "--receipts",
            str(tmp_path / "receipts.jsonl"),
            "--escalation",
            str(tmp_path / "escalation.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_success_closes_task_and_writes_chained_receipt(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    write_config(config, [sys.executable, "-c", "raise SystemExit(0)"])

    result = invoke(tmp_path, config)

    assert result.returncode == 0
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    receipt = json.loads((tmp_path / "receipts.jsonl").read_text(encoding="utf-8"))
    assert state["tasks"]["TEST-001"]["status"] == "complete"
    assert state["lease"] is None
    assert report["result"]["decision"] == "COMPLETE"
    assert receipt["decision"] == "COMPLETE"
    assert receipt["hash"]
    assert not (tmp_path / "escalation.json").exists()


def test_failure_retries_once_then_escalates_fail_closed(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    write_config(config, [sys.executable, "-c", "raise SystemExit(1)"], remediation="rerun_once")

    result = invoke(tmp_path, config)

    assert result.returncode == 1
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    escalation = json.loads((tmp_path / "escalation.json").read_text(encoding="utf-8"))
    assert state["tasks"]["TEST-001"]["status"] == "escalated"
    assert state["tasks"]["TEST-001"]["attempts"] == 1
    assert state["lease"] is None
    assert report["result"]["decision"] == "ESCALATE_FAIL_CLOSED"
    assert report["result"]["remediation"]["exit_code"] == 1
    assert escalation["external_mutation_attempted"] is False


def test_active_lease_suppresses_duplicate_execution(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    write_config(config, [sys.executable, "-c", "raise SystemExit(0)"])
    state = {
        "schema_version": 1,
        "repository": "Data-Continuation/core-lite",
        "updated_at": "2026-07-14T00:00:00+00:00",
        "lease": {
            "task_id": "TEST-001",
            "attempt_id": "existing",
            "acquired_at": "2099-01-01T00:00:00+00:00",
            "expires_at": "2099-01-01T00:15:00+00:00",
        },
        "tasks": {
            "TEST-001": {
                "status": "running",
                "attempts": 1,
                "last_result": None,
                "completed_at": None,
            }
        },
    }
    (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")

    result = invoke(tmp_path, config)

    assert result.returncode == 0
    assert "duplicate execution suppressed" in result.stdout
    assert not (tmp_path / "receipts.jsonl").exists()


def test_missing_state_recovers_completed_task_and_runs_successor(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    write_config(config, [sys.executable, "-c", "raise SystemExit(0)"], two_tasks=True)
    body = {
        "receipt_type": "core_lite.reference_loop.task_closure",
        "timestamp": "2026-07-15T00:00:00+00:00",
        "repository": "Data-Continuation/core-lite",
        "task_id": "TEST-001",
        "attempt_id": "recovered",
        "decision": "COMPLETE",
        "execution_exit_code": 0,
        "remediation_exit_code": None,
        "verification_exit_code": 0,
        "previous_hash": None,
    }
    receipt = {**body, "hash": _digest(body)}
    (tmp_path / "receipts.jsonl").write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    result = invoke(tmp_path, config)

    assert result.returncode == 0
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    receipts = [json.loads(line) for line in (tmp_path / "receipts.jsonl").read_text(encoding="utf-8").splitlines()]
    assert state["recovered_from_receipts"] is True
    assert state["tasks"]["TEST-001"]["status"] == "complete"
    assert state["tasks"]["TEST-002"]["status"] == "complete"
    assert report["selected_task"] == "TEST-002"
    assert receipts[-1]["previous_hash"] == receipts[0]["hash"]


def test_invalid_receipt_chain_fails_closed_without_execution(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    write_config(config, [sys.executable, "-c", "raise SystemExit(0)"])
    invalid = {
        "task_id": "TEST-001",
        "decision": "COMPLETE",
        "execution_exit_code": 0,
        "verification_exit_code": 0,
        "previous_hash": None,
        "hash": "not-a-valid-hash",
    }
    (tmp_path / "receipts.jsonl").write_text(json.dumps(invalid) + "\n", encoding="utf-8")

    result = invoke(tmp_path, config)

    assert result.returncode == 1
    escalation = json.loads((tmp_path / "escalation.json").read_text(encoding="utf-8"))
    assert escalation["decision"] == "ESCALATE_FAIL_CLOSED"
    assert "Receipt hash mismatch" in escalation["reason"]
    assert not (tmp_path / "state.json").exists()


def test_escalated_task_retries_once_when_evidence_changes(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    watch = tmp_path / "watch.json"
    watch.write_text('{"version":1}', encoding="utf-8")
    write_config(config, [sys.executable, "-c", "raise SystemExit(1)"])
    value = json.loads(config.read_text(encoding="utf-8"))
    value["tasks"][0]["retry_on_evidence_change"] = True
    value["tasks"][0]["retry_watch_paths"] = [str(watch)]
    config.write_text(json.dumps(value), encoding="utf-8")
    state = {
        "schema_version": 1,
        "repository": "Data-Continuation/core-lite",
        "updated_at": "2026-09-01T00:00:00+00:00",
        "lease": None,
        "tasks": {
            "TEST-001": {
                "status": "escalated",
                "attempts": 1,
                "last_result": "ESCALATE_FAIL_CLOSED",
                "completed_at": None,
            }
        },
    }
    (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")

    first = invoke(tmp_path, config)
    assert first.returncode == 1
    first_state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert first_state["tasks"]["TEST-001"]["attempts"] == 2
    fingerprint = first_state["tasks"]["TEST-001"]["retry_evidence_fingerprint"]

    second = invoke(tmp_path, config)
    assert second.returncode == 0
    assert "No eligible task." in second.stdout
    second_state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert second_state["tasks"]["TEST-001"]["attempts"] == 2
    assert second_state["tasks"]["TEST-001"]["retry_evidence_fingerprint"] == fingerprint

    watch.write_text('{"version":2}', encoding="utf-8")
    third = invoke(tmp_path, config)
    assert third.returncode == 1
    third_state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert third_state["tasks"]["TEST-001"]["attempts"] == 3
    assert third_state["tasks"]["TEST-001"]["retry_evidence_fingerprint"] != fingerprint
