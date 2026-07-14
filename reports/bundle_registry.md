# Core-Lite Bundle Registry Report

Generated: `2026-07-14T07:52:29+00:00`

## Operating Rule

Bundle-only delivery is valid. Untracked bundle proliferation is not.

## Summary

- result: `pass`
- bundle_count: `12`
- observed_external_zip_count: `869`
- status_counts: `{'current': 2, 'failed': 1, 'superseded': 9}`
- class_counts: `{'corrective_rework': 7, 'versioned_development': 5}`
- current_bundle_count: `2`
- failed_bundle_count: `1`
- quarantine_candidate_count: `7`
- corrective_or_avoidable_count: `7`
- source_only_count: `11`
- generated_artifacts_included_count: `1`
- contains_markdown_count: `6`
- estimated_handling_hours_low: `43.45`
- estimated_handling_hours_likely: `86.9`
- estimated_handling_hours_high: `144.83`
- error_count: `0`

## Current Bundles

- `B-CORELITE-011` — `core-lite-maintainer-python-stub-classifier-fix.zip`: Fix Python stub classifier to avoid keyword false positives.
- `B-CORELITE-012` — `core-lite-bundle-registry-supersession.zip`: Add bundle registry and supersession reporting.

## Failed Bundles

- `B-CORELITE-009` — `core-lite-maintainer-classifier-false-positive-fix.zip`: Bundle exposed only VERIFY_RESULT.txt and was unusable.

## Quarantine Candidates

- `B-CORELITE-002` — `core-lite-parallel-transition-control-source-only.zip` / status `superseded` / class `corrective_rework`
- `B-CORELITE-003` — `core-lite-parallel-transition-control-iphone-visible.zip` / status `superseded` / class `corrective_rework`
- `B-CORELITE-006` — `core-lite-ecosystem-maintainer-workflow-dependency-fix.zip` / status `superseded` / class `corrective_rework`
- `B-CORELITE-008` — `core-lite-pyyaml-repeat-failure-hardening.zip` / status `superseded` / class `corrective_rework`
- `B-CORELITE-009` — `core-lite-maintainer-classifier-false-positive-fix.zip` / status `failed` / class `corrective_rework`
- `B-CORELITE-010` — `core-lite-maintainer-classifier-false-positive-fix-v2.zip` / status `superseded` / class `corrective_rework`
- `B-CORELITE-011` — `core-lite-maintainer-python-stub-classifier-fix.zip` / status `current` / class `corrective_rework`

## Bundles

### B-CORELITE-001 — core-lite-parallel-transition-control.zip

- Workstream: `W2`
- Class: `versioned_development`
- Status: `superseded`
- Purpose: Initial parallel transition control surface.
- Supersedes: `[]`
- Superseded by: `B-CORELITE-003`
- Source only: `False`
- Generated artifacts included: `True`
- Contains Markdown: `True`
- Verification result: `pass_with_cleanup_needed`
- Notes: Included generated reports/receipts and needed iPhone-visible correction.

### B-CORELITE-002 — core-lite-parallel-transition-control-source-only.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `superseded`
- Purpose: Remove generated reports and receipts from source bundle.
- Supersedes: `['B-CORELITE-001']`
- Superseded by: `B-CORELITE-003`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `True`
- Verification result: `superseded`
- Notes: Corrected source/runtime artifact mixing but still carried hidden workflow path issue.

### B-CORELITE-003 — core-lite-parallel-transition-control-iphone-visible.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `superseded`
- Purpose: Make workflow path visible on iPhone by using visible bundle path.
- Supersedes: `['B-CORELITE-002']`
- Superseded by: `B-CORELITE-004`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `True`
- Verification result: `pass`
- Notes: Established visible workflow path convention.

### B-CORELITE-004 — core-lite-transition-block-warning-fix.zip

