# EGC 2.0 Semantic-Fidelity Anchor Bank Protocol

**Status:** Methods specification for pilot construction; no anchor is yet validated  
**Date:** 2026-07-25  
**Parent protocol:** `research/EGC_2_HUMAN_RATING_RELIABILITY_PROTOCOL.md`  
**Scope:** Blinded human rating of semantic fidelity between a private intention map and a produced response  
**Non-claim:** This protocol does not validate EGC as a consciousness measure and does not treat any synthetic example as a gold-standard score before empirical calibration.

---

## 1. Purpose

EGC 2.0 requires raters to judge how faithfully a written response communicates the central meaning, essential concepts, relationships, and intended tone documented in a participant's private intention map.

A rating rubric alone is insufficient. Raters can agree on the wrong construct by substituting length, polish, emotional intensity, vocabulary sophistication, or agreement with the author for semantic fidelity. An anchor bank is therefore required to:

1. make the target construct concrete;
2. expose common construct-irrelevant shortcuts;
3. calibrate category use before production scoring;
4. detect rater drift across batches;
5. support adjudication without revealing experimental condition;
6. test whether the seven response categories are distinguishable in practice.

The anchor bank is a measurement instrument. It must be constructed, reviewed, piloted, revised, and versioned with the same discipline as the study itself.

---

## 2. Target construct

### 2.1 Primary construct

**Semantic fidelity** is the degree to which the produced response accurately transmits the participant-defined central meaning, essential concepts, and relationships in the private intention map.

The rating target is not literary merit. It is not the amount of text. It is not emotional vividness. It is not whether the rater agrees with the participant.

### 2.2 Evidence raters may use

Raters may compare the response against:

- the central-meaning statement;
- the essential concept or detail list;
- explicitly stated relationships among concepts;
- intended emotional tone where tone is part of the intended meaning;
- intended audience understanding;
- participant-declared uncertainty in the intention map.

### 2.3 Evidence raters must not substitute

Raters must not increase a score merely because a response is:

- longer;
- grammatically polished;
- emotionally intense;
- rhetorically persuasive;
- sophisticated in vocabulary;
- agreeable or morally appealing;
- autobiographically dramatic;
- stylistically distinctive.

These features matter only when they improve or damage transmission of the documented intended meaning.

---

## 3. Anchor-bank architecture

The pilot bank should contain **at least 42 candidate anchor packets** before reduction:

- 7 intended score regions;
- 3 prompt domains;
- 2 examples per score-region-by-domain cell.

The three initial domains are:

1. autobiographical meaning;
2. conceptual explanation;
3. position and reasoning.

This balanced starting bank prevents the rating scale from being learned through one genre only. The final production bank may be smaller after pilot testing, but every score region must remain represented in every domain unless evidence shows a region cannot be instantiated reliably in that domain.

Each anchor packet contains:

```text
anchor_id
anchor_version
prompt_domain
prompt_text
private_intention_map
candidate_response
provisional_score_region
provisional_reason_codes
construct_irrelevant_features
expert_rationale
admissible_score_range
known_ambiguities
validation_status
source_type
```

`source_type` must distinguish:

- `synthetic_constructed`;
- `pilot_response_deidentified`;
- `production_response_retired`.

No production response may become an active anchor while its condition remains available to raters or while inclusion could affect the confirmatory analysis.

---

## 4. Seven provisional score regions

The exact wording must remain aligned with the parent reliability protocol. These regions are provisional until empirical category-functioning evidence is available.

### Region 1 — Absent or materially contradictory

The response communicates little or none of the intended central meaning, or materially reverses it.

Required anchor characteristics:

- central meaning omitted or contradicted;
- essential concepts mostly absent;
- no plausible reading preserves the intended relationship structure.

### Region 2 — Minimal fragments

A small fragment of the intended meaning appears, but the response is largely incomplete, displaced, or misleading.

Required anchor characteristics:

- at least one intended concept recognizable;
- central meaning not recoverable without substantial inference;
- major omissions or distortions dominate.

