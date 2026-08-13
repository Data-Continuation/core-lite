# Manifest Route Carrier Mirror Handoff

```text
goal_id: CORE-LITE-MANIFEST-ROUTE-CARRIER-001
repository: Data-Continuation/core-lite
branch: feat/manifest-route-carrier
parent_handoff: CORE_LITE_MIRROR_HANDOFF.md
implementation_state: INSTALLED_PENDING_INTEGRATION_VALIDATION
release_state: NOT_RELEASED
```

## Governing invariant

Every governed ecosystem transaction begins with a manifest (supplied or applied at entry). The manifest declares the intended route. Each checkpoint emits a receipt that is recorded in Master Records; only the recorded receipt clears the next declared route leg. The heartbeat carrier signal preserves transaction identity, route position, prior receipt, and prior event hash across the route.

## Installed surfaces

```text
core_lite/transaction_route.py
tests/test_transaction_route.py
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

The carrier emits and requires `RECORDED` custody for the corresponding state transitions before advancing. The route manifest contains `execution_provenance`; production-validation and enclosed-demo lane provenance are therefore part of transaction identity rather than external documentation.

## Heartbeat carrier

Each transition includes `stegverse.heartbeat-carrier-signal.v1` with route manifest ID, transaction ID, sequence, checkpoint, previous route receipt, and previous event hash. This is transaction continuity/carrier state, not a grant of authority.

## Cross-repository dependencies

```text
Master Records generic manifested-route event custody: master-records/orchestration PR #30 branch
SDK evaluator integration: StegVerse-org/StegVerse-SDK PR #23 branch
Canonical governance handler: StegVerse-Labs/StegCore
```

## Remaining before evaluator-ready claim

```text
1. expose/install importable core-lite package contract for SDK use;
2. bind SDK governed evaluator run to this carrier rather than direct StegCore invocation;
3. bind transition sink to authenticated Master Records manifested-route event API;
4. prove missing/unrecorded checkpoint blocks advancement;
5. prove production-validation provenance is retained in manifested route and exact-run evidence;
6. execute integrated SDK -> ingestion/CGE -> StegCore -> ingestion/CGE -> SDK run and replay/reconstruction validation.
```

No evaluator-ready, release, production activation, or consequence-authority claim is made by this branch until those validations pass.
