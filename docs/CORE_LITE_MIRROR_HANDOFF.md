# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current goal

Install target-side intake handoff support for StegClaw while keeping this repository local-only.

## Current version

```text
0.1.0-stegclaw-target-intake-handoff
```

## Current status

```text
MIRROR_HANDOFF_PRESENT
STEGCLAW_TARGET_INTAKE_HANDOFF_PENDING
LOCAL_ONLY
```

## Source-of-truth documents

```text
docs/CORE_LITE_MIRROR_HANDOFF.md
```

## Bound upstream source

```text
repo:Data-Continuation:StegClaw
```

## Expected upstream artifact names

```text
standing_envelope.json
standing_receipt.json
ingestion_candidate.json
ingestion_candidate_receipt.json
outbound_envelope.json
outbound_receipt.json
live_integration_manifest.json
```

## Boundary rules

Core-Lite receives StegClaw handoff material as intake candidates.

Core-Lite only advances those candidates after local workstream and transition-block checks.

This handoff does not install a runtime connector.

## Next build candidate

Install a target-side StegClaw intake declaration and validation receipt path.

## Handoff instruction

Continue from this file before relying on prior chat context.
