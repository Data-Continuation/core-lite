# Core-Lite v0.8: Source State Index

## Purpose

Core-Lite v0.8 adds a source state index for answering:

```text
What is the latest validated source?
Is the local chain coherent?
Are parent links locally resolved?
Can this scope produce ALLOW?
```

## Core rule

```text
Only the most recent validated source may produce ALLOW.
```

## New files

```text
core_lite/source_state_index.py
schemas/source_state_index.schema.json
docs/core-lite-v0.8-source-state-index.md
iosnoperiod.md
```

## Runtime output

```text
.stegverse/source_state_index.json
```

Displayed without leading dot:

```text
stegverse/source_state_index.json
```

## Validation dimensions

```text
latest_validated_source
local_chain_valid
parent_links_valid_locally
blocking_outcome
allow_status_by_scope
```
