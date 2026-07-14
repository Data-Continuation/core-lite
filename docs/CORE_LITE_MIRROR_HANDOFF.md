# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.7.1-rce-p0-001-implemented-pending-ci
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
RELATIONSHIP_CONDITIONED_EXECUTION_TASK_IMPLEMENTED_PENDING_CI
DRAFT_PR_2_OPEN
LOCAL_AND_CI
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md
README.md
core_lite/stegverse_002_export_manifest.json
core_lite/tasks/relationship_conditioned_execution.json
schemas/relationship_conditioned_human_decision_policy.schema.json
samples/relationship_conditioned_human_decision_policy.example.json
tools/validate_relationship_conditioned_human_decision_policy.py
tests/test_relationship_conditioned_human_decision_policy.py
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

`RCE-P0-001` now includes:

```text
docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md
schemas/relationship_conditioned_human_decision_policy.schema.json
samples/relationship_conditioned_human_decision_policy.example.json
tools/validate_relationship_conditioned_human_decision_policy.py
tests/test_relationship_conditioned_human_decision_policy.py
```

Its current state is `IMPLEMENTED_PENDING_CI` on draft PR #2. The required validation commands are:

```text
python tools/validate_relationship_conditioned_human_decision_policy.py
python -m pytest -q tests/test_relationship_conditioned_human_decision_policy.py
```

No pull-request-triggered workflow run was found for the current head. A direct local clone was also blocked by the execution environment's unavailable network resolution. These facts are preserved as validation blockers rather than represented as passing evidence.

The workstream preserves these boundaries:

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
adaptive policy changes require bounded review authority
unknown authority fails closed, abstains, or escalates
```

## Next build candidate

1. Obtain and preserve the authoritative `RCE-P0-001` validation receipt.
2. If both commands pass, mark `RCE-P0-001` complete.
3. Activate `RCE-P0-002`: canonical manifest and sandbox fixture package.
4. Keep the existing management-package mirroring task independently valid.
