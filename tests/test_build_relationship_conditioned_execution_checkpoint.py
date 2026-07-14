import json
from pathlib import Path

import pytest

from tools.build_relationship_conditioned_execution_checkpoint import CheckpointError, build


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    _write(root / "core_lite/tasks/relationship_conditioned_execution_p0_014.json", {
        "task_id": "RCE-P0-014",
        "status": "WAITING_AUTOMATED_PREDECESSOR",
        "activation_dependency": {"satisfied": False},
        "blocked_by": ["pending"],
    })
    snapshot_root = "a" * 64
    _write(root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json", {
        "snapshot_root_sha256": snapshot_root,
    })
    _write(root / "reports/rce_p0_012_restoration_equivalence.json", {
        "decision": "RESTORATION_EQUIVALENCE_ATTESTED",
        "snapshot_root_sha256": snapshot_root,
    })
    for number in range(1, 14):
        _write(root / f"receipts/rce_p0_{number:03d}_authoritative_validation.json", {
            "task_id": f"RCE-P0-{number:03d}",
            "authoritative_completion_evidence": True,
            "decision": "DIVERGENCE_GUARD_ARMED" if number == 13 else "PASS",
            "manual_actions_required": [],
        })
    return root


def test_builds_deterministic_local_checkpoint(tmp_path):
    root = _fixture(tmp_path)
    first = build(root)
    second = build(root)
    assert first["decision"] == "CONTINUITY_CHECKPOINT_CANDIDATE_READY"
    assert first["checkpoint_root_sha256"] == second["checkpoint_root_sha256"]
    assert first["publication_performed"] is False
    assert first["receipt_count"] == 13
    assert first["manual_actions_required"] == []


def test_denies_missing_receipt(tmp_path):
    root = _fixture(tmp_path)
    (root / "receipts/rce_p0_006_authoritative_validation.json").unlink()
    with pytest.raises(CheckpointError, match="authoritative receipt missing"):
        build(root)


def test_denies_non_authoritative_predecessor(tmp_path):
    root = _fixture(tmp_path)
    path = root / "receipts/rce_p0_013_authoritative_validation.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["authoritative_completion_evidence"] = False
    _write(path, value)
    with pytest.raises(CheckpointError, match="P0-013 is not authoritatively complete"):
        build(root)


def test_denies_snapshot_root_mismatch(tmp_path):
    root = _fixture(tmp_path)
    path = root / "reports/rce_p0_012_restoration_equivalence.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["snapshot_root_sha256"] = "b" * 64
    _write(path, value)
    with pytest.raises(CheckpointError, match="snapshot root mismatch"):
        build(root)
