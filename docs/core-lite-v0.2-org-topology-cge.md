# Core-Lite v0.2: Org Topology, Shim Planning, and CGE Fingerprinting

## Purpose

Core-Lite v0.2 upgrades core-lite from repo-local ingestion into an Org-level topology and monitoring surface.

## Core claim

```text
CGE fingerprinting becomes meaningful when the system has a governed ingestion topology.
```

## Canonical framing

```text
A repo can be checked.
An Org can be fingerprinted.
A multi-Org ecosystem can be governed.
```

## New generated artifacts

```text
.stegverse/ingestion_topology_registry.json
.stegverse/repo_shim_coverage_report.json
.stegverse/cge_fingerprint.json
.stegverse/receipts/core_lite_receipts.jsonl
```

Displayed without leading dots above where needed; real paths preserve them.

## Drift flags

```text
missing_shim
unknown_shim_state
runtime_artifacts_in_source_root
failed_bundle_history_present
unexpected_workflow
```

## Current known ingestion topology

Org-level engines:

```text
Installed:
  Data-Continuation/core-lite
  StegVerse-org/demo_ingest_engine

Attempted:
  BCAT-GCAT-Engine/core-lite-prod

Missing:
  master-records
  AaCT-E
```

Repo-level engines:

```text
StegGhost/entity-sandbox/runner
StegVerse-Labs/Site
```
