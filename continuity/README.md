# Data-Continuation Continuity Layer

## Purpose

This directory defines the minimum continuity contract for the Data-Continuation core-lite repo.

The continuity layer records whether a transition, intake, review, or evidence packet can be reconstructed from declared artifacts. It is not an identity system, a consent system, or a replacement for commit-time governance.

## Done criteria

This continuity layer is initially installed when the repo contains:

1. a continuity event schema;
2. a minimal continuity event example;
3. a validator script;
4. explicit policy notes for continuity, reconstruction, and quarantine;
5. a bundle manifest that names the installed continuity files.

## Boundary

A continuity event may say that an artifact was observed, hashed, classified, routed, or quarantined.

A continuity event must not claim broad authority, user consent, or final admissibility unless a separate commit-time governance artifact explicitly supports that claim.

## Expected paths

```text
continuity/README.md
continuity/schemas/continuity_event.schema.json
continuity/examples/continuity_event.example.json
continuity/scripts/validate_continuity_event.py
CONTINUITY_POLICY.md
RECONSTRUCTION_POLICY.md
QUARANTINE_POLICY.md
bundle_manifest.json
```
