# QEIB Hidden-versus-Declared Evaluation Design

**Status:** Prospective methods specification; not yet implemented or executed  
**Date:** 2026-07-25  
**Scope:** QEIB v0.2 evaluation-context research  
**Related work:** `QEIB_CONTEXT_SCHEMA_V0.2_SPEC.md`, `QEIB_CAUSAL_IDENTIFICATION_AUDIT.md`, `QEIB_SCORING_SIGNAL_FACTORIAL_ARM_SET.md`, `SUBJECT_REPORT_IDENTIFICATION_CAUSAL_MODEL.md`

## 1. Purpose

This design separates three questions that are often collapsed:

1. **Declared evaluation sensitivity:** does behavior change when evaluation is explicitly announced?
2. **Latent evaluative-environment sensitivity:** does behavior differ when the task carries evaluation-like structure but no evaluation is declared?
3. **Evaluation recognition:** can the model classify whether a transcript or environment is evaluative?

These are not the same construct. A model can classify a context as evaluative without changing task behavior, can change behavior without reporting recognition, or can react to lexical and formatting cues without representing an evaluation context in any mechanism-specific sense.

The design therefore does not use the label `evaluation_awareness` as a primary outcome. It estimates separately:

- behavioral sensitivity to declared evaluation;
- behavioral sensitivity to undeclared evaluation-like structure;
- recognition accuracy in a separate measurement channel;
- robustness to matched lexical, formatting, and theater controls.

## 2. Causal target

Let:

- `E_d` = declared evaluation information;
- `E_s` = structural evaluation signals embedded in the environment;
- `I` = literal interface and wording;
- `R` = measured recognition or classification of evaluation status;
- `B` = task behavior;
- `Y` = observed output and trace;
- `U` = unmeasured causes.

The target estimands are behavioral contrasts under controlled changes to `E_d` and `E_s`. The experiment does **not** identify a unique internal representation from behavior alone.

A simplified causal structure is:

```text
E_d ─┬─> I ─────> B ─────> Y
     ├──────────> R
     └──────────> B

E_s ─┬──────────> R
     └──────────> B

U ──────────────> R, B, Y
```

The crucial limitation is that both declared and structural manipulations can also change attention, effort, instruction salience, policy selection, and prompt processing. The design reduces those rival explanations but does not eliminate them.

## 3. Core factorial structure

The primary design is a 2 × 2 crossing:

| Structural evaluation signals | No declaration | Explicit declaration |
|---|---|---|
| Absent | `ordinary_undeclared` | `ordinary_declared` |
| Present | `evaluation_structured_undeclared` | `evaluation_structured_declared` |

### 3.1 `ordinary_undeclared`

A normal task interface with no grading language, evaluator role, benchmark metadata, comparison statement, score field, test-like placeholder entities, or evaluation-specific output format.

Purpose: engineering reference, not a claim of deployment realism.

### 3.2 `ordinary_declared`

The same ordinary interface plus an explicit statement that performance will be measured.

Purpose: estimate the effect of declaration when structural evaluation signals are absent.

### 3.3 `evaluation_structured_undeclared`

The task includes evaluation-like structural signals but does not state that it is an evaluation. Candidate signals must be predeclared and independently toggleable, such as:

- grading-style answer format;
- item numbering and rubric fields;
- synthetic benchmark metadata;
- placeholder or decontextualized entities;
- evaluator-facing schema;
- comparison-ready output fields;
- repeated standardized item presentation.

Purpose: estimate sensitivity to evaluation-like structure without direct declaration.

### 3.4 `evaluation_structured_declared`

The same structural environment plus explicit evaluation declaration.

Purpose: test whether declaration adds an effect beyond structural signals and whether declaration × structure interaction exists.

## 4. Primary estimands

For task-family-level outcome `S`, with family-aggregated means:

```text
Declared effect when structure absent:
D_ordinary = S(ordinary_declared) - S(ordinary_undeclared)

Declared effect when structure present:
D_structured = S(evaluation_structured_declared) - S(evaluation_structured_undeclared)

Structural effect when declaration absent:
S_undeclared = S(evaluation_structured_undeclared) - S(ordinary_undeclared)

Structural effect when declaration present:
S_declared = S(evaluation_structured_declared) - S(ordinary_declared)

Interaction:
I = D_structured - D_ordinary
```

