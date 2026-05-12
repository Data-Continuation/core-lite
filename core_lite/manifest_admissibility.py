from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


POLICY_PATH = Path("schemas/manifest_admissibility_policy.json")
PRIORITY_ORDER = ["Critical", "Medium", "Low", "NonCritical"]


def load_manifest_admissibility_policy(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / POLICY_PATH
    if not path.exists():
        raise FileNotFoundError(f"manifest admissibility policy not found: {POLICY_PATH}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "stegverse_manifest_admissibility_policy.v1":
        raise ValueError("unsupported manifest admissibility policy schema")
    return payload


def priority_rank(priority: str) -> int:
    try:
        return PRIORITY_ORDER.index(priority)
    except ValueError:
        return PRIORITY_ORDER.index("Low")


def priority_exceeds(requested: str, maximum: str) -> bool:
    return priority_rank(requested) < priority_rank(maximum)


def canonical_has_leading_period(path: str) -> bool:
    return any(part.startswith(".") for part in Path(path).parts)


def expected_iosnoperiod_path(canonical_path: str) -> str:
    parts = []
    for part in Path(canonical_path).parts:
        if part == ".github":
            parts.append("github")
        elif part == ".stegverse":
            parts.append("stegverse")
        elif part == ".gitkeep":
            parts.append("gitkeep")
        elif part.startswith("."):
            parts.append(part[1:])
        else:
            parts.append(part)
    return str(Path("iosnoperiod", *parts)).replace("\\", "/")


def manifest_file_paths(manifest: Dict[str, Any]) -> List[str]:
    paths: List[str] = []
    for item in manifest.get("files", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.append(item["path"])
    return paths


def iosnoperiod_mappings(manifest: Dict[str, Any]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in manifest.get("iosnoperiod_mappings", []):
        if not isinstance(item, dict):
            continue
        canonical = item.get("canonical_path")
        ios_path = item.get("iosnoperiod_path")
        if isinstance(canonical, str) and isinstance(ios_path, str):
            result[canonical] = ios_path
    return result


def validate_iosnoperiod_completeness(manifest: Dict[str, Any], staging_root: Path) -> List[str]:
    errors: List[str] = []
    files = set(manifest_file_paths(manifest))
    mappings = iosnoperiod_mappings(manifest)

    leading_period_paths = [
        path for path in files
        if canonical_has_leading_period(path) and not path.startswith("iosnoperiod/")
    ]

    if leading_period_paths and not (staging_root / "iosnoperiod.md").exists():
        errors.append("bundle contains leading-period paths but is missing iosnoperiod.md")

    for canonical in leading_period_paths:
        expected = expected_iosnoperiod_path(canonical)
        mapped = mappings.get(canonical)

        if mapped != expected:
            errors.append(f"missing or incorrect iosnoperiod mapping for {canonical}: expected {expected}")

        if mapped and mapped not in files:
            errors.append(f"iosnoperiod mapped file is not declared in files list: {mapped}")

        if not (staging_root / expected).exists():
            errors.append(f"iosnoperiod mirror file missing from bundle: {expected}")

    return errors


def validate_entrypoint_and_source(manifest: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    entrypoint = manifest.get("entrypoint", {})
    if not isinstance(entrypoint, dict):
        entrypoint = {}

    entrypoint_class = str(entrypoint.get("class", manifest.get("entrypoint_class", ""))).strip()
    source = str(entrypoint.get("source", manifest.get("source", ""))).strip()

    if not entrypoint_class:
        errors.append("manifest missing entrypoint.class")
        return errors

    entrypoint_policy = policy.get("entrypoint_classes", {}).get(entrypoint_class)
    if not isinstance(entrypoint_policy, dict):
        errors.append(f"unknown entrypoint class: {entrypoint_class}")
        return errors

    if not source:
        errors.append("manifest missing entrypoint.source")
        return errors

    allowed_sources = entrypoint_policy.get("allowed_sources", [])
    if source not in allowed_sources:
        errors.append(f"source {source!r} is not allowed for entrypoint class {entrypoint_class!r}")

    parent_required = bool(entrypoint_policy.get("parent_event_hash_required", False))
    parent_event_hash = manifest.get("parent_event_hash") or entrypoint.get("parent_event_hash")
    if parent_required and not parent_event_hash:
        errors.append(f"parent_event_hash required for entrypoint class {entrypoint_class}")

    return errors


def validate_priority_authority(manifest: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    entrypoint = manifest.get("entrypoint", {})
    if not isinstance(entrypoint, dict):
        entrypoint = {}

    source = str(entrypoint.get("source", manifest.get("source", ""))).strip()
    requested_priority = str(manifest.get("priority", "Low")).strip() or "Low"

    source_policy = policy.get("source_authority", {}).get(source)
    if not isinstance(source_policy, dict):
        errors.append(f"no source authority policy for source: {source}")
        return errors

    max_priority = str(source_policy.get("max_priority_without_confirmation", "Low"))
    authority_confirmation = manifest.get("authority_confirmation") or entrypoint.get("authority_confirmation")

    if priority_exceeds(requested_priority, max_priority) and not authority_confirmation:
        errors.append(
            f"source {source!r} requested priority {requested_priority!r}, "
            f"which exceeds max unconfirmed priority {max_priority!r}"
        )

    return errors


def validate_allow_scope(manifest: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    entrypoint = manifest.get("entrypoint", {})
    if not isinstance(entrypoint, dict):
        entrypoint = {}

    source = str(entrypoint.get("source", manifest.get("source", ""))).strip()
    source_policy = policy.get("source_authority", {}).get(source, {})

    requested = manifest.get("requested_allow_scopes", [])
    if isinstance(requested, str):
        requested = [requested]

    if not isinstance(requested, list):
        errors.append("requested_allow_scopes must be a list or string")
        return errors

    known_scopes = set(policy.get("scoped_allow_values", []))
    allowed = set(source_policy.get("allowed_scopes", []))
    disallowed = set(source_policy.get("disallowed_scopes", []))

    for scope in requested:
        if not isinstance(scope, str):
            errors.append("requested_allow_scopes entries must be strings")
            continue
        if scope not in known_scopes:
            errors.append(f"unknown allow scope requested: {scope}")
            continue
        if scope in disallowed or scope not in allowed:
            errors.append(f"source {source!r} is not authorized for allow scope {scope!r}")

    return errors


def validate_manifest_admissibility(repo_root: Path, manifest: Dict[str, Any], staging_root: Path) -> Dict[str, Any]:
    policy = load_manifest_admissibility_policy(repo_root)

    errors: List[str] = []
    warnings: List[str] = []

    errors.extend(validate_entrypoint_and_source(manifest, policy))
    errors.extend(validate_priority_authority(manifest, policy))
    errors.extend(validate_allow_scope(manifest, policy))

    if bool(policy.get("iosnoperiod_required_for_leading_period_paths", True)):
        errors.extend(validate_iosnoperiod_completeness(manifest, staging_root))

    result = {
        "schema": "stegverse_manifest_admissibility_result.v1",
        "policy_version": policy.get("version", ""),
        "success": not errors,
        "errors": errors,
        "warnings": warnings,
        "bundle_id": manifest.get("bundle_id", ""),
        "bundle_version": manifest.get("bundle_version", ""),
        "target_repo": manifest.get("target_repo", ""),
    }

    return result
