#!/usr/bin/env python3
"""Refresh and verify terminal read-only Reference Loop contracts."""
from __future__ import annotations

import json
from pathlib import Path

from build_reference_loop_receipt_contract import contract_for, load_chain, write_report as write_receipt_report
from build_reference_loop_site_status import load_json as load_site_json, status_for, write_json
from build_reference_loop_portability_manifest import manifest_for, write_report as write_portability_report

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts/reference_loop_receipts.jsonl"
STATE = ROOT / "core_lite/reference_loop_state.json"
RECEIPT_REPORT = ROOT / "reports/reference_loop_receipt_contract.json"
SITE_REPORT = ROOT / "reports/reference_loop_site_status.json"
PORTABILITY_REPORT = ROOT / "reports/reference_loop_portability_manifest.json"

def refresh() -> dict:
    receipts = load_chain(RECEIPTS)
    receipt_contract = contract_for(receipts)
    write_receipt_report(RECEIPT_REPORT, receipt_contract)

    state = load_site_json(STATE)
    site_status = status_for(state, receipt_contract)
    write_json(SITE_REPORT, site_status)

    portability = manifest_for(state, receipt_contract, site_status)
    write_portability_report(PORTABILITY_REPORT, portability)

    # Deterministic second pass: compare all three against recomputed values.
    observed_receipt = load_site_json(RECEIPT_REPORT)
    observed_site = load_site_json(SITE_REPORT)
    observed_portability = load_site_json(PORTABILITY_REPORT)
    if observed_receipt != contract_for(load_chain(RECEIPTS)):
        raise ValueError("receipt contract verification mismatch")
    if observed_site != status_for(load_site_json(STATE), observed_receipt):
        raise ValueError("site status verification mismatch")
    if observed_portability != manifest_for(load_site_json(STATE), observed_receipt, observed_site):
        raise ValueError("portability manifest verification mismatch")

    return {
        "decision": "TERMINAL_PORTABILITY_CONTRACTS_VERIFIED",
        "completed_reference_tasks": portability["completed_tasks"],
        "receipt_chain_head": receipt_contract["chain_head"],
        "attempt_count": receipt_contract["attempt_count"],
        "failed_closed_attempt_count": receipt_contract["failed_closed_attempt_count"],
        "target_repository": portability["target_repository"],
        "authority_effect": "NONE",
        "manual_actions_required": [],
    }

def main() -> int:
    try:
        result = refresh()
    except Exception as exc:
        print(json.dumps({"decision": "DENY_TERMINAL_PORTABILITY_REFRESH", "error": str(exc), "authority_effect": "NONE"}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
