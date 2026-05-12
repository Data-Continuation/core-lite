from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

try:
    from .paths import utc_now
except ImportError:
    from paths import utc_now


def load_task_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "name": "missing task manifest",
            "version": "0",
            "tasks": [],
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("tasks"), list):
        raise ValueError(f"task manifest must contain tasks list: {path}")
    return payload


def run_declared_tasks(repo_root: Path, manifest_path: Path, task_id: str | None = None) -> Dict[str, Any]:
    manifest = load_task_manifest(manifest_path)
    tasks = manifest.get("tasks", [])

    if task_id:
        selected = [task for task in tasks if task.get("task_id") == task_id]
        if not selected:
            raise ValueError(f"task_id not found: {task_id}")
    else:
        selected = [task for task in tasks if task.get("enabled", True) is True]

    results: List[Dict[str, Any]] = []

    for task in selected:
        command = task.get("command")
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            raise ValueError(f"invalid command for task: {task.get('task_id')}")

        started = utc_now()
        completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
        finished = utc_now()

        expected_outputs = task.get("expected_outputs", [])
        if not isinstance(expected_outputs, list):
            raise ValueError(f"expected_outputs must be list for task: {task.get('task_id')}")

        output_status = {path: (repo_root / path).exists() for path in expected_outputs}
        success = completed.returncode == 0 and all(output_status.values())

        results.append({
            "task_id": task.get("task_id", ""),
            "description": task.get("description", ""),
            "command": command,
            "started_at": started,
            "finished_at": finished,
            "returncode": completed.returncode,
            "success": success,
            "expected_outputs": output_status,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        })

    report = {
        "schema": "stegverse_declared_task_report.v1",
        "generated_at": utc_now(),
        "manifest_path": str(manifest_path),
        "manifest_name": manifest.get("name", ""),
        "manifest_version": manifest.get("version", ""),
        "task_count": len(results),
        "success": all(result["success"] for result in results),
        "results": results,
    }

    (repo_root / "declared_task_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return report
