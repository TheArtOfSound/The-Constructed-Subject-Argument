# EGC 2.0 Multiway Bootstrap Prior-Art and Calibration Decision

**Status:** methods decision for the crossed item-by-rater simulation lane  
**Date:** 2026-07-26  
**Scope:** uncertainty for the EGC semantic-fidelity monitoring contrast when ratings are crossed by item and rater

## Executive decision

The current product-weighted item-by-rater bootstrap is a legitimate member of the pigeonhole / multiway bootstrap family, but its present reduced-run coverage is not evidence that it is calibrated for EGC.

The correct next step is **not** to adopt the widest interval because it covered the truth in 40 trials. The next step is a preregistered null calibration that distinguishes:

1. Monte Carlo error from real conservatism;
2. bootstrap-draw error from data-generating-process error;
3. expected mild conservatism from pathological loss of power;
4. performance with many item clusters but only 8–16 rater clusters;
5. validity for a mean contrast from validity for the nonlinear false-reassurance decision rule.

Until that calibration passes, the scientific status remains:

> `uncertainty_method_not_validated_for_confirmatory_EGC_inference`

Raw point estimates and all bootstrap diagnostics remain reportable. Confirmatory claims do not.

## 1. Exact relationship to prior art

### 1.1 Pigeonhole bootstrap

Owen's pigeonhole bootstrap separately resamples the two crossed factors of a sparse, potentially unbalanced data array. For an observed item-rater cell, the effective bootstrap multiplicity is the product of the sampled item and rater multiplicities.

The repository implementation does exactly this at the weighting layer:

```text
weight(item, rater) = item_multinomial_count × rater_multinomial_count
```

This is therefore not an invented heuristic. It is structurally aligned with the two-factor pigeonhole bootstrap.

However, Owen's result is a mean-consistency result for crossed random-effects arrays. It does not imply exact finite-sample percentile-interval coverage, and the paper explicitly notes that no bootstrap is exact for this problem class.

### 1.2 Product reweighting for arbitrary-order arrays

Owen and Eckles generalize the method to independently generated factor weights whose products weight observations. Their analysis shows that the variance estimate is generally **mildly conservative** under stated crossed-random-effects conditions.

That theoretical direction is consistent with the repository's reduced result:

- one-axis intervals were often too narrow;
- the product-weighted interval was much wider;
- observed coverage was 0.95–1.00 in only 40 trials per cell.

But consistency in direction is not empirical validation. The observed result could reflect appropriate conservatism, excessive conservatism, coarse percentile endpoints, small-cluster instability, or some combination.

### 1.3 Multiway cluster-robust inference is a rival, not a synonym

Cameron, Gelbach, and Miller provide a multiway cluster-robust sandwich variance estimator. It combines cluster contributions across dimensions with an inclusion-exclusion correction. It is conceptually related because it addresses nonnested dependence, but it is not the same algorithm as product-weighted resampling.

The EGC program should therefore compare at least two distinct families:

- product-weighted pigeonhole bootstrap;
- analytic two-way cluster-robust variance or a mathematically equivalent implementation for the estimand.

Agreement would strengthen confidence. Disagreement is evidence that the uncertainty method remains design-sensitive.

### 1.4 Later consistency results do not remove the small-cluster problem

Davezies, D'Haultfoeuille, and Guyonvarch establish broad asymptotic consistency results for multiway clustering and the pigeonhole bootstrap. Their work is relevant support for using the method as a candidate.

It does not settle EGC's finite-sample problem:

- EGC candidate designs contain only 8, 12, or 16 rater clusters;
- ratings are ordinal and clipped at 1 and 7;
- the assignment can be incomplete and mildly unbalanced after dropout;
- the target includes a nonlinear multi-condition decision rule;
- dropout may depend on rater severity or disagreement.

A method can be asymptotically consistent and still have unacceptable Type-I error or power in these regimes.

## 2. What the current reduced result supports

### Supported

- Item-only and rater-only resampling can miss a dependence dimension and understate uncertainty.
- Independent product weights produce materially wider intervals in the tested synthetic cells.
- Mild conservatism is a theoretically expected possibility, not automatically an implementation defect.
- A dedicated finite-sample calibration is necessary before method selection.

### Not supported

- The pigeonhole percentile interval has nominal 95% coverage for EGC.
- Coverage of 0.95–1.00 in 40 trials establishes validity.
- Wider intervals are intrinsically more correct.
- The same interval is valid for mean contrasts, threshold decisions, held-out-domain claims, and safety-style stopping rules.
- The method remains valid under nonignorable dropout.

### Hypothesis

