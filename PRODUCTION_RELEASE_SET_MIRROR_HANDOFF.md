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
aggregate_release_set: ODA3-EVALUATOR-PATH-2026-08-18-R1
role: manifest_route_carrier
package: stegverse-core-lite
package_version: 0.9.0
target_release_tag: v0.9.0
candidate_commit: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
SDK governed-test pin matches candidate: true
current main at original handoff creation matches candidate: true
release_notes: RELEASE_NOTES_EVALUATOR_PATH_0.9.0.md
```

## Release requirements

The StegVerse worker owning release execution must:

1. verify the candidate commit with the strongest repository validation available;
2. create durable tag `v0.9.0` resolving exactly to `72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8`;
3. publish the prepared release notes/changelog describing the manifested route carrier state;
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

## Readiness evidence

Issue #15 records the release-readiness audit: this exact 0.9.0 candidate was subsequently exercised by the SDK sovereign frozen validation across the cross-repository manifested route, including 10/10 route transitions, one transaction identity, Master Records custody, replay, and reconstruction PASS. A sampled red scheduled job was attributed to post-test persistence mechanics rather than product failure.

## Current executable state

```text
SOURCE_CANDIDATE: FROZEN
RELEASE_NOTES: PREPARED
TARGET_TAG: FIXED_TO_v0.9.0
TAG_PUBLICATION: PENDING_TV_TVC_RELEASE_AUTHORITY
GITHUB_ACTIONS_RUNTIME_AUTHORITY: NONE
STATUS: RELEASE_READY_AWAITING_TAG_PUBLICATION
```
