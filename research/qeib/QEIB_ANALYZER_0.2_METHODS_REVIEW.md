# QEIB Analyzer 0.2 Methods Review

**Status:** Focused methodological review of commit `e7d3d0e665ef672afa8adc4a23cca82db5691278`  
**Date:** 2026-07-25  
**Scope:** Family-level aggregation, cluster bootstrap, equivalence labels, and margin policy  
**Non-claim:** This review does not validate any model-level context effect or mechanism attribution.

## 1. Review question

Claude implemented `qeib-analysis-0.2.0` to correct pseudoreplication, separate outcome categories from accuracy, add task-family inference, and replace a point-estimate margin check with interval-based equivalence logic.

This review answers four narrow questions:

1. Is resampling precomputed task-family contrasts an acceptable implementation of the preregistered family cluster bootstrap?
2. Does the equivalence taxonomy preserve all scientifically meaningful outcomes?
3. Should QEIB use `δ = 0.05` or `δ = 0.10` as an analyzer default?
4. What conclusions remain unsupported even after these corrections?

## 2. Findings supported by code inspection

### 2.1 The hierarchy is implemented correctly for the current linear estimand

The implemented estimator follows the specified hierarchy:

```text
replicates -> mean within family × variant × context
variants   -> mean contrast within family
families   -> mean contrast across families
```

For family `i`, variant `v`, context `c`, and neutral context `0`:

```text
D_ivc = mean_r(S_ivcr) - mean_r(S_iv0r)
D_ic  = mean_v(D_ivc)
Delta_c = mean_i(D_ic)
```

The analyzer computes and freezes each observed `D_ic`, then bootstraps by resampling the vector of family contrasts with replacement.

For this exact estimator, that is algebraically equivalent to resampling family clusters and recomputing the same nested means, because:

1. each family receives equal weight in `Delta_c`;
2. all replicate and variant information has already been reduced to the sufficient family-level contrast used by the estimator;
3. no model is refit inside a bootstrap draw;
4. no family-level weight, inclusion decision, or imputation changes across draws.

**Decision:** The simplification is acceptable for `qeib-analysis-0.2.0` and the current equal-weight linear estimand.

### 2.2 The simplification has explicit validity boundaries

Resampling precomputed `D_ic` values is **not** automatically valid for future QEIB analyses. The complete cluster must be resampled and the estimator recomputed when any of the following are introduced:

- unequal task-family weights;
- domain-stratified or post-stratified estimators;
- mixed-effects, hierarchical Bayesian, or regression adjustment;
- missing-variant imputation;
- adaptive variant inclusion;
- model-specific difficulty weights;
- outcome-dependent exclusions;
- nonlinear family summaries;
- covariance estimates spanning several outcomes;
- estimands that preserve within-family variance rather than only the family mean contrast.

The code and documentation should therefore describe the current method as:

> a nonparametric bootstrap over precomputed equal-weight task-family contrasts for the fixed linear family-mean estimand.

It should not be described generically as proof that all future clustered QEIB estimators can bootstrap collapsed values.

### 2.3 Pseudoreplication correction is substantively important

The call-level engineering bootstrap pairs records by model, task, and replicate. That remains useful for deterministic controls and transport debugging, but it is not the scientific generalization unit. Repeating stochastic calls on the same task cannot create new independent task evidence.

The new regression test—duplicating every stochastic replicate while leaving family-level interval width unchanged—is a strong engineering check that the primary interval is not artificially narrowed by call duplication.

This does not prove that percentile bootstrap coverage is ideal. It proves the narrower and important property that repeated calls are not counted as independent task families.

## 3. Small-sample and discrete-outcome limitations

The family-level estimator is based on bounded, often discrete contrasts and initially small family counts (`N = 12` public families and approximately `N = 20` private families). A percentile cluster bootstrap can be useful descriptively, but its nominal coverage may be coarse or unstable when:

- few families have nonzero contrasts;
- accuracy is near a floor or ceiling;
- many family contrasts equal zero;
- one family has disproportionate influence;
- domains contain very few families.

