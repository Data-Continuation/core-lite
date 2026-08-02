#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

VERSION = "1.0.0"
PRIVATE_KEYS = {
    "vin", "vehicle_identification_number", "address", "signature",
    "account_number", "driver_license", "social_security_number",
}
ALLOWED_CLASSIFICATIONS = {"observation", "representation", "inference", "hypothesis", "verified_fact"}
ALLOWED_VERIFICATION = {"unverified", "pending", "verified", "contradicted", "inaccessible"}
FORBIDDEN_CONCLUSION_TYPES = {"legal", "safety", "recall_applicability", "liability", "damages", "entitlement"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def walk_keys(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{prefix}.{key}"
            found.append((here, str(key).lower()))
            found.extend(walk_keys(child, here))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_keys(child, f"{prefix}[{index}]"))
    return found


def validate_intake(doc: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(doc, dict):
        return {"result": "FAIL_CLOSED", "completeness": "INVALID", "errors": ["root must be an object"], "warnings": []}

    required = [
        "schema_version", "record_id", "record_type", "subject_class", "status",
        "claim_posture", "assertions", "ownership", "privacy", "permitted_continuation",
    ]
    for field in required:
        if field not in doc:
            errors.append(f"missing required field: {field}")

    if doc.get("schema_version") != "1.0":
        errors.append("schema_version must equal 1.0")
    if doc.get("record_type") != "evidence_intake":
        errors.append("record_type must equal evidence_intake")

    assertions = doc.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        errors.append("assertions must be a non-empty list")
        assertions = []

    seen_ids: set[str] = set()
    verified_count = 0
    unresolved_count = 0
    for index, item in enumerate(assertions):
        if not isinstance(item, dict):
            errors.append(f"assertions[{index}] must be an object")
            continue
        for field in ("id", "classification", "text", "provenance", "verification_state"):
            if field not in item:
                errors.append(f"assertions[{index}] missing required field: {field}")
        assertion_id = item.get("id")
        if isinstance(assertion_id, str):
            if assertion_id in seen_ids:
                errors.append(f"duplicate assertion id: {assertion_id}")
            seen_ids.add(assertion_id)
        classification = item.get("classification")
        if classification not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"assertions[{index}] invalid classification: {classification!r}")
        state = item.get("verification_state")
        if state not in ALLOWED_VERIFICATION:
            errors.append(f"assertions[{index}] invalid verification_state: {state!r}")
        elif state == "verified":
            verified_count += 1
            if classification != "verified_fact":
                warnings.append(f"assertions[{index}] verified evidence does not automatically change classification")
        else:
            unresolved_count += 1
        if classification == "verified_fact" and state != "verified":
            errors.append(f"assertions[{index}] verified_fact requires verification_state=verified")

    privacy = doc.get("privacy")
    publication_class = privacy.get("publication_class") if isinstance(privacy, dict) else None
    if publication_class not in {"public_safe", "private", "restricted"}:
        errors.append("privacy.publication_class is invalid")
    if publication_class == "public_safe":
        for path, key in walk_keys(doc):
            if key in PRIVATE_KEYS:
                errors.append(f"public_safe record contains prohibited private field at {path}")

    conclusions = doc.get("conclusions", [])
    if not isinstance(conclusions, list):
        errors.append("conclusions must be a list")
        conclusions = []
    for index, conclusion in enumerate(conclusions):
        if not isinstance(conclusion, dict):
            errors.append(f"conclusions[{index}] must be an object")
            continue
        conclusion_type = conclusion.get("type")
        support = conclusion.get("support_state")
        if conclusion_type in FORBIDDEN_CONCLUSION_TYPES and support != "supported":
            errors.append(f"unsupported {conclusion_type} conclusion is prohibited")
        if support == "supported" and verified_count == 0:
            errors.append(f"conclusions[{index}] cannot be supported without verified assertions")

    if doc.get("claim_posture") == "SUPPORTED" and verified_count == 0:
        errors.append("claim_posture cannot be SUPPORTED without verified assertions")

    if errors:
        result, completeness = "FAIL_CLOSED", "INVALID"
    elif unresolved_count:
        result, completeness = "PASS", "INCOMPLETE"
    else:
        result, completeness = "PASS", "COMPLETE"

    core = {
        "validator": "evidence_intake",
        "validator_version": VERSION,
        "record_id": doc.get("record_id"),
        "result": result,
        "completeness": completeness,
        "claim_posture": doc.get("claim_posture"),
        "assertion_count": len(assertions),
        "verified_assertion_count": verified_count,
        "unresolved_assertion_count": unresolved_count,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
        "source_digest": stable_hash(doc),
    }
    return {**core, "receipt_digest": stable_hash(core)}


def validate_chronology(doc: Any) -> dict[str, Any]:
    errors: list[str] = []
    events = doc.get("events") if isinstance(doc, dict) else None
    if not isinstance(events, list):
        errors.append("events must be a list")
        events = []
    sequences = [event.get("sequence") for event in events if isinstance(event, dict)]
    if any(not isinstance(value, int) or value < 1 for value in sequences):
        errors.append("event sequence values must be positive integers")
    if len(sequences) != len(set(sequences)):
        errors.append("event sequence values must be unique")
    if sequences != sorted(sequences):
        errors.append("events must be ordered by sequence")
    core = {
        "validator": "claim_chronology",
        "validator_version": VERSION,
        "record_id": doc.get("record_id") if isinstance(doc, dict) else None,
        "result": "PASS" if not errors else "FAIL_CLOSED",
        "errors": sorted(errors),
        "source_digest": stable_hash(doc),
    }
    return {**core, "receipt_digest": stable_hash(core)}


def validate_matrix(doc: Any) -> dict[str, Any]:
    errors: list[str] = []
    questions = doc.get("questions") if isinstance(doc, dict) else None
    if not isinstance(questions, list):
        errors.append("questions must be a list")
        questions = []
    valid_status = {"missing", "pending", "supporting", "contradictory", "inaccessible", "resolved"}
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            errors.append(f"questions[{index}] must be an object")
            continue
        for field in ("question_id", "question", "status", "evidence_refs", "owner"):
            if field not in question:
                errors.append(f"questions[{index}] missing required field: {field}")
        if question.get("status") not in valid_status:
            errors.append(f"questions[{index}] invalid status")
    unresolved = sum(1 for q in questions if isinstance(q, dict) and q.get("status") in {"missing", "pending", "contradictory", "inaccessible"})
    core = {
        "validator": "evidence_matrix",
        "validator_version": VERSION,
        "record_id": doc.get("record_id") if isinstance(doc, dict) else None,
        "result": "PASS" if not errors else "FAIL_CLOSED",
        "completeness": "INCOMPLETE" if unresolved else "COMPLETE",
        "unresolved_question_count": unresolved,
        "errors": sorted(errors),
        "source_digest": stable_hash(doc),
    }
    return {**core, "receipt_digest": stable_hash(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--kind", choices=("intake", "chronology", "matrix"), default="intake")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    doc = load_json(args.path)
    report = {"intake": validate_intake, "chronology": validate_chronology, "matrix": validate_matrix}[args.kind](doc)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
