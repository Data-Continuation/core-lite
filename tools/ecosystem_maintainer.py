#!/usr/bin/env python3
"""
Core-Lite Ecosystem Maintainer Scan

Purpose:
- scan a repository
- classify files by reality state
- detect stubs, stub-dependent files, orphan candidates, and broken local references
- write downloadable Markdown + JSON reports
- append a receipt

This script performs observe/classify/report/receipt only.
It does not mutate source files, move files, delete files, complete stubs, or create service scaffolds.
"""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "reports",
    "receipts",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".sh",
    ".toml",
    ".ini",
    ".cfg",
    ".lock",
}

CANONICAL_NAMES = {
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "requirements.txt",
}

STUB_PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
    re.compile(r"\bSTUB\b", re.IGNORECASE),
    re.compile(r"\bNOT IMPLEMENTED\b", re.IGNORECASE),
    re.compile(r"raise\s+NotImplementedError\b"),
    re.compile(r"console\.log\(['\"]TODO", re.IGNORECASE),
    re.compile(r"return\s+None\s*$", re.MULTILINE),
]

LOCAL_REF_PATTERNS = [
    re.compile(r"(?:from|import)\s+['\"](?P<path>\.{1,2}/[^'\"]+)['\"]"),
    re.compile(r"require\(['\"](?P<path>\.{1,2}/[^'\"]+)['\"]\)"),
    re.compile(r"href=['\"](?P<path>[^'\"]+)['\"]"),
    re.compile(r"src=['\"](?P<path>[^'\"]+)['\"]"),
    re.compile(r"\[[^\]]+\]\((?P<path>[^)]+)\)"),
]

PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+(?P<frommod>[a-zA-Z_][\w.]*)\s+import|import\s+(?P<importmod>[a-zA-Z_][\w.]*))", re.MULTILINE)


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds")


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_probably_text(path: Path) -> bool:
    if path.suffix in TEXT_EXTENSIONS:
        return True
    if path.name in CANONICAL_NAMES:
        return True
    return False


def should_exclude(path: Path, root: Path, exclude_dirs: set[str]) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in exclude_dirs for part in rel_parts)


