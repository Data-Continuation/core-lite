from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "tools" / "validate_evidence_intake.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def load(name: str):
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


class EvidenceIntakeTests(unittest.TestCase):
    def test_valid_incomplete_intake(self):
        report = validator.validate_intake(load("toyota_tundra_case.intake.json"))
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["completeness"], "INCOMPLETE")

    def test_missing_classification_fails_closed(self):
        report = validator.validate_intake(load("invalid_missing_classification.intake.json"))
        self.assertEqual(report["result"], "FAIL_CLOSED")

    def test_privacy_violation_fails_closed(self):
        report = validator.validate_intake(load("invalid_privacy_violation.intake.json"))
        self.assertEqual(report["result"], "FAIL_CLOSED")
        self.assertTrue(any("prohibited private field" in error for error in report["errors"]))

    def test_unsupported_conclusion_fails_closed(self):
        report = validator.validate_intake(load("invalid_unsupported_conclusion.intake.json"))
        self.assertEqual(report["result"], "FAIL_CLOSED")

    def test_contradiction_is_preserved(self):
        doc = load("toyota_tundra_case.intake.json")
        doc["assertions"][0]["verification_state"] = "contradicted"
        report = validator.validate_intake(doc)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["completeness"], "INCOMPLETE")

    def test_chronology_order_is_deterministic(self):
        doc = load("toyota_tundra_case.chronology.json")
        self.assertEqual(validator.validate_chronology(doc)["result"], "PASS")
        changed = copy.deepcopy(doc)
        changed["events"] = list(reversed(changed["events"]))
        self.assertEqual(validator.validate_chronology(changed)["result"], "FAIL_CLOSED")

    def test_receipt_digest_is_deterministic(self):
        doc = load("toyota_tundra_case.intake.json")
        self.assertEqual(
            validator.validate_intake(doc)["receipt_digest"],
            validator.validate_intake(copy.deepcopy(doc))["receipt_digest"],
        )

    def test_changed_evidence_changes_digest(self):
        doc = load("toyota_tundra_case.intake.json")
        changed = copy.deepcopy(doc)
        changed["assertions"][0]["text"] += " Changed."
        self.assertNotEqual(
            validator.validate_intake(doc)["receipt_digest"],
            validator.validate_intake(changed)["receipt_digest"],
        )

    def test_verification_does_not_upgrade_claim_posture(self):
        doc = load("toyota_tundra_case.intake.json")
        doc["assertions"][0]["verification_state"] = "verified"
        report = validator.validate_intake(doc)
        self.assertEqual(report["claim_posture"], "POTENTIAL")

    def test_matrix_remains_incomplete(self):
        report = validator.validate_matrix(load("toyota_tundra_case.evidence_matrix.json"))
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["completeness"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
