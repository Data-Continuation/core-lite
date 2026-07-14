# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.7.4-rce-p0-001-action-required-p0-002-prepared
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
RELATIONSHIP_CONDITIONED_EXECUTION_TASK_INDEPENDENTLY_VALIDATED
RCE_P0_001_AUTHORITATIVE_WORKFLOW_ACTION_REQUIRED
RCE_P0_002_PACKAGE_PREPARED_NOT_ACTIVATED
ADVERSARIAL_AI_EXECUTION_MODEL_PRESENT
DRAFT_PR_2_OPEN
LOCAL_AND_CI
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md
docs/ADVERSARIAL_AI_EXECUTION_MODEL.md
docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md
README.md
core_lite/stegverse_002_export_manifest.json
core_lite/tasks/relationship_conditioned_execution.json
core_lite/tasks/relationship_conditioned_execution_p0_002.json
schemas/relationship_conditioned_human_decision_policy.schema.json
schemas/execution_candidate_manifest.schema.json
samples/relationship_conditioned_human_decision_policy.example.json
samples/execution_candidate_manifest.allow.example.json
samples/execution_candidate_manifest.stale_state.example.json
samples/execution_candidate_manifest.scope_leakage.example.json
tools/validate_relationship_conditioned_human_decision_policy.py
tools/validate_execution_candidate_manifest.py
tests/test_relationship_conditioned_human_decision_policy.py
tests/test_execution_candidate_manifest.py
.github/workflows/rce-p0-001-validation.yml
receipts/rce_p0_001_connector_rehydrated_validation.json
```

## Current activation goal

`Data-Continuation/core-lite` is the StegVerse-001 parallel workstream and ecosystem management verifier. It generates and commits the management report package required by `StegVerse-002/core-lite` management package intake.

The stable workflow:

```text
1. Generates management reports and receipts.
2. Commits reports/ and receipts/ to the default branch when changed.
3. Uploads the same package as workflow artifact core-lite-workstream-status.
```

This removes the previous dependency on manual artifact download for 002 intake.

## Published package paths

```text
reports/ecosystem_maintainer_scan.json
reports/auto_fix_eligibility.json
reports/friction_avoided.json
reports/bundle_registry.json
reports/capability_gap_plan.json
reports/stegverse_002_export_manifest.json
receipts/ecosystem_maintainer_receipts.jsonl
receipts/auto_fix_eligibility_receipts.jsonl
receipts/friction_avoided_receipts.jsonl
receipts/bundle_registry_receipts.jsonl
receipts/capability_gap_receipts.jsonl
receipts/stegverse_002_export_receipts.jsonl
```

## Destination intake

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

Expected destination transition:

```text
MANAGEMENT_PACKAGE_CANDIDATE_EVIDENCE_ACCEPTED
```

## Relationship-conditioned execution workstream

The AI-human relationship discussion and v1.0-v2.2 artifact lineage are durably preserved in:

```text
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
core_lite/tasks/relationship_conditioned_execution.json
```

The prior ZIPs are unvalidated scaffolding and must not be ingested as production releases.

`RCE-P0-001` includes:

```text
docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md
schemas/relationship_conditioned_human_decision_policy.schema.json
samples/relationship_conditioned_human_decision_policy.example.json
tools/validate_relationship_conditioned_human_decision_policy.py
tests/test_relationship_conditioned_human_decision_policy.py
.github/workflows/rce-p0-001-validation.yml
```

The exact fetched branch artifacts passed independent connector-rehydrated validation on 2026-07-13:

```text
python tools/validate_relationship_conditioned_human_decision_policy.py
RELATIONSHIP_CONDITIONED_POLICY_VALID

