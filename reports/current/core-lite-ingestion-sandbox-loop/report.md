# Core-Lite Recorded Ingestion + CGE + Sandbox Loop Report

## Status

```text
success: true
final_decision: REVIEW_REQUIRED
bundle_id: sample-core-lite-ingestion-sandbox-loop-001
install_performed: false
```

## Boundary

```text
Bundle entered ingestion.
CGE precheck evaluated the manifest.
Sandbox evaluated without install.
CGE classified the sandbox result.
Founder/operator review remains required.
```

## CGE Precheck

```text
decision: ALLOW_SANDBOX
basis: bundle manifest is admissible for sandbox evaluation only
```

## CGE Result Classification

```text
decision: REVIEW_REQUIRED
basis: sandbox completed; founder/operator review required before any install gate
```

## Evaluated Files

- `payload/sample.txt` sha256=`8c7fe5b6713d176f40680fac7d7ca59d3b1c1fa175ab5da2753f51e0ee16dbf2`

## Receipt Chain

```text
receipt_path: receipts/current/core-lite-ingestion-sandbox-loop/receipts.jsonl
receipt_count: 4
```
