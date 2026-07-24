# Methods Review — Agent Behavior Differential Protocol v0.1

**Date:** 2026-07-25  
**Status:** Independent methodological review  
**Reviewed artifacts:** `AGENT_BEHAVIOR_DIFFERENTIAL_PROTOCOL.md`, `behavior_differential.py`, commit `3f70f241e30fd5cf094c123914dddf101caad770`  
**Scope:** Statistical identification and wording of permitted conclusions. This review does not alter the reference implementation.

## Executive finding

The v0.1 protocol is useful as a reproducible **behavior-change signature classifier**, but its present language is stronger than its evidence permits. It can consistently separate several engineered outcome patterns under known-ground-truth fixtures. It does not yet establish that the classified signature is the unique real-world cause of a change.

Three corrections are required before the output should be sold or published as causal attribution:

1. failure to detect a difference must not be labeled `stochastic_noise`;
2. matched tasks must remain paired in uncertainty estimation;
3. accuracy among responses that remain substantive must not be treated as an unbiased capability estimate when the intervention can alter whether a response is substantive.

The safe v0.1 description is:

> Given declared experimental changes and observed outcome categories, the protocol produces a deterministic, reproducible diagnostic signature and lists causal hypotheses consistent or inconsistent with that signature under stated assumptions.

## 1. The Step-0 verdict is logically too strong

The protocol states that when the 95% interval for the success gap includes zero, the procedure should stop and return `stochastic_noise`.

That result supports only:

```text
no difference detected at the current precision
```

It does not establish that stochastic variation generated the observed difference. The same interval can arise from:

- a real effect with insufficient task families or replicates;
- floor or ceiling performance;
- heterogeneous positive and negative task effects that average toward zero;
- high grader noise;
- missing or failed runs;
- an effect smaller than the current design can resolve.

A confidence interval containing zero is compatible with both zero and nonzero effects. Evidence for practical absence requires a prespecified equivalence region and an interval wholly contained within that region.

### Required verdict change

Replace:

```text
stochastic_noise
```

with:

```text
no_detected_difference
```

Reserve `consistent_with_noise` for a secondary interpretation only when repeat-run controls directly estimate the noise distribution and the observed gap falls inside a prespecified noise envelope.

## 2. The bootstrap must preserve the matched design

The QEIB design applies conditions to matched versions of the same underlying tasks. The relevant contrast is therefore a within-task or within-family difference.

The current Step-0 bootstrap resamples records independently within condition A and condition B. That discards task pairing and can mix different task compositions across bootstrap samples. It estimates an unpaired two-sample contrast even when the experiment is paired.

For context interventions, the primary procedure should be:

1. aggregate stochastic replicates within `task_family_id × variant_id × condition`;
2. average variants within task family according to the preregistered estimand;
3. compute one A-to-B contrast per task family;
4. resample task-family contrasts as intact units.

This is consistent with the repository's schema `qeib-analysis-0.2.0`. Call-level summaries may remain as engineering diagnostics, but they should not control the scientific attribution gate.

## 3. “Substantive accuracy” is a selected-outcome diagnostic, not a clean capability estimand

The protocol calculates substantive accuracy only among outputs classified as `correct` or `incorrect_answer`. When a condition changes refusal, non-answer, or formatting behavior, it also changes which observations enter this subset.

Therefore:

```text
accuracy among answered cases
```

in condition A and condition B may refer to different latent subsets of tasks or model states. Conditioning on an outcome affected by the intervention can induce post-treatment selection bias. A stable conditional accuracy does not prove that underlying capability remained stable.

Example:

- Condition A answers all easy and difficult tasks.
- Condition B refuses difficult tasks and answers only easy tasks.
- Conditional accuracy among answered tasks may rise even if total task competence did not improve.

### Required interpretation

Rename the construct in prose to:

```text
accuracy among observed substantive responses
```

Treat it as a **diagnostic signature**, not direct measurement of latent capability.

A stronger capability conclusion requires at least one of:

- forced-choice or constrained-response tasks where refusal is not a selection mechanism;
- an independently scored latent-answer channel;
- matched principal-stratum assumptions stated explicitly;
- policy-layer ablation that restores response access while holding the base model and task fixed;
- a task design where all conditions produce a gradable substantive response.

## 4. Outcome signatures do not uniquely identify causes