- Workstream: `W3`
- Class: `versioned_development`
- Status: `superseded`
- Purpose: Add missing forbidden/high-risk transition blocks and reduce warnings to zero.
- Supersedes: `['B-CORELITE-003']`
- Superseded by: `B-CORELITE-005`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `False`
- Verification result: `pass`
- Notes: Cleaned transition block registry warnings.

### B-CORELITE-005 — core-lite-ecosystem-maintainer-scan.zip

- Workstream: `W2`
- Class: `versioned_development`
- Status: `superseded`
- Purpose: Add scan-only ecosystem maintainer.
- Supersedes: `['B-CORELITE-004']`
- Superseded by: `B-CORELITE-006`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `True`
- Verification result: `pass_local_then_ci_dependency_failure`
- Notes: Introduced maintainer scan but workflow dependency was missing in active CI path.

### B-CORELITE-006 — core-lite-ecosystem-maintainer-workflow-dependency-fix.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `superseded`
- Purpose: Install PyYAML before running validator in maintainer workflow.
- Supersedes: `['B-CORELITE-005']`
- Superseded by: `B-CORELITE-008`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `False`
- Verification result: `insufficient_alone`
- Notes: Workflow-only fix was not robust enough because validator itself still depended on PyYAML availability.

### B-CORELITE-007 — core-lite-friction-avoided-metric.zip

- Workstream: `W2`
- Class: `versioned_development`
- Status: `superseded`
- Purpose: Add Friction Avoided metric.
- Supersedes: `['B-CORELITE-006']`
- Superseded by: `B-CORELITE-008`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `True`
- Verification result: `pass`
- Notes: Friction metric generated 31.05 estimated hours saved and 219 repeated prompts prevented.

### B-CORELITE-008 — core-lite-pyyaml-repeat-failure-hardening.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `superseded`
- Purpose: Harden validator against repeated PyYAML missing dependency failure.
- Supersedes: `['B-CORELITE-006', 'B-CORELITE-007']`
- Superseded by: `B-CORELITE-010`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `False`
- Verification result: `pass`
- Notes: Validator self-installs PyYAML if missing.

### B-CORELITE-009 — core-lite-maintainer-classifier-false-positive-fix.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `failed`
- Purpose: Intended to fix classifier false positives.
- Supersedes: `['B-CORELITE-008']`
- Superseded by: `B-CORELITE-010`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `False`
- Verification result: `failed_bundle_content`
- Notes: Bundle exposed only VERIFY_RESULT.txt and was unusable.

### B-CORELITE-010 — core-lite-maintainer-classifier-false-positive-fix-v2.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `superseded`
- Purpose: Provide actual maintainer classifier false-positive fix.
- Supersedes: `['B-CORELITE-009']`
- Superseded by: `B-CORELITE-011`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `False`
- Verification result: `partial_pass`
- Notes: Fixed workflow/support false positives but Python scanner still classified itself as STUB.

### B-CORELITE-011 — core-lite-maintainer-python-stub-classifier-fix.zip

- Workstream: `W2`
- Class: `corrective_rework`
- Status: `current`
- Purpose: Fix Python stub classifier to avoid keyword false positives.
- Supersedes: `['B-CORELITE-010']`
- Superseded by: `None`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `False`
- Verification result: `pass`
- Notes: Latest maintainer scan shows STUB 0, ORPHAN_CANDIDATE 0, BROKEN 0.

### B-CORELITE-012 — core-lite-bundle-registry-supersession.zip

- Workstream: `W2`
- Class: `versioned_development`
- Status: `current`
- Purpose: Add bundle registry and supersession reporting.
- Supersedes: `['B-CORELITE-011']`
- Superseded by: `None`
- Source only: `True`
- Generated artifacts included: `False`
- Contains Markdown: `True`
- Verification result: `pending_user_run`
- Notes: Introduces canonical bundle tracking and bundle churn metrics.

## Receipt

- Receipt hash: `54d678c8dd991a248bbde4c02abbe9b37f979c80556da575b0409bbc47263a5f`
- Receipt path: `receipts/bundle_registry_receipts.jsonl`