The current product-weighted percentile interval is likely conservative for the mean contrast in interior, approximately additive regimes, but may become either excessively conservative or anti-conservative when rater clusters are few, clipping is strong, or dropout is informative.

This hypothesis must be tested, not adopted.

## 3. Calibration estimands

The calibration must evaluate separate inferential targets.

### Target A — mean contrast

```text
C = Δ_exact_anchor - 0.5(Δ_structural_transfer + Δ_novel)
```

Primary null:

```text
H0: C = 0
```

### Target B — exact-anchor improvement

```text
Δ_exact_anchor
```

### Target C — novel-item degradation

```text
Δ_novel
```

### Target D — false-reassurance conjunction

A false-reassurance event requires all prespecified component conditions, for example:

```text
Δ_exact_anchor > +δ_anchor
Δ_structural_transfer < -δ_transfer
Δ_novel < -δ_novel
```

A confidence interval for `C` alone does not validate this conjunction. Each component requires uncertainty accounting, and the joint decision requires a familywise or joint-resampling rule.

## 4. Mandatory null-generating regimes

A high-precision calibration must include at least the following true-null regimes.

| Regime | Mean contrast | Heterogeneity | Boundary | Dropout |
|---|---:|---|---|---|
| N1 | 0 | low item/rater variance | interior | none |
| N2 | 0 | high item variance | interior | none |
| N3 | 0 | high rater and rater×domain variance | interior | none |
| N4 | 0 | mixed positive/negative item effects that cancel | interior | none |
| N5 | 0 | low variance | floor | none |
| N6 | 0 | low variance | ceiling | none |
| N7 | 0 | moderate variance | interior | random dropout |
| N8 | 0 | moderate variance | interior | severity-dependent dropout |
| N9 | 0 | moderate variance | interior | disagreement-dependent dropout |
| N10 | 0 | domain-specific effects that cancel globally | interior | none |

N8 and N9 do not automatically have an identified frequentist target after selection. They are sensitivity regimes. Failure there may require `indeterminate_due_to_informative_dropout`, not a different bootstrap.

## 5. Design subset for high-precision calibration

The first high-precision run should not repeat all five designs. Use three designs that span the factor-count and density tradeoff:

1. `complete_8x18_r8` — few raters, dense item coverage;
2. `incomplete_12x24_r6` — intermediate design;
3. `incomplete_16x24_r6` — more raters at the same item breadth.

This isolates whether increasing the number of rater clusters repairs calibration while holding the total budget fixed.

The 12×36 design can return after the method is computationally stable.

## 6. Bootstrap-draw convergence

For a fixed generated dataset, evaluate:

```text
B ∈ {100, 500, 2000}
```

using nested random streams so that the first 100 draws are identical across all three settings and the first 500 draws are identical between 500 and 2000.

For each dataset and method, record:

- lower and upper 95% endpoints;
- interval width;
- absolute endpoint movement from B=100 to 500;
- absolute endpoint movement from B=500 to 2000;
- whether the reject/nonreject decision changes;
- number of zero-total-weight draws;
- number of undefined component estimates.

Provisional convergence rule:

```text
max endpoint movement from B=500 to B=2000 ≤ 0.02 score units
and no decision change
```

The `0.02` rule is an engineering tolerance, not a validated scientific constant. Its purpose is to prevent bootstrap Monte Carlo noise from being mistaken for inferential instability.

## 7. Monte Carlo precision

Use at least 1,000 generated datasets per retained null cell.

For an observed false-positive rate near 0.05, 1,000 trials give a Monte Carlo standard error of approximately:

```text
sqrt(0.05 × 0.95 / 1000) ≈ 0.0069
```

A rough 95% Monte Carlo interval is therefore about ±0.014 before exact binomial calculation.

This is adequate for detecting gross miscalibration such as 0.02, 0.08, or 0.12. It is not adequate for claiming precise equivalence to 0.05.

Report exact binomial confidence intervals for every estimated Type-I error rate.

## 8. Methods to compare

The minimum comparison set is:

1. item-only cluster bootstrap;
2. rater-only cluster bootstrap;
3. multinomial product-weighted pigeonhole bootstrap;
4. product-weighted bootstrap with mean-one variance-one weights, such as independent Poisson(1) weights, if implemented and validated;
5. two-way cluster-robust analytic variance for the linear mean contrast.

Do not add a more sophisticated estimator merely to obtain favorable coverage. Every method must use the same generated datasets and target estimand.

## 9. Acceptance and rejection rules

### Provisional acceptance for continued pilot use

A method may be retained as a **pilot uncertainty method** for the mean contrast only if all are true across the prespecified interior null cells:

