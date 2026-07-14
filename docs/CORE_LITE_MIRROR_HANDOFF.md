# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.7.0-relationship-conditioned-execution-handoff
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
RELATIONSHIP_CONDITIONED_EXECUTION_TASK_DECLARED
LOCAL_AND_CI
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
README.md
core_lite/stegverse_002_export_manifest.json
core_lite/tasks/relationship_conditioned_execution.json
```

## Current managed files

```text
core_lite/workstreams.yml
core_lite/transition_blocks.yml
core_lite/stegclaw_target_intake.json
core_lite/bundle_registry.yml
core_lite/stegverse_002_export_manifest.json
core_lite/tasks/relationship_conditioned_execution.json
tools/validate_workstreams.py
tools/validate_stegclaw_intake.py
tools/ecosystem_maintainer.py
tools/auto_fix_eligibility.py
tools/measure_friction.py
tools/bundle_registry_report.py
tools/capability_gap_plan.py
tools/validate_stegverse_002_export.py
docs/STEGCLAW_TARGET_INTAKE.md
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
github/workflows/workstream-status.yml
```

Path note: `github/workflows/workstream-status.yml` is displayed without the leading dot. The actual path is `.github/workflows/workstream-status.yml`.

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

The AI-human relationship discussion and v1.0-v2.2 artifact lineage are now durably preserved in:

```text
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
core_lite/tasks/relationship_conditioned_execution.json
```

The previous ZIPs are explicitly classified as unvalidated scaffolding and must not be ingested as production releases. The active task is `RCE-P0-001`: define the normative relationship-conditioned human-decision policy, schema, example, and tests.

The workstream must preserve these boundaries:

```text
relationship history provides context but does not create authority
uncertainty acknowledgment does not authorize irreversible harm
AI quorum or reputation cannot authorize human harm
adaptive policy changes require bounded review authority
unknown authority fails closed, abstains, or escalates
```

## Next build candidate

Build `RCE-P0-001` outputs, validate them locally and in CI, then prepare `RCE-P0-002` as a canonical manifest and sandbox fixture package. The existing management-package mirroring task remains independently valid and may proceed without requiring this conversation.
