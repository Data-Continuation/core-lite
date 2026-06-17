# Continuity Policy

## Purpose

This policy defines the baseline continuity rule for Data-Continuation/core-lite.

Continuity means the system can identify the declared artifact, source path, hash, event type, timestamp, and disposition for a transition-related event.

## Policy

Every continuity event should include:

- schema name;
- event id;
- event type;
- source path;
- source hash;
- timestamp in UTC;
- actor or system component;
- disposition;
- evidence reference.

## Non-claims

A continuity event is not proof of user consent, policy authority, identity truth, or final admissibility.

## Failure mode

If the event cannot be reconstructed from declared fields, the event should be treated as incomplete and routed to review or quarantine according to repo-local policy.
