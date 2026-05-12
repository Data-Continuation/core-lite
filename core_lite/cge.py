from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict, List
try:
    from .paths import utc_now
except ImportError:
    from paths import utc_now

ROOT_RUNTIME_ARTIFACTS = ["verification.json", "declared_task_report.json", "boundary_dynamics_report.json", "continuation_gate_report.json", "core_lite_ingest_report.json", "core_lite_run_summary.json"]

def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

def _runtime_at_root(repo_root: Path) -> List[str]:
    return [name for name in ROOT_RUNTIME_ARTIFACTS if (repo_root / name).exists()]

def _failed_bundle_count(repo_root: Path) -> int:
    failed = repo_root / "legacy" / "failed-bundles"
    return 0 if not failed.exists() else len([p for p in failed.rglob("*.zip") if p.is_file()])

def _unexpected_workflow_count(repo_root: Path, expected: List[str]) -> int:
    workflow_dir = repo_root / ".github" / "workflows"
    if not workflow_dir.exists():
        return 0
    actual = {p.relative_to(repo_root).as_posix() for p in workflow_dir.glob("*.yml")}
    actual.update({p.relative_to(repo_root).as_posix() for p in workflow_dir.glob("*.yaml")})
    return len(sorted(actual - set(expected)))

def generate_cge_fingerprint(repo_root: Path, context: Dict[str, str], registry: Dict[str, Any], topology: Dict[str, Any], shim_report: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    expected_workflows = policy.get("expected_workflows", [".github/workflows/core-lite-intake.yml"])
    runtime = _runtime_at_root(repo_root)
    failed = _failed_bundle_count(repo_root)
    missing = int(shim_report.get("summary", {}).get("missing", 0))
    unknown = int(shim_report.get("summary", {}).get("unknown", 0))
    unexpected = _unexpected_workflow_count(repo_root, expected_workflows)
    flags = []
    if missing: flags.append("missing_shim")
    if unknown: flags.append("unknown_shim_state")
    if runtime: flags.append("runtime_artifacts_in_source_root")
    if failed: flags.append("failed_bundle_history_present")
    if unexpected: flags.append("unexpected_workflow")
    basis = {
        "repository": context["repository"],
        "registry_discovery_mode": registry.get("discovery_mode", ""),
        "topology_summary": topology.get("summary", {}),
        "shim_summary": shim_report.get("summary", {}),
        "runtime_at_root": runtime,
        "failed_bundle_count": failed,
        "unexpected_workflow_count": unexpected,
        "drift_flags": flags,
    }
    fingerprint = {
        "schema": "stegverse_cge_fingerprint.v1",
        "generated_at": utc_now(),
        "repository": context["repository"],
        "org": context["org"],
        "fingerprint_hash": _hash(basis),
        "fingerprint_basis": basis,
        "status": "drift_detected" if flags else "healthy",
        "drift_flags": flags,
        "checks": {
            "runtime_artifacts_at_root": runtime,
            "failed_bundle_count": failed,
            "missing_shim_count": missing,
            "unknown_shim_count": unknown,
            "unexpected_workflow_count": unexpected,
        },
    }
    _write_json(repo_root / ".stegverse" / "cge_fingerprint.json", fingerprint)
    return fingerprint
