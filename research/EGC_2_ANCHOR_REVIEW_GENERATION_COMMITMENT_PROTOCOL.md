# EGC 2.0 — Anchor Review Generation Commitment Protocol

**Status:** Focused engineering control validated; no live ceremony executed  
**Date:** 2026-07-27  
**Scope:** Future generation of the three target-blind expert-review queues for the first 24 synthetic anchor packets

## Decision

The anchor-review pipeline had artifact-level digests and cross-artifact lineage checks, but it did not yet define a safe public record for the live queue-generation event.

A live run requires a secret seed and a protected mapping from opaque presentation IDs to source anchors. Neither may be committed. At the same time, the project needs evidence that the queues were generated from a predeclared manifest, code revision, reviewer pseudonym set, and seed commitment rather than regenerated opportunistically after inspecting outputs.

The new two-phase protocol records that evidence without storing the seed, private nonce, protected mapping, reviewer names, reviewer emails, item text, source anchor IDs, constructor targets, or reviewer content.

## Phase 1 — pre-generation commitment

Before queue generation, create a precommit containing only:

- ceremony ID;
- repository identity;
- exact 40-character code commit SHA;
- source manifest ID and SHA-256 digest;
- sorted opaque reviewer pseudonyms;
- a domain-separated seed commitment;
- operator pseudonym;
- UTC creation time;
- explicit claim limit.

The seed commitment is:

```text
SHA256("egc2-anchor-review-seed-v0.1" || ceremony_id || secret_seed || private_nonce)
```

The live seed and private nonce remain outside the public record. The commitment allows later controlled verification if disclosure becomes appropriate, but it does not require disclosure and does not prove that the seed was generated randomly.

## Phase 2 — post-generation commitment

After generation, create a postcommit bound to the precommit. It records:

- the precommit digest;
- the same ceremony, manifest, code revision, and reviewer set;
- one public queue digest for every predeclared reviewer;
- the protected-bundle digest, but not its content;
- generator and Python versions;
- UTC generation time;
- optional witness pseudonyms;
- a review-run commitment over the precommit, queue digests, and protected-bundle digest.

The reviewer set must match exactly. Missing, substituted, or additional queues fail closed.

## Forbidden public material

The validator recursively rejects fields named as secret or protected material, including:

- seed or nonce;
- protected mapping;
- reviewer name or email;
- source anchor ID;
- contrast-group ID;
- constructor target;
- candidate response;
- private intention map.

This is a defense against accidental disclosure, not a complete information-flow proof. Sensitive content hidden under an unexpected field name could still evade a key-name denylist. Operational review remains required.

## Tamper and rebinding controls

The focused tests verify rejection of:

1. secret seed material added and fully redigested;
2. reviewer email material added and fully redigested;
3. a missing reviewer queue after recomputing the run and postcommit digests;
4. cross-ceremony rebinding;
5. protected source-mapping leakage.

The controls detect internal inconsistency and prohibited fields. They do not authenticate the operator, reviewer, or witness; prove timestamp accuracy; establish randomness; or prevent an administrator from creating an entirely new ceremony.

## Validation

Commands executed in an isolated local harness:

```text
python -m unittest -v test_anchor_review_generation_commitment.py
python -m py_compile anchor_review_generation_commitment.py test_anchor_review_generation_commitment.py
```

Result:

```text
8 tests passed
0 tests failed
py_compile passed
```

The validation artifact is:

`research/egc2/results/anchor_review_generation_commitment_validation.v0.1.json`

## CI observability finding

The dedicated committed-manifest workflow still has no observable result through the available connector interfaces:

- combined commit status returns no statuses;
- the available workflow-run action is restricted to pull-request-triggered runs;
- an empty result therefore cannot be interpreted as either a pass or a failure.

This is an observability limitation, not evidence that GitHub Actions malfunctioned. The live ceremony remains blocked until the committed-manifest integration gate is executed in an environment that can preserve its result.

## Permitted conclusions

Supported as focused engineering evidence:

- a live generation event can be precommitted without publishing its seed;
- the post-generation record can bind the exact reviewer set, queue digests, and protected-bundle digest;
- fully redigested cross-ceremony and reviewer-set mismatches can fail closed;
- common secret, identity, source-mapping, and item-content fields are prohibited from commitment records.

Not supported:

- that the committed manifest passes the full integration workflow;
- that a live seed or queue has been generated;
- that any timestamp, witness, operator, or reviewer identity is authenticated;
- that the seed is random or was not reused;
- that any anchor is valid;
- that semantic fidelity, EGC, subjectivity, hidden intention, or consciousness is measured or established.

## Highest-leverage next action

Execute the committed-manifest integration test in a repository-capable environment and preserve the exact pass or failure. Only after a pass should the first live precommit be created and the protected queue-generation ceremony run.
