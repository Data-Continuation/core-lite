# Evaluator Path Release Notes — stegverse-core-lite 0.9.0

Release-set role: `manifest_route_carrier`

Canonical evaluator candidate:

```text
repository: Data-Continuation/core-lite
package: stegverse-core-lite
version: 0.9.0
tag_to_publish: v0.9.0
commit: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
```

This historical release candidate is the manifested route-carrier state pinned by the StegVerse SDK governed evaluator lane. It provides receipt-gated route progression, transaction identity continuity, execution-provenance binding, heartbeat carrier state, and fail-closed advancement when prior Master Records custody is absent.

Cross-repository retained validation subsequently exercised the candidate in the sovereign SDK production-validation route with all declared route transitions, one transaction identity, Master Records custody, replay, and reconstruction evidence retained. Later `main` development does not alter the identity of this candidate.

## Release invariant

`v0.9.0` must resolve exactly to `72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8`. Do not move or reuse the tag. A later Core-Lite state requires a later distinct release.

Aggregate release-set identity: `ODA3-EVALUATOR-PATH-2026-08-18-R1`.

This note prepares release metadata only; GitHub source control and CI do not become runtime, control-plane, or credential authority.