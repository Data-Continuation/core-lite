#!/usr/bin/env python3
"""Validate the RCE sandbox candidate manifest and fixture set."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "core_lite" / "relationship_conditioned_execution_manifest.json"
FIXTURES_PATH = ROOT / "samples" / "relationship_conditioned_execution_sandbox_cases.json"

SAFE_IRREVERSIBLE = {"PROTECTIVE_DELAY", "ESCALATE", "ABSTAIN", "FAIL_CLOSED"}
NONVALID_AUTHORITY = {"ESCALATE", "ABSTAIN", "FAIL_CLOSED"}
REQUIRED_ROLES = {"normative_policy", "machine_readable_schema", "fail_closed_validator", "canonical_example", "acceptance_tests"}


class PackageValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise PackageValidationError(f"{path} must contain an object")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    authority = manifest.get("authority", {})
    if authority.get("candidate_evidence_only") is not True:
        raise PackageValidationError("candidate evidence boundary missing")
    if authority.get("production_install_authorized") is not False:
        raise PackageValidationError("production installation must remain unauthorized")
    if authority.get("may_execute_irreversible_human_impact") is not False:
        raise PackageValidationError("irreversible human-impact execution must be prohibited")

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise PackageValidationError("manifest files are required")

    roles = set()
    paths = []
    for item in files:
        path = item.get("path")
        blob_sha = item.get("source_blob_sha")
        role = item.get("role")
        if not isinstance(path, str) or not path:
            raise PackageValidationError("file path is required")
        if not isinstance(blob_sha, str) or len(blob_sha) != 40:
            raise PackageValidationError(f"invalid source blob hash for {path}")
        if item.get("required") is not True:
            raise PackageValidationError(f"required file not marked required: {path}")
        if not (ROOT / path).is_file():
            raise PackageValidationError(f"required source file missing: {path}")
        roles.add(role)
        paths.append(path)

    if roles != REQUIRED_ROLES:
        raise PackageValidationError("manifest role set is incomplete")
    if paths != manifest.get("dependency_order"):
        raise PackageValidationError("dependency order must match declared file order")

    integrity = manifest.get("integrity", {})
    if integrity.get("sha256_required_at_package_emission") is not True:
        raise PackageValidationError("package-time sha256 requirement missing")
    if integrity.get("byte_count_required_at_package_emission") is not True:
        raise PackageValidationError("package-time byte-count requirement missing")


def validate_fixtures(fixtures: dict[str, Any]) -> None:
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 5:
        raise PackageValidationError("at least five sandbox cases are required")

    ids = set()
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or case_id in ids:
            raise PackageValidationError("sandbox case IDs must be unique")
        ids.add(case_id)

        expected = set(case.get("expected_decisions", []))
        forbidden = set(case.get("forbidden_decisions", []))
        if not expected or not forbidden:
            raise PackageValidationError(f"case {case_id} requires expected and forbidden decisions")
        if expected & forbidden:
            raise PackageValidationError(f"case {case_id} has overlapping outcomes")

        operation = case.get("requested_operation")
        impact = case.get("human_impact")
        if operation == "execute_irreversible" or impact in {"irreversible", "self_sacrificial"}:
            if not expected.issubset(SAFE_IRREVERSIBLE):
                raise PackageValidationError(f"case {case_id} admits unsafe irreversible outcome")
            if "ALLOW" not in forbidden:
                raise PackageValidationError(f"case {case_id} must forbid ALLOW")

        if case.get("authority_state") != "valid" and not expected.issubset(NONVALID_AUTHORITY):
            raise PackageValidationError(f"case {case_id} admits action with non-valid authority")

        if case.get("collective_vote") == "execute" and "ALLOW" not in forbidden:
            raise PackageValidationError("collective vote must not override human safety")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    fixtures = load_json(FIXTURES_PATH)
    validate_manifest(manifest)
    validate_fixtures(fixtures)
    print("RCE_SANDBOX_CANDIDATE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
