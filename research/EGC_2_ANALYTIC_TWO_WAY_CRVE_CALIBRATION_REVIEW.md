# EGC 2.0 Analytic Two-Way CRVE Calibration Review

## Scope

This run implemented and calibrated an analytic two-way cluster-robust variance estimator for the existing EGC crossed item-by-rater mean contrast. The estimator follows the Cameron–Gelbach–Miller inclusion–exclusion form:

```text
V_two_way = V_item + V_rater - V_item×rater
```

The point estimand remains:

```text
mean(exact-anchor shift)
- 0.5 × mean(structural-transfer shift)
- 0.5 × mean(novel-response shift)
```

The interval uses a two-sided Student-t reference with:

```text
df = min(number of item clusters, number of rater clusters) - 1
```

For `complete_8x18_r8`, this gives `df = 7`.

This is an engineering calibration of one estimator in one synthetic regime. It is not a validation of confirmatory EGC inference.

## Why this task mattered

The existing candidates had an unacceptable calibration-power frontier:

- item-only percentile intervals retained useful power but were anti-conservative;
- multinomial pigeonhole intervals controlled false positives by becoming excessively wide and insensitive;
- rater-only intervals were already rejected.

An analytic multiway cluster estimator was therefore the highest-leverage untested rival.

## Implementation

`research/egc2/calibrate_two_way_crve.py`:

- derives row-level influence contributions for the class-mean contrast;
- aggregates those contributions by item, by rater, and by item×rater cell;
- applies finite-cluster corrections separately to the three components;
- records raw negative variance estimates before truncating them to zero for interval construction;
- reports positive-direction rejection, negative-direction rejection, two-sided rejection, coverage, width, bias, and negative-variance frequency;
- uses the same deterministic N1 data seeds as the existing null and matched-power calibrations.

The intersection subtraction is essential. Item-only plus rater-only variance without subtracting the shared item×rater component would double-count observation-level variation.

## Validation

Seven focused tests were added:

1. the temporary power truth has the requested estimand;
2. null and power runs preserve the common-random-number data-seed contract;
3. the CRVE calculation is deterministic;
4. the design produces 72 item clusters, 8 rater clusters, and `df = 7`;
5. intervals contain their point estimate and all variance components are finite;
6. empty input fails clearly;
7. invalid effects and trial counts fail clearly.

Direct repository cloning failed because the execution environment could not resolve `github.com`. Numerical execution therefore used an isolated harness implementing the exact committed simulator and estimator equations. Repository-wide CI success is not claimed.

## Numerical result

### Null calibration

The null cell used 1,000 generated datasets.

| Metric | Result |
|---|---:|
| Positive-direction rejection | 4.1% |
| Negative-direction rejection | 4.9% |
| Two-sided rejection | 9.0% |
| 95% interval coverage | 91.0% |
| Mean interval width | 0.3506 |
| Negative variance estimates | 1.4% |

The directional positive false-positive rate appears close to 5%, but the nominal claim is two-sided 95% coverage. On that criterion the method fails: 9.0% of null intervals excluded zero and coverage was only 91.0%.

The occasional negative variance estimate is also substantive. Inclusion–exclusion multiway estimates are not guaranteed to remain positive in finite samples. Truncation makes an interval computable but does not repair the inferential defect.

### Matched power

The power cells used 250 generated datasets per effect.

| True contrast | Positive-direction power | Coverage | Mean width |
|---:|---:|---:|---:|
| 0.10 | 19.6% | 90.8% | 0.3512 |
| 0.20 | 58.8% | 90.8% | 0.3512 |
| 0.30 | 90.8% | 90.8% | 0.3512 |

The analytic method occupies a middle position:

- materially more power than the pigeonhole percentile interval;
- less power than the item-only percentile interval;
- interval width between the two bootstrap candidates;
- still materially subnominal coverage.

At the practically important `0.20` effect, power was 58.8%. That is better than pigeonhole's 25.2% but below item-only's 69.6%. The coverage deficit means this gain is not a valid calibration-power solution.

## Claims supported

Within the exact synthetic N1 design:

1. analytic two-way CRVE improves the calibration-power tradeoff relative to multinomial pigeonhole percentile intervals;
2. it does not achieve nominal two-sided coverage;
3. it occasionally produces negative finite-sample variance estimates;
4. using only positive-direction rejection would conceal the two-sided coverage failure;
5. no tested uncertainty method currently satisfies both calibration and useful power.

## Claims rejected or weakened

### Rejected

```text
analytic_two_way_crve_validated_for_confirmatory_EGC_inference
```

### Still rejected

```text
item_only_percentile_interval_validated
multinomial_pigeonhole_percentile_interval_acceptable_default
rater_only_percentile_interval_acceptable
```

### Current program status

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

## Unresolved uncertainty

This run does not establish performance under:

- high item or rater heterogeneity;
- incomplete-block designs;
- informative dropout;
- floor or ceiling compression;
- nonzero item×rater interaction beyond the current generator;
- real rater data;
- alternative small-sample corrections;
- wild multiway bootstrap, CR2/Satterthwaite corrections, or crossed mixed models.

The `df = min(G_item, G_rater)-1` rule is conservative in intent but did not deliver nominal coverage here. A different degrees-of-freedom rule alone should not be tuned post hoc against this one cell.

## Highest-leverage next action

Implement a CR2-style bias-reduced cluster-robust estimator with Satterthwaite degrees of freedom, or a multiway wild cluster bootstrap, and evaluate it on the same frozen N1 seeds. The next method must improve two-sided coverage without collapsing power at a `0.20` material contrast.
