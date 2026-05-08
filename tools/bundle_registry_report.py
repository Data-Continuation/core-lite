#!/usr/bin/env python3
"""
Core-Lite Bundle Registry Report

Reads core_lite/bundle_registry.yml and generates:
- reports/bundle_registry.md
- reports/bundle_registry.json
- receipts/bundle_registry_receipts.jsonl

Purpose:
Track bundle supersession, current canonical bundles, obsolete/failure churn,
and estimated handling friction.

This tool does not mutate source files or delete bundles.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_yaml_module():
    try:
        return importlib.import_module("yaml")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        return importlib.import_module("yaml")


yaml = load_yaml_module()


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def normalize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): normalize_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_json(v) for v in value]
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return value


def append_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    receipt_path = root / "receipts" / "bundle_registry_receipts.jsonl"
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
        "receipt_type": "core_lite.bundle_registry",
        "timestamp": report["generated_at"],
        "result": report["summary"]["result"],
        "bundle_count": report["summary"]["bundle_count"],
        "current_count": report["summary"]["status_counts"].get("current", 0),
        "superseded_count": report["summary"]["status_counts"].get("superseded", 0),
        "failed_count": report["summary"]["status_counts"].get("failed", 0),
        "obsolete_count": report["summary"]["status_counts"].get("obsolete", 0),
        "observed_external_zip_count": report["summary"]["observed_external_zip_count"],
        "estimated_handling_hours_likely": report["summary"]["estimated_handling_hours_likely"],
        "previous_hash": previous_hash,
    }
    receipt = {**payload, "hash": stable_hash(payload)}

    with receipt_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")

    return receipt


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bundles = registry.get("bundles", [])
    if not isinstance(bundles, list) or not bundles:
        return ["bundle_registry.yml must contain a non-empty bundles list"]

    ids = set()
    for index, bundle in enumerate(bundles):
        if not isinstance(bundle, dict):
            errors.append(f"bundle index {index} is not a mapping")
            continue
        bundle_id = bundle.get("id")
        if not bundle_id:
            errors.append(f"bundle index {index} missing id")
        elif bundle_id in ids:
            errors.append(f"duplicate bundle id: {bundle_id}")
        else:
            ids.add(bundle_id)

        for field in [
            "name",
            "workstream_id",
            "class",
            "status",
            "purpose",
            "supersedes",
            "source_only",
            "generated_artifacts_included",
            "contains_markdown",
            "verification_result",
        ]:
            if field not in bundle:
                errors.append(f"bundle {bundle_id or index} missing {field}")

    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        bundle_id = bundle.get("id", "<missing>")
        for parent in bundle.get("supersedes") or []:
            if parent not in ids:
                errors.append(f"bundle {bundle_id} supersedes unknown bundle id: {parent}")
        child = bundle.get("superseded_by")
        if child and child not in ids:
            errors.append(f"bundle {bundle_id} superseded_by unknown bundle id: {child}")

    return errors


def compute_report(root: Path) -> tuple[dict[str, Any], int]:
    registry_path = root / "core_lite" / "bundle_registry.yml"
    registry = normalize_json(read_yaml(registry_path))
    errors = validate_registry(registry)

    bundles = registry.get("bundles", [])
    defaults = registry.get("defaults", {})
    observed = registry.get("registry", {}).get("observed_external_inventory", {})

    status_counts: dict[str, int] = {}
    class_counts: dict[str, int] = {}
    markdown_count = 0
    source_only_count = 0
    generated_artifacts_count = 0

    current_bundles: list[dict[str, Any]] = []
    failed_bundles: list[dict[str, Any]] = []
    quarantine_candidates: list[dict[str, Any]] = []

    for bundle in bundles:
        status = str(bundle.get("status", "unknown"))
        klass = str(bundle.get("class", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
        class_counts[klass] = class_counts.get(klass, 0) + 1

        if bundle.get("contains_markdown"):
            markdown_count += 1
        if bundle.get("source_only"):
            source_only_count += 1
        if bundle.get("generated_artifacts_included"):
            generated_artifacts_count += 1

        if status == "current":
            current_bundles.append(bundle)
        if status == "failed":
            failed_bundles.append(bundle)
        if status in {"failed", "obsolete", "quarantine"} or klass in {"avoidable_failure_churn", "corrective_rework"}:
            quarantine_candidates.append(bundle)

    observed_zip_count = int(observed.get("observed_item_count", 0) or 0)
    likely_minutes = int(defaults.get("estimated_handling_minutes_per_bundle_likely", 6))
    low_minutes = int(defaults.get("estimated_handling_minutes_per_bundle_low", 3))
    high_minutes = int(defaults.get("estimated_handling_minutes_per_bundle_high", 10))

    corrective_count = class_counts.get("corrective_rework", 0) + class_counts.get("avoidable_failure_churn", 0)
    tracked_count = len(bundles)

    summary = {
        "result": "pass" if not errors else "fail",
        "bundle_count": tracked_count,
        "observed_external_zip_count": observed_zip_count,
        "status_counts": dict(sorted(status_counts.items())),
        "class_counts": dict(sorted(class_counts.items())),
        "current_bundle_count": len(current_bundles),
        "failed_bundle_count": len(failed_bundles),
        "quarantine_candidate_count": len(quarantine_candidates),
        "corrective_or_avoidable_count": corrective_count,
        "source_only_count": source_only_count,
        "generated_artifacts_included_count": generated_artifacts_count,
        "contains_markdown_count": markdown_count,
        "estimated_handling_hours_low": round((observed_zip_count * low_minutes) / 60, 2),
        "estimated_handling_hours_likely": round((observed_zip_count * likely_minutes) / 60, 2),
        "estimated_handling_hours_high": round((observed_zip_count * high_minutes) / 60, 2),
        "error_count": len(errors),
    }

    report: dict[str, Any] = {
        "generated_at": now(),
        "summary": summary,
        "registry": registry.get("registry", {}),
        "current_bundles": current_bundles,
        "failed_bundles": failed_bundles,
        "quarantine_candidates": quarantine_candidates,
        "bundles": bundles,
        "errors": errors,
    }

    report["receipt"] = append_receipt(root, report)

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "bundle_registry.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (reports_dir / "bundle_registry.md").write_text(
        render_markdown(report),
        encoding="utf-8",
    )

    return report, 0 if not errors else 1


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Core-Lite Bundle Registry Report")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Operating Rule")
    lines.append("")
    lines.append("Bundle-only delivery is valid. Untracked bundle proliferation is not.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in report["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Current Bundles")
    lines.append("")
    if not report["current_bundles"]:
        lines.append("- None")
    for bundle in report["current_bundles"]:
        lines.append(f"- `{bundle['id']}` — `{bundle['name']}`: {bundle['purpose']}")
    lines.append("")
    lines.append("## Failed Bundles")
    lines.append("")
    if not report["failed_bundles"]:
        lines.append("- None")
    for bundle in report["failed_bundles"]:
        lines.append(f"- `{bundle['id']}` — `{bundle['name']}`: {bundle.get('notes', '')}")
    lines.append("")
    lines.append("## Quarantine Candidates")
    lines.append("")
    if not report["quarantine_candidates"]:
        lines.append("- None")
    for bundle in report["quarantine_candidates"]:
        lines.append(f"- `{bundle['id']}` — `{bundle['name']}` / status `{bundle['status']}` / class `{bundle['class']}`")
    lines.append("")
    lines.append("## Bundles")
    lines.append("")
    for bundle in report["bundles"]:
        lines.append(f"### {bundle['id']} — {bundle['name']}")
        lines.append("")
        lines.append(f"- Workstream: `{bundle['workstream_id']}`")
        lines.append(f"- Class: `{bundle['class']}`")
        lines.append(f"- Status: `{bundle['status']}`")
        lines.append(f"- Purpose: {bundle['purpose']}")
        lines.append(f"- Supersedes: `{bundle.get('supersedes')}`")
        lines.append(f"- Superseded by: `{bundle.get('superseded_by')}`")
        lines.append(f"- Source only: `{bundle['source_only']}`")
        lines.append(f"- Generated artifacts included: `{bundle['generated_artifacts_included']}`")
        lines.append(f"- Contains Markdown: `{bundle['contains_markdown']}`")
        lines.append(f"- Verification result: `{bundle['verification_result']}`")
        if bundle.get("notes"):
            lines.append(f"- Notes: {bundle['notes']}")
        lines.append("")
    if report["errors"]:
        lines.append("## Errors")
        lines.append("")
        for error in report["errors"]:
            lines.append(f"- {error}")
        lines.append("")
    lines.append("## Receipt")
    lines.append("")
    lines.append(f"- Receipt hash: `{report['receipt']['hash']}`")
    lines.append("- Receipt path: `receipts/bundle_registry_receipts.jsonl`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Core-Lite bundle registry report.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    try:
        report, code = compute_report(root)
    except Exception as exc:
        print(f"Bundle registry report failed: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {(root / 'reports' / 'bundle_registry.md').as_posix()}")
    print(f"Wrote {(root / 'reports' / 'bundle_registry.json').as_posix()}")
    print(f"Wrote {(root / 'receipts' / 'bundle_registry_receipts.jsonl').as_posix()}")
    print(f"Result: {report['summary']['result']}")
    print(f"Current bundles: {report['summary']['current_bundle_count']}")
    print(f"Quarantine candidates: {report['summary']['quarantine_candidate_count']}")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return code


if __name__ == "__main__":
    raise SystemExit(main())
