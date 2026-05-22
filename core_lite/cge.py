from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROTECTED_PREFIXES = (
    ".github/workflows/",
    "github/workflows/",
    ".stegverse/",
    "iosnoperiod/github/workflows/",
)

FORBIDDEN_ACTIONS = {"install", "execute", "deploy", "promote", "self_accredit"}


@dataclass(frozen=True)
class CGEDecision:
    decision: str
    basis: str
    severity: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "basis": self.basis,
            "severity": self.severity,
            "details": self.details,
        }


def _declared_paths(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    paths = manifest.get("declared_paths")
    if not isinstance(paths, list):
        return []
    return [p for p in paths if isinstance(p, dict)]


def precheck_manifest(manifest: dict[str, Any]) -> CGEDecision:
    required = ["schema", "bundle_id", "purpose", "actor", "declared_paths"]
    missing = [key for key in required if not manifest.get(key)]
    if missing:
        return CGEDecision(
            decision="FAIL_CLOSED",
            basis="bundle manifest missing required fields",
            severity="high",
            details={"missing": missing},
        )

    declared_paths = _declared_paths(manifest)
    if not declared_paths:
        return CGEDecision(
            decision="FAIL_CLOSED",
            basis="bundle manifest has no declared paths",
            severity="high",
            details={},
        )

    forbidden = []
    protected = []
    for item in declared_paths:
        path = str(item.get("path", "")).strip()
        action = str(item.get("action", "sandbox_only")).strip().lower()
        if not path:
            forbidden.append({"path": path, "reason": "empty path"})
        if action in FORBIDDEN_ACTIONS:
            forbidden.append({"path": path, "reason": f"forbidden action: {action}"})
        if path.startswith(PROTECTED_PREFIXES):
            protected.append(path)

    if forbidden:
        return CGEDecision(
            decision="DENY",
            basis="bundle declares forbidden actions or invalid paths",
            severity="high",
            details={"forbidden": forbidden, "protected": protected},
        )

    if protected:
        return CGEDecision(
            decision="REVIEW_REQUIRED",
            basis="bundle touches protected paths and may only be reviewed in sandbox",
            severity="medium",
            details={"protected": protected},
        )

    return CGEDecision(
        decision="ALLOW_SANDBOX",
        basis="bundle manifest is admissible for sandbox evaluation only",
        severity="low",
        details={"declared_path_count": len(declared_paths)},
    )


def classify_sandbox_result(result: dict[str, Any]) -> CGEDecision:
    if not result.get("success"):
        return CGEDecision(
            decision="FAIL_CLOSED",
            basis="sandbox result indicates failure",
            severity="high",
            details={"errors": result.get("errors", [])},
        )

    protected = result.get("protected_paths", [])
    missing = result.get("missing_declared_paths", [])
    if missing:
        return CGEDecision(
            decision="FAIL_CLOSED",
            basis="sandbox could not find all declared paths",
            severity="high",
            details={"missing_declared_paths": missing},
        )

    if protected:
        return CGEDecision(
            decision="REVIEW_REQUIRED",
            basis="sandbox detected protected paths; no installation authority granted",
            severity="medium",
            details={"protected_paths": protected},
        )

    return CGEDecision(
        decision="REVIEW_REQUIRED",
        basis="sandbox completed; founder/operator review required before any install gate",
        severity="low",
        details={
            "evaluated_file_count": result.get("evaluated_file_count", 0),
            "install_authority": False,
        },
    )
