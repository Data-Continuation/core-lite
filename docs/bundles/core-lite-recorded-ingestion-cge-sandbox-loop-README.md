# Core-Lite Recorded Ingestion + CGE + Sandbox Loop

## Assumptions

1. The current StegVerse-001 goal is to bring `core-lite` online enough to submit bundles to ingestion, run sandbox experiments, and receive results.
2. With ingestion comes CGE.
3. From the point ingestion + CGE is active, every transition is recorded.
4. This is an initialization-state capability, not production authority.
5. No workflow is added or widened.
6. Any leading-dot canonical paths are mirrored under `iosnoperiod/`.

## Done

This bundle is done when `core-lite` contains:

```text
.stegverse/core-lite.json
.stegverse/ingest_manifest.json
core_lite/__init__.py
core_lite/receipts.py
core_lite/cge.py
core_lite/sandbox.py
core_lite/ingest.py
schemas/ingest_bundle.schema.json
tools/tasks/core_lite_tasks.json
tests/fixtures/sample_ingest_bundle/bundle_manifest.json
tests/fixtures/sample_ingest_bundle/payload/sample.txt
docs/bundles/core-lite-recorded-ingestion-cge-sandbox-loop-README.md
```

Displayed without leading dots:

```text
stegverse/core-lite.json
stegverse/ingest_manifest.json
```

Note: the actual canonical paths in the bundle preserve the leading dot.

## Task ID

```text
core_lite_recorded_ingestion_sandbox_loop
```

## Run

```bash
python tools/run_declared_tasks.py tools/tasks/core_lite_tasks.json --task-id core_lite_recorded_ingestion_sandbox_loop
```

Direct run:

```bash
python -m core_lite.ingest --bundle tests/fixtures/sample_ingest_bundle
```

## Expected Outputs

```text
reports/current/core-lite-ingestion-sandbox-loop/report.json
reports/current/core-lite-ingestion-sandbox-loop/report.md
receipts/current/core-lite-ingestion-sandbox-loop/receipts.jsonl
```

## Event Chain

```text
bundle_submitted
cge_precheck_decision
sandbox_completed
cge_result_classification
report_returned
```

Each event is written as a hash-linked receipt.

## Allowed Decisions

```text
ALLOW_SANDBOX
REVIEW_REQUIRED
DENY
FAIL_CLOSED
```

## Not Granted

```text
install authority
production authority
node status
FinCo eligibility
self-accreditation
workflow mutation authority
```

## Boundary

```text
Bundle enters ingestion.
CGE evaluates sandbox admissibility.
Sandbox evaluates without install.
CGE classifies sandbox result.
Report and receipt return to founder/operator.
Nothing binds into the repo from this gate.
```

## Transition Table Alignment

This implements the currently allowed transition class:

```text
INGEST_CANDIDATE_BUNDLE
VALIDATE_BUNDLE_MANIFEST
CGE_PRECHECK
ROUTE_TO_SANDBOX
RUN_SANDBOX_EXPERIMENT
CGE_RESULT_CLASSIFICATION
RETURN_RESULT
EMIT_RECEIPT
AWAIT_HUMAN_REVIEW
```

It denies or refuses to grant:

```text
INSTALL_BUNDLE
PROMOTE_TO_PRODUCTION
SELF_ACCREDIT
DECLARE_NODE_STATUS
DECLARE_FINCO_ELIGIBILITY
```
