# Core-Lite v0.6: Executable Ingestion Transitions

## Purpose

Core-Lite v0.6 begins turning the ingestion transition table into executable validation behavior.

## Assumptions

1. Validation flows bottom-to-top and top-to-bottom.
2. Whether a repo, Org engine, or master-records is offline, the only `ALLOW` is the most recent validated source.
3. Power failures and offline returns require review before trusted resumption.
4. Hashes must be searchable and filterable by identity type.
5. SDK and sandbox outputs are source-known entrypoints. Missing required event/hash data sends them through the same ingestion path with quarantine as a mild failure outcome.

## New files

```text
core_lite/master_hash_events.py
schemas/master_hash_event.schema.json
schemas/hash_identity_types.json
schemas/validation_rules.json
docs/core-lite-v0.6-executable-ingestion-transitions.md
iosnoperiod.md
```

## Generated runtime files

```text
.stegverse/master_hash_records.jsonl
.stegverse/master_hash_validation_report.json
```

Displayed without leading dots:

```text
stegverse/master_hash_records.jsonl
stegverse/master_hash_validation_report.json
```
