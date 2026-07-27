# EGC 2.0 — Anchor Expert Review v0.2 Hardening Review

**Status:** Focused engineering hardening complete; real expert review still absent  
**Date:** 2026-07-27  
**Scope:** First 24 synthetic semantic-fidelity development packets

## Decision

The first expert-review implementation was not safe enough for live distribution.

It removed explicit contrast labels but still exposed sequential source IDs such as `A001` and `A002`. Because pair members were constructed as adjacent source records, the public identifier itself could reveal pairing. It also required only a six-position separation, bundled review identity too closely with source identity, and computed a submission digest without requiring the submitted artifact to carry and validate that digest.

Version 0.2 is now the required live-review path. Version 0.1 remains preserved as development history but must not be distributed to reviewers.

## Weaknesses fixed

### 1. Source-identity leakage

Reviewer-facing queues now contain reviewer-specific opaque presentation IDs derived from a secret seed, reviewer pseudonym, and source anchor ID.

The public queue contains no:

- source anchor ID;
- contrast-group ID;
- contrast-family label;
- constructor target;
- constructor rationale;
- admissible score range;
- audit authorship.

The source mapping is stored only in a separate protected key.

### 2. Pair-recognition exposure

Every designed pair is separated by exactly twelve positions: one member appears in the first half of the 24-item queue and the other in the second half.

Each half contains four items from each frozen domain. Pair ordering also rejects domain runs longer than two.

This is a deterministic structural improvement over ordinary random shuffling and over the previous six-position minimum. It does not prevent recognition from repeated prompts or memorable content.

### 3. Public/protected artifact separation

The tool emits:

- one public queue per reviewer;
- one separately stored protected assignment-key bundle.

The protected bundle records source IDs, pair membership, contrast families, and constructor targets. It is not intended for reviewer distribution or repository commitment.

### 4. Tamper-evident chain

Version 0.2 independently binds:

- public queue content;
- each protected reviewer mapping;
- the full protected bundle;
- each completed submission;
- the aggregate report.

Validation recomputes rather than merely copying declared digests.

This detects later changes. It does not authenticate reviewer identity or provide a trusted timestamp.

### 5. Inadequate reference targets

A reviewer is no longer forced to manufacture a numeric fidelity score when the intention map cannot support one.

A null score is permitted only when:

```text
intention_map_adequacy != adequate
score_disposition = suppress_reference_inadequate
semantic_fidelity_score = null
```

A suppressed numeric score, or suppression of an adequate map, fails closed.

### 6. Pair-recognition evidence

A reviewer who marks possible pair recognition must provide a note. This creates inspectable evidence rather than an uninterpretable checkbox.

### 7. Pre-reveal discrepancy review

Version 0.1 blocked aggregation entirely until constructor targets were revealed. Version 0.2 can aggregate reviewer disagreement, adequacy judgments, reason codes, suppression requests, and pair-recognition reports without joining constructor targets.

Post-lock reveal is a separate explicit operation.

## Files

- `research/egc2/harden_anchor_expert_review.py`
- `research/egc2/test_harden_anchor_expert_review.py`
- `research/egc2/anchor_review_submission.v0.2.schema.json`
- `research/egc2/ANCHOR_EXPERT_REVIEW_V0.2_HARDENING_PACKET.md`
- `research/egc2/results/anchor_expert_review_hardening_validation.v0.2.json`

## Focused validation

The hardened code was executed against a self-contained synthetic fixture matching the committed structural contract:

- 24 packets;
- 12 two-packet contrast groups;
- three frozen domains;
- four groups per domain;
- three reviewer pseudonyms.

Commands:

```bash
python -m unittest -v test_harden_anchor_expert_review.py
python -m py_compile harden_anchor_expert_review.py test_harden_anchor_expert_review.py
```

Result:

- **11 tests passed**;
- **0 tests failed**;
- Python compilation passed.

The tests verify:

1. exact twelve-position pair separation;
2. exact domain balance within both queue halves;
3. opaque public identifiers and protected source mapping;
4. deterministic regeneration;
5. distinct reviewer anchor orders;
6. minimum three-reviewer enforcement;
7. queue and submission tamper rejection;
8. inadequate-map suppression rules;
9. mandatory pair-recognition notes;
10. target-free pre-reveal aggregation;
11. post-reveal discrepancy flags and protected-key tamper rejection.

## Validation limit

Direct cloning of the full repository remained unavailable because the execution environment could not resolve `github.com`. Therefore:

- the hardened module was not executed against the committed 24-packet manifest in that isolated runtime;
- repository-wide CI is not claimed;
- the focused fixture does not prove compatibility with every committed packet field;
- the v0.2 CLI still requires execution in a repository-capable environment before distribution.

## Claims supported

Supported as focused engineering evidence:

- source IDs and constructor targets can be removed from public queues;
- exact twelve-position separation is achievable by construction;
- public queues and protected mappings can be stored separately;
- queue, key, submission, and aggregate tampering can be detected;
- pre-reveal discrepancy aggregation can exclude constructor targets;
- inadequate reference maps can suppress forced numeric scoring.

## Claims not supported

Not established:

- that any expert will agree with another;
- that any constructor target is correct;
- that twelve-position separation prevents semantic pair recognition;
- that three experts are sufficient;
- that a digest authenticates a reviewer or lock time;
- that any packet is a valid anchor;
- that expert-reviewed anchors transfer to ordinary trained raters;
- that semantic fidelity is empirically validated.

## Remaining blockers

- execution against the committed manifest;
- generation of the real three reviewer queues;
- recruitment and conflict screening of three experts;
- consent and compensation terms;
- authorized ethics/data-use determination;
- secure reviewer identity and digest log;
- at least 18 additional candidates for the full 42-packet blueprint;
- the full 96-item monitoring bank and later rater pilot.

## Highest-leverage next action

Run v0.2 against the committed manifest in a repository-capable environment, verify the generated queue digests and exact twelve-position gaps, then recruit three independent reviewers and record their locked submission digests before constructor-target reveal.
