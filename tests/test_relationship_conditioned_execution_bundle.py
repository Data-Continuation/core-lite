import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.build_relationship_conditioned_execution_bundle import build, canonical_bytes
from tools.validate_relationship_conditioned_execution_bundle import (
    BundleValidationError,
    OUT,
    validate,
)


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def write(name: str, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refresh_manifest(inventory=None, plan=None):
    manifest = load("bundle_manifest.json")
    if inventory is not None:
        manifest["source_inventory_sha256"] = hashlib.sha256(canonical_bytes(inventory)).hexdigest()
    if plan is not None:
        manifest["install_plan_sha256"] = hashlib.sha256(canonical_bytes(plan)).hexdigest()
    write("bundle_manifest.json", manifest)


@pytest.fixture(autouse=True)
def rebuild_bundle():
    build()
    yield
    build()


def test_canonical_bundle_validates():
    validate()


def test_builder_is_deterministic():
    first = {path.name: path.read_bytes() for path in OUT.glob("*.json")}
    build()
    second = {path.name: path.read_bytes() for path in OUT.glob("*.json")}
    assert first == second


def test_missing_source_file_fails(monkeypatch, tmp_path):
    inventory = load("source_inventory.json")
    inventory["files"][0]["source_path"] = "missing/not-present.md"
    write("source_inventory.json", inventory)
    refresh_manifest(inventory=inventory)
    with pytest.raises(BundleValidationError, match="missing source file"):
        validate()


def test_hash_mismatch_fails():
    inventory = load("source_inventory.json")
    inventory["files"][0]["sha256"] = "0" * 64
    write("source_inventory.json", inventory)
    refresh_manifest(inventory=inventory)
    with pytest.raises(BundleValidationError, match="hash mismatch"):
        validate()


def test_size_mismatch_fails():
    inventory = load("source_inventory.json")
    inventory["files"][0]["bytes"] += 1
    write("source_inventory.json", inventory)
    refresh_manifest(inventory=inventory)
    with pytest.raises(BundleValidationError, match="size mismatch"):
        validate()


def test_path_traversal_fails():
    inventory = load("source_inventory.json")
    inventory["files"][0]["target_path"] = "sandbox/relationship_conditioned_execution/../../production/file"
    write("source_inventory.json", inventory)
    refresh_manifest(inventory=inventory)
    with pytest.raises(BundleValidationError, match="unsafe path"):
        validate()


def test_production_target_fails():
    inventory = load("source_inventory.json")
    inventory["files"][0]["target_path"] = "production/relationship_conditioned_execution/file"
    write("source_inventory.json", inventory)
    refresh_manifest(inventory=inventory)
    with pytest.raises(BundleValidationError, match="production or external target"):
        validate()


def test_execution_authority_fails():
    manifest = load("bundle_manifest.json")
    manifest["autonomous_execution_authority"] = True
    write("bundle_manifest.json", manifest)
    with pytest.raises(BundleValidationError, match="autonomous execution authority"):
        validate()


def test_dependency_order_violation_fails():
    inventory = load("source_inventory.json")
    inventory["files"][0]["kind"] = "fixture"
    write("source_inventory.json", inventory)
    refresh_manifest(inventory=inventory)
    with pytest.raises(BundleValidationError, match="dependency order"):
        validate()
