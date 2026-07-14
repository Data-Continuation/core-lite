# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.14.0-rce-p0-009-automated-destination-intake-decision-observation
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
RCE_P0_009_SCHEDULED_DESTINATION_INTAKE_DECISION_OBSERVATION_ACTIVE
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
core_lite/tasks/relationship_conditioned_execution_p0_009.json
config/rce_destination_acknowledgement_watch.json
config/rce_destination_intake_decision_watch.json
tools/observe_rce_destination_acknowledgement.py
tools/observe_rce_destination_intake_decision.py
.github/workflows/rce-p0-004-validation.yml
.github/workflows/rce-p0-005-validation.yml
.github/workflows/rce-p0-006-validation.yml
.github/workflows/rce-p0-007-validation.yml
.github/workflows/rce-p0-008-observation.yml
.github/workflows/rce-p0-009-observation.yml
```

## Completed validation chain

```text
RCE-P0-001 -> COMPLETE
RCE-P0-002 -> COMPLETE
RCE-P0-003 -> COMPLETE
manual_actions_required: []
```

## Automation-owned continuation

### RCE-P0-004 — independent reconstruction

Reconstructs and validates the sandbox-only bundle and emits `ALLOW_CANDIDATE_INTAKE` or `DENY_CANDIDATE_INTAKE`. It performs no destination mutation.

### RCE-P0-005 — repository-local staging

Waits for P0-004 evidence, stages verified candidate evidence inside this repository only, and persists its report, receipt, and state automatically.

### RCE-P0-006 — destination-neutral envelope

Waits for P0-005 and creates a candidate envelope asserting:

```text
candidate_evidence_only: true
may_bind_destination_repo_state: false
destination_mutation_performed: false
```

### RCE-P0-007 — candidate availability notification

Waits for P0-006 and publishes candidate availability while preserving:

```text
destination_receipt_observed: false
destination_acceptance_claimed: false
destination_mutation_performed: false
```

### RCE-P0-008 — destination acknowledgement observation

Checks destination-owned acknowledgement evidence every six hours. Absence remains:

```text
PENDING_DESTINATION_ACKNOWLEDGEMENT
```

Only a valid destination-owned acknowledgement can produce:

```text
DESTINATION_ACKNOWLEDGEMENT_OBSERVED
```

Acknowledgement is receipt for evaluation only. It is not acceptance, installation authority, or execution authority.

### RCE-P0-009 — destination intake-decision observation

Owner:

```text
github_actions:rce-p0-009-destination-intake-decision-observer
```

Installed artifacts:

```text
config/rce_destination_intake_decision_watch.json
tools/observe_rce_destination_intake_decision.py
core_lite/tasks/relationship_conditioned_execution_p0_009.json
.github/workflows/rce-p0-009-observation.yml
```

P0-009 waits for authoritative P0-008 evidence and then checks the destination-owned intake-decision record every six hours.

Possible states:

```text
PENDING_DESTINATION_INTAKE_DECISION
CANDIDATE_UNDER_EVALUATION
CANDIDATE_ACCEPTED_FOR_SANDBOX_INTAKE
CANDIDATE_REJECTED
```

A missing or unreachable destination remains pending. Acknowledgement is not converted into acceptance. Evaluation is not converted into acceptance. Acceptance is not converted into installation or execution authority. Rejection is preserved as a destination-owned decision rather than source-side failure.

An observed decision must prove:

```text
required decision schema
source and destination repository identities
exact notification sha256
exact candidate envelope sha256
exact destination acknowledgement sha256
production_installation_authority: false
autonomous_execution_authority: false
```

P0-009 automatically persists:

```text
reports/rce_p0_009_destination_intake_decision.json
receipts/rce_p0_009_authoritative_validation.json
core_lite/tasks/relationship_conditioned_execution_p0_009.json
```

Terminal outcomes declare P0-010 automatically:

```text
accepted -> RCE-P0-010 accepted sandbox-intake continuity observation
rejected -> RCE-P0-010 rejection remediation observation
```

Generated state commits contain `[rce-p0-009-state]`, preventing recursive workflow loops.

## Intended destination contract

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

No source-side task may claim destination receipt, evaluation, acceptance, rejection, installation, or execution authority without matching destination-owned evidence.

## Manual-task elimination

The chain automatically:

```text
waits for predecessor evidence
resumes when evidence appears
reconstructs validates stages envelopes and notifies
polls for destination acknowledgement and intake decisions
verifies hashes byte counts identities paths authority and receipt chains
persists reports receipts task state and conditional successors
avoids recursive state-commit loops
```

No manual dispatch, approval, artifact download, receipt copying, staging, envelope generation, notification, acknowledgement check, intake-decision check, task edit, or successor declaration remains in the continuation path.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
receipt is not acceptance
evaluation is not acceptance
acceptance is not installation
installation is not execution authority
absence does not permit fabrication
observation does not mutate the destination
no workflow may authorize autonomous harmful execution
all receipt digest identity path authority or state mismatches fail closed
```

## Next continuation

1. P0-004 through P0-007 continue automatically as predecessor evidence appears.
2. P0-008 continues scheduled acknowledgement observation.
3. P0-009 continues scheduled intake-decision observation after acknowledgement.
4. Accepted and rejected terminal states automatically select the appropriate P0-010 observation/remediation path.
5. Destination intake, installation, and execution remain exclusively destination-owned.
