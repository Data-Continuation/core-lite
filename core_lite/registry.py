from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Dict, List, Any

try:
    from .paths import utc_now
except ImportError:
    from paths import utc_now


def _load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def discover_org_repos(org: str, token: str | None) -> List[Dict[str, Any]]:
    if not token or org == "unknown":
        return []

    repos: List[Dict[str, Any]] = []
    page = 1

    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}&type=all"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "stegverse-core-lite",
            },
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if not payload:
            break

        for item in payload:
            repos.append({
                "name": item.get("name", ""),
                "full_name": item.get("full_name", ""),
                "private": bool(item.get("private", False)),
                "archived": bool(item.get("archived", False)),
                "disabled": bool(item.get("disabled", False)),
                "default_branch": item.get("default_branch", ""),
                "html_url": item.get("html_url", ""),
            })

        page += 1

    return repos


def refresh_registry(repo_root: Path, context: Dict[str, str], registry_path: Path) -> Dict[str, Any]:
    now = utc_now()
    org = context["org"]
    current_full_name = context["repository"]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    registry = _load_json(registry_path, {
        "schema": "stegverse_org_repo_registry.v1",
        "created_at": now,
        "updated_at": now,
        "org": org,
        "current_repo": current_full_name,
        "discovery_mode": "current_repo_only",
        "repos": {},
        "events": [],
    })

    registry["updated_at"] = now
    registry["org"] = org
    registry["current_repo"] = current_full_name

    discovered = []
    discovery_error = None

    try:
        discovered = discover_org_repos(org, token)
    except Exception as exc:
        discovery_error = str(exc)

    if discovered:
        registry["discovery_mode"] = "org_api"
        discovered_names = {repo["full_name"] for repo in discovered if repo.get("full_name")}
    else:
        registry["discovery_mode"] = "current_repo_only" if not discovery_error else "current_repo_only_after_discovery_error"
        discovered_names = {current_full_name}

    repos = registry.setdefault("repos", {})

    for full_name in discovered_names:
        existing = repos.get(full_name, {})
        repos[full_name] = {
            **existing,
            "full_name": full_name,
            "status": "active",
            "first_seen": existing.get("first_seen", now),
            "last_seen": now,
            "last_missing": existing.get("last_missing"),
        }

    for repo in discovered:
        full_name = repo.get("full_name")
        if full_name:
            repos[full_name].update({
                "name": repo.get("name", ""),
                "private": repo.get("private", False),
                "archived": repo.get("archived", False),
                "disabled": repo.get("disabled", False),
                "default_branch": repo.get("default_branch", ""),
                "html_url": repo.get("html_url", ""),
            })

    for full_name, existing in list(repos.items()):
        if full_name not in discovered_names:
            if registry["discovery_mode"] == "org_api":
                existing["status"] = "missing_or_unreachable"
                existing["last_missing"] = now
            else:
                existing.setdefault("status", "unknown_not_refreshed")

    event = {
        "at": now,
        "type": "registry_refresh",
        "discovery_mode": registry["discovery_mode"],
        "repo_count": len(repos),
        "current_repo": current_full_name,
    }
    if discovery_error:
        event["discovery_error"] = discovery_error

    registry.setdefault("events", []).append(event)
    registry["events"] = registry["events"][-200:]

    _write_json(registry_path, registry)
    return registry
