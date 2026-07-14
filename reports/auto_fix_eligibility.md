# Core-Lite Auto-Fix Eligibility Plan

Generated: `2026-07-14T05:18:28+00:00`
Source scan generated: `2026-07-14T05:18:28+00:00`

## Done Definition

- Read latest ecosystem maintainer scan.
- Classify files into next safe transition buckets.
- Generate Markdown and JSON reports.
- Emit receipt.
- Perform no source mutation.

## Summary

- Result: `pass`
- Files evaluated: `125`
- Mutations performed: `0`

## Bucket Counts

- DO_NOT_TOUCH: `41`
- HUMAN_REVIEW_REQUIRED: `47`
- NO_ACTION: `37`

## Transition Block Counts

- ASK_BOUNDARY_DECISION: `44`
- AUTO_QUARANTINE_STUB: `44`

## Decisions

### .github/workflows/auto-fix-eligibility.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/bundle-registry.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/core-lite-intake.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/core-lite-self-test.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/ecosystem-maintainer-scan.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/friction-avoided.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/install-iosnoperiod.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/rce-p0-001-validation.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/target-capability-gap.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/target-repo-scan.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .github/workflows/workstream-status.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### .stegverse/core-lite-json

- Source class: `BINARY_OR_UNKNOWN`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: unrecognized or unsupported class: BINARY_OR_UNKNOWN

### .stegverse/core-lite.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### .stegverse/ingest_manifest-json

- Source class: `BINARY_OR_UNKNOWN`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: unrecognized or unsupported class: BINARY_OR_UNKNOWN

### .stegverse/ingest_manifest.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### BUILD_VERIFICATION.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### CONTINUITY_POLICY.md

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### README-Add.md

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### README.md

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### RECONSTRUCTION_POLICY.md

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### UPLOAD_MAP.txt

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### VERIFY_RESULT.txt

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### bundle_manifest.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### continuity/README.md

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### continuity/examples/continuity_event.example.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### continuity/schemas/continuity_event.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### continuity/scripts/validate_continuity_event.py

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### core_lite/__init__.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/bundle_registry.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/cge.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/cli.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/context.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/friction_events.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/ingest.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/ingestion_transition_table.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/iosnoperiod.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/manifest.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/manifest_admissibility.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/master_hash_events.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/paths.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/queue.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/receipts.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/registry.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/sandbox.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/shims.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/source_state_index.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/stegclaw_target_intake.json

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/stegverse_002_export_manifest.json

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/tasks/relationship_conditioned_execution.json

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/tasks/relationship_conditioned_execution_p0_002.json

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/tasks.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/topology.py

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/transition_blocks.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### core_lite/workstreams.yml

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### docs/ADVERSARIAL_AI_EXECUTION_MODEL.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/CORE_LITE_MIRROR_HANDOFF.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/README-a001.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/README.md

- Source class: `CANONICAL_OR_CONTROL`
- Recommended bucket: `DO_NOT_TOUCH`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: canonical/control file requires explicit boundary review before mutation

### docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/STEGCLAW_TARGET_INTAKE.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/bundles/CORE_LITE_INGEST_REPO_ROOT_FIX.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/bundles/CORE_LITE_RECEIPT_ACTOR_FIX.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/bundles/core-lite-recorded-ingestion-cge-sandbox-loop-README.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/bundles/stegverse-001-worker-instruction-channel-README.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-empty-repo-install-v0.9.0.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.2-org-topology-cge.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.3-bundle-queue-protocol.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.4-ingestion-transition-table.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.5-iosnoperiod-bridge.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.6-executable-ingestion-transitions.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.7-manifest-admissibility-enforcement.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.7.1-wire-manifest-admissibility.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.8-source-state-index.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/core-lite-v0.8.1-wire-source-state-index.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### docs/iosnoperiod.md

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### entity-architecture.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### incoming/.gitkeep

- Source class: `SUPPORT_ARTIFACT`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: support artifact should be kept unless superseded by bundle registry policy

### incoming/core-lite-v0.9.1-self-test-mock-shim-fix-bundle.zip

- Source class: `BINARY_OR_UNKNOWN`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `ASK_BOUNDARY_DECISION`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: unrecognized or unsupported class: BINARY_OR_UNKNOWN

### ingest_manifest.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### instructions/current/stegverse-001-command.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### path_mappings.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### samples/execution_candidate_manifest.allow.example.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### samples/execution_candidate_manifest.scope_leakage.example.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### samples/execution_candidate_manifest.stale_state.example.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### samples/relationship_conditioned_human_decision_policy.example.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/bundle_queue_metadata.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/cge_fingerprint.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/execution_candidate_manifest.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/hash_identity_types.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/ingest_bundle.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/ingest_manifest.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/ingestion_transition_table.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/ingestion_transition_table.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/manifest_admissibility_policy.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/manifest_admissibility_policy.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/master_hash_event.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/relationship_conditioned_human_decision_policy.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/source_state_index.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/stegverse_worker_instruction.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/task_manifest.schema.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### schemas/validation_rules.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### templates/core-lite-intake.yml

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### templates/core-lite.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### templates/install-iosnoperiod.yml

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tests/fixtures/sample_ingest_bundle/bundle_manifest.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tests/fixtures/sample_ingest_bundle/payload/sample.txt

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tests/test_execution_candidate_manifest.py

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tests/test_ingest_incoming_contract.py

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tests/test_receipts_append_contract.py

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tests/test_relationship_conditioned_human_decision_policy.py

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

### tools/auto_fix_eligibility.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/bundle_registry_report.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/capability_gap_plan.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/ecosystem_maintainer.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/measure_friction.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/stegverse001_worker.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/tasks/core_lite_tasks.json

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/validate_execution_candidate_manifest.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/validate_relationship_conditioned_human_decision_policy.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/validate_stegclaw_intake.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/validate_stegverse_002_export.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### tools/validate_workstreams.py

- Source class: `REAL`
- Recommended bucket: `NO_ACTION`
- Recommended transition block: `None`
- Mutation allowed now: `False`
- Requires human review: `False`
- Reason: real file with no maintainer finding

### verification.json

- Source class: `ORPHAN_CANDIDATE`
- Recommended bucket: `HUMAN_REVIEW_REQUIRED`
- Recommended transition block: `AUTO_QUARANTINE_STUB`
- Mutation allowed now: `False`
- Requires human review: `True`
- Reason: orphan candidates are not auto-quarantined without review

## Receipt

- Receipt hash: `281d24d8a51f256ce19cf43a3a5ee702fdb5a9756d736abb3f0966077c62ffd9`
- Receipt path: `receipts/auto_fix_eligibility_receipts.jsonl`
