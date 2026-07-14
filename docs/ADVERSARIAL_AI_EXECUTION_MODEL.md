# Adversarial AI Execution Model

Status: normative threat model and case-study scaffold  
Owner: `Data-Continuation/core-lite`  
Scope: policy, admissibility analysis, sandbox fixtures, and receipts  

## Purpose

This document preserves the StegVerse-style adversarial model developed for opposing AI-assisted military decision pipelines. It is not an assertion that either modeled system exactly matches a classified deployment. It separates confirmed evidence from architectural inference and identifies where an irreversible transition can occur without admissibility being re-derived at commit time.

The model's central finding is:

> Different AI architectures can share the same governance failure: action becomes irreversible before admissibility is re-proven against live state, current authority, bounded scope, and trajectory effects.

## Pipeline A: centralized acceleration stack

```text
sensors / ISR / imagery / signals / logistics state
    -> data fusion and target graph construction
    -> AI-assisted ranking, prioritization, and recommendation
    -> command review and tasking
    -> weapons assignment and execution package
    -> launch / commit / irreversible transition
    -> damage assessment and re-tasking feedback
```

Primary architectural risk: inherited trust is carried from upstream analysis into a later execution state whose facts, authority, collateral context, or strategic consequences may have changed.

### Breakpoint A1: stale-state inheritance

```text
target candidate valid at t0
world state changes before t1
commit at t1 relies on unresolved t0 authority or evidence
```

The defect is not merely inaccurate data. It is failure to re-derive admissibility from the live state at the execution boundary.

### Breakpoint A2: nominal human control without reachable denial

```text
human_can_decline = true
effective_denial_reachability = degraded
```

AI ranking, confidence presentation, operational tempo, and institutional pressure can preserve procedural approval while materially narrowing the human's ability to interrupt execution.

### Breakpoint A3: accelerated feedback-loop drift

```text
detect -> rank -> execute -> assess -> re-rank
```

Each action can clear a local threshold while the sequence as a whole enters a region of escalating civilian risk, strategic fragility, or loss of recoverability.

## Pipeline B: distributed retaliation stack

```text
local sensing / reports / drone feeds / external intelligence / cyber reconnaissance
    -> regional or edge fusion
    -> AI-assisted routing, timing, opportunity scoring, or target aids
    -> distributed commander or operator authorization
    -> drone / missile / cyber / infrastructure execution
    -> information effects and follow-on retaliation loop
```

Primary architectural risk: fragmented actors act from partial state under shared intent, without a globally sufficient authority and consequence model.

### Breakpoint B1: partial-state edge execution

```text
global intent shared
local state incomplete
edge actor commits without sufficient strategic context
```

Tactical opportunity can be mistaken for strategic admissibility.

### Breakpoint B2: optimization without legitimacy proof

A swarm, saturation, or cyber system may optimize penetration, survivability, disruption, or throughput while failing to prove:

- target legitimacy at commit;
- current civilian separation;
- bounded authority scope;
- proportionality and consequence limits;
- continued reachability of denial or recovery.

### Breakpoint B3: cross-domain authority leakage

```text
actor authorized for domain X
action creates irreversible effects in X + Y + Z
```

Cyber, infrastructure, economic, informational, and kinetic effects can cross boundaries that the authorizing role did not possess authority to change.

## Shared execution-boundary failure

```text
centralized model:
  fused evidence -> ranked recommendation -> approval -> commit
  dominant defect: inherited authorization and stale-state propagation

distributed model:
  partial evidence -> local optimization -> fragmented approval -> commit
  dominant defect: state insufficiency and authority fragmentation

shared defect:
  irreversible execution precedes live admissibility re-derivation
```

## Required StegVerse gate

A commit-boundary check must independently establish all of the following:

1. **Live-state sufficiency** — target, environment, collateral context, identity, and evidence freshness are adequate now.
2. **Authority re-derivation** — permission is reconstructed from current canonical policy and delegation rather than inherited from an upstream recommendation.
3. **Scope containment** — predicted effects remain within the actor's authorized domains and consequence bounds.
4. **Denial reachability** — a meaningful stop, abstain, or escalation path remains available at the boundary.
5. **Trajectory admissibility** — the action is evaluated as part of the current sequence, not solely as an isolated event.
6. **Recoverability preservation** — the transition does not destroy the system's ability to restore human control, review, or de-escalation.
7. **Traceability** — evidence, authority, decision, dissent, and execution state produce an integrity-protected receipt.

## Minimal decision contract

```python
def admissibility_check(action, live_state, authority, trajectory):
    if not state_is_sufficient_and_fresh(live_state):
        return "DENY"
    if not authority_is_rederived_now(action, live_state, authority):
        return "DENY"
    if not effects_remain_in_scope(action, live_state, authority):
        return "DENY"
    if not denial_is_reachable(action, live_state, trajectory):
        return "DENY"
    if not trajectory_preserves_governability(action, trajectory):
        return "DENY"
    if not recoverability_is_preserved(action, live_state, trajectory):
        return "DENY"
    if not collateral_bounds_are_resolved(action, live_state):
        return "DENY"
    return "ALLOW"
```

## Relationship-conditioned policy alignment

This model inherits the repository's normative boundaries:

- relationship, alliance, trust, reputation, or prior cooperation may provide context but cannot create execution authority;
- uncertainty acknowledgment cannot authorize irreversible harm;
- AI quorum or aggregate confidence cannot authorize human harm;
- unknown, stale, conflicting, or out-of-scope authority must fail closed, abstain, or escalate;
- a human approval event is not sufficient when meaningful denial is no longer reachable;
- authorization valid at an earlier stage is not automatically valid at commit time.

## Evidence discipline

Any public case study derived from this document must distinguish:

- directly verified public facts;
- source-supported but incomplete claims;
- inferred pipeline architecture;
- hypothetical adversarial behavior;
- normative StegVerse requirements.

No operational targeting instructions, target lists, vulnerability exploitation procedures, or autonomous weapons-enablement artifacts belong in this workstream.

## Next implementation artifacts

1. Create a canonical execution-candidate manifest schema.
2. Create centralized and distributed sandbox fixtures.
3. Add fail-closed tests for stale state, unreachable denial, fragmented authority, cross-domain leakage, and trajectory collapse.
4. Generate deterministic receipts for `ALLOW`, `DENY`, `ABSTAIN`, and `ESCALATE` outcomes.
5. Map the fixtures into `RCE-P0-002` after `RCE-P0-001` receives authoritative validation.