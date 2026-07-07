#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

MANIFEST = Path("core_lite/stegverse_002_export_manifest.json")
REPORT_JSON = Path("reports/stegverse_002_export_manifest.json")
REPORT_MD = Path("reports/stegverse_002_export_manifest.md")
RECEIPT_PATH = Path("receipts/stegverse_002_export_receipts.jsonl")


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def append_receipt(report: dict[str, Any]) -> dict[str, Any]:
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = None
    if RECEIPT_PATH.exists():
        lines = [line for line in RECEIPT_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            try:
                previous_hash = json.loads(lines[-1]).get("hash")
            except json.JSONDecodeError:
                previous_hash = None

    payload = {
        "schema": "stegverse.core_lite.stegverse_002_export_receipt.v1",
        "version": report["version"],
        "source_repo": report["source_repo"],
        "destination_repo": report["destination_repo"],
        "result": report["result"],
        "missing_required_report_count": len(report["missing_required_reports"]),
        "missing_required_receipt_count": len(report["missing_required_receipts"]),
        "candidate_evidence_only": report["authority"]["candidate_evidence_only"],
        "may_bind_destination_repo_state": report["authority"]["may_bind_destination_repo_state"],
        "previous_hash": previous_hash,
    }
    receipt = {**payload, "hash": stable_hash(payload)}
    with RECEIPT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# StegVerse-002 Export Manifest Validation",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Source repo: `{report['source_repo']}`",
        f"Destination repo: `{report['destination_repo']}`",
        f"Artifact: `{report['artifact_name']}`",
        "",
        "## Result",
        "",
        f"`{report['result']}`",
        "",
        "## Authority Boundary",
        "",
    ]
    for key, value in report["authority"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Missing Required Reports", ""])
    if report["missing_required_reports"]:
        lines.extend(f"- `{path}`" for path in report["missing_required_reports"])
    else:
        lines.append("- None")
    lines.extend(["", "## Missing Required Receipts", ""])
    if report["missing_required_receipts"]:
        lines.extend(f"- `{path}`" for path in report["missing_required_receipts"])
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Destination Intake",
        "",
        f"- Policy: `{report['destination_intake']['policy']}`",
        f"- Pending result: `{report['destination_intake']['pending_result']}`",
        f"- Accepted result: `{report['destination_intake']['accepted_result']}`",
        "",
        "## Receipt",
        "",
        f"- Receipt hash: `{report['receipt']['hash']}`",
        f"- Receipt path: `{RECEIPT_PATH.as_posix()}`",
        "",
    ])
    return "\n".join(lines)


def build_report(root: Path) -> tuple[dict[str, Any], int]:
    manifest_path = root / MANIFEST
    manifest = read_json(manifest_path)

    required_reports = list(manifest.get("required_reports", []))
    required_receipts = list(manifest.get("required_receipts", []))
    missing_reports = [path for path in required_reports if not (root / path).exists()]
    missing_receipts = [path for path in required_receipts if not (root / path).exists()]

    complete = not missing_reports and not missing_receipts
    result = manifest.get("export_result_when_complete", "STEGVERSE_002_EXPORT_PACKAGE_DECLARED") if complete else "STEGVERSE_002_EXPORT_PACKAGE_PENDING_REPORTS"

    report: dict[str, Any] = {
        "schema": "stegverse.core_lite.stegverse_002_export_manifest_validation.v1",
        "version": manifest["version"],
        "generated_at": now(),
        "source_repo": manifest["source_repo"],
        "destination_repo": manifest["destination_repo"],
        "artifact_name": manifest["artifact_name"],
        "authority": manifest["authority"],
        "destination_intake": manifest["destination_intake"],
        "required_reports": required_reports,
        "required_receipts": required_receipts,
        "missing_required_reports": missing_reports,
        "missing_required_receipts": missing_receipts,
        "result": result,
        "mutation_count": 0,
    }
    report["receipt"] = append_receipt(report)

    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / REPORT_JSON).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (root / REPORT_MD).write_text(render_markdown(report), encoding="utf-8")
    return report, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the StegVerse-002 export manifest.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report, code = build_report(Path(args.root).resolve())
    except Exception as exc:
        print(f"StegVerse-002 export validation failed: {exc}")
        return 2

    print(f"Wrote {REPORT_MD.as_posix()}")
    print(f"Wrote {REPORT_JSON.as_posix()}")
    print(f"Wrote {RECEIPT_PATH.as_posix()}")
    print(f"Result: {report['result']}")
    print("Mutations performed: 0")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