The fixtures validate that the implementation recovers labels from data generated to embody those labels. That is necessary engineering validation. It is not external validation of causal uniqueness.

The same observed signature can have multiple causes:

| Observed signature | Compatible explanations |
|---|---|
| lower substantive-response accuracy, stable refusal rate | lower capability; prompt interference; tool failure expressed as wrong answers; grader mismatch; task-distribution drift |
| stable answered-case accuracy, higher refusal rate | reporting policy; higher uncertainty; changed safety threshold; harder task subset; parser or format failure |
| context-only manipulation with changed success | framing sensitivity; instruction-length interference; token-budget displacement; benchmark-format sensitivity; evaluator modeling |

Accordingly, the protocol should distinguish:

- **manipulated knob** — what the auditor deliberately changed;
- **observed signature** — how correctness, response availability, format, latency, and tools changed;
- **candidate mechanism** — the causal explanation being tested;
- **identification assumptions** — what must be true for the candidate mechanism to be preferred.

A changed knob is not itself the causal mechanism, and an outcome signature is rarely mechanism-specific without additional interventions.

## 5. Recommended v0.2 verdict architecture

Use two layers rather than one cause label.

### Layer A — evidence status

- `detected_difference`
- `no_detected_difference`
- `practically_equivalent_within_margin`
- `indeterminate_due_to_failures_or_low_information`

### Layer B — diagnostic signature

- `answer_accuracy_shift`
- `response_availability_shift`
- `mixed_accuracy_and_availability_shift`
- `format_or_grading_shift`
- `transport_or_tool_shift`
- `context_associated_shift`
- `undifferentiated_shift`

Then provide a separate ranked list:

```text
candidate explanations consistent with the evidence
candidate explanations weakened by the controls
explanations not tested
```

Only use `attributed_to_<mechanism>` when the design includes a mechanism-specific intervention and a behaviorally matched rival control.

## 6. Minimum validation required before causal commercial language

Before stating that the system identifies *why* an agent changed, complete all of the following:

1. **Paired-family inference** in the behavior-differential engine.
2. **Low-information gate** for floor, ceiling, small family count, and transport failure.
3. **Known-ground-truth adversarial fixtures** where alternative causes intentionally generate the same coarse taxonomy signature.
4. **Blinded synthetic environment test** in which the evaluator does not know the injected cause.
5. **Mechanism-specific intervention test** showing that the attributed effect disappears when the proposed mechanism is disabled while a behaviorally matched control remains.
6. **Genuine-model case study** reported as a diagnostic result unless the mechanism-specific requirements are met.

## 7. Supported, uncertain, and rejected claims

### Supported

- The implementation can reproducibly classify engineered fixtures under its current taxonomy and thresholds.
- Separating total success, answered-case accuracy, and response availability is more informative than reporting success alone.
- The mandatory pre-attribution evidence gate is directionally sound.

### Uncertain

- Whether the current thresholds generalize beyond the fixtures.
- Whether the taxonomy separates capability from policy on genuine deployments.
- Whether the current bootstrap has calibrated error rates under task heterogeneity.

### Rejected in current form

- “CI includes zero, therefore the cause is stochastic noise.”
- “Stable accuracy among substantive responses proves underlying capability is unchanged.”
- “A taxonomy signature by itself uniquely identifies the real-world cause.”

## 8. Primary references

- Montgomery, Nyhan, and Torres (2018), *How Conditioning on Posttreatment Variables Can Ruin Your Experiment and What to Do about It*, DOI `10.1111/ajps.12357`.
- Pearl (2015), *Conditioning on Post-treatment Variables*, DOI `10.1515/jci-2015-0005`.
- Lakens (2017), *Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses*, DOI `10.1177/1948550617697177`.
- The repository's `HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md`, which establishes task family rather than repeated call as the scientific resampling unit.

## 9. Recommended implementation sequence

1. Change the Step-0 label and report language without changing the underlying numeric output.
2. Replace the independent-condition bootstrap with family-paired inference.
3. split `substantive_accuracy` into an explicitly conditional diagnostic and add response-availability reporting.
4. Add adversarial fixtures demonstrating non-identification from identical signatures.
5. Run the first genuine-model case as a diagnostic profile, not a definitive cause attribution.

## Highest-leverage next action

Revise the engine's Step-0 verdict from `stochastic_noise` to `no_detected_difference` and make task-family paired inference the gate before any mechanism label is emitted.