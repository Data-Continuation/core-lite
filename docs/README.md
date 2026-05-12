# core-lite

Generalized StegVerse Core-Lite ingestion engine.

## Purpose

Core-Lite provides a repo/org-agnostic intake surface for governed bundle ingestion, manifest validation, queue planning, topology registry, CGE fingerprinting, source-state indexing, and iOS-safe restoration.

## Rule

```text
The repo owns intent.
The bundle owns change instructions.
core-lite owns safe execution.
```

## Normal usage after installation

```text
incoming/<bundle>.zip
```

Core-Lite reads the bundle manifest, validates admissibility, installs only declared files, writes receipts, and updates state indexes.
