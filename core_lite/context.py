from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional


def _remote_repo_from_git(repo_root: Path) -> Optional[str]:
    try:
        completed = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None

    remote = completed.stdout.strip()
    if not remote:
        return None

    if remote.endswith(".git"):
        remote = remote[:-4]

    if "github.com/" in remote:
        return remote.split("github.com/", 1)[1].replace(":", "/").strip("/")

    if remote.startswith("git@github.com:"):
        return remote.split("git@github.com:", 1)[1].strip("/")

    return None


def detect_context(repo_root: Path) -> Dict[str, str]:
    repository = os.environ.get("GITHUB_REPOSITORY") or _remote_repo_from_git(repo_root) or "unknown/unknown"

    if "/" in repository:
        org, repo = repository.split("/", 1)
    else:
        org, repo = "unknown", repository

    return {
        "repository": repository,
        "org": org,
        "repo": repo,
        "repo_root": str(repo_root),
        "event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "sha": os.environ.get("GITHUB_SHA", ""),
        "actor": os.environ.get("GITHUB_ACTOR", ""),
    }
