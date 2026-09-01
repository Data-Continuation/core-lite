from tools.build_reference_loop_portability_manifest import PortabilityManifestError, manifest_for


def _state() -> dict:
    return {
        "tasks": {f"REF-LOOP-{index:03d}": {"status": "complete"} for index in range(1, 9)},
        "lease": None,
    }


def _receipt_contract() -> dict:
    return {
        "decision": "RECEIPT_CONTRACT_VERIFIED",
        "chain_head": "a" * 64,
        "chain_sha256": "b" * 64,
        "authority": {"external_repository_mutation": False},
    }


def _site_status() -> dict:
    return {
        "decision": "SITE_STATUS_CONTRACT_VERIFIED",
        "authority": {"external_repository_mutation": False},
    }


def test_builds_read_only_portability_manifest() -> None:
    result = manifest_for(_state(), _receipt_contract(), _site_status())
    assert result["decision"] == "PORTABILITY_MANIFEST_VERIFIED"
    assert result["target_repository"] == "StegVerse-org/demo_ingest_engine"
    assert result["authority"] == {
        "read_only_manifest": True,
        "installation_authorized": False,
        "ingestion_authorized": False,
        "publication_authorized": False,
        "external_repository_mutation": False,
        "production_mutation": False,
    }


def test_declares_typed_custody_contract_and_consumer_capabilities() -> None:
    result = manifest_for(_state(), _receipt_contract(), _site_status())
    assert result["typed_custody_contract"] == {
        "owner_repository": "master-records/core-lite",
        "schema_path": "schemas/typed_custody_evidence.schema.json",
        "reference_validator": "Data-Continuation/core-lite/tools/validate_typed_custody_evidence.py",
        "required_evidence_types": [
            "file_digest",
            "record_self_hash",
            "canonical_object_digest",
            "git_object_id",
            "external_artifact",
        ],
        "authority_effect": "NONE",
    }
    required = set(result["required_consumer_capabilities"])
    assert {
        "validate_typed_custody_evidence",
        "distinguish_file_record_object_git_and_external_digests",
        "require_repository_resident_mirror_for_expired_required_artifacts",
        "preserve_append_only_hash_transitions",
        "deny_authority_expansion_from_evidence",
    } <= required


def test_is_deterministic() -> None:
    assert manifest_for(_state(), _receipt_contract(), _site_status()) == manifest_for(
        _state(), _receipt_contract(), _site_status()
    )


def test_fails_closed_on_incomplete_source_task() -> None:
    state = _state()
    state["tasks"]["REF-LOOP-008"]["status"] = "ready"
    try:
        manifest_for(state, _receipt_contract(), _site_status())
    except PortabilityManifestError as exc:
        assert "incomplete tasks" in str(exc)
    else:
        raise AssertionError("incomplete source task did not fail closed")


def test_fails_closed_on_unverified_source_contract() -> None:
    contract = _receipt_contract()
    contract["decision"] = "DENY_RECEIPT_CONTRACT"
    try:
        manifest_for(_state(), contract, _site_status())
    except PortabilityManifestError as exc:
        assert "not verified" in str(exc)
    else:
        raise AssertionError("unverified contract did not fail closed")


def test_fails_closed_if_external_mutation_is_not_denied() -> None:
    status = _site_status()
    status["authority"]["external_repository_mutation"] = True
    try:
        manifest_for(_state(), _receipt_contract(), status)
    except PortabilityManifestError as exc:
        assert "does not deny external mutation" in str(exc)
    else:
        raise AssertionError("external mutation authority did not fail closed")
