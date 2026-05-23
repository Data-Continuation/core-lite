from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReceiptRecorder:
    """Append-only hash-linked receipt writer for core-lite initialization events."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.previous_receipt_hash = self._last_hash()

    @staticmethod
    def canonical_json(value: dict[str, Any]) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    @staticmethod
    def hash_value(value: dict[str, Any]) -> str:
        return hashlib.sha256(ReceiptRecorder.canonical_json(value).encode("utf-8")).hexdigest()

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

    def record(
        self,
        *,
        event_type: str,
        actor: str,
        decision: str,
        basis: str,
        input_hash: str | None = None,
        output_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        receipt = {
            "schema": "stegverse_core_lite_event_receipt.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "actor": actor,
            "decision": decision,
            "basis": basis,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "previous_receipt_hash": self.previous_receipt_hash,
            "metadata": metadata or {},
        }
        receipt["receipt_hash"] = self.hash_value(receipt)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(self.canonical_json(receipt) + "\n")
        self.previous_receipt_hash = receipt["receipt_hash"]
        return receipt

def append_receipt(repo_root: Path | str = ".", receipt: dict[str, Any] | None = None, **metadata: Any) -> dict[str, Any]:
    root = Path(repo_root)
    recorder = ReceiptRecorder(root / ".stegverse" / "receipts" / "core_lite_receipts.jsonl")
    payload = receipt if receipt is not None else {}
    if not isinstance(payload, dict):
        payload = {"value": repr(payload)}
    if metadata:
        payload = {**payload, **metadata}
    return recorder.record(
        event_type=str(payload.get("event_type", "core_lite_cli_receipt")),
        decision=str(payload.get("decision", "RECORDED")),
        basis=str(payload.get("basis", "Core-Lite CLI receipt recorded.")),
        metadata=payload,
    )
