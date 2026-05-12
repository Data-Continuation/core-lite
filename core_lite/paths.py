from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_join(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    root_resolved = root.resolve()
    if root_resolved != target and root_resolved not in target.parents:
        raise ValueError(f"path escapes repo root: {relative}")
    return target
