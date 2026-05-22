#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTRUCTION_PATH = Path("instructions/current/stegverse-001-command.json")
REPORT_DIR = Path("reports/current/stegverse-001-worker")
RECEIPT_DIR = Path("receipts/current/stegverse-001-worker")
REPORT_JSON = REPORT_DIR / "working_contract_report.json"
REPORT_MD = REPORT_DIR / "working_contract_report.md"
PLAN_JSON = REPORT_DIR / "working_contract_plan.json"
RECEIPTS = RECEIPT_DIR / "receipts.jsonl"


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def hash_dict(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


class ReceiptChain:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.previous_hash = self._last_hash()

    def _last_hash(self) -> str | None:
        if not self.path.exists():
            return None
        last = None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                last = json.loads(line).get("receipt_hash")
            except json.JSONDecodeError:
                continue
        return last

    def record(self, event_type: str, decision: str, basis: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        receipt = {
            "schema": "stegverse_worker_receipt.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "actor": "StegVerse-001",
            "event_type": event_type,
            "decision": decision,
            "basis": basis,
            "previous_receipt_hash": self.previous_hash,
            "metadata": metadata or {},
        }
        receipt["receipt_hash"] = hash_dict(receipt)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(receipt) + "\n")
        self.previous_hash = receipt["receipt_hash"]
        return receipt


def parse_python(path: Path) -> dict[str, Any]:
    text = read_text(path)
    contract: dict[str, Any] = {
        "path": path.as_posix(),
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "functions": [],
        "classes": [],
        "import_from": [],
        "parse_error": None,
    }
    if not text:
        return contract
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        contract["parse_error"] = f"{exc.__class__.__name__}: {exc}"
        return contract

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            contract["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            contract["classes"].append(node.name)
        elif isinstance(node, ast.ImportFrom):
            contract["import_from"].append(
                {"module": node.module or "", "names": [alias.name for alias in node.names]}
            )
    contract["functions"] = sorted(set(contract["functions"]))
    contract["classes"] = sorted(set(contract["classes"]))
    return contract


def inspect_workflows(root: Path) -> list[dict[str, Any]]:
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return []
    out = []
    for path in sorted(workflow_dir.glob("*")):
        if not path.is_file():
            continue
        text = read_text(path)
        out.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "mentions_incoming": "incoming" in text,
            "mentions_intake": "intake" in text.lower(),
            "mentions_cge": "cge" in text.lower(),
            "python_commands": re.findall(r"python[^\n]+", text),
        })
    return out


def inspect_tasks(root: Path) -> list[dict[str, Any]]:
    task_dir = root / "tools" / "tasks"
    if not task_dir.exists():
        return []
    out = []
    for path in sorted(task_dir.glob("*.json")):
        item = {"path": path.relative_to(root).as_posix(), "task_ids": [], "commands": [], "sha256": sha256_file(path), "parse_error": None}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for task in data.get("tasks", []):
                if isinstance(task, dict):
                    if task.get("task_id"):
                        item["task_ids"].append(task["task_id"])
                    if task.get("command"):
                        item["commands"].append(task["command"])
        except Exception as exc:
            item["parse_error"] = f"{exc.__class__.__name__}: {exc}"
        out.append(item)
    return out


