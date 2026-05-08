#!/usr/bin/env python3
"""
Core-Lite Capability Gap Planner

Reads a target repository and generates:
- reports/capability_gap_plan.md
- reports/capability_gap_plan.json
- receipts/capability_gap_receipts.jsonl

Purpose:
Detect when a repository is clean but underbuilt relative to its apparent product role.

This tool performs zero source mutations.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_CAPABILITIES = {
    "scanner": {
        "description": "Repository scanning / metadata extraction",
        "signals": ["src/scanner", "scanner", "scan", "commit_metadata"],
        "expected_files": ["src/scanner"],
    },
    "classifier": {
        "description": "Finding classification and severity classification",
        "signals": ["src/classifier", "classifier", "severity_rules", "severity"],
        "expected_files": ["src/classifier"],
    },
    "sanitizer": {
        "description": "Sanitization / remediation planning",
        "signals": ["src/sanitizer", "sanitizer", "sanitize", "redact"],
        "expected_files": ["src/sanitizer"],
    },
    "reporter": {
        "description": "Markdown/JSON report generation",
        "signals": ["src/reporter", "reporter", "report", "reports"],
        "expected_files": ["src/reporter"],
    },
    "config": {
        "description": "Configuration registry and rule configuration",
        "signals": ["config/", "config", "ecosystems.yaml", "severity_rules.yaml"],
        "expected_files": ["config/ecosystems.yaml", "config/severity_rules.yaml"],
    },
    "operations_docs": {
        "description": "Operator workflow and usage documentation",
        "signals": ["docs/OPERATIONS.md", "operations", "usage"],
        "expected_files": ["docs/OPERATIONS.md"],
    },
    "cli_or_entrypoint": {
        "description": "Executable command entrypoint for local or CI operation",
        "signals": ["cli", "main", "__main__", "argparse", "click", "typer"],
        "expected_files": [],
    },
    "tests": {
        "description": "Automated tests for scanner/classifier/sanitizer/reporter behavior",
        "signals": ["tests/", "pytest", "unittest"],
        "expected_files": ["tests"],
    },
    "workflow": {
        "description": "GitHub Actions workflow for running product checks",
        "signals": [".github/workflows", "github/workflows"],
        "expected_files": [".github/workflows", "github/workflows"],
    },
}


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def list_repo_files(root: Path) -> list[str]:
    ignored = {".git", "reports", "receipts", "__pycache__", ".pytest_cache", "node_modules"}
    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(root).parts)
        if parts.intersection(ignored):
            continue
        files.append(rel(path, root))
    return files


def list_repo_dirs(root: Path) -> list[str]:
    ignored = {".git", "reports", "receipts", "__pycache__", ".pytest_cache", "node_modules"}
    dirs: set[str] = set()
    for path in sorted(root.rglob("*")):
        if not path.is_dir():
            continue
        parts = set(path.relative_to(root).parts)
        if parts.intersection(ignored):
            continue
        dirs.add(rel(path, root))
    return sorted(dirs)


def path_exists(root: Path, path_text: str) -> bool:
    return (root / path_text).exists()


def non_gitkeep_files_under(root: Path, dir_text: str) -> list[str]:
    directory = root / dir_text
    if not directory.exists() or not directory.is_dir():
        return []
    out: list[str] = []
    for path in directory.rglob("*"):
        if path.is_file() and path.name != ".gitkeep":
            out.append(rel(path, root))
    return sorted(out)


def collect_text_corpus(root: Path, files: list[str]) -> str:
    chunks: list[str] = []
    for file_path in files:
        path = root / file_path
        if path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".toml"} or path.name in {"README.md"}:
            chunks.append(file_path)
            chunks.append(read_text_safe(path)[:20000])
    return "\n".join(chunks).lower()


def infer_repo_role(root: Path, files: list[str], dirs: list[str], corpus: str) -> dict[str, Any]:
    role_terms = {
        "footprint-auditor": ["footprint", "auditor", "audit", "metadata", "exposure", "sanitize", "severity"],
        "core-lite": ["core-lite", "transition", "workstream", "receipt", "friction"],
        "formalism": ["formalism", "axiom", "theorem", "proof"],
    }

    scores: dict[str, int] = {}
    joined_paths = "\n".join(files + dirs).lower()
    combined = joined_paths + "\n" + corpus

    for role, terms in role_terms.items():
        scores[role] = sum(combined.count(term) for term in terms)

    best_role = max(scores, key=scores.get) if scores else "unknown"
    confidence = "low"
    if scores.get(best_role, 0) >= 8:
        confidence = "high"
    elif scores.get(best_role, 0) >= 3:
        confidence = "medium"

    return {
        "role": best_role if scores.get(best_role, 0) > 0 else "unknown",
        "confidence": confidence if scores.get(best_role, 0) > 0 else "low",
        "scores": scores,
    }


def evaluate_capability(root: Path, capability_id: str, spec: dict[str, Any], files: list[str], dirs: list[str], corpus: str) -> dict[str, Any]:
    evidence: list[str] = []
    missing: list[str] = []

    path_text = "\n".join(files + dirs).lower()
    signals = spec.get("signals", [])
    signal_hits = [signal for signal in signals if signal.lower() in path_text or signal.lower() in corpus]

    if signal_hits:
        evidence.append(f"signal hit(s): {', '.join(signal_hits)}")

    expected_files = spec.get("expected_files", [])
    for expected in expected_files:
        if path_exists(root, expected):
            evidence.append(f"expected path exists: {expected}")
        else:
            missing.append(f"expected path missing: {expected}")

    implementation_files: list[str] = []
    for expected in expected_files:
        if expected.endswith((".yaml", ".yml", ".md", ".json", ".py")):
            if path_exists(root, expected):
                implementation_files.append(expected)
        else:
            implementation_files.extend(non_gitkeep_files_under(root, expected))

    if implementation_files:
        evidence.append(f"implementation file(s): {', '.join(implementation_files[:8])}")

    status = "absent"
    risk = "medium"
    recommended_transition = "DETECT_CAPABILITY_GAP"

    if implementation_files:
        status = "implemented_or_seeded"
        risk = "low"
        recommended_transition = "NO_ACTION"
    elif signal_hits and expected_files and all(path_exists(root, expected) for expected in expected_files):
        status = "placeholder_only"
        risk = "medium"
        recommended_transition = "PLAN_CAPABILITY_COMPLETION"
    elif signal_hits:
        status = "signaled_missing"
        risk = "high"
        recommended_transition = "PLAN_CAPABILITY_COMPLETION"
    elif missing:
        status = "missing"
        risk = "medium"
        recommended_transition = "PLAN_CAPABILITY_COMPLETION"

    return {
        "capability_id": capability_id,
        "description": spec["description"],
        "status": status,
        "risk": risk,
        "recommended_transition_block": recommended_transition,
        "evidence": evidence,
        "missing": missing,
        "implementation_files": implementation_files,
    }


def append_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    receipt_path = root / "receipts" / "capability_gap_receipts.jsonl"
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
        "receipt_type": "core_lite.capability_gap_plan",
        "timestamp": report["generated_at"],
        "result": report["summary"]["result"],
        "repo_role": report["repo_role"]["role"],
        "capability_count": report["summary"]["capability_count"],
        "missing_or_placeholder_count": report["summary"]["missing_or_placeholder_count"],
        "implemented_or_seeded_count": report["summary"]["implemented_or_seeded_count"],
        "mutation_count": 0,
        "previous_hash": previous_hash,
    }
    receipt = {**payload, "hash": stable_hash(payload)}

    with receipt_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")

    return receipt


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Core-Lite Capability Gap Plan")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append(f"Target root: `{report['target_root']}`")
    lines.append("")
    lines.append("## Done Definition")
    lines.append("")
    lines.append("- Read repository role signals.")
    lines.append("- Read directory and file structure.")
    lines.append("- Infer expected capabilities.")
    lines.append("- Classify missing, placeholder-only, and implemented/seeded capabilities.")
    lines.append("- Generate Markdown and JSON reports.")
    lines.append("- Emit receipt.")
    lines.append("- Perform no source mutation.")
    lines.append("")
    lines.append("## Repository Role")
    lines.append("")
    lines.append(f"- Role: `{report['repo_role']['role']}`")
    lines.append(f"- Confidence: `{report['repo_role']['confidence']}`")
    lines.append(f"- Scores: `{report['repo_role']['scores']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in report["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Capabilities")
    lines.append("")
    for item in report["capabilities"]:
        lines.append(f"### {item['capability_id']} — {item['description']}")
        lines.append("")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Risk: `{item['risk']}`")
        lines.append(f"- Recommended transition block: `{item['recommended_transition_block']}`")
        if item["implementation_files"]:
            lines.append("- Implementation files:")
            for value in item["implementation_files"]:
                lines.append(f"  - `{value}`")
        if item["missing"]:
            lines.append("- Missing:")
            for value in item["missing"]:
                lines.append(f"  - {value}")
        if item["evidence"]:
            lines.append("- Evidence:")
            for value in item["evidence"]:
                lines.append(f"  - {value}")
        lines.append("")
    lines.append("## Receipt")
    lines.append("")
    lines.append(f"- Receipt hash: `{report['receipt']['hash']}`")
    lines.append("- Receipt path: `receipts/capability_gap_receipts.jsonl`")
    lines.append("")
    return "\n".join(lines)


def build_report(root: Path) -> tuple[dict[str, Any], int]:
    target = root.resolve()
    files = list_repo_files(target)
    dirs = list_repo_dirs(target)
    corpus = collect_text_corpus(target, files)
    repo_role = infer_repo_role(target, files, dirs, corpus)

    capabilities = [
        evaluate_capability(target, cap_id, spec, files, dirs, corpus)
        for cap_id, spec in EXPECTED_CAPABILITIES.items()
    ]

    status_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    for item in capabilities:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
        risk_counts[item["risk"]] = risk_counts.get(item["risk"], 0) + 1

    missing_or_placeholder = sum(
        1 for item in capabilities
        if item["status"] in {"missing", "signaled_missing", "placeholder_only", "absent"}
    )
    implemented = sum(1 for item in capabilities if item["status"] == "implemented_or_seeded")

    report: dict[str, Any] = {
        "generated_at": now(),
        "target_root": target.as_posix(),
        "repo_role": repo_role,
        "summary": {
            "result": "pass",
            "file_count": len(files),
            "directory_count": len(dirs),
            "capability_count": len(capabilities),
            "implemented_or_seeded_count": implemented,
            "missing_or_placeholder_count": missing_or_placeholder,
            "mutation_count": 0,
            "status_counts": dict(sorted(status_counts.items())),
            "risk_counts": dict(sorted(risk_counts.items())),
        },
        "capabilities": capabilities,
    }

    report["receipt"] = append_receipt(target, report)

    reports_dir = target / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "capability_gap_plan.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (reports_dir / "capability_gap_plan.md").write_text(
        render_markdown(report),
        encoding="utf-8",
    )

    return report, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Core-Lite capability gap plan.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    try:
        report, code = build_report(root)
    except Exception as exc:
        print(f"Capability gap planning failed: {exc}")
        return 2

    print(f"Wrote {(root / 'reports' / 'capability_gap_plan.md').as_posix()}")
    print(f"Wrote {(root / 'reports' / 'capability_gap_plan.json').as_posix()}")
    print(f"Wrote {(root / 'receipts' / 'capability_gap_receipts.jsonl').as_posix()}")
    print(f"Result: {report['summary']['result']}")
    print(f"Missing or placeholder capabilities: {report['summary']['missing_or_placeholder_count']}")
    print("Mutations performed: 0")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return code


if __name__ == "__main__":
    raise SystemExit(main())
