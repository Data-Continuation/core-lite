from __future__ import annotations
import json, os, urllib.error, urllib.request
from pathlib import Path
from typing import Any, Dict, List
try:
    from .paths import utc_now
except ImportError:
    from paths import utc_now

DEFAULT_REQUIRED_SHIMS = ["incoming/.gitkeep", ".stegverse/core-lite.json", ".github/workflows/core-lite-intake.yml"]

def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _github_file_exists(full_name: str, path: str, token: str | None) -> bool | None:
    if not token:
        return None
    req = urllib.request.Request(
        f"https://api.github.com/repos/{full_name}/contents/{path}",
        headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}", "User-Agent": "stegverse-core-lite"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        return False if exc.code == 404 else None
    except Exception:
        return None

def generate_shim_coverage_report(repo_root: Path, context: Dict[str, str], org_registry: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    now = utc_now()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    required = policy.get("required_repo_shims", DEFAULT_REQUIRED_SHIMS)
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        raise ValueError("required_repo_shims must be a list of strings")
    repos = org_registry.get("repos", {})
    if not isinstance(repos, dict):
        repos = {}
    results: Dict[str, Any] = {}
    for full_name, info in sorted(repos.items()):
        checks: Dict[str, Any] = {}
        for shim in required:
            checks[shim] = (repo_root / shim).exists() if full_name == context["repository"] else _github_file_exists(full_name, shim, token)
        missing = [p for p, ok in checks.items() if ok is False]
        unknown = [p for p, ok in checks.items() if ok is None]
        if missing:
            status = "missing"
        elif unknown:
            status = "unknown"
        elif checks:
            status = "installed"
        else:
            status = "unknown"
        results[full_name] = {
            "repo_status": info.get("status", "unknown"),
            "shim_status": status,
            "required_shims": checks,
            "missing_shims": missing,
            "unknown_shims": unknown,
            "last_checked": now,
        }
    report = {
        "schema": "stegverse_repo_shim_coverage_report.v1",
        "generated_at": now,
        "current_repo": context["repository"],
        "required_shims": required,
        "repo_count": len(results),
        "repos": results,
        "summary": {
            "installed": sum(1 for r in results.values() if r["shim_status"] == "installed"),
            "missing": sum(1 for r in results.values() if r["shim_status"] == "missing"),
            "unknown": sum(1 for r in results.values() if r["shim_status"] == "unknown"),
        },
    }
    _write_json(repo_root / ".stegverse" / "repo_shim_coverage_report.json", report)
    return report