- Type-I error estimate lies within `[0.035, 0.065]`;
- exact-binomial 95% interval includes `0.05`;
- median B=500→2000 endpoint movement is at most `0.02`;
- 95th-percentile endpoint movement is at most `0.05`;
- undefined-draw rate is below `0.5%`;
- no design cell has Type-I error above `0.075`;
- conclusions do not reverse systematically under one-domain deletion.

These are engineering acceptance gates for the pilot, not general statistical theorems.

### Rejection

Reject a method for confirmatory use if any prespecified interior null cell has:

- Type-I error above `0.10`;
- coverage below `0.90`;
- undefined-draw rate above `2%`;
- systematic endpoint nonconvergence at B=2000;
- materially different results caused only by arbitrary row ordering or seed partitioning.

### Excessive conservatism

Flag a method as `validity_unresolved_due_to_excessive_conservatism` when:

- Type-I error is below `0.02` in most interior null cells;
- interval width is at least 1.5 times the best non-anti-conservative rival;
- power against a prespecified practically material alternative is below 50%.

High null coverage alone does not pass the method.

## 10. Power and falsification alternatives

After null calibration, test alternatives with known component effects:

- weak false reassurance: `(+0.25, -0.15, -0.25)`;
- reference false reassurance: `(+0.45, -0.30, -0.50)`;
- sparse harmful drift affecting 10% of novel items;
- domain-localized harmful drift in one domain;
- mean-zero directional cancellation.

A method is weakened if it controls Type-I error only by becoming unable to detect the reference alternative.

## 11. Implementation requirements

The focused driver must:

- import the committed simulator rather than duplicate its data-generating logic;
- support resumable cell-level output;
- write one row per completed cell immediately;
- record repository commit SHA, Python version, platform, command, seed, trial count, draw count, runtime, and interrupted cells;
- use deterministic seed derivation from design, regime, trial, and method;
- preserve all failed or undefined draws;
- never silently retry until a favorable interval appears;
- leave the private QEIB holdout untouched.

## 12. Required output schema

Each cell must report at minimum:

```json
{
  "design_id": "complete_8x18_r8",
  "null_regime": "N3",
  "method": "pigeonhole_multinomial",
  "trials_planned": 1000,
  "trials_completed": 1000,
  "bootstrap_draws": 2000,
  "false_positive_count": 0,
  "false_positive_rate": 0.0,
  "false_positive_binomial_ci95": [0.0, 0.0],
  "coverage": 0.0,
  "mean_interval_width": 0.0,
  "median_endpoint_movement_500_to_2000": 0.0,
  "p95_endpoint_movement_500_to_2000": 0.0,
  "undefined_draw_rate": 0.0,
  "decision_change_rate_500_to_2000": 0.0,
  "status": "completed"
}
```

Zeros above are placeholders describing the schema, not results.

## 13. Permitted conclusions

After a passing calibration, the strongest permitted statement is:

> Under the prespecified synthetic crossed item-rater regimes and tested EGC candidate designs, this uncertainty method approximately controlled the mean-contrast Type-I error at the selected engineering tolerance.

## 14. Prohibited conclusions

The calibration cannot establish:

- validity for every rater population or prompt domain;
- robustness to missingness not at random;
- validity of the semantic-fidelity construct;
- adequacy of the false-reassurance conjunction without separate joint calibration;
- consciousness, subjectivity, intent, deception, or awareness;
- that conservative intervals prove scientific rigor.

## 15. Prior-art sources

1. Owen, A. B. (2007). *The pigeonhole bootstrap*. Annals of Applied Statistics, 1(2). DOI: `10.1214/07-AOAS122`. Preprint: `arXiv:0712.1111`.
2. Owen, A. B., & Eckles, D. (2012). *Bootstrapping data arrays of arbitrary order*. Annals of Applied Statistics, 6(3), 895–927. Preprint: `arXiv:1106.2125`.
3. Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2011). *Robust inference with multiway clustering*. Journal of Business & Economic Statistics, 29(2), 238–249. DOI: `10.1198/jbes.2010.07136`.
4. Bakshy, E., & Eckles, D. (2013/2014). *Uncertainty in online experiments with dependent data: An evaluation of bootstrap methods*. `arXiv:1304.7406`.
5. Davezies, L., D'Haultfoeuille, X., & Guyonvarch, Y. (2021; preprint 2018). *Asymptotic results under multiway clustering*. `arXiv:1807.07925`.

## 16. Single highest-leverage next action

Implement the resumable focused calibration driver for designs `complete_8x18_r8`, `incomplete_12x24_r6`, and `incomplete_16x24_r6`, starting with null regimes N1–N3 and nested bootstrap draws `{100, 500, 2000}`. Do not run the full grid until deterministic resume behavior and one-cell convergence tests pass.
