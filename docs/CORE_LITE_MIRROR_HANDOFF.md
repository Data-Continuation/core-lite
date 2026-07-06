# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.4.0-ecosystem-management-workflow-covered
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
ECOSYSTEM_MANAGEMENT_WORKFLOW_COVERED
LOCAL_AND_CI
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
README.md
```

## Current managed files

```text
core_lite/workstreams.yml
core_lite/transition_blocks.yml
core_lite/stegclaw_target_intake.json
core_lite/bundle_registry.yml
tools/validate_workstreams.py
tools/validate_stegclaw_intake.py
tools/ecosystem_maintainer.py
tools/auto_fix_eligibility.py
tools/measure_friction.py
tools/bundle_registry_report.py
tools/capability_gap_plan.py
docs/STEGCLAW_TARGET_INTAKE.md
github/workflows/workstream-status.yml
```

Path note: `github/workflows/workstream-status.yml` is displayed without the leading dot. The actual path is `.github/workflows/workstream-status.yml`.

## Current activation goal

`Data-Continuation/core-lite` is the StegVerse-001 parallel workstream and ecosystem management verifier. It should now produce the management artifact set directly from the stable workflow, without manual report assembly.

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
```

## Next build candidate

Use the workflow-produced artifact set as the handoff input to StegVerse-002/core-lite so 002 can evaluate repo standing, authority posture, and next transition candidates from 001's reports instead of requiring manual coordination.
