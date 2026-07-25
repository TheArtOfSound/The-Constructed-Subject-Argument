# EGC 2.0 Anchor-Memory Detector Calibration Review

**Date:** 2026-07-25  
**Status:** Synthetic engineering calibration; not empirical evidence about real raters

## Question

Can a preregistered detector identify the false-reassurance pattern—recurring exact anchors improve while novel-item scoring deteriorates—without forcing noisy cases into a binary conclusion?

The detector resamples whole raters, computes 95% intervals for exact-anchor and novel-item early-to-late shifts, and returns:

- `supported` when the exact-anchor lower bound is at least `+delta` and the novel-item upper bound is at most `-delta`;
- `rejected` when either interval excludes the required material shift;
- `indeterminate` otherwise.

## Calibration grid

The compact run evaluated three generating regimes, thresholds `0.20`, `0.35`, and `0.50`, and 11 stress scenarios varying item count, exact-anchor learning strength, novel drift, noise, and floor/ceiling position. It used 40 Monte Carlo trials and 80 rater-cluster bootstrap samples per cell with eight raters.

These counts are engineering-scale. They are not sufficient for precise tail-rate or interval-coverage claims.

## Main finding

The interval-gated detector was conservative but weakly sensitive.

Across the full local grid:

- mean supported rate in adversarial cells: `0.157`;
- maximum observed supported rate in either non-adversarial regime: `0.000`;
- mean indeterminate rate across all cells: `0.324`.

The observed zero false-positive rate is encouraging, but 40 trials per cell cannot establish that the true false-positive rate is zero.

## Decision-relevant cells

At `delta = 0.20`, memorization plus novel drift was supported in:

- `47.5%` of reference trials;
- `77.5%` with 36 items per class;
- `30.0%` with eight items per class;
- `77.5%` under strong exact-anchor learning;
- `5.0%` under weak exact-anchor learning;
- `72.5%` under low noise;
- `25.0%` under high noise.

At the same threshold, floor- and ceiling-limited scenarios were supported only `7.5%` of the time. Near the floor, novel deterioration is clipped; near the ceiling, exact-anchor improvement is clipped. A negative result near either boundary cannot be interpreted as stability.

Raising the threshold sharply reduced usefulness:

- reference sensitivity at `delta = 0.35`: `7.5%`;
- reference sensitivity at `delta = 0.50`: `0%`.

The `0.50` threshold is therefore not “more rigorous” under this design; it mostly produces indeterminate results.

## Supported findings

Within these synthetic regimes:

1. Rater-cluster interval gating avoided obvious point-estimate false positives in the tested non-adversarial cases.
2. Eight raters and 18 items per class do not provide high sensitivity for a two-component false-reassurance claim.
3. Increasing item-class coverage materially improved detection at `delta = 0.20`.
4. Floor and ceiling compression can hide the opposing pattern the detector is meant to identify.
5. An explicit `indeterminate` state is necessary; it must not be translated into evidence of stability.
6. Exact-anchor and surface-variant performance alone remain insufficient. Structural-transfer and novel-item evidence are required.

## Not established

This run does not validate `delta = 0.20`, establish that 36 items per class are sufficient, estimate real-rater behavior, validate the semantic-fidelity scale, or demonstrate calibrated bootstrap coverage. The simulation parameter called `learning_gain` is an engineering manipulation, not a validated measure of memory or recognition.

## Provisional rules

- Treat `delta = 0.20` only as an engineering screening threshold.
- Do not use `delta = 0.50` as the primary detector threshold with the current design.
- Require a dynamic-range gate before interpreting a negative result.
- Preserve `supported`, `rejected`, and `indeterminate` separately.
- Do not describe `indeterminate` as stable.
- Prefer more independent raters or broader item-class coverage over repeated presentation of the same anchor packets.

## Highest-leverage next action

Run a targeted high-precision calibration rather than expanding the grid indiscriminately: compare eight, 12, and 16 raters at `delta = 0.20`, with 18 versus 36 items per class, interior versus floor/ceiling baselines, and low versus high noise. Use at least 1,000 trials and 2,000 rater-cluster bootstrap samples per decision cell. The immediate design question is whether added raters or added item coverage buys more detector power without inflating false positives.
