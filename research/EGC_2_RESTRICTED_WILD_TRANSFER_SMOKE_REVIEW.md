# EGC 2.0 Restricted Wild-Cluster Transfer Smoke Review

## Status

This is a small engineering falsification run, not confirmatory calibration.

The prior high-precision result found favorable null calibration for the exact restricted rater wild bootstrap-t only in the easiest tested cell: complete `8×18`, N1 low heterogeneity. The present run asks whether that result immediately collapses under higher heterogeneity or the fixed-budget incomplete `12×24` design.

## Method change

`research/egc2/calibrate_restricted_wild_transfer.py` generalizes the exact procedure to:

- complete `8×18` and incomplete `12×24` designs;
- N1, N2, and N3 heterogeneity regimes;
- exact enumeration of all rater-level Rademacher patterns (`256` or `4096`);
- the same scalar-null projection and two-way CGM studentization;
- an explicit fail-closed outcome.

A dataset is `indeterminate` when:

1. its observed two-way variance is nonpositive; or
2. more than 10% of the exact sign patterns have nonpositive bootstrap variance.

Indeterminate datasets remain in the all-trial denominator. They are never silently deleted and then used to report a cleaner conditional error rate.

The 10% threshold is provisional. It is a transparent engineering rule whose operating characteristics still require calibration; it is not a validated scientific constant.

## Preserved smoke run

Command represented by the committed result:

```bash
python research/egc2/calibrate_restricted_wild_transfer.py \
  --output research/egc2/results/restricted_wild_transfer_N2_N3_30null.json \
  --trials 30 \
  --effect 0.0 \
  --designs complete_8x18_r8 incomplete_12x24_r6 \
  --regimes N2 N3
```

| Design | Regime | Rejections / all | Rejections / defined | Indeterminate |
|---|---:|---:|---:|---:|
| complete `8×18` | N2 | 1/30 = 3.3% | 1/28 = 3.6% | 2/30 = 6.7% |
| complete `8×18` | N3 | 1/30 = 3.3% | 1/28 = 3.6% | 2/30 = 6.7% |
| incomplete `12×24` | N2 | 1/30 = 3.3% | 1/29 = 3.4% | 1/30 = 3.3% |
| incomplete `12×24` | N3 | 0/30 = 0.0% | 0/30 = 0.0% | 0/30 = 0.0% |

All three indeterminate cases were caused by the provisional undefined-pattern threshold rather than being silently omitted.

## Findings supported by this run

- The optimized exact procedure executes on the incomplete 12-rater design and enumerates all 4,096 rater sign patterns.
- The favorable N1 result was not immediately falsified by this very small N2/N3 null smoke run.
- Undefined bootstrap variance remains operationally important: the fail-closed rule made 0% to 6.7% of cells indeterminate.
- Reporting only conditional rejection among defined datasets would conceal part of the method's failure surface.

## Findings not supported

This run does not establish:

- nominal Type-I error in N2 or N3;
- valid transfer to incomplete blocks;
- the correctness of the 10% undefined-pattern threshold;
- adequate power under N2, N3, or incomplete designs;
- robustness to dropout, ordinal boundaries, domain imbalance, or real human ratings.

With only 30 trials per cell, one rejection changes the reported rate by 3.3 percentage points. The observed rates are therefore descriptive engineering evidence only.

## Validation and execution limits

A focused isolated harness implementing the committed public function contract passed five deterministic and input-validation tests, and `py_compile` passed for the transfer logic. Direct repository cloning failed because the execution environment could not resolve `github.com`, so repository-wide CI and execution of the exact committed test file are not claimed.

## Claim status

The overall status remains:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

The transfer hypothesis remains alive but unconfirmed. The smoke result is too small to retain or reject the method.

## Next decision

The next calibration should concentrate compute rather than expand the grid: run at least 1,000 null datasets for the incomplete `12×24 × N2` cell and 250 matched datasets at effect `0.20`, preserving both all-trial and defined-only rates. That cell simultaneously tests incomplete assignment, 12-rater enumeration, higher item heterogeneity, fail-closed frequency, and usable power.
