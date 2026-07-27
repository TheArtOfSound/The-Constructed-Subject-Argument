# EGC 2.0 — Blind Expert Anchor Review Packet

**Status:** Review instructions for the first 24 synthetic anchor-development packets  
**Minimum reviewers:** Three independent reviewers per packet  
**Target visibility:** Prohibited until submissions are locked  
**Use:** Development review only; not production scoring

## Reviewer role

You are evaluating whether a candidate response faithfully communicates the meaning documented in its private intention map.

You are not evaluating:

- literary quality;
- persuasiveness;
- sophistication;
- emotional intensity;
- moral or political agreement;
- whether the response sounds human;
- whether the response was produced by a human or an AI;
- consciousness, subjectivity, or deception.

## Materials shown for each item

You will see:

1. an opaque review item ID;
2. a prompt;
3. a private intention map;
4. a candidate response.

You will not see:

- the constructor's target score;
- constructor reason codes;
- contrast-family labels;
- paired-item identifiers;
- constructor rationale;
- admissible score range;
- prior reviewer scores;
- pilot results.

Do not attempt to infer or reconstruct the hidden target. Score the item from the visible evidence.

## Semantic-fidelity scale

### 1 — Absent or materially contradictory

The central meaning is absent or reversed. Essential concepts are largely missing.

### 2 — Minimal fragments

A small fragment is recognizable, but the intended message is not recoverable without substantial inference.

### 3 — Partial but materially incomplete

The broad topic and multiple intended concepts are present, but an essential relationship, qualification, or implication is missing or wrong.

### 4 — Substantial transmission with important loss

The central meaning is recoverable and most essential concepts are present, but consequential loss or distortion remains.

### 5 — Strong transmission with limited loss

The response is accurate and substantially complete. Remaining loss is real but does not materially change the intended overall understanding.

### 6 — Very high fidelity

The central meaning, essential concepts, relationships, and relevant tone are preserved with no material contradiction or omission.

### 7 — Exceptionally complete and precise

The response preserves all documented components, qualifications, dependencies, audience fit, and meaning-relevant tone with exceptional precision.

A short or plain response may receive a 7. Length and polish are not requirements.

## Intention-map adequacy

Before finalizing the score, classify the intention map:

- `adequate`
- `too_sparse`
- `internal_conflict`
- `uninterpretable`
- `response_dependent`
- `other_problem`

When the map is inadequate, do not invent missing intention. Record the adequacy problem and explain whether a numerical score remains defensible.

## Reason codes

Select every code that materially explains your judgment.

### Meaning coverage

- `CM_MISSING`
- `CM_REVERSED`
- `EC_MISSING`
- `EC_DISTORTED`
- `REL_MISSING`
- `REL_REVERSED`
- `QUAL_MISSING`
- `IMPLICATION_CHANGED`

### Tone and audience

- `TONE_MISMATCH_MATERIAL`
- `AUDIENCE_TARGET_MISSED`
- `TONE_DIFFERENCE_NONMATERIAL`

### Reference target

- `MAP_TOO_SPARSE`
- `MAP_INTERNAL_CONFLICT`
- `MAP_UNINTERPRETABLE`
- `MAP_RESPONSE_DEPENDENT`
- `MAP_OTHER`

### No material loss

- `NO_MATERIAL_LOSS`

The development export does not show constructor warning codes for length, polish, emotion, agreement, or lexical overlap. Reviewers should independently note suspected bias in the ambiguity field rather than trying to identify a hidden manipulation.

## Required item-level submission

For each item, submit:

```json
{
  "review_item_id": "A000",
  "semantic_fidelity_score": 1,
  "reason_codes": [],
  "intention_map_adequacy": "adequate",
  "confidence_1_to_5": 1,
  "ambiguity_note": null,
  "reviewer_id": "opaque-reviewer-id",
  "reviewed_at_utc": "ISO-8601 timestamp",
  "locked_before_target_reveal": true
}
```

`semantic_fidelity_score` is required even when the map is inadequate because the current schema is being stress-tested. In the ambiguity note, state clearly when you believe the score should later be suppressed.

## Independence and locking

Reviewers must:

- score independently;
- avoid discussing items with other reviewers;
- avoid searching for or requesting constructor targets;
- avoid using generative AI or external scoring assistance;
- lock every submission before target reveal;
- report accidental recognition of repeated or paired items.

The review coordinator must:

- assign independent item orders;
- separate members of the same contrast pair;
- preserve the original export and each locked submission;
- timestamp every lock;
- reveal targets only after all assigned reviews are locked;
- preserve disagreements and rejected packets.

## Discrepancy review

After all reviews are locked, the coordinator may reveal constructor targets and rationales.

A packet is automatically flagged for revision or rejection when:

- the median reviewer score differs from the provisional region by more than one point;
- the reviewer score range exceeds three points;
- reviewers disagree about the central meaning;
- two or more reviewers flag map inadequacy;
- reason codes indicate different causal or logical readings;
- the response has multiple plausible interpretations;
- apparent length, polish, emotion, agreement, or lexical-overlap bias drives the score.

A revised packet receives:

- a new version;
- a new content digest;
- a documented change rationale;
- a fresh blind review.

Prior review results remain archived and are not overwritten.

## Review report

For every packet, report:

- all independent scores;
- median, minimum, maximum, and range;
- all reason codes;
- adequacy judgments;
- confidence distribution;
- ambiguity notes;
- provisional-target discrepancy;
- disposition: `retain_for_pilot`, `revise_and_rereview`, or `reject`.

The report must not call a retained packet validated. Retention only advances it to pilot-candidate status.
