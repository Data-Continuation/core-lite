# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.7.3-rce-p0-001-authoritative-workflow-present-pending-run
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
RCE_P0_001_AUTHORITATIVE_WORKFLOW_PRESENT_PENDING_RUN
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
README.md
core_lite/stegverse_002_export_manifest.json
core_lite/tasks/relationship_conditioned_execution.json
schemas/relationship_conditioned_human_decision_policy.schema.json
samples/relationship_conditioned_human_decision_policy.example.json
tools/validate_relationship_conditioned_human_decision_policy.py
tests/test_relationship_conditioned_human_decision_policy.py
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

The repository now contains:

```text
.github/workflows/rce-p0-001-validation.yml
```

Workflow commit:

```text
43a7f25f5a22acdf87793f41b4fb0d3e293fb87d
```

It runs only the two declared validation commands, hashes the five canonical source files, creates `rce-p0-001-validation-receipt.json`, and uploads the following 90-day artifact:

```text
rce-p0-001-validation-receipt
```

The workflow supports `pull_request` and `workflow_dispatch`, uses read-only repository permissions, contains no secret-dependent conditions, and does not activate `RCE-P0-002`.

No pull-request-triggered workflow run was returned for workflow commit `43a7f25f5a22acdf87793f41b4fb0d3e293fb87d` when checked. A direct clone also remains blocked by unavailable DNS resolution for `github.com`.

Required authoritative transition:

```text
RCE P0-001 Validation run succeeds
-> receipt artifact is downloaded and preserved
-> task is marked COMPLETE
-> RCE-P0-002 activates
```

The workstream preserves these boundaries:

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

The previously session-only U.S.-Iran adversarial AI pipeline model is durably preserved at:

```text
docs/ADVERSARIAL_AI_EXECUTION_MODEL.md
```

It records centralized and distributed pipeline archetypes, six execution-boundary breakpoints, the shared commit-time admissibility defect, required StegVerse gates, evidence-discipline rules, and the permitted next fixture scope. It explicitly excludes operational targeting instructions and autonomous-weapons enablement.

## Next build candidate

1. Observe or dispatch `RCE P0-001 Validation`.
2. Download and preserve the `rce-p0-001-validation-receipt` artifact.
3. Verify both command outcomes are `success` and `authoritative_completion_evidence` is `true`.
4. Mark `RCE-P0-001` complete.
5. Activate `RCE-P0-002`: canonical manifest and sandbox fixture package.
6. Use `docs/ADVERSARIAL_AI_EXECUTION_MODEL.md` as a fixture-design input, not as operational targeting guidance.
7. Keep the existing management-package mirroring task independently valid.
