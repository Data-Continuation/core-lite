from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core_lite.cge import classify_sandbox_result, precheck_manifest
from core_lite.receipts import ReceiptRecorder
from core_lite.sandbox import run_sandbox


REPORT_DIR = Path("reports/current/core-lite-ingestion-sandbox-loop")
RECEIPT_DIR = Path("receipts/current/core-lite-ingestion-sandbox-loop")
REPORT_JSON = REPORT_DIR / "report.json"
REPORT_MD = REPORT_DIR / "report.md"
RECEIPTS = RECEIPT_DIR / "receipts.jsonl"


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def hash_dict(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_manifest(bundle_dir: Path) -> tuple[dict[str, Any], Path]:
    for name in ("bundle_manifest.json", "manifest.json"):
        candidate = bundle_dir / name
        if candidate.exists() and candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8")), candidate
    raise FileNotFoundError("bundle_manifest.json or manifest.json not found")


def write_markdown_report(report: dict[str, Any]) -> None:
    lines = [
        "# Core-Lite Recorded Ingestion + CGE + Sandbox Loop Report",
        "",
        "## Status",
        "",
        "```text",
        f"success: {str(report['success']).lower()}",
        f"final_decision: {report['final_decision']['decision']}",
        f"bundle_id: {report['bundle'].get('bundle_id')}",
        "install_performed: false",
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "Bundle entered ingestion.",
        "CGE precheck evaluated the manifest.",
        "Sandbox evaluated without install.",
        "CGE classified the sandbox result.",
        "Founder/operator review remains required.",
        "```",
        "",
        "## CGE Precheck",
        "",
        "```text",
        f"decision: {report['cge_precheck']['decision']}",
        f"basis: {report['cge_precheck']['basis']}",
        "```",
        "",
        "## CGE Result Classification",
        "",
        "```text",
        f"decision: {report['final_decision']['decision']}",
        f"basis: {report['final_decision']['basis']}",
        "```",
        "",
        "## Evaluated Files",
        "",
    ]

    evaluated = report.get("sandbox_result", {}).get("evaluated_files", [])
    if evaluated:
        for item in evaluated:
            lines.append(f"- `{item['path']}` sha256=`{item['sha256']}`")
    else:
        lines.append("No files evaluated.")

    lines.extend(
        [
            "",
            "## Receipt Chain",
            "",
            "```text",
            f"receipt_path: {report['receipt_path']}",
            f"receipt_count: {len(report['receipts'])}",
            "```",
        ]
    )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_ingestion(bundle: str | Path) -> dict[str, Any]:
    bundle_dir = Path(bundle)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

    recorder = ReceiptRecorder(RECEIPTS)

    manifest, manifest_path = load_manifest(bundle_dir)
    manifest_hash = hash_dict(manifest)

    receipts = []
    receipts.append(
        recorder.record(
            event_type="bundle_submitted",
            actor=manifest.get("actor", "unknown"),
            decision="RECEIVED",
            basis="candidate bundle submitted to core-lite ingestion",
            input_hash=manifest_hash,
            metadata={"bundle_dir": str(bundle_dir), "manifest_path": str(manifest_path)},
        )
    )

    precheck = precheck_manifest(manifest)
    receipts.append(
        recorder.record(
            event_type="cge_precheck_decision",
            actor="core-lite-cge",
            decision=precheck.decision,
            basis=precheck.basis,
            input_hash=manifest_hash,
            metadata=precheck.to_dict(),
        )
    )

    sandbox_result: dict[str, Any] | None = None
    final_decision = precheck

    if precheck.decision in {"ALLOW_SANDBOX", "REVIEW_REQUIRED"}:
        sandbox_result = run_sandbox(bundle_dir, manifest)
        sandbox_hash = hash_dict(sandbox_result)
        receipts.append(
            recorder.record(
                event_type="sandbox_completed",
                actor="core-lite-sandbox",
                decision="SANDBOX_COMPLETED" if sandbox_result.get("success") else "SANDBOX_FAILED",
                basis="sandbox evaluated candidate bundle without installation",
                input_hash=manifest_hash,
                output_hash=sandbox_hash,
                metadata={"install_performed": False},
            )
        )

        final_decision = classify_sandbox_result(sandbox_result)
        receipts.append(
            recorder.record(
                event_type="cge_result_classification",
                actor="core-lite-cge",
                decision=final_decision.decision,
                basis=final_decision.basis,
                input_hash=sandbox_hash,
                metadata=final_decision.to_dict(),
            )
        )
    else:
        sandbox_result = {
            "schema": "stegverse_core_lite_sandbox_result.v1",
            "success": False,
            "install_performed": False,
            "evaluated_file_count": 0,
            "evaluated_files": [],
            "protected_paths": [],
            "missing_declared_paths": [],
            "errors": ["CGE precheck did not allow sandbox evaluation."],
        }

    success = final_decision.decision in {"REVIEW_REQUIRED", "ALLOW_SANDBOX"}

    report = {
        "schema": "stegverse_core_lite_recorded_ingestion_sandbox_loop_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "success": success,
        "bundle": {
            "bundle_dir": str(bundle_dir),
            "manifest_path": str(manifest_path),
            "bundle_id": manifest.get("bundle_id"),
            "purpose": manifest.get("purpose"),
            "actor": manifest.get("actor"),
            "manifest_hash": manifest_hash,
        },
        "cge_precheck": precheck.to_dict(),
        "sandbox_result": sandbox_result,
        "final_decision": final_decision.to_dict(),
        "install_performed": False,
        "production_authority": False,
        "node_status": False,
        "finco_eligibility": False,
        "receipt_path": str(RECEIPTS),
        "receipts": receipts,
        "boundary": [
            "Ingestion received candidate bundle.",
            "CGE evaluated admissibility for sandbox only.",
            "Sandbox ran without installation.",
            "CGE classified sandbox result.",
            "Founder/operator review remains required before any install gate.",
        ],
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report)

    recorder.record(
        event_type="report_returned",
        actor="core-lite-ingest",
        decision=final_decision.decision,
        basis="reviewable report and receipt chain returned to founder/operator",
        output_hash=hash_dict(report),
        metadata={"report": str(REPORT_JSON), "markdown_report": str(REPORT_MD)},
    )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run core-lite recorded ingestion + CGE + sandbox loop.")
    parser.add_argument("--bundle", default="tests/fixtures/sample_ingest_bundle", help="Path to ingestible bundle directory.")
    args = parser.parse_args()

    try:
        report = run_ingestion(args.bundle)
    except Exception as exc:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        failure = {
            "schema": "stegverse_core_lite_recorded_ingestion_sandbox_loop_report.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": type(exc).__name__,
            "basis": str(exc),
            "install_performed": False,
        }
        REPORT_JSON.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(failure, indent=2, sort_keys=True))
        return 1

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())

