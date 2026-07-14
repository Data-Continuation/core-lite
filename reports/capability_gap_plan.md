# Core-Lite Capability Gap Plan

Generated: `2026-07-14T06:57:22+00:00`
Target root: `/home/runner/work/core-lite/core-lite`

## Done Definition

- Read repository role signals.
- Read directory and file structure.
- Infer expected capabilities.
- Classify missing, placeholder-only, and implemented/seeded capabilities.
- Generate Markdown and JSON reports.
- Emit receipt.
- Perform no source mutation.

## Repository Role

- Role: `core-lite`
- Confidence: `high`
- Scores: `{'footprint-auditor': 107, 'core-lite': 1637, 'formalism': 55}`

## Summary

- result: `pass`
- file_count: `140`
- directory_count: `25`
- capability_count: `9`
- implemented_or_seeded_count: `2`
- missing_or_placeholder_count: `7`
- mutation_count: `0`
- status_counts: `{'implemented_or_seeded': 2, 'signaled_missing': 7}`
- risk_counts: `{'high': 7, 'low': 2}`

## Capabilities

### scanner — Repository scanning / metadata extraction

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Missing:
  - expected path missing: src/scanner
- Evidence:
  - signal hit(s): src/scanner, scanner, scan, commit_metadata

### classifier — Finding classification and severity classification

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Missing:
  - expected path missing: src/classifier
- Evidence:
  - signal hit(s): src/classifier, classifier, severity_rules, severity

### sanitizer — Sanitization / remediation planning

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Missing:
  - expected path missing: src/sanitizer
- Evidence:
  - signal hit(s): src/sanitizer, sanitizer, sanitize, redact

### reporter — Markdown/JSON report generation

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Missing:
  - expected path missing: src/reporter
- Evidence:
  - signal hit(s): src/reporter, reporter, report, reports

### config — Configuration registry and rule configuration

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Missing:
  - expected path missing: config/ecosystems.yaml
  - expected path missing: config/severity_rules.yaml
- Evidence:
  - signal hit(s): config/, config, ecosystems.yaml, severity_rules.yaml

### operations_docs — Operator workflow and usage documentation

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Missing:
  - expected path missing: docs/OPERATIONS.md
- Evidence:
  - signal hit(s): docs/OPERATIONS.md, operations, usage

### cli_or_entrypoint — Executable command entrypoint for local or CI operation

- Status: `signaled_missing`
- Risk: `high`
- Recommended transition block: `PLAN_CAPABILITY_COMPLETION`
- Evidence:
  - signal hit(s): cli, main, __main__, argparse, click, typer

### tests — Automated tests for scanner/classifier/sanitizer/reporter behavior

- Status: `implemented_or_seeded`
- Risk: `low`
- Recommended transition block: `NO_ACTION`
- Implementation files:
  - `tests/fixtures/sample_ingest_bundle/bundle_manifest.json`
  - `tests/fixtures/sample_ingest_bundle/payload/sample.txt`
  - `tests/test_execution_candidate_manifest.py`
  - `tests/test_ingest_incoming_contract.py`
  - `tests/test_receipts_append_contract.py`
  - `tests/test_reconstruct_relationship_conditioned_execution_bundle.py`
  - `tests/test_relationship_conditioned_execution_bundle.py`
  - `tests/test_relationship_conditioned_human_decision_policy.py`
- Evidence:
  - signal hit(s): tests/, pytest, unittest
  - expected path exists: tests
  - implementation file(s): tests/fixtures/sample_ingest_bundle/bundle_manifest.json, tests/fixtures/sample_ingest_bundle/payload/sample.txt, tests/test_execution_candidate_manifest.py, tests/test_ingest_incoming_contract.py, tests/test_receipts_append_contract.py, tests/test_reconstruct_relationship_conditioned_execution_bundle.py, tests/test_relationship_conditioned_execution_bundle.py, tests/test_relationship_conditioned_human_decision_policy.py

### workflow — GitHub Actions workflow for running product checks

- Status: `implemented_or_seeded`
- Risk: `low`
- Recommended transition block: `NO_ACTION`
- Implementation files:
  - `.github/workflows/auto-fix-eligibility.yml`
  - `.github/workflows/bundle-registry.yml`
  - `.github/workflows/core-lite-intake.yml`
  - `.github/workflows/core-lite-self-test.yml`
  - `.github/workflows/ecosystem-maintainer-scan.yml`
  - `.github/workflows/friction-avoided.yml`
  - `.github/workflows/install-iosnoperiod.yml`
  - `.github/workflows/rce-p0-001-validation.yml`
  - `.github/workflows/rce-p0-002-validation.yml`
  - `.github/workflows/rce-p0-003-validation.yml`
  - `.github/workflows/rce-p0-004-validation.yml`
  - `.github/workflows/target-capability-gap.yml`
  - `.github/workflows/target-repo-scan.yml`
  - `.github/workflows/workstream-status.yml`
- Missing:
  - expected path missing: github/workflows
- Evidence:
  - signal hit(s): .github/workflows, github/workflows
  - expected path exists: .github/workflows
  - implementation file(s): .github/workflows/auto-fix-eligibility.yml, .github/workflows/bundle-registry.yml, .github/workflows/core-lite-intake.yml, .github/workflows/core-lite-self-test.yml, .github/workflows/ecosystem-maintainer-scan.yml, .github/workflows/friction-avoided.yml, .github/workflows/install-iosnoperiod.yml, .github/workflows/rce-p0-001-validation.yml

## Receipt

- Receipt hash: `9285e8e33e90806315a52690973570a910ff10686591e6f8f1e61fdf2809a296`
- Receipt path: `receipts/capability_gap_receipts.jsonl`
