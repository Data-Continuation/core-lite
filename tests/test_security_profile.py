from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.validate_security_profile import validate

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "fixtures" / "security_profile.federal_plus.json"


class SecurityProfileTests(unittest.TestCase):
    def load(self):
        return json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_federal_plus_profile_passes_but_release_remains_blocked(self):
        report = validate(self.load())
        self.assertEqual("PASS", report["result"])
        self.assertEqual("BLOCKED", report["release_readiness"])
        self.assertIn("INDEPENDENT_REPRODUCTION", report["blocking_controls"])

    def test_compliance_claim_fails_closed(self):
        doc = self.load()
        doc["compliance_claim"] = "FISMA_COMPLIANT"
        self.assertEqual("FAIL_CLOSED", validate(doc)["result"])

    def test_missing_required_control_fails_closed(self):
        doc = self.load()
        doc["controls"] = [c for c in doc["controls"] if c["control_id"] != "AUTHORITY_NON_MINTING"]
        self.assertEqual("FAIL_CLOSED", validate(doc)["result"])

    def test_release_gate_cannot_be_relaxed(self):
        doc = self.load()
        doc["release_gate"]["requires_independent_reproduction"] = False
        self.assertEqual("FAIL_CLOSED", validate(doc)["result"])

    def test_digest_changes_with_control_change(self):
        first = validate(self.load())["receipt_digest"]
        changed = copy.deepcopy(self.load())
        changed["controls"][0]["status"] = "blocked"
        second = validate(changed)["receipt_digest"]
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
