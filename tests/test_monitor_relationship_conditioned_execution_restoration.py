import json
from pathlib import Path

import pytest

from tools.monitor_relationship_conditioned_execution_restoration import EquivalenceError, verify


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    source = root / "evidence/source.txt"
    restored = root / "sandbox/restoration_drills/relationship_conditioned_execution/evidence/source.txt"
    source.parent.mkdir(parents=True)
    restored.parent.mkdir(parents=True)
    source.write_text("verified evidence\n", encoding="utf-8")
    restored.write_bytes(source.read_bytes())
    import hashlib
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    size = source.stat().st_size
    snapshot = {
        "snapshot_root_sha256": "root-123",
        "entries": [{"path": "evidence/source.txt", "sha256": digest, "bytes": size, "evidence_class": "fixture"}],
    }
    restoration = {
        "snapshot_root_sha256": "root-123",
        "entries": [{"source_path": "evidence/source.txt", "restored_path": "sandbox/restoration_drills/relationship_conditioned_execution/evidence/source.txt", "sha256": digest, "bytes": size}],
    }
    _write(root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json", snapshot)
    restoration_path = root / "sandbox/restoration_drills/relationship_conditioned_execution/restoration_manifest.json"
    _write(restoration_path, restoration)
    restoration_digest = hashlib.sha256(restoration_path.read_bytes()).hexdigest()
    _write(root / "receipts/rce_p0_011_authoritative_validation.json", {
        "task_id": "RCE-P0-011",
        "authoritative_completion_evidence": True,
        "decision": "SEALED_SNAPSHOT_RESTORATION_VERIFIED",
        "restoration_manifest_sha256": restoration_digest,
        "manual_actions_required": [],
    })
    _write(root / "core_lite/tasks/relationship_conditioned_execution_p0_012.json", {
        "activation_dependency": {"satisfied": False},
        "status": "WAITING_AUTOMATED_PREDECESSOR",
        "blocked_by": ["pending"],
    })
    return root


def test_attests_three_way_equivalence(tmp_path):
    root = _fixture(tmp_path)
    result = verify(root)
    assert result["decision"] == "RESTORATION_EQUIVALENCE_ATTESTED"
    assert result["entry_count"] == 1
    assert result["manual_actions_required"] == []


def test_denies_restored_content_drift(tmp_path):
    root = _fixture(tmp_path)
    restored = root / "sandbox/restoration_drills/relationship_conditioned_execution/evidence/source.txt"
    restored.write_text("changed\n", encoding="utf-8")
    with pytest.raises(EquivalenceError, match="hash divergence"):
        verify(root)


def test_denies_snapshot_root_divergence(tmp_path):
    root = _fixture(tmp_path)
    path = root / "sandbox/restoration_drills/relationship_conditioned_execution/restoration_manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["snapshot_root_sha256"] = "other-root"
    _write(path, value)
    import hashlib
    receipt = root / "receipts/rce_p0_011_authoritative_validation.json"
    receipt_value = json.loads(receipt.read_text(encoding="utf-8"))
    receipt_value["restoration_manifest_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    _write(receipt, receipt_value)
    with pytest.raises(EquivalenceError, match="snapshot root divergence"):
        verify(root)


def test_denies_invalid_predecessor(tmp_path):
    root = _fixture(tmp_path)
    receipt = root / "receipts/rce_p0_011_authoritative_validation.json"
    value = json.loads(receipt.read_text(encoding="utf-8"))
    value["authoritative_completion_evidence"] = False
    _write(receipt, value)
    with pytest.raises(EquivalenceError, match="not authoritatively complete"):
        verify(root)
