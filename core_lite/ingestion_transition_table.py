from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_TABLE_PATH = Path("schemas/ingestion_transition_table.json")


def load_ingestion_transition_table(repo_root: Path, table_path: Path | None = None) -> Dict[str, Any]:
    path = repo_root / (table_path or DEFAULT_TABLE_PATH)
    if not path.exists():
        raise FileNotFoundError(f"ingestion transition table not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_ingestion_transition_table(payload)
    return payload


def validate_ingestion_transition_table(table: Dict[str, Any]) -> None:
    if table.get("schema") != "stegverse_ingestion_transition_table.v1":
        raise ValueError("unsupported ingestion transition table schema")
    transitions = table.get("transition_classes")
    if not isinstance(transitions, list) or not transitions:
        raise ValueError("transition table must contain transition_classes")
    outcomes = set(table.get("outcomes", []))
    seen = set()
    for item in transitions:
        transition_id = item.get("transition_id")
        if not isinstance(transition_id, str) or not transition_id:
            raise ValueError("transition class missing transition_id")
        if transition_id in seen:
            raise ValueError(f"duplicate transition_id: {transition_id}")
        seen.add(transition_id)
        required_fields = item.get("required_fields")
        if not isinstance(required_fields, list) or not all(isinstance(x, str) for x in required_fields):
            raise ValueError(f"{transition_id} required_fields must be a string list")
        allowed_outcomes = item.get("allowed_outcomes")
        if not isinstance(allowed_outcomes, list) or not all(isinstance(x, str) for x in allowed_outcomes):
            raise ValueError(f"{transition_id} allowed_outcomes must be a string list")
        unknown = sorted(set(allowed_outcomes) - outcomes)
        if unknown:
            raise ValueError(f"{transition_id} has outcomes not listed in table outcomes: {unknown}")


def transition_summary(table: Dict[str, Any]) -> Dict[str, Any]:
    by_family = {}
    for transition in table["transition_classes"]:
        family = str(transition.get("family", "unknown"))
        by_family[family] = by_family.get(family, 0) + 1
    return {
        "schema": "stegverse_ingestion_transition_table_summary.v1",
        "table_id": table.get("table_id"),
        "version": table.get("version"),
        "transition_count": len(table["transition_classes"]),
        "family_count": len(by_family),
        "by_family": by_family,
        "outcome_count": len(table.get("outcomes", [])),
    }
