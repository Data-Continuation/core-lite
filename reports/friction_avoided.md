# Core-Lite Friction Avoided Report

Generated: `2026-07-14T07:35:19+00:00`

## Definition

Avoidable human recovery burden prevented by governed execution.

## Summary

- result: `pass`
- failure_type_count: `12`
- estimated_minutes_saved: `1863`
- estimated_hours_saved: `31.05`
- repeated_prompts_prevented: `219`
- manual_actions_prevented: `68`
- reruns_prevented: `3`
- trust_friction_score: `30`
- error_count: `0`

## Category Totals

### artifact_architecture

- event_count: `2`
- estimated_minutes_saved: `720`
- repeated_prompts_prevented: `85`
- manual_actions_prevented: `17`
- reruns_prevented: `0`

### assistant_process

- event_count: `1`
- estimated_minutes_saved: `30`
- repeated_prompts_prevented: `6`
- manual_actions_prevented: `4`
- reruns_prevented: `0`

### bundle_delivery

- event_count: `2`
- estimated_minutes_saved: `23`
- repeated_prompts_prevented: `5`
- manual_actions_prevented: `3`
- reruns_prevented: `0`

### communications_boundary

- event_count: `1`
- estimated_minutes_saved: `60`
- repeated_prompts_prevented: `6`
- manual_actions_prevented: `3`
- reruns_prevented: `1`

### memory_continuity

- event_count: `1`
- estimated_minutes_saved: `420`
- repeated_prompts_prevented: `50`
- manual_actions_prevented: `10`
- reruns_prevented: `0`

### mutation_execution

- event_count: `1`
- estimated_minutes_saved: `360`
- repeated_prompts_prevented: `35`
- manual_actions_prevented: `20`
- reruns_prevented: `0`

### theory_to_implementation

- event_count: `1`
- estimated_minutes_saved: `180`
- repeated_prompts_prevented: `18`
- manual_actions_prevented: `5`
- reruns_prevented: `0`

### verification

- event_count: `1`
- estimated_minutes_saved: `15`
- repeated_prompts_prevented: `4`
- manual_actions_prevented: `1`
- reruns_prevented: `1`

### workflow

- event_count: `2`
- estimated_minutes_saved: `55`
- repeated_prompts_prevented: `10`
- manual_actions_prevented: `5`
- reruns_prevented: `1`

## Failure Types

### F-A1 — New-artifact drift

- Category: `artifact_architecture`
- Estimated minutes saved: `240`
- Estimated hours saved: `4.0`
- Repeated prompts prevented: `30`
- Manual actions prevented: `5`
- Reruns prevented: `0`
- Trust severity: `high`
- Prevented by:
  - `CONTINUITY_REGISTRY_CHECK`
  - `BLOCK_START_OVER`
  - `CREATE_NEW_REPO`
  - `CREATE_UNUSED_SCAFFOLD`
- Evidence note: Existing artifact not checked before proposing a new artifact.

### F-A2 — Stub multiplication

- Category: `artifact_architecture`
- Estimated minutes saved: `480`
- Estimated hours saved: `8.0`
- Repeated prompts prevented: `55`
- Manual actions prevented: `12`
- Reruns prevented: `0`
- Trust severity: `high`
- Prevented by:
  - `DETECT_STUB`
  - `DETECT_STUB_DEPENDENCY`
  - `AUTO_QUARANTINE_STUB`
  - `COMPLETE_LOW_RISK_STUB`
  - `CREATE_UNUSED_SCAFFOLD`
- Evidence note: Skeletons and placeholders create later cleanup debt.

### F-W1 — Missing workflow dependency

- Category: `workflow`
- Estimated minutes saved: `25`
- Estimated hours saved: `0.42`
- Repeated prompts prevented: `4`
- Manual actions prevented: `2`
- Reruns prevented: `1`
- Trust severity: `medium`
- Prevented by:
  - `VERIFY_WORKFLOW_DEPENDENCIES`
  - `VERIFY_REPO`
- Evidence note: Workflow called a Python script before installing PyYAML.

### F-W3 — Hidden workflow path visibility failure

- Category: `workflow`
- Estimated minutes saved: `30`
- Estimated hours saved: `0.5`
- Repeated prompts prevented: `6`
- Manual actions prevented: `3`
- Reruns prevented: `0`
- Trust severity: `medium`
- Prevented by:
  - `VERIFY_WORKFLOW_PATH`
  - `DEFINE_UPLOAD_MAP`
