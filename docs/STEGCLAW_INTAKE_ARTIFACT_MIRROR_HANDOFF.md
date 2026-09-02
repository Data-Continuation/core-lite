# Core-Lite StegClaw Intake Artifact Mirror Handoff

Updated: 2026-09-02
Repository: `Data-Continuation/core-lite`
Issue: #25
Branch: `fix/stegclaw-intake-artifact-25`
State: ACTIVE_IMPLEMENTATION

## Authority

Subordinate to `docs/CORE_LITE_MIRROR_HANDOFF.md`.

Canonical RCE execution remains exclusively owned by:

```text
.github/workflows/reference-loop.yml
core_lite/reference_loop.json
```

This lane is validation-only. It may validate the static StegClaw target intake declaration and upload an artifact. It MUST NOT execute or mutate RCE lifecycle state, leases, reference-loop state, receipts, sandbox state, production state, external repositories, or publication state.

## Problem

StegClaw currently requires:

```text
core-lite-workstream-status
  -> reports/stegclaw_target_intake.json
```

But `.github/workflows/workstream-status.yml` is intentionally superseded and non-executable. The required artifact is therefore stale/unproducible from current canonical workflow state.

## Goal

Install a dedicated validation-only workflow:

```text
.github/workflows/stegclaw-intake-validation.yml
artifact: core-lite-stegclaw-intake
report: reports/stegclaw_target_intake.json
```

The workflow will:

1. check out source;
2. set up Python;
3. run `python tools/validate_stegclaw_intake.py`;
4. upload the generated report;
5. grant no write authority.

## Remaining work

1. Install workflow.
2. Update target-side documentation.
3. Validate exact PR head.
4. Merge.
5. Update StegClaw artifact request and queue to consume the new artifact identity.
6. Verify a visible completed artifact before clearing the target-artifact blocker.

## Archive posture

Not archive-ready until validation and merge are complete.
