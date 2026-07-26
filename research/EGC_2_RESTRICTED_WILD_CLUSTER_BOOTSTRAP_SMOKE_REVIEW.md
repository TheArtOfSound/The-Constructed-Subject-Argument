# EGC 2.0 Restricted Wild-Cluster Bootstrap-t Calibration Review

## Scope

This run completed the frozen `complete_8x18_r8 × N1` calibration for the exact restricted rater wild-cluster bootstrap-t candidate.

The bootstrap data-generating process clusters on the eight-rater dimension. Every bootstrap draw is studentized using the existing two-way CGM item + rater - item-by-rater variance estimator. All `2^8 = 256` rater-level Rademacher sign patterns are enumerated exactly, eliminating bootstrap Monte Carlo error within each generated dataset.

The procedure remains narrowly scoped. It is not asserted to be a universally valid multiway bootstrap for arbitrary crossed designs.

## Algebraic optimization

The prior implementation rebuilt 576 row dictionaries and recomputed three cluster-score maps for every one of 256 sign patterns. That implementation was correct but too slow for the planned calibration.

The optimized implementation uses the fact that, conditional on one generated dataset:

1. every null-restricted bootstrap class mean is linear in the rater-sign vector;
2. every item, rater, and item-by-rater cluster influence score is linear in that vector;
3. every CGM variance component is therefore a quadratic form in the same vector.

The code now precomputes one point coefficient vector and three `8 × 8` score-product matrices. Each exact sign-pattern statistic is then evaluated from those sufficient statistics.

The optimization does not change the scalar null projection, residuals, sign patterns, data seeds, studentization, undefined-draw rule, or p-value definition.

## Validation

Eight focused tests passed in the execution harness, including comparisons of the optimized calculation against explicit row reconstruction across multiple frozen datasets.

Across seven checked seeds:

- exact p-values matched;
- defined and undefined pattern counts matched;
- negative-variance pattern counts matched;
- maximum bootstrap-t difference was below `1e-11`, attributable to floating-point summation order.

A representative dataset improved from approximately `0.257` seconds to `0.0084` seconds per exact test in the execution environment, about a 30-fold speedup. Runtime is an engineering observation, not a scientific result.

## High-precision calibration

Frozen contract:

- design: `complete_8x18_r8`;
- regime: N1 low heterogeneity;
- seed: `20260726`;
- null datasets: `1,000`;
- matched power datasets at true contrast `0.20`: `250`;
- exact 256-pattern enumeration per defined dataset.

### Null

- rejections: `54 / 1,000`;
- Type-I error among all generated datasets: **5.4%**;
- exact binomial 95% interval: **4.08%–6.99%**;
- observed-test undefined datasets: `14 / 1,000 = 1.4%`;
- rejection among defined datasets: `54 / 986 = 5.48%`;
- mean undefined bootstrap-pattern rate among defined datasets: `1.61%`;
- worst observed undefined-pattern rate: `36.72%`;
- minimum defined patterns in a defined trial: `162 / 256`.

The point estimate is near nominal and its exact binomial interval includes 5%. This is materially better calibrated in N1 than the previously tested item-only bootstrap, analytic CGM/t, CV3J-plus-max, and pigeonhole percentile procedures.

It is not sufficient to call the method validated because 1.4% of observed datasets were undefined and some otherwise defined datasets lost a large fraction of sign patterns to nonpositive CGM variance.

### Power at true contrast 0.20

- rejections: `121 / 250`;
- power among all generated datasets: **48.4%**;
- exact binomial 95% interval: **42.06%–54.78%**;
- observed-test undefined datasets: `2 / 250 = 0.8%`;
- power among defined datasets: `121 / 248 = 48.79%`;
- mean undefined bootstrap-pattern rate among defined datasets: `1.89%`.

The method's power is higher than the pigeonhole percentile interval's 25.2% and the CV3J-plus-max procedure's 42.4%, but lower than analytic CGM/t at 58.8% and item-only bootstrap at 69.6%. The latter two methods were anti-conservative in the same frozen null cell.

## Comparative decision

| Method | Null rejection | Power at 0.20 | Main failure |
|---|---:|---:|---|
| Item-only percentile | 7.0% | 69.6% | anti-conservative |
| Analytic CGM/t | 9.0% | 58.8% | anti-conservative; negative variances |
| Exact restricted rater wild bootstrap-t | **5.4%** | **48.4%** | undefined observed tests and sign patterns |
| CV3J + max repair | 1.6% | 42.4% | conservative; repair active about 78% |
| Pigeonhole percentile | 0.4% | 25.2% | severely conservative and low power |

Within the single N1 complete-design cell, the exact restricted wild bootstrap-t currently has the best observed calibration-power compromise of the tested candidates.

That is a provisional engineering finding, not a confirmatory-method validation.

## Claims supported

- The quadratic-form implementation is algebraically equivalent to explicit row reconstruction within numerical tolerance.
- Exact enumeration is computationally practical after optimization.
- In the frozen N1 complete-design cell, observed null rejection was close to 5% and materially better than prior candidates.
- At a true contrast of 0.20, the method retained moderate but not high power.
- Nonpositive two-way variance remains a real failure mode in both observed datasets and bootstrap sign patterns.

## Claims not supported

This run does not establish:

- validity under N2/N3 heterogeneity;
- validity for incomplete-block designs;
- validity under informative dropout, floor/ceiling compression, or real human-rating data;
- that rater clustering is the optimal bootstrap-DGP dimension;
- a valid confidence interval inversion procedure;
- that undefined sign patterns may be ignored without bias;
- confirmatory readiness.

The overall status remains:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

## Next decision rule

The highest-leverage next step is to run the same exact method on N2 and N3 and on the `incomplete_12x24_r6` design, while preregistering how observed-test undefined cases and high undefined-pattern fractions force an `indeterminate` result. A method that calibrates only in the easiest complete low-heterogeneity cell is not adequate for the planned EGC study.
