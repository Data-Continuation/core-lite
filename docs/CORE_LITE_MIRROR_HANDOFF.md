# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.10.0-rce-p0-007-lifecycle-active
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

## Stable autonomous path

`.github/workflows/workstream-status.yml` is the controlling workflow. It runs on relevant repository changes and hourly reconciliation. It performs:

```text
workstream validation
management report generation
RCE reconstruction and candidate-intake decision
sandbox staging
custody and replay verification
lifecycle tests
lifecycle reconciliation
report and receipt persistence
task-state transitions
sandbox evidence persistence
fail-closed enforcement after evidence persistence
```

Generated state commits contain `[core-lite-managed-state]` and are excluded from recursive push execution. Scheduled runs remain enabled so suppressed app-authored or workflow-authored push events do not create a manual recovery requirement.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum, reputation, voting, or adaptation cannot authorize human harm
candidate intake and sandbox staging do not grant production authority
no RCE task may mutate an external or production destination
no autonomous harmful execution is permitted
all receipt, hash, path, version, authority, and custody mismatches fail closed
manual_actions_required remains an empty array
```

## Permitted continuation scope

Continuation may build sandbox lifecycle, expiry, renewal, supersession, custody, replay, deterministic archival, receipts, reports, tests, and automatic task-state persistence.

Continuation may not perform production installation, external destination mutation, autonomous execution, human-harm authorization, real-world targeting, weapons enablement, or cyber exploitation.

## Next transition

```text
Core-Lite management workflow executes lifecycle tests and reconciler
-> reports/rce_p0_007_lifecycle.json is persisted
-> receipts/rce_p0_007_authoritative_validation.json is persisted
-> lifecycle_state.json records ACTIVATE_INITIAL_SANDBOX_CANDIDATE, NO_CHANGE_ACTIVE_CANDIDATE, or SUPERSEDE_SANDBOX_CANDIDATE
-> RCE-P0-007 becomes COMPLETE
-> RCE-P0-008 sandbox expiry and renewal automation becomes the successor
```

No user-run command, workflow dispatch, approval, artifact download, receipt copying, or task-state edit is required.
