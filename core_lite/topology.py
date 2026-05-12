from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
try:
    from .paths import utc_now
except ImportError:
    from paths import utc_now

def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def generate_topology_registry(repo_root: Path, context: Dict[str, str], org_registry: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    now = utc_now()
    peers = policy.get("peer_ingestion_engines", [])
    if not isinstance(peers, list):
        raise ValueError("peer_ingestion_engines must be a list")
    normalized = [{"org": str(p.get("org", "")), "engine_repo": str(p.get("engine_repo", "")), "engine_class": str(p.get("engine_class", "unknown")), "status": str(p.get("status", "unknown")), "native_org": False, "last_seen": str(p.get("last_seen", ""))} for p in peers if isinstance(p, dict)]
    repos = org_registry.get("repos", {}) if isinstance(org_registry.get("repos", {}), dict) else {}
    topology = {"schema": "stegverse_ingestion_topology_registry.v1", "generated_at": now, "native_engine": {"org": context["org"], "engine_repo": context["repository"], "engine_class": "org_core_lite", "status": "installed", "native_org": True, "last_seen": now}, "peer_engines": normalized, "native_org": {"org": context["org"], "repo_count": len(repos), "discovery_mode": org_registry.get("discovery_mode", "unknown"), "repos": repos}, "summary": {"installed_org_engines": 1 + sum(1 for p in normalized if p["status"] == "installed"), "attempted_org_engines": sum(1 for p in normalized if p["status"] == "attempted"), "missing_org_engines": sum(1 for p in normalized if p["status"] == "missing"), "repo_only_engines": sum(1 for p in normalized if p["status"] == "repo_only"), "declared_peer_engines": len(normalized)}}
    _write_json(repo_root / ".stegverse" / "ingestion_topology_registry.json", topology)
    return topology
