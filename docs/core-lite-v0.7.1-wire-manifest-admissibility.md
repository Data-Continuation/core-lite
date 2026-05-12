# Core-Lite v0.7.1: Wire Manifest Admissibility

## Purpose

Core-Lite v0.7.1 wires the v0.7 manifest admissibility validator into bundle ingestion.

## Done criteria

```text
1. load_bundle_manifest reads the bundle manifest.
2. validate_manifest checks target_repo and unclassified files.
3. validate_manifest calls validate_manifest_admissibility.
4. failed manifest admissibility prevents installation.
5. .stegverse/manifest_admissibility_report.json is written.
6. queue_planned receipt is emitted before bundle processing.
```

## Files

```text
core_lite/manifest.py
core_lite/ingest.py
docs/core-lite-v0.7.1-wire-manifest-admissibility.md
iosnoperiod.md
```

## Runtime output

```text
.stegverse/manifest_admissibility_report.json
core_lite_queue_plan.json
core_lite_ingest_report.json
```

Displayed without leading dot:

```text
stegverse/manifest_admissibility_report.json
```

## Rule

```text
A bundle may be present in incoming/.
It does not become installable until its manifest is admissible under the local core-lite policy.
```
