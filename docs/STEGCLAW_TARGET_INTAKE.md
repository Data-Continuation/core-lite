# StegClaw Target Intake

## Purpose

This document records Core-Lite's target-side intake declaration for StegClaw handoff artifacts.

Core-Lite is currently bound as:

```text
ingestion target
CGE target
```

## Declaration

```text
core_lite/stegclaw_target_intake.json
```

## Validator

```text
python tools/validate_stegclaw_intake.py
```

Expected result:

```text
ALLOW
```

The validator writes:

```text
reports/stegclaw_target_intake.json
```

## Boundary

This intake declaration is local-only. It validates that the expected StegClaw handoff artifacts are named and that Core-Lite rules still require workstream binding and transition-block binding before any later runtime connector is added.

## Next step

Add workflow artifact coverage after the local intake validator is stable.
