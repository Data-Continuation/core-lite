# Relationship-Conditioned Execution Handoff

## Status

This record preserves the design decisions and generated-artifact lineage from the AI–human self-sacrifice governance discussion. The prior ZIPs are **unvalidated conversation artifacts**, not production-ready releases or install authority.

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
| v1.0 | relationship state, history, policy, ethics, non-guarantee, temporal identity, receipt integration | described in-thread; not durably packaged here |
| v1.1 | distributed witnesses, quorum, anomaly detection, trust decay, recovery routing | scaffold only |
| v1.2 | global state, stability scoring, cascade prevention | scaffold only |
| v1.3 | receipt chain, continuous state, checkpoint, replay | scaffold only |
| v1.4 | predictive risk, drift detection, throttling | scaffold only |
| v1.5 | outcome feedback and threshold adaptation | scaffold only; unsafe without bounded policy-change authority |
| v2.0 | multi-agent registry, conflict detection, negotiation, incentives | scaffold only |
| v2.1 | adversarial detection, reputation change, slashing/filtering | scaffold only; failure rate is not proof of adversarial intent |
| v2.2 | weighted voting, quorum, consensus, execution | scaffold only; current voting model does not encode agent choices and must not execute human-impacting decisions |

## Known blockers and defects

1. Bundle manifests do not conform to the canonical Core-Lite manifest shape documented for incoming bundles.
2. No file-level hashes, byte counts, provenance receipts, or install destinations were preserved in the generated manifests.
3. Versions were produced as incremental standalone bundles rather than one verified dependency-aware distribution.
4. Most state is process-local and non-durable.
5. Receipt hashing uses wall-clock time and does not establish deterministic replay.
6. Rollback restores a stored object but does not reverse external effects.
7. Predictive and anomaly logic uses simplistic heuristics with no calibration or context-of-use declaration.
8. Adaptive threshold code mutates shared state and may progressively exceed valid bounds.
9. Reputation and slashing mechanisms conflate failure, malice, degraded capability, and environmental uncertainty.
10. The v2.2 voting scaffold grants every agent weight to every proposal, producing non-expressive votes.
11. No hard invariant separates advisory output from execution authority over human-impacting actions.
12. No tests demonstrate StegVerse ethics, boundary preservation, witness independence, Byzantine tolerance, chain verification, replay equivalence, or fail-closed behavior.

## Required reconstruction target

Do not ingest the prior ZIPs as-is. Rebuild the concept as a governed Core-Lite candidate package with:

- a canonical manifest with per-file hashes and sizes;
- explicit target paths and dependency order;
- policy schemas separating human safety, relationship role, evidence posture, and execution authority;
- a non-execution invariant for self-harm or self-sacrificial human-impacting actions;
- deterministic receipts and chain verification;
- durable state storage and migration rules;
- witness independence and conflict-of-interest declarations;
- bounded, review-gated policy adaptation rather than autonomous threshold mutation;
- tests for ALLOW, BLOCK, ESCALATE, ABSTAIN, and FAIL_CLOSED outcomes;
- sandbox validation before any destination installation;
- ingestion receipts and master-record pointers after authorized installation.

## Permitted continuation scope

A continuation session may create schemas, validators, tests, sandbox fixtures, threat models, decision receipts, and a canonical ingestion candidate. It may not represent the prior ZIPs as production-ready, authorize irreversible harm, infer human intent from reputation or history alone, or allow collective AI voting to override human safety boundaries.

## Next task

Build `RCE-P0-001`: a normative relationship-conditioned human-decision policy and machine-readable schema before rebuilding executable modules.
