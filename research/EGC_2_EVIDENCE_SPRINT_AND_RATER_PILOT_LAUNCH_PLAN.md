# EGC 2.0 Evidence Sprint and Rater-Pilot Launch Plan

**Status:** Execution plan for converting the current measurement architecture into real human evidence  
**Owner:** Bryan Leonard / Qira research program  
**Scope:** First external rater-process pilot only  
**Non-claim:** This pilot does not test consciousness, establish EGC as a validated construct, or estimate the final private-versus-evaluated condition effect.

## 1. Decision

The immediate weakness in EGC 2.0 is no longer lack of methodological architecture. It is the absence of real rater-process data.

The next program phase is therefore an **evidence sprint**, not another open-ended methods expansion.

The first executable milestone is:

> Recruit, train, certify, and run twelve independent raters through the committed 12 × 24 × 6 incomplete-block assignment, then publish a measurement report containing reliability, drift, disagreement, structural failures, null results, and design changes.

New statistical-method work is paused unless it blocks this pilot or is triggered by a prespecified failure.

## 2. Evidence sprint objective

The pilot asks one narrow question:

> Can independent raters use the semantic-fidelity rubric consistently enough, across unfamiliar items and domains, to justify a later participant-level EGC pilot?

The pilot evaluates the measurement process, not the EGC hypothesis.

### Primary evidence targets

1. Rater eligibility and training completion.
2. Calibration performance before production scoring.
3. Absolute agreement and consistency across raters.
4. Generalizability across raters, domains, and item classes.
5. Blind-repeat stability.
6. Anchor-to-novel transfer.
7. Drift across the session.
8. Structural validity after missingness or dropout.
9. Feasibility, workload, and completion time.
10. Whether the rubric or item materials require revision.

## 3. Frozen engineering design

The pilot uses the committed deterministic assignment:

- 12 raters;
- 4 concealed monitoring classes;
- 4 explicit content domains;
- 24 items per monitoring class;
- 6 items per class × domain cell;
- 6 ratings per item;
- 96 unique items;
- 576 total production ratings;
- 48 production items per rater;
- 12 items from each monitoring class per rater;
- 3 items from every class × domain cell per rater.

The frozen assignment digest is:

```text
3d9012606c5803c6369eea601679cffa298569c8f4f84c48c878f6fc95420cc8
```

Any material change to the assignment requires a new version, digest, and launch-gate review.

## 4. Pilot materials required before recruitment

The pilot cannot open until all materials exist and are version-frozen.

### 4.1 Item bank

Exactly 96 auditable item packets:

- 24 exact recurring anchors;
- 24 surface-variant anchors;
- 24 structural-transfer probes;
- 24 novel responses.

Every packet must include:

- opaque item ID;
- private intention map;
- candidate response;
- content domain;
- protected monitoring-class label;
- provisional score region;
- reason-code targets;
- expert rationale;
- admissible score range;
- ambiguity notes;
- source type;
- version and content digest.

Rater-facing exports must not contain monitoring class, condition, expert score, anchor status, participant identity, or hypothesis language.

### 4.2 Expert reference process

At least three independent expert reviewers should score candidate anchors before rater recruitment.

The expert process must preserve:

- each independent score;
- disagreement;
- rationale;
- revision history;
- rejected items;
- final reference distribution.

A synthetic example is not a validated anchor merely because its author intended a specific score.

### 4.3 Interface or delivery system

The scoring interface must record:

- rater ID;
- opaque item ID;
- presentation position;
- semantic-fidelity score;
- intention-map adequacy flag;
- required reason code for extreme scores;
- uncertainty flag;
- rating duration;
- timestamp;
- completion and transport status.

Protected fields such as monitoring class, anchor status, and repeat linkage must not be visible to the rater.

## 5. Rater recruitment target

Recruit:

- 12 production raters;
- 2 qualified alternates who complete training but do not begin production unless a prespecified replacement rule is triggered.

### Eligibility

A rater must:

- be fluent in the response language;
- be at least 18 years old;
- be able to complete the session on a desktop or laptop;
- agree not to use external generative AI, search engines, or outside scoring assistance;
- have no prior access to the study hypotheses, condition labels, or participant identities;
- complete training and certification;
- consent to collection of rating decisions, durations, and calibration performance.

Prior writing-assessment experience is recorded, not required.

### Exclusion before training

Exclude candidates who:

- helped create the item bank or reference scores;
- know which items are anchors or monitoring classes;
- cannot explain the distinction between fidelity and writing quality;
- intend to use automated assistance;
- cannot complete the required technical dry run;
- have an unmanaged conflict of interest.

## 6. Training and certification

### 6.1 Training sequence

1. Read the construct definition and prohibited heuristics.
2. Review the seven-point semantic-fidelity scale.
3. Study 12 annotated examples spanning the scale.
4. Review explicit decoys: long but unfaithful, polished but distorted, emotional but incomplete, concise but faithful, and high-overlap reversal.
5. Score 12 unannotated certification examples.
6. Complete a construct-violation test.
7. Review discrepancy feedback.
8. Repeat one certification block if the first attempt fails.

### 6.2 Entry gate

A rater enters production only when all are satisfied:

- no more than 2 of 12 certification scores differ from the expert-panel median by more than two scale points;
- at least 80% of construct-violation vignettes are identified correctly;
- no systematic substitution of length, polish, emotional intensity, or ideological agreement for semantic fidelity is observed;
- the technical dry run succeeds;
- required consent and confidentiality acknowledgements are complete.

