#!/usr/bin/env python3
"""Build or verify a read-only Site status contract for the reference loop."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "core_lite/reference_loop_state.json"
RECEIPT_CONTRACT = ROOT / "reports/reference_loop_receipt_contract.json"
REPORT = ROOT / "reports/reference_loop_site_status.json"


class SiteStatusError(ValueError):
    pass


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SiteStatusError(f"JSON root must be an object: {path}")
    return value


def status_for(state: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    tasks = state.get("tasks")
    if not isinstance(tasks, dict) or not tasks:
        raise SiteStatusError("reference-loop task state is missing")
    required = [f"REF-LOOP-{index:03d}" for index in range(1, 9)]
    incomplete = sorted(task_id for task_id in required if tasks.get(task_id, {}).get("status") != "complete")
    if incomplete:
        raise SiteStatusError(f"incomplete tasks: {incomplete}")
    if contract.get("decision") != "RECEIPT_CONTRACT_VERIFIED":
        raise SiteStatusError("receipt contract is not verified")
    if contract.get("authority", {}).get("external_repository_mutation") is not False:
        raise SiteStatusError("receipt contract authority is not read-only")
    completed = required
    payload = {
        "schema": "stegverse.core_lite.site_status_contract.v1",
        "source_repository": "Data-Continuation/core-lite",
        "target_repository": "StegVerse-Labs/Site",
        "relationship": "verified_status_surface_contract",
        "completed_tasks": completed,
        "completed_task_count": len(completed),
        "receipt_chain_head": contract["chain_head"],
        "receipt_chain_sha256": contract["chain_sha256"],
        "reference_state_sha256": digest(state),
        "authority": {
            "read_only_status": True,
            "publication_authorized": False,
            "site_control_authorized": False,
            "external_repository_mutation": False,
            "production_mutation": False,
        },
        "decision": "SITE_STATUS_CONTRACT_VERIFIED",
        "manual_actions_required": [],
    }
    return payload


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--receipt-contract", type=Path, default=RECEIPT_CONTRACT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        expected = status_for(load_json(args.state), load_json(args.receipt_contract))
        if args.verify:
            observed = load_json(args.report)
            if observed != expected:
                raise SiteStatusError("Site status contract does not match verified state")
        else:
            write_json(args.report, expected)
    except (OSError, json.JSONDecodeError, SiteStatusError, KeyError) as exc:
        print(json.dumps({"decision": "DENY_SITE_STATUS_CONTRACT", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"decision": expected["decision"], "completed_task_count": expected["completed_task_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
