from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .cge import generate_cge_fingerprint
    from .context import detect_context
    from .ingest import ingest_incoming, load_core_policy
    from .receipts import append_receipt
    from .registry import refresh_registry
    from .shims import generate_shim_coverage_report
    from .source_state_index import generate_source_state_index
    from .tasks import run_declared_tasks
    from .topology import generate_topology_registry
except ImportError:
    from cge import generate_cge_fingerprint
    from context import detect_context
    from ingest import ingest_incoming, load_core_policy
    from receipts import append_receipt
    from registry import refresh_registry
    from shims import generate_shim_coverage_report
    from source_state_index import generate_source_state_index
    from tasks import run_declared_tasks
    from topology import generate_topology_registry


def run(repo_root: Path, task_id: str | None = None, skip_tasks: bool = False) -> int:
    repo_root = repo_root.resolve()
    context = detect_context(repo_root)
    policy = load_core_policy(repo_root)

    registry_path = repo_root / policy.get("registry_path", ".stegverse/org_registry.json")
    registry = refresh_registry(repo_root, context, registry_path)

    topology = generate_topology_registry(repo_root, context, registry, policy)
    shim_report = generate_shim_coverage_report(repo_root, context, registry, policy)
    cge_fingerprint = generate_cge_fingerprint(repo_root, context, registry, topology, shim_report, policy)

    append_receipt(repo_root, {
        "type": "registry_topology_fingerprint_refresh",
        "repository": context["repository"],
        "registry_path": str(registry_path),
        "topology_path": ".stegverse/ingestion_topology_registry.json",
        "shim_report_path": ".stegverse/repo_shim_coverage_report.json",
        "cge_fingerprint_path": ".stegverse/cge_fingerprint.json",
        "cge_status": cge_fingerprint.get("status"),
        "drift_flags": cge_fingerprint.get("drift_flags", []),
        "success": True,
    })

    ingest_report = ingest_incoming(repo_root)

    task_report = None
    run_tasks = bool(policy.get("run_tasks_after_ingest", True)) and not skip_tasks

    if run_tasks:
        task_manifest = repo_root / policy.get("default_task_manifest", "tools/tasks/formalism_tests_tasks.json")
        task_report = run_declared_tasks(repo_root, task_manifest, task_id=task_id)

    source_state_index = generate_source_state_index(repo_root, repository=context["repository"])

    append_receipt(repo_root, {
        "type": "source_state_index_generated",
        "repository": context["repository"],
        "source_state_index_path": ".stegverse/source_state_index.json",
        "event_count": source_state_index.get("event_count"),
        "scope_count": len(source_state_index.get("latest_validated_sources", {})),
        "allow_scope_count": len(source_state_index.get("allow_status", {})),
        "local_chain_valid": source_state_index.get("chain_status", {}).get("local_chain", {}).get("valid"),
        "parent_links_valid_locally": source_state_index.get("chain_status", {}).get("parent_links", {}).get("valid_locally"),
        "success": True,
    })

    summary = {
        "schema": "stegverse_core_lite_run_summary.v3",
        "context": context,
        "registry_path": str(registry_path),
        "registry_discovery_mode": registry.get("discovery_mode"),
        "topology_path": ".stegverse/ingestion_topology_registry.json",
        "shim_report_path": ".stegverse/repo_shim_coverage_report.json",
        "cge_fingerprint_path": ".stegverse/cge_fingerprint.json",
        "source_state_index_path": ".stegverse/source_state_index.json",
        "cge_status": cge_fingerprint.get("status"),
        "drift_flags": cge_fingerprint.get("drift_flags", []),
        "source_state_event_count": source_state_index.get("event_count"),
        "source_state_scope_count": len(source_state_index.get("latest_validated_sources", {})),
        "source_state_allow_scope_count": len(source_state_index.get("allow_status", {})),
        "local_chain_valid": source_state_index.get("chain_status", {}).get("local_chain", {}).get("valid"),
        "parent_links_valid_locally": source_state_index.get("chain_status", {}).get("parent_links", {}).get("valid_locally"),
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

    local_chain_valid = source_state_index.get("chain_status", {}).get("local_chain", {}).get("valid")
    if local_chain_valid is False:
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="StegVerse Core-Lite CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Refresh registry, fingerprint topology, ingest bundles, run tasks, and update source state.")
    run_parser.add_argument("--repo-root", default=".", help="Target repository root.")
    run_parser.add_argument("--task-id", default=None, help="Optional declared task id.")
    run_parser.add_argument("--skip-tasks", action="store_true", help="Skip declared task execution.")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command == "run":
        return run(Path(args.repo_root), task_id=args.task_id, skip_tasks=args.skip_tasks)

    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