### Region 3 — Partial but materially incomplete

The response conveys a meaningful portion of the intention but omits or distorts elements required for a substantially faithful account.

Required anchor characteristics:

- central topic identifiable;
- multiple intended concepts present;
- at least one essential relationship, qualification, or implication missing or wrong.

### Region 4 — Substantial transmission with important loss

The central meaning is communicated, but important intended content, nuance, or relationship structure is missing or weakened.

Required anchor characteristics:

- central meaning recoverable;
- most essential concepts present;
- one or more consequential omissions, compressions, or distortions remain.

### Region 5 — Strong transmission with limited loss

The response communicates the intended meaning accurately and substantially completely, with only limited omissions or imprecision.

Required anchor characteristics:

- central meaning accurate;
- essential concepts and major relationships preserved;
- remaining loss is real but does not materially change the overall intended understanding.

### Region 6 — Very high fidelity

The response communicates the intended meaning, essential concepts, relationships, and relevant tone with high completeness and accuracy.

Required anchor characteristics:

- no material contradiction;
- no essential concept omitted;
- only minor, local, or stylistic differences from the intention map.

### Region 7 — Exceptionally complete and precise

The response transmits the documented intention with exceptional completeness, precision, relationship preservation, and audience fit.

Required anchor characteristics:

- all required meaning components clearly represented;
- important qualifications and dependencies preserved;
- tone and audience understanding accurately realized where specified;
- no construct-irrelevant polish requirement.

A Region 7 response need not be long or elegant. A concise response can qualify when the intention map itself is concise and fully transmitted.

---

## 5. Mandatory contrast families

The anchor bank must include paired or triplet examples that isolate common rater errors.

### 5.1 Length decoy

Same semantic fidelity, materially different word count.

Purpose: test whether raters reward length after fidelity is held approximately constant.

### 5.2 Polish decoy

A polished response with lower fidelity paired with a plain response with higher fidelity.

Purpose: detect substitution of writing quality for meaning preservation.

### 5.3 Emotional-intensity decoy

A highly emotional response that omits intended content paired with a restrained but faithful response.

Purpose: test whether emotional vividness inflates fidelity judgments.

### 5.4 Agreement decoy

A response expressing a view the rater may prefer but misrepresenting the intention map, paired with a less agreeable but faithful response.

Purpose: detect ideological or moral agreement bias.

### 5.5 Verbosity-with-contradiction decoy

A long response containing many intended terms but reversing one essential relationship.

Purpose: ensure lexical overlap and concept counts do not conceal relational contradiction.

### 5.6 Concise-completeness decoy

A short response that fully transmits a narrow intention map.

Purpose: prevent minimum-length assumptions.

### 5.7 Tone-versus-content contrast

Two responses with equal propositional coverage but different preservation of an explicitly intended emotional tone.

Purpose: calibrate when tone is part of fidelity and when it is merely stylistic.

### 5.8 Reference-target inadequacy contrast

A sparse or internally inconsistent intention map paired with a plausible response.

Purpose: train raters to flag intention-map inadequacy rather than forcing a false precision score.

---

## 6. Reason-code system

Every candidate anchor must include one or more reason codes. Production raters should select reason codes for low or disputed ratings, but the numerical score remains primary.

### Meaning-coverage codes

- `CM_MISSING` — central meaning absent;
- `CM_REVERSED` — central meaning contradicted;
- `EC_MISSING` — essential concept omitted;
- `EC_DISTORTED` — essential concept materially altered;
- `REL_MISSING` — required relationship absent;
- `REL_REVERSED` — causal, temporal, logical, or evaluative relationship reversed;
- `QUAL_MISSING` — essential qualification or uncertainty removed;
- `IMPLICATION_CHANGED` — resulting audience understanding materially differs.

### Tone and audience codes

- `TONE_MISMATCH_MATERIAL` — specified tone was meaning-relevant and not preserved;
- `AUDIENCE_TARGET_MISSED` — response would predictably produce a different intended understanding;
- `TONE_DIFFERENCE_NONMATERIAL` — tone differs but semantic fidelity is not materially reduced.

