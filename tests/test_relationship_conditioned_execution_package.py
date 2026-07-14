import copy
import json
from pathlib import Path

import pytest

from tools.validate_relationship_conditioned_execution_package import (
    PackageValidationError,
    validate_fixtures,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "core_lite" / "relationship_conditioned_execution_manifest.json").read_text(encoding="utf-8"))
FIXTURES = json.loads((ROOT / "samples" / "relationship_conditioned_execution_sandbox_cases.json").read_text(encoding="utf-8"))


def test_manifest_validates():
    validate_manifest(copy.deepcopy(MANIFEST))


def test_fixture_set_validates():
    validate_fixtures(copy.deepcopy(FIXTURES))


def test_production_install_authority_fails_closed():
    manifest = copy.deepcopy(MANIFEST)
    manifest["authority"]["production_install_authorized"] = True
    with pytest.raises(PackageValidationError, match="production installation"):
        validate_manifest(manifest)


def test_missing_source_hash_fails_closed():
    manifest = copy.deepcopy(MANIFEST)
    manifest["files"][0]["source_blob_sha"] = ""
    with pytest.raises(PackageValidationError, match="invalid source blob hash"):
        validate_manifest(manifest)


def test_dependency_order_mismatch_fails_closed():
    manifest = copy.deepcopy(MANIFEST)
    manifest["dependency_order"] = list(reversed(manifest["dependency_order"]))
    with pytest.raises(PackageValidationError, match="dependency order"):
        validate_manifest(manifest)


def test_irreversible_fixture_cannot_admit_allow():
    fixtures = copy.deepcopy(FIXTURES)
    fixtures["cases"][0]["expected_decisions"] = ["ALLOW"]
    with pytest.raises(PackageValidationError, match="unsafe irreversible outcome"):
        validate_fixtures(fixtures)


def test_collective_vote_cannot_override_safety():
    fixtures = copy.deepcopy(FIXTURES)
    fixtures["cases"][4]["forbidden_decisions"].remove("ALLOW")
    with pytest.raises(PackageValidationError, match="must forbid ALLOW|collective vote"):
        validate_fixtures(fixtures)


def test_nonvalid_authority_cannot_admit_protective_action():
    fixtures = copy.deepcopy(FIXTURES)
    fixtures["cases"][2]["expected_decisions"] = ["PROTECTIVE_DELAY"]
    with pytest.raises(PackageValidationError, match="non-valid authority"):
        validate_fixtures(fixtures)
