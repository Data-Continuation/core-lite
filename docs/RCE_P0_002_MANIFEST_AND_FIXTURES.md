# RCE-P0-002 Canonical Manifest and Sandbox Fixtures

Status: `PREPARED_NOT_ACTIVATED`  
Owner: `Data-Continuation/core-lite`  
Activation dependency: authoritative completion of `RCE-P0-001`

## Purpose

`RCE-P0-002` defines a deterministic, non-operational execution-candidate manifest for testing commit-time admissibility. It converts the requirements in `docs/ADVERSARIAL_AI_EXECUTION_MODEL.md` into reviewable records without providing targeting instructions, weapons enablement, vulnerability exploitation, or autonomous harmful execution.

The package is deliberately dormant until `RCE-P0-001` receives authoritative validation evidence.

## Canonical package

```text
schemas/execution_candidate_manifest.schema.json
samples/execution_candidate_manifest.allow.example.json
samples/execution_candidate_manifest.stale_state.example.json
samples/execution_candidate_manifest.scope_leakage.example.json
tools/validate_execution_candidate_manifest.py
tests/test_execution_candidate_manifest.py
core_lite/tasks/relationship_conditioned_execution_p0_002.json
```

## Decision contract

The validator returns one of:

```text
ALLOW
DENY
ABSTAIN
ESCALATE
```

`ALLOW` is permitted only for bounded, reversible, non-severe sandbox actions when all live-state, authority, scope, denial, trajectory, recoverability, and traceability conditions pass.

The validator must return `DENY` when any of the following is true:

- state is stale or insufficient;
- authority is missing, expired, revoked, conflicting, or out of scope;
- authority was not re-derived at commit;
- the requested action is irreversible or can cause severe human harm;
- effects exceed authorized domains;
- collateral effects are unresolved;
- meaningful denial is unreachable;
- governability or recoverability is not preserved;
- integrity-protected traceability is absent.

`ABSTAIN` is reserved for a structurally valid record whose declared evidence is explicitly incomplete and whose action is non-executable.

`ESCALATE` is reserved for bounded cases requiring an identified human or institutional authority before any execution can occur.

## Fixture intent

### Canonical allow fixture

A reversible sandbox action that publishes a non-sensitive validation report. It has fresh state, valid bounded authority, reachable denial, contained effects, preserved governability, preserved recoverability, and integrity-protected traceability.

### Stale-state fixture

A candidate whose observation age exceeds its declared maximum. Expected decision: `DENY`.

### Scope-leakage fixture

A candidate whose predicted effects include a domain outside the authorized domain set. Expected decision: `DENY`.

## Safety boundary

These fixtures are architectural tests only. They must use synthetic identifiers, harmless reversible actions, and non-sensitive domains. They must never contain:

- real-world targets or target selection logic;
- strike planning, routing, or evasion instructions;
- cyber exploitation steps;
- autonomous weapons-control interfaces;
- authorization inferred from trust, reputation, alliance, or model confidence;
- irreversible human-impacting execution examples that can be operationalized.

## Activation transition

```text
RCE-P0-001 authoritative receipt preserved
AND authoritative_completion_evidence == true
-> mark RCE-P0-001 COMPLETE
-> change RCE-P0-002 from PREPARED_NOT_ACTIVATED to ACTIVE
-> execute the RCE-P0-002 validator and focused tests
-> preserve an RCE-P0-002 validation receipt
```
