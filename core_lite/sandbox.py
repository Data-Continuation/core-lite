from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


PROTECTED_PREFIXES = (
    ".github/workflows/",
    "github/workflows/",
    ".stegverse/",
    "iosnoperiod/github/workflows/",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_sandbox(bundle_dir: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    root = Path(bundle_dir)
    errors: list[str] = []
    evaluated: list[dict[str, Any]] = []
    protected_paths: list[str] = []
    missing_declared_paths: list[str] = []

    declared_paths = manifest.get("declared_paths", [])
    if not isinstance(declared_paths, list):
        declared_paths = []

    for item in declared_paths:
        if not isinstance(item, dict):
            errors.append("declared path entry is not an object")
            continue

        rel = str(item.get("path", "")).strip()
        if not rel:
            errors.append("declared path is empty")
            continue

        if rel.startswith(PROTECTED_PREFIXES):
            protected_paths.append(rel)

        candidate = root / rel
        if not candidate.exists() or not candidate.is_file():
            missing_declared_paths.append(rel)
            continue

        evaluated.append(
            {
                "path": rel,
                "size": candidate.stat().st_size,
                "sha256": sha256_file(candidate),
                "action": item.get("action", "sandbox_only"),
                "type": item.get("type", "candidate_file"),
                "protected": rel.startswith(PROTECTED_PREFIXES),
            }
        )

    return {
        "schema": "stegverse_core_lite_sandbox_result.v1",
        "success": not errors and not missing_declared_paths,
        "install_performed": False,
        "evaluated_file_count": len(evaluated),
        "evaluated_files": evaluated,
        "protected_paths": protected_paths,
        "missing_declared_paths": missing_declared_paths,
        "errors": errors,
        "boundary": [
            "Sandbox evaluated declared files only.",
            "Sandbox did not install.",
            "Sandbox did not execute candidate files.",
            "Founder/operator review remains required.",
        ],
    }
