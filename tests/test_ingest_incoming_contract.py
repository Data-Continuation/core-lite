from __future__ import annotations

import json
import zipfile
from pathlib import Path

from core_lite.ingest import ingest_incoming, run_ingestion


def _write_bundle(root: Path) -> Path:
    bundle = root / "bundle"
    bundle.mkdir(parents=True)
    (bundle / "payload.txt").write_text("hello core-lite\n", encoding="utf-8")
    manifest = {
        "schema": "stegverse_test_bundle_manifest.v1",
        "bundle_id": "test-bundle",
        "purpose": "verify ingestion contract",
        "actor": "test-suite",
        "declared_paths": [
            {
                "path": "payload.txt",
                "action": "sandbox_only",
                "type": "candidate_file",
            }
        ],
    }
    (bundle / "bundle_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return bundle


def test_run_ingestion_accepts_repo_root_keyword_for_directory_bundle(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)

    report = run_ingestion(bundle, repo_root=tmp_path)

    assert report["success"] is True
    assert report["install_performed"] is False
    assert report["production_authority"] is False
    assert (tmp_path / "reports/current/core-lite-ingestion-sandbox-loop/report.json").exists()
    assert (tmp_path / "receipts/current/core-lite-ingestion-sandbox-loop/receipts.jsonl").exists()


def test_ingest_incoming_accepts_zip_bundles_and_remains_non_installing(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    zip_path = incoming / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in bundle.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(bundle).as_posix())

    report = ingest_incoming(tmp_path, skip_tasks=True)

    assert report["success"] is True
    assert report["bundle_count"] == 1
    assert report["install_authority"] is False
    assert report["production_authority"] is False
    assert report["results"][0]["bundle"]["submitted_bundle_type"] == "zip"
    assert report["results"][0]["bundle"]["extracted"] is True
    assert (tmp_path / "core_lite_ingest_report.json").exists()