python -m pytest -q tests/test_relationship_conditioned_human_decision_policy.py
16 passed in 2.07s
```

Evidence is preserved in:

```text
receipts/rce_p0_001_connector_rehydrated_validation.json
```

This is independent validation evidence, not the authoritative CI or direct-checkout receipt required to close `RCE-P0-001`.

## Authoritative validation workflow

The repository contains:

```text
.github/workflows/rce-p0-001-validation.yml
```

It runs only the two declared validation commands, hashes the five canonical source files, creates `rce-p0-001-validation-receipt.json`, and uploads the 90-day artifact:

```text
rce-p0-001-validation-receipt
```

The workflow supports `pull_request` and `workflow_dispatch`, uses read-only repository permissions, contains no secret-dependent conditions, and does not activate `RCE-P0-002`.

Observed authoritative run state:

```text
run_id: 29306690630
run_number: 5
commit: 109ab9890ed3e3a4e2230d3b1b6925072b7cb1c3
status: completed
conclusion: action_required
jobs_created: 0
```

Because no job was created, this is an approval or dispatch gate rather than validator failure evidence.

Required authoritative transition:

```text
repository maintainer approves or manually dispatches RCE P0-001 Validation
-> validation job executes
-> receipt artifact is downloaded and preserved
-> authoritative_completion_evidence == true is verified
-> RCE-P0-001 is marked COMPLETE
-> RCE-P0-002 activates
```

## RCE-P0-002 prepared package

`RCE-P0-002` is materially prepared but remains dormant:

```text
status: PREPARED_NOT_ACTIVATED
activation_allowed: false
activation_dependency: RCE-P0-001 COMPLETE with authoritative receipt
```

Prepared files:

```text
docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md
core_lite/tasks/relationship_conditioned_execution_p0_002.json
schemas/execution_candidate_manifest.schema.json
samples/execution_candidate_manifest.allow.example.json
samples/execution_candidate_manifest.stale_state.example.json
samples/execution_candidate_manifest.scope_leakage.example.json
tools/validate_execution_candidate_manifest.py
tests/test_execution_candidate_manifest.py
```

The validator deterministically derives `ALLOW`, `DENY`, `ABSTAIN`, or `ESCALATE`. `ALLOW` is limited to reversible, non-severe, harmless sandbox actions with fresh sufficient state, valid commit-time authority, contained effects, resolved collateral, reachable denial, preserved governability, preserved recoverability, and integrity-protected traceability.

Prepared fixtures:

```text
allow.example: reversible non-sensitive report publication -> ALLOW
stale_state.example: evidence older than declared maximum -> DENY
scope_leakage.example: predicted effect outside authorized domains -> DENY
```

The package excludes real-world targets, targeting logic, weapons enablement, strike routing, evasion, cyber exploitation, and autonomous harmful execution.

## Preserved boundaries

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
adaptive policy changes require bounded review authority
unknown authority fails closed, abstains, or escalates
commit-time admissibility must be re-derived from live state
denial must remain meaningfully reachable
authority scope must contain cross-domain effects
```

## Adversarial execution-boundary model

The U.S.-Iran adversarial AI pipeline model is durably preserved at:

```text
docs/ADVERSARIAL_AI_EXECUTION_MODEL.md
```

It records centralized and distributed pipeline archetypes, six execution-boundary breakpoints, the shared commit-time admissibility defect, required StegVerse gates, evidence-discipline rules, and the permitted next fixture scope. It explicitly excludes operational targeting instructions and autonomous-weapons enablement.

## Next build sequence

1. Approve or manually dispatch `RCE P0-001 Validation`.
2. Observe the resulting workflow run and inspect its jobs.
3. Download and preserve `rce-p0-001-validation-receipt`.
4. Verify both command outcomes are `success` and `authoritative_completion_evidence` is `true`.
5. Mark `RCE-P0-001` complete.
6. Change `RCE-P0-002` from `PREPARED_NOT_ACTIVATED` to `ACTIVE`.
7. Execute the prepared RCE-P0-002 validator and tests and preserve their receipt.
8. Keep the existing management-package mirroring task independently valid.
