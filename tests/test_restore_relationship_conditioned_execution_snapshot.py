import hashlib
import json
from pathlib import Path

import pytest

from tools.restore_relationship_conditioned_execution_snapshot import RestorationError, restore


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    evidence = root / "receipts/example.json"
    _write(evidence, {"ok": True})
    entry = {
        "path": "receipts/example.json",
        "evidence_class": "authoritative_receipt",
        "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        "bytes": evidence.stat().st_size,
    }
    root_material = {
        "index_sha256": "1" * 64,
        "predecessor_receipt_sha256": "2" * 64,
        "entries": [entry],
    }
    snapshot = {
        "snapshot_root_sha256": hashlib.sha256(_canonical(root_material)).hexdigest(),
        "reconstruction_index_sha256": root_material["index_sha256"],
        "source_receipt_sha256": root_material["predecessor_receipt_sha256"],
        "entries": [entry],
    }
    snapshot_path = root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
    _write(snapshot_path, snapshot)
    _write(
        root / "receipts/rce_p0_010_authoritative_validation.json",
        {
            "task_id": "RCE-P0-010",
            "authoritative_completion_evidence": True,
            "decision": "SANDBOX_EVIDENCE_SNAPSHOT_SEALED",
            "snapshot_manifest_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
            "manual_actions_required": [],
        },
    )
    _write(
        root / "core_lite/tasks/relationship_conditioned_execution_p0_011.json",
        {"activation_dependency": {"satisfied": False}, "status": "WAITING_AUTOMATED_PREDECESSOR", "blocked_by": []},
    )
    return root


def test_restores_and_verifies_snapshot(tmp_path):
    root = _fixture(tmp_path)
    result = restore(root)
    assert result["decision"] == "SEALED_SNAPSHOT_RESTORATION_VERIFIED"
    assert result["restored_entry_count"] == 1
    restored = root / result["entries"][0]["restored_path"]
    assert restored.read_bytes() == (root / "receipts/example.json").read_bytes()
    assert result["manual_actions_required"] == []


def test_denies_tampered_source(tmp_path):
    root = _fixture(tmp_path)
    (root / "receipts/example.json").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(RestorationError, match="source evidence changed"):
        restore(root)


def test_denies_bad_snapshot_root(tmp_path):
    root = _fixture(tmp_path)
    path = root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json"
    value = json.loads(path.read_text())
    value["snapshot_root_sha256"] = "0" * 64
    _write(path, value)
    receipt = root / "receipts/rce_p0_010_authoritative_validation.json"
    receipt_value = json.loads(receipt.read_text())
    receipt_value["snapshot_manifest_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    _write(receipt, receipt_value)
    with pytest.raises(RestorationError, match="snapshot root mismatch"):
        restore(root)


def test_denies_invalid_predecessor(tmp_path):
    root = _fixture(tmp_path)
    path = root / "receipts/rce_p0_010_authoritative_validation.json"
    value = json.loads(path.read_text())
    value["authoritative_completion_evidence"] = False
    _write(path, value)
    with pytest.raises(RestorationError, match="not authoritatively complete"):
        restore(root)
