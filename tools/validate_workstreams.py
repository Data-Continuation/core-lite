#!/usr/bin/env python3
"""
Validate Core-Lite workstreams against transition blocks and generate status artifacts.

This script is intentionally small and real:
- reads core_lite/workstreams.yml
- reads core_lite/transition_blocks.yml
- validates block references
- validates required workstream fields
- writes reports/workstream_status.md
- writes reports/workstream_status.json
- appends receipts/workstream_receipts.jsonl

Hardening:
- If PyYAML is missing in CI, the script installs it once and continues.
  This prevents the repeated workflow failure where validation runs before
  dependency installation.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _load_yaml_module():
    try:
        return importlib.import_module("yaml")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        return importlib.import_module("yaml")


yaml = _load_yaml_module()


ROOT = Path(__file__).resolve().parents[1]
WORKSTREAMS_PATH = ROOT / "core_lite" / "workstreams.yml"
BLOCKS_PATH = ROOT / "core_lite" / "transition_blocks.yml"
REPORTS_DIR = ROOT / "reports"
RECEIPTS_DIR = ROOT / "receipts"
MD_REPORT_PATH = REPORTS_DIR / "workstream_status.md"
JSON_REPORT_PATH = REPORTS_DIR / "workstream_status.json"
RECEIPTS_PATH = RECEIPTS_DIR / "workstream_receipts.jsonl"


REQUIRED_WORKSTREAM_FIELDS = {
    "id",
    "name",
    "status",
    "goal",
    "done_when",
    "allowed_blocks",
    "human_review_required_for",
    "forbidden_blocks",
    "next_action",
}

VALID_STATUSES = {
    "active",
    "blocked",
    "ready_for_auto_fix",
    "ready_for_review",
    "quarantined",
    "complete",
    "paused",
}


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path.relative_to(ROOT)}")
    return data


def get_defined_blocks(blocks_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_blocks = blocks_doc.get("blocks", [])
    if not isinstance(raw_blocks, list):
        raise ValueError("transition_blocks.yml field 'blocks' must be a list")

    defined: dict[str, dict[str, Any]] = {}
    for index, block in enumerate(raw_blocks):
        if not isinstance(block, dict):
            raise ValueError(f"Block at index {index} must be a mapping")
        block_id = block.get("id")
        if not isinstance(block_id, str) or not block_id.strip():
            raise ValueError(f"Block at index {index} is missing a valid id")
        if block_id in defined:
            raise ValueError(f"Duplicate transition block id: {block_id}")
        defined[block_id] = block
    return defined


def validate_workstream(
    workstream: dict[str, Any],
    defined_blocks: dict[str, dict[str, Any]],
    global_forbidden: set[str],
) -> dict[str, Any]:
    wid = workstream.get("id", "<missing>")
    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(field for field in REQUIRED_WORKSTREAM_FIELDS if field not in workstream)
    for field in missing:
        errors.append(f"missing required field: {field}")

    status = workstream.get("status")
    if status not in VALID_STATUSES:
        errors.append(f"invalid status: {status!r}")

    allowed_blocks = workstream.get("allowed_blocks", [])
    forbidden_blocks = workstream.get("forbidden_blocks", [])
    done_when = workstream.get("done_when", [])
    human_review = workstream.get("human_review_required_for", [])

    if not isinstance(allowed_blocks, list) or not allowed_blocks:
        errors.append("allowed_blocks must be a non-empty list")
        allowed_blocks = []

    if not isinstance(forbidden_blocks, list):
        errors.append("forbidden_blocks must be a list")
        forbidden_blocks = []

    if not isinstance(done_when, list) or not done_when:
        errors.append("done_when must be a non-empty list")

    if not isinstance(human_review, list) or not human_review:
        errors.append("human_review_required_for must be a non-empty list")

    unknown_allowed = sorted(block for block in allowed_blocks if block not in defined_blocks)
    unknown_forbidden = sorted(
        block for block in forbidden_blocks
        if block not in defined_blocks and block not in global_forbidden
    )

    for block in unknown_allowed:
        errors.append(f"allowed block is not defined: {block}")

    for block in unknown_forbidden:
        warnings.append(f"forbidden block is not defined in transition block registry: {block}")

    overlap = sorted(set(allowed_blocks).intersection(set(forbidden_blocks)))
    for block in overlap:
        errors.append(f"block appears in both allowed and forbidden lists: {block}")

    if status == "blocked" and not workstream.get("blocked_reason"):
        errors.append("blocked workstream must include blocked_reason")

    return {
        "id": wid,
        "name": workstream.get("name", ""),
        "status": status,
        "goal": workstream.get("goal", ""),
        "next_action": workstream.get("next_action", ""),
        "allowed_block_count": len(allowed_blocks),
        "forbidden_block_count": len(forbidden_blocks),
        "done_when_count": len(done_when) if isinstance(done_when, list) else 0,
        "human_review_boundary_count": len(human_review) if isinstance(human_review, list) else 0,
        "errors": errors,
        "warnings": warnings,
    }


def build_markdown_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Core-Lite Workstream Status")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Workstreams: `{report['summary']['workstream_count']}`")
    lines.append(f"- Transition blocks: `{report['summary']['transition_block_count']}`")
    lines.append(f"- Errors: `{report['summary']['error_count']}`")
    lines.append(f"- Warnings: `{report['summary']['warning_count']}`")
    lines.append(f"- Result: `{report['summary']['result']}`")
    lines.append("")
    lines.append("## Operating Rule")
    lines.append("")
    lines.append("Any idea may be captured as a workstream. Only block-authorized transitions may mutate the repo.")
    lines.append("")
    lines.append("## Workstreams")
    lines.append("")

    for item in report["workstreams"]:
        lines.append(f"### {item['id']} — {item['name']}")
        lines.append("")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Goal: {item['goal']}")
        lines.append(f"- Next action: {item['next_action']}")
        lines.append(f"- Allowed blocks: `{item['allowed_block_count']}`")
        lines.append(f"- Forbidden blocks: `{item['forbidden_block_count']}`")
        lines.append(f"- Done criteria: `{item['done_when_count']}`")
        lines.append(f"- Human-review boundaries: `{item['human_review_boundary_count']}`")

        if item["errors"]:
            lines.append("")
            lines.append("Errors:")
            for error in item["errors"]:
                lines.append(f"- {error}")

        if item["warnings"]:
            lines.append("")
            lines.append("Warnings:")
            for warning in item["warnings"]:
                lines.append(f"- {warning}")

        if not item["errors"] and not item["warnings"]:
            lines.append("")
            lines.append("Validation: pass")

        lines.append("")

    lines.append("## Receipts")
    lines.append("")
    lines.append(f"- Receipt hash: `{report['receipt']['hash']}`")
    lines.append("- Receipt path: `receipts/workstream_receipts.jsonl`")
    lines.append("")
    return "\n".join(lines)


def append_receipt(report: dict[str, Any]) -> dict[str, Any]:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

    previous_hash = None
    if RECEIPTS_PATH.exists():
        lines = [line for line in RECEIPTS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            try:
                previous_hash = json.loads(lines[-1]).get("hash")
            except json.JSONDecodeError:
                previous_hash = None

    receipt_payload = {
        "receipt_type": "core_lite.workstream_status",
        "timestamp": report["generated_at"],
        "workstream_count": report["summary"]["workstream_count"],
        "transition_block_count": report["summary"]["transition_block_count"],
        "error_count": report["summary"]["error_count"],
        "warning_count": report["summary"]["warning_count"],
        "result": report["summary"]["result"],
        "previous_hash": previous_hash,
    }
    receipt_hash = stable_hash(receipt_payload)
    receipt = {**receipt_payload, "hash": receipt_hash}

    with RECEIPTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")

    return receipt


def validate() -> tuple[dict[str, Any], int]:
    workstreams_doc = load_yaml(WORKSTREAMS_PATH)
    blocks_doc = load_yaml(BLOCKS_PATH)

    defined_blocks = get_defined_blocks(blocks_doc)
    policy = workstreams_doc.get("policy", {})
    global_forbidden = set(policy.get("global_forbidden_blocks", []))

    raw_workstreams = workstreams_doc.get("workstreams", [])
    if not isinstance(raw_workstreams, list) or not raw_workstreams:
        raise ValueError("workstreams.yml field 'workstreams' must be a non-empty list")

    seen_ids: set[str] = set()
    workstream_reports: list[dict[str, Any]] = []

    for index, workstream in enumerate(raw_workstreams):
        if not isinstance(workstream, dict):
            raise ValueError(f"Workstream at index {index} must be a mapping")

        wid = workstream.get("id")
        if wid in seen_ids:
            item = {
                "id": wid,
                "name": workstream.get("name", ""),
                "status": workstream.get("status", ""),
                "goal": workstream.get("goal", ""),
                "next_action": workstream.get("next_action", ""),
                "allowed_block_count": 0,
                "forbidden_block_count": 0,
                "done_when_count": 0,
                "human_review_boundary_count": 0,
                "errors": [f"duplicate workstream id: {wid}"],
                "warnings": [],
            }
        else:
            item = validate_workstream(workstream, defined_blocks, global_forbidden)
            seen_ids.add(wid)

        workstream_reports.append(item)

    error_count = sum(len(item["errors"]) for item in workstream_reports)
    warning_count = sum(len(item["warnings"]) for item in workstream_reports)

    report = {
        "generated_at": utc_now(),
        "summary": {
            "workstream_count": len(workstream_reports),
            "transition_block_count": len(defined_blocks),
            "error_count": error_count,
            "warning_count": warning_count,
            "result": "pass" if error_count == 0 else "fail",
        },
        "workstreams": workstream_reports,
    }

    receipt = append_receipt(report)
    report["receipt"] = receipt

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MD_REPORT_PATH.write_text(build_markdown_report(report), encoding="utf-8")
    JSON_REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return report, 0 if error_count == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Core-Lite workstreams and generate status artifacts.")
    parser.add_argument("--json", action="store_true", help="Print the generated JSON report to stdout.")
    args = parser.parse_args()

    try:
        report, exit_code = validate()
    except Exception as exc:
        print(f"Validation failed before report generation: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {MD_REPORT_PATH.relative_to(ROOT)}")
    print(f"Wrote {JSON_REPORT_PATH.relative_to(ROOT)}")
    print(f"Wrote {RECEIPTS_PATH.relative_to(ROOT)}")
    print(f"Result: {report['summary']['result']}")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
