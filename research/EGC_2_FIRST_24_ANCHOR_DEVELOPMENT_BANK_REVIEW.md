# EGC 2.0 — First 24-Anchor Development Bank Review

**Status:** Draft synthetic development bank; not an active or validated anchor bank  
**Date:** 2026-07-27  
**Target construct:** Semantic fidelity between a private intention map and a candidate response  
**Source material:** Entirely synthetic; no identifiable participant material

## Decision

The first 24 machine-readable anchor packets now exist and can enter target-blind expert review.

This closes the prior absence of actual anchor content, but it does **not** close the empirical-validation gap. Every packet remains `draft_unreviewed`. Constructor targets, admissible ranges, rationales, and contrast labels are hypotheses that reviewers must test rather than accept.

The bank is a development tranche, not the final anchor instrument.

## Construction

The manifest contains:

- 24 synthetic packets;
- 12 paired contrast groups;
- 8 packets in each of the three frozen prompt domains;
- all eight mandatory construct-bias contrast families;
- all seven provisional semantic-fidelity score regions;
- explicit intention maps, meaning-critical relationships, reason codes, ambiguity notes, and audit fields;
- no expert consensus scores;
- no pilot metrics;
- no participant-derived or identifiable content.

The three domains are:

1. autobiographical meaning;
2. conceptual explanation;
3. position and reasoning.

The mandatory contrast families represented are:

1. length decoy;
2. polish decoy;
3. emotional-intensity decoy;
4. agreement decoy;
5. verbosity with contradiction;
6. concise completeness;
7. tone versus content;
8. reference-target inadequacy.

## Pairing design

Each contrast group contains exactly two packets that share the same prompt.

All non-reference-target pairs also share the exact private intention map. This permits reviewers to compare the effect of response form, omission, distortion, or relationship reversal while holding the intended target fixed.

The reference-target-inadequacy pair deliberately changes the intention-map adequacy to test whether reviewers flag an unusable reference instead of manufacturing a precise fidelity judgment.

## Leakage control

`validate_anchor_development_manifest.py` generates blind-review packets from an explicit allowlist. The expert-facing export includes only:

- opaque review item ID;
- packet version;
- prompt domain;
- prompt;
- private intention map;
- candidate response;
- blank review fields.

It excludes:

- provisional score region;
- constructor reason codes;
- manipulated feature labels;
- contrast family and group;
- constructor rationale;
- admissible score range;
- ambiguity notes;
- validation status;
- prior review data;
- pilot metrics;
- audit authorship.

The tool fails closed if packet digests, pair structure, domain balance, required contrast coverage, score-region coverage, or review-state restrictions are violated.

## Validation evidence

Focused validation produced:

- 24 packets;
- 12 two-item contrast groups;
- 8 packets per prompt domain;
- all eight required contrast families represented;
- all seven provisional score regions represented;
- canonical packet digest:

```text
c862442118a78ad912f09361ed03424f5a0f51b94b1977c71e1c889c353691f2
```

Eight focused tests passed:

1. committed manifest validation;
2. digest-tampering rejection;
3. missing contrast-family rejection;
4. pair intention-map mismatch rejection;
5. blind-export target-leakage check;
6. source-digest preservation;
7. inadequate-map reason-code enforcement;
8. command-line summary and export generation.

`py_compile` passed for the validator and tests.

## Important weaknesses preserved

### 1. The bank is smaller than the full blueprint

The anchor-bank protocol calls for at least 42 development candidates to cover:

- seven score regions;
- three domains;
- two candidates per region-by-domain cell.

This 24-packet tranche cannot satisfy that 42-cell blueprint. It prioritizes mandatory contrast-family coverage and domain balance.

It must not be described as the complete candidate bank.

### 2. Provisional score regions are imbalanced

The current constructor targets are:

| Region | Packet count |
|---|---:|
| 1 | 1 |
| 2 | 3 |
| 3 | 1 |
| 4 | 3 |
| 5 | 2 |
| 6 | 10 |
| 7 | 4 |

Region 6 is intentionally common because many contrast pairs contain a high-fidelity comparator. Regions 1 and 3 are underrepresented.

Blind expert review may also move packets away from their constructor targets. The next construction tranche must fill region-by-domain deficits after, not before, reviewing how the first tranche functions.

### 3. Synthetic construction is not reference validity

A packet is not a valid anchor because its constructor can explain the intended score. Expert reviewers may disagree about:

- the central meaning;
- whether an omission is material;
- whether tone is meaning-relevant;
- whether a response fits region 5 versus 6;
- whether an inadequate map should receive any retained numerical score.

Those disagreements are evidence about the instrument and must be preserved.

### 4. Paired items can create recognition risk

If both members of a contrast pair appear close together, reviewers may infer the manipulation or compare items directly instead of independently scoring fidelity.

Expert and pilot exports must therefore:

- randomize item order independently;
- impose separation between pair members;
- conceal group identifiers;
- prohibit revisiting earlier answers where feasible;
- record whether reviewers recognized a pair.

### 5. Expert review is not pilot-rater calibration

Three independent expert reviews can reject bad packets and create reference distributions, but they do not establish:

- category functioning among ordinary trained raters;
- anchor-to-novel transfer;
- drift sensitivity;
- workload feasibility;
- absence of length, polish, agreement, or emotional bias;
- adequate reliability for production scoring.

### 6. One map-inadequacy packet challenges the scoring architecture

Packet `A007` deliberately pairs an inadequate map with a plausible response. The schema still requires a provisional numeric region.

Reviewers must record whether the correct disposition is:

- retain a score with a strong adequacy warning;
- treat the score as exploratory only;
- suppress the score because the reference target is unusable.

This is a design decision, not a clerical disagreement.

## Permitted conclusions

Supported as development evidence:

- actual auditable anchor content now exists;
- the content covers all mandatory contrast families and all domains;
- target-blind review exports can be generated without constructor-target leakage;
- manifest structure and digest integrity are testable.

Not supported:

- any packet's provisional target is correct;
- any packet is suitable for training or drift monitoring;
- the seven-point scale functions as intended;
- the bank validates semantic fidelity as a construct;
- the bank validates EGC or supports claims about consciousness, hidden intention, or subjectivity.

## Review disposition

The bank is ready for **blind expert review**, not rater recruitment.

The launch gate must remain closed until:

1. at least three independent reviewers score every packet;
2. submissions are locked before constructor targets are revealed;
3. discrepancy review identifies revision, rejection, or candidate-retention status;
4. revised packets receive new versions and repeat blind review;
5. the remaining 18+ candidates are constructed to satisfy the full region-by-domain blueprint;
6. the full 96-item monitoring bank and ethics/data-use requirements are complete.

## Highest-leverage next action

Recruit three independent target-blind reviewers for this 24-packet tranche and lock their item-level scores, reason codes, adequacy judgments, confidence, and ambiguity notes before any constructor targets are revealed.
