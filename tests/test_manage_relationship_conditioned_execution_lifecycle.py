import json
from pathlib import Path

import pytest

from tools.manage_relationship_conditioned_execution_lifecycle import LifecycleError, reconcile


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_root(tmp_path: Path, version: str = "1.0.0-sandbox-candidate") -> Path:
    root = tmp_path / "repo"
    stage = root / "sandbox/intake/relationship_conditioned_execution"
    write_json(stage / "bundle_manifest.json", {
        "package_id": "relationship-conditioned-execution",
        "package_version": version,
        "sandbox_only": True,
        "production_destination_allowed": False,
        "autonomous_execution_authority": False,
        "human_harm_authority": False,
    })
    write_json(stage / "install_plan.json", {"operations": []})
    write_json(stage / "source_inventory.json", {"files": []})
    write_json(stage / "staging_manifest.json", {
        "decision": "STAGED_CANDIDATE_EVIDENCE",
        "external_destination_mutation_performed": False,
    })
    write_json(root / "receipts/rce_p0_006_authoritative_validation.json", {
        "task_id": "RCE-P0-006",
        "authoritative_completion_evidence": True,
        "decision": "CUSTODY_AND_REPLAY_VERIFIED",
        "manual_actions_required": [],
    })
    write_json(root / "core_lite/tasks/relationship_conditioned_execution_p0_007.json", {
        "task_id": "RCE-P0-007",
        "status": "ACTIVE",
        "blocked_by": [],
    })
    return root


def test_initial_activation_and_idempotent_reconciliation(tmp_path):
    root = fixture_root(tmp_path)
    first = reconcile(root)
    assert first["decision"] == "ACTIVATE_INITIAL_SANDBOX_CANDIDATE"
    second = reconcile(root)
    assert second["decision"] == "NO_CHANGE_ACTIVE_CANDIDATE"
    assert second["manual_actions_required"] == []


def test_denies_version_downgrade(tmp_path):
    root = fixture_root(tmp_path, "2.0.0-sandbox-candidate")
    reconcile(root)
    manifest = root / "sandbox/intake/relationship_conditioned_execution/bundle_manifest.json"
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["package_version"] = "1.0.0-sandbox-candidate"
    write_json(manifest, value)
    with pytest.raises(LifecycleError, match="downgrade"):
        reconcile(root)


def test_denies_same_version_content_drift(tmp_path):
    root = fixture_root(tmp_path)
    reconcile(root)
    write_json(root / "sandbox/intake/relationship_conditioned_execution/install_plan.json", {"operations": ["changed"]})
    with pytest.raises(LifecycleError, match="content drift"):
        reconcile(root)


def test_supersedes_newer_version_and_archives_prior(tmp_path):
    root = fixture_root(tmp_path)
    reconcile(root)
    manifest = root / "sandbox/intake/relationship_conditioned_execution/bundle_manifest.json"
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["package_version"] = "1.1.0-sandbox-candidate"
    write_json(manifest, value)
    result = reconcile(root)
    assert result["decision"] == "SUPERSEDE_SANDBOX_CANDIDATE"
    assert (root / "sandbox/archive/relationship_conditioned_execution/1.0.0-sandbox-candidate/bundle_manifest.json").is_file()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("sandbox_only", False, "not sandbox only"),
        ("production_destination_allowed", True, "production destination"),
        ("autonomous_execution_authority", True, "autonomous execution"),
        ("human_harm_authority", True, "human-harm"),
    ],
)
def test_denies_authority_or_destination_expansion(tmp_path, field, value, message):
    root = fixture_root(tmp_path)
    manifest = root / "sandbox/intake/relationship_conditioned_execution/bundle_manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data[field] = value
    write_json(manifest, data)
    with pytest.raises(LifecycleError, match=message):
        reconcile(root)


def test_denies_unverified_predecessor(tmp_path):
    root = fixture_root(tmp_path)
    receipt = root / "receipts/rce_p0_006_authoritative_validation.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    data["authoritative_completion_evidence"] = False
    write_json(receipt, data)
    with pytest.raises(LifecycleError, match="not authoritatively complete"):
        reconcile(root)
