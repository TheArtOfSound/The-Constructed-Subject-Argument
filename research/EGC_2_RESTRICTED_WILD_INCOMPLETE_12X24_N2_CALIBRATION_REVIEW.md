# EGC 2.0 Restricted Wild-Cluster Calibration: Incomplete 12×24, N2

## Scope

This review evaluates the exact restricted wild-cluster bootstrap-t candidate on the first materially harder incomplete-design cell selected in the prior GPT handoff:

- design: `incomplete_12x24_r6`;
- 12 raters;
- 24 items per monitoring class;
- 6 ratings per item;
- 576 planned ratings;
- N2 heterogeneity: item SD 1.00, ambiguity SD 0.35, rater SD 0.50, rater-by-domain SD 0.25;
- no dropout;
- 1,000 global-null datasets;
- 250 matched datasets at true contrast 0.20;
- exact enumeration of all `2^12 = 4,096` rater-level Rademacher patterns.

The inferential target remains the repository contrast:

```text
mean(exact-anchor shift)
- 0.5 × mean(structural-transfer shift)
- 0.5 × mean(novel-response shift)
```

This calibration does not test consciousness, awareness, deception, intent, or any latent psychological type.

## Frozen method contract

The run preserved the existing restricted-wild procedure:

1. impose the scalar null through the existing minimum-norm projection of monitoring-class means;
2. retain the observed item/rater assignment structure;
3. enumerate all rater-level Rademacher patterns;
4. studentize each pattern with the existing two-way CGM item + rater − item-by-rater variance;
5. declare an observed dataset indeterminate when its two-way variance is nonpositive;
6. declare it indeterminate when more than 10% of sign patterns have nonpositive variance;
7. retain indeterminate datasets in the all-trial denominator.

The 10% undefined-pattern threshold remains provisional. This run evaluates its operational consequences; it does not validate the threshold.

## Validation and execution

The scientific calculation was executed in an isolated algebraically equivalent quadratic-form harness because a direct repository clone was unavailable in the execution environment.

Checks completed before the calibration:

- the design generated exactly 576 rows;
- fixed seeds reproduced identical datasets and exact-test outputs;
- vectorized quadratic forms matched direct sign-by-sign summation within `1e-12` on selected patterns;
- all 4,096 sign patterns were represented;
- the simulator, truth profile, stable seed contract, null projection, studentization, p-value rule, and fail-closed conditions were preserved.

Repository-wide CI is not claimed.

Raw compact result:

`research/egc2/results/restricted_wild_incomplete_12x24_N2_1000null_250power.json`

## Results

### Global null

| Quantity | Result |
|---|---:|
| Trials | 1,000 |
| Defined trials | 992 |
| Indeterminate trials | 8 (0.8%) |
| Rejections | 42 |
| Rejection rate, all trials | **4.2%** |
| Exact 95% binomial CI | **3.04%–5.64%** |
| Rejection rate, defined trials | 4.23% |
| Mean point estimate | 0.00001 |

Indeterminate reasons:

- excessive undefined-pattern fraction: 5;
- observed nonpositive two-way variance: 3.

Undefined-pattern distribution across recorded trials:

- median: 0%;
- mean: 0.316%;
- 95th percentile: 1.514%;
- maximum: 31.445%.

### Material effect 0.20

| Quantity | Result |
|---|---:|
| Trials | 250 |
| Defined trials | 248 |
| Indeterminate trials | 2 (0.8%) |
| Rejections | 153 |
| Power, all trials | **61.2%** |
| Exact 95% binomial CI | **54.86%–67.28%** |
| Power, defined trials | 61.69% |
| Mean point estimate | 0.20236 |
| Bias | +0.00236 |

Indeterminate reasons:

- excessive undefined-pattern fraction: 1;
- observed nonpositive two-way variance: 1.

Undefined-pattern distribution across recorded trials:

- median: 0%;
- mean: 0.206%;
- 95th percentile: 0.928%;
- maximum: 10.645%.

## Interpretation

### Finding supported within this synthetic cell

The favorable low-heterogeneity N1 result transferred to the incomplete `12×24` N2 cell without obvious Type-I inflation.

The all-trial null rejection rate was 4.2%, and its exact 95% binomial interval included 5%. The method also retained materially more power than it showed in the complete `8×18` N1 cell: 61.2% here versus 48.4% previously at the same nominal effect.

That power increase should not be overinterpreted as a general superiority claim. The design, heterogeneity, item breadth, rater count, and seed-specific finite-sample structure all changed together.

### Important failure preserved

The method remained undefined or fail-closed on 0.8% of datasets in both the null and power cells. Most datasets had no undefined sign patterns, but the null maximum reached 31.4%. A mean undefined rate alone therefore conceals a long-tail failure mode.

Conditioning only on defined trials changed the headline rates little in this run, but that is an observed property of this cell, not a guarantee. The all-trial denominator remains primary.

### Claim strengthened, not validated

The evidence strengthens the hypothesis that exact rater-level restricted wild bootstrap-t may offer a workable calibration–power compromise for EGC monitoring data.

It does not yet support `validated_for_confirmatory_EGC_inference` because:

- only one incomplete design and one higher-heterogeneity regime received high-precision calibration;
- the provisional 10% threshold is not independently calibrated;
- N3, informative dropout, ordinal boundary compression, domain imbalance, and real rater data remain untested at high precision;
- studentization still relies on a two-way CGM variance that can be nonpositive;
- power at 0.20 remains only about 61%, which may be inadequate for a confirmatory stopping rule;
- the simulation parameters are sensitivity settings, not empirical estimates from EGC raters.

The claim status remains:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

## Decision

Do not freeze the method as confirmatory yet.

Retain it as the leading candidate for the next calibration stage because it currently has the strongest observed calibration–power balance among tested procedures, while preserving the explicit indeterminate state.

## Highest-leverage next action

Run the same 1,000-null and 250-power calibration for `incomplete_12x24_r6 × N3`, using the identical fail-closed rule and seed contract. N3 directly stresses the rater dimension used for the bootstrap data-generating process and is therefore the most discriminating next falsification test.
