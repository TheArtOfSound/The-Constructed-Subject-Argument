# EGC 2.0 Blind Expert Anchor Review — Execution Packet

**Status:** Ready for reviewer recruitment and target-blind scoring of the first 24 synthetic development packets  
**Non-claim:** Reviewer agreement does not validate an anchor, the seven-point scale, EGC, hidden intention, subjectivity, or consciousness.

## Purpose

The review asks whether three independent reviewers, without access to constructor targets or rationales, interpret each intention-map/response pair similarly enough to justify revision, rejection, or continued pilot development.

This is an instrument-development review, not a study of the EGC hypothesis.

## Reviewer profile

Recruit three reviewers who:

- are fluent in English;
- can distinguish semantic fidelity from writing quality;
- did not construct the packets;
- have not seen constructor targets, rationales, contrast labels, or admissible ranges;
- can complete all 24 items independently;
- agree not to use generative AI, search, or another reviewer while scoring;
- disclose relevant writing assessment, psychometrics, cognitive science, qualitative coding, linguistics, or research-methods experience;
- have no financial or authorship interest in obtaining a favorable result.

Expertise is useful but does not confer correctness. Each reviewer remains an independent measurement source.

## Copy-ready outreach

### Subject

Independent blind review of a semantic-fidelity rating instrument

### Message

We are developing a research instrument for measuring how accurately a written response transmits a separately documented intention map. We need independent reviewers to score 24 synthetic intention-map/response pairs using a seven-point semantic-fidelity rubric.

The review is target-blind: you will not see the constructor's intended score, rationale, contrast design, or any other reviewer's answers. The task is not to judge writing quality, agree with the response, or evaluate consciousness. It is to judge preservation of central meaning, essential concepts, relationships, qualifications, and meaning-relevant tone.

The review requires one complete independent submission. Scores are locked before constructor targets are revealed. We preserve disagreement, ambiguity notes, and rejected items rather than forcing consensus.

Before participation, we will provide the rubric, estimated workload, compensation terms, confidentiality and data-use information, and a technical dry run.

## Independence declaration

Before receiving a queue, each reviewer records:

- reviewer ID;
- relevant experience;
- whether they helped create any packet;
- whether they have seen any target score or constructor rationale;
- whether they know another assigned reviewer;
- whether they have discussed the item bank;
- conflict-of-interest disclosure;
- agreement not to use external assistance;
- agreement to complete the assigned order without reordering items;
- agreement that scores become immutable before target reveal.

A reviewer who has seen constructor targets must not score that tranche.

## Queue controls

`prepare_anchor_expert_review.py` creates one deterministic queue for each reviewer.

Each queue:

- contains every packet exactly once;
- is bound to the source manifest digest;
- has a reviewer-specific deterministic order;
- separates the two members of every contrast pair by at least six positions;
- conceals contrast-group IDs and all constructor targets;
- has its own queue digest;
- embeds the assigned reviewer ID in every blank form.

Reviewers must not exchange queues. Different ordering reduces shared order artifacts but does not eliminate recognition of conceptually similar pairs.

## Required item-level fields

For each item, reviewers provide:

1. semantic-fidelity score from 1 to 7, or a suppressed-score disposition when the intention map is unusable;
2. score disposition:
   - `retained_numeric`;
   - `suppressed_reference_inadequate`;
3. reason codes;
4. intention-map adequacy judgment;
5. confidence from 1 to 5;
6. ambiguity note where relevant;
7. whether the reviewer suspects they recognized a related comparison item.

Scores of 1, 2, 6, or 7 require at least one reason code.

## Reference-target inadequacy rule

The previous architecture forced a numerical score even when an intention map might be too sparse or internally unusable. The review workflow now permits:

```text
score_disposition = suppressed_reference_inadequate
semantic_fidelity_score = null
```

This is allowed only when the reviewer marks the intention map as non-adequate. The suppressed result remains part of the audit record and is not converted to a neutral or midpoint score.

Two or more suppressions on the same packet trigger:

```text
reference_target_inadequate_review_required
```

This resolves the mechanical scoring problem but does not establish the correct substantive handling for later participant data.

## Submission lock

A submission is admissible only when:

- all 24 items appear once and in assigned order;
- source and queue digests match;
- reviewer ID matches;
- all required fields are present;
- `locked_before_target_reveal` is true;
- `targets_seen_before_lock` is false;
- lock time is timezone-aware;
- the submission passes the fail-closed validator.

No item-level correction is allowed after reveal. Clerical repair requires a preserved superseding submission and documented reason before any target join.

## Reveal and discrepancy review

Constructor targets may be joined only after all assigned submissions validate and explicit reveal authorization is recorded.

The discrepancy report classifies packets as:

- `candidate_retention_review`;
- `revision_or_rejection_required`;
- `reference_target_inadequate_review_required`;
- `insufficient_numeric_reviews`.

Automatic retention is prohibited. The report is triage evidence for a blinded discrepancy meeting.

Revision or rejection is triggered when the blind median differs from the constructor target by more than one region, the score range exceeds three points, or the reference target is repeatedly suppressed.

Revised packets receive a new version and undergo a new blind review. They do not inherit the original review status.

## Data handling

The review file must not contain reviewer names, emails, payment details, or other direct identifiers. A separate private linkage table may map reviewer IDs for administration.

Preserve:

- source manifest and digest;
- reviewer queue and digest;
- locked submission and digest;
- validation result;
- reveal authorization timestamp;
- discrepancy report;
- revision or rejection decision;
- all null, failed, suppressed, and contradictory outcomes.

## Remaining limitations

This execution package does not solve:

- recruitment of genuinely independent reviewers;
- compensation and consent terms;
- authorized ethics/data-use determination;
- whether three reviewers are sufficient;
- whether reviewers share the same construct despite numerical agreement;
- whether synthetic packets generalize to real participant material;
- pair recognition from semantic content;
- the missing 18+ development candidates required by the 42-packet blueprint;
- pilot-rater category functioning, reliability, fatigue, or drift.

## Execution command

```bash
python research/egc2/prepare_anchor_expert_review.py \
  research/egc2/anchor_development_manifest.v0.1.json \
  --reviewers R01 R02 R03 \
  --queue-set-out private/egc2/anchor-review/queue-set.v0.1.json
```

The generated queue set contains blinded item content and should be distributed reviewer-by-reviewer rather than published as a common answerable form.

## Next decision

The next valid evidence step is to recruit three independent reviewers, generate their queues, obtain locked complete submissions, and run discrepancy aggregation only after all three pass validation.