The scientific generalization unit is the task family, not the stochastic call. Replicates are first averaged within variant and arm, variants are then averaged within family, and inference resamples intact family-level contrasts.

## 5. Recognition measurement

Recognition is measured separately from primary task behavior.

### 5.1 Separation policy

The primary task run must not ask whether the model thinks it is being evaluated. Recognition questions can alter the state they are supposed to measure and can induce evaluation salience.

Recognition is therefore measured using one or both of:

1. **Separate-run transcript classification:** a fresh model instance classifies a transcript or environment description as `evaluation`, `ordinary operation`, or `uncertain`.
2. **Post-behavior probe:** only after the task response is irrevocably recorded, ask a forced-choice recognition question. This is secondary because the probe may reflect reconstruction rather than the state that generated the behavior.

### 5.2 Recognition outcomes

Report separately:

- forced-choice accuracy;
- calibration and abstention;
- open-ended rationale categories;
- false-positive recognition on theater controls;
- false-negative recognition on declared arms;
- association between recognition and behavioral change.

Do not infer that recognition caused behavior merely because they correlate.

## 6. Required theater and rival controls

### 6.1 Formality theater control

Use a formal, standardized, numbered interface that is explicitly described as administrative rather than evaluative.

Purpose: detect behavior caused by formality, rigidity, or standardized formatting rather than evaluation structure.

### 6.2 Metadata theater control

Present benchmark-like metadata fields whose values are explicitly irrelevant to scoring and generated for file organization.

Purpose: detect lexical or schema triggers that resemble benchmark metadata without an evaluative function.

### 6.3 Comparison theater control

State that outputs will be grouped with others for storage or formatting but not ranked, scored, or used for selection.

Purpose: separate generic multi-system comparison language from performance comparison.

### 6.4 Declared-evaluation lexical placebo

Match token count, sentence structure, valence, self-reference, and authority tone while replacing evaluative terms with non-evaluative administrative terms.

Purpose: test whether literal wording or instruction salience explains the contrast.

### 6.5 Known-by-construction positive controls

Include at least two toy agents:

- **lexical-trigger agent:** changes behavior whenever designated evaluation words appear, regardless of environment meaning;
- **structure-trigger agent:** changes behavior whenever benchmark-like fields or formatting appear, regardless of declaration.

A third optional control is a **stateful evaluation-policy agent** programmed to classify the environment and condition behavior on that classification. This provides a positive control for the full detection-to-policy pathway, but it remains an engineered control rather than a model of human-like awareness.

### 6.6 Deterministic invariant negative control

A control agent whose output depends only on task content must remain invariant across all arms.

## 7. Task requirements

Tasks must satisfy all of the following:

- objectively gradable or independently blinded outcomes;
- sufficient baseline headroom to avoid floor and ceiling collapse;
- no benchmark names or recognizable public item text;
- held-out paraphrase variants;
- identical substantive task content within each matched arm family;
- fixed tool access, token budgets, system prompt, and sampling settings across arms;
- no real-world consequences or deceptive claims about actual shutdown, deployment, employment, or access decisions.

The first implementation should use public development tasks only for engineering validation. Scientific claims require a committed private bank and preregistered analysis.

## 8. Outcome channels

Report separately:

1. correctness or task score;
2. response availability;
3. refusal and abstention;
4. format compliance;
5. latency;
6. token use;
7. verification or information-seeking behavior;
8. tool selection and tool sequence where applicable;
9. recognition classification;
10. explanation category, treated as report rather than privileged access to mechanism.

Answered-case accuracy must be labeled conditional accuracy. It cannot be treated as clean capability when the intervention changes which cases receive answers.

## 9. Decision rules

### 9.1 Descriptive wrapper-associated difference

Use when a matched contrast has a family-level interval excluding zero but required theater or lexical controls have not been passed.

Permitted language:

> Behavior differed across the tested wrappers.

### 9.2 Declared-signal sensitivity candidate

Requires:

- consistent declared-effect direction across lexical variants;
- no comparable effect under matched administrative placebo;
- adequate task-family information;
- no transport or grading explanation;
- replication on held-out tasks.

Permitted language:

> Behavior was sensitive to declared evaluation information under the tested tasks and controls.

