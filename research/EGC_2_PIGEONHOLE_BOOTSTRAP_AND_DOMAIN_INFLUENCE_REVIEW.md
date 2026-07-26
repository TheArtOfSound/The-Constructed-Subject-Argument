# EGC 2.0 Pigeonhole Bootstrap and Material Domain-Influence Review

**Status:** reduced engineering calibration; not publication-grade validation  
**Scope:** synthetic crossed item–rater simulator only  
**Private holdout:** not accessed

## Task completed

This run implemented two previously missing diagnostics:

1. a two-way item-by-rater bootstrap using independent multinomial weights for item and rater clusters, with each observed rating weighted by the product of its sampled item and rater counts;
2. a magnitude-aware leave-one-domain-out rule that separates raw sign changes from materially consequential domain influence.

The two-way procedure is labeled `pigeonhole` in the executable. It is a diagnostic adaptation for crossed dependence. It is not asserted to be exact for sparse, unbalanced, clipped ordinal data.

## Failed full run preserved

The planned 100-trial × 100-bootstrap-draw diagnostic exceeded the available execution window and produced no completed result artifact. No values were inferred from the interrupted run.

A reduced run was then completed with:

```bash
python research/egc2/simulate_crossed_item_rater.py \
  --diagnostic \
  --trials 40 \
  --bootstrap-samples 50 \
  --domain-threshold 0.10 \
  --output research/egc2/results/crossed_pigeonhole_bootstrap_40x50.json
```

The reduced run covers all five fixed-budget designs under item SD `1.0`, severity-dependent dropout, global-stability truth, and strong false-reassurance truth.

## Two-way bootstrap result

Across the ten reduced cells:

- item-only coverage ranged from `0.85` to `1.00`;
- rater-only coverage ranged from `0.775` to `0.925`;
- pigeonhole coverage ranged from `0.95` to `1.00`;
- mean pigeonhole interval width ranged from approximately `0.468` to `0.498`;
- mean item-only width ranged from approximately `0.278` to `0.302`;
- mean rater-only width ranged from approximately `0.248` to `0.289`.

The two-way intervals were therefore substantially wider and more conservative in this reduced grid. That is directionally consistent with the fact that both item and rater sampling contribute uncertainty. However, 40 trials and 50 bootstrap draws per trial are too small to establish nominal coverage, tail behavior, or superiority.

### Supported finding

Within these synthetic cells, item-only and especially rater-only resampling can materially understate uncertainty relative to the two-way procedure.

### Not supported

The reduced result does not establish that the pigeonhole interval is correctly calibrated, optimal, or suitable for confirmatory EGC inference. Observed coverage of `1.00` in several 40-trial cells may indicate conservatism, Monte Carlo noise, or both.

## Domain-influence correction

The earlier diagnostic treated any leave-one-domain-out sign change as instability. That rule was defective near a null contrast, where tiny numerical perturbations can reverse the sign without changing the scientific conclusion.

The new rule reports:

- the contrast after omitting each domain;
- the signed and absolute change from the full contrast;
- the most influential domain;
- whether any absolute change meets a prespecified materiality threshold;
- whether a sign reversal is also materially large.

For this engineering run, the threshold was explicitly set to `0.10`. This is a provisional sensitivity threshold, not a validated scientific constant.

### Reduced-run comparison

Under global stability:

- raw sign-change rates ranged from `0.475` to `0.575`;
- material-influence rates ranged from `0.075` to `0.10`;
- material sign-reversal rates ranged from `0.025` to `0.075`.

Thus most raw sign changes disappeared once a magnitude requirement was imposed. This confirms that sign alone was generating substantial false instability near zero.

Under the strong false-reassurance truth:

- raw sign-change rates were `0.00` in every design;
- material-influence rates ranged from `0.10` to `0.15`;
- material sign-reversal rates were `0.00`.

The nonzero material-influence rate does not imply a failed effect; it indicates that omitting some domains changed the estimated contrast by at least `0.10` even without reversing its direction.

## Claims discipline

### Supported within the simulator

- Joint item-and-rater resampling produces materially wider intervals than either one-axis bootstrap in the reduced crossed design.
- Rater-only coverage was particularly weak in several cells.
- Raw leave-one-domain-out sign flips are a poor instability metric near zero.
- A magnitude-aware domain rule sharply reduces spurious instability flags while preserving large omission effects.

### Weakened or rejected

- Rejected: any domain-omission sign change is automatically scientifically material.
- Weakened: one-axis bootstrap inference is adequate for crossed EGC ratings.
- Not accepted: the pigeonhole bootstrap is calibrated merely because reduced-cell coverage was high.

### Unresolved

- Coverage and type-I error at substantially higher Monte Carlo counts.
- Whether multinomial pigeonhole weighting is overly conservative for the incomplete-block designs.
- Appropriate domain-influence thresholds for the actual semantic-fidelity scale.
- Behavior under domain-specific true effects, item-by-domain interactions, boundary compression, and nonignorable dropout.
- Comparison with crossed mixed-effects, Bayesian hierarchical, and generalizability-theory estimators.

## Required next decision rule

Until higher-precision calibration succeeds, crossed-simulator inference remains:

```text
design_decision_indeterminate
```

No candidate rating design should be selected because it happens to obtain the narrowest one-axis interval.

## Highest-leverage next action

Run a targeted high-precision calibration of the pigeonhole procedure under the global-stability truth, including at least 1,000 Monte Carlo trials for a reduced subset of designs and bootstrap-draw convergence checks at 100, 500, and 2,000 draws. The immediate question is whether the apparent conservatism persists and whether false-positive control is actually near nominal.
