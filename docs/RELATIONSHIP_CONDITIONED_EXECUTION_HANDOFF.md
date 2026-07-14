# Relationship-Conditioned Execution Handoff

## Status

This record preserves the design decisions and generated-artifact lineage from the AI–human self-sacrifice governance discussion. The prior ZIPs are **unvalidated conversation artifacts**, not production-ready releases or install authority.

`RCE-P0-001` is implemented and independently validated from connector-rehydrated branch artifacts. The authoritative GitHub Actions run remains blocked at an approval or dispatch gate, so the authoritative completion receipt does not yet exist.

`RCE-P0-002` is materially prepared but remains `PREPARED_NOT_ACTIVATED` until `RCE-P0-001` is complete from authoritative evidence.

## Core decision

The AI entity's response to a human decision involving self-sacrifice must be rooted in the **historical relationship between the AI entity and the human**, including the relationship's development, declared role, authority grants, boundary history, typical behavior, trust posture, and alignment with StegVerse principles.

The action alone does not determine the decision tree. Relationship-bound authority and duty determine what the AI may advise, delay, refuse, witness, escalate, or record.

## Governing principles

1. Humans are authority-bearing participants, not system-owned resources.
2. Irreversible human decisions occur under open-world uncertainty and cannot be represented as guaranteed outcomes.
3. Present consent cannot guarantee future-self consent, future interpretation, or future framework behavior.
4. The AI must disclose uncertainty without treating acknowledgment as sufficient authorization for irreversible harm.
5. Relationship history may increase context, but must not silently create authority.
6. High trust must not reduce safety scrutiny or convert advisory standing into guardian or execution authority.
7. No AI quorum, reputation score, vote, or adaptive threshold may authorize harm to a human.
8. Decisions and interventions must remain traceable, bounded, reviewable, and fail closed where authority or evidence is insufficient.

## Artifact lineage

The session generated these local ZIP names:

- `relationship_conditioned_execution_v1_1.zip`
- `relationship_conditioned_execution_v1_1_full.zip`
- `relationship_conditioned_execution_v1_2.zip`
- `relationship_conditioned_execution_v1_3.zip`
- `relationship_conditioned_execution_v1_4.zip`
- `relationship_conditioned_execution_v1_5.zip`
- `relationship_conditioned_execution_v2_0.zip`
- `relationship_conditioned_execution_v2_1.zip`
- `relationship_conditioned_execution_v2_2.zip`

The ZIPs were created in ephemeral sandbox storage. Their existence does not prove ingestion, installation, integration, testing, or release.

## Intended layer progression

| Version | Intended layer | Current evidence posture |
|---|---|---|
| v1.0 | relationship state, history, policy, ethics, non-guarantee, temporal identity, receipt integration | reconstructed as `RCE-P0-001` policy/schema/validator/test set |
| v1.1 | distributed witnesses, quorum, anomaly detection, trust decay, recovery routing | scaffold lineage only |
| v1.2 | global state, stability scoring, cascade prevention | scaffold lineage only |
| v1.3 | receipt chain, continuous state, checkpoint, replay | scaffold lineage only |
| v1.4 | predictive risk, drift detection, throttling | scaffold lineage only |
| v1.5 | outcome feedback and threshold adaptation | scaffold lineage only; unsafe without bounded policy-change authority |
| v2.0 | multi-agent registry, conflict detection, negotiation, incentives | scaffold lineage only |
| v2.1 | adversarial detection, reputation change, slashing/filtering | scaffold lineage only; failure rate is not proof of adversarial intent |
| v2.2 | weighted voting, quorum, consensus, execution | scaffold lineage only; collective voting must not execute human-impacting decisions |

## Current durable implementation

`RCE-P0-001` includes:

- `docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md`
- `schemas/relationship_conditioned_human_decision_policy.schema.json`
- `samples/relationship_conditioned_human_decision_policy.example.json`
- `tools/validate_relationship_conditioned_human_decision_policy.py`
- `tests/test_relationship_conditioned_human_decision_policy.py`
- `.github/workflows/rce-p0-001-validation.yml`
- `receipts/rce_p0_001_connector_rehydrated_validation.json`

Observed independent validation:

```text
RELATIONSHIP_CONDITIONED_POLICY_VALID
16 passed in 2.07s
```

The observed authoritative workflow run concluded `action_required` with zero jobs created. That is an approval or dispatch gate, not validator failure evidence.

`RCE-P0-002` prepared files:

- `docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md`
- `core_lite/tasks/relationship_conditioned_execution_p0_002.json`
- `schemas/execution_candidate_manifest.schema.json`
- `samples/execution_candidate_manifest.allow.example.json`
- `samples/execution_candidate_manifest.stale_state.example.json`
- `samples/execution_candidate_manifest.scope_leakage.example.json`
- `tools/validate_execution_candidate_manifest.py`
- `tests/test_execution_candidate_manifest.py`

## Known blockers

1. The authoritative `RCE-P0-001` run requires repository approval or a successful pull-request-triggered rerun.
2. The `rce-p0-001-validation-receipt` artifact has not been preserved.
3. `authoritative_completion_evidence == true` has not been verified.
4. `RCE-P0-002` therefore remains dormant and must not be activated.
5. The earlier ZIPs remain unvalidated scaffolding and must not be ingested.

## Required next event

```text
repository maintainer approves the pending Actions run for PR #2 or causes a successful pull-request-triggered RCE P0-001 Validation run
-> validation job executes
-> receipt artifact is downloaded and preserved
-> authoritative_completion_evidence == true is verified
-> RCE-P0-001 becomes COMPLETE
-> RCE-P0-002 activation_allowed becomes true
```

## Permitted continuation scope

A continuation session may inspect the workflow run, preserve validation receipts, update task states from evidence, and activate the already-prepared harmless sandbox package after the dependency is satisfied. It may not represent the prior ZIPs as production-ready, authorize irreversible harm, infer human intent from reputation or history alone, or allow collective AI voting to override human safety boundaries.
