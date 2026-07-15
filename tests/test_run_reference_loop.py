from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_reference_loop.py"


def write_config(path: Path, command: list[str], remediation: str = "none") -> None:
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
                "tasks": [
                    {
                        "id": "TEST-001",
                        "status": "ready",
                        "priority": 1,
                        "command": "task",
                        "verification_command": "verify",
                        "remediation": {
                            "strategy": remediation,
                            "eligible_exit_codes": [1],
                        },
                        "done_when": "test command and verification exit zero",
                        "next_task": None,
                    }
                ],
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
