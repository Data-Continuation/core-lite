#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from validate_evidence_intake import (
    VERSION as VALIDATOR_VERSION,
    load_json,
    stable_hash,
    validate_chronology,
    validate_intake,
    validate_matrix,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "receipts" / "evidence_intake_validation.receipt.json"

SOURCE_PATHS = [
    "schemas/evidence_intake.schema.json",
    "schemas/claim_chronology.schema.json",
    "schemas/evidence_matrix.schema.json",
    "fixtures/toyota_tundra_case.intake.json",
    "fixtures/toyota_tundra_case.chronology.json",
    "fixtures/toyota_tundra_case.evidence_matrix.json",
    "fixtures/invalid_privacy_violation.intake.json",
    "fixtures/invalid_unsupported_conclusion.intake.json",
    "fixtures/invalid_missing_classification.intake.json",
    "tools/validate_evidence_intake.py",
    "tools/run_evidence_intake_suite.py",
    "tests/test_evidence_intake.py",
]

CASES = [
    ("valid_intake", "fixtures/toyota_tundra_case.intake.json", validate_intake, "PASS"),
    ("valid_chronology", "fixtures/toyota_tundra_case.chronology.json", validate_chronology, "PASS"),
    ("valid_matrix", "fixtures/toyota_tundra_case.evidence_matrix.json", validate_matrix, "PASS"),
    ("privacy_violation", "fixtures/invalid_privacy_violation.intake.json", validate_intake, "FAIL_CLOSED"),
    ("unsupported_conclusion", "fixtures/invalid_unsupported_conclusion.intake.json", validate_intake, "FAIL_CLOSED"),
    ("missing_classification", "fixtures/invalid_missing_classification.intake.json", validate_intake, "FAIL_CLOSED"),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> int:
    missing = [relative for relative in SOURCE_PATHS if not (ROOT / relative).is_file()]
    if missing:
        print(json.dumps({"result": "FAIL_CLOSED", "missing_sources": missing}, indent=2))
        return 2

    case_results: list[dict[str, Any]] = []
    suite_pass = True
    for case_id, relative, validator, expected in CASES:
        report = validator(load_json(ROOT / relative))
        observed = report.get("result")
        matched = observed == expected
        suite_pass = suite_pass and matched
        case_results.append(
            {
                "case_id": case_id,
                "path": relative,
                "expected_result": expected,
                "observed_result": observed,
                "matched": matched,
                "receipt_digest": report.get("receipt_digest"),
            }
        )

    source_hashes = {relative: sha256_file(ROOT / relative) for relative in SOURCE_PATHS}
    core = {
        "receipt_type": "core_lite.evidence_intake_validation",
        "receipt_version": "1.0",
        "validator_version": VALIDATOR_VERSION,
        "result": "PASS" if suite_pass else "FAIL_CLOSED",
        "completeness_posture": "INCOMPLETE",
        "test_command": "python -m unittest discover -s tests && python tools/run_evidence_intake_suite.py",
        "source_commit": git_value("rev-parse", "HEAD"),
        "source_branch": git_value("rev-parse", "--abbrev-ref", "HEAD"),
        "source_hashes": source_hashes,
        "case_results": case_results,
        "claim_posture_upgraded": False,
        "legal_conclusion_emitted": False,
        "safety_conclusion_emitted": False,
        "recall_applicability_determined": False,
        "private_evidence_included": False,
        "prior_receipt": None,
    }
    receipt = {**core, "receipt_digest": stable_hash(core)}
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if suite_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
