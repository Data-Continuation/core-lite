import json
from pathlib import Path

import pytest

from tools.index_relationship_conditioned_execution_evidence import EvidenceIndexError, build_index


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for task_no in range(1, 9):
        _write(
            root / f"receipts/rce_p0_{task_no:03d}_authoritative_validation.json",
            {
                "task_id": f"RCE-P0-{task_no:03d}",
                "authoritative_completion_evidence": True,
                "manual_actions_required": [],
            },
        )
    _write(root / "reports/rce_p0_008_lease.json", {"decision": "LEASE_ACTIVE"})
    _write(root / "bundles/relationship_conditioned_execution/bundle_manifest.json", {"sandbox_only": True})
    _write(root / "sandbox/intake/relationship_conditioned_execution/lifecycle_state.json", {"active_version": "1.0.0"})
    _write(root / "sandbox/intake/relationship_conditioned_execution/lease_state.json", {"status": "ACTIVE"})
    _write(
        root / "core_lite/tasks/relationship_conditioned_execution_p0_009.json",
        {"activation_dependency": {"satisfied": False}, "blocked_by": ["pending"], "status": "WAITING"},
    )
    return root


def test_builds_deterministic_hash_and_size_index(tmp_path):
    root = _fixture_root(tmp_path)
    first = build_index(root)
    second = build_index(root)
    assert first["decision"] == "RECONSTRUCTION_INDEX_VERIFIED"
    assert first["index_sha256"] == second["index_sha256"]
    assert first["manual_actions_required"] == []
    assert all(entry["bytes"] > 0 and len(entry["sha256"]) == 64 for entry in first["entries"])


def test_indexes_active_sandbox_and_source_package(tmp_path):
    root = _fixture_root(tmp_path)
    result = build_index(root)
    classes = {entry["evidence_class"] for entry in result["entries"]}
    assert "active_sandbox_evidence" in classes
    assert "source_package" in classes
    assert "authoritative_receipt" in classes


def test_fails_closed_when_predecessor_is_not_authoritative(tmp_path):
    root = _fixture_root(tmp_path)
    path = root / "receipts/rce_p0_008_authoritative_validation.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["authoritative_completion_evidence"] = False
    _write(path, value)
    with pytest.raises(EvidenceIndexError, match="not authoritatively complete"):
        build_index(root)


def test_fails_closed_when_any_authoritative_receipt_is_missing(tmp_path):
    root = _fixture_root(tmp_path)
    (root / "receipts/rce_p0_004_authoritative_validation.json").unlink()
    with pytest.raises(EvidenceIndexError, match="missing authoritative receipts"):
        build_index(root)


def test_does_not_delete_existing_evidence(tmp_path):
    root = _fixture_root(tmp_path)
    evidence = root / "sandbox/archive/relationship_conditioned_execution/0.9.0/archive.json"
    _write(evidence, {"preserved": True})
    build_index(root)
    assert evidence.is_file()
