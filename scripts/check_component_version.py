#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
EXPECTED_REPOSITORY = "Data-Continuation/core-lite"

def fail(msg: str) -> None:
    raise SystemExit(f"COMPONENT_VERSION=FAIL\n- {msg}")

if DATA.get("schema_version") != "1.0.0": fail("schema_version must be 1.0.0")
if DATA.get("repository") != EXPECTED_REPOSITORY: fail("repository identity mismatch")
if not DATA.get("component_id") or not DATA.get("component_version"): fail("component identity/version required")
if DATA.get("authority_effect") != "NONE": fail("version declaration may not grant authority")
if DATA.get("version_stage") not in {"DEVELOPMENT","RELEASE_CANDIDATE","RELEASED"}: fail("unsupported version_stage")
release = DATA.get("release", {})
if DATA["version_stage"] == "RELEASED":
    if not release.get("tag") or not release.get("commit") or not release.get("release_evidence"): fail("RELEASED requires exact tag, commit, evidence")
elif release.get("tag") is not None or release.get("commit") is not None:
    fail("non-released component may not claim release tag/commit")
expected = DATA.get("expected_aggregate_release_binding", {})
if expected.get("observed_as_released") is False and DATA.get("version_stage") == "RELEASED":
    fail("cannot claim RELEASED while aggregate binding is unobserved")
workstream = DATA.get("workstream_identity", {})
if workstream.get("completed_reference_loop_tasks_observed", 0) < 5: fail("reference-loop completion evidence regressed")
print("COMPONENT_VERSION=PASS")
print(f"COMPONENT_ID={DATA['component_id']}")
print(f"COMPONENT_VERSION_VALUE={DATA['component_version']}")
print(f"VERSION_STAGE={DATA['version_stage']}")
print("AUTHORITY_EFFECT=NONE")