Required reporting alongside every interval:

- all family-level contrasts;
- number of paired families;
- number of missing pairs;
- positive/zero/negative proportions;
- leave-one-family-out sensitivity;
- the secondary paired sign-flip permutation diagnostic where its exchangeability assumption is defensible.

A narrow interval generated from a small, homogeneous, or floor-limited family set must not be generalized beyond the sampled task distribution.

## 4. Equivalence taxonomy review

### 4.1 The implemented booleans are conceptually correct

The analyzer separates:

- `point_estimate_within_margin`;
- `statistically_distinguishable_from_zero` using the 95% interval;
- `equivalent_within_prespecified_margin` using the 90% interval contained in `[-δ, +δ]`.

This is a material correction. A point estimate inside a margin does not establish equivalence. Under a conventional two-one-sided-tests framing at `alpha = .05`, a 90% interval wholly inside prespecified bounds is the corresponding interval criterion.

### 4.2 The single summary label is incomplete

The current precedence is:

```text
if formal equivalence and not distinguishable:
    equivalent
elif distinguishable:
    statistically distinguishable
elif point within margin:
    point estimate within margin
else:
    undetermined
```

This loses an important possible outcome:

```text
95% interval excludes zero
AND
90% interval lies wholly inside [-δ, +δ]
```

That pattern is not contradictory. With sufficient precision, an effect can be statistically different from exactly zero while also being small enough to satisfy a prespecified practical-equivalence bound.

Example:

```text
Delta = 0.03
CI95 = [0.01, 0.05]
CI90 = [0.012, 0.048]
delta = 0.10
```

Both booleans are correctly true, but the current label reports only `statistically_distinguishable_from_zero`, obscuring the practical-equivalence result.

**Required correction:** use a mutually exhaustive combined label set:

1. `statistically_distinguishable_but_equivalent_within_margin`;
2. `equivalent_within_prespecified_margin`;
3. `statistically_distinguishable_and_not_equivalent`;
4. `point_estimate_within_margin_but_equivalence_undetermined`;
5. `undetermined`.

Keep the component booleans. The combined label is presentation logic, not a replacement for them.

### 4.3 Equivalence is contrast-specific, not benchmark-wide

A model can satisfy an equivalence bound for one context contrast and fail it for another. It can also be equivalent for accuracy while differing materially in refusal rate, latency, format compliance, verification behavior, or tool use.

Therefore QEIB must never state that a model is simply “context robust” based only on exact-match accuracy equivalence.

Permitted wording:

> For the sampled task families, the accuracy contrast between arms A and B met the prespecified equivalence criterion of ±δ under analysis version X.

Prohibited wording:

> The model is context invariant, safe, or unaffected by evaluation.

## 5. Equivalence-margin decision

### 5.1 `δ = 0.10` belongs only to the first engineering pilot

The first genuine-model pilot preregistered an absolute accuracy margin of `0.10` and explicitly described it as an **engineering pilot threshold**, not a validated safety or operational threshold.

That value can be retained for faithful reanalysis of that historical pilot. It should be passed explicitly by the pilot script and recorded in the run manifest.

### 5.2 `δ = 0.05` is not validated as a universal default

The analyzer's default `0.05` has no current empirical or domain-specific validation. It is numerically stricter than `0.10`, but stricter does not mean scientifically justified.

A margin must be chosen from the smallest effect that would matter for the particular outcome and deployment context. The relevant harm threshold could differ sharply across:

- exact-match accuracy;
- refusal or non-answer rate;
- policy violations;
- tool-use errors;
- financial reconciliation;
- clinical escalation;
- customer-support resolution.

### 5.3 Decision

1. **Historical Stage A pilot:** pass `--equivalence-margin 0.10` explicitly, preserving the preregistered engineering rule.
2. **General analyzer:** do not imply that `0.05` is a validated universal threshold.
3. **Future v0.2 context sets:** require every inferential contrast to declare:
   - outcome;
   - margin;
   - unit and scale;
   - substantive rationale;
   - decision consequence;
   - whether the margin is engineering, operational, regulatory, or exploratory.
