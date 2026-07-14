# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.9.0-rce-p0-004-automated-reconstruction-active
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

## Existing management path

`Data-Continuation/core-lite` remains the StegVerse-001 parallel workstream and ecosystem management verifier. Its existing candidate-evidence destination remains:

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

Expected destination transition:

```text
MANAGEMENT_PACKAGE_CANDIDATE_EVIDENCE_ACCEPTED
```

No relationship-conditioned execution task in this handoff authorizes production mutation.

## RCE-P0-001 — COMPLETE

Purpose: define the normative relationship-conditioned human-decision policy and machine-readable boundary record.

```text
workflow run: 29308124165
authoritative_completion_evidence: true
receipt: receipts/rce_p0_001_authoritative_validation.json
```

Core boundaries:

```text
relationship history provides context but does not create authority
uncertainty acknowledgment is not execution authorization
present consent does not bind an uncertain future self
AI quorum, reputation, voting, or adaptive thresholds cannot authorize human harm
irreversible severe human impact cannot receive autonomous ALLOW
unknown, expired, revoked, conflicting, or out-of-scope authority fails closed
```

## RCE-P0-002 — COMPLETE

Purpose: define a deterministic, non-operational execution-candidate manifest and harmless sandbox fixtures.

```text
workflow run: 29308190352
authoritative_completion_evidence: true
receipt: receipts/rce_p0_002_authoritative_validation.json
```

Validated fixture decisions:

```text
bounded reversible sandbox report publication -> ALLOW
stale state -> DENY
cross-domain scope leakage -> DENY
```

## RCE-P0-003 — COMPLETE

Purpose: package validated RCE artifacts as a deterministic sandbox-only ingestion candidate.

```text
workflow: .github/workflows/rce-p0-003-validation.yml
workflow run: 29308626043
authoritative_completion_evidence: true
receipt: receipts/rce_p0_003_authoritative_validation.json
manual_actions_required: []
```

Durable package:

```text
bundles/relationship_conditioned_execution/bundle_manifest.json
bundles/relationship_conditioned_execution/install_plan.json
bundles/relationship_conditioned_execution/source_inventory.json
```

Validated properties:

```text
per-file sha256 digests and byte counts
explicit source and sandbox target paths
policy and schemas ordered before validators and fixtures
candidate_evidence_only: true
autonomous_execution_authority: false
human_harm_authority: false
production_destination_allowed: false
fail closed on missing file, hash mismatch, size mismatch, path traversal, production target, or execution authority
```

## RCE-P0-004 — AUTOMATED RECONSTRUCTION ACTIVE

Purpose: independently reconstruct the committed package from canonical source files and issue an automated sandbox candidate-intake decision.

Implemented records:

```text
tools/reconstruct_relationship_conditioned_execution_bundle.py
tests/test_reconstruct_relationship_conditioned_execution_bundle.py
.github/workflows/rce-p0-004-validation.yml
core_lite/tasks/relationship_conditioned_execution_p0_004.json
```

The reconstruction implementation does not import the bundle builder. It compares independently reconstructed manifest, inventory, and install-plan bytes against the committed package and validates the authoritative `RCE-P0-003` receipt.

Automatic outputs:

```text
reports/rce_p0_004_reconstruction.json
receipts/rce_p0_004_authoritative_validation.json
reports/rce_automation_status.json
```

Possible decisions:

```text
ALLOW_CANDIDATE_INTAKE
DENY_CANDIDATE_INTAKE
```

`ALLOW_CANDIDATE_INTAKE` means candidate evidence may proceed to sandbox intake staging. It does not authorize destination mutation, production installation, autonomous execution, or human harm.

## Manual-task elimination

The RCE continuation path no longer requires:

```text
manual workflow dispatch
manual approval-dependent validation
manual artifact download
manual receipt copying
manual task-state transition
manual candidate-intake decision
```

Push-triggered workflows build artifacts, execute validators and focused tests, commit authoritative receipts and reports, update task states, and select the next candidate goal. Generated-state commits use guarded paths and commit-message markers to prevent workflow loops.

## Permitted continuation scope

Continuation may perform deterministic reconstruction, sandbox candidate-intake staging, manifest and receipt chaining, validators, tests, reports, and automatic evidence persistence.

Continuation may not perform production installation, mutate a production destination, grant autonomous execution authority, authorize human harm, introduce real-world target data, enable weapons, or provide cyber exploitation instructions.

## Next build candidate

1. Observe the automated `RCE-P0-004` reconstruction result.
2. On authoritative `ALLOW_CANDIDATE_INTAKE`, automatically declare and activate `RCE-P0-005` for sandbox intake staging.
3. Stage only candidate evidence under a non-production sandbox path.
4. Produce origin, destination, source-package, reconstruction, and staging receipts.
5. Keep `manual_actions_required` empty and fail closed on any missing receipt, hash mismatch, path escape, or authority expansion.
