# Core-Lite Ecosystem Maintainer Scan

Generated: `2026-07-14T05:20:02+00:00`
Target root: `/home/runner/work/core-lite/core-lite`

## Done Definition

- Scan repository files.
- Classify files by reality state.
- Detect stubs, stub dependencies, orphan candidates, and broken local references.
- Generate Markdown and JSON reports.
- Emit receipt.
- Perform no source mutation.

## Summary

- Files scanned: `127`
- Result: `pass`
- Mutations performed: `0`

## Class Counts

- BINARY_OR_UNKNOWN: `3`
- CANONICAL_OR_CONTROL: `43`
- ORPHAN_CANDIDATE: `44`
- REAL: `12`
- SUPPORT_ARTIFACT: `25`

## Recommended Next Transition Blocks

- STUB files: `AUTO_QUARANTINE_STUB` or `COMPLETE_LOW_RISK_STUB` after evidence review.
- STUB_DEPENDENT files: `MAP_DEPENDENCY`, then complete or quarantine dependency first.
- ORPHAN_CANDIDATE files: review before quarantine; do not delete automatically.
- BROKEN files: `AUTO_FIX_MECHANICAL` only when the target path is obvious.
- SUPPORT_ARTIFACT files: keep unless superseded by bundle registry policy.

## Findings

### .github/workflows/auto-fix-eligibility.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `1277` bytes
- Evidence:
  - canonical/control file

### .github/workflows/bundle-registry.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `1098` bytes
- Evidence:
  - canonical/control file

### .github/workflows/core-lite-intake.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `3941` bytes
- Evidence:
  - canonical/control file

### .github/workflows/core-lite-self-test.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `5704` bytes
- Evidence:
  - canonical/control file

### .github/workflows/ecosystem-maintainer-scan.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `1110` bytes
- Evidence:
  - canonical/control file

### .github/workflows/friction-avoided.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `1095` bytes
- Evidence:
  - canonical/control file

### .github/workflows/install-iosnoperiod.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `1784` bytes
- Evidence:
  - canonical/control file

### .github/workflows/rce-p0-001-validation.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `4310` bytes
- Evidence:
  - canonical/control file

### .github/workflows/rce-p0-002-validation.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `5119` bytes
- Evidence:
  - canonical/control file

### .github/workflows/target-capability-gap.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `2287` bytes
- Evidence:
  - canonical/control file

### .github/workflows/target-repo-scan.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `1944` bytes
- Evidence:
  - canonical/control file

### .github/workflows/workstream-status.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `3166` bytes
- Evidence:
  - canonical/control file

### .stegverse/core-lite.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1754` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### .stegverse/ingest_manifest.json

- Class: `ORPHAN_CANDIDATE`
- Size: `11294` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### BUILD_VERIFICATION.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1553` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### CONTINUITY_POLICY.md

- Class: `ORPHAN_CANDIDATE`
- Size: `788` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### README-Add.md

- Class: `ORPHAN_CANDIDATE`
- Size: `30118` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### README.md

- Class: `CANONICAL_OR_CONTROL`
- Size: `4556` bytes
- Evidence:
  - canonical/control file

### RECONSTRUCTION_POLICY.md

- Class: `ORPHAN_CANDIDATE`
- Size: `740` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### UPLOAD_MAP.txt

- Class: `SUPPORT_ARTIFACT`
- Size: `482` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### VERIFY_RESULT.txt

- Class: `SUPPORT_ARTIFACT`
- Size: `888` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### bundle_manifest.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1330` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### continuity/README.md

- Class: `CANONICAL_OR_CONTROL`
- Size: `1265` bytes
- Evidence:
  - canonical/control file

### continuity/examples/continuity_event.example.json

- Class: `ORPHAN_CANDIDATE`
- Size: `532` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### continuity/schemas/continuity_event.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1084` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### continuity/scripts/validate_continuity_event.py

- Class: `ORPHAN_CANDIDATE`
- Size: `1627` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### core_lite/__init__.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `58` bytes
- Evidence:
  - canonical/control file

### core_lite/bundle_registry.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `7179` bytes
- Evidence:
  - canonical/control file

### core_lite/cge.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `5402` bytes
- Evidence:
  - canonical/control file
- Inbound refs:
  - `core_lite/ingest.py`

### core_lite/cli.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `5235` bytes
- Evidence:
  - canonical/control file

### core_lite/context.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `1363` bytes
- Evidence:
  - canonical/control file

