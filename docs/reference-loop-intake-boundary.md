# Reference Loop Intake Boundary Expansion

`REF-LOOP-003` is the first responsibility added after the repository-local closure proof and repository scan.

It remains local to `Data-Continuation/core-lite` and validates the existing StegClaw intake boundary twice: once as execution and once as independent verification.

It does not authorize external repository mutation, production mutation, package installation, downstream publication, or policy derivation from command output.

Activation is dependency-gated:

```text
REF-LOOP-001 complete
-> REF-LOOP-002 scan and eligibility closure
-> REF-LOOP-003 intake-boundary verification
```

This task prepares the reference loop to monitor an input contract without granting it authority over the originating or destination repository.
