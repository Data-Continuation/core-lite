from __future__ import annotations

import json
from pathlib import Path

from core_lite.receipts import append_receipt


def test_append_receipt_supplies_default_actor_and_type(tmp_path: Path) -> None:
    receipt = append_receipt(
        tmp_path,
        {
            "type": "registry_topology_fingerprint_refresh",
            "repository": "Data-Continuation/core-lite",
            "success": True,
        },
    )

    assert receipt["actor"] == "core-lite"
    assert receipt["event_type"] == "registry_topology_fingerprint_refresh"
    assert receipt["decision"] == "RECORDED"
    assert receipt["basis"] == "Core-Lite CLI receipt recorded."
    assert receipt["metadata"]["success"] is True

    receipt_log = tmp_path / ".stegverse" / "receipts" / "core_lite_receipts.jsonl"
    assert receipt_log.exists()

    lines = receipt_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    recorded = json.loads(lines[0])
    assert recorded["receipt_hash"] == receipt["receipt_hash"]
    assert recorded["actor"] == "core-lite"


def test_append_receipt_preserves_explicit_actor_event_type_and_hashes(tmp_path: Path) -> None:
    receipt = append_receipt(
        tmp_path,
        {
            "event_type": "source_state_index_generated",
            "actor": "core-lite-intake",
            "decision": "ALLOW",
            "basis": "source state index generated during intake",
            "input_hash": "abc",
            "output_hash": "def",
        },
    )

    assert receipt["actor"] == "core-lite-intake"
    assert receipt["event_type"] == "source_state_index_generated"
    assert receipt["decision"] == "ALLOW"
    assert receipt["basis"] == "source state index generated during intake"
    assert receipt["input_hash"] == "abc"
    assert receipt["output_hash"] == "def"
