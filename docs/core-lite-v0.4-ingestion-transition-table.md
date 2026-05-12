# Core-Lite v0.4: Ingestion Transition Table

## Purpose

Core-Lite v0.4 defines the ingestion transition table.

## Canonical claim

```text
Ingestion is not file transfer. Ingestion is a governed transition sequence where every artifact, action, outcome, and generated artifact must remain hash-linked, authority-matched, locally recorded, and upward-reconcilable.
```

## Core correction

```text
No event completes at origin.
An event completes only after its outcome has been ingested, reconciled, and confirmed at the next governing layer.
```

## Entrypoint classes

```text
user_entrypoint_and_master_records_endpoint
master_records_endpoint_only
```

## Transition families

```text
external_entry
master_records_entry
queue
quarantine
installation
installation_recovery
succession
hash_integrity
authority
routing
confirmation
timeout
promotion
revocation
task_execution
```

## New files

```text
schemas/ingestion_transition_table.json
schemas/ingestion_transition_table.schema.json
core_lite/ingestion_transition_table.py
docs/core-lite-v0.4-ingestion-transition-table.md
```
