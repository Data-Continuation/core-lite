import hashlib
import json
from pathlib import Path

import pytest

from tools.seal_relationship_conditioned_execution_snapshot import SnapshotSealError, seal


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    evidence = root / "receipts/example.json"
    _write_json(evidence, {"example": True})
    entry = {
        "path": "receipts/example.json",
        "evidence_class": "receipt",
        "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        "bytes": evidence.stat().st_size,
    }
    _write_json(root / "reports/rce_p0_009_reconstruction_index.json", {"entries": [entry]})
    _write_json(
        root / "receipts/rce_p0_009_authoritative_validation.json",
        {
            "task_id": "RCE-P0-009",
            "authoritative_completion_evidence": True,
            "decision": "RECONSTRUCTION_INDEX_VERIFIED",
            "manual_actions_required": [],
        },
    )
    _write_json(
        root / "core_lite/tasks/relationship_conditioned_execution_p0_010.json",
        {"activation_dependency": {"satisfied": False}, "status": "WAITING_AUTOMATED_PREDECESSOR", "blocked_by": ["pending"]},
    )
    return root


def test_seals_deterministic_snapshot(tmp_path):
    root = _fixture_root(tmp_path)
    first = seal(root)
    second = seal(root)
    assert first["decision"] == "SANDBOX_EVIDENCE_SNAPSHOT_SEALED"
    assert first["snapshot_root_sha256"] == second["snapshot_root_sha256"]
    assert first["manual_actions_required"] == []
    assert first["production_destination_allowed"] is False


def test_denies_invalid_predecessor(tmp_path):
    root = _fixture_root(tmp_path)
    path = root / "receipts/rce_p0_009_authoritative_validation.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    receipt["authoritative_completion_evidence"] = False
    _write_json(path, receipt)
    with pytest.raises(SnapshotSealError, match="not authoritatively complete"):
        seal(root)


def test_denies_changed_indexed_evidence(tmp_path):
    root = _fixture_root(tmp_path)
    (root / "receipts/example.json").write_text("changed\n", encoding="utf-8")
    with pytest.raises(SnapshotSealError, match="indexed evidence changed"):
        seal(root)


def test_denies_missing_indexed_evidence(tmp_path):
    root = _fixture_root(tmp_path)
    (root / "receipts/example.json").unlink()
    with pytest.raises(SnapshotSealError, match="indexed evidence missing"):
        seal(root)


def test_binds_index_and_predecessor_receipt(tmp_path):
    root = _fixture_root(tmp_path)
    result = seal(root)
    snapshot = json.loads((root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json").read_text(encoding="utf-8"))
    assert snapshot["reconstruction_index_sha256"] == hashlib.sha256((root / "reports/rce_p0_009_reconstruction_index.json").read_bytes()).hexdigest()
    assert snapshot["source_receipt_sha256"] == hashlib.sha256((root / "receipts/rce_p0_009_authoritative_validation.json").read_bytes()).hexdigest()
    assert snapshot["snapshot_root_sha256"] == result["snapshot_root_sha256"]
