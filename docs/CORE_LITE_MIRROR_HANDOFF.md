# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.8.0-rce-p0-003-declared
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
RCE_P0_003_DECLARED
LOCAL_AND_CI
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md
docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md
core_lite/tasks/relationship_conditioned_execution.json
core_lite/tasks/relationship_conditioned_execution_p0_002.json
core_lite/tasks/relationship_conditioned_execution_p0_003.json
receipts/rce_p0_001_authoritative_validation.json
receipts/rce_p0_002_authoritative_validation.json
```

## Existing management path

`Data-Continuation/core-lite` remains the StegVerse-001 parallel workstream and ecosystem management verifier. It generates management reports and receipts, commits them when changed, and exports candidate evidence for:

```text
StegVerse-002/core-lite::incoming/data_continuation_core_lite/
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

Expected destination transition:

```text
MANAGEMENT_PACKAGE_CANDIDATE_EVIDENCE_ACCEPTED
```

This existing management-package path remains independently valid.

## Relationship-conditioned execution lineage

The AI-human relationship discussion and the v1.0-v2.2 artifact lineage are durably preserved in:

```text
docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md
```

The prior conversation ZIPs remain unvalidated scaffolding and must not be ingested as production releases.

### RCE-P0-001 — COMPLETE

Purpose: define the normative relationship-conditioned human-decision policy and machine-readable boundary record.

Authoritative validation:

```text
workflow: RCE P0-001 Validation
run_id: 29308124165
run_number: 32
conclusion: success
authoritative_completion_evidence: true
receipt: receipts/rce_p0_001_authoritative_validation.json
```

Validated commands:

```text
python tools/validate_relationship_conditioned_human_decision_policy.py
python -m pytest -q tests/test_relationship_conditioned_human_decision_policy.py
```

The policy preserves these invariants:

```text
relationship history provides context but does not create authority
uncertainty acknowledgment is not execution authorization
present consent does not bind an uncertain future self
AI quorum, reputation, voting, or adaptive thresholds cannot authorize human harm
irreversible severe human impact cannot receive autonomous ALLOW
unknown, expired, revoked, conflicting, or out-of-scope authority fails closed
```

### RCE-P0-002 — COMPLETE

Purpose: define a deterministic, non-operational execution-candidate manifest and harmless sandbox fixtures.

Authoritative validation:

```text
workflow: RCE P0-002 Validation
run_id: 29308190352
run_number: 1
conclusion: success
authoritative_completion_evidence: true
receipt: receipts/rce_p0_002_authoritative_validation.json
```

Validated fixtures:

```text
allow.example: reversible non-sensitive sandbox report publication -> ALLOW
stale_state.example: stale evidence -> DENY
scope_leakage.example: predicted effect outside authorized domains -> DENY
```

`ALLOW` remains limited to reversible, non-severe, harmless sandbox actions with fresh sufficient state, valid commit-time authority, contained effects, resolved collateral, reachable denial, preserved governability, preserved recoverability, and integrity-protected traceability.

### RCE-P0-003 — DECLARED

Purpose: package the validated RCE artifacts as a deterministic, sandbox-only Core-Lite ingestion candidate.

Required outputs:

```text
bundles/relationship_conditioned_execution/bundle_manifest.json
bundles/relationship_conditioned_execution/install_plan.json
bundles/relationship_conditioned_execution/source_inventory.json
tools/build_relationship_conditioned_execution_bundle.py
tools/validate_relationship_conditioned_execution_bundle.py
tests/test_relationship_conditioned_execution_bundle.py
.github/workflows/rce-p0-003-validation.yml
```

Required package properties:

```text
per-file sha256 digests and byte counts
explicit source and sandbox target paths
policy and schemas ordered before validators and fixtures
candidate_evidence_only: true
autonomous_execution_authority: false
no production destination paths
fail closed on missing file, hash mismatch, size mismatch, path traversal, production target, or execution authority
```

## Permitted continuation scope

Continuation may create manifests, sandbox-only install plans, deterministic inventories, builders, validators, tests, and receipts. It may not install to production, mutate a destination automatically, grant autonomous execution authority, authorize human harm, introduce real-world target data, enable weapons, or provide cyber exploitation instructions.

## Next build candidate

Implement and authoritatively validate `RCE-P0-003`. After its receipt is preserved, the next admissible decision is whether to submit the sandbox-only candidate to the existing Core-Lite intake path or require an additional independent reconstruction review first.
