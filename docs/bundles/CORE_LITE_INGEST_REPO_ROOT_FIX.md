# Core-Lite Ingest `repo_root` Fix Bundle

## Assumptions

1. The first receipt failure has been repaired.
2. The new failing workflow is still `Core-Lite Intake`.
3. The current blocker is `TypeError: run_ingestion() got an unexpected keyword argument 'repo_root'`.
4. The failing call path is `ingest_incoming()` calling `run_ingestion(bundle, repo_root=root)`.
5. Incoming bundles are expected to arrive as ZIP files or bundle directories.
6. No workflow changes are needed.

## Done Means

This bundle is done when:

1. `run_ingestion()` accepts `repo_root`.
2. `ingest_incoming()` can call `run_ingestion(bundle, repo_root=root)` without TypeError.
3. Incoming ZIP bundles can be sandbox-read without install authority.
4. Reports and receipts are written relative to the provided repo root.
5. Ingestion remains non-installing and non-production-authorizing.
6. Contract tests pass.

## Files Included

```text
core_lite/ingest.py
tests/test_ingest_incoming_contract.py
docs/bundles/CORE_LITE_INGEST_REPO_ROOT_FIX.md
bundle_manifest.json
iosnoperiod.md
BUILD_VERIFICATION.json
```

## Primary Fix

The replacement `core_lite/ingest.py` updates:

```text
run_ingestion(bundle, repo_root=".")
```

and preserves the existing call from `ingest_incoming()`:

```text
run_ingestion(bundle, repo_root=root)
```

## Additional Operational Repair

The previous implementation collected only files from `incoming/`, but `run_ingestion()` expected a directory containing a manifest. This bundle allows incoming candidates to be either:

```text
incoming/<bundle-directory>/
incoming/<bundle>.zip
```

ZIP bundles are extracted into a temporary sandbox-read location, evaluated, and not installed.

## Verification Commands

Run from repository root:

```bash
python -m pytest tests/test_ingest_incoming_contract.py
python -m core_lite.cli run --repo-root . --skip-tasks
```

## Boundary Notes

No production authority is added.

No install authority is added.

No workflow files are changed.

This is a mechanical operational repair to the existing Core-Lite intake path.
