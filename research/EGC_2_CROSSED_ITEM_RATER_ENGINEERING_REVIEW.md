# EGC 2.0 Crossed Item–Rater Engineering Review

## Status

Engineering smoke test only. This is not a design-selection result and does not validate any real rater architecture.

## Work completed

Implemented `research/egc2/simulate_crossed_item_rater.py` for the five fixed-budget designs defined in the crossed simulation protocol. The simulator currently covers:

- global stability and false-reassurance truths;
- low and high item variance;
- moderate rater severity and rater-by-domain heterogeneity;
- balanced four-domain allocation including a held-out diagnostic domain;
- seven-point clipping;
- no dropout and severity-dependent dropout;
- descriptive false-reassurance support, item-population error, held-out-domain gap, and observed-row count.

## Validation

Eight tests passed in Python 3.13:

1. every candidate uses exactly 576 planned ratings;
2. all 576 rows are generated without dropout;
3. fixed seeds reproduce exact scientific output;
4. truth definitions have the intended direction;
5. ordinal scores remain inside 1–7;
6. severity-dependent dropout does not increase row count;
7. item-population and held-out-domain diagnostics are emitted;
8. compact-grid cell count is correct.

The first test-loader attempt failed because the dynamically loaded module was not inserted into `sys.modules` before dataclass evaluation. The loader was corrected and the full suite then passed. This failure was implementation-related and did not change simulation results.

## Engineering smoke result

A 20-trial-per-cell run was preserved at `research/egc2/results/crossed_item_rater_engineering_20.json`.

Under global stability, no cell produced false-reassurance support in the 20-trial smoke run. Under the deliberately strong false-reassurance truth, support ranged from 0.85 to 1.00 across tested cells.

For the high-item-variance plus severity-dropout condition:

| Design | Support | Mean item-population error | Held-out-domain gap |
|---|---:|---:|---:|
| complete 8×18 | 0.90 | 0.068 | 0.072 |
| incomplete 12×36 | 0.95 | 0.082 | 0.055 |
| incomplete 12×24 | 0.85 | 0.079 | 0.060 |
| complete 12×12 | 0.95 | 0.074 | 0.059 |
| incomplete 16×24 | 0.85 | 0.091 | 0.070 |

These differences are too unstable to rank designs. Twenty trials per cell are insufficient for tail-rate estimation, and the current estimator remains descriptive rather than a crossed random-effects fit.

## Claims discipline

Supported:

- all five designs can be represented at the same 576-rating budget;
- the simulator preserves rater, item, domain, ordinal-boundary, and dropout structure;
- the strong synthetic false-reassurance truth is detectable in an engineering smoke run;
- the global-stability smoke did not generate an observed false-reassurance flag.

Not supported:

- preference for any design;
- nominal false-positive control;
- valid held-out-domain inference;
- adequacy of the descriptive estimator;
- resemblance to real EGC rater or item distributions.

## Highest-leverage next action

Add whole-item and whole-rater bootstrap intervals plus leave-one-domain-out evaluation, then run at least 100 trials per cell before implementing or comparing a crossed random-effects estimator.