### core_lite/friction_events.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `5013` bytes
- Evidence:
  - canonical/control file

### core_lite/ingest.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `14642` bytes
- Evidence:
  - canonical/control file
- Inbound refs:
  - `tests/test_ingest_incoming_contract.py`

### core_lite/ingestion_transition_table.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `2136` bytes
- Evidence:
  - canonical/control file

### core_lite/iosnoperiod.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `2649` bytes
- Evidence:
  - canonical/control file

### core_lite/manifest.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `3436` bytes
- Evidence:
  - canonical/control file

### core_lite/manifest_admissibility.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `7190` bytes
- Evidence:
  - canonical/control file

### core_lite/master_hash_events.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `5501` bytes
- Evidence:
  - canonical/control file

### core_lite/paths.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `641` bytes
- Evidence:
  - canonical/control file

### core_lite/queue.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `4556` bytes
- Evidence:
  - canonical/control file

### core_lite/receipts.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `3101` bytes
- Evidence:
  - canonical/control file
- Inbound refs:
  - `core_lite/ingest.py`
  - `tests/test_receipts_append_contract.py`

### core_lite/registry.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `3803` bytes
- Evidence:
  - canonical/control file

### core_lite/sandbox.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `2406` bytes
- Evidence:
  - canonical/control file
- Inbound refs:
  - `core_lite/ingest.py`

### core_lite/shims.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `2767` bytes
- Evidence:
  - canonical/control file

### core_lite/source_state_index.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `5489` bytes
- Evidence:
  - canonical/control file

### core_lite/stegclaw_target_intake.json

- Class: `CANONICAL_OR_CONTROL`
- Size: `653` bytes
- Evidence:
  - canonical/control file

### core_lite/stegverse_002_export_manifest.json

- Class: `CANONICAL_OR_CONTROL`
- Size: `1579` bytes
- Evidence:
  - canonical/control file

### core_lite/tasks/relationship_conditioned_execution.json

- Class: `CANONICAL_OR_CONTROL`
- Size: `3772` bytes
- Evidence:
  - canonical/control file

### core_lite/tasks/relationship_conditioned_execution_p0_002.json

- Class: `CANONICAL_OR_CONTROL`
- Size: `2840` bytes
- Evidence:
  - canonical/control file

### core_lite/tasks/relationship_conditioned_execution_p0_003.json

- Class: `CANONICAL_OR_CONTROL`
- Size: `2560` bytes
- Evidence:
  - canonical/control file

### core_lite/tasks.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `2383` bytes
- Evidence:
  - canonical/control file

### core_lite/topology.py

- Class: `CANONICAL_OR_CONTROL`
- Size: `2042` bytes
- Evidence:
  - canonical/control file

### core_lite/transition_blocks.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `28617` bytes
- Evidence:
  - canonical/control file

### core_lite/workstreams.yml

- Class: `CANONICAL_OR_CONTROL`
- Size: `9894` bytes
- Evidence:
  - canonical/control file

### docs/ADVERSARIAL_AI_EXECUTION_MODEL.md

- Class: `SUPPORT_ARTIFACT`
- Size: `7574` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/CORE_LITE_MIRROR_HANDOFF.md

- Class: `SUPPORT_ARTIFACT`
- Size: `8020` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/RCE_P0_002_MANIFEST_AND_FIXTURES.md

- Class: `SUPPORT_ARTIFACT`
- Size: `3502` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/README-a001.md

- Class: `SUPPORT_ARTIFACT`
- Size: `2643` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/README.md

- Class: `CANONICAL_OR_CONTROL`
- Size: `606` bytes
- Evidence:
  - canonical/control file

### docs/RELATIONSHIP_CONDITIONED_EXECUTION_HANDOFF.md

- Class: `SUPPORT_ARTIFACT`
- Size: `6395` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/RELATIONSHIP_CONDITIONED_HUMAN_DECISION_POLICY.md

- Class: `SUPPORT_ARTIFACT`
- Size: `6389` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/STEGCLAW_TARGET_INTAKE.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1210` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/bundles/CORE_LITE_INGEST_REPO_ROOT_FIX.md

- Class: `SUPPORT_ARTIFACT`
- Size: `2068` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/bundles/CORE_LITE_RECEIPT_ACTOR_FIX.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1851` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/bundles/core-lite-recorded-ingestion-cge-sandbox-loop-README.md

