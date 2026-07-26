# EGC 2.0 Restricted-Wild Informative-Dropout Calibration Review

**Status:** concentrated synthetic falsification; not confirmatory validation  
**Design:** `incomplete_12x24_r6`  
**Regime:** N3  
**Primary uncertainty method:** exact restricted wild cluster bootstrap-t over the rater dimension

## Question

Does the favorable complete-data calibration of the restricted wild-cluster candidate survive selective missingness associated with rater severity, rater disagreement, or both?

This is a direct falsification test of the bootstrap data-generating dimension. If rater participation becomes selective, the surviving rater sample and item-rater graph can change even when the complete-data method is calibrated.

## Simulation contract

The complete data-generating process preserves the prior N3 design:

- 12 raters;
- 24 items per monitoring class;
- 6 planned ratings per item;
- 576 planned ratings;
- item SD 0.60;
- ambiguity SD 0.35;
- rater severity SD 1.00;
- rater-by-domain SD 0.75;
- seven-point score clipping;
- exact enumeration of all 4,096 rater Rademacher patterns;
- two-way CGM item + rater − item-by-rater studentization;
- observed nonpositive variance treated as indeterminate;
- undefined-pattern fraction above 10% treated as indeterminate;
- all-trial rates retained as primary.

Four missingness mechanisms were compared:

1. `none`;
2. `severity`: dropout probability increases with absolute rater severity;
3. `disagreement`: dropout probability increases with the rater's mean absolute deviation from the complete-data class mean;
4. `combined`: both standardized severity and disagreement enter the selection model.

The dropout logit intercept was −2.2, with coefficients 0.9 for standardized severity and 1.0 for standardized disagreement. These are sensitivity settings, not empirical estimates.

The disagreement mechanism is deliberately adversarial and uses complete-data disagreement as an oracle selection variable. It therefore tests vulnerability to nonignorable selection; it is not presented as an operational real-time dropout model.

## Results

The null cells used 500 datasets per mechanism. The effect-0.20 cells used 250 datasets per mechanism.

| Mechanism | Mean dropout | Null rejection | Null indeterminate | Power at 0.20 | Power indeterminate |
|---|---:|---:|---:|---:|---:|
| None | 0.0% | 3.6% | 1.8% | 53.6% | 1.6% |
| Severity | 13.0% | 3.8% | 1.4% | 50.0% | 0.8% |
| Disagreement | 13.4% | 3.4% | 1.2% | 53.6% | 1.6% |
| Combined | 14.0% | 4.2% | 1.2% | 47.6% | 1.2% |

Exact 95% binomial intervals for all-trial null rejection were:

- none: 2.15%–5.63%;
- severity: 2.30%–5.87%;
- disagreement: 1.99%–5.39%;
- combined: 2.62%–6.35%.

No tested selective-missingness mechanism produced observed Type-I inflation in this concentrated run. The combined mechanism produced the largest observed loss of power: 47.6% versus 53.6% without dropout, a descriptive decline of 6.0 percentage points.

## Coverage degradation in the assignment

The inferential headline is not the only relevant result. Selective dropout materially weakened the planned rating structure:

- severity dropout left a mean minimum of 2.85 ratings per item and 2.59 items per dataset with fewer than four ratings;
- disagreement dropout left a mean minimum of 2.83 ratings per item and 3.01 items with fewer than four ratings;
- combined dropout left a mean minimum of 2.76 ratings per item and 3.42 items with fewer than four ratings.

Thus, nominal null calibration in this simulation does not imply that the resulting dataset still satisfies the intended measurement design. The method can remain numerically calibrated while the item-level replication target is violated.

## Findings supported by this run

Within the tested synthetic N3 setting:

- approximately 13%–14% selective dropout did not create observed Type-I inflation for the restricted wild-cluster test;
- severity-dependent dropout reduced power modestly;
- the combined severity-plus-disagreement mechanism produced the lowest observed power;
- all-trial and defined-only rates remained close because indeterminate rates stayed near 1%–2%;
- selective dropout routinely pushed some items below four retained ratings.

## Findings not supported

This run does not establish that:

- informative dropout is harmless;
- the method is valid under missing-not-at-random selection;
- the dropout coefficients resemble real EGC raters;
- the 10% undefined-pattern threshold is validated;
- retained item-level replication is scientifically sufficient;
- graph connectivity or rater coverage remained adequate in every dataset;
- calibration transfers to stronger dropout, complete rater loss, domain-selective dropout, score-boundary compression, or real human ratings.

The disagreement selection mechanism also conditions on a complete-data quantity unavailable after real dropout. It is useful as an adversarial sensitivity analysis, not a deployable correction model.

## Methodological decision

The complete-data candidate was not falsified by these moderate selective-dropout mechanisms, but the measurement design was weakened before the inferential method visibly failed.

The current status remains:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

A confirmatory protocol should fail closed when retained ratings per item, rater coverage, or domain balance fall below preregistered thresholds even if the wild-bootstrap p-value itself is defined.

## Highest-leverage next action

Add explicit whole-rater loss and domain-selective dropout, then preregister structural validity gates for minimum ratings per item, minimum active raters, class/domain balance, and graph connectivity before further calibration. The next test should determine whether structural failure is detected before a seemingly well-calibrated p-value is reported.
