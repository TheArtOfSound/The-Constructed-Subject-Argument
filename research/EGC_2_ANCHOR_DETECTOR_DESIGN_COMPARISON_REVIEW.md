# EGC 2.0 Anchor Detector Design Comparison Review

## Status

**Artifact type:** synthetic engineering calibration review  
**Decision addressed:** whether additional independent raters or broader item-class coverage produces the larger gain in detecting false reassurance from recurring anchors  
**Primary threshold:** `delta = 0.20`  
**Interpretation limit:** these parameters are stress regimes, not empirical estimates of real EGC raters

## Design

The comparison crossed:

- rater counts: 8, 12, and 16;
- items per class: 18 and 36;
- five environments: interior, low noise, high noise, floor-limited, and ceiling-limited;
- three generating regimes: generalized learning, pure memorization, and memorization plus novel-item drift.

Each cell used 100 Monte Carlo trials and 100 whole-rater bootstrap draws. The detector supported false reassurance only when the lower 95% bound for recurring-anchor improvement exceeded `+0.20` and the upper 95% bound for novel-item change was below `-0.20`.

The executable comparison preserves the committed simulator's random-number sequence and ordinal clipping while aggregating only the rater-level early-versus-late shifts needed by the detector.

## Results

### Interior regime

| Design | Supported | Indeterminate |
|---|---:|---:|
| 8 raters × 18 items | 0.44 | 0.56 |
| 8 × 36 | 0.71 | 0.29 |
| 12 × 18 | 0.63 | 0.37 |
| 12 × 36 | 0.92 | 0.08 |
| 16 × 18 | 0.76 | 0.24 |
| 16 × 36 | 0.98 | 0.02 |

Doubling item coverage from 18 to 36 at eight raters increased support by 0.27. Increasing raters from 8 to 16 while retaining 18 items increased support by 0.32. Neither dimension alone was enough for consistently high sensitivity; the joint 12 × 36 design reached 0.92 support.

### High-noise regime

| Design | Supported | Indeterminate |
|---|---:|---:|
| 8 × 18 | 0.20 | 0.80 |
| 8 × 36 | 0.33 | 0.67 |
| 12 × 18 | 0.24 | 0.76 |
| 12 × 36 | 0.60 | 0.40 |
| 16 × 18 | 0.32 | 0.68 |
| 16 × 36 | 0.69 | 0.31 |

Under high noise, broader item coverage was more valuable than adding raters alone. At 12 raters, doubling items increased support by 0.36; at 18 items, increasing from 8 to 16 raters increased support by only 0.12.

### Floor and ceiling regimes

Even the largest tested design remained weak:

- floor-limited, 16 × 36: 0.40 support;
- ceiling-limited, 16 × 36: 0.24 support.

This is not primarily a sample-size problem. Ordinal scale compression removes observable room for the required directional changes. More raters and items cannot fully recover information that the outcome scale does not contain.

### False-positive screen

The maximum observed support rate across the generalized-learning and pure-memorization cells was 0.01. This is encouraging but not a validated false-positive guarantee: 100 trials per cell is insufficient for precise tail-rate claims, and percentile-bootstrap coverage remains uncalibrated.

## Findings supported within this synthetic comparison

1. **The current 8 × 18 design is underpowered for the detector.** Interior support was 0.44 and high-noise support was 0.20.
2. **A balanced expansion is stronger than choosing only one dimension.** The 12 × 36 design produced 0.92 interior support and 0.60 high-noise support.
3. **Item coverage is especially valuable under high noise.** Repeated independent content reduces uncertainty in each rater's transfer trajectory.
4. **Additional raters remain valuable in ordinary interior conditions.** Rater count and item count address different variance sources and are not interchangeable.
5. **Floor and ceiling compression require a fail-closed dynamic-range gate.** A negative or indeterminate detector result near the rating boundaries cannot support stability.

## Hypotheses and unresolved uncertainty

- It is not established that 12 × 36 is the cost-optimal real pilot design.
- Real rater variance, recognition strength, item dependence, fatigue, and dropout may differ materially from the simulator.
- The 36 items per class in this synthetic design may impose unacceptable fatigue in an actual session; splitting content across sessions or raters may be necessary.
- The bootstrap's interval coverage has not been established at these rater counts.
- The materiality threshold `0.20` is provisional and lacks empirical construct validation.

## Design recommendation

Use **12 raters and 36 observations per monitoring class as the provisional calibration target**, not as a final confirmatory requirement. This is the smallest tested joint design that exceeded 0.90 support in the interior regime while retaining meaningful, though incomplete, sensitivity under high noise.

Do not simply assign every rater 36 items in every class without a workload study. The next assignment architecture should distribute the larger item bank through a connected incomplete-block design so that item coverage increases without making each individual session unreasonably long.

## Prohibited conclusions

This simulation does not show that:

- real EGC raters memorize anchors;
- 12 × 36 guarantees reliable detection;
- recurring-anchor divergence validates semantic fidelity;
- a detector failure establishes stable scoring;
- any result bears on AI consciousness, deception, awareness, or intent.

## Highest-leverage next action

Design and simulate a **12-rater connected incomplete-block anchor-monitoring assignment** that achieves 36 observations per item class at the study level while constraining each rater's workload, preserving exact-anchor/surface/transfer/novel concealment, and maintaining dropout robustness.
