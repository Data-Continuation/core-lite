# Reconstruction Policy

## Purpose

This policy defines when a Data-Continuation event is reconstructable.

An event is reconstructable when a reviewer can identify what was observed, where it came from, when it was recorded, how it was hashed, what disposition was assigned, and where supporting evidence is stored.

## Minimum reconstruction fields

- `event_id`
- `event_type`
- `source_path`
- `source_sha256`
- `created_at_utc`
- `actor`
- `disposition`
- `evidence_ref`

## Review rule

If any minimum field is missing, the event is not reconstructable enough for automated reliance.

## Boundary

Reconstructability supports review. It does not by itself prove that the original transition was authorized, consented, or admissible.
