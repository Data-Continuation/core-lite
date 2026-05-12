# Core-Lite v0.3: Incoming Bundle Queue Protocol

## Purpose

Core-Lite v0.3 adds deterministic processing rules for multiple `incoming/*.zip` bundles.

## Bundle processing order

```text
Priority first:
  Critical
  Medium
  Low
  NonCritical

Then version order:
  oldest version -> newest version

Then chronology:
  oldest file timestamp -> newest file timestamp
```

## Succession modes

### versioning

```text
Process all queued versions in version order.
```

### supersede

```text
For the same bundle family, keep only the winning superseding bundle.
Move older queued bundles to legacy/superseded-bundles/.
```

## Manifest fields

Bundles may include:

```json
{
  "priority": "Critical",
  "bundle_family": "stage-5-boundary-transition",
  "succession": {
    "mode": "supersede",
    "family": "stage-5-boundary-transition"
  }
}
```

If omitted:

```text
priority defaults to Low
succession defaults to versioning
family defaults to bundle_id
```

## Generated artifacts

```text
core_lite_queue_plan.json
core_lite_ingest_report.json
.stegverse/receipts/core_lite_receipts.jsonl
```

## Done criteria

```text
1. All incoming bundles are read before processing.
2. Queue plan is generated.
3. Superseded bundles are moved to legacy/superseded-bundles/.
4. Unreadable bundles are moved to legacy/failed-bundles/.
5. Remaining bundles are processed Critical -> Medium -> Low -> NonCritical.
6. For equal priority, versions process oldest -> newest.
7. For equal priority/version, chronology processes oldest -> newest.
```
