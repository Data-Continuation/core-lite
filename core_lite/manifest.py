from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Dict, Any, List

try:
    from .manifest_admissibility import validate_manifest_admissibility
except ImportError:
    from manifest_admissibility import validate_manifest_admissibility


MANIFEST_PATH = ".stegverse/ingest_manifest.json"


def load_bundle_manifest(staging_root: Path) -> Dict[str, Any]:
    path = staging_root / MANIFEST_PATH
    if not path.exists():
        raise FileNotFoundError(f"bundle missing {MANIFEST_PATH}")

    manifest = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(manifest, dict):
        raise ValueError("ingest manifest must be a JSON object")

    if "files" not in manifest or not isinstance(manifest["files"], list):
        raise ValueError("ingest manifest must contain files list")

    return manifest


def declared_paths(manifest: Dict[str, Any]) -> set[str]:
    return {
        item["path"]
        for item in manifest.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def excluded_patterns(manifest: Dict[str, Any]) -> List[str]:
    patterns: List[str] = []
    for key in ["excluded_files", "excluded_runtime_artifacts"]:
        for item in manifest.get(key, []):
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                patterns.append(item["path"])
            elif isinstance(item, str):
                patterns.append(item)
    return patterns


def is_excluded(path: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def all_bundle_files(staging_root: Path) -> List[str]:
    paths: List[str] = []
    for path in staging_root.rglob("*"):
        if path.is_file():
            paths.append(path.relative_to(staging_root).as_posix())
    return sorted(paths)


def validate_manifest(
    manifest: Dict[str, Any],
    context: Dict[str, str],
    staging_root: Path,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    target = manifest.get("target_repo", "any")
    current = context["repository"]

    if target not in {"any", "*", current}:
        raise ValueError(f"manifest target_repo {target!r} does not match current repo {current!r}")

    policy = manifest.get("install_policy", {})
    fail_on_unclassified = bool(policy.get("fail_on_unclassified_files", True))

    declared = declared_paths(manifest)
    excluded = excluded_patterns(manifest)
    bundle_files = all_bundle_files(staging_root)

    allowed_special = {MANIFEST_PATH}
    unclassified = [
        path for path in bundle_files
        if path not in declared and path not in allowed_special and not is_excluded(path, excluded)
    ]

    if fail_on_unclassified and unclassified:
        raise ValueError(f"unclassified files in bundle: {unclassified}")

    admissibility = None
    if repo_root is not None:
        admissibility = validate_manifest_admissibility(repo_root, manifest, staging_root)
        report_path = repo_root / ".stegverse" / "manifest_admissibility_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(admissibility, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if not admissibility.get("success"):
            raise ValueError(f"manifest admissibility failed: {admissibility.get('errors', [])}")

    return {
        "target_repo": target,
        "current_repo": current,
        "declared_count": len(declared),
        "bundle_file_count": len(bundle_files),
        "unclassified": unclassified,
        "excluded_patterns": excluded,
        "manifest_admissibility": admissibility,
    }
