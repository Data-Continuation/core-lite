#!/usr/bin/env python3
"""
Core-Lite Ecosystem Maintainer Scan

Scan-only maintainer:
- classifies repository files
- writes reports/ecosystem_maintainer_scan.md
- writes reports/ecosystem_maintainer_scan.json
- appends receipts/ecosystem_maintainer_receipts.jsonl
- performs zero source mutations

Classifier hardening:
- workflow files are CANONICAL_OR_CONTROL
- core_lite registry files are CANONICAL_OR_CONTROL
- repository config files are CANONICAL_OR_CONTROL
- docs files are SUPPORT_ARTIFACT unless they are README.md
- .gitkeep files are SUPPORT_ARTIFACT
- src files are REAL unless they have direct stub or broken-reference evidence
- Python stub classification uses executable AST evidence, not keyword matches in identifiers/comments/strings
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXCLUDE_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", "dist", "build", ".next", ".venv", "venv", "reports", "receipts",
}

TEXT_EXTENSIONS = {
    ".md", ".txt", ".yml", ".yaml", ".json", ".py", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".sh", ".toml", ".ini", ".cfg", ".lock",
}

CANONICAL_NAMES = {
    "README.md", "LICENSE", "pyproject.toml", "package.json", "package-lock.json",
    "requirements.txt",
}

SUPPORT_NAMES = {"UPLOAD_MAP.txt", "VERIFY_RESULT.txt", ".gitkeep"}

STD_IMPORTS = {
    "argparse", "ast", "datetime", "hashlib", "io", "json", "os", "pathlib",
    "re", "sys", "tokenize", "typing", "subprocess", "shutil", "zipfile",
}

TEXT_STUB_PATTERNS = [
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bFIXME\b", re.I),
    re.compile(r"\bPLACEHOLDER\b", re.I),
    re.compile(r"\bSTUB\b", re.I),
    re.compile(r"\bNOT IMPLEMENTED\b", re.I),
]

LOCAL_REF_PATTERNS = [
    re.compile(r"require\(['\"](?P<path>\.{1,2}/[^'\"]+)['\"]\)"),
    re.compile(r"from\s+['\"](?P<path>\.{1,2}/[^'\"]+)['\"]"),
    re.compile(r"import\s+['\"](?P<path>\.{1,2}/[^'\"]+)['\"]"),
    re.compile(r"href=['\"](?P<path>[^'\"]+)['\"]"),
    re.compile(r"src=['\"](?P<path>[^'\"]+)['\"]"),
    re.compile(r"\[[^\]]+\]\((?P<path>[^)]+)\)"),
]

PY_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+(?P<frommod>[a-zA-Z_][\w.]*)\s+import|import\s+(?P<importmod>[a-zA-Z_][\w.]*))",
    re.M,
)


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def sha(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def skip(path: Path, root: Path, exclude_dirs: set[str]) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in exclude_dirs for part in parts)


def is_text(path: Path) -> bool:
    return path.suffix in TEXT_EXTENSIONS or path.name in CANONICAL_NAMES or path.name in SUPPORT_NAMES


def is_workflow(path_str: str) -> bool:
    return path_str.startswith(".github/workflows/") or path_str.startswith("github/workflows/")


def is_control(path_str: str) -> bool:
    return (
        path_str.startswith("core_lite/")
        or path_str.startswith("config/")
        or path_str in {"README.md", "pyproject.toml", "package.json", "requirements.txt"}
    )


def is_support(path_str: str, path: Path) -> bool:
    return (
        path.name in SUPPORT_NAMES
        or path_str.startswith("docs/")
        or path_str.startswith("examples/")
    )


def read(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return "", "non_utf8"
    except OSError as exc:
        return "", f"read_error:{exc}"


def python_stub_reasons(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return ["empty file"]

    if len(stripped) < 40 and stripped.lower() in {"todo", "placeholder", "stub", "not implemented"}:
        return ["tiny placeholder content"]

    reasons: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ["python syntax error"]

    module_body = [
        node for node in tree.body
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Expr))
    ]
    if module_body and all(isinstance(node, ast.Pass) for node in module_body):
        reasons.append("module body only contains pass")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = [
                stmt for stmt in node.body
                if not (
                    isinstance(stmt, ast.Expr)
                    and isinstance(getattr(stmt, "value", None), ast.Constant)
                    and isinstance(stmt.value.value, str)
                )
            ]

            if not body:
                reasons.append(f"function {node.name} has no executable body after docstring")
                continue

            if all(isinstance(stmt, ast.Pass) for stmt in body):
                reasons.append(f"function {node.name} only contains pass")

            if any(
                isinstance(stmt, ast.Raise)
                and (
                    (
                        isinstance(stmt.exc, ast.Call)
                        and getattr(stmt.exc.func, "id", "") == "NotImplementedError"
                    )
                    or (
                        isinstance(stmt.exc, ast.Name)
                        and stmt.exc.id == "NotImplementedError"
                    )
                )
                for stmt in body
            ):
                reasons.append(f"function {node.name} raises NotImplementedError")

    return reasons


def text_stub_reasons(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return ["empty file"]

    reasons = [f"matched stub pattern: {pattern.pattern}" for pattern in TEXT_STUB_PATTERNS if pattern.search(text)]

    if len(stripped) < 40 and stripped.lower() in {"todo", "placeholder", "stub", "not implemented"}:
        reasons.append("tiny placeholder content")

    return reasons


def stub_reasons(text: str, path: Path) -> list[str]:
    if path.suffix == ".py":
        return python_stub_reasons(text)
    return text_stub_reasons(text)


def local_ref_exists(ref: str, src: Path) -> bool:
    if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return True
    clean = ref.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return True
    base = (src.parent / clean).resolve()
    if base.exists():
        return True
    for suffix in [".md", ".py", ".js", ".ts", ".json", ".yml", ".yaml", ".html"]:
        if Path(str(base) + suffix).exists():
            return True
    return (base / "index.html").exists() or (base / "README.md").exists()


def find_refs(text: str, path: Path) -> list[str]:
    if path.suffix == ".py":
        return []

    refs: set[str] = set()
    for pattern in LOCAL_REF_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group("path").strip()
            if value and not value.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                refs.add(value)
    return sorted(refs)


def py_import_refs(text: str, root: Path) -> list[str]:
    refs: set[str] = set()
    for match in PY_IMPORT_RE.finditer(text):
        mod = match.group("frommod") or match.group("importmod") or ""
        top = mod.split(".", 1)[0]
        if not mod or top in STD_IMPORTS:
            continue
        f = root / (mod.replace(".", "/") + ".py")
        pkg = root / mod.replace(".", "/") / "__init__.py"
        if f.exists():
            refs.add(f.relative_to(root).as_posix())
        elif pkg.exists():
            refs.add(pkg.relative_to(root).as_posix())
    return sorted(refs)


def build_inbound(files: list[dict[str, Any]]) -> dict[str, set[str]]:
    paths = {f["path"] for f in files}
    inbound = {p: set() for p in paths}
    for item in files:
        parent = Path(item["path"]).parent
        for ref_value in item.get("local_refs", []):
            clean = ref_value.split("#", 1)[0].split("?", 1)[0]
            base = (parent / clean).as_posix()
            candidates = {
                base, base + ".md", base + ".py", base + ".js", base + ".ts",
                base + ".json", base + ".yml", base + ".yaml", base + ".html",
                f"{base}/index.html", f"{base}/README.md",
            }
            for candidate in candidates & paths:
                inbound[candidate].add(item["path"])
        for ref_value in item.get("python_import_refs", []):
            if ref_value in paths:
                inbound[ref_value].add(item["path"])
    return inbound


def classify(root: Path, exclude_dirs: set[str]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or skip(path, root, exclude_dirs):
            continue

        path_str = rel(path, root)
        item: dict[str, Any] = {
            "path": path_str,
            "size_bytes": path.stat().st_size,
            "extension": path.suffix,
            "class": "UNCLASSIFIED",
            "evidence": [],
            "local_refs": [],
            "broken_refs": [],
            "python_import_refs": [],
            "inbound_refs": [],
        }

        if not is_text(path):
            item["class"] = "BINARY_OR_UNKNOWN"
            item["evidence"].append("non-text or unsupported extension")
            files.append(item)
            continue

        text, err = read(path)
        if err:
            item["class"] = "BINARY_OR_UNKNOWN"
            item["evidence"].append(err)
            files.append(item)
            continue

        item["local_refs"] = find_refs(text, path)
        item["python_import_refs"] = py_import_refs(text, root)
        item["broken_refs"] = [r for r in item["local_refs"] if not local_ref_exists(r, path)]

        if path.name in CANONICAL_NAMES or is_workflow(path_str) or is_control(path_str):
            item["class"] = "CANONICAL_OR_CONTROL"
            item["evidence"].append("canonical/control file")
            files.append(item)
            continue

        if is_support(path_str, path):
            item["class"] = "SUPPORT_ARTIFACT"
            item["evidence"].append("support artifact for upload, verification, documentation, examples, or empty directory retention")
            files.append(item)
            continue

        reasons = stub_reasons(text, path)
        if item["broken_refs"]:
            item["class"] = "BROKEN"
            item["evidence"].append(f"{len(item['broken_refs'])} broken local reference(s)")
        elif reasons:
            item["class"] = "STUB"
            item["evidence"].extend(reasons)
        else:
            item["class"] = "REAL"
            item["evidence"].append("text file with no stub or broken-reference signal")
        files.append(item)

    inbound = build_inbound(files)
    stub_paths = {i["path"] for i in files if i["class"] == "STUB"}
    for item in files:
        item["inbound_refs"] = sorted(inbound.get(item["path"], set()))

    for item in files:
        if item["class"] in {"REAL", "CANONICAL_OR_CONTROL", "SUPPORT_ARTIFACT"}:
            parent = Path(item["path"]).parent
            refs_stub: set[str] = set()
            for ref_value in item.get("local_refs", []):
                base = (parent / ref_value.split("#", 1)[0].split("?", 1)[0]).as_posix()
                refs_stub.update({base, base + ".py", base + ".md", base + ".js", base + ".ts"} & stub_paths)
            refs_stub.update(set(item.get("python_import_refs", [])) & stub_paths)
            if refs_stub:
                item["class"] = "STUB_DEPENDENT"
                item["evidence"].append(f"depends on stub(s): {', '.join(sorted(refs_stub))}")

    for item in files:
        if item["class"] == "REAL" and not item["inbound_refs"]:
            p = item["path"]
            if not (
                p.startswith("tools/")
                or p.startswith("src/")
                or p.startswith("core_lite/")
                or is_workflow(p)
                or p.endswith("README.md")
                or Path(p).name in CANONICAL_NAMES
            ):
                item["class"] = "ORPHAN_CANDIDATE"
                item["evidence"].append("no inbound references found in scanned text files")

    return files


def counts(files: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in files:
        out[item["class"]] = out.get(item["class"], 0) + 1
    return dict(sorted(out.items()))


def append_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    path = root / "receipts" / "ecosystem_maintainer_receipts.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = None
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
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
    receipt = {**payload, "hash": sha(payload)}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Core-Lite Ecosystem Maintainer Scan",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Target root: `{report['target_root']}`",
        "",
        "## Done Definition",
        "",
        "- Scan repository files.",
        "- Classify files by reality state.",
        "- Detect stubs, stub dependencies, orphan candidates, and broken local references.",
        "- Generate Markdown and JSON reports.",
        "- Emit receipt.",
        "- Perform no source mutation.",
        "",
        "## Summary",
        "",
        f"- Files scanned: `{report['summary']['file_count']}`",
        f"- Result: `{report['summary']['result']}`",
        "- Mutations performed: `0`",
        "",
        "## Class Counts",
        "",
    ]
    for k, v in report["summary"]["class_counts"].items():
        lines.append(f"- {k}: `{v}`")
    lines += [
        "",
        "## Recommended Next Transition Blocks",
        "",
        "- STUB files: `AUTO_QUARANTINE_STUB` or `COMPLETE_LOW_RISK_STUB` after evidence review.",
        "- STUB_DEPENDENT files: `MAP_DEPENDENCY`, then complete or quarantine dependency first.",
        "- ORPHAN_CANDIDATE files: review before quarantine; do not delete automatically.",
        "- BROKEN files: `AUTO_FIX_MECHANICAL` only when the target path is obvious.",
        "- SUPPORT_ARTIFACT files: keep unless superseded by bundle registry policy.",
        "",
        "## Findings",
        "",
    ]
    for item in report["files"]:
        if item["class"] in {"REAL", "BINARY_OR_UNKNOWN"}:
            continue
        lines += [f"### {item['path']}", "", f"- Class: `{item['class']}`", f"- Size: `{item['size_bytes']}` bytes"]
        if item["evidence"]:
            lines.append("- Evidence:")
            lines.extend(f"  - {e}" for e in item["evidence"])
        if item["broken_refs"]:
            lines.append("- Broken refs:")
            lines.extend(f"  - `{r}`" for r in item["broken_refs"])
        if item["inbound_refs"]:
            lines.append("- Inbound refs:")
            lines.extend(f"  - `{r}`" for r in item["inbound_refs"])
        lines.append("")
    lines += [
        "## Receipt",
        "",
        f"- Receipt hash: `{report['receipt']['hash']}`",
        "- Receipt path: `receipts/ecosystem_maintainer_receipts.jsonl`",
        "",
    ]
    return "\n".join(lines)


def run_scan(target_root: Path, exclude_dirs: set[str]) -> tuple[dict[str, Any], int]:
    root = target_root.resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Target root is not a directory: {root}")

    files = classify(root, exclude_dirs)
    report: dict[str, Any] = {
        "generated_at": now(),
        "target_root": root.as_posix(),
        "summary": {
            "result": "pass",
            "file_count": len(files),
            "class_counts": counts(files),
            "mutation_count": 0,
        },
        "files": files,
    }
    report["receipt"] = append_receipt(root, report)

    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "ecosystem_maintainer_scan.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "ecosystem_maintainer_scan.md").write_text(to_markdown(report), encoding="utf-8")
    return report, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Core-Lite ecosystem maintainer scan.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--exclude-dir", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    exclude_dirs = set(EXCLUDE_DIRS)
    exclude_dirs.update(args.exclude_dir)

    try:
        report, code = run_scan(Path(args.root), exclude_dirs)
    except Exception as exc:
        print(f"Maintainer scan failed: {exc}")
        return 2

    root = Path(args.root).resolve()
    print(f"Wrote {(root / 'reports' / 'ecosystem_maintainer_scan.md').as_posix()}")
    print(f"Wrote {(root / 'reports' / 'ecosystem_maintainer_scan.json').as_posix()}")
    print(f"Wrote {(root / 'receipts' / 'ecosystem_maintainer_receipts.jsonl').as_posix()}")
    print("Result: pass")
    print("Mutations performed: 0")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
