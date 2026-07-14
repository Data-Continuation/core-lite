#!/usr/bin/env python3
"""Validate the deterministic sandbox-only RCE ingestion candidate package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "bundles" / "relationship_conditioned_execution"
ALLOWED_TARGET_ROOT = PurePosixPath("sandbox/relationship_conditioned_execution")
ORDER = {"policy": 0, "schema": 1, "validator": 2, "fixture": 3}


class BundleValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BundleValidationError(f"{path} must contain an object")
    return value


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise BundleValidationError(f"unsafe path: {value}")
    return path


def validate() -> None:
    manifest = load_json(OUT / "bundle_manifest.json")
    inventory = load_json(OUT / "source_inventory.json")
    plan = load_json(OUT / "install_plan.json")

    for record in (manifest, inventory, plan):
        if record.get("candidate_evidence_only") is not True:
            raise BundleValidationError("candidate_evidence_only must be true")
        if record.get("autonomous_execution_authority") is not False:
            raise BundleValidationError("autonomous execution authority is prohibited")

    if manifest.get("sandbox_only") is not True:
        raise BundleValidationError("bundle must be sandbox-only")
    if manifest.get("human_harm_authority") is not False:
        raise BundleValidationError("human-harm authority is prohibited")
    if manifest.get("production_destination_allowed") is not False:
        raise BundleValidationError("production destinations are prohibited")
    if plan.get("mode") != "sandbox_only" or plan.get("automatic_destination_mutation") is not False:
        raise BundleValidationError("install plan must remain non-mutating sandbox evidence")

    if hashlib.sha256(canonical_bytes(inventory)).hexdigest() != manifest.get("source_inventory_sha256"):
        raise BundleValidationError("source inventory digest mismatch")
    if hashlib.sha256(canonical_bytes(plan)).hexdigest() != manifest.get("install_plan_sha256"):
        raise BundleValidationError("install plan digest mismatch")

    files = inventory.get("files")
    operations = plan.get("operations")
    if not isinstance(files, list) or not isinstance(operations, list) or len(files) != len(operations):
        raise BundleValidationError("inventory and plan must contain matching file lists")
    if manifest.get("file_count") != len(files):
        raise BundleValidationError("manifest file count mismatch")

    last_order = -1
    for index, (record, operation) in enumerate(zip(files, operations), 1):
        if not isinstance(record, dict) or not isinstance(operation, dict):
            raise BundleValidationError("invalid file or operation record")
        if record.get("order") != index or operation.get("order") != index:
            raise BundleValidationError("non-deterministic operation order")

        kind = record.get("kind")
        if kind not in ORDER or ORDER[kind] < last_order:
            raise BundleValidationError("dependency order violation")
        last_order = ORDER[kind]

        source_value = str(record.get("source_path", ""))
        target_value = str(record.get("target_path", ""))
        source = safe_relative(source_value)
        target = safe_relative(target_value)
        if target.parts[: len(ALLOWED_TARGET_ROOT.parts)] != ALLOWED_TARGET_ROOT.parts:
            raise BundleValidationError(f"production or external target prohibited: {target_value}")
        if any(part.lower() in {"prod", "production", "live"} for part in target.parts):
            raise BundleValidationError(f"production target prohibited: {target_value}")

        path = ROOT / source
        if not path.is_file():
            raise BundleValidationError(f"missing source file: {source_value}")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if record.get("sha256") != digest or operation.get("expected_sha256") != digest:
            raise BundleValidationError(f"hash mismatch: {source_value}")
        if record.get("bytes") != len(data) or operation.get("expected_bytes") != len(data):
            raise BundleValidationError(f"size mismatch: {source_value}")
        if operation.get("source_path") != source_value or operation.get("target_path") != target_value:
            raise BundleValidationError("install plan diverges from source inventory")
        if operation.get("operation") != "copy_candidate_evidence":
            raise BundleValidationError("unsupported operation")


def main() -> int:
    validate()
    print("RCE_BUNDLE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
