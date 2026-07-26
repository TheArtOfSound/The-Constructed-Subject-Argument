# EGC 2.0 Crossed Bootstrap and Domain-Sensitivity Review

## Scope

This review evaluates a narrow engineering question: whether whole-item and whole-rater bootstrap intervals, together with leave-one-domain-out diagnostics, materially change the interpretation of the current fixed-budget crossed item–rater simulations.

The run used the deliberately difficult regime with item standard deviation `1.0`, severity-dependent dropout, 100 Monte Carlo trials per cell, and 100 bootstrap draws per trial. It covered all five 576-rating candidate designs under both global stability and false-reassurance truths.

These are synthetic sensitivity results. They are not empirical estimates of EGC raters or items.

## Implementation

`simulate_crossed_item_rater.py` now provides:

- whole-item cluster bootstrap intervals for the false-reassurance contrast;
- whole-rater cluster bootstrap intervals for the same contrast;
- leave-one-domain-out contrast estimates for all four domains;
- domain-omission range and sign-change diagnostics;
- a focused `--diagnostic` run mode preserving coverage, interval width, false-reassurance support, and domain sensitivity.

The item and rater bootstraps answer different generalization questions. Neither is a substitute for a crossed random-effects model. Agreement between them is reassuring only within the simulated data-generating process.

## Main results

### Coverage is not uniformly nominal

Observed item-bootstrap coverage across the ten cells ranged from `0.88` to `0.97`. Rater-bootstrap coverage ranged from `0.86` to `0.94`.

The rater bootstrap was notably anti-conservative in several cells:

- complete 8×18, global stability: `0.87`;
- complete 8×18, false reassurance: `0.86`;
- incomplete 12×36, false reassurance: `0.87`.

The item bootstrap also undercovered in some designs, including complete 12×12 under global stability (`0.88`). Therefore neither bootstrap can yet be treated as a validated primary inferential procedure.

### Interval width was similar across designs

Mean 95% interval widths were approximately `0.289–0.307` for the item bootstrap and `0.264–0.288` for the rater bootstrap. The narrower rater intervals did not reliably produce better coverage; in several cells they coincided with worse undercoverage.

A narrower interval is not evidence of a better estimator.

### Strong false reassurance remained detectable

Under the deliberately strong false-reassurance truth, descriptive support ranged from `0.90` to `0.95` across designs. Under global stability it remained `0.00` in all cells.

This supports only the engineering claim that the strong synthetic signal is detectable. One hundred trials per cell do not establish a precise false-positive bound.

### Leave-one-domain-out instability is expected near a true zero

Under global stability, leave-one-domain-out sign-change rates ranged from `0.43` to `0.55`. This initially looks alarming, but the full contrast is centered near zero, so tiny domain omissions can mechanically flip its sign without producing a material effect.

Therefore sign change alone is a poor instability metric near the null. It must be paired with a magnitude threshold.

The mean leave-one-domain-out contrast range was much more stable, approximately `0.102–0.112` under global stability and `0.105–0.115` under false reassurance. No domain omission reversed the strong false-reassurance contrast in the tested cells.

## Claims discipline

### Supported within this simulation

- Item-level and rater-level resampling produce meaningfully different coverage behavior.
- Neither bootstrap procedure achieved uniformly adequate 95% coverage in the compact diagnostic.
- Rater-level intervals were often narrower but sometimes more anti-conservative.
- A raw sign-change diagnostic is misleading when the full estimate is near zero.
- The deliberately strong false-reassurance truth remained detectable across all five designs.

### Weakened

- Any claim that a single cluster axis is sufficient for uncertainty quantification.
- Any preference for rater bootstrap solely because its intervals are narrower.
- Any use of leave-one-domain-out sign flips without a materiality threshold.

### Unresolved

- Whether a multiway bootstrap, crossed mixed model, Bayesian hierarchical model, or generalizability-theory estimator provides better calibrated inference.
- Whether coverage behavior persists at 1,000 or more Monte Carlo trials.
- Whether domain omission should be evaluated against an absolute margin, a standardized effect, or a decision threshold.
- Whether informative dropout should be modeled rather than handled through complete-case resampling.

## Required next methodological change

Before comparing crossed random-effects estimators, add a magnitude-aware domain influence rule and a two-way item-by-rater bootstrap or pigeonhole bootstrap. Then calibrate coverage and type-I error at substantially higher trial counts.

Until then, the correct interpretation is `design_decision_indeterminate`.
