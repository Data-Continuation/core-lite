from __future__ import annotations
import json, re, zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

MANIFEST_PATH = ".stegverse/ingest_manifest.json"
PRIORITY_ORDER = {"Critical": 0, "Medium": 1, "Low": 2, "NonCritical": 3}

@dataclass(frozen=True)
class QueuedBundle:
    path: Path
    manifest: Dict[str, Any]
    bundle_id: str
    bundle_version: str
    target_repo: str
    priority: str
    succession_mode: str
    family: str
    created_sort: float

def parse_semverish(version: str) -> Tuple[int, ...]:
    parts = re.findall(r"\d+", version or "")
    return tuple(int(p) for p in parts) if parts else (0,)

def read_manifest_from_zip(path: Path) -> Dict[str, Any]:
    with zipfile.ZipFile(path, "r") as archive:
        raw = archive.read(MANIFEST_PATH)
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} manifest must be JSON object")
    return payload

def normalize_priority(value: Any) -> str:
    value = str(value or "Low").strip()
    return value if value in PRIORITY_ORDER else "Low"

def normalize_succession(manifest: Dict[str, Any]) -> str:
    succession = manifest.get("succession", "versioning")
    mode = str(succession.get("mode", "versioning") if isinstance(succession, dict) else succession).strip().lower()
    return "supersede" if mode in {"supersede", "supersedes", "superseding"} else "versioning"

def normalize_family(manifest: Dict[str, Any]) -> str:
    succession = manifest.get("succession", {})
    if isinstance(succession, dict) and succession.get("family"):
        return str(succession["family"])
    return str(manifest.get("bundle_family") or manifest.get("bundle_id", "unknown"))

def load_queued_bundle(path: Path) -> QueuedBundle:
    manifest = read_manifest_from_zip(path)
    return QueuedBundle(path, manifest, str(manifest.get("bundle_id", path.stem)), str(manifest.get("bundle_version", "0")), str(manifest.get("target_repo", "any")), normalize_priority(manifest.get("priority")), normalize_succession(manifest), normalize_family(manifest), path.stat().st_mtime)

def sort_key(bundle: QueuedBundle):
    return (PRIORITY_ORDER[bundle.priority], parse_semverish(bundle.bundle_version), bundle.created_sort, bundle.path.name)

def bundle_to_dict(bundle: QueuedBundle) -> Dict[str, Any]:
    return {"path": bundle.path.as_posix(), "name": bundle.path.name, "bundle_id": bundle.bundle_id, "bundle_version": bundle.bundle_version, "target_repo": bundle.target_repo, "priority": bundle.priority, "succession_mode": bundle.succession_mode, "family": bundle.family, "version_sort": list(parse_semverish(bundle.bundle_version)), "created_sort": bundle.created_sort}

def plan_incoming_bundles(incoming_dir: Path) -> Dict[str, Any]:
    loaded: List[QueuedBundle] = []
    failed_to_read: List[Dict[str, str]] = []
    for path in sorted(incoming_dir.glob("*.zip")):
        try:
            loaded.append(load_queued_bundle(path))
        except Exception as exc:
            failed_to_read.append({"path": path.as_posix(), "error": str(exc)})
    winners: Dict[str, QueuedBundle] = {}
    for b in loaded:
        if b.succession_mode != "supersede":
            continue
        current = winners.get(b.family)
        if current is None or PRIORITY_ORDER[b.priority] < PRIORITY_ORDER[current.priority] or (PRIORITY_ORDER[b.priority] == PRIORITY_ORDER[current.priority] and parse_semverish(b.bundle_version) > parse_semverish(current.bundle_version)) or (PRIORITY_ORDER[b.priority] == PRIORITY_ORDER[current.priority] and parse_semverish(b.bundle_version) == parse_semverish(current.bundle_version) and b.created_sort > current.created_sort):
            winners[b.family] = b
    superseded_paths = {b.path for family, winner in winners.items() for b in loaded if b.family == family and b.path != winner.path}
    process = sorted([b for b in loaded if b.path not in superseded_paths], key=sort_key)
    superseded = sorted([b for b in loaded if b.path in superseded_paths], key=sort_key)
    return {"schema": "stegverse_core_lite_bundle_queue_plan.v1", "incoming_dir": incoming_dir.as_posix(), "priority_order": ["Critical", "Medium", "Low", "NonCritical"], "process": [bundle_to_dict(b) for b in process], "superseded": [bundle_to_dict(b) for b in superseded], "failed_to_read": failed_to_read, "counts": {"process": len(process), "superseded": len(superseded), "failed_to_read": len(failed_to_read), "total_zip_files": len(list(incoming_dir.glob("*.zip")))}}
