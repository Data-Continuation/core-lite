# Manifest Route Carrier Mirror Handoff

```text
goal_id: CORE-LITE-MANIFEST-ROUTE-CARRIER-001
repository: Data-Continuation/core-lite
branch: feat/manifest-route-carrier
parent_handoff: CORE_LITE_MIRROR_HANDOFF.md
implementation_state: COMPLETE_CONTRACT_VALIDATED_PENDING_CROSS_REPO_INTEGRATION
release_state: NOT_RELEASED
```

## Governing invariant

Every governed ecosystem transaction begins with a manifest (supplied or applied at entry). The manifest declares the intended route. Each checkpoint emits a receipt that is recorded in Master Records; only the recorded receipt clears the next declared route leg. The heartbeat carrier signal preserves transaction identity, route position, prior receipt, and prior event hash across the route.

## Installed surfaces

```text
core_lite/transaction_route.py
tests/test_transaction_route.py
pyproject.toml
validation/MANIFEST_ROUTE_CARRIER_2026-08-13.md
MANIFEST_ROUTE_CARRIER_MIRROR_HANDOFF.md
```

## Canonical validation route for the SDK evaluator lane

```text
SDK entry
-> ingestion/CGE
-> StegCore
-> ingestion/CGE return
-> SDK return
```

The carrier emits and requires `RECORDED` custody for every route transition before advancing. Default route transition sequence:

```text
MANIFEST_ESTABLISHED
SDK_ENTERED
INGESTION_ENTERED
CGE_ADMITTED
CGE_ROUTED
MODULE_ENTERED
MODULE_RESULT
CGE_RETURN_INGESTED
ROUTE_CLEARED
RETURNED
```

The route manifest contains `execution_provenance`; production-validation and enclosed-demo lane provenance are therefore part of transaction identity rather than external documentation.

## Heartbeat carrier

Each transition includes `stegverse.heartbeat-carrier-signal.v1` with route manifest ID, transaction ID, sequence, checkpoint, previous route receipt, and previous event hash. This is transaction continuity/carrier state, not a grant of authority.

## Completed scoped tasks

```text
[done] importable Python package contract via pyproject.toml
[done] receipt-gated manifest route carrier
[done] production-validation default route
[done] heartbeat carrier state on every route transition
[done] fail closed when transition custody is not RECORDED
[done] lane provenance bound into route-manifest identity
[done] isolated carrier contract validation: PASS
[done] SDK production-validation runtime consumes this carrier on its active branch
[done] SDK transition sink targets Master Records generic manifested-route custody API
[done] StegCore externally established transaction identity hook merged via StegCore PR #89
```

## Cross-repository dependencies

```text
Master Records generic manifested-route event custody: master-records/orchestration PR #30
SDK evaluator integration: StegVerse-org/StegVerse-SDK PR #23
Canonical governance handler: StegVerse-Labs/StegCore PR #89 MERGED
```

## Remaining before evaluator-ready claim

```text
1. merge/validate Master Records generic manifested-route custody;
2. merge this route carrier after final review;
3. update SDK dependency pins to merged commits;
4. execute integrated authenticated SDK -> ingestion/CGE -> StegCore -> ingestion/CGE -> SDK run;
5. verify exact-run MR-* custody and full MRR-* route trace share one transaction identity;
6. execute replay/reconstruction and verify MRO-* transition custody;
7. retain evaluator-facing PASS evidence and genuine receipt locators.
```

Hosted repository self-test was not executed because the existing Core-Lite Self Test is `workflow_dispatch` only and no dispatch surface is available in this session. The strongest available isolated carrier contract is retained in `validation/MANIFEST_ROUTE_CARRIER_2026-08-13.md`. Do not convert that into a hosted-integration claim.
