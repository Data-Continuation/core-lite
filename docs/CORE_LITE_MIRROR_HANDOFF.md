# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.12.0-rce-p0-007-automated-candidate-notification
```

## Current status

```text
MIRROR_HANDOFF_PRESENT
RCE_P0_001_COMPLETE
RCE_P0_002_COMPLETE
RCE_P0_003_COMPLETE
RCE_P0_004_AUTOMATED_RECONSTRUCTION_ACTIVE
RCE_P0_005_DEPENDENCY_AWARE_AUTOMATED_STAGING_ACTIVE
RCE_P0_006_DEPENDENCY_AWARE_AUTOMATED_ENVELOPE_ACTIVE
RCE_P0_007_DEPENDENCY_AWARE_AUTOMATED_NOTIFICATION_ACTIVE
MANUAL_ACTIONS_REQUIRED_NONE
DESTINATION_MUTATION_AUTHORITY_NONE
LOCAL_AND_CI
```

## Source-of-truth records

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md
docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md
docs/ADVERSARIAL_AI_EXECUTION_MODEL.md
core_lite/tasks/relationship_conditioned_execution.json
core_lite/tasks/relationship_conditioned_execution_p0_002.json
core_lite/tasks/relationship_conditioned_execution_p0_003.json
core_lite/tasks/relationship_conditioned_execution_p0_004.json
core_lite/tasks/relationship_conditioned_execution_p0_005.json
core_lite/tasks/relationship_conditioned_execution_p0_006.json
core_lite/tasks/relationship_conditioned_execution_p0_007.json
receipts/rce_p0_001_authoritative_validation.json
receipts/rce_p0_002_authoritative_validation.json
receipts/rce_p0_003_authoritative_validation.json
.github/workflows/rce-p0-004-validation.yml
.github/workflows/rce-p0-005-validation.yml
.github/workflows/rce-p0-006-validation.yml
.github/workflows/rce-p0-007-validation.yml
```

## Completed validation chain

```text
RCE-P0-001 -> COMPLETE
RCE-P0-002 -> COMPLETE
RCE-P0-003 -> COMPLETE
manual_actions_required: []
```

## Automated continuation chain

### RCE-P0-004 — independent reconstruction

Independently reconstructs the committed sandbox-only bundle, verifies the P0-003 receipt, compares deterministic bytes, and emits:

```text
ALLOW_CANDIDATE_INTAKE | DENY_CANDIDATE_INTAKE
```

It performs no destination mutation and persists its report, receipt, task state, and successor evidence automatically.

### RCE-P0-005 — repository-local sandbox staging

Waits for P0-004 evidence. On `ALLOW_CANDIDATE_INTAKE`, it verifies the receipt and integrity chain, copies candidate evidence into repository-local sandbox staging, verifies each staged copy, and persists:

```text
staging/relationship_conditioned_execution/staging_manifest.json
reports/rce_p0_005_staging.json
receipts/rce_p0_005_authoritative_validation.json
```

It performs no external or production destination mutation.

### RCE-P0-006 — destination-neutral candidate envelope

Waits for P0-005 authoritative evidence and then verifies staged hashes, byte counts, paths, and authority boundaries before creating:

```text
exports/relationship_conditioned_execution/candidate_envelope.json
reports/rce_p0_006_candidate_envelope.json
receipts/rce_p0_006_authoritative_validation.json
```

The envelope names the intended destination intake contract but asserts:

```text
candidate_evidence_only: true
may_bind_destination_repo_state: false
destination_mutation_performed: false
```

### RCE-P0-007 — destination-observable candidate notification

Owner:

```text
github_actions:rce-p0-007-candidate-notification
```

Installed artifacts:

```text
core_lite/tasks/relationship_conditioned_execution_p0_007.json
tools/publish_rce_candidate_notification.py
tests/test_publish_rce_candidate_notification.py
.github/workflows/rce-p0-007-validation.yml
```

P0-007 waits automatically for the P0-006 receipt and candidate envelope. It then:

```text
verifies P0-006 authoritative completion
verifies candidate-envelope digest and authority boundaries
publishes a repository-visible availability notification
asserts destination_receipt_observed=false
asserts destination_acceptance_claimed=false
asserts destination_mutation_performed=false
persists notification report receipt and task state automatically
declares RCE-P0-008 automatically
```

Expected durable outputs:

```text
notifications/relationship_conditioned_execution/candidate_available.json
reports/rce_p0_007_candidate_notification.json
receipts/rce_p0_007_authoritative_validation.json
core_lite/tasks/relationship_conditioned_execution_p0_008.json
```

Generated state commits contain `[rce-p0-007-state]`, preventing recursive workflow loops.

## Existing management intake contract

The intended destination remains:

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

The candidate envelope and notification are destination-neutral evidence. They do not claim destination receipt, acceptance, installation, or authority to bind or mutate `StegVerse-002/core-lite`.

## Manual-task elimination

The automation-owned chain performs without user-run commands:

```text
wait for predecessor evidence
resume when predecessor evidence appears
reconstruct validate stage envelope and notify
verify hashes byte counts paths authority and receipt chains
persist reports receipts task state and successor declarations
avoid recursive state-commit loops
```

No manual dispatch, workflow approval, artifact download, receipt copying, staging command, envelope command, notification command, task-state edit, or successor declaration is part of the continuation path.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
candidate evidence does not grant destination acceptance or installation authority
repository-local staging does not grant external mutation authority
destination-neutral envelope does not bind destination repository state
notification does not prove destination receipt or acceptance
no workflow may authorize autonomous harmful execution
all missing receipt hash path authority reconstruction staging envelope or notification mismatches fail closed
```

## Next continuation

1. P0-004 automatically persists reconstruction evidence.
2. P0-005 automatically stages candidate evidence locally.
3. P0-006 automatically creates the destination-neutral candidate envelope.
4. P0-007 automatically publishes candidate availability without claiming destination receipt.
5. P0-007 automatically declares `RCE-P0-008`.
6. P0-008 may observe a destination-owned acknowledgement when one becomes durably available, but absence must remain `PENDING_DESTINATION_ACKNOWLEDGEMENT` and no receipt or acceptance may be fabricated.
7. Any destination intake or installation must be separately derived and executed by destination-owned policy and authority.

The existing management-package mirroring workstream remains independently valid.
