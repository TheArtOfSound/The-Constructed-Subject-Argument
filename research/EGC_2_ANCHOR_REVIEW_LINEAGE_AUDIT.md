# EGC 2.0 Anchor Review Cross-Artifact Lineage Audit

**Status:** Focused engineering control added; real review execution still pending  
**Date:** 2026-07-27

## Decision

The v0.2 review path hardened individual queues, keys, submissions, and aggregates, but individual digest validity was not sufficient to prove that every artifact belonged to the same review run.

A malicious or accidental recombination could preserve internally valid digests while mixing:

- a protected bundle from another manifest;
- only a subset of assigned reviewers;
- a queue rebound to another source digest;
- a protected key that duplicated one anchor and omitted another;
- a redigested submission with reordered review rows;
- an inadequate-reference suppression without a map-inadequacy reason.

`research/egc2/validate_anchor_review_lineage.py` now fails closed on those conditions.

## Controls added

The validator requires exact agreement across:

1. source manifest ID and content digest;
2. reviewer sets in public queues, protected keys, and locked submissions;
3. queue schema, digest, reviewer, source manifest, and source digest;
4. protected-key schema, digest, queue digest, source digest, order, and complete one-to-one anchor mapping;
5. submission schema, digest, queue digest, manifest identity, reviewer identity, lock declarations, and exact review order;
6. map-inadequacy reason codes whenever a numeric score is suppressed.

After a valid run, it creates a single `review_run_commitment_sha256` over the manifest, reviewer set, all queue digests, the protected-bundle digest, and all submission digests.

This commitment is a reproducibility anchor. It is not identity authentication or a trusted timestamp.

## Focused validation

Commands:

```bash
python -m unittest -v test_validate_anchor_review_lineage.py
python -m py_compile validate_anchor_review_lineage.py test_validate_anchor_review_lineage.py
```

Result:

- 8 tests passed;
- 0 tests failed;
- Python compilation passed.

The adversarial tests include cases in which altered artifacts are fully redigested. They therefore test cross-artifact identity, not only detection of stale hash fields.

## Supported claim

The review workflow now has an explicit fail-closed method for determining whether the manifest, queues, protected mapping, reviewer set, and submissions form one complete internally consistent review run.

## Claims not supported

This does not establish:

- reviewer identity;
- reviewer independence;
- trusted or externally witnessed lock time;
- correctness of reviewer judgments;
- validity of any anchor;
- validity of the seven-point scale;
- validity of semantic fidelity as measured;
- transfer to ordinary raters or participant material.

## Preserved blocker

Direct cloning of the repository failed because the execution environment could not resolve `github.com`. The focused test suite ran against a self-contained contract-matching fixture, not the committed 24-packet manifest and generated real reviewer queues.

## Highest-leverage next action

Run the v0.2 queue generator and the new lineage validator against the committed 24-packet manifest in a repository-capable environment, then freeze the resulting queue and protected-bundle commitments before recruiting reviewers.
