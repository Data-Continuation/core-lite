import hashlib
import json
from pathlib import Path

import pytest

from tools.guard_relationship_conditioned_execution_restoration import GuardError, guard


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    source = root / "evidence/source.json"
    restored = root / "sandbox/restoration_drills/relationship_conditioned_execution/evidence/source.json"
    _write(source, {"value": 1})
    restored.parent.mkdir(parents=True, exist_ok=True)
    restored.write_bytes(source.read_bytes())
    entry = {"path": "evidence/source.json", "sha256": _sha(source), "bytes": source.stat().st_size}
    _write(root / "sandbox/snapshots/relationship_conditioned_execution/snapshot_manifest.json", {
        "snapshot_root_sha256": "root",
        "entries": [entry],
    })
    _write(root / "sandbox/restoration_drills/relationship_conditioned_execution/restoration_manifest.json", {
        "snapshot_root_sha256": "root",
        "entries": [{
            "source_path": "evidence/source.json",
            "restored_path": "sandbox/restoration_drills/relationship_conditioned_execution/evidence/source.json",
            "sha256": entry["sha256"],
            "bytes": entry["bytes"],
        }],
    })
    _write(root / "receipts/rce_p0_012_authoritative_validation.json", {
        "task_id": "RCE-P0-012",
        "authoritative_completion_evidence": True,
        "decision": "RESTORATION_EQUIVALENCE_ATTESTED",
        "manual_actions_required": [],
    })
    _write(root / "core_lite/tasks/relationship_conditioned_execution_p0_013.json", {
        "activation_dependency": {"satisfied": False},
        "status": "WAITING_AUTOMATED_PREDECESSOR",
        "blocked_by": [],
    })
    return root


def test_arms_clean_guard(tmp_path):
    root = _root(tmp_path)
    result = guard(root)
    assert result["decision"] == "DIVERGENCE_GUARD_ARMED"
    assert result["divergence_count"] == 0
    assert result["manual_actions_required"] == []
    receipt = json.loads((root / "receipts/rce_p0_013_authoritative_validation.json").read_text())
    assert receipt["authoritative_completion_evidence"] is True


def test_quarantines_restored_drift(tmp_path):
    root = _root(tmp_path)
    restored = root / "sandbox/restoration_drills/relationship_conditioned_execution/evidence/source.json"
    restored.write_text("drift\n", encoding="utf-8")
    result = guard(root)
    assert result["decision"] == "EVIDENCE_DIVERGENCE_QUARANTINED"
    assert result["divergence_count"] == 1
    assert (root / "sandbox/quarantine/relationship_conditioned_execution/divergence_alert.json").is_file()


def test_quarantines_source_drift(tmp_path):
    root = _root(tmp_path)
    (root / "evidence/source.json").write_text("changed\n", encoding="utf-8")
    result = guard(root)
    assert result["decision"] == "EVIDENCE_DIVERGENCE_QUARANTINED"


def test_denies_invalid_predecessor(tmp_path):
    root = _root(tmp_path)
    path = root / "receipts/rce_p0_012_authoritative_validation.json"
    value = json.loads(path.read_text())
    value["authoritative_completion_evidence"] = False
    _write(path, value)
    with pytest.raises(GuardError, match="not authoritatively complete"):
        guard(root)


def test_detects_membership_divergence(tmp_path):
    root = _root(tmp_path)
    restoration = root / "sandbox/restoration_drills/relationship_conditioned_execution/restoration_manifest.json"
    value = json.loads(restoration.read_text())
    value["entries"] = []
    _write(restoration, value)
    result = guard(root)
    assert result["divergence_count"] == 1
