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

## Workflow artifact coverage

The earlier `.github/workflows/workstream-status.yml` path is superseded and non-executable under the canonical Reference Closure Loop handoff. It must not be used as a StegClaw artifact source.

Canonical validation-only artifact producer:

```text
.github/workflows/stegclaw-intake-validation.yml
artifact: core-lite-stegclaw-intake
report: reports/stegclaw_target_intake.json
```

This workflow validates only the static target-intake declaration and uploads its report. It does not execute or mutate RCE lifecycle state, leases, reference-loop state, receipts, sandbox state, production state, external repositories, or publication state.

## Boundary

This intake declaration is local-only. It validates that the expected StegClaw handoff artifacts are named and that Core-Lite rules still require workstream binding and transition-block binding before any later runtime connector is added.

## Next step

Inspect the next visible completed `core-lite-stegclaw-intake` artifact and confirm `reports/stegclaw_target_intake.json` is present and ALLOW.
