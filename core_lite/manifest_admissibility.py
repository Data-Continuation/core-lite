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
    return PRIORITY_ORDER.index(priority) if priority in PRIORITY_ORDER else PRIORITY_ORDER.index("Low")

def priority_exceeds(requested: str, maximum: str) -> bool:
    return priority_rank(requested) < priority_rank(maximum)

def canonical_has_leading_period(path: str) -> bool:
    return any(part.startswith(".") for part in Path(path).parts)

def expected_iosnoperiod_path(canonical_path: str) -> str:
    parts = []
    for part in Path(canonical_path).parts:
        if part == ".github": parts.append("github")
        elif part == ".stegverse": parts.append("stegverse")
        elif part == ".gitkeep": parts.append("gitkeep")
        elif part.startswith("."): parts.append(part[1:])
        else: parts.append(part)
    return str(Path("iosnoperiod", *parts)).replace("\\", "/")

def manifest_file_paths(manifest: Dict[str, Any]) -> List[str]:
    return [i["path"] for i in manifest.get("files", []) if isinstance(i, dict) and isinstance(i.get("path"), str)]

def iosnoperiod_mappings(manifest: Dict[str, Any]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in manifest.get("iosnoperiod_mappings", []):
        if isinstance(item, dict) and isinstance(item.get("canonical_path"), str) and isinstance(item.get("iosnoperiod_path"), str):
            result[item["canonical_path"]] = item["iosnoperiod_path"]
    return result

def validate_iosnoperiod_completeness(manifest: Dict[str, Any], staging_root: Path) -> List[str]:
    errors: List[str] = []
    files = set(manifest_file_paths(manifest))
    mappings = iosnoperiod_mappings(manifest)
    leading = [p for p in files if canonical_has_leading_period(p) and not p.startswith("iosnoperiod/")]
    if leading and not (staging_root / "iosnoperiod.md").exists():
        errors.append("bundle contains leading-period paths but is missing iosnoperiod.md")
    for canonical in leading:
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
    entrypoint = manifest.get("entrypoint", {}) if isinstance(manifest.get("entrypoint", {}), dict) else {}
    entrypoint_class = str(entrypoint.get("class", manifest.get("entrypoint_class", ""))).strip()
    source = str(entrypoint.get("source", manifest.get("source", ""))).strip()
    if not entrypoint_class:
        return ["manifest missing entrypoint.class"]
    ep = policy.get("entrypoint_classes", {}).get(entrypoint_class)
    if not isinstance(ep, dict):
        return [f"unknown entrypoint class: {entrypoint_class}"]
    if not source:
        errors.append("manifest missing entrypoint.source")
    elif source not in ep.get("allowed_sources", []):
        errors.append(f"source {source!r} is not allowed for entrypoint class {entrypoint_class!r}")
    if bool(ep.get("parent_event_hash_required", False)) and not (manifest.get("parent_event_hash") or entrypoint.get("parent_event_hash")):
        errors.append(f"parent_event_hash required for entrypoint class {entrypoint_class}")
    return errors

def validate_priority_authority(manifest: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    entrypoint = manifest.get("entrypoint", {}) if isinstance(manifest.get("entrypoint", {}), dict) else {}
    source = str(entrypoint.get("source", manifest.get("source", ""))).strip()
    requested = str(manifest.get("priority", "Low")).strip() or "Low"
    sp = policy.get("source_authority", {}).get(source)
    if not isinstance(sp, dict):
        return [f"no source authority policy for source: {source}"]
    max_priority = str(sp.get("max_priority_without_confirmation", "Low"))
    if priority_exceeds(requested, max_priority) and not (manifest.get("authority_confirmation") or entrypoint.get("authority_confirmation")):
        return [f"source {source!r} requested priority {requested!r}, which exceeds max unconfirmed priority {max_priority!r}"]
    return []

def validate_allow_scope(manifest: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    entrypoint = manifest.get("entrypoint", {}) if isinstance(manifest.get("entrypoint", {}), dict) else {}
    source = str(entrypoint.get("source", manifest.get("source", ""))).strip()
    sp = policy.get("source_authority", {}).get(source, {})
    requested = manifest.get("requested_allow_scopes", [])
    if isinstance(requested, str):
        requested = [requested]
    if not isinstance(requested, list):
        return ["requested_allow_scopes must be a list or string"]
    known = set(policy.get("scoped_allow_values", []))
    allowed = set(sp.get("allowed_scopes", []))
    disallowed = set(sp.get("disallowed_scopes", []))
    for scope in requested:
        if not isinstance(scope, str):
            errors.append("requested_allow_scopes entries must be strings")
        elif scope not in known:
            errors.append(f"unknown allow scope requested: {scope}")
        elif scope in disallowed or scope not in allowed:
            errors.append(f"source {source!r} is not authorized for allow scope {scope!r}")
    return errors

def validate_manifest_admissibility(repo_root: Path, manifest: Dict[str, Any], staging_root: Path) -> Dict[str, Any]:
    policy = load_manifest_admissibility_policy(repo_root)
    errors: List[str] = []
    errors.extend(validate_entrypoint_and_source(manifest, policy))
    errors.extend(validate_priority_authority(manifest, policy))
    errors.extend(validate_allow_scope(manifest, policy))
    if bool(policy.get("iosnoperiod_required_for_leading_period_paths", True)):
        errors.extend(validate_iosnoperiod_completeness(manifest, staging_root))
    return {"schema": "stegverse_manifest_admissibility_result.v1", "policy_version": policy.get("version", ""), "success": not errors, "errors": errors, "warnings": [], "bundle_id": manifest.get("bundle_id", ""), "bundle_version": manifest.get("bundle_version", ""), "target_repo": manifest.get("target_repo", "")}
