# Core-Lite Mirror Handoff

This file is the source of truth for continuing `Data-Continuation/core-lite` work across sessions.

## Current version

```text
0.11.1-reference-closure-loop-merged
```

## Current status

```text
MIRROR_HANDOFF_PRESENT
ECOSYSTEM_GOAL_RETAINED
REFERENCE_REPOSITORY_SELECTED
REFERENCE_LOOP_IMPLEMENTATION_VERIFIED
REFERENCE_LOOP_MERGED_TO_MAIN
REFERENCE_LOOP_ACTIVATION_TRIGGER_COMMITTED
FIRST_MANAGED_CLOSURE_PENDING
RCE_P0_001_THROUGH_P0_006_COMPLETE
RCE_P0_007_LIFECYCLE_ACTIVE
RCE_P0_008_THROUGH_P0_014_IMPLEMENTED_DEPENDENCY_GATED
SANDBOX_ONLY
NO_PRODUCTION_DESTINATION_AUTHORITY
NO_EXTERNAL_REPOSITORY_MUTATION_AUTHORITY
```

## Verified integration evidence

```text
pull request: 6
verification workflow run: 29382140223
verification result: SUCCESS
merged commit: 440d09590eef7008e5f3e5369a5257930c2c65b3
activation trigger commit: 456084a5e06d18dd531dbe9cd9d717e2fb15ac88
expected first state: core_lite/reference_loop_state.json
expected first report: reports/reference_loop_status.json
expected first receipt chain: receipts/reference_loop_receipts.jsonl
```

The implementation is merged and its tests passed on the pull-request merge ref. Activation is not yet declared complete because the first managed state, report, and receipt have not been persisted on `main`.

## Direction

The ecosystem autonomy goal is not reset or narrowed. Execution is redirected through one complete reference implementation in one repository before responsibility is expanded or replicated.

`Data-Continuation/core-lite` is the lead repository. It must prove a repository-local loop:

```text
observe
-> select eligible task
-> acquire lease
-> execute registered command
-> apply bounded remediation policy
-> verify
-> persist hash-chained receipt
-> update task state
-> activate eligible successor
-> continue or escalate fail-closed
```

The loop retains situational awareness of related ecosystem repositories and their relative build posture, but it has no authority to mutate them.

## Reference-loop implementation

```text
configuration and ecosystem map: core_lite/reference_loop.json
runner: tools/run_reference_loop.py
state: core_lite/reference_loop_state.json
status report: reports/reference_loop_status.json
escalation report: reports/reference_loop_escalation.json
receipt chain: receipts/reference_loop_receipts.jsonl
tests: tests/test_run_reference_loop.py
workflow: .github/workflows/reference-loop.yml
```

The workflow runs one eligible local task per cycle. A concurrency group and persisted lease suppress duplicate execution. Commands must exist in the local command registry. Unknown commands, unapproved remediation, non-zero verification, production mutation, and external-repository mutation are not authorized.

The first task validates the existing workstream registry and closes only after independent verification succeeds. Its only remediation policy is one declared rerun. Continued failure creates an escalation receipt and fails the workflow after evidence persistence.

The second task becomes eligible only after the first closes. It runs the existing repository scanner and verifies that the existing auto-fix eligibility planner completes.

## Ecosystem situational awareness

The machine-readable relationship map in `core_lite/reference_loop.json` records the current sequencing posture:

```text
Data-Continuation/core-lite -> lead reference implementation
master-records/master-records -> parallel receipt and reconstruction contract work
BCAT-GCAT-Engine/core-lite-prod -> production-class successor after reference proof
StegVerse-Labs/Site -> parallel bundle, receipt, and status interface work
StegGhost/entity-sandbox -> sandbox replication candidate after activation
StegVerse-org/demo_ingest_engine -> portability validation after activation
StegVerse-Labs/StegAgents -> future task-worker contract consumer
StegVerse-Labs/StegVerse-Healer -> future bounded-remediation contract consumer
BCAT-GCAT-Engine/Publisher -> downstream verified publication obligation
StegVerse-Labs/Sit -> downstream update-verification obligation
admissibility-wiki -> downstream governance documentation obligation
stegguardian-wiki -> downstream Guardian documentation obligation
```

This map is advisory and observational. It does not create cross-repository standing or mutation authority.

## Existing RCE authoritative chain

```text
RCE-P0-001 -> COMPLETE
receipt: receipts/rce_p0_001_authoritative_validation.json

RCE-P0-002 -> COMPLETE
receipt: receipts/rce_p0_002_authoritative_validation.json

RCE-P0-003 -> COMPLETE
receipt: receipts/rce_p0_003_authoritative_validation.json

RCE-P0-004 -> COMPLETE
receipt: receipts/rce_p0_004_authoritative_validation.json
decision: ALLOW_CANDIDATE_INTAKE

RCE-P0-005 -> COMPLETE
receipt: receipts/rce_p0_005_authoritative_validation.json
decision: STAGED_CANDIDATE_EVIDENCE

RCE-P0-006 -> COMPLETE
receipt: receipts/rce_p0_006_authoritative_validation.json
decision: CUSTODY_AND_REPLAY_VERIFIED
```

## Active RCE task

```text
RCE-P0-007
owner: core_lite_management_workflow
purpose: sandbox lifecycle, supersession, downgrade prevention, and deterministic archival
status: ACTIVE pending authoritative managed-state receipt
expected receipt: receipts/rce_p0_007_authoritative_validation.json
expected lifecycle state: sandbox/intake/relationship_conditioned_execution/lifecycle_state.json
```

The existing `.github/workflows/workstream-status.yml` remains responsible for the RCE sandbox chain. Repeated workflow failures mean its autonomous claims are not considered proven merely because the schedule and implementation exist. The reference closure loop is responsible for producing explicit task-level closure or escalation evidence and will be expanded only after its first cycle is verified.

## Safety and authority boundaries

```text
relationship history provides context but does not create authority
candidate intake and sandbox staging do not grant production authority
no task may mutate an external or production destination
no autonomous harmful execution is permitted
all receipt, hash, path, version, authority, custody, lease, and verification mismatches fail closed
historical quarantine and divergence evidence is never deleted
cross-repository awareness does not create cross-repository mutation authority
```

## Immediate continuation

```text
observe the activation-triggered workflow result
-> persist REF-LOOP-001 completion or escalation evidence
-> verify core_lite/reference_loop_state.json and the receipt chain
-> confirm REF-LOOP-002 activation only after verified closure
-> execute and verify REF-LOOP-002
-> reconcile the results with the existing RCE workstream failure evidence
-> expand responsibility only to the nearest compatible scope
```

Do not begin ecosystem-wide mutation. Do not duplicate the loop before the reference cycle is verified. Parallel work is limited to compatibility contracts and situational-awareness updates that do not claim operational completion.
