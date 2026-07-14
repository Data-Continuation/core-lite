# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.10.0-rce-p0-005-automated-sandbox-staging
```

## Current status

```text
MIRROR_HANDOFF_PRESENT
STEGCLAW_TARGET_INTAKE_DECLARED
STEGCLAW_TARGET_INTAKE_VALIDATOR_PRESENT
STEGCLAW_TARGET_INTAKE_WORKFLOW_COVERED
ECOSYSTEM_MAINTAINER_SCAN_PRESENT
AUTO_FIX_ELIGIBILITY_PRESENT
FRICTION_AVOIDED_METRIC_PRESENT
BUNDLE_REGISTRY_PRESENT
CAPABILITY_GAP_PLAN_PRESENT
STEGVERSE_002_EXPORT_MANIFEST_PRESENT
STEGVERSE_002_EXPORT_VALIDATOR_PRESENT
STEGVERSE_002_EXPORT_WORKFLOW_COVERED
MANAGEMENT_REPORTS_PUBLISHED_TO_REPOSITORY
ECOSYSTEM_MANAGEMENT_WORKFLOW_COVERED
RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF_PRESENT
RCE_P0_001_COMPLETE
RCE_P0_002_COMPLETE
RCE_P0_003_COMPLETE
RCE_P0_004_AUTOMATED_RECONSTRUCTION_ACTIVE
RCE_P0_005_DEPENDENCY_AWARE_AUTOMATED_STAGING_ACTIVE
MANUAL_ACTIONS_REQUIRED_NONE
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
receipts/rce_p0_001_authoritative_validation.json
receipts/rce_p0_002_authoritative_validation.json
receipts/rce_p0_003_authoritative_validation.json
reports/rce_automation_status.json
.github/workflows/rce-p0-004-validation.yml
.github/workflows/rce-p0-005-validation.yml
```

## Completed validation chain

```text
RCE-P0-001 -> COMPLETE
receipt: receipts/rce_p0_001_authoritative_validation.json

RCE-P0-002 -> COMPLETE
receipt: receipts/rce_p0_002_authoritative_validation.json

RCE-P0-003 -> COMPLETE
receipt: receipts/rce_p0_003_authoritative_validation.json
manual_actions_required: []
```

## RCE-P0-004 — automated reconstruction review

Owner:

```text
github_actions:rce-p0-004-reconstruction-review
```

The workflow independently reconstructs the committed sandbox-only package, compares committed bytes, validates the P0-003 authoritative receipt, and emits one of:

```text
ALLOW_CANDIDATE_INTAKE
DENY_CANDIDATE_INTAKE
```

It persists its report, authoritative receipt, task state, automation status, and successor declaration automatically. It performs no destination mutation.

Required outputs when complete:

```text
reports/rce_p0_004_reconstruction.json
receipts/rce_p0_004_authoritative_validation.json
```

## RCE-P0-005 — dependency-aware automated sandbox staging

Owner:

```text
github_actions:rce-p0-005-sandbox-staging
```

Installed artifacts:

```text
core_lite/tasks/relationship_conditioned_execution_p0_005.json
tools/stage_relationship_conditioned_execution_candidate.py
tests/test_stage_relationship_conditioned_execution_candidate.py
.github/workflows/rce-p0-005-validation.yml
```

The P0-005 workflow runs on both `main` and `stegops/rce-handoff-clean`. It detects whether the P0-004 report and authoritative receipt exist.

```text
if P0-004 evidence is absent:
  exit successfully in automatic waiting state

if P0-004 evidence exists and decision is ALLOW_CANDIDATE_INTAKE:
  verify P0-003 and P0-004 authoritative receipts
  verify bundle manifest inventory and install plan
  verify every source hash and byte count
  copy candidate evidence only into repository-local sandbox staging
  verify every staged copy
  persist staging manifest report receipt and task transition
  declare RCE-P0-006 automatically
```

P0-005 generated-state commits contain:

```text
[rce-p0-005-state]
```

This prevents recursive workflow mutation loops.

Expected durable outputs:

```text
staging/relationship_conditioned_execution/staging_manifest.json
reports/rce_p0_005_staging.json
receipts/rce_p0_005_authoritative_validation.json
core_lite/tasks/relationship_conditioned_execution_p0_006.json
```

## Manual-task elimination

The automated chain performs all of the following without user-run commands:

```text
wait for predecessor evidence
resume when predecessor evidence is committed
reconstruct or stage canonical artifacts
run validators and focused tests
calculate source report and staging digests
verify complete receipt chains
create authoritative receipts
persist reports receipts and task state
select and declare the next goal
avoid recursive workflow loops
```

No manual workflow dispatch, approval, artifact download, receipt copying, task-state edit, staging command, or successor declaration is part of the continuation path.

## Existing management path

`Data-Continuation/core-lite` remains the StegVerse-001 parallel workstream and ecosystem management verifier. Its existing candidate-evidence destination remains:

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

Neither P0-004 nor P0-005 mutates that destination. P0-005 only stages evidence inside this repository.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
ALLOW remains limited to harmless reversible non-severe sandbox actions
candidate intake does not grant production installation authority
repository-local staging does not grant external mutation authority
no workflow may authorize autonomous harmful execution
all missing receipt hash path authority or reconstruction mismatches fail closed
```

## Next continuation

1. P0-004 automatically persists its report and authoritative receipt.
2. The P0-004 state commit automatically triggers P0-005.
3. P0-005 waits or stages deterministically without human intervention.
4. Successful P0-005 staging automatically declares `RCE-P0-006`.
5. P0-006 may create a candidate envelope for the existing management intake path, but must not mutate the destination repository unless destination-owned policy and authority are separately proven.

The existing management-package mirroring workstream remains independently valid.