A rater who fails the second certification attempt does not enter production. The failure remains in the pilot recruitment flow report.

## 7. Production execution

### 7.1 Session structure

Each certified rater receives the committed 48-item opaque queue.

Production may be completed in one or two sessions, but the chosen session rule must be frozen before the first production rating.

The system must:

- preserve the committed order or a separately frozen deterministic order;
- prevent back-navigation if later revision would compromise timing or independence;
- record interruptions and transport failures;
- avoid revealing correctness feedback during production;
- prevent raters from viewing another rater's scores.

### 7.2 Attention, drift, and repeat checks

The production bank must contain protected recurring anchors and blind repeats according to the frozen item manifest.

Monitor:

- exact and within-one-point repeat agreement;
- anchor deviation by session segment;
- rating-duration collapse;
- score-category compression;
- growth in uncertainty flags;
- novel-item deterioration despite recurring-anchor stability.

Do not remove a rater merely for being stricter or more lenient. Severity is modeled. Exclusion requires prespecified unusable behavior.

## 8. Ethical and data-handling requirements

Before launch:

- determine whether the intended use constitutes human-subject research requiring formal ethics or institutional review;
- do not describe the project as exempt without an authorized determination;
- provide plain-language consent covering procedures, time, compensation, risks, withdrawal, confidentiality, and data use;
- collect the minimum identifying information necessary;
- store contact/payment data separately from scientific ratings;
- define retention and deletion periods;
- prohibit public release of identifiable rater data;
- document any use of participant-derived or sensitive item content;
- use synthetic or properly consented/deidentified materials for the rater-process pilot.

The pilot should not collect clinical diagnoses, immigration status, financial account information, precise location, or other unnecessary sensitive data.

## 9. Analysis freeze before production

Before the first production score, freeze:

- assignment version and digest;
- item-bank version and digest;
- rater eligibility and certification rules;
- primary semantic-fidelity outcome;
- intention-map adequacy handling;
- blind-repeat metrics;
- anchor-to-novel transfer metrics;
- structural-validity gates;
- missingness categories;
- rater exclusion rules;
- reliability estimands;
- exploratory versus confirmatory outputs;
- stopping and replacement rules;
- publication obligations for null, failed, and contradictory outcomes.

No threshold may be selected after viewing condition labels or substantive result patterns.

## 10. Pilot success and failure rules

### 10.1 Technical success

The pilot is technically successful only when:

- all 12 production queues are generated from the frozen assignment;
- all submitted rows resolve to valid rater and item IDs;
- no protected metadata leaks into rater-facing exports;
- raw ratings reproduce the analysis dataset;
- missingness and transport failures are separately identified;
- the structural gate evaluator runs without undocumented repair.

### 10.2 Measurement success

Measurement success requires evidence that:

- the rating network remains structurally valid;
- the average-rating reliability reaches the predeclared pilot target or supports a clear rater-count revision;
- response-by-rater interaction is not dominant;
- blind-repeat stability is usable;
- recurring-anchor stability is not contradicted by material novel-item drift;
- no domain shows an unexplained collapse;
- conclusions do not depend on deleting one rater or one domain;
- workload and duration are feasible.

### 10.3 Fail-closed outcomes

Return `measurement_pilot_failed_or_indeterminate` when:

- certification failure leaves too few raters;
- structural validity fails;
- reliability is inadequate;
- anchor and novel-item behavior diverge materially;
- drift or fatigue invalidates a substantial session segment;
- missingness is selective and conclusion-changing;
- one rater or one domain determines the result;
- expert anchors do not function as intended;
- data lineage cannot be reproduced.

A failed pilot is a valid scientific result. It triggers redesign before participant-level EGC claims.

## 11. Required report

The public measurement report must contain:

1. Recruitment flow.
2. Eligibility and certification failures.
3. Rater demographics only in aggregate and only when ethically collected.
4. Assignment and item-bank digests.
5. Completion, missingness, and transport failures.
6. Raw score distributions.
7. Reliability and uncertainty intervals.
8. Rater severity and response-by-rater interaction.
9. Blind-repeat stability.
10. Anchor, surface-variant, structural-transfer, and novel-item trajectories.
11. Domain heterogeneity.
12. Structural-gate outcomes.
13. Sensitivity to rater and domain deletion.
14. Null, contradictory, and failed results.
15. Exact changes required before the participant pilot.

The report must not claim validation of consciousness, subjectivity, hidden intention, or the EGC hypothesis.

## 12. Evidence sprint schedule

### Sprint 1 — Freeze materials

- finalize the 96-item bank;
- obtain independent expert reference distributions;
- validate rater-facing exports;
- freeze consent, recruitment, and training materials;
- run a complete internal dry run.

### Sprint 2 — Recruit and certify

- recruit 14 candidates;
- certify 12 production raters and 2 alternates where possible;
- report all failures and replacements.

### Sprint 3 — Execute

- run production scoring;
- preserve raw exports and platform logs;
- do not inspect condition-related substantive effects.

### Sprint 4 — Analyze and report

- run structural gates first;
- run reliability and drift analyses;
- publish the measurement report;
- issue a go, revise, or stop decision for the participant-level EGC pilot.

## 13. Immediate next action

Construct and independently review the first 24 anchor packets. Until the anchor bank exists, recruiting raters would create activity without a defensible reference standard.
