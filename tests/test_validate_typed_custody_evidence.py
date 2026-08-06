from tools.validate_typed_custody_evidence import validate


def base_record() -> dict:
    return {
        "record_type": "typed_custody_evidence_chain",
        "source_repository": "master-records/core-lite",
        "destination_repository": "Data-Continuation/core-lite",
        "authority_boundary": {"execution_authority": False, "runtime_activation": False},
        "evidence": [
            {
                "type": "git_object_id",
                "repository": "master-records/core-lite",
                "object_kind": "commit",
                "value": "a" * 40,
                "required_for_decision": True,
            },
            {
                "type": "record_self_hash",
                "repository": "master-records/core-lite",
                "field": "record_hash",
                "value": "b" * 64,
                "required_for_decision": True,
            },
            {
                "type": "external_artifact",
                "repository": "GCAT-BCAT-Engine/core-lite-prod",
                "provider": "github_actions",
                "artifact_id": 1,
                "digest": "sha256:" + "c" * 64,
                "availability": "MIRRORED",
                "mirror_status": "REPOSITORY_RESIDENT",
                "mirror_repository": "GCAT-BCAT-Engine/core-lite-prod",
                "mirror_path": "evidence/artifact-mirrors/1.json",
                "mirror_commit": "d" * 40,
                "mirror_hash": "e" * 64,
                "expires_at": "2026-01-01T00:00:00Z",
                "required_for_decision": True,
            },
        ],
    }


def test_accepts_valid_mirrored_chain() -> None:
    assert validate(base_record())["decision"] == "COMPLETE"


def test_rejects_unqualified_repository() -> None:
    record = base_record()
    record["source_repository"] = "core-lite"
    assert validate(record)["decision"] == "REVIEW_REQUIRED"


def test_rejects_git_object_without_kind() -> None:
    record = base_record()
    del record["evidence"][0]["object_kind"]
    assert validate(record)["decision"] == "REVIEW_REQUIRED"


def test_rejects_self_hash_without_field() -> None:
    record = base_record()
    del record["evidence"][1]["field"]
    assert validate(record)["decision"] == "REVIEW_REQUIRED"


def test_blocks_expired_unmirrored_required_artifact() -> None:
    record = base_record()
    artifact = record["evidence"][2]
    artifact["availability"] = "EXPIRED"
    artifact["mirror_status"] = "REQUIRED_BEFORE_EXPIRY"
    for key in ("mirror_repository", "mirror_path", "mirror_commit", "mirror_hash"):
        artifact.pop(key)
    assert validate(record)["decision"] == "BLOCKED"


def test_rejects_authority_expansion() -> None:
    record = base_record()
    record["authority_boundary"]["execution_authority"] = True
    assert validate(record)["decision"] == "REVIEW_REQUIRED"
