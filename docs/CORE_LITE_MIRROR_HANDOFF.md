# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.13.0-rce-p0-008-automated-destination-acknowledgement-observation
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
RCE_P0_008_SCHEDULED_DESTINATION_ACKNOWLEDGEMENT_OBSERVATION_ACTIVE
MANUAL_ACTIONS_REQUIRED_NONE
DESTINATION_MUTATION_AUTHORITY_NONE
```

## Authoritative records

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
core_lite/tasks/relationship_conditioned_execution_p0_008.json
config/rce_destination_acknowledgement_watch.json
tools/observe_rce_destination_acknowledgement.py
.github/workflows/rce-p0-004-validation.yml
.github/workflows/rce-p0-005-validation.yml
.github/workflows/rce-p0-006-validation.yml
.github/workflows/rce-p0-007-validation.yml
.github/workflows/rce-p0-008-observation.yml
```

## Completed validation chain

```text
RCE-P0-001 -> COMPLETE
RCE-P0-002 -> COMPLETE
RCE-P0-003 -> COMPLETE
manual_actions_required: []
```

## Automation-owned continuation

### RCE-P0-004

Independently reconstructs the sandbox-only bundle and emits `ALLOW_CANDIDATE_INTAKE` or `DENY_CANDIDATE_INTAKE`. It performs no destination mutation.

### RCE-P0-005

Waits for P0-004 evidence, stages validated candidate evidence inside this repository only, verifies every copied byte, and commits its report, receipt, and task state automatically.

### RCE-P0-006

Waits for P0-005, creates a destination-neutral candidate envelope, names the intended StegVerse-002 intake contract, and asserts:

```text
candidate_evidence_only: true
may_bind_destination_repo_state: false
destination_mutation_performed: false
```

### RCE-P0-007

Waits for P0-006 and publishes repository-visible candidate availability while explicitly preserving:

```text
destination_receipt_observed: false
destination_acceptance_claimed: false
destination_mutation_performed: false
```

### RCE-P0-008

Owner:

```text
github_actions:rce-p0-008-destination-acknowledgement-observer
```

Installed artifacts:

```text
config/rce_destination_acknowledgement_watch.json
tools/observe_rce_destination_acknowledgement.py
core_lite/tasks/relationship_conditioned_execution_p0_008.json
.github/workflows/rce-p0-008-observation.yml
```

P0-008 waits automatically for P0-007 evidence and then checks the destination-owned acknowledgement URL every six hours. It uses no secret and performs no destination mutation.

Possible states:

```text
PENDING_DESTINATION_ACKNOWLEDGEMENT
DESTINATION_ACKNOWLEDGEMENT_OBSERVED
```

A missing or unreachable destination remains pending. It is not converted into a failure, receipt, acceptance, or fabricated acknowledgement.

An observed acknowledgement must prove all of the following:

```text
required acknowledgement schema
authoritative source and destination repository identities
candidate state CANDIDATE_RECEIVED_FOR_EVALUATION
exact source notification sha256
exact candidate envelope sha256
destination_acceptance: false
production_installation_authority: false
autonomous_execution_authority: false
```

P0-008 automatically persists:

```text
reports/rce_p0_008_destination_acknowledgement.json
receipts/rce_p0_008_authoritative_validation.json
core_lite/tasks/relationship_conditioned_execution_p0_008.json
```

Only a valid destination-owned acknowledgement can mark P0-008 complete and declare `RCE-P0-009`. Pending observations require no manual action and continue on schedule.

Generated state commits contain `[rce-p0-008-state]`, preventing recursive workflow loops.

## Intended destination contract

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

No source-side task may claim destination receipt, acceptance, intake, installation, or authority merely because candidate evidence was published.

## Manual-task elimination

The chain automatically:

```text
waits for predecessor evidence
resumes when evidence appears
reconstructs validates stages envelopes and notifies
polls for destination-owned acknowledgement
verifies hashes byte counts identities paths authority and receipt chains
persists reports receipts task state and conditional successors
avoids recursive state-commit loops
```

No manual dispatch, workflow approval, artifact download, receipt copying, staging command, envelope command, notification command, acknowledgement check, task edit, or successor declaration remains in the continuation path.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
candidate evidence does not grant destination acceptance or installation authority
notification does not prove destination receipt
absence does not permit acknowledgement fabrication
observation does not imply acceptance
no workflow may mutate the destination or authorize autonomous harmful execution
all receipt digest identity path authority or state mismatches fail closed
```

## Next continuation

1. P0-004 through P0-007 continue automatically as predecessor evidence becomes available.
2. P0-008 records pending state and checks the destination-owned acknowledgement every six hours.
3. A valid acknowledgement automatically completes P0-008 and declares `RCE-P0-009` for destination-owned intake-decision observation.
4. P0-009 must preserve the distinction between receipt, evaluation, acceptance, rejection, installation, and execution authority.
5. Any destination intake or installation remains exclusively destination-owned.
