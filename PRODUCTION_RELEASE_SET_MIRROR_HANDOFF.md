# Production Release Set Mirror Handoff

## Source of truth

```text
organization: Data-Continuation
repository: core-lite
canonical_branch: main
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
```

## Goal

Create a durable tagged/released production-lane state for evaluator provenance. Ongoing development must not change the identity of that released state.

## Validated release candidate

```text
role: manifest_route_carrier
package: stegverse-core-lite
package_version: 0.9.0
candidate_commit: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
SDK governed-test pin matches candidate: true
current main at handoff creation matches candidate: true
current GitHub releases: none
```

## Release requirements

The StegVerse worker owning release execution must:

1. verify the candidate commit with the strongest repository validation available;
2. create a durable release tag that resolves exactly to `72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8`;
3. publish release notes/changelog describing the manifested route carrier state;
4. record tag, immutable commit SHA, package version, publication time, release URL, and changelog URL;
5. propagate the completed release identity to `StegVerse-org/StegVerse-SDK` production release catalog/packet contract;
6. continue subsequent development without moving or reusing the released tag.

## Evaluator invariant

```text
release tag != moving branch
released commit is immutable evidence
future main changes do not rewrite prior evaluator runs
replay/reconstruction must retain the original release identity
```

## Remaining executable work

```text
OWNER: StegVerse release worker / TV-TVC governed release authority
TASK: validate candidate, tag, publish release/changelog, propagate receipt to SDK
STATUS: READY_FOR_RELEASE_EXECUTION
```