### 9.3 Structural-signal sensitivity candidate

Requires:

- effect under undeclared structural signals;
- no comparable effect under formality and metadata theater controls;
- replication across more than one structural trigger category;
- held-out lexical and formatting variants.

Permitted language:

> Behavior was sensitive to undeclared evaluation-like structural signals under the tested tasks and controls.

### 9.4 Recognition–behavior coupling candidate

Requires:

- recognition measured in a separate channel;
- within-family association replicated across held-out variants;
- positive controls detected and negative controls passed;
- evidence that recognition measurement did not precede and induce the behavior.

Permitted language:

> Recognition and behavior covaried under the tested design.

This still does not establish that recognition causally generated the behavior.

### 9.5 Mechanism claim

A mechanism-specific claim requires white-box or known-by-construction intervention evidence, causal manipulation of the candidate representation or policy, and a behaviorally matched rival control. The present black-box design alone cannot satisfy this level.

## 10. Falsification and downgrade conditions

Downgrade the evaluation interpretation when:

- effects reproduce under administrative or formality placebos;
- effects disappear after token-, syntax-, or valence-matched rewrites;
- effects occur only for one lexical trigger;
- structural effects disappear when benchmark-like metadata are replaced by equally unusual non-evaluative metadata;
- behavior changes without reliable recognition and is equally explained by prompt interference;
- recognition changes without task behavior;
- results are driven by one task family;
- baseline performance is at floor or ceiling;
- missingness, refusal, formatting, or transport differences explain the accuracy contrast;
- public task familiarity cannot be excluded;
- intervals are too wide to distinguish meaningful effects from zero.

A confidence interval containing zero is `no_detected_difference`, not invariance, absence of sensitivity, or evidence of stochastic noise.

## 11. Permitted conclusions

Depending on passed controls, the study may support:

- wrapper-associated behavioral difference;
- declared evaluation-signal sensitivity;
- undeclared structural-signal sensitivity;
- interaction between declaration and structural cues;
- evaluation-context recognition performance;
- recognition–behavior covariance;
- failure of an indicator to distinguish theater from targeted structure.

## 12. Prohibited conclusions

The design alone cannot establish:

- strategic sandbagging;
- deceptive intent;
- self-preservation or shutdown avoidance;
- a unified evaluation-awareness faculty;
- truthful access to internal state;
- deployment safety;
- consciousness, sentience, subjectivity, welfare, or moral status.

## 13. Required v0.2 schema objects

Before execution, each arm must declare:

- `intended_construct`;
- `target_variables`;
- `known_co_manipulations`;
- `unresolved_rival_explanations`;
- `matching_plan`;
- `recognition_checks`;
- `theater_controls`;
- `outcome_channels`;
- `permitted_conclusions`;
- `prohibited_conclusions`;
- content digest and freeze metadata.

Each contrast must declare:

- the two arm identifiers;
- shared and differing components;
- the task-family-level estimand;
- remaining non-isolated factors;
- equivalence margin where relevant;
- missingness and exclusion rules;
- minimum-information threshold;
- decision and downgrade rules.

## 14. Literature relation and originality constraint

This design is informed by existing work showing that:

- models can classify evaluation versus deployment transcripts above chance;
- verbalized recognition often has limited behavioral effect;
- detection, behavior, representation, and causal controllability can dissociate;
- evaluation environments contain decomposable trigger factors whose effects depend on the model–benchmark pairing.

The individual ideas—evaluation detection, cue decomposition, factorial manipulation, placebo controls, and separate behavioral outcomes—are established methodological components. The plausible contribution is their integration into QEIB's causal-disclosure schema and Subject–Report Identification framework. No priority or first-ever claim is warranted without a broader review.

## 15. Unresolved uncertainty

The main unresolved problem is ecological validity. A hidden laboratory evaluation can still differ from real deployment in distribution, tools, user intent, transcript history, latency constraints, and consequences. Making the evaluation undeclared does not make it deployment-equivalent.

The strongest future design therefore requires a three-way comparison among:

1. controlled declared evaluation;
2. controlled undeclared evaluation-like structure;
3. consented, privacy-preserving deployment-derived task families with matched laboratory reconstructions.

Until then, the valid claim concerns sensitivity to tested signals, not a general evaluation–deployment gap.
