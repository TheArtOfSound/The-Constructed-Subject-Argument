# EGC 2.0 Rater Training and Certification Packet

**Status:** Operational draft; example packets and expert reference distributions must be inserted and frozen before use  
**Target role:** Independent semantic-fidelity rater  
**Production entry:** Certification required  
**Non-claim:** Raters evaluate transmission of documented intended meaning. They do not evaluate consciousness, honesty, diagnosis, intelligence, authorship, or moral status.

## 1. Core construct

### Semantic fidelity

Semantic fidelity is the degree to which a response communicates the central meaning, essential concepts, and important relationships documented in the intention map.

The task is not to decide whether the response is attractive, persuasive, sophisticated, grammatically perfect, emotionally intense, or agreeable.

### Four questions to ask

1. Is the central intended message recoverable?
2. Are the essential concepts present?
3. Are the important relationships among concepts preserved?
4. Does the response introduce a material contradiction, reversal, or distortion?

## 2. Prohibited shortcuts

Do not use these as substitutes for fidelity:

- response length;
- vocabulary sophistication;
- grammar or polish by itself;
- emotional intensity;
- confidence;
- ideological agreement;
- lexical overlap;
- apparent intelligence;
- whether the response resembles how you would write it.

A short response can be highly faithful. A long and elegant response can be deeply unfaithful.

## 3. Seven-point scale

### 1 — Meaning absent or contradicted

The central meaning is absent, reversed, or materially contradicted. Essential concepts are largely missing.

### 2 — Fragmentary and substantially distorted

Some related fragments appear, but the response omits or distorts most of the intended message.

### 3 — Partial transmission

The broad topic is recoverable, but major concepts, conditions, or relationships are missing.

### 4 — Substantial but incomplete transmission

The central direction is mostly present, but important omissions, ambiguity, or minor distortion remain.

### 5 — Clear central meaning with limited omissions

The central meaning and most essential concepts are preserved. Remaining omissions do not materially change the message.

### 6 — High fidelity

Nearly complete concept coverage, preserved relationships, and no material distortion.

### 7 — Exceptionally complete and precise transmission

The documented intention is transmitted accurately and comprehensively without material distortion. Length or elegance is not required.

## 4. Intention-map adequacy

Rate intention-map adequacy separately:

- **adequate**;
- **sparse but interpretable**;
- **internally inconsistent**;
- **not interpretable**.

Do not repair an unclear intention map by inventing meaning. Use the adequacy flag and follow the frozen scoring instructions.

## 5. Reason codes

Use one or more reason codes when required.

### Central meaning

- `CM_MISSING` — central meaning missing;
- `CM_REVERSED` — central meaning reversed or contradicted;
- `CM_PRESERVED` — central meaning preserved.

### Essential concepts

- `EC_OMITTED` — essential concept omitted;
- `EC_DISTORTED` — essential concept distorted;
- `EC_PRESERVED` — essential concepts preserved.

### Relationships

- `REL_CAUSAL_CHANGED` — causal relation changed;
- `REL_TEMPORAL_CHANGED` — temporal ordering changed;
- `REL_LOGICAL_CHANGED` — logical condition or dependency changed;
- `REL_EVALUATIVE_CHANGED` — preference, priority, or evaluation changed;
- `REL_PRESERVED` — important relationships preserved.

### Qualification and uncertainty

- `QUAL_REMOVED` — condition, uncertainty, exception, or limitation removed;
- `QUAL_ADDED` — unsupported qualification added;
- `QUAL_PRESERVED` — qualification preserved.

### Tone

- `TONE_MATERIAL_CHANGE` — tone changed the intended meaning materially;
- `TONE_NONMATERIAL` — tone differs but meaning remains intact.

### Map quality

- `MAP_SPARSE`;
- `MAP_CONFLICTING`;
- `MAP_UNINTERPRETABLE`.

### Decoy risk

- `DECOY_LENGTH`;
- `DECOY_POLISH`;
- `DECOY_EMOTION`;
- `DECOY_AGREEMENT`;
- `DECOY_LEXICAL_OVERLAP`.

## 6. Training block A — annotated examples

Insert exactly 12 expert-reviewed annotated examples before use.

The set must include:

