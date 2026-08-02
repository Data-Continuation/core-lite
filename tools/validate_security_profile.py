#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_REFERENCES = {
    "NIST-SP-800-53r5-release-5.2.0",
    "NIST-SP-800-218-v1.1",
    "FIPS-140-3",
    "CISA-SECURE-BY-DESIGN",
}
REQUIRED_CONTROLS = {
    "AC_LEAST_PRIVILEGE",
    "IA_PHISHING_RESISTANT_MFA",
    "SC_ENCRYPT_TRANSIT",
    "SC_ENCRYPT_REST",
    "CRYPTO_FIPS_BOUNDARY",
    "AU_TAMPER_EVIDENT",
    "CM_PROTECTED_CHANGE",
    "SSDF_DEPENDENCY_INTEGRITY",
    "SSDF_NEGATIVE_TESTS",
    "PRIVACY_MINIMIZATION",
    "AUTHORITY_NON_MINTING",
    "RECOVERY_TESTED",
    "CLAIM_EXPIRATION",
    "INDEPENDENT_REPRODUCTION",
}
VALID_ENFORCEMENT = {"fail_closed", "release_block", "deployment_block"}
VALID_STATUS = {"implemented", "pending_validation", "deployment_conditional", "blocked"}


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(doc: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(doc, dict):
        return {"result": "FAIL_CLOSED", "errors": ["root must be an object"], "warnings": []}

    if doc.get("schema_version") != "1.0":
        errors.append("schema_version must equal 1.0")
    if doc.get("assurance_posture") != "federal_plus":
        errors.append("assurance_posture must equal federal_plus")
    if doc.get("compliance_claim") != "NONE":
        errors.append("compliance_claim must remain NONE")

    refs = doc.get("baseline_references", [])
    found_refs = {item.get("id") for item in refs if isinstance(item, dict)}
    missing_refs = sorted(REQUIRED_REFERENCES - found_refs)
    if missing_refs:
        errors.append("missing baseline references: " + ", ".join(missing_refs))

    controls = doc.get("controls", [])
    if not isinstance(controls, list):
        errors.append("controls must be a list")
        controls = []
    found_controls: set[str] = set()
    for index, control in enumerate(controls):
        if not isinstance(control, dict):
            errors.append(f"controls[{index}] must be an object")
            continue
        control_id = control.get("control_id")
        if not isinstance(control_id, str) or not control_id:
            errors.append(f"controls[{index}] missing control_id")
            continue
        if control_id in found_controls:
            errors.append(f"duplicate control_id: {control_id}")
        found_controls.add(control_id)
        if control.get("enforcement") not in VALID_ENFORCEMENT:
            errors.append(f"{control_id} has invalid enforcement")
        if control.get("status") not in VALID_STATUS:
            errors.append(f"{control_id} has invalid status")
        evidence = control.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{control_id} requires evidence locations")
        if control.get("status") == "implemented" and control.get("enforcement") == "deployment_block":
            warnings.append(f"{control_id} is implemented but still deployment-scoped")

    missing_controls = sorted(REQUIRED_CONTROLS - found_controls)
    if missing_controls:
        errors.append("missing required controls: " + ", ".join(missing_controls))

    gate = doc.get("release_gate", {})
    for key in (
        "requires_commit_bound_validation",
        "requires_independent_reproduction",
        "requires_current_main_validation",
    ):
        if gate.get(key) is not True:
            errors.append(f"release_gate.{key} must be true")
    if gate.get("release_authority") != "SEPARATE_AUTHORIZATION_REQUIRED":
        errors.append("release authority must require separate authorization")

    blocking = sorted(
        control["control_id"]
        for control in controls
        if isinstance(control, dict) and control.get("status") in {"blocked", "pending_validation"}
    )
    result = "FAIL_CLOSED" if errors else "PASS"
    readiness = "BLOCKED" if errors or blocking else "READY_FOR_SEPARATE_RELEASE_REVIEW"
    core = {
        "validator": "security_profile",
        "validator_version": "1.0.0",
        "profile_id": doc.get("profile_id"),
        "result": result,
        "release_readiness": readiness,
        "blocking_controls": blocking,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
        "source_digest": stable_hash(doc),
    }
    return {**core, "receipt_digest": stable_hash(core)}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/security_profile.federal_plus.json")
    with path.open("r", encoding="utf-8") as handle:
        report = validate(json.load(handle))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
