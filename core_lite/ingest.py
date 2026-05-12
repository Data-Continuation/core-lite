from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, List

try:
    from .context import detect_context
    from .manifest import load_bundle_manifest, validate_manifest
    from .paths import ensure_dir, safe_join, utc_stamp
    from .receipts import append_receipt
except ImportError:
    from context import detect_context
    from manifest import load_bundle_manifest, validate_manifest
    from paths import ensure_dir, safe_join, utc_stamp
    from receipts import append_receipt


def load_core_policy(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / ".stegverse" / "core-lite.json"
    if not path.exists():
        return {
            "incoming_dir": "incoming",
            "success_dir": "legacy/ingested-bundles",
            "failed_dir": "legacy/failed-bundles",
            "default_task_manifest": "tools/tasks/formalism_tests_tasks.json",
            "run_tasks_after_ingest": True,
        }
    return json.loads(path.read_text(encoding="utf-8"))


def install_declared_files(repo_root: Path, staging_root: Path, manifest: Dict[str, Any]) -> List[Dict[str, str]]:
    installed: List[Dict[str, str]] = []

    for item in manifest.get("files", []):
        if not isinstance(item, dict):
            raise ValueError("manifest file entries must be objects")

        rel = item.get("path")
        action = item.get("action", "overwrite")

        if not isinstance(rel, str) or not rel:
            raise ValueError("manifest file entry missing path")

        if action == "read_before_install":
            continue

        if action not in {"overwrite", "merge_or_replace_with_review"}:
            raise ValueError(f"unsupported install action for {rel}: {action}")

        source = staging_root / rel
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"declared file missing from bundle: {rel}")

        destination = safe_join(repo_root, rel)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

        installed.append({
            "path": rel,
            "action": action,
            "class": str(item.get("class", "")),
        })

    return installed


def process_bundle(repo_root: Path, zip_path: Path, policy: Dict[str, Any], context: Dict[str, str]) -> Dict[str, Any]:
    stamp = utc_stamp()
    staging_root = repo_root / ".core-lite-staging" / f"{zip_path.stem}-{stamp}"
    ensure_dir(staging_root)

    success_dir = ensure_dir(repo_root / policy.get("success_dir", "legacy/ingested-bundles"))
    failed_dir = ensure_dir(repo_root / policy.get("failed_dir", "legacy/failed-bundles"))

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(staging_root)

        manifest = load_bundle_manifest(staging_root)
        validation = validate_manifest(manifest, context, staging_root)
        installed = install_declared_files(repo_root, staging_root, manifest)

        destination = success_dir / f"{stamp}-{zip_path.name}"
        shutil.move(str(zip_path), str(destination))

        receipt = {
            "type": "bundle_ingested",
            "bundle": zip_path.name,
            "moved_to": destination.relative_to(repo_root).as_posix(),
            "manifest": {
                "bundle_id": manifest.get("bundle_id", ""),
                "bundle_version": manifest.get("bundle_version", ""),
                "target_repo": manifest.get("target_repo", ""),
            },
            "validation": validation,
            "installed": installed,
            "success": True,
        }
        append_receipt(repo_root, receipt)
        return receipt

    except Exception as exc:
        destination = failed_dir / f"{stamp}-{zip_path.name}"
        if zip_path.exists():
            shutil.move(str(zip_path), str(destination))

        receipt = {
            "type": "bundle_failed",
            "bundle": zip_path.name,
            "moved_to": destination.relative_to(repo_root).as_posix(),
            "error": str(exc),
            "success": False,
        }
        append_receipt(repo_root, receipt)
        return receipt

    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)


def ingest_incoming(repo_root: Path) -> Dict[str, Any]:
    context = detect_context(repo_root)
    policy = load_core_policy(repo_root)

    incoming_dir = ensure_dir(repo_root / policy.get("incoming_dir", "incoming"))
    bundles = sorted(incoming_dir.glob("*.zip"))

    receipts = [
        process_bundle(repo_root, bundle, policy, context)
        for bundle in bundles
    ]

    report = {
        "schema": "stegverse_core_lite_ingest_report.v1",
        "bundle_count": len(bundles),
        "success": all(receipt.get("success") for receipt in receipts),
        "receipts": receipts,
    }

    (repo_root / "core_lite_ingest_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return report
