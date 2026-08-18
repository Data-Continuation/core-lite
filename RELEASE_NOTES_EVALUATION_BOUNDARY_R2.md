# Core-Lite 0.9.0 — Evaluation Boundary R2

This release candidate is a release-note-only successor to source commit `72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8` for the immutable evaluation-boundary aggregate test set.

## Included source

The executable source is unchanged from the pinned Core-Lite candidate. It provides the manifested route-carrier behavior used by the generalized StegVerse SDK governed path.

## Release-boundary invariant

This commit adds only this release note. It does not alter route semantics, governance authority, receipt authority, custody authority, runtime authority, or execution behavior. The source-parent relationship must be verified before publication.

## Authority boundary

Credential and release authority remain TV/TVC. GitHub Actions, generic GitHub tokens, moving branches, and third-party runtime providers are not release or production authority.

## Aggregate-run requirement

The exact governed evaluation run must not begin until this component tag, every other component tag in the aggregate set, all release objects, and the retained TVC aggregate-release receipt have been verified against their frozen commits.
