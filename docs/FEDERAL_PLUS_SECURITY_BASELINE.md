# Federal-Plus Security Baseline

## Status

```text
profile_id: core-lite-federal-plus-v1
status: IMPLEMENTED_PENDING_VALIDATION
scope: evidence-intake source, workflows, receipts, and public-safe fixtures
compliance_claim: NONE
```

## Governing rule

Applicable United States federal cybersecurity requirements are the minimum floor, not the target ceiling. This repository must fail closed when it cannot demonstrate the controls required by its selected profile. A passing repository-local validator does not itself establish FISMA, FedRAMP, agency ATO, legal compliance, deployment authorization, or production security.

## Authoritative baseline references

- NIST SP 800-53 Rev. 5, including the current Release 5.2.0 control catalog.
- NIST SP 800-218, Secure Software Development Framework Version 1.1.
- FIPS 140-3 for cryptographic modules where cryptographic protection is deployed in a federal or equivalent assurance context.
- CISA Secure by Design principles as a product-security posture.

The machine profile records exact reference identifiers and review dates. Changes to those references require review rather than silent acceptance.

## Mandatory floor controls

1. Least privilege for repository, workflow, artifact, and deployment credentials.
2. Phishing-resistant multi-factor authentication for privileged operators where the hosting platform supports it.
3. No long-lived secrets in source, fixtures, logs, receipts, or workflow output.
4. Encryption in transit and at rest for private evidence and operational secrets.
5. FIPS-validated cryptographic modules where required by the deployment or federal assurance boundary.
6. Immutable or append-only security-relevant audit evidence with identity, action, target, outcome, and ordering.
7. Protected branches, reviewed changes, status checks, and separation of implementation from approval.
8. Dependency pinning, vulnerability review, provenance, and software bill of materials for release artifacts.
9. Deterministic tests for privacy leakage, unsupported conclusions, malformed input, and claim-posture escalation.
10. Incident-response ownership, revocation path, and recovery evidence.
11. Backups and restore tests for authoritative handoffs, receipts, and private evidence custody.
12. Data minimization, explicit retention, deletion authority, and public/private classification.

## Controls that exceed the floor

The `federal_plus` profile additionally requires:

- deterministic canonicalization and content digests for governed inputs and receipts;
- hash-linked or otherwise tamper-evident receipt continuity;
- explicit non-authority fields proving that validation cannot mint legal, safety, recall, or execution authority;
- dual classification of evidence truth state and publication/privacy state;
- negative fixtures that prove the gate rejects privacy leakage and unsupported conclusions;
- no automatic posture elevation from `POTENTIAL` to `SUPPORTED` or from unverified material to verified fact;
- independent reproduction before release readiness;
- machine-observable claim ownership and expiration/release conditions;
- fail-closed behavior when required security evidence is missing, stale, contradictory, or inaccessible;
- post-merge current-main validation before release or downstream propagation;
- downstream handoff review before Site, Publisher, wiki, Master Records, or deployment mutation.

## Repository implementation

```text
schemas/security_profile.schema.json
fixtures/security_profile.federal_plus.json
tools/validate_security_profile.py
tests/test_security_profile.py
claims/security-hardening.claim.json
.github/workflows/security-profile-verify.yml
```

## Release boundary

Release remains blocked until the security profile passes on the exact target commit, its receipt or job evidence is inspected, branch and review requirements are satisfied, and the canonical handoff records the result. Deployment requires a separate deployment-specific control assessment and authority record.