from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


MANIFEST_PATH = ".stegverse/ingest_manifest.json"

PRIORITY_ORDER = {
    "Critical": 0,
    "Medium": 1,
    "Low": 2,
    "NonCritical": 3,
}


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
    """Parse simple semantic-ish versions into a sortable tuple.

    Examples:
        0.1.0 -> (0, 1, 0)
        v2.10 -> (2, 10)
        stage-5 -> (5,)
    """
    parts = re.findall(r"\d+", version or "")
    if not parts:
        return (0,)
    return tuple(int(part) for part in parts)


def read_manifest_from_zip(path: Path) -> Dict[str, Any]:
    with zipfile.ZipFile(path, "r") as archive:
        try:
            raw = archive.read(MANIFEST_PATH)
        except KeyError as exc:
            raise FileNotFoundError(f"{path.name} missing {MANIFEST_PATH}") from exc
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} manifest must be a JSON object")
    return payload


def normalize_priority(value: Any) -> str:
    priority = str(value or "Low").strip()
    if priority not in PRIORITY_ORDER:
        return "Low"
    return priority


def normalize_succession(manifest: Dict[str, Any]) -> str:
    succession = manifest.get("succession", "versioning")

    if isinstance(succession, str):
        mode = succession.strip().lower()
    elif isinstance(succession, dict):
        mode = str(succession.get("mode", "versioning")).strip().lower()
    else:
        mode = "versioning"

    if mode in {"supersede", "supersedes", "superseding"}:
        return "supersede"

    return "versioning"


def normalize_family(manifest: Dict[str, Any]) -> str:
    succession = manifest.get("succession", {})
    if isinstance(succession, dict) and succession.get("family"):
        return str(succession["family"])

    if manifest.get("bundle_family"):
        return str(manifest["bundle_family"])

    return str(manifest.get("bundle_id", "unknown"))


def load_queued_bundle(path: Path) -> QueuedBundle:
    manifest = read_manifest_from_zip(path)

    bundle_id = str(manifest.get("bundle_id", path.stem))
    bundle_version = str(manifest.get("bundle_version", "0"))
    target_repo = str(manifest.get("target_repo", "any"))
    priority = normalize_priority(manifest.get("priority"))
    succession_mode = normalize_succession(manifest)
    family = normalize_family(manifest)

    return QueuedBundle(
        path=path,
        manifest=manifest,
        bundle_id=bundle_id,
        bundle_version=bundle_version,
        target_repo=target_repo,
        priority=priority,
        succession_mode=succession_mode,
        family=family,
        created_sort=path.stat().st_mtime,
    )


def sort_key(bundle: QueuedBundle) -> Tuple[int, Tuple[int, ...], float, str]:
    return (
        PRIORITY_ORDER[bundle.priority],
        parse_semverish(bundle.bundle_version),
        bundle.created_sort,
        bundle.path.name,
    )


def plan_incoming_bundles(incoming_dir: Path) -> Dict[str, Any]:
    """Plan incoming bundle processing.

    Rules:
      1. Priority order: Critical, Medium, Low, NonCritical.
      2. Within same priority, versioning mode processes oldest version to newest.
      3. Within same priority and version, chronology is oldest file timestamp to newest.
      4. Supersede mode removes older queued versions in the same family.
    """
    zip_paths = sorted(incoming_dir.glob("*.zip"))
    loaded: List[QueuedBundle] = []
    failed_to_read: List[Dict[str, str]] = []

    for path in zip_paths:
        try:
            loaded.append(load_queued_bundle(path))
        except Exception as exc:
            failed_to_read.append({
                "path": path.as_posix(),
                "error": str(exc),
            })

    superseding_families: Dict[str, QueuedBundle] = {}

    for bundle in loaded:
        if bundle.succession_mode != "supersede":
            continue

        current = superseding_families.get(bundle.family)
        if current is None:
            superseding_families[bundle.family] = bundle
            continue

        current_key = (
            PRIORITY_ORDER[current.priority],
            parse_semverish(current.bundle_version),
            current.created_sort,
        )
        candidate_key = (
            PRIORITY_ORDER[bundle.priority],
            parse_semverish(bundle.bundle_version),
            bundle.created_sort,
        )

        # Higher priority wins. For same priority, newest version wins. For same
        # version, newest arrival wins as the superseding declaration.
        if (
            PRIORITY_ORDER[bundle.priority] < PRIORITY_ORDER[current.priority]
            or (
                PRIORITY_ORDER[bundle.priority] == PRIORITY_ORDER[current.priority]
                and parse_semverish(bundle.bundle_version) > parse_semverish(current.bundle_version)
            )
            or (
                PRIORITY_ORDER[bundle.priority] == PRIORITY_ORDER[current.priority]
                and parse_semverish(bundle.bundle_version) == parse_semverish(current.bundle_version)
                and bundle.created_sort > current.created_sort
            )
        ):
            superseding_families[bundle.family] = bundle

    superseded_paths = set()

    for family, winner in superseding_families.items():
        for bundle in loaded:
            if bundle.family != family:
                continue
            if bundle.path == winner.path:
                continue
            superseded_paths.add(bundle.path)

    process = [
        bundle for bundle in loaded
        if bundle.path not in superseded_paths
    ]
    process = sorted(process, key=sort_key)

    superseded = [
        bundle for bundle in loaded
        if bundle.path in superseded_paths
    ]
    superseded = sorted(superseded, key=sort_key)

    return {
        "schema": "stegverse_core_lite_bundle_queue_plan.v1",
        "incoming_dir": incoming_dir.as_posix(),
        "priority_order": ["Critical", "Medium", "Low", "NonCritical"],
        "process": [bundle_to_dict(bundle) for bundle in process],
        "superseded": [bundle_to_dict(bundle) for bundle in superseded],
        "failed_to_read": failed_to_read,
        "counts": {
            "process": len(process),
            "superseded": len(superseded),
            "failed_to_read": len(failed_to_read),
            "total_zip_files": len(zip_paths),
        },
    }


def bundle_to_dict(bundle: QueuedBundle) -> Dict[str, Any]:
    return {
        "path": bundle.path.as_posix(),
        "name": bundle.path.name,
        "bundle_id": bundle.bundle_id,
        "bundle_version": bundle.bundle_version,
        "target_repo": bundle.target_repo,
        "priority": bundle.priority,
        "succession_mode": bundle.succession_mode,
        "family": bundle.family,
        "version_sort": list(parse_semverish(bundle.bundle_version)),
        "created_sort": bundle.created_sort,
    }