def determine(root: Path, instruction: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    py = {
        "cli": parse_python(root / "core_lite" / "cli.py"),
        "cge": parse_python(root / "core_lite" / "cge.py"),
        "ingest": parse_python(root / "core_lite" / "ingest.py"),
        "sandbox": parse_python(root / "core_lite" / "sandbox.py"),
        "receipts": parse_python(root / "core_lite" / "receipts.py"),
    }

    cge_exports = set(py["cge"]["functions"]) | set(py["cge"]["classes"])
    observed_import_needs = []
    missing_cge_exports = []
    for module_name, contract in py.items():
        for import_item in contract.get("import_from", []):
            if import_item.get("module") == "core_lite.cge":
                need = {"importing_module": module_name, "from_module": "core_lite.cge", "names": import_item.get("names", [])}
                observed_import_needs.append(need)
                for name in need["names"]:
                    if name not in cge_exports:
                        missing_cge_exports.append({"name": name, "required_by": module_name})

    surfaces = {
        "incoming_exists": (root / "incoming").exists(),
        "reports_current_exists": (root / "reports" / "current").exists(),
        "receipts_current_exists": (root / "receipts" / "current").exists(),
        "workflows": inspect_workflows(root),
        "task_manifests": inspect_tasks(root),
    }

    transition_requirements = {
        "incoming_bundle_detected": surfaces["incoming_exists"],
        "manifest_validation_surface": py["ingest"]["exists"],
        "cge_surface": py["cge"]["exists"],
        "sandbox_surface": py["sandbox"]["exists"],
        "receipt_surface": py["receipts"]["exists"],
        "current_report_surface": surfaces["reports_current_exists"],
        "current_receipt_surface": surfaces["receipts_current_exists"],
    }

    blockers = []
    if missing_cge_exports:
        blockers.append({
            "type": "cge_contractual_inclusion",
            "basis": "Observed core-lite modules import symbols from core_lite.cge that are not currently exported.",
            "items": missing_cge_exports,
        })
    for key, ok in transition_requirements.items():
        if not ok:
            blockers.append({"type": "missing_transition_surface", "basis": f"Required transition surface not observed: {key}", "items": [key]})

    if missing_cge_exports:
        next_change = {
            "classification": "contractual_inclusion",
            "target": "core_lite/cge.py",
            "required_exports": sorted({item["name"] for item in missing_cge_exports}),
            "preserve_existing_exports": True,
            "basis": "Observed import needs require these exports before intake/CGE/sandbox can run.",
        }
    elif blockers:
        next_change = {
            "classification": "surface_completion",
            "target": "minimal_missing_transition_surface",
            "basis": "One or more required surfaces are absent.",
        }
    else:
        next_change = {
            "classification": "run_existing_intake",
            "target": "existing Core-Lite Intake workflow or intake command",
            "basis": "No structural blockers observed for current transition.",
        }

    report = {
        "schema": "stegverse_001_working_contract_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "success": True,
        "actor": instruction.get("actor"),
        "mode": instruction.get("mode"),
        "transition": instruction.get("transition"),
        "goal": instruction.get("goal"),
        "target_repo": instruction.get("target_repo"),
        "root": root.resolve().as_posix(),
        "instruction_hash": hash_dict(instruction),
        "python_contracts": py,
        "observed_import_needs": observed_import_needs,
        "cge_exports": sorted(cge_exports),
        "missing_cge_exports": missing_cge_exports,
        "surfaces": surfaces,
        "transition_requirements": transition_requirements,
        "blockers": blockers,
        "decision": "PLAN_RETURNED",
        "stop_condition": instruction.get("stop_condition"),
    }

    plan = {
        "schema": "stegverse_001_working_contract_plan.v1",
        "generated_at": report["generated_at"],
        "actor": instruction.get("actor"),
        "transition": "Core-Lite Recorded Ingestion + CGE + Sandbox Result Return",
        "decision": "RETURN_PLAN_ONLY",
        "install_authority": False,
        "production_authority": False,
        "workflow_change_authority": False,
        "incoming_submission_authority": False,
        "blockers": blockers,
        "next_admissible_change": next_change,
        "implementation_rule": "Apply only the minimal change required by observed working-structure blockers, then STOP.",
    }
    return report, plan


def write_markdown(report: dict[str, Any], plan: dict[str, Any]) -> None:
    lines = [
        "# StegVerse-001 Working Core-Lite Contract Report",
        "",
        "## Status",
        "",
        "```text",
        f"actor: {report.get('actor')}",
        f"mode: {report.get('mode')}",
        f"transition: {report.get('transition')}",
        f"decision: {report.get('decision')}",
        f"blocker_count: {len(report.get('blockers', []))}",
        "```",
        "",
        "## Missing CGE Exports",
        "",
    ]
    if report["missing_cge_exports"]:
        for item in report["missing_cge_exports"]:
            lines.append(f"- `{item['name']}` required by `{item['required_by']}`")
    else:
        lines.append("No missing CGE exports observed.")

    lines.extend(["", "## Transition Surfaces", "", "```text"])
    for key, value in report["transition_requirements"].items():
        lines.append(f"{key}: {value}")
    lines.extend(["```", "", "## Next Admissible Change", "", "```json"])
    lines.append(json.dumps(plan["next_admissible_change"], indent=2, sort_keys=True))
    lines.extend(["```", "", "## Boundary", "", "```text", "No workflow changes.", "No incoming bundle submission.", "No install.", "No production.", "Return plan and receipt.", "STOP.", "```"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

    if not INSTRUCTION_PATH.exists():
        failure = {
            "schema": "stegverse_001_working_contract_report.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": "missing_instruction",
            "missing": INSTRUCTION_PATH.as_posix(),
        }
        REPORT_JSON.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(failure, indent=2, sort_keys=True))
        return 1

    instruction = json.loads(INSTRUCTION_PATH.read_text(encoding="utf-8"))
    receipts = ReceiptChain(RECEIPTS)
    receipts.record("instruction_received", "RECEIVED", "StegVerse-001 instruction channel received current command.", {"instruction_hash": hash_dict(instruction)})

    report, plan = determine(Path("."), instruction)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PLAN_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, plan)

    receipts.record("working_contract_determined", "PLAN_RETURNED", "StegVerse-001 returned working contract report and plan, then stopped.", {"report": REPORT_JSON.as_posix(), "plan": PLAN_JSON.as_posix(), "blocker_count": len(report["blockers"])})
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
