# EGC 2.0 Resumable Multiway Calibration Driver

**Status:** engineering implementation complete; high-precision calibration not yet run  
**Date:** 2026-07-26

## Concrete contribution

`research/egc2/calibrate_multiway_bootstrap_resumable.py` implements the focused null-calibration driver specified in `EGC_2_MULTIWAY_BOOTSTRAP_PRIOR_ART_AND_CALIBRATION_DECISION.md`.

It imports the committed crossed item-rater simulator rather than duplicating the data-generating model. The first supported scope is:

- designs: `complete_8x18_r8`, `incomplete_12x24_r6`, `incomplete_16x24_r6`;
- null regimes: N1 low heterogeneity, N2 high item heterogeneity, N3 high rater and rater-by-domain heterogeneity;
- methods: item-only cluster bootstrap, rater-only cluster bootstrap, and multinomial pigeonhole bootstrap;
- nested draw levels: 100, 500, and 2,000;
- default target: 1,000 generated datasets per cell.

## Resume and failure behavior

The driver writes one strict-JSON record per completed design × regime × method cell. Each record is flushed and `fsync`-ed immediately. On restart, completed cell keys are loaded and skipped.

A duplicate cell with bytewise-equivalent scientific content is tolerated by the loader. A duplicate key with conflicting content fails closed rather than silently selecting one result.

The optional `--stop-after-cells` argument exists only to test interruption and resume behavior. It is not a scientific stopping rule.

## Nested bootstrap reuse

For each generated dataset and method, the driver produces one deterministic stream of `max_draws` bootstrap replicates. Intervals at 100 and 500 draws use prefixes of that same stream. Therefore endpoint movement measures bootstrap Monte Carlo convergence rather than differences caused by unrelated random draws.

Seeds are deterministically derived from:

```text
base seed × design × null regime × trial × method × purpose
```

This prevents cell ordering and interrupted execution from changing already specified draws.

## Recorded evidence

Every completed cell preserves:

- all trial-level data and draw seeds;
- interval endpoints at every retained draw level;
- reject/nonreject decisions;
- undefined-draw counts;
- Type-I error and coverage;
- exact Clopper-Pearson intervals for the Monte Carlo false-positive rate;
- interval width;
- endpoint movement and decision changes;
- runtime, Python version, platform, command, base seed, and repository SHA when available.

Missing convergence comparisons are serialized as JSON `null`, not nonstandard `NaN`.

## Validation completed

Six focused tests cover:

1. deterministic and partitioned seed derivation;
2. exact nested-prefix reuse;
3. completed-cell loading;
4. fail-closed conflicting duplicate detection;
5. deterministic cell output apart from elapsed runtime;
6. Clopper-Pearson boundary behavior.

An isolated integration run also verified that rerunning an already completed cell leaves the output file unchanged and that produced JSON parses in strict mode.

## Evidence boundary

The full repository could not be cloned in the execution container because GitHub DNS resolution was unavailable. Validation therefore used the committed simulator's fetched public function contract in an isolated local harness. Repository-wide CI success is not claimed.

No high-trial operating characteristic is claimed in this run. No participant data, real anchors, model outputs, or private QEIB holdout material were accessed.

## Claim status

### Supported

- A resumable cell-level calibration driver now exists.
- Nested 100/500/2,000 draw comparisons reuse identical bootstrap prefixes.
- Cell ordering and interruption do not alter deterministic scientific seeds.
- Conflicting duplicate outputs are rejected rather than merged silently.

### Not yet supported

- Nominal Type-I error for any bootstrap method.
- Adequate endpoint convergence at 2,000 draws.
- Preference among item, rater, or pigeonhole intervals.
- Validity under informative dropout, floor/ceiling compression, or the nonlinear false-reassurance conjunction.

## Highest-leverage next action

Run one complete 1,000-trial N1 cell for each method on `complete_8x18_r8`, preserve the JSONL output, and inspect runtime plus 100→500→2,000 endpoint convergence before launching the remaining eight design-regime cells.