def read_text(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return "", "non_utf8"
    except OSError as exc:
        return "", f"read_error:{exc}"


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def classify_stub(text: str, path: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    stripped = text.strip()

    if not stripped:
        return True, ["empty file"]

    for pattern in STUB_PATTERNS:
        if pattern.search(text):
            reasons.append(f"matched stub pattern: {pattern.pattern}")

    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
            body = tree.body
            if body and all(
                isinstance(node, (ast.Pass, ast.Expr, ast.Import, ast.ImportFrom))
                for node in body
            ):
                if any(isinstance(node, ast.Pass) for node in body):
                    reasons.append("module-level pass without implementation")
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.body:
                        reasons.append(f"function {node.name} has empty body")
                    elif all(isinstance(stmt, ast.Pass) for stmt in node.body):
                        reasons.append(f"function {node.name} only contains pass")
                    elif any(isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call) and getattr(stmt.exc.func, "id", "") == "NotImplementedError" for stmt in node.body):
                        reasons.append(f"function {node.name} raises NotImplementedError")
        except SyntaxError:
            pass

    tiny_placeholder = len(stripped) < 40 and stripped.lower() in {
        "todo",
        "placeholder",
        "stub",
        "not implemented",
        "coming soon",
    }
    if tiny_placeholder:
        reasons.append("tiny placeholder content")

    return bool(reasons), reasons


def local_reference_exists(ref: str, source_path: Path, root: Path) -> bool:
    if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return True

    clean = ref.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return True

    candidate = (source_path.parent / clean).resolve()
    if candidate.exists():
        return True

    suffixes = ["", ".md", ".py", ".js", ".ts", ".json", ".yml", ".yaml", ".html"]
    for suffix in suffixes:
        if suffix and Path(str(candidate) + suffix).exists():
            return True

    for index in ["index.html", "README.md"]:
        if (candidate / index).exists():
            return True

    return False


def find_local_refs(text: str) -> list[str]:
    refs: list[str] = []
    for pattern in LOCAL_REF_PATTERNS:
        for match in pattern.finditer(text):
            ref = match.group("path").strip()
            if ref and not ref.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                refs.append(ref)
    return sorted(set(refs))


def find_python_local_imports(text: str, path: Path, root: Path) -> list[str]:
    refs: list[str] = []
    for match in PY_IMPORT_RE.finditer(text):
        mod = match.group("frommod") or match.group("importmod") or ""
        if not mod:
            continue
        top = mod.split(".", 1)[0]
        if top in {"os", "sys", "json", "re", "pathlib", "typing", "argparse", "datetime", "hashlib", "subprocess", "shutil", "zipfile"}:
            continue
        possible = root / (mod.replace(".", "/") + ".py")
        possible_pkg = root / mod.replace(".", "/") / "__init__.py"
        if possible.exists() or possible_pkg.exists():
            refs.append(possible.relative_to(root).as_posix() if possible.exists() else possible_pkg.relative_to(root).as_posix())
    return sorted(set(refs))


def build_reference_index(files: list[dict[str, Any]]) -> dict[str, set[str]]:
    inbound: dict[str, set[str]] = {item["path"]: set() for item in files}
    path_set = set(inbound)

    for item in files:
        for ref in item.get("local_refs", []):
            source_parent = Path(item["path"]).parent
            normalized = (source_parent / ref.split("#", 1)[0].split("?", 1)[0]).as_posix()
            candidates = {
                normalized,
                normalized + ".md",
                normalized + ".py",
                normalized + ".js",
                normalized + ".ts",
                normalized + ".json",
                normalized + ".yml",
                normalized + ".yaml",
                normalized + ".html",
                f"{normalized}/index.html",
                f"{normalized}/README.md",
            }
            for candidate in candidates:
                if candidate in path_set:
                    inbound[candidate].add(item["path"])

        for ref in item.get("python_import_refs", []):
            if ref in path_set:
                inbound[ref].add(item["path"])

    return inbound


def classify_files(root: Path, exclude_dirs: set[str]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if should_exclude(path, root, exclude_dirs):
            continue

        item: dict[str, Any] = {
            "path": relpath(path, root),
            "size_bytes": path.stat().st_size,
            "extension": path.suffix,
            "class": "UNCLASSIFIED",
            "evidence": [],
            "local_refs": [],
            "broken_refs": [],
            "python_import_refs": [],
            "inbound_refs": [],
        }

        if not is_probably_text(path):
            item["class"] = "BINARY_OR_UNKNOWN"
            item["evidence"].append("non-text or unsupported extension")
            files.append(item)
            continue

        text, read_error = read_text(path)
        if read_error:
            item["class"] = "BINARY_OR_UNKNOWN"
            item["evidence"].append(read_error)
            files.append(item)
            continue

        local_refs = find_local_refs(text)
        item["local_refs"] = local_refs
        item["python_import_refs"] = find_python_local_imports(text, path, root)

        broken_refs = [
            ref for ref in local_refs
            if not local_reference_exists(ref, path, root)
        ]
        item["broken_refs"] = broken_refs

        is_stub, stub_reasons = classify_stub(text, path)
        if path.name in CANONICAL_NAMES or item["path"].startswith("core_lite/"):
            item["class"] = "CANONICAL_OR_CONTROL"
            item["evidence"].append("canonical/control file")
            if stub_reasons:
                item["evidence"].extend(stub_reasons)
        elif broken_refs:
            item["class"] = "BROKEN"
            item["evidence"].append(f"{len(broken_refs)} broken local reference(s)")
        elif is_stub:
            item["class"] = "STUB"
            item["evidence"].extend(stub_reasons)
        else:
            item["class"] = "REAL"
            item["evidence"].append("text file with no stub or broken-reference signal")

        files.append(item)

    inbound = build_reference_index(files)
    stub_paths = {item["path"] for item in files if item["class"] == "STUB"}

    for item in files:
        item["inbound_refs"] = sorted(inbound.get(item["path"], set()))

    for item in files:
        if item["class"] in {"REAL", "CANONICAL_OR_CONTROL"}:
            refs_stub = []
            source_parent = Path(item["path"]).parent
            for ref in item.get("local_refs", []):
                normalized = (source_parent / ref.split("#", 1)[0].split("?", 1)[0]).as_posix()
                possible = {
                    normalized,
                    normalized + ".md",
                    normalized + ".py",
                    normalized + ".js",
                    normalized + ".ts",
                    normalized + ".json",
                    normalized + ".yml",
                    normalized + ".yaml",
                    normalized + ".html",
                }
                refs_stub.extend(sorted(possible.intersection(stub_paths)))
            refs_stub.extend(sorted(set(item.get("python_import_refs", [])).intersection(stub_paths)))
            if refs_stub:
                item["class"] = "STUB_DEPENDENT"
                item["evidence"].append(f"depends on stub(s): {', '.join(sorted(set(refs_stub)))}")

    for item in files:
        if item["class"] == "REAL" and not item["inbound_refs"]:
            p = item["path"]
            if not (
                p.startswith("tools/")
                or p.startswith("core_lite/")
                or p.startswith("github/")
                or p.endswith("README.md")
                or Path(p).name in CANONICAL_NAMES
            ):
                item["class"] = "ORPHAN_CANDIDATE"
                item["evidence"].append("no inbound references found in scanned text files")

    return files


def summarize(files: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in files:
        counts[item["class"]] = counts.get(item["class"], 0) + 1
    return dict(sorted(counts.items()))


def append_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    receipts_dir = root / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipts_dir / "ecosystem_maintainer_receipts.jsonl"

    previous_hash = None
    if receipt_path.exists():
        lines = [line for line in receipt_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            try:
                previous_hash = json.loads(lines[-1]).get("hash")
            except json.JSONDecodeError:
                previous_hash = None

    payload = {
        "receipt_type": "core_lite.ecosystem_maintainer_scan",
        "timestamp": report["generated_at"],
        "target_root": report["target_root"],
        "file_count": report["summary"]["file_count"],
        "class_counts": report["summary"]["class_counts"],
        "mutation_count": 0,
        "result": "pass",
        "previous_hash": previous_hash,
    }
    receipt = {**payload, "hash": stable_hash(payload)}
    with receipt_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def markdown_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Core-Lite Ecosystem Maintainer Scan")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append(f"Target root: `{report['target_root']}`")
    lines.append("")
    lines.append("## Done Definition")
    lines.append("")
    lines.append("- Scan repository files.")
    lines.append("- Classify files by reality state.")
    lines.append("- Detect stubs, stub dependencies, orphan candidates, and broken local references.")
    lines.append("- Generate Markdown and JSON reports.")
    lines.append("- Emit receipt.")
    lines.append("- Perform no source mutation.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files scanned: `{report['summary']['file_count']}`")
    lines.append(f"- Result: `{report['summary']['result']}`")
    lines.append(f"- Mutations performed: `0`")
    lines.append("")
    lines.append("## Class Counts")
    lines.append("")
    for key, value in report["summary"]["class_counts"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Recommended Next Transition Blocks")
    lines.append("")
    lines.append("- STUB files: `AUTO_QUARANTINE_STUB` or `COMPLETE_LOW_RISK_STUB` after evidence review.")
    lines.append("- STUB_DEPENDENT files: `MAP_DEPENDENCY`, then complete or quarantine dependency first.")
    lines.append("- ORPHAN_CANDIDATE files: review before quarantine; do not delete automatically.")
    lines.append("- BROKEN files: `AUTO_FIX_MECHANICAL` only when the target path is obvious.")
    lines.append("")
    lines.append("## Findings")
    lines.append("")

    for item in report["files"]:
        if item["class"] in {"REAL", "BINARY_OR_UNKNOWN"}:
            continue
        lines.append(f"### {item['path']}")
        lines.append("")
        lines.append(f"- Class: `{item['class']}`")
        lines.append(f"- Size: `{item['size_bytes']}` bytes")
        if item["evidence"]:
            lines.append("- Evidence:")
            for evidence in item["evidence"]:
                lines.append(f"  - {evidence}")
        if item["broken_refs"]:
            lines.append("- Broken refs:")
            for ref in item["broken_refs"]:
                lines.append(f"  - `{ref}`")
        if item["inbound_refs"]:
            lines.append("- Inbound refs:")
            for ref in item["inbound_refs"]:
                lines.append(f"  - `{ref}`")
        lines.append("")

    lines.append("## Receipt")
    lines.append("")
    lines.append(f"- Receipt hash: `{report['receipt']['hash']}`")
    lines.append("- Receipt path: `receipts/ecosystem_maintainer_receipts.jsonl`")
    lines.append("")
    return "\n".join(lines)


def run_scan(target_root: Path, exclude_dirs: set[str]) -> tuple[dict[str, Any], int]:
    target_root = target_root.resolve()
    if not target_root.exists() or not target_root.is_dir():
        raise FileNotFoundError(f"Target root is not a directory: {target_root}")

    files = classify_files(target_root, exclude_dirs)
    class_counts = summarize(files)

    report: dict[str, Any] = {
        "generated_at": utc_now(),
        "target_root": target_root.as_posix(),
        "summary": {
            "result": "pass",
            "file_count": len(files),
            "class_counts": class_counts,
            "mutation_count": 0,
        },
        "files": files,
    }

    receipt = append_receipt(target_root, report)
    report["receipt"] = receipt

    reports_dir = target_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "ecosystem_maintainer_scan.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (reports_dir / "ecosystem_maintainer_scan.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )

    return report, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Core-Lite ecosystem maintainer scan.")
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to scan. Defaults to current directory.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Additional directory name to exclude. Can be used multiple times.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON report to stdout.",
    )
    args = parser.parse_args()

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    exclude_dirs.update(args.exclude_dir)

    try:
        report, exit_code = run_scan(Path(args.root), exclude_dirs)
    except Exception as exc:
        print(f"Maintainer scan failed: {exc}", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    print(f"Wrote {(root / 'reports' / 'ecosystem_maintainer_scan.md').as_posix()}")
    print(f"Wrote {(root / 'reports' / 'ecosystem_maintainer_scan.json').as_posix()}")
    print(f"Wrote {(root / 'receipts' / 'ecosystem_maintainer_receipts.jsonl').as_posix()}")
    print("Result: pass")
    print("Mutations performed: 0")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
