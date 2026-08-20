import json
from pathlib import Path

import pytest

from tools.build_relationship_conditioned_execution_bundle import build
from tools.reconstruct_relationship_conditioned_execution_bundle import (
    BUNDLE,
    REPORT,
    review,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "rce_p0_003_authoritative_validation.json"


@pytest.fixture(autouse=True)
def restore_state():
    build()
    original_receipt = RECEIPT.read_bytes()
    original_report = REPORT.read_bytes() if REPORT.exists() else None
    yield
    RECEIPT.write_bytes(original_receipt)
    build()
    if original_report is None:
        if REPORT.exists():
            REPORT.unlink()
    else:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_bytes(original_report)


def test_independent_reconstruction_allows_candidate_intake():
    result = review()
    assert result["decision"] == "ALLOW_CANDIDATE_INTAKE"
    assert result["destination_mutation_performed"] is False
    assert result["manual_actions_required"] == []


def test_tampered_manifest_denies():
    path = BUNDLE / "bundle_manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["sandbox_only"] = False
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert review()["decision"] == "DENY_CANDIDATE_INTAKE"


def test_tampered_inventory_denies():
    path = BUNDLE / "source_inventory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["files"][0]["bytes"] += 1
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert review()["decision"] == "DENY_CANDIDATE_INTAKE"


def test_tampered_install_plan_denies():
    path = BUNDLE / "install_plan.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["automatic_destination_mutation"] = True
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert review()["decision"] == "DENY_CANDIDATE_INTAKE"


def test_invalid_authoritative_receipt_denies():
    value = json.loads(RECEIPT.read_text(encoding="utf-8"))
    value["authoritative_completion_evidence"] = False
    RECEIPT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert review()["decision"] == "DENY_CANDIDATE_INTAKE"
