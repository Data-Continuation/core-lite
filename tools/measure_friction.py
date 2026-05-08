#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: PyYAML. Install with: python -m pip install pyyaml") from exc


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def append_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    receipt_path = root / "receipts" / "friction_avoided_receipts.jsonl"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    previous_hash = None
    if receipt_path.exists():
        lines = [line for line in receipt_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            previous_hash = json.loads(lines[-1]).get("hash")

    payload = {
        "receipt_type": "core_lite.friction_avoided",
        "timestamp": report["generated_at"],
        "result": report["summary"]["result"],
        "failure_type_count": report["summary"]["failure_type_count"],
        "estimated_minutes_saved": report["summary"]["estimated_minutes_saved"],
        "estimated_hours_saved": report["summary"]["estimated_hours_saved"],
        "repeated_prompts_prevented": report["summary"]["repeated_prompts_prevented"],
        "manual_actions_prevented": report["summary"]["manual_actions_prevented"],
        "reruns_prevented": report["summary"]["reruns_prevented"],
        "trust_friction_score": report["summary"]["trust_friction_score"],
        "previous_hash": previous_hash,
    }
    receipt = {**payload, "hash": stable_hash(payload)}
    with receipt_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Core-Lite Friction Avoided Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Definition",
        "",
        report["metric"]["definition"],
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines += ["", "## Category Totals", ""]
    for category, totals in sorted(report["categories"].items()):
        lines += [f"### {category}", ""]
        for key, value in totals.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    lines += ["## Failure Types", ""]
    for event in report["failure_types"]:
        lines += [
            f"### {event['id']} — {event['name']}",
            "",
            f"- Category: `{event['category']}`",
            f"- Estimated minutes saved: `{event['estimated_minutes_saved']}`",
            f"- Estimated hours saved: `{event['estimated_hours_saved']}`",
            f"- Repeated prompts prevented: `{event['repeated_prompts_prevented']}`",
            f"- Manual actions prevented: `{event['manual_actions_prevented']}`",
            f"- Reruns prevented: `{event['reruns_prevented']}`",
            f"- Trust severity: `{event['trust_severity']}`",
            "- Prevented by:",
        ]
        for block in event["prevented_by"]:
            lines.append(f"  - `{block}`")
        lines += [f"- Evidence note: {event['evidence_note']}", ""]
    lines += [
        "## Receipt",
        "",
        f"- Receipt hash: `{report['receipt']['hash']}`",
        "- Receipt path: `receipts/friction_avoided_receipts.jsonl`",
        "",
    ]
    return "\n".join(lines)


def run(root: Path) -> tuple[dict[str, Any], int]:
    registry = load_yaml(root / "core_lite" / "friction_events.yml")
    metric = registry.get("metric", {})
    weights = metric.get("trust_severity_weights", {})
    events = registry.get("failure_types", [])
    if not isinstance(events, list) or not events:
        raise ValueError("failure_types must be a non-empty list")

    required = {
        "id", "name", "category", "prevented_by", "estimated_minutes_saved",
        "repeated_prompts_prevented", "manual_actions_prevented", "reruns_prevented",
        "trust_severity", "evidence_note",
    }

    errors: list[str] = []
    normalized: list[dict[str, Any]] = []
    categories: dict[str, dict[str, int]] = {}
    totals = {
        "estimated_minutes_saved": 0,
        "repeated_prompts_prevented": 0,
        "manual_actions_prevented": 0,
        "reruns_prevented": 0,
        "trust_friction_score": 0,
    }

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"event index {index} is not a mapping")
            continue
        missing = sorted(required - set(event))
        if missing:
            errors.append(f"event {event.get('id', index)} missing: {', '.join(missing)}")

        category = str(event.get("category", "unknown"))
        categories.setdefault(category, {
            "event_count": 0,
            "estimated_minutes_saved": 0,
            "repeated_prompts_prevented": 0,
            "manual_actions_prevented": 0,
            "reruns_prevented": 0,
        })

        minutes = int(event.get("estimated_minutes_saved", 0))
        prompts = int(event.get("repeated_prompts_prevented", 0))
        manual = int(event.get("manual_actions_prevented", 0))
        reruns = int(event.get("reruns_prevented", 0))
        severity = str(event.get("trust_severity", "low"))

        totals["estimated_minutes_saved"] += minutes
        totals["repeated_prompts_prevented"] += prompts
        totals["manual_actions_prevented"] += manual
        totals["reruns_prevented"] += reruns
        totals["trust_friction_score"] += int(weights.get(severity, 1))

        categories[category]["event_count"] += 1
        categories[category]["estimated_minutes_saved"] += minutes
        categories[category]["repeated_prompts_prevented"] += prompts
        categories[category]["manual_actions_prevented"] += manual
        categories[category]["reruns_prevented"] += reruns

        normalized.append({
            "id": event.get("id"),
            "name": event.get("name"),
            "category": category,
            "prevented_by": event.get("prevented_by", []),
            "estimated_minutes_saved": minutes,
            "estimated_hours_saved": round(minutes / 60, 2),
            "repeated_prompts_prevented": prompts,
            "manual_actions_prevented": manual,
            "reruns_prevented": reruns,
            "trust_severity": severity,
            "evidence_note": event.get("evidence_note", ""),
        })

    report = {
        "generated_at": now(),
        "metric": {
            "name": metric.get("name", "Friction Avoided"),
            "short_name": metric.get("short_name", "FA"),
            "definition": metric.get("definition", ""),
        },
        "summary": {
            "result": "pass" if not errors else "fail",
            "failure_type_count": len(normalized),
            "estimated_minutes_saved": totals["estimated_minutes_saved"],
            "estimated_hours_saved": round(totals["estimated_minutes_saved"] / 60, 2),
            "repeated_prompts_prevented": totals["repeated_prompts_prevented"],
            "manual_actions_prevented": totals["manual_actions_prevented"],
            "reruns_prevented": totals["reruns_prevented"],
            "trust_friction_score": totals["trust_friction_score"],
            "error_count": len(errors),
        },
        "categories": categories,
        "failure_types": normalized,
        "errors": errors,
    }
    report["receipt"] = append_receipt(root, report)

    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "friction_avoided.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "friction_avoided.md").write_text(markdown(report), encoding="utf-8")
    return report, 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        report, code = run(root)
    except Exception as exc:
        print(f"Friction report failed: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {(root / 'reports' / 'friction_avoided.md').as_posix()}")
    print(f"Wrote {(root / 'reports' / 'friction_avoided.json').as_posix()}")
    print(f"Wrote {(root / 'receipts' / 'friction_avoided_receipts.jsonl').as_posix()}")
    print(f"Result: {report['summary']['result']}")
    print(f"Estimated hours saved: {report['summary']['estimated_hours_saved']}")
    print(f"Repeated prompts prevented: {report['summary']['repeated_prompts_prevented']}")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
