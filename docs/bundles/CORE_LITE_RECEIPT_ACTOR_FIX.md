# Core-Lite Receipt Actor Fix Bundle

## Assumptions

1. The failing workflow is `Core-Lite Intake`.
2. The observed failure is caused by `append_receipt()` calling `ReceiptRecorder.record()` without the required keyword-only `actor` argument.
3. The minimum operational fix is to update `core_lite/receipts.py` only.
4. Tests may be added because they validate the fixed receipt contract and prevent recurrence.
5. No workflow files are changed.

## Done Means

This bundle is done when:

1. `python -m core_lite.cli run --repo-root . --skip-tasks` no longer fails with `ReceiptRecorder.record() missing 1 required keyword-only argument: 'actor'`.
2. Receipt entries include an `actor`.
3. Existing CLI calls that pass only a `type` field still produce a meaningful `event_type`.
4. Receipt log generation still writes `.stegverse/receipts/core_lite_receipts.jsonl`.
5. The new receipt contract tests pass.

## Files Included

```text
core_lite/receipts.py
tests/test_receipts_append_contract.py
docs/bundles/CORE_LITE_RECEIPT_ACTOR_FIX.md
bundle_manifest.json
iosnoperiod.md
```

## Primary Change

`append_receipt()` now supplies:

```text
actor = payload.get("actor", "core-lite")
```

It also maps legacy payloads using `type` into receipt `event_type`:

```text
event_type = payload.get("event_type", payload.get("type", "core_lite_cli_receipt"))
```

This preserves the existing CLI call shape while satisfying the stricter `ReceiptRecorder.record()` contract.

## Verification Commands

Run from repository root:

```bash
python -m pytest tests/test_receipts_append_contract.py
python -m core_lite.cli run --repo-root . --skip-tasks
```

## Boundary Notes

No production authority is added.

No workflow files are changed.

No install authority is granted.

This is a mechanical operational repair for the existing Core-Lite receipt contract.