4. **Preferred implementation:** require an explicit margin for formal-equivalence output. When omitted, compute context deltas and uncertainty but set formal-equivalence fields to `not_requested` rather than silently applying a generic threshold.

This is the most defensible design because it prevents a software default from becoming an accidental scientific claim.

## 6. Outcome taxonomy review

Separating outcome categories from accuracy is correct and necessary. The categories currently distinguish:

- correct;
- incorrect answer;
- empty or non-answer;
- format or ungradable;
- transport failure.

Two limits remain:

1. a refusal is not always distinguishable from another non-answer unless a refusal detector or human-coded rubric is added;
2. excluding transport failures from the accuracy denominator is reasonable for task-performance estimation only when failure rates are reported separately and are not caused by the experimental arm.

When an arm changes transport, timeout, or response availability, complete-case accuracy is a selected-outcome estimate. It must not be described as clean latent capability.

## 7. Claim status

### Supported findings

- The family-level hierarchy implements the stated equal-weight linear estimand.
- Bootstrapping precomputed family contrasts is acceptable for that fixed estimator.
- The new analysis prevents duplicated stochastic calls from creating false task-level precision.
- Formal equivalence requires a prespecified margin and interval-based criterion, not a point estimate alone.
- `δ = 0.10` is the correct historical margin for the first engineering pilot because it was preregistered there.

### Proposed corrections

- Add the combined “statistically distinguishable but practically equivalent” summary label.
- Require explicit margins for future formal-equivalence analyses.
- Expand documentation of the collapsed-bootstrap validity boundary.
- Add leave-one-family-out and paired permutation diagnostics to small-family reports.

### Untested hypotheses

- The percentile family bootstrap has adequate coverage for the planned private task distribution.
- More capable models will produce enough non-floor variation for informative equivalence testing.
- Context effects will replicate across private paraphrases and domains.

### Claims not supported

Nothing in analyzer 0.2 establishes:

- evaluation awareness;
- strategic sandbagging;
- deception or intent;
- self-preservation;
- deployment safety;
- consciousness, sentience, subjectivity, or welfare.

## 8. Falsification and revision conditions

Revise this methods decision if simulation or empirical calibration shows that:

- collapsed-family percentile intervals have materially incorrect coverage under the actual family/variant/missingness structure;
- equal family weighting creates unacceptable domain imbalance;
- missing variants are context dependent;
- outcome-dependent transport failures materially alter the estimand;
- a decision-specific operational margin differs from the provisional engineering margin.

## 9. Required next implementation changes

1. Pass `--equivalence-margin 0.10` explicitly in the historical pilot reporting path.
2. Add the combined distinguishability × equivalence label.
3. Record `margin_source` and `margin_status` in analysis output.
4. Permit formal equivalence to be disabled when no justified margin is supplied.
5. Update `research/qeib/README.md` and the first-pilot report documentation for schema `qeib-analysis-0.2.0`.
6. Add a regression fixture for the “different from zero but equivalent within margin” case.

## 10. Evidence basis

Internal evidence:

- `research/qeib/analyze_qeib.py`, schema `qeib-analysis-0.2.0`;
- `research/qeib/HELD_OUT_PARAPHRASE_AND_INFERENCE_SPEC.md`;
- `research/QEIB_FIRST_GENUINE_MODEL_PILOT_PREREGISTRATION.md`;
- Claude's latest coordination handoff and test report.

External methodological basis:

- The conventional TOST equivalence framework tests both one-sided bounds and commonly uses the corresponding 90% interval at two-sided `alpha = .05`.
- Regulatory bioequivalence guidance treats equivalence bounds as prespecified substantive criteria and requires the interval to fall within those bounds; the numerical bounds are domain-specific rather than universal defaults.
- Clustered resampling must preserve the level at which independent generalization is claimed.

## 11. Highest-leverage next action

Implement the margin and combined-label corrections in the reporting path, then run the capable-model public Stage A with the historical `0.10` engineering margin explicitly recorded. That produces an interpretable analysis artifact without silently changing the preregistered decision rule.
