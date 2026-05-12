from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
try:
    from .paths import utc_now
except ImportError:
    from paths import utc_now

def append_receipt(repo_root: Path, receipt: Dict[str, Any]) -> None:
    receipt_path = repo_root / ".stegverse" / "receipts" / "core_lite_receipts.jsonl"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "stegverse_core_lite_receipt.v1", "generated_at": utc_now(), **receipt}
    with receipt_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
