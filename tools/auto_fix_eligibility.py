#!/usr/bin/env python3
"""
Core-Lite Auto-Fix Eligibility Planner

Reads reports/ecosystem_maintainer_scan.json and generates:
- reports/auto_fix_eligibility.md
- reports/auto_fix_eligibility.json
- receipts/auto_fix_eligibility_receipts.jsonl

Purpose:
Move from scan-only to mutation planning without applying mutations.

This tool performs no source mutation. It only classifies each scanned file into
the next safe transition bucket:
- NO_ACTION
- AUTO_FIX_ELIGIBLE
- AUTO_QUARANTINE_ELIGIBLE
- COMPLETE_STUB_ELIGIBLE
- HUMAN_REVIEW_REQUIRED
- DO_NOT_TOUCH
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_scan(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required scan report not found: {path}. Run tools/ecosystem_maintainer.py first."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("scan report must be a JSON object")
    if "files" not in data or not isinstance(data["files"], list):
        raise ValueError("scan report must contain a files list")
    return data


def is_canonical_path(path: str) -> bool:
    return (
        path == "README.md"
        or path.startswith("core_lite/")
        or path.startswith(".github/workflows/")
        or path.startswith("github/workflows/")
    )


def classify_file(item: dict[str, Any]) -> dict[str, Any]:
    path = str(item.get("path", ""))
    klass = str(item.get("class", "UNCLASSIFIED"))
    broken_refs = item.get("broken_refs", []) or []
    inbound_refs = item.get("inbound_refs", []) or []
    evidence = item.get("evidence", []) or []

    result: dict[str, Any] = {
        "path": path,
        "source_class": klass,
        "recommended_bucket": "NO_ACTION",
        "recommended_transition_block": None,
        "mutation_allowed_now": False,
        "requires_human_review": False,
        "reason": "",
    }

    if klass == "CANONICAL_OR_CONTROL":
        result.update({
            "recommended_bucket": "DO_NOT_TOUCH",
            "recommended_transition_block": "ASK_BOUNDARY_DECISION",
            "requires_human_review": True,
            "reason": "canonical/control file requires explicit boundary review before mutation",
        })
        return result

    if klass == "SUPPORT_ARTIFACT":
        result.update({
            "recommended_bucket": "NO_ACTION",
            "reason": "support artifact should be kept unless superseded by bundle registry policy",
        })
        return result

    if klass == "REAL":
        result.update({
            "recommended_bucket": "NO_ACTION",
            "reason": "real file with no maintainer finding",
        })
        return result

    if klass == "BROKEN":
        result.update({
            "recommended_bucket": "HUMAN_REVIEW_REQUIRED",
            "recommended_transition_block": "AUTO_FIX_MECHANICAL",
            "requires_human_review": True,
            "reason": f"broken references require review unless target path is mechanically obvious: {broken_refs}",
        })
        return result

    if klass == "ORPHAN_CANDIDATE":
        result.update({
            "recommended_bucket": "HUMAN_REVIEW_REQUIRED",
            "recommended_transition_block": "AUTO_QUARANTINE_STUB",
            "requires_human_review": True,
            "reason": "orphan candidates are not auto-quarantined without review",
        })
        return result

    if klass == "STUB":
        if is_canonical_path(path):
            result.update({
                "recommended_bucket": "DO_NOT_TOUCH",
                "recommended_transition_block": "ASK_BOUNDARY_DECISION",
                "requires_human_review": True,
                "reason": "stub signal is on a canonical/control path",
            })
        elif inbound_refs:
            result.update({
                "recommended_bucket": "HUMAN_REVIEW_REQUIRED",
                "recommended_transition_block": "COMPLETE_LOW_RISK_STUB",
                "requires_human_review": True,
                "reason": f"stub has inbound references and may need completion before quarantine: {inbound_refs}",
            })
        elif any("empty file" in str(e).lower() or "tiny placeholder" in str(e).lower() for e in evidence):
            result.update({
                "recommended_bucket": "AUTO_QUARANTINE_ELIGIBLE",
                "recommended_transition_block": "AUTO_QUARANTINE_STUB",
                "mutation_allowed_now": True,
                "reason": "inactive placeholder stub with no inbound references",
            })
        else:
            result.update({
                "recommended_bucket": "COMPLETE_STUB_ELIGIBLE",
                "recommended_transition_block": "COMPLETE_LOW_RISK_STUB",
                "requires_human_review": True,
                "reason": "stub may be completable but intended behavior must be explicit",
            })
        return result

    if klass == "STUB_DEPENDENT":
        result.update({
            "recommended_bucket": "HUMAN_REVIEW_REQUIRED",
            "recommended_transition_block": "MAP_DEPENDENCY",
            "requires_human_review": True,
            "reason": "dependency must be handled before dependent file is mutated",
        })
        return result

    result.update({
        "recommended_bucket": "HUMAN_REVIEW_REQUIRED",
        "recommended_transition_block": "ASK_BOUNDARY_DECISION",
        "requires_human_review": True,
        "reason": f"unrecognized or unsupported class: {klass}",
    })
    return result


def append_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    receipt_path = root / "receipts" / "auto_fix_eligibility_receipts.jsonl"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    previous_hash = None
    if receipt_path.exists():
        lines = [line for line in receipt_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            try:
                previous_hash = json.loads(lines[-1]).get("hash")
            except json.JSONDecodeError:
                previous_hash = None

    payload = {
        "receipt_type": "core_lite.auto_fix_eligibility",
        "timestamp": report["generated_at"],
        "result": report["summary"]["result"],
        "file_count": report["summary"]["file_count"],
        "auto_fix_eligible_count": report["summary"]["bucket_counts"].get("AUTO_FIX_ELIGIBLE", 0),
        "auto_quarantine_eligible_count": report["summary"]["bucket_counts"].get("AUTO_QUARANTINE_ELIGIBLE", 0),
        "complete_stub_eligible_count": report["summary"]["bucket_counts"].get("COMPLETE_STUB_ELIGIBLE", 0),
        "human_review_required_count": report["summary"]["bucket_counts"].get("HUMAN_REVIEW_REQUIRED", 0),
        "do_not_touch_count": report["summary"]["bucket_counts"].get("DO_NOT_TOUCH", 0),
        "mutation_count": 0,
        "previous_hash": previous_hash,
    }
    receipt = {**payload, "hash": stable_hash(payload)}

    with receipt_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")

    return receipt


def build_report(root: Path) -> tuple[dict[str, Any], int]:
    scan_path = root / "reports" / "ecosystem_maintainer_scan.json"
    scan = load_scan(scan_path)

    decisions = [classify_file(item) for item in scan["files"]]

    bucket_counts: dict[str, int] = {}
    block_counts: dict[str, int] = {}
    for decision in decisions:
        bucket = decision["recommended_bucket"]
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        block = decision.get("recommended_transition_block")
        if block:
            block_counts[block] = block_counts.get(block, 0) + 1

    report: dict[str, Any] = {
        "generated_at": now(),
        "source_scan_generated_at": scan.get("generated_at"),
        "summary": {
            "result": "pass",
            "file_count": len(decisions),
            "mutation_count": 0,
            "bucket_counts": dict(sorted(bucket_counts.items())),
            "transition_block_counts": dict(sorted(block_counts.items())),
        },
        "decisions": decisions,
    }

    report["receipt"] = append_receipt(root, report)

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "auto_fix_eligibility.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (reports_dir / "auto_fix_eligibility.md").write_text(
        render_markdown(report),
        encoding="utf-8",
    )

    return report, 0


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Core-Lite Auto-Fix Eligibility Plan")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append(f"Source scan generated: `{report['source_scan_generated_at']}`")
    lines.append("")
    lines.append("## Done Definition")
    lines.append("")
    lines.append("- Read latest ecosystem maintainer scan.")
    lines.append("- Classify files into next safe transition buckets.")
    lines.append("- Generate Markdown and JSON reports.")
    lines.append("- Emit receipt.")
    lines.append("- Perform no source mutation.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Result: `{report['summary']['result']}`")
    lines.append(f"- Files evaluated: `{report['summary']['file_count']}`")
    lines.append(f"- Mutations performed: `0`")
    lines.append("")
    lines.append("## Bucket Counts")
    lines.append("")
    for key, value in report["summary"]["bucket_counts"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Transition Block Counts")
    lines.append("")
    if not report["summary"]["transition_block_counts"]:
        lines.append("- None")
    for key, value in report["summary"]["transition_block_counts"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Decisions")
    lines.append("")
    for decision in report["decisions"]:
        lines.append(f"### {decision['path']}")
        lines.append("")
        lines.append(f"- Source class: `{decision['source_class']}`")
        lines.append(f"- Recommended bucket: `{decision['recommended_bucket']}`")
        lines.append(f"- Recommended transition block: `{decision['recommended_transition_block']}`")
        lines.append(f"- Mutation allowed now: `{decision['mutation_allowed_now']}`")
        lines.append(f"- Requires human review: `{decision['requires_human_review']}`")
        lines.append(f"- Reason: {decision['reason']}")
        lines.append("")
    lines.append("## Receipt")
    lines.append("")
    lines.append(f"- Receipt hash: `{report['receipt']['hash']}`")
    lines.append("- Receipt path: `receipts/auto_fix_eligibility_receipts.jsonl`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Core-Lite auto-fix eligibility plan.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    try:
        report, code = build_report(root)
    except Exception as exc:
        print(f"Auto-fix eligibility failed: {exc}")
        return 2

    print(f"Wrote {(root / 'reports' / 'auto_fix_eligibility.md').as_posix()}")
    print(f"Wrote {(root / 'reports' / 'auto_fix_eligibility.json').as_posix()}")
    print(f"Wrote {(root / 'receipts' / 'auto_fix_eligibility_receipts.jsonl').as_posix()}")
    print(f"Result: {report['summary']['result']}")
    print("Mutations performed: 0")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return code


if __name__ == "__main__":
    raise SystemExit(main())
