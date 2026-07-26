# EGC 2.0 Matched Multiway-Bootstrap Power Calibration Review

**Date:** 2026-07-26  
**Design:** `complete_8x18_r8`  
**Regime:** N1 low-heterogeneity interior regime  
**Status:** engineering calibration; not confirmatory validation

## Question

The preceding 1,000-trial null calibration found that item-only percentile intervals were mildly anti-conservative while multinomial pigeonhole intervals were extremely conservative and substantially wider. The immediate unresolved question was whether the pigeonhole method's apparent Type-I error control was purchased at an unusable loss of power.

This run compares the two retained candidates against matched nonzero truth profiles at contrasts of `0.10`, `0.20`, and `0.30`.

## Data-generating intervention

The committed simulator's null generator was not rewritten. Instead, the power driver temporarily supplies the following class-shift profile before ordinal clipping:

```text
exact_anchor        = +effect / 2
surface_variant     = 0
structural_transfer = -effect / 2
novel               = -effect / 2
```

For the estimator

```text
exact_anchor - mean(structural_transfer, novel)
```

this gives the requested true contrast exactly before score clipping.

The same data seed is reused across effect sizes and resampling methods. This common-random-number design reduces Monte Carlo noise in paired comparisons without changing each cell's marginal generator.

## Execution

Each cell used:

- 250 independently generated datasets;
- 500 bootstrap draws;
- base seed `20260726`;
- the `complete_8x18_r8` design;
- the N1 low-heterogeneity interior regime;
- item-only cluster resampling or multinomial pigeonhole item-by-rater resampling.

The first row-reconstruction run exceeded the execution window and produced no retained result. The completed execution used cluster sufficient statistics with vectorized weighted sums. Twenty draw-by-draw comparisons per method against the committed row-reconstruction implementation differed by no more than `1e-12`.

## Results

| True contrast | Method | Detection power | Coverage | Mean interval width |
|---:|---|---:|---:|---:|
| 0.10 | Item-only | 0.252 | 0.924 | 0.3051 |
| 0.10 | Pigeonhole | 0.028 | 0.992 | 0.5116 |
| 0.20 | Item-only | 0.696 | 0.924 | 0.3047 |
| 0.20 | Pigeonhole | 0.252 | 0.992 | 0.5114 |
| 0.30 | Item-only | 0.956 | 0.924 | 0.3028 |
| 0.30 | Pigeonhole | 0.700 | 0.992 | 0.5114 |

Mean point-estimate bias was approximately `-0.0041` in every effect cell, consistent with minor ordinal clipping rather than method-specific estimation bias.

## Findings supported within this synthetic cell

1. **The pigeonhole interval loses substantial sensitivity.** At a material contrast of `0.20`, power was `25.2%`, compared with `69.6%` for item-only resampling.
2. **The loss is operationally serious at small effects.** At `0.10`, pigeonhole power was only `2.8%`.
3. **Even a strong `0.30` contrast was not reliably detected by pigeonhole intervals.** Power reached `70.0%`, below a conventional 80% planning target.
4. **Item-only intervals remain scientifically compromised despite much better power.** Their observed coverage was `92.4%` in every tested effect cell, consistent with the earlier null calibration's mild anti-conservatism.
5. **The current tradeoff is not acceptable for confirmatory inference.** One candidate is too liberal; the other is too insensitive.

## Claim decision

The prior status remains unchanged:

```text
uncertainty_method_not_validated_for_confirmatory_EGC_inference
```

The new evidence strengthens a narrower decision:

```text
multinomial_pigeonhole_percentile_interval_rejected_as_default_power_method_for_complete_8x18_N1
```

This rejection is limited to the tested percentile construction, design, regime, effect profile, and draw count. It does not reject all multiway resampling or product-weight methods.

## What is not established

This run does not establish:

- exact power at 1,000 trials or 2,000 draws;
- calibration under N2/N3 heterogeneity;
- performance in incomplete-block designs;
- performance with informative dropout or scale-boundary compression;
- validity of studentized, BCa, Poisson-product, analytic multiway-cluster, or model-based intervals;
- that the symmetric effect profile represents actual rater-process failures;
- that any uncertainty method is ready for confirmatory EGC use.

## Methodological consequence

Continuing to expand the pigeonhole percentile grid is low leverage. Its conservatism is not merely cosmetic: it converts deliberately material synthetic effects into nondetections at rates that would make the monitoring design ineffective.

The next method should target the calibration-power frontier directly. The strongest candidate is a studentized two-way procedure or an analytic two-way cluster-robust interval evaluated against the same common-random-number datasets. Any new method must beat both current candidates on prespecified criteria rather than merely splitting the difference informally.

## Highest-leverage next action

Implement an analytic two-way cluster-robust variance estimator for the mean contrast and calibrate it on the exact same N1 null and power seeds, reporting Type-I error, coverage, power, undefined/singular cases, and interval width against item-only and pigeonhole benchmarks.
