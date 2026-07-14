# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.9.1-rce-p0-004-trusted-main-automation
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
TRUSTED_MAIN_PUSH_AUTOMATION_CONFIGURED
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
receipts/rce_p0_001_authoritative_validation.json
receipts/rce_p0_002_authoritative_validation.json
receipts/rce_p0_003_authoritative_validation.json
reports/rce_automation_status.json
```

## Relationship-conditioned execution state

`RCE-P0-001`, `RCE-P0-002`, and `RCE-P0-003` are complete with authoritative receipts. The previous conversation ZIPs remain historical scaffolding and are not production installation authority.

`RCE-P0-004` independently reconstructs the committed sandbox-only package from canonical source artifacts, compares bytes, validates the `RCE-P0-003` receipt, emits `ALLOW_CANDIDATE_INTAKE` or `DENY_CANDIDATE_INTAKE`, and persists its report, receipt, task state, and successor candidate automatically.

## Manual-task elimination

The automated path performs all of the following without a user-run command:

```text
build or reconstruct canonical artifacts
run validators and focused tests
calculate source and report digests
create authoritative receipts
persist reports and receipts
transition task state
publish automation status
select the next goal candidate
```

`.github/workflows/rce-p0-004-validation.yml` runs on trusted pushes to `main` and on the development branch. Generated state commits contain `[rce-p0-004-state]` so they cannot recursively trigger the same mutation loop.

After repository integration, `github_actions:rce-p0-004-reconstruction-review` owns the full transition. `manual_actions_required` remains an empty array.

## Existing management path

`Data-Continuation/core-lite` remains the StegVerse-001 parallel workstream and ecosystem management verifier. Its existing candidate-evidence destination remains:

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

No RCE task in this handoff authorizes production destination mutation.

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

## Active task

```text
RCE-P0-004
owner: github_actions:rce-p0-004-reconstruction-review
purpose: independent byte reconstruction and automated candidate-intake decision
possible decisions: ALLOW_CANDIDATE_INTAKE | DENY_CANDIDATE_INTAKE
destination_mutation_performed: false
manual_actions_required: []
successor_on_pass: RCE-P0-005 automated sandbox intake staging
```

`ALLOW_CANDIDATE_INTAKE` means candidate evidence may proceed to non-production sandbox staging. It does not authorize production installation, autonomous execution, human harm, operational targeting, weapon enablement, or cyber exploitation.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
ALLOW remains limited to harmless reversible non-severe sandbox actions
candidate intake does not grant production installation authority
no workflow may mutate a production destination or authorize autonomous harmful execution
all integrity path authority or reconstruction mismatches fail closed
```

## Next continuation

1. Trusted `main` push runs `RCE P0-004 Automated Reconstruction Review`.
2. Workflow persists the reconstruction report, authoritative receipt, automation status, and completed task state.
3. On `ALLOW_CANDIDATE_INTAKE`, automation declares `RCE-P0-005` for sandbox-only intake staging.
4. Staging must preserve origin, destination, source-package, reconstruction, and staging receipts.
5. Missing receipts, hash mismatch, path escape, authority expansion, or non-sandbox destination must fail closed.

The existing management-package mirroring workstream remains independently valid.
