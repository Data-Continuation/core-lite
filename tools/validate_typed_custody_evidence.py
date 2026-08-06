#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = {"file_digest", "record_self_hash", "canonical_object_digest", "git_object_id", "external_artifact"}


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "typed_custody_evidence_chain":
        errors.append("record_type")
    for key in ("source_repository", "destination_repository"):
        if not REPOSITORY.fullmatch(str(record.get(key, ""))):
            errors.append(key)
    boundary = record.get("authority_boundary")
    if not isinstance(boundary, dict) or not boundary or any(value is not False for value in boundary.values()):
        errors.append("authority_boundary")

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence")
        evidence = []

    blocked = False
    for index, item in enumerate(evidence, start=1):
        kind = item.get("type")
        if kind not in ALLOWED:
            errors.append(f"evidence[{index}].type")
            continue
        if not REPOSITORY.fullmatch(str(item.get("repository", ""))):
            errors.append(f"evidence[{index}].repository")
        if kind in {"file_digest", "record_self_hash", "canonical_object_digest"}:
            if not HEX64.fullmatch(str(item.get("value", ""))):
                errors.append(f"evidence[{index}].sha256")
        if kind == "record_self_hash" and not item.get("field"):
            errors.append(f"evidence[{index}].field")
        if kind == "git_object_id":
            if item.get("object_kind") not in {"commit", "blob"}:
                errors.append(f"evidence[{index}].object_kind")
            if not HEX40.fullmatch(str(item.get("value", ""))):
                errors.append(f"evidence[{index}].git_object_id")
        if kind == "external_artifact":
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(item.get("digest", ""))):
                errors.append(f"evidence[{index}].digest")
            availability = item.get("availability")
            mirrored = availability == "MIRRORED" and item.get("mirror_status") == "REPOSITORY_RESIDENT"
            if mirrored:
                required = ("mirror_repository", "mirror_path", "mirror_commit", "mirror_hash")
                if not all(item.get(key) for key in required):
                    errors.append(f"evidence[{index}].mirror_metadata")
                if not REPOSITORY.fullmatch(str(item.get("mirror_repository", ""))):
                    errors.append(f"evidence[{index}].mirror_repository")
                if not HEX40.fullmatch(str(item.get("mirror_commit", ""))):
                    errors.append(f"evidence[{index}].mirror_commit")
                if not HEX64.fullmatch(str(item.get("mirror_hash", ""))):
                    errors.append(f"evidence[{index}].mirror_hash")
            else:
                try:
                    expired = _time(str(item.get("expires_at"))) <= datetime.now(timezone.utc)
                except Exception:
                    expired = True
                    errors.append(f"evidence[{index}].expires_at")
                if item.get("required_for_decision") is True and (availability in {"EXPIRED", "UNAVAILABLE"} or expired):
                    blocked = True

    if errors:
        return {"decision": "REVIEW_REQUIRED", "errors": errors, "next_task": "CORRECT_TYPED_CUSTODY_EVIDENCE"}
    if blocked:
        return {"decision": "BLOCKED", "errors": [], "next_task": "RESTORE_OR_MIRROR_REQUIRED_EVIDENCE"}
    return {"decision": "COMPLETE", "errors": [], "next_task": "PORTABILITY_CONTRACT_INTEGRATION", "authority_effect": "NONE"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError("record must be an object")
        result = validate(record)
    except Exception as exc:
        result = {"decision": "FAILED", "errors": [f"invalid_input:{type(exc).__name__}"], "next_task": "REVIEW_REQUIRED"}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["decision"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