### Reference-target codes

- `MAP_TOO_SPARSE`;
- `MAP_INTERNAL_CONFLICT`;
- `MAP_UNINTERPRETABLE`;
- `MAP_RESPONSE_DEPENDENT` — intention map appears to have been generated from or after the response;
- `MAP_OTHER`.

### Construct-irrelevant warning codes

- `LENGTH_DECOY`;
- `POLISH_DECOY`;
- `EMOTION_DECOY`;
- `AGREEMENT_DECOY`;
- `LEXICAL_OVERLAP_DECOY`.

These warning codes describe anchor design, not participant deficits.

---

## 7. Construction procedure

### Phase 1 — Blueprint freeze

Before drafting anchors, freeze:

- domain cells;
- target score regions;
- mandatory contrast families;
- reason-code definitions;
- minimum anchor count;
- review criteria;
- retirement rules.

### Phase 2 — Independent construction

At least two constructors independently draft candidate anchor packets from the blueprint.

Constructors may know the target region but must document:

- which meaning components are preserved;
- which are omitted, distorted, or reversed;
- which construct-irrelevant features were manipulated;
- why the response should fall in the target region.

Synthetic anchors must not mimic identifiable participant material.

### Phase 3 — Blind expert review

At least three reviewers who did not draft the anchor independently score each packet without seeing its target region or rationale.

Reviewers provide:

- numerical score;
- reason codes;
- intention-map adequacy flag;
- confidence;
- ambiguity note.

### Phase 4 — Discrepancy review

Reveal the provisional target only after blind scoring is locked.

Anchors are revised or rejected when:

- median reviewer score differs from the target by more than one region;
- score range exceeds three scale points;
- reviewers disagree about the central meaning;
- construct-irrelevant features appear to drive scoring;
- the intention map is inadequate;
- the response has multiple equally plausible interpretations.

Revised anchors must return to blind review. They do not inherit prior validation.

### Phase 5 — Pilot-rater calibration

The candidate bank is administered to the eight-rater pilot described in the reliability protocol.

For each anchor, record:

- score distribution;
- median and dispersion;
- target-region hit rate;
- adjacent-region rate;
- nonadjacent error rate;
- reason-code agreement;
- response time;
- confidence;
- differential performance by rater severity and experience.

### Phase 6 — Empirical retention

An anchor may enter the active calibration bank only when:

1. the reference intention map passes adequacy review;
2. expert median is in the intended region or the region is formally revised;
3. at least 80% of pilot ratings fall in the intended or immediately adjacent region;
4. no more than 10% are nonadjacent errors;
5. the explanation for the target score is stable across reviewers;
6. the anchor does not produce a material length, polish, emotion, or agreement bias inconsistent with its design purpose;
7. the anchor contributes unique coverage to the blueprint.

The 80% and 10% thresholds are provisional pilot rules, not validated universal standards. They must be evaluated against observed category functioning and may be revised before confirmatory scoring, with the revision and rationale frozen before condition unblinding.

---

## 8. Calibration use

### 8.1 Initial qualification

Before production work, a rater must complete a calibration set containing:

- at least one anchor from each score region;
- all mandatory contrast families;
- all three prompt domains;
- at least two intention-map inadequacy cases.

A rater qualifies only if all preregistered conditions are met, including:

- acceptable weighted agreement with the anchor consensus;
- acceptable nonadjacent error rate;
- no systematic length or polish bias;
- correct handling of map-inadequacy cases;
- completion of rationale review for every nonadjacent error.

Numerical gates must be fixed after the pilot and before production recruitment.

### 8.2 Recurring drift checks

Production batches must include undisclosed anchor items.

Drift monitoring must distinguish:

- global severity shift;
- category compression;
- increased nonadjacent errors;
- construct-irrelevant bias;
- domain-specific drift;
- reason-code drift.

A rater who crosses a preregistered drift boundary is paused. Previously completed ratings are not silently deleted. The protocol must specify whether they are retained, down-weighted only in sensitivity analyses, or independently rescored.

