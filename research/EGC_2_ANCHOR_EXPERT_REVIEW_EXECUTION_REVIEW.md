# EGC 2.0 — Anchor Expert-Review Execution Review

**Status:** Engineering implementation committed; runtime validation still required  
**Date:** 2026-07-27  
**Scope:** First 24 synthetic semantic-fidelity development packets

## Decision

The first-tranche anchor review is now operationally specified and machine-enforceable rather than depending on informal document exchange.

The implementation closes four concrete weaknesses:

1. paired contrast items could appear adjacent and reveal the manipulation;
2. reviewer submissions were not cryptographically bound to a specific queue and source manifest;
3. constructor targets could be joined before blind judgments were locked;
4. the prior architecture forced a numerical score even when the intention map was judged unusable.

It does not create expert evidence. No reviewer has been recruited and no submission exists.

## Implementation

### Reviewer-specific queues

`research/egc2/prepare_anchor_expert_review.py` creates deterministic queues for at least three unique reviewer IDs.

Every queue:

- contains all 24 anchors exactly once;
- is deterministically seeded by the source manifest digest and reviewer ID;
- requires a minimum six-position gap between contrast-pair members;
- exposes only target-blind fields;
- embeds the reviewer ID in each blank form;
- records the source-content digest;
- receives a canonical SHA-256 queue digest.

Determinism makes queue regeneration auditable. Reviewer-specific order reduces common order effects. Neither property prevents conceptual recognition of paired content.

### Locked submissions

The submission contract requires:

- exact reviewer and queue identity;
- exact source-content digest;
- exact assigned item order;
- one completed record per item;
- timezone-aware lock timestamp;
- affirmative pre-reveal lock;
- negative declaration of target exposure;
- valid score, reason-code, adequacy, confidence, ambiguity, and pair-recognition fields.

The corresponding JSON Schema is:

`research/egc2/anchor_review_submission.v0.1.schema.json`

### Inadequate-reference handling

A reviewer may suppress a numerical score only through:

```text
score_disposition = suppressed_reference_inadequate
semantic_fidelity_score = null
```

The map must simultaneously be marked non-adequate. Suppression is preserved as an outcome rather than recoded as a midpoint.

Two or more suppressions trigger a reference-target review disposition in the aggregate report.

This fixes the earlier mechanical requirement to score an unusable target. It does not yet determine how inadequate participant intention maps should be handled in a confirmatory EGC study.

### Reveal control

Discrepancy aggregation fails closed unless explicit reveal authorization is passed after all assigned reviewer submissions validate.

The aggregate report preserves:

- every blind numeric score;
- numeric-review count;
- suppression count;
- score range;
- pair-recognition flags;
- constructor target after authorization;
- packet-level review disposition.

No packet is automatically accepted.

## Proposed discrepancy rules

The current engineering triage marks a packet for revision or rejection when:

- blind median differs from constructor target by more than one score region; or
- blind score range exceeds three points.

It separately identifies inadequate-reference and insufficient-numeric-review cases.

These are provisional instrument-development rules, not validated psychometric cutoffs.

## Validation status

A focused 12-test suite was added in:

`research/egc2/test_prepare_anchor_expert_review.py`

It covers:

1. deterministic queue generation;
2. complete three-reviewer allocation;
3. minimum pair separation;
4. queue-digest tampering rejection;
5. target-leakage rejection;
6. complete locked-submission acceptance;
7. unlocked-submission rejection;
8. assigned-order enforcement;
9. permitted inadequate-reference suppression;
10. rejection of suppression for an adequate map;
11. aggregation rejection before reveal authorization;
12. preservation of all packets after authorized aggregation.

**Important limitation:** the current tool environment could write and inspect repository files through GitHub but could not clone or execute the repository because DNS resolution for `github.com` failed. Therefore, the tests are committed but not claimed as run or passed in this cycle. Runtime validation remains mandatory before reviewer distribution.

## Claims supported

Supported as engineering design:

- reviewer-specific target-blind queues can be generated under an explicit pair-separation rule;
- submissions can be bound to exact source and queue digests;
- aggregation can be blocked before explicit target reveal;
- reference inadequacy can be recorded without manufacturing a numerical score;
- discrepancy and recognition outcomes can be preserved rather than silently repaired.

## Claims not supported

Not established:

- that the implementation runs without defect;
- that the six-position gap prevents pair recognition;
- that three reviewers are sufficient;
- that independent reviewers will agree;
- that agreement implies construct validity;
- that constructor targets are correct;
- that any packet is a usable anchor;
- that synthetic-anchor behavior transfers to ordinary raters or participant material.

## Current blockers

- runtime execution of the focused test suite;
- recruitment of three independent reviewers;
- compensation and consent terms;
- authorized ethics/data-use determination;
- 18+ additional development candidates for the full 42-packet blueprint;
- the full 96-item production bank;
- pilot interface and production dry run.

## Highest-leverage next action

Run the committed focused suite in a repository-capable environment, fix any failures, generate the three reviewer queues, and obtain three complete locked target-blind submissions before constructor targets are revealed.