- Evidence note: iPhone Files hid a workflow folder whose actual name begins with a leading dot.

### F-B1 — Source bundle polluted with generated artifacts

- Category: `bundle_delivery`
- Estimated minutes saved: `15`
- Estimated hours saved: `0.25`
- Repeated prompts prevented: `3`
- Manual actions prevented: `2`
- Reruns prevented: `0`
- Trust severity: `medium`
- Prevented by:
  - `VERIFY_BUNDLE_CONTENTS`
  - `VERIFY_SOURCE_ONLY_BUNDLE`
- Evidence note: Source bundle included generated reports and receipts.

### F-B3 — Path-display rule violation

- Category: `bundle_delivery`
- Estimated minutes saved: `8`
- Estimated hours saved: `0.13`
- Repeated prompts prevented: `2`
- Manual actions prevented: `1`
- Reruns prevented: `0`
- Trust severity: `medium`
- Prevented by:
  - `VERIFY_RESPONSE_CONSTRAINTS`
- Evidence note: A path beginning with a leading dot was displayed directly.

### F-V3 — Warning debt tolerated

- Category: `verification`
- Estimated minutes saved: `15`
- Estimated hours saved: `0.25`
- Repeated prompts prevented: `4`
- Manual actions prevented: `1`
- Reruns prevented: `1`
- Trust severity: `medium`
- Prevented by:
  - `VERIFY_BLOCK_REFERENCE`
  - `DEFINE_TRANSITION_BLOCK`
- Evidence note: Registry passed with warnings before missing forbidden blocks were defined.

### F-X2 — Over-conservative mutation block

- Category: `mutation_execution`
- Estimated minutes saved: `360`
- Estimated hours saved: `6.0`
- Repeated prompts prevented: `35`
- Manual actions prevented: `20`
- Reruns prevented: `0`
- Trust severity: `high`
- Prevented by:
  - `AUTO_FIX_MECHANICAL`
  - `AUTO_QUARANTINE_STUB`
  - `GENERATE_ROLLBACK`
  - `VERIFY_REPO`
- Evidence note: Blocking all mutation pushes safe maintenance debt back to the user.

### F-M1 — Context reset causes artifact replacement

- Category: `memory_continuity`
- Estimated minutes saved: `420`
- Estimated hours saved: `7.0`
- Repeated prompts prevented: `50`
- Manual actions prevented: `10`
- Reruns prevented: `0`
- Trust severity: `high`
- Prevented by:
  - `CONTINUITY_REGISTRY_CHECK`
  - `BLOCK_START_OVER`
  - `CREATE_NEW_REPO`
- Evidence note: Existing artifacts lose continuity when new chats restart from concept.

### F-R1 — Patch instead of full replacement

- Category: `assistant_process`
- Estimated minutes saved: `30`
- Estimated hours saved: `0.5`
- Repeated prompts prevented: `6`
- Manual actions prevented: `4`
- Reruns prevented: `0`
- Trust severity: `medium`
- Prevented by:
  - `VERIFY_RESPONSE_CONSTRAINTS`
- Evidence note: Partial patches increase iPhone application and merge risk.

### F-C1 — SMS treated as authority

- Category: `communications_boundary`
- Estimated minutes saved: `60`
- Estimated hours saved: `1.0`
- Repeated prompts prevented: `6`
- Manual actions prevented: `3`
- Reruns prevented: `1`
- Trust severity: `high`
- Prevented by:
  - `PARSE_DECISION_CODE`
  - `MAP_ACTOR`
  - `DEFINE_AUTHORITY_BOUNDARY`
  - `DIRECT_EXECUTION_FROM_SMS`
- Evidence note: SMS must be a channel, not execution authority.

### F-T1 — Formalism stays descriptive

- Category: `theory_to_implementation`
- Estimated minutes saved: `180`
- Estimated hours saved: `3.0`
- Repeated prompts prevented: `18`
- Manual actions prevented: `5`
- Reruns prevented: `0`
- Trust severity: `high`
- Prevented by:
  - `DEFINE_TRANSITION_BLOCK`
  - `VERIFY_BLOCK_REFERENCE`
  - `CLASSIFY_TRANSITION_BLOCK`
- Evidence note: Transition table must become executable constraints, not only theory.

## Receipt

- Receipt hash: `4d04444949ebbc6950c964be69478030cce39290a79a272b119222793bf63673`
- Receipt path: `receipts/friction_avoided_receipts.jsonl`
