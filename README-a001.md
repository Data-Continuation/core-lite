# core-lite

Generalized StegVerse Core-Lite bootstrap engine.

Core-Lite is repo- and org-agnostic. It discovers its current repository context, accepts incoming bundles, reads each bundle manifest, installs declared files, routes runtime artifacts, emits receipts, and maintains an organization/repository registry.

## Core Rule

```text
The repo owns intent.
The bundle owns change instructions.
core-lite owns safe execution.
```

## What core-lite does

```text
1. Discover current org/repo.
2. Refresh the org/repo registry when GitHub token access is available.
3. Accept incoming/*.zip bundles.
4. Stage and inspect each bundle before installing anything.
5. Read .stegverse/ingest_manifest.json from the bundle.
6. Verify target_repo.
7. Install only declared files.
8. Reject unclassified files when policy requires it.
9. Exclude runtime artifacts.
10. Move successful bundles to legacy/ingested-bundles/.
11. Move failed bundles to legacy/failed-bundles/.
12. Emit append-only receipts.
13. Run declared repo-local tasks when configured.
```

## First ingestion establishes registry

On the first successful run, core-lite creates:

```text
.stegverse/org_registry.json
```

The registry records:

```text
org
repo
known repositories
active/missing/deleted_or_unreachable status
first_seen
last_seen
registry events
```

If the workflow has GitHub token access to list org repositories, core-lite refreshes the registry from the GitHub API. If not, it records the current repository only and marks the registry as limited-discovery.

## Deleted and new repo handling

Core-Lite never silently deletes registry entries.

```text
new repo discovered:
  add with status active

repo seen before but not discovered now:
  mark missing_or_unreachable

repo remains missing across later refreshes:
  keep history; do not erase automatically
```

This prevents a temporary permission/API failure from being misread as deletion.

## Minimal consuming repo footprint

A repo using core-lite only needs:

```text
incoming/.gitkeep
.stegverse/core-lite.json
.github/workflows/core-lite-intake.yml
```

Displayed without leading dot above. Real paths preserve the leading dots.

## Workflow model

The consuming repo workflow checks out this `core-lite` repo into `_core_lite` and runs:

```bash
python _core_lite/core_lite/cli.py run --repo-root .
```

## Bundle contract

Every incoming bundle must contain:

```text
.stegverse/ingest_manifest.json
```

The manifest declares target repo, install policy, file list, excluded runtime artifacts, and done criteria.

## Status

v0.1.0 bootstrap. Minimal, deterministic, standard-library only.
