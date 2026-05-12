from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_TABLE_PATH = Path("schemas/ingestion_transition_table.json")

def load_ingestion_transition_table(repo_root: Path, table_path: Path | None = None) -> Dict[str, Any]:
    path = repo_root / (table_path or DEFAULT_TABLE_PATH)
    if not path.exists(): raise FileNotFoundError(f"ingestion transition table not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_ingestion_transition_table(payload)
    return payload

def validate_ingestion_transition_table(table: Dict[str, Any]) -> None:
    if table.get("schema") != "stegverse_ingestion_transition_table.v1": raise ValueError("unsupported ingestion transition table schema")
    transitions = table.get("transition_classes")
    if not isinstance(transitions, list) or not transitions: raise ValueError("transition table must contain transition_classes")
    outcomes = set(table.get("outcomes", []))
    seen = set()
    for item in transitions:
        tid = item.get("transition_id")
        if not isinstance(tid, str) or not tid: raise ValueError("transition class missing transition_id")
        if tid in seen: raise ValueError(f"duplicate transition_id: {tid}")
        seen.add(tid)
        allowed = item.get("allowed_outcomes")
        if not isinstance(allowed, list): raise ValueError(f"{tid} allowed_outcomes must be a list")
        unknown = sorted(set(allowed) - outcomes)
        if unknown: raise ValueError(f"{tid} has outcomes not listed in table outcomes: {unknown}")

def transition_summary(table: Dict[str, Any]) -> Dict[str, Any]:
    by_family: Dict[str, int] = {}
    for t in table["transition_classes"]:
        family = str(t.get("family", "unknown"))
        by_family[family] = by_family.get(family, 0) + 1
    return {"schema": "stegverse_ingestion_transition_table_summary.v1", "table_id": table.get("table_id"), "version": table.get("version"), "transition_count": len(table["transition_classes"]), "family_count": len(by_family), "by_family": by_family, "outcome_count": len(table.get("outcomes", []))}
