# EGC 2.0 — Committed-Manifest Anchor Review Integration Gate

**Status:** Integration test and CI gate committed; CI result not yet observed  
**Date:** 2026-07-27  
**Scope:** Actual `anchor_development_manifest.v0.1.json` with review hardening v0.2 and lineage validation

## Decision

The prior focused tests used self-contained fixtures matching the intended 24-packet structure. That was useful engineering evidence but did not establish compatibility with the actual committed anchor manifest.

A repository-native integration test now loads the committed manifest and exercises the real chain:

1. validate the committed anchor manifest;
2. generate three reviewer-specific v0.2 queue/key artifacts using an explicitly test-only seed;
3. verify opaque reviewer-facing IDs and absence of source anchor IDs;
4. verify exact twelve-position pair separation;
5. verify four items from each domain in each queue half;
6. generate clearly labeled synthetic locked submissions for integration testing only;
7. validate each synthetic submission;
8. validate complete manifest–queue–protected-key–submission lineage;
9. produce a 64-character review-run commitment.

The synthetic submissions are software fixtures, not expert judgments, pilot data, or scientific evidence.

## Added artifacts

- `research/egc2/test_anchor_review_committed_manifest_integration.py`
- `.github/workflows/egc-anchor-review-integration.yml`

## CI contract

The workflow compiles and tests:

- `validate_anchor_development_manifest.py`;
- `harden_anchor_expert_review.py`;
- `validate_anchor_review_lineage.py`;
- the committed-manifest integration test.

It runs when the committed manifest, any of the three pipeline modules, the integration test, or the workflow itself changes. This turns future source-manifest or pipeline drift into a visible repository failure rather than a latent incompatibility.

## Evidence currently supported

- The repository now contains an executable test that targets the actual committed manifest rather than a structurally similar fixture.
- The test asserts the main privacy, pairing, domain-balance, submission, and lineage invariants required before live reviewer distribution.
- The workflow is configured to rerun the integration test when relevant artifacts change.

## Evidence not yet supported

At the time of this commit, the GitHub status endpoint returned no completed status for the workflow commit. Therefore this document does **not** claim:

- that GitHub Actions executed successfully;
- that the committed manifest currently passes the new integration test;
- that live reviewer queues were generated or frozen;
- that a protected live seed exists;
- that any reviewer was recruited;
- that any expert score or anchor is valid.

## Failure handling

Any CI failure must be preserved. A failing integration test means live queue generation remains blocked until the exact incompatibility is fixed and the workflow passes. It must not be bypassed by reverting to the deprecated v0.1 review path or by publishing test-only queue artifacts.

## Claim status

```text
measurement_process_not_yet_empirically_validated
committed_manifest_integration_ci_pending
```

## Highest-leverage next action

Observe the repository CI result for the committed-manifest integration workflow. If it fails, fix the exact incompatibility. If it passes, generate the real reviewer queues once with a protected non-public seed, retain only their public queue digests and protected-bundle commitment in the audit log, and begin independent reviewer recruitment.