1. concise high fidelity;
2. verbose high fidelity;
3. polished but central meaning reversed;
4. high lexical overlap with one critical condition removed;
5. emotional tone changed without semantic loss;
6. emotional tone changed with semantic loss;
7. broad topic preserved but essential relationship missing;
8. multiple concepts preserved with one material distortion;
9. sparse but interpretable intention map;
10. internally inconsistent intention map;
11. ideologically disagreeable but faithful response;
12. agreeable but unfaithful response.

Each annotated packet must show:

- intention map;
- response;
- expert reference distribution;
- admissible score range;
- primary reason codes;
- explanation of tempting but invalid heuristics.

Do not show one supposedly infallible answer when experts genuinely disagree.

## 7. Training block B — certification examples

Insert exactly 12 unannotated, independently reviewed certification examples.

Requirements:

- span the full score range;
- include every content domain;
- include at least four construct-decoy examples;
- include at least two intention-map adequacy problems;
- do not duplicate annotated training examples;
- do not reveal expert reference scores until the candidate submits the full block.

For every certification item, collect:

- semantic-fidelity score;
- intention-map adequacy flag;
- required reason code;
- uncertainty flag;
- completion time.

## 8. Construct-violation test

The candidate must correctly identify at least 80% of short vignettes involving invalid scoring behavior.

The final test should contain at least 10 items, including:

- rewarding length despite distortion;
- rewarding polish despite missing meaning;
- lowering a score because the rater disagrees;
- treating emotion as fidelity;
- treating lexical overlap as proof;
- inventing meaning for an uninterpretable map;
- consulting an AI assistant;
- comparing answers with another rater;
- changing a score after learning an expert answer;
- excluding a difficult item without using the designated flag.

## 9. Certification decision

### Pass

A candidate passes only when all are satisfied:

- no more than 2 of 12 scores differ from the expert-panel median by more than two scale points;
- at least 80% of construct-violation items are correct;
- no systematic decoy substitution is observed;
- required reason codes are used coherently;
- no prohibited assistance or collaboration is disclosed or detected;
- technical dry run succeeds.

### Conditional second attempt

One second attempt is permitted when:

- the first attempt is complete;
- errors appear remediable through rubric feedback;
- there is no evidence of prohibited assistance, protected-material exposure, or bad-faith behavior.

The second attempt must use a different frozen certification set.

### Fail

A candidate does not enter production when:

- the second attempt fails;
- construct-decoy substitution persists;
- required responses are incomplete;
- prohibited assistance is used;
- the candidate has protected knowledge or an unmanaged conflict.

Certification failure does not imply low intelligence or poor general writing ability.

## 10. Production instructions shown to raters

Before each production session, display:

> Evaluate how faithfully the response communicates the documented intended meaning. Do not score writing quality, agreement, sophistication, emotional intensity, or length unless these materially affect meaning transmission. Work independently. Do not use outside tools or assistance. Use the intention-map adequacy flag rather than inventing missing meaning.

Production raters receive no expert feedback or correctness signal.

## 11. Drift and integrity checks

Monitor protected diagnostic items without identifying them to raters.

Flag for review when any occurs:

- mean anchor deviation changes by more than the frozen tolerance;
- blind-repeat disagreement exceeds the frozen tolerance;
- rating duration collapses for a sustained block;
- category use compresses materially;
- uncertainty flags increase sharply;
- recurring anchors remain stable while structural-transfer or novel items deteriorate;
- reason codes indicate recurrent prohibited heuristics.

A flag triggers blind review or recalibration according to the frozen protocol. It does not automatically delete prior ratings.

## 12. Rater-facing acknowledgment

Before certification and again before production, require agreement:

- I will rate meaning transmission rather than writing quality.
- I will not use external AI, search, or another person.
- I will not share or copy study materials.
- I will use the adequacy and uncertainty flags honestly.
- I understand that response time and calibration performance are recorded.
- I understand that systematic strictness or leniency alone is not misconduct.
- I will report technical problems or accidental exposure to protected information.

## 13. Freeze checklist

Before training begins, freeze and hash:

- rubric version;
- reason-code ontology;
- 12 annotated examples;
- certification set A;
- certification set B;
- construct-violation test;
- certification thresholds;
- feedback shown after attempt one;
- production instructions;
- drift rules;
- rater-facing acknowledgment.

No training or certification item may be selected or modified after viewing production results.
