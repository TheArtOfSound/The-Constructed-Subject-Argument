# EGC 2.0 Two-Way Cluster-Jackknife Calibration Review

**Date:** 2026-07-26  
**Status:** engineering calibration; not confirmatory validation

## Task completed

Implemented and calibrated a two-way cluster-jackknife candidate for the frozen `complete_8x18_r8 × N1` synthetic cell.

The estimator follows the two-way CV3J inclusion-exclusion structure:

```text
V_two_way_raw = V_item_CV3J + V_rater_CV3J - V_intersection_CV3J
```

Each component is computed from delete-one-cluster estimates centered on their mean. The implemented safeguard is the scalar version of the max-one-way repair discussed by MacKinnon, Nielsen, and Webb:

```text
V_repaired = max(V_two_way_raw, V_item_CV3J, V_rater_CV3J)
```

All item, rater, and item-by-rater deletion estimates are preserved. The repair does not overwrite the raw variance.

## Calibration contract

- Design: `complete_8x18_r8`
- Regime: N1 low heterogeneity
- Null: 1,000 generated datasets
- Power: 250 matched datasets each at contrasts `0.10`, `0.20`, and `0.30`
- Data seed contract: unchanged from the committed item-only, pigeonhole, and analytic CGM calibrations
- Interval reference: two-sided Student-t with `df = min(item clusters, rater clusters) - 1 = 7`

## Results

| True contrast | Two-sided rejection / power | Coverage | Mean width | Repair activation |
|---:|---:|---:|---:|---:|
| 0.00 | 1.6% | 98.4% | 0.4205 | 77.9% |
| 0.10 | 10.8% | 98.0% | 0.4208 | 78.8% |
| 0.20 | 42.4% | 98.0% | 0.4208 | 78.8% |
| 0.30 | 86.0% | 98.0% | 0.4208 | 78.8% |

No undefined interval occurred after repair.

## Interpretation

### Supported within this synthetic cell

- The jackknife-plus-max repair eliminates the negative-variance failure that affected the analytic CGM implementation.
- It also corrects the analytic CGM method's severe anti-conservatism.
- The correction overshoots: the null rejection rate is only 1.6%, far below the nominal 5% target.
- At the prespecified material contrast of `0.20`, power is only 42.4%.
- The max repair activates in roughly four out of five datasets, so the result is driven primarily by the safeguard rather than the unmodified two-way inclusion-exclusion variance.

### Comparison with previously committed N1 results

At effect `0.20`:

| Method | Null two-sided rejection | Power | Mean interval width |
|---|---:|---:|---:|
| Item-only percentile bootstrap | 7.0% | 69.6% | ~0.304 |
| Analytic CGM/t | 9.0% | 58.8% | ~0.351 |
| Two-way CV3J + max repair | 1.6% | 42.4% | ~0.421 |
| Pigeonhole percentile bootstrap | 0.4% | 25.2% | ~0.511 |

The jackknife candidate occupies the expected middle position between analytic CGM and the pigeonhole bootstrap, but it still does not meet the program's joint calibration-and-power requirement.

## Claim decision

Rejected as a default confirmatory procedure for the tested cell:

```text
two_way_cv3j_max_one_way_validated_for_confirmatory_EGC_inference
```

The broader status remains:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

## Evidence limits

This result does not establish operating characteristics under:

- N2 or N3 heterogeneity;
- incomplete-block designs;
- informative dropout;
- ordinal floor or ceiling compression;
- real human-rating data;
- alternative two-way jackknife variants;
- multiway wild cluster bootstrap-t inference.

The implementation uses the scalar contrast form of the max-one-way repair. It does not claim to reproduce a general matrix-valued estimator for arbitrary regression coefficients.

## Highest-leverage next action

Implement a restricted multiway wild cluster bootstrap-t on the same frozen N1 seeds, with exact enumeration of the eight-rater Rademacher patterns where feasible, and compare null calibration plus `0.20` power against the four existing methods.
