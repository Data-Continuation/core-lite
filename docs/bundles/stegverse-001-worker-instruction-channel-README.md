# StegVerse-001 Worker Instruction Channel

## Assumptions

1. StegVerse-001 must become an operational worker, not just a name used in chat.
2. The first worker channel should not be `incoming/` because `incoming/` is already consumed by Core-Lite Intake.
3. The first worker task must determine the working structure and return the plan.
4. The worker must not patch files during this task.
5. The worker must stop after returning report, plan, and receipt.

## Done

This bundle is done when `core-lite` contains:

```text
instructions/current/stegverse-001-command.json
schemas/stegverse_worker_instruction.schema.json
tools/stegverse001_worker.py
tools/tasks/stegverse001_worker_tasks.json
docs/bundles/stegverse-001-worker-instruction-channel-README.md
```

and the task emits:

```text
reports/current/stegverse-001-worker/working_contract_report.json
reports/current/stegverse-001-worker/working_contract_report.md
reports/current/stegverse-001-worker/working_contract_plan.json
receipts/current/stegverse-001-worker/receipts.jsonl
```

## Task ID

```text
stegverse001_determine_core_lite_working_contract
```

## Run

```bash
python tools/run_declared_tasks.py tools/tasks/stegverse001_worker_tasks.json --task-id stegverse001_determine_core_lite_working_contract
```

Direct run:

```bash
python tools/stegverse001_worker.py
```

## What the Worker Does

```text
reads instructions/current/stegverse-001-command.json
inspects workflows
inspects tools/tasks
inspects core_lite/cli.py
inspects core_lite/cge.py
inspects core_lite/ingest.py
inspects core_lite/sandbox.py
inspects core_lite/receipts.py
detects observed import needs
detects missing contractual exports
detects transition surfaces
returns one plan
emits receipt
stops
```

## What the Worker Does Not Do

```text
does not patch files
does not submit bundles to incoming/
does not add workflows
does not install
does not promote to production
does not activate node status
does not activate FinCo
does not self-accredit
```

## Active Transition

```text
incoming bundle detected
manifest validated
CGE precheck
sandbox experiment
sandbox result
CGE result classification
report returned
receipt emitted
STOP
```

## Operating Rule

```text
Transition Table in.
One transition out.
Receipt.
Stop.
```
