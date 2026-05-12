# Core-Lite v0.8.1: Wire Source State Index

## Purpose

Core-Lite v0.8.1 wires the source state index into the normal `core_lite/cli.py run` path.

## Done criteria

```text
1. Core-Lite run generates .stegverse/source_state_index.json.
2. core_lite_run_summary.json includes source state fields.
3. A source_state_index_generated receipt is emitted.
4. Invalid local chain continuity fails the run.
```

## Runtime output

```text
.stegverse/source_state_index.json
core_lite_run_summary.json
.stegverse/receipts/core_lite_receipts.jsonl
```

Displayed without leading dots:

```text
stegverse/source_state_index.json
stegverse/receipts/core_lite_receipts.jsonl
```

## Core rule

```text
Only the most recent validated source may produce ALLOW.
```
