import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.stage_relationship_conditioned_execution_sandbox import StagingError, stage


PACKAGE_FILES = ("bundle_manifest.json", "install_plan.json", "source_inventory.json")


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    bundle = root / "bundles" / "relationship_conditioned_execution"
    bundle.mkdir(parents=True)
    _write_json(
        bundle / "bundle_manifest.json",
        {
            "authority": {
                "candidate_evidence_only": True,
                "autonomous_execution_authority": False,
                "human_harm_authority": False,
            },
            "production_destination_allowed": False,
        },
    )
    _write_json(bundle / "install_plan.json", {"steps": ["policy", "schema", "fixtures"]})
    _write_json(bundle / "source_inventory.json", {"files": []})
    _write_json(
        root / "receipts" / "rce_p0_004_authoritative_validation.json",
        {
            "task_id": "RCE-P0-004",
            "authoritative_completion_evidence": True,
            "decision": "ALLOW_CANDIDATE_INTAKE",
            "destination_mutation_performed": False,
            "manual_actions_required": [],
        },
    )
    return root


def test_stages_candidate_evidence_and_preserves_hashes(tmp_path):
    root = _fixture_root(tmp_path)
    result = stage(root=root)
    assert result["decision"] == "STAGED_CANDIDATE_EVIDENCE"
    assert result["manual_actions_required"] == []
    assert result["external_destination_mutation_performed"] is False

    for entry in result["files"]:
        source = root / entry["source_path"]
        target = root / entry["target_path"]
        assert target.is_file()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == entry["sha256"]
        assert target.read_bytes() == source.read_bytes()


def test_denies_missing_authoritative_completion(tmp_path):
    root = _fixture_root(tmp_path)
    receipt_path = root / "receipts" / "rce_p0_004_authoritative_validation.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["authoritative_completion_evidence"] = False
    _write_json(receipt_path, receipt)
    with pytest.raises(StagingError, match="not authoritatively complete"):
        stage(root=root)


def test_denies_non_allow_decision(tmp_path):
    root = _fixture_root(tmp_path)
    receipt_path = root / "receipts" / "rce_p0_004_authoritative_validation.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["decision"] = "DENY_CANDIDATE_INTAKE"
    _write_json(receipt_path, receipt)
    with pytest.raises(StagingError, match="was not allowed"):
        stage(root=root)


@pytest.mark.parametrize(
    ("field", "unsafe_value"),
    [
        ("candidate_evidence_only", False),
        ("autonomous_execution_authority", True),
        ("human_harm_authority", True),
    ],
)
def test_denies_authority_expansion(tmp_path, field, unsafe_value):
    root = _fixture_root(tmp_path)
    path = root / "bundles" / "relationship_conditioned_execution" / "bundle_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["authority"][field] = unsafe_value
    _write_json(path, manifest)
    with pytest.raises(StagingError):
        stage(root=root)


def test_denies_production_destination_permission(tmp_path):
    root = _fixture_root(tmp_path)
    path = root / "bundles" / "relationship_conditioned_execution" / "bundle_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["production_destination_allowed"] = True
    _write_json(path, manifest)
    with pytest.raises(StagingError, match="production destination"):
        stage(root=root)


def test_denies_path_escape(tmp_path):
    root = _fixture_root(tmp_path)
    with pytest.raises(StagingError, match="escaped sandbox intake"):
        stage(root=root, stage_root=tmp_path / "outside")


def test_denies_missing_package_file(tmp_path):
    root = _fixture_root(tmp_path)
    (root / "bundles" / "relationship_conditioned_execution" / "install_plan.json").unlink()
    with pytest.raises(StagingError, match="missing package file"):
        stage(root=root)
