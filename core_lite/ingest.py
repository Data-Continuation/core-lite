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
    from .queue import plan_incoming_bundles
    from .receipts import append_receipt
except ImportError:
    from context import detect_context
    from manifest import load_bundle_manifest, validate_manifest
    from paths import ensure_dir, safe_join, utc_stamp
    from queue import plan_incoming_bundles
    from receipts import append_receipt


def load_core_policy(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / ".stegverse" / "core-lite.json"
    if not path.exists():
        return {
            "incoming_dir": "incoming",
            "success_dir": "legacy/ingested-bundles",
            "failed_dir": "legacy/failed-bundles",
            "superseded_dir": "legacy/superseded-bundles",
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


def move_zip(zip_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / zip_path.name

    if destination.exists():
        stamp = utc_stamp()
        destination = destination_dir / f"{stamp}-{zip_path.name}"

    shutil.move(str(zip_path), str(destination))
    return destination


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
        validation = validate_manifest(manifest, context, staging_root, repo_root=repo_root)
        installed = install_declared_files(repo_root, staging_root, manifest)

        destination = move_zip(zip_path, success_dir)

        receipt = {
            "type": "bundle_ingested",
            "bundle": zip_path.name,
            "moved_to": destination.relative_to(repo_root).as_posix(),
            "manifest": {
                "bundle_id": manifest.get("bundle_id", ""),
                "bundle_version": manifest.get("bundle_version", ""),
                "target_repo": manifest.get("target_repo", ""),
                "priority": manifest.get("priority", "Low"),
                "succession": manifest.get("succession", "versioning"),
                "entrypoint": manifest.get("entrypoint", {}),
                "requested_allow_scopes": manifest.get("requested_allow_scopes", []),
            },
            "validation": validation,
            "installed": installed,
            "success": True,
        }
        append_receipt(repo_root, receipt)
        return receipt

    except Exception as exc:
        destination = move_zip(zip_path, failed_dir) if zip_path.exists() else failed_dir

        receipt = {
            "type": "bundle_failed",
            "bundle": zip_path.name,
            "moved_to": destination.relative_to(repo_root).as_posix() if isinstance(destination, Path) else "",
            "error": str(exc),
            "success": False,
        }
        append_receipt(repo_root, receipt)
        return receipt

    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)


def move_superseded_bundle(repo_root: Path, zip_path: Path, policy: Dict[str, Any], queue_entry: Dict[str, Any]) -> Dict[str, Any]:
    superseded_dir = ensure_dir(repo_root / policy.get("superseded_dir", "legacy/superseded-bundles"))
    destination = move_zip(zip_path, superseded_dir)

    receipt = {
        "type": "bundle_superseded",
        "bundle": zip_path.name,
        "moved_to": destination.relative_to(repo_root).as_posix(),
        "queue_entry": queue_entry,
        "success": True,
    }
    append_receipt(repo_root, receipt)
    return receipt


def move_unreadable_bundle(repo_root: Path, zip_path: Path, policy: Dict[str, Any], error: str) -> Dict[str, Any]:
    failed_dir = ensure_dir(repo_root / policy.get("failed_dir", "legacy/failed-bundles"))
    destination = move_zip(zip_path, failed_dir)

    receipt = {
        "type": "bundle_failed_manifest_read",
        "bundle": zip_path.name,
        "moved_to": destination.relative_to(repo_root).as_posix(),
        "error": error,
        "success": False,
    }
    append_receipt(repo_root, receipt)
    return receipt


def ingest_incoming(repo_root: Path) -> Dict[str, Any]:
    context = detect_context(repo_root)
    policy = load_core_policy(repo_root)

    incoming_dir = ensure_dir(repo_root / policy.get("incoming_dir", "incoming"))
    queue_plan = plan_incoming_bundles(incoming_dir)

    (repo_root / "core_lite_queue_plan.json").write_text(
        json.dumps(queue_plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    append_receipt(repo_root, {
        "type": "queue_planned",
        "queue_plan_path": "core_lite_queue_plan.json",
        "counts": queue_plan.get("counts", {}),
        "success": True,
    })

    receipts: List[Dict[str, Any]] = []

    for entry in queue_plan["failed_to_read"]:
        path = Path(entry["path"])
        if path.exists():
            receipts.append(move_unreadable_bundle(repo_root, path, policy, entry["error"]))

    for entry in queue_plan["superseded"]:
        path = Path(entry["path"])
        if path.exists():
            receipts.append(move_superseded_bundle(repo_root, path, policy, entry))

    for entry in queue_plan["process"]:
        path = Path(entry["path"])
        if path.exists():
            receipts.append(process_bundle(repo_root, path, policy, context))

    report = {
        "schema": "stegverse_core_lite_ingest_report.v2",
        "queue_plan_path": "core_lite_queue_plan.json",
        "bundle_count": len(queue_plan["process"]),
        "superseded_count": len(queue_plan["superseded"]),
        "failed_to_read_count": len(queue_plan["failed_to_read"]),
        "success": all(receipt.get("success") for receipt in receipts if receipt.get("type") != "bundle_failed_manifest_read") and not queue_plan["failed_to_read"],
        "receipts": receipts,
    }

    (repo_root / "core_lite_ingest_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return report
