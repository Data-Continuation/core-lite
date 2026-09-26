# Exact pinned-source rights remediation — evidence and owner decision form

Parent task: `ECOSYSTEM-OPEN-SOURCE-STRATEGY-001`; COSV `20010010100000`. Source-owned tracking: [#34](https://github.com/Data-Continuation/core-lite/issues/34). No separate Goal Task ID or execution authority is created.

## Immutable scope

SDK consumer: `StegVerse-org/StegVerse-SDK`, `governed-test` extra. Exact source pin: `72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8`. The [source-owned 2026-09-25 audit](https://github.com/Data-Continuation/.github/blob/main/docs/CORE_LITE_PINNED_SOURCE_RIGHTS_AUDIT_20260925.md) reports a complete 335-entry nontruncated pinned tree, no root LICENSE/NOTICE, and 351 reachable commit attribution records (336 StegVerse; 14 Core-Lite Manager; 1 Actions bot). Attribution cannot prove copyright title or consent. No rights-holder approval has been produced.

Independently re-read [exact pinned pyproject](https://github.com/Data-Continuation/core-lite/blob/72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8/pyproject.toml) (blob `3ba3dcc4f89f56613147ceae66bc1cc3695ca729`): `stegverse-core-lite` v0.9.0; `requires-python >=3.11`; build `setuptools>=68`; no `license` field and no declared runtime dependencies. The current [SDK pyproject](https://github.com/StegVerse-org/StegVerse-SDK/blob/main/pyproject.toml) retains `requires-python >=3.9` and the exact Core-Lite pin in its optional `governed-test` extra. Earlier audit inspected 20 package module top-level imports; delayed imports, source-file origin, build tooling and test dependencies remain unexamined.

## Required evidence and precise dispositions

| Predicate | Current disposition | Evidence needed for correction |
| --- | --- | --- |
| Exact file/version license scope | `DENY:SOURCE_LICENSE_SCOPE_UNVERIFIED` | Source-owning maintainer records all relevant file headers, historical grants, imported-source licenses and the affected version/commit; authorized actual rights holder approves written exact-scope grant or documented existing grant. |
| Contributor ownership chain | `DENY:CONTRIBUTOR_CHAIN_UNVERIFIED` | Per-file original source/commit provenance, coauthor trailers, any external imports and generated content, manager/bot provenance, and attested permissions or assignments from each relevant holder. |
| Dependency provenance | `DENY:DEPENDENCY_PROVENANCE_PARTIAL` | Pinned-version file/content SBOM including setuptools, vendored/generated code, lazy imports, scripts, tests, optional extras and compatible distribution rights; reproducible consumer build result. |
| Optional Python eligibility | `DENY:OPTIONAL_PYTHON_COMPATIBILITY_REVIEW` | SDK-owned CI that preserves Python >=3.9 base installation and documents/tests >=3.11 for this optional extra, without silently changing pins. |
| Publication | `DENY:RELEASE_NOT_AUTHORIZED` | Separate recorded owner clearance, applicable legal review, protected exact-head checks and governed publication evidence; GitHub visibility alone never suffices. |

## Rights-holder evidence intake (blank until independently established)

- Actual rights-holder identity and basis of authority: **UNVERIFIED**.
- Signed or otherwise independently verifiable permission/assignment instrument, immutable reference and exact files/versions: **NOT PROVIDED**.
- Excluded third-party files or historical grants requiring preservation: **NOT YET ENUMERATED**.
- Independent reviewing owner, reviewed exact source commit and decision receipt: **NONE RECORDED**.
- InTr authorization / Master Records closure / release receipt: **NONE RECORDED**.

The repository owner can collect and verify evidence through existing authorized interfaces and append source-linked findings to issue #34. Never paste private agreements, personal identity documents, or nonpublic repository names into public evidence. Record a restricted evidence reference and minimal public disposition when confidentiality requires it. A failed or missing predicate should return its first explicit non-ALLOW result and next correction, not a fabricated approval.

This document changes no source license, dependencies, distribution policy, runtime execution or governance authority. Update this report, `README.md` and `CORE_LITE_MIRROR_HANDOFF.md` together upon any source-owned finding, then return only independently verified public-safe dispositions to Data-Continuation organization inventory and the central task handoff.
