# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.10.1-rce-p0-007-accelerated-reconciliation
```

## Current status

```text
MIRROR_HANDOFF_PRESENT
ECOSYSTEM_MANAGEMENT_WORKFLOW_COVERED
RCE_P0_001_COMPLETE
RCE_P0_002_COMPLETE
RCE_P0_003_COMPLETE
RCE_P0_004_COMPLETE
RCE_P0_005_COMPLETE
RCE_P0_006_COMPLETE
RCE_P0_007_LIFECYCLE_ACTIVE
RCE_P0_008_THROUGH_P0_014_IMPLEMENTED_DEPENDENCY_GATED
AUTONOMOUS_RECONCILIATION_EVERY_FIVE_MINUTES
HISTORICAL_QUARANTINE_ALERTS_PRESERVED
MANUAL_ACTIONS_REQUIRED_NONE
SANDBOX_ONLY
NO_PRODUCTION_DESTINATION_AUTHORITY
```

## Authoritative chain

```text
RCE-P0-001 -> COMPLETE
receipt: receipts/rce_p0_001_authoritative_validation.json

RCE-P0-002 -> COMPLETE
receipt: receipts/rce_p0_002_authoritative_validation.json

RCE-P0-003 -> COMPLETE
receipt: receipts/rce_p0_003_authoritative_validation.json

RCE-P0-004 -> COMPLETE
receipt: receipts/rce_p0_004_authoritative_validation.json
decision: ALLOW_CANDIDATE_INTAKE

RCE-P0-005 -> COMPLETE
receipt: receipts/rce_p0_005_authoritative_validation.json
decision: STAGED_CANDIDATE_EVIDENCE

RCE-P0-006 -> COMPLETE
receipt: receipts/rce_p0_006_authoritative_validation.json
decision: CUSTODY_AND_REPLAY_VERIFIED
```

## Active task

```text
RCE-P0-007
owner: core_lite_management_workflow
purpose: sandbox lifecycle, supersession, downgrade prevention, and deterministic archival
status: ACTIVE pending authoritative managed-state receipt
expected receipt: receipts/rce_p0_007_authoritative_validation.json
expected lifecycle state: sandbox/intake/relationship_conditioned_execution/lifecycle_state.json
manual_actions_required: []
```

`RCE-P0-007` maintains exactly one authoritative sandbox candidate. It denies version downgrade, same-version content drift, package-identity change, production permission, autonomous execution authority, human-harm authority, and external destination mutation. A newer version may supersede the active sandbox candidate only after authoritative custody and replay verification; the prior candidate is archived under `sandbox/archive/relationship_conditioned_execution/<version>/`.

## Implemented dependency-gated continuation

```text
RCE-P0-008 -> sandbox expiry, renewal, and quarantine
RCE-P0-009 -> evidence retention and reconstruction index
RCE-P0-010 -> deterministic sandbox snapshot seal
RCE-P0-011 -> isolated sealed-snapshot restoration drill
RCE-P0-012 -> three-way restoration equivalence attestation
RCE-P0-013 -> persistent divergence guard and quarantine evidence
RCE-P0-014 -> local continuity-checkpoint publication candidate
```

These tasks are implemented but cannot become authoritative until each predecessor receipt exists and has the required decision. No downstream task bypasses `RCE-P0-007`.

## Stable autonomous path

`.github/workflows/workstream-status.yml` is the controlling workflow. It runs on relevant repository changes and every five minutes. It performs:

```text
workstream validation
management report generation
RCE reconstruction and candidate-intake decision
sandbox staging
custody and replay verification
lifecycle tests and reconciliation
lease renewal or quarantine
reconstruction indexing
snapshot sealing
isolated restoration drill
restoration equivalence attestation
persistent divergence guarding
report and receipt persistence
task-state transitions
sandbox evidence persistence
fail-closed enforcement after evidence persistence
```

Generated state commits contain `[core-lite-managed-state]` and are excluded from recursive push execution. Scheduled runs remain enabled so suppressed app-authored or workflow-authored push events do not create a manual recovery requirement. The fallback cadence is `*/5 * * * *`, which is the minimum practical GitHub Actions schedule interval.

`RCE-P0-014` also has an independent five-minute scheduled fallback in `.github/workflows/rce-p0-014-checkpoint.yml`.

## Evidence-retention correction

The clean `RCE-P0-013` guard path never deletes a prior quarantine alert. Existing `sandbox/quarantine/relationship_conditioned_execution/divergence_alert.json` evidence is preserved byte-for-byte and referenced by subsequent clean receipts. Later equivalence does not erase historical divergence evidence.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum, reputation, voting, or adaptation cannot authorize human harm
candidate intake and sandbox staging do not grant production authority
no RCE task may mutate an external or production destination
no autonomous harmful execution is permitted
all receipt, hash, path, version, authority, and custody mismatches fail closed
historical quarantine and divergence evidence is never deleted
manual_actions_required remains an empty array
```

## Permitted continuation scope

Continuation may build sandbox lifecycle, expiry, renewal, supersession, custody, replay, deterministic archival, receipts, reports, tests, automatic task-state persistence, evidence indexing, restoration verification, divergence quarantine, and local publication candidates.

Continuation may not perform production installation, external publication, external destination mutation, autonomous execution, human-harm authorization, real-world targeting, weapons enablement, or cyber exploitation.

## Next transition

```text
Core-Lite management workflow executes on the five-minute schedule
-> reports/rce_p0_007_lifecycle.json is persisted
-> receipts/rce_p0_007_authoritative_validation.json is persisted
-> lifecycle_state.json records ACTIVATE_INITIAL_SANDBOX_CANDIDATE, NO_CHANGE_ACTIVE_CANDIDATE, or SUPERSEDE_SANDBOX_CANDIDATE
-> RCE-P0-007 becomes COMPLETE
-> dependency-gated successors execute in order through RCE-P0-013
-> RCE-P0-014 creates a local checkpoint candidate only after the complete authoritative chain exists
```

No user-run command, workflow dispatch, approval, artifact download, receipt copying, task-state edit, external publication, or production mutation is required or authorized.
