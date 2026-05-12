from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .context import detect_context
    from .ingest import ingest_incoming, load_core_policy
    from .registry import refresh_registry
    from .tasks import run_declared_tasks
except ImportError:
    from context import detect_context
    from ingest import ingest_incoming, load_core_policy
    from registry import refresh_registry
    from tasks import run_declared_tasks


def run(repo_root: Path, task_id: str | None = None) -> int:
    repo_root = repo_root.resolve()
    context = detect_context(repo_root)
    policy = load_core_policy(repo_root)

    registry_path = repo_root / policy.get("registry_path", ".stegverse/org_registry.json")
    registry = refresh_registry(repo_root, context, registry_path)

    ingest_report = ingest_incoming(repo_root)

    run_tasks = bool(policy.get("run_tasks_after_ingest", True))
    task_report = None

    if run_tasks:
        task_manifest = repo_root / policy.get("default_task_manifest", "tools/tasks/formalism_tests_tasks.json")
        task_report = run_declared_tasks(repo_root, task_manifest, task_id=task_id)

    summary = {
        "schema": "stegverse_core_lite_run_summary.v1",
        "context": context,
        "registry_path": str(registry_path),
        "registry_discovery_mode": registry.get("discovery_mode"),
        "ingest_success": ingest_report.get("success"),
        "task_success": None if task_report is None else task_report.get("success"),
    }

    (repo_root / "core_lite_run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))

    if not ingest_report.get("success"):
        return 1
    if task_report is not None and not task_report.get("success"):
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="StegVerse Core-Lite CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Refresh registry, ingest incoming bundles, and run declared tasks.")
    run_parser.add_argument("--repo-root", default=".", help="Target repository root.")
    run_parser.add_argument("--task-id", default=None, help="Optional declared task id.")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command == "run":
        return run(Path(args.repo_root), task_id=args.task_id)

    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
