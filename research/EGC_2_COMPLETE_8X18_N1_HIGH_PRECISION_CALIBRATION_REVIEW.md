# EGC 2.0 Complete 8×18 N1 High-Precision Bootstrap Calibration

**Date:** 2026-07-26  
**Scope:** `complete_8x18_r8 × N1`, 1,000 generated null datasets per method, nested bootstrap prefixes at 100, 500, and 2,000 draws.

## Question

Do the current item-only, rater-only, or multinomial pigeonhole percentile intervals control false-positive error near the nominal 5% level under the low-heterogeneity interior null regime N1?

This is a calibration result for one synthetic regime and one design. It is not evidence about actual EGC raters, semantic-fidelity validity, or any participant-level condition effect.

## Execution and preservation

The original row-reconstruction driver exceeded the execution environment's hard per-call window. The run was therefore executed through an algebraically equivalent sufficient-statistic implementation:

- item bootstrap: resampled item-cluster sums and counts;
- rater bootstrap: resampled rater-cluster sums and counts;
- pigeonhole bootstrap: independently sampled item and rater multiplicities and applied their products to item×rater cell sums and counts.

Draw-level comparison against the committed row-reconstruction implementation produced a maximum absolute discrepancy of `8.4e-17`, attributable only to floating-point summation order. Seeds, cluster draws, weights, estimand, and nested prefixes were preserved.

The complete trial-record JSONL was generated in the execution runtime:

- size: `874,023` bytes;
- SHA-256: `65bf438e5b819bb90808b77ae73db413b31c34adef43332ab649fb10a506dda1`;
- repository status: not committed because the GitHub connector could not accept the large payload directly.

A compact, auditable summary is committed at:

`research/egc2/results/multiway_bootstrap_complete_8x18_N1_1000x2000_summary.json`

The missing raw upload is a preservation blocker and must not be concealed.

## Results at 2,000 bootstrap draws

| Method | False positives | Type-I error | Exact binomial 95% CI | Coverage | Mean width |
|---|---:|---:|---:|---:|---:|
| Item-only | 70 / 1,000 | 0.070 | [0.0550, 0.0876] | 0.930 | 0.3058 |
| Rater-only | 110 / 1,000 | 0.110 | [0.0913, 0.1311] | 0.890 | 0.2794 |
| Pigeonhole multinomial | 4 / 1,000 | 0.004 | [0.0011, 0.0102] | 0.996 | 0.5141 |

## Decision against the preregistered engineering criteria

The prior calibration decision required, for retained interior-null methods:

- Type-I error between `0.035` and `0.065`;
- an exact-binomial interval containing `0.05`;
- no cell above `0.075`;
- coverage at least `0.90`;
- endpoint stabilization from 500 to 2,000 draws.

### Item-only bootstrap

**Status: fails the retention criterion in N1.**

The observed Type-I error was `0.070`, above the `0.065` retention ceiling. Its exact-binomial interval `[0.0550, 0.0876]` excludes `0.05`. Coverage was `0.930`, but coverage alone does not rescue anti-conservative rejection behavior.

The result is close to, but still outside, the chosen engineering window. It should not be rounded into nominal validity.

### Rater-only bootstrap

**Status: rejected for confirmatory use in N1.**

The observed Type-I error was `0.110`, with exact-binomial interval `[0.0913, 0.1311]`, and coverage was `0.890`. This exceeds the prior `0.10` rejection boundary and falls below the `0.90` coverage floor.

The narrower interval was not a better interval. It materially understated crossed item uncertainty.

### Multinomial pigeonhole bootstrap

**Status: excessively conservative in N1; not retained as calibrated.**

The observed Type-I error was `0.004`, with exact-binomial interval `[0.0011, 0.0102]`. Coverage was `0.996`, but the mean interval width was `0.5141`, approximately 68% wider than the item-only interval and 84% wider than the rater-only interval.

This does not demonstrate rigorous calibration. It shows that the procedure controls false positives in this cell largely by producing very wide intervals. Power against prespecified material effects must be measured before the method can be accepted.

## Bootstrap-draw convergence

| Method | Median endpoint movement, 500→2,000 | 95th percentile | Decision-change rate |
|---|---:|---:|---:|
| Item-only | 0.0087 | 0.0194 | 0.014 |
| Rater-only | 0.0068 | 0.0190 | 0.010 |
| Pigeonhole | 0.0152 | 0.0347 | 0.001 |

The item and rater methods approximately meet the provisional `0.02` endpoint tolerance at the 95th percentile. The pigeonhole method does not: its 95th-percentile endpoint movement remained `0.0347` between 500 and 2,000 draws.

Thus, 2,000 draws appear adequate for most item/rater endpoint estimates in this cell, but not demonstrably adequate for the wider pigeonhole interval tails.

## Findings supported by this run

1. Rater-only resampling is materially anti-conservative for `complete_8x18_r8 × N1` under the tested simulator.
2. Item-only resampling remains mildly anti-conservative under the preregistered retention rule.
3. Multinomial pigeonhole intervals are extremely conservative in this cell and materially wider than the one-axis alternatives.
4. Increasing bootstrap draws from 500 to 2,000 does not repair structural miscalibration; the Type-I ordering is stable across draw levels.
5. The previous status `uncertainty_method_not_validated_for_confirmatory_EGC_inference` remains correct.

## Findings not supported

This run does not establish:

- calibration under N2, N3, informative dropout, floor, or ceiling regimes;
- calibration for incomplete-block designs;
- power or useful sensitivity of the pigeonhole procedure;
- validity for the nonlinear false-reassurance conjunction;
- validity of percentile intervals relative to studentized, analytic multiway-cluster, or model-based alternatives;
- any empirical fact about real human raters or EGC condition effects.

## Claim status

- **Rejected:** rater-only percentile bootstrap as a confirmatory uncertainty method for this design/regime.
- **Weakened:** item-only percentile bootstrap as a plausible near-nominal method; the high-precision cell is outside the retained range.
- **Unresolved:** whether item-only performance becomes acceptable with other designs or whether the deviation reflects a persistent structural defect.
- **Unresolved:** whether pigeonhole conservatism is tolerable once power is quantified.
- **Preserved null/failure:** no method met the preregistered retention rule in this first high-precision cell.

## Highest-leverage next action

Run a matched power calibration in the same `complete_8x18_r8 × N1` cell at prespecified true contrasts, comparing item-only and pigeonhole intervals. The immediate decision is whether pigeonhole's false-positive control is purchased at an unusable loss of power, or whether it remains a defensible conservative pilot method while a better two-way procedure is developed.
