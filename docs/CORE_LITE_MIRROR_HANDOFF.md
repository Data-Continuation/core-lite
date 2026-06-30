# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.3.0-stegclaw-target-intake-workflow-covered
```

## Current status

```text
MIRROR_HANDOFF_PRESENT
STEGCLAW_TARGET_INTAKE_DECLARED
STEGCLAW_TARGET_INTAKE_VALIDATOR_PRESENT
STEGCLAW_TARGET_INTAKE_WORKFLOW_COVERED
LOCAL_ONLY
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
docs/STEGCLAW_TARGET_INTAKE.md
```

## Current managed files

```text
core_lite/stegclaw_target_intake.json
tools/validate_stegclaw_intake.py
docs/STEGCLAW_TARGET_INTAKE.md
github/workflows/workstream-status.yml
```

Path note: `github/workflows/workstream-status.yml` is displayed without the leading dot. The actual path is `.github/workflows/workstream-status.yml`.

## Next build candidate

Inspect a visible `core-lite-workstream-status` artifact and confirm it contains `reports/stegclaw_target_intake.json`.