- Class: `SUPPORT_ARTIFACT`
- Size: `2747` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/bundles/stegverse-001-worker-instruction-channel-README.md

- Class: `SUPPORT_ARTIFACT`
- Size: `2273` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-empty-repo-install-v0.9.0.md

- Class: `SUPPORT_ARTIFACT`
- Size: `927` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.2-org-topology-cge.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1177` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.3-bundle-queue-protocol.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1538` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.4-ingestion-transition-table.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1089` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.5-iosnoperiod-bridge.md

- Class: `SUPPORT_ARTIFACT`
- Size: `740` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.6-executable-ingestion-transitions.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1147` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.7-manifest-admissibility-enforcement.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1394` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.7.1-wire-manifest-admissibility.md

- Class: `SUPPORT_ARTIFACT`
- Size: `1048` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.8-source-state-index.md

- Class: `SUPPORT_ARTIFACT`
- Size: `782` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/core-lite-v0.8.1-wire-source-state-index.md

- Class: `SUPPORT_ARTIFACT`
- Size: `752` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### docs/iosnoperiod.md

- Class: `SUPPORT_ARTIFACT`
- Size: `831` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### entity-architecture.json

- Class: `ORPHAN_CANDIDATE`
- Size: `5697` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### incoming/.gitkeep

- Class: `SUPPORT_ARTIFACT`
- Size: `1` bytes
- Evidence:
  - support artifact for upload, verification, documentation, examples, or empty directory retention

### ingest_manifest.json

- Class: `ORPHAN_CANDIDATE`
- Size: `2355` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### instructions/current/stegverse-001-command.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1557` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### path_mappings.json

- Class: `ORPHAN_CANDIDATE`
- Size: `283` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### samples/execution_candidate_manifest.allow.example.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1237` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### samples/execution_candidate_manifest.scope_leakage.example.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1253` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### samples/execution_candidate_manifest.stale_state.example.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1222` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### samples/relationship_conditioned_human_decision_policy.example.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1500` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/bundle_queue_metadata.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `130` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/cge_fingerprint.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `234` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/execution_candidate_manifest.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `3860` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/hash_identity_types.json

- Class: `ORPHAN_CANDIDATE`
- Size: `770` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/ingest_bundle.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1071` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/ingest_manifest.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `207` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/ingestion_transition_table.json

- Class: `ORPHAN_CANDIDATE`
- Size: `3034` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/ingestion_transition_table.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `226` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/manifest_admissibility_policy.json

- Class: `ORPHAN_CANDIDATE`
- Size: `2673` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/manifest_admissibility_policy.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `264` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/master_hash_event.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `295` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/relationship_conditioned_human_decision_policy.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `4786` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/source_state_index.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `231` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/stegverse_worker_instruction.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `996` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/task_manifest.schema.json

- Class: `ORPHAN_CANDIDATE`
- Size: `155` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### schemas/validation_rules.json

- Class: `ORPHAN_CANDIDATE`
- Size: `226` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### templates/core-lite-intake.yml

- Class: `ORPHAN_CANDIDATE`
- Size: `1884` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### templates/core-lite.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1699` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### templates/install-iosnoperiod.yml

- Class: `ORPHAN_CANDIDATE`
- Size: `1784` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### tests/fixtures/sample_ingest_bundle/bundle_manifest.json

- Class: `ORPHAN_CANDIDATE`
- Size: `420` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### tests/fixtures/sample_ingest_bundle/payload/sample.txt

- Class: `ORPHAN_CANDIDATE`
- Size: `189` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### tests/test_execution_candidate_manifest.py

- Class: `ORPHAN_CANDIDATE`
- Size: `2688` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### tests/test_ingest_incoming_contract.py

- Class: `ORPHAN_CANDIDATE`
- Size: `2257` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### tests/test_receipts_append_contract.py

- Class: `ORPHAN_CANDIDATE`
- Size: `1819` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### tests/test_relationship_conditioned_human_decision_policy.py

- Class: `ORPHAN_CANDIDATE`
- Size: `3150` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

### verification.json

- Class: `ORPHAN_CANDIDATE`
- Size: `1856` bytes
- Evidence:
  - text file with no stub or broken-reference signal
  - no inbound references found in scanned text files

## Receipt

- Receipt hash: `da2246d86d51b02c183745b4c2275b02bf8f561d637724d8d8edecd524819bb9`
- Receipt path: `receipts/ecosystem_maintainer_receipts.jsonl`
