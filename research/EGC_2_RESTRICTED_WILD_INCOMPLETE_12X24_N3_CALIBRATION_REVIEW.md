# EGC 2.0 Restricted Wild-Cluster Calibration: Incomplete 12×24, N3

## Status

This document reports a high-precision synthetic calibration of the exact restricted wild-cluster bootstrap-t candidate for the `incomplete_12x24_r6` monitoring design under the N3 high-rater-heterogeneity regime.

The result is evidence about one simulated design-regime cell. It is not validation for confirmatory EGC inference, human raters, other assignment structures, informative dropout, or scale-boundary regimes.

## Frozen design and method

- 12 raters
- 24 items per monitoring class
- 6 ratings per item
- 576 planned ratings
- N3 parameters:
  - item SD: 0.60
  - ambiguity SD: 0.35
  - rater SD: 1.00
  - rater-by-domain SD: 0.75
  - no dropout
- exact enumeration of all 4,096 rater-level Rademacher sign patterns
- minimum-norm scalar-null projection
- two-way CGM item + rater − item-by-rater studentization
- fixed base seed: `20260726`

The fail-closed rule was unchanged:

1. nonpositive observed two-way variance → `indeterminate`;
2. undefined bootstrap-variance fraction greater than 10% → `indeterminate`;
3. indeterminate datasets remain in the all-trial denominator.

The 10% threshold remains provisional and is not empirically validated.

## Calibration results

### Global null

- trials: 1,000
- defined: 989
- indeterminate: 11
- rejections: 44
- all-trial Type-I error: **4.4%**
- exact 95% binomial interval: **3.21%–5.86%**
- defined-only rejection: **4.45%**
- mean estimate: **0.00137**

Indeterminate reasons:

- observed two-way variance nonpositive: 2
- excessive undefined-pattern fraction: 9

Undefined-pattern distribution among the 998 datasets where pattern evaluation occurred:

- median: 0%
- p90: 0.454%
- p95: 1.667%
- p99: 8.696%
- maximum: **34.766%**

### True contrast 0.20

- trials: 250
- defined: 247
- indeterminate: 3
- rejections: 145
- all-trial power: **58.0%**
- exact 95% binomial interval: **51.62%–64.19%**
- defined-only power: **58.70%**
- mean estimate: **0.19441**
- bias: **−0.00559**

All three indeterminate datasets exceeded the 10% undefined-pattern threshold.

Undefined-pattern distribution:

- median: 0%
- p90: 0.405%
- p95: 0.906%
- p99: 9.169%
- maximum: **17.578%**

## Comparison with the N2 cell

The prior `incomplete_12x24_r6 × N2` calibration reported:

- Type-I error: 4.2%
- power at 0.20: 61.2%
- indeterminate rate: 0.8% in both cells

N3 therefore did not produce observed Type-I inflation, but power decreased by 3.2 percentage points and the indeterminate rate rose to 1.1% under the null and 1.2% under the power condition.

This is consistent with, but does not prove, a modest cost from increasing heterogeneity in the rater dimension used by the bootstrap data-generating process.

## Findings supported within this synthetic cell

1. The favorable N2 null calibration transferred to N3: the exact 95% binomial interval for all-trial Type-I error contains 5%.
2. The method retained moderate power at a 0.20 contrast, but not high power.
3. Conditioning on defined datasets changed the headline rates only slightly.
4. Undefined two-way variance remains a genuine long-tail failure surface. The median is zero, but one null dataset had 34.8% undefined sign patterns.
5. Increased rater heterogeneity did not immediately falsify the restricted wild-cluster candidate.

## Claims not supported

This run does not establish:

- confirmatory validity;
- robustness to informative dropout;
- robustness to floor or ceiling compression;
- robustness to domain imbalance;
- correct choice of bootstrap-DGP dimension;
- validity of the provisional 10% threshold;
- applicability to real human semantic-fidelity ratings.

The simulation parameters are sensitivity settings, not empirical estimates.

## Methodological decision

The method remains the strongest tested candidate for this limited simulation program, because both N2 and N3 incomplete-design cells show approximately nominal all-trial null rejection with moderate power.

However, it cannot be frozen for confirmatory use. The next failure mode to test is informative dropout because the method resamples the rater dimension while dropout may selectively alter which raters and item-rater intersections remain observed.

Current status:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

## Validation boundary

The run used an isolated vectorized harness algebraically equivalent to the committed transfer driver. It preserved the generator, stable-seed contract, null projection, all 4,096 sign patterns, CGM studentization, and fail-closed accounting. Repository-wide CI is not claimed because direct cloning was unavailable.

## Next highest-leverage action

Add severity- and disagreement-dependent dropout to the same `incomplete_12x24_r6 × N3` calibration and run a concentrated null/power falsification while reporting positivity loss, rater coverage, item coverage, undefined-pattern tails, and all-trial error.
