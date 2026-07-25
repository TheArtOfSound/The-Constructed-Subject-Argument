# EGC 2.0 Compact Rater-Bias and Informative-Dropout Calibration Review

**Status:** Engineering sensitivity analysis  
**Date:** 2026-07-25  
**Scope:** Synthetic true-zero condition-effect scenarios only  
**Non-claim:** These simulations do not estimate real rater behavior, validate semantic fidelity, or establish that the pilot design controls bias in deployment.

## Run configuration

- 30 participants / 60 paired responses
- 8 raters
- 4 ratings per response before dropout
- complementary condition assignment preventing a rater from seeing both responses from one participant
- 60 Monte Carlo trials per scenario
- 200 participant-cluster bootstrap samples per trial
- true latent condition effect: `0.0`
- ordinal 1–7 observed ratings
- naive and equal-weight within-rater centered estimators
- deterministic seed: `20260725`
- Python: `3.13.5`
- runtime: `20.231` seconds
- full JSON digest: `9c0cbc014acafa5d41f7eb8b9c625e306c82f4adfddff9a939a39fbdec8bd263`

This is a compact engineering run. With 60 trials, one false-positive event changes the estimated rate by approximately `0.0167`; tail-rate estimates remain noisy.

## Observed results

| Scenario | Naive false-positive rate | Rater-centered false-positive rate | Naive mean bias | Centered mean bias |
|---|---:|---:|---:|---:|
| clean | 0.050 | 0.100 | -0.021 | -0.021 |
| most severe rater removed | 0.017 | 0.033 | -0.012 | -0.012 |
| most lenient rater removed | 0.050 | 0.033 | 0.005 | 0.005 |
| two extreme raters removed | 0.067 | 0.050 | 0.018 | 0.018 |
| disagreement-dependent removal | 0.033 | 0.050 | 0.010 | 0.010 |
| late severity-dependent dropout | 0.117 | 0.067 | 0.020 | 0.008 |
| high-severity disagreement dropout | 0.100 | 0.167 | 0.034 | 0.034 |

The machine-readable CSV is at `research/egc2/results/rater_bias_dropout_compact.csv`.

## Findings supported within this synthetic scope

1. **Balanced assignment and graph connectedness do not guarantee nominal false-positive behavior.** The design can remain structurally estimable while the decision procedure becomes anti-conservative.

2. **Late severity-dependent dropout was the clearest tested failure for naive analysis.** Its false-positive rate reached `0.117`. Rater centering reduced it to `0.067`, suggesting that rater identity matters, but not proving that centering is sufficient.

3. **Rater centering is not uniformly protective.** Under high severity variance and disagreement-dependent dropout, its false-positive rate reached `0.167`, worse than the naive estimator's `0.100`. Removing constant severity does not repair selection related to disagreement, fatigue, or unmodeled rater-by-condition structure.

4. **Small average bias can coexist with bad interval decisions.** Mean signed bias stayed modest while false-positive rates exceeded `0.05` in several regimes. Near-zero mean bias is therefore not a validity certificate.

## Unresolved uncertainty

- Sixty trials are too few for stable operating-characteristic estimates.
- The bootstrap preserves participant-level paired responses but does not fit a crossed ordinal mixed model.
- The rater-centered estimator removes constant severity only.
- Explicit anchor learning, anchor memorization, and novel-item drift are not yet implemented.
- Parameter values are synthetic sensitivity regimes, not empirical priors.
- A startup warning from an unrelated spreadsheet-runtime patch appeared in the execution environment; the simulator and all seven tests nevertheless completed successfully.

## Claims weakened or rejected

- **Weakened:** a connected co-rating graph plus balanced assignment is sufficient for unbiased condition-effect inference.
- **Rejected:** rater centering automatically neutralizes informative dropout.
- **Not tested:** whether a crossed mixed-effects, ordinal, or inverse-probability procedure provides adequate protection.
- **Prohibited:** treating this compact simulation as evidence that real rater missingness is ignorable.

## Provisional design consequence

Future confirmatory analysis should fail closed when dropout is associated with severity, disagreement, condition exposure, or session position, or when naive and rater-adjusted estimates disagree materially. Thresholds must be calibrated with larger simulations before preregistration.

## Highest-leverage next action

Extend the simulator with explicit anchor memorization versus novel-item drift and compare complete-case, rater-fixed-effect, and inverse-probability analyses under known dropout probabilities using at least 1,000 trials per high-risk scenario.
