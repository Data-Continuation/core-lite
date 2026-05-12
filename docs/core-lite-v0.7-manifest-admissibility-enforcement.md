# Core-Lite v0.7: Manifest Admissibility Enforcement

## Purpose

Core-Lite v0.7 makes bundle manifests admissibility-checked before install action.

## Core rule

```text
Manifest declares requested processing.
Core-lite policy decides admissible processing.
```

## Enforced checks

```text
entrypoint class
source type
parent_event_hash when required
priority authority
scoped ALLOW authority
iosnoperiod completeness
```

## Scoped ALLOW values

```text
ALLOW_OBSERVE
ALLOW_QUEUE
ALLOW_ROUTE
ALLOW_INSTALL
ALLOW_CONFIRM
ALLOW_PROMOTE
ALLOW_RELEASE_PAYLOAD
ALLOW_QUARANTINE
ALLOW_REPAIR_CANDIDATE
```

## SDK and Sandbox

SDK and sandbox outputs are source-known entrypoints, not generic quarantine items.

They may enter the same ingestion path as other artifacts, but missing event/hash/authority requirements produce quarantine as a mild failure outcome rather than direct install.

## iOS bundle standard

Any canonical path with a leading period must have:

```text
iosnoperiod mirror file
iosnoperiod.md
manifest iosnoperiod_mappings entry
```

Example:

```text
.github/workflows/core-lite-intake.yml
iosnoperiod/github/workflows/core-lite-intake.yml
```

## New files

```text
core_lite/manifest_admissibility.py
schemas/manifest_admissibility_policy.json
schemas/manifest_admissibility_policy.schema.json
docs/core-lite-v0.7-manifest-admissibility-enforcement.md
iosnoperiod.md
```