def load_core_policy(repo_root: Path | str = ".") -> dict[str, Any]:
    root = Path(repo_root)
    policy_candidates = [
        root / "core_lite_policy.json",
        root / ".stegverse" / "core_lite_policy.json",
        root / "policy" / "core_lite_policy.json",
    ]
    for candidate in policy_candidates:
        if candidate.exists() and candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {
                    "schema": "stegverse_core_lite_policy.v1",
                    "policy_loaded": False,
                    "policy_error": "invalid_json",
                    "policy_path": candidate.as_posix(),
                    "install_authority": False,
                    "production_authority": False,
                }
    return {
        "schema": "stegverse_core_lite_policy.v1",
        "policy_loaded": False,
        "policy_path": None,
        "install_authority": False,
        "production_authority": False,
        "node_status": False,
        "finco_eligibility": False,
    }


def ingest_incoming(repo_root: Path | str = ".", *, task_id: str = "", skip_tasks: bool = False) -> dict[str, Any]:
    root = Path(repo_root)
    incoming = root / "incoming"

    if not incoming.exists():
        report = {
            "schema": "stegverse_core_lite_ingest_incoming_report.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "decision": "NO_INCOMING_DIRECTORY",
            "repo_root": root.as_posix(),
            "incoming": incoming.as_posix(),
            "task_id": task_id,
            "skip_tasks": skip_tasks,
            "install_authority": False,
            "production_authority": False,
        }
        (root / "core_lite_ingest_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report

    bundles = sorted([path for path in incoming.iterdir() if path.is_file()])
    if not bundles:
        report = {
            "schema": "stegverse_core_lite_ingest_incoming_report.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "decision": "NO_INCOMING_BUNDLES",
            "repo_root": root.as_posix(),
            "incoming": incoming.as_posix(),
            "task_id": task_id,
            "skip_tasks": skip_tasks,
            "install_authority": False,
            "production_authority": False,
        }
        (root / "core_lite_ingest_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report

    results = [run_ingestion(bundle, repo_root=root) for bundle in bundles]
    report = {
        "schema": "stegverse_core_lite_ingest_incoming_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "success": all(bool(item.get("success")) for item in results),
        "decision": "INGESTION_ATTEMPTED",
        "repo_root": root.as_posix(),
        "incoming": incoming.as_posix(),
        "bundle_count": len(bundles),
        "task_id": task_id,
        "skip_tasks": skip_tasks,
        "results": results,
        "install_authority": False,
        "production_authority": False,
    }
    (root / "core_lite_ingest_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
