# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.11.0-rce-p0-006-automated-candidate-envelope
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
receipts/rce_p0_001_authoritative_validation.json
receipts/rce_p0_002_authoritative_validation.json
receipts/rce_p0_003_authoritative_validation.json
.github/workflows/rce-p0-004-validation.yml
.github/workflows/rce-p0-005-validation.yml
.github/workflows/rce-p0-006-validation.yml
```

## Completed validation chain

```text
RCE-P0-001 -> COMPLETE
RCE-P0-002 -> COMPLETE
RCE-P0-003 -> COMPLETE
manual_actions_required: []
```

## Automated continuation chain

### RCE-P0-004

Independently reconstructs the committed sandbox-only bundle, verifies the P0-003 receipt, compares deterministic bytes, and emits:

```text
ALLOW_CANDIDATE_INTAKE | DENY_CANDIDATE_INTAKE
```

It performs no destination mutation and automatically persists its report, receipt, task state, and successor evidence.

### RCE-P0-005

Waits automatically for P0-004 evidence. On `ALLOW_CANDIDATE_INTAKE`, it verifies the full receipt and integrity chain, copies candidate evidence only into repository-local sandbox staging, verifies every staged copy, and automatically persists:

```text
staging/relationship_conditioned_execution/staging_manifest.json
reports/rce_p0_005_staging.json
receipts/rce_p0_005_authoritative_validation.json
```

It performs no external or production destination mutation.

### RCE-P0-006

Owner:

```text
github_actions:rce-p0-006-candidate-envelope
```

Installed artifacts:

```text
core_lite/tasks/relationship_conditioned_execution_p0_006.json
tools/build_rce_candidate_intake_envelope.py
tests/test_build_rce_candidate_intake_envelope.py
.github/workflows/rce-p0-006-validation.yml
```

P0-006 waits automatically until the P0-005 authoritative receipt and staging manifest exist. It then:

```text
verifies P0-005 authoritative completion
verifies staged candidate-evidence authority boundaries
verifies every staged file hash and byte count
creates a deterministic destination-neutral candidate envelope
names the intended StegVerse-002 intake policy and incoming path
asserts candidate_evidence_only=true
asserts may_bind_destination_repo_state=false
asserts destination_mutation_performed=false
persists envelope report receipt and task transition automatically
declares RCE-P0-007 automatically
```

Expected durable outputs:

```text
exports/relationship_conditioned_execution/candidate_envelope.json
reports/rce_p0_006_candidate_envelope.json
receipts/rce_p0_006_authoritative_validation.json
core_lite/tasks/relationship_conditioned_execution_p0_007.json
```

Generated state commits contain `[rce-p0-006-state]`, preventing recursive workflow loops.

## Existing management intake contract

The intended destination remains:

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

The P0-006 envelope is destination-neutral candidate evidence. It does not claim destination acceptance, bind destination state, install into production, or mutate `StegVerse-002/core-lite`.

## Manual-task elimination

The automation-owned chain performs without user-run commands:

```text
wait for predecessor evidence
resume when predecessor evidence appears
reconstruct validate stage and envelope candidate artifacts
verify hashes byte counts paths authority and receipt chains
persist reports receipts task state and successor declarations
avoid recursive state-commit loops
```

No manual dispatch, workflow approval, artifact download, receipt copying, staging command, envelope command, task-state edit, or successor declaration is part of the continuation path.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
candidate evidence does not grant destination acceptance or installation authority
repository-local staging does not grant external mutation authority
destination-neutral envelope does not bind destination repository state
no workflow may authorize autonomous harmful execution
all missing receipt hash path authority reconstruction staging or envelope mismatches fail closed
```

## Next continuation

1. P0-004 automatically persists reconstruction evidence.
2. P0-005 automatically stages candidate evidence locally.
3. P0-006 automatically creates and persists the destination-neutral candidate envelope.
4. P0-006 automatically declares `RCE-P0-007`.
5. P0-007 may publish a destination-observable notification through the existing management evidence surface, but may not mutate the destination or claim acceptance.
6. Any destination intake or installation must be separately derived and executed by destination-owned policy and authority.

The existing management-package mirroring workstream remains independently valid.