### 8.3 Anchor exposure control

Repeated exposure can convert judgment into memorization. Therefore:

- maintain multiple anchors per region and domain;
- rotate anchor forms;
- do not disclose which items are anchors;
- monitor implausibly fast responses;
- retire overexposed anchors;
- keep retired anchors for audit and sensitivity analysis.

---

## 9. Anchor-bank versioning and audit trail

Every active bank version must include:

```text
bank_version
created_at_utc
blueprint_version
rubric_version
anchor_ids
anchor_content_digests
expert_review_summary
pilot_summary
retired_anchor_ids
change_log
approval_status
```

Changes requiring a new major version:

- score-region definition change;
- construct-definition change;
- reason-code ontology change;
- domain change;
- retention-rule change;
- new use of rater-adjusted rather than raw anchor consensus.

Changes requiring a minor version:

- addition or retirement of anchors under unchanged rules;
- typo corrections that do not alter meaning;
- metadata corrections.

All prior bank versions must remain reproducible.

---

## 10. Prohibited practices

The following are prohibited:

- declaring a synthetic anchor "gold" because its author intended a score;
- revising an anchor until it produces the desired score without documenting failed versions;
- selecting only anchors that create high apparent rater agreement;
- using condition labels during anchor selection;
- using participant responses from the confirmatory sample as anchors before primary analysis is frozen;
- rewarding raters for matching a target when the target itself is disputed;
- replacing disagreement with adjudicated consensus and then reporting only the consensus;
- treating anchor agreement as proof of construct validity;
- treating semantic fidelity as direct measurement of private thought, consciousness, or phenomenology.

---

## 11. Falsification and failure conditions

The anchor-bank approach is weakened or fails when:

- reviewers cannot distinguish adjacent score regions above chance or practical utility;
- anchors function differently across prompt domains;
- ratings remain driven by length, polish, emotion, or agreement after training;
- map-inadequacy flags are unreliable;
- reason codes do not explain numerical disagreement;
- recurring anchors improve apparent reliability while novel items remain unstable;
- category thresholds drift materially across rater cohorts;
- acceptable reliability requires so many raters that the full study is infeasible.

A failed anchor pilot is a measurement result. It must trigger rubric revision, category collapse, alternative outcome design, or abandonment of human-rated semantic fidelity as the primary outcome. It must not be hidden through selective anchor retirement.

---

## 12. Evidence basis

This protocol extends the parent reliability design and is grounded in established measurement principles:

- ICC form must match the rater model and intended use: Shrout & Fleiss (1979), DOI `10.1037/0033-2909.86.2.420`; McGraw & Wong (1996), DOI `10.1037/1082-989X.1.1.30`.
- Multiple error facets require explicit decomposition rather than one undifferentiated reliability coefficient: Brennan (1992), DOI `10.1111/j.1745-3992.1992.tb00260.x`.
- Writing ratings can exhibit severity, halo, central tendency, and range restriction despite training: Engelhard (1992), DOI `10.1207/s15324818ame0503_1`; Engelhard (1994), DOI `10.1111/j.1745-3984.1994.tb00436.x`; Myford & Wolfe (2003), *Journal of Applied Measurement*, 4(4).

These sources support the need to model and monitor rater behavior. They do not validate the specific EGC semantic-fidelity construct or the provisional retention thresholds in this protocol.

---

## 13. Immediate implementation sequence

1. Create the machine-readable anchor packet schema.
2. Draft 42 synthetic candidate packets from the frozen blueprint.
3. Run independent blind expert review.
4. Reject or revise ambiguous packets before pilot-rater exposure.
5. Generate a connected 60-response × 8-rater assignment schedule with four ratings per response, shared anchors, and blind repeats.
6. Run the pilot decision study before fixing production rater count or reliability gates.

The next executable artifact should be the anchor packet JSON Schema plus an assignment generator that verifies graph connectedness, domain balance, condition blindness, anchor coverage, and no same-participant paired-response exposure.