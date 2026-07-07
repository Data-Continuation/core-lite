# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.5.0-stegverse-002-export-package-covered
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
ECOSYSTEM_MANAGEMENT_WORKFLOW_COVERED
LOCAL_AND_CI
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
README.md
core_lite/stegverse_002_export_manifest.json
```

## Current managed files

```text
core_lite/workstreams.yml
core_lite/transition_blocks.yml
core_lite/stegclaw_target_intake.json
core_lite/bundle_registry.yml
core_lite/stegverse_002_export_manifest.json
tools/validate_workstreams.py
tools/validate_stegclaw_intake.py
tools/ecosystem_maintainer.py
tools/auto_fix_eligibility.py
tools/measure_friction.py
tools/bundle_registry_report.py
tools/capability_gap_plan.py
tools/validate_stegverse_002_export.py
docs/STEGCLAW_TARGET_INTAKE.md
github/workflows/workstream-status.yml
```

Path note: `github/workflows/workstream-status.yml` is displayed without the leading dot. The actual path is `.github/workflows/workstream-status.yml`.

## Current activation goal

`Data-Continuation/core-lite` is the StegVerse-001 parallel workstream and ecosystem management verifier. It now declares and validates the management artifact package required by `StegVerse-002/core-lite` management package intake.

Expected workflow artifact: `core-lite-workstream-status`

Expected included outputs:

```text
reports/workstream_status.md
reports/workstream_status.json
receipts/workstream_receipts.jsonl
reports/stegclaw_target_intake.json
reports/ecosystem_maintainer_scan.md
reports/ecosystem_maintainer_scan.json
receipts/ecosystem_maintainer_receipts.jsonl
reports/auto_fix_eligibility.md
reports/auto_fix_eligibility.json
receipts/auto_fix_eligibility_receipts.jsonl
reports/friction_avoided.md
reports/friction_avoided.json
receipts/friction_avoided_receipts.jsonl
reports/bundle_registry.md
reports/bundle_registry.json
receipts/bundle_registry_receipts.jsonl
reports/capability_gap_plan.md
reports/capability_gap_plan.json
receipts/capability_gap_receipts.jsonl
reports/stegverse_002_export_manifest.md
reports/stegverse_002_export_manifest.json
receipts/stegverse_002_export_receipts.jsonl
```

## Destination intake

```text
StegVerse-002/core-lite::config/management_package_intake_policy.json
```

Expected destination transition:

```text
MANAGEMENT_PACKAGE_CANDIDATE_EVIDENCE_ACCEPTED
```

## Next build candidate

Inspect or retrieve the workflow-produced `core-lite-workstream-status` artifact and use `reports/stegverse_002_export_manifest.json` plus the required management reports as the handoff input to `StegVerse-002/core-lite`.
