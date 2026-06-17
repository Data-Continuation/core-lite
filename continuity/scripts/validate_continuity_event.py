#!/usr/bin/env python3
"""Validate the required fields for a continuity event JSON file."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "schema",
    "event_id",
    "event_type",
    "source_path",
    "source_sha256",
    "created_at_utc",
    "actor",
    "disposition",
    "evidence_ref",
]

SHA_RE = re.compile(r"^sha256:[a-fA-F0-9]{64}$")
ALLOWED_DISPOSITIONS = {"observed", "accepted_for_review", "incomplete", "isolated"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED:
        if key not in data or data[key] in ("", None):
            errors.append(f"missing:{key}")
    if data.get("schema") != "stegverse.continuity_event.v1":
        errors.append("invalid:schema")
    if "source_sha256" in data and not SHA_RE.match(str(data["source_sha256"])):
        errors.append("invalid:source_sha256")
    if "disposition" in data and data["disposition"] not in ALLOWED_DISPOSITIONS:
        errors.append("invalid:disposition")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("continuity/examples/continuity_event.example.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)
    result = {
        "schema": "stegverse.continuity_event.validation_result.v1",
        "path": str(path),
        "status": "ok" if not errors else "failed",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
