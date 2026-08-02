# Core-Lite Parallel Transition Control

This repository package adds the first working Core-Lite control surface for **parallel governed continuation**.

It does not create a communications scaffold, SMS scaffold, LLM scaffold, or unused service tree. It creates a real operating layer that can validate active workstreams, bind them to transition blocks, and produce downloadable status artifacts.

## Assumptions

1. StegVerse work happens in parallel.
2. Parallelism is not the bug; unclassified parallel drift is the bug.
3. Every active effort must be bound to a workstream.
4. Every workstream must define what "done" means.
5. Every repo-mutating action must belong to an allowed transition block.
6. Human review is required only for boundary decisions.
7. No new service skeleton should be created unless a workstream and transition block authorize it.

## Done means

This package is working when:

1. `core_lite/workstreams.yml` declares the active StegVerse workstreams.
2. `core_lite/transition_blocks.yml` declares the permitted transition blocks.
3. `tools/validate_workstreams.py` validates the relationship between workstreams and blocks.
4. A Markdown status report is generated at `reports/workstream_status.md`.
5. A JSON status report is generated at `reports/workstream_status.json`.
6. A receipt log is generated at `receipts/workstream_receipts.jsonl`.
7. The GitHub Actions workflow uploads those reports as downloadable artifacts.

## Files

```text
README.md
core_lite/workstreams.yml
core_lite/transition_blocks.yml
tools/validate_workstreams.py
github/workflows/workstream-status.yml
```

Path note: `github/workflows/workstream-status.yml` is displayed without the leading dot. The actual path in the bundle is `.github/workflows/workstream-status.yml`.

## Local usage

From the repository root:

```bash
python tools/validate_workstreams.py
```

The script writes:

```text
reports/workstream_status.md
reports/workstream_status.json
receipts/workstream_receipts.jsonl
```

## GitHub Actions usage

After uploading these files to the repo, open GitHub Actions and run:

```text
Core-Lite Workstream Status
```

The workflow uploads a downloadable artifact named:

```text
core-lite-workstream-status
```

That artifact contains:

```text
workstream_status.md
workstream_status.json
workstream_receipts.jsonl
```

## Operating rule

Core-Lite does not decide freely what kind of work it is doing.

Core-Lite is bound to user-selected transition blocks.

Any new idea may be captured as a workstream, but only block-authorized transitions may mutate the repo.

## Ecosystem Maintainer Scan

The next working W2 control is:

```bash
python tools/ecosystem_maintainer.py --root .
```

It writes:

```text
reports/ecosystem_maintainer_scan.md
reports/ecosystem_maintainer_scan.json
receipts/ecosystem_maintainer_receipts.jsonl
```

This scan performs no source mutation. It classifies files and emits reports/receipts so the next transition can be selected safely.

The first mutation-capable version should only be added after scan output proves which transition block applies.

## Friction Avoided Metric

Run:

```bash
python tools/measure_friction.py --root .
```

It writes:

```text
reports/friction_avoided.md
reports/friction_avoided.json
receipts/friction_avoided_receipts.jsonl
```

This measures estimated hours saved, repeated prompts prevented, manual actions prevented, reruns prevented, and trust-friction score.

## Bundle Registry

Run:

```bash
python tools/bundle_registry_report.py --root .
```

It writes:

```text
reports/bundle_registry.md
reports/bundle_registry.json
receipts/bundle_registry_receipts.jsonl
```

The report tracks bundle status, supersession, failed/corrective bundle churn, current canonical bundles, and estimated handling friction from the observed ZIP inventory.

## Auto-Fix Eligibility

Run:

```bash
python tools/ecosystem_maintainer.py --root .
python tools/auto_fix_eligibility.py --root .
```

It writes:

```text
reports/auto_fix_eligibility.md
reports/auto_fix_eligibility.json
receipts/auto_fix_eligibility_receipts.jsonl
```

The report classifies each scanned file into a next safe transition bucket without applying mutations.

## Capability Gap Plan

Run against a repository root:

```bash
python tools/capability_gap_plan.py --root .
```

It writes:

```text
reports/capability_gap_plan.md
reports/capability_gap_plan.json
receipts/capability_gap_receipts.jsonl
```

The report detects when a repository is clean but underbuilt relative to its inferred product role.

## Bounded evidence intake

Core-Lite also provides a privacy-safe evidence-intake and reconstruction layer for potential claims or disputed events. It preserves reported observations, representations, inferences, hypotheses, verified facts, missing evidence, contradictory evidence, ownership, and continuation scope without automatically converting them into conclusions.

This layer is governed by `CORE_LITE_MIRROR_HANDOFF.md` and currently uses Issue #3 as its canonical non-sensitive example.

### Included surfaces

```text
schemas/evidence_intake.schema.json
schemas/claim_chronology.schema.json
schemas/evidence_matrix.schema.json
fixtures/toyota_tundra_case.intake.json
fixtures/toyota_tundra_case.chronology.json
fixtures/toyota_tundra_case.evidence_matrix.json
tools/validate_evidence_intake.py
tools/run_evidence_intake_suite.py
tests/test_evidence_intake.py
receipts/evidence_intake_validation.receipt.json
.github/workflows/evidence-intake-verify.yml
```

### Local validation

```bash
python -m unittest discover -s tests
python tools/run_evidence_intake_suite.py
```

The suite regenerates `receipts/evidence_intake_validation.receipt.json` with:

- the checked-out commit and branch when available;
- SHA-256 hashes for every governed source file;
- expected and observed results for valid and fail-closed fixtures;
- deterministic receipt linkage data;
- explicit proof that validation did not upgrade claim posture or emit legal, safety, recall-applicability, liability, damages, or entitlement conclusions.

### Authority boundary

Evidence-intake validation establishes structural consistency only. It does not establish truth, legal standing, liability, vehicle safety, recall applicability, damages, entitlement, or third-party endorsement.

Public fixtures must not contain VINs, addresses, signatures, account numbers, private repair documents, or equivalent sensitive evidence. Private source evidence remains in user-controlled storage and may be represented publicly only by non-sensitive references or hashes under separately authorized custody rules.
