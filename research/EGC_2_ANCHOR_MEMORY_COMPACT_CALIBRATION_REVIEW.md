# EGC 2.0 Anchor-Memory Compact Calibration Review

**Status:** Synthetic engineering calibration, not empirical validation  
**Simulator:** `research/egc2/simulate_anchor_memory.py`  
**Results:** `research/egc2/results/anchor_memory_compact.json`

## Question

Can recurring exact-anchor performance falsely reassure researchers that scoring remains stable on unfamiliar responses?

The compact simulator compares three deliberately separated data-generating regimes:

1. **Generalized learning** — scoring improvement transfers across exact anchors, surface variants, structural-transfer probes, and novel responses.
2. **Pure memorization** — improvement is confined to exact recurring anchors.
3. **Memorization plus novel-item drift** — exact anchors improve while structural-transfer and novel responses deteriorate.

These are falsification regimes. Their parameters are not estimates of real EGC raters.

## Operational criterion

A trial produces **false reassurance** when:

- the exact recurring anchors improve by at least `0.35` scale points from early to late session; and
- novel items deteriorate by at least `0.35` scale points over the same period.

The threshold is provisional and must be varied in sensitivity analysis before use as a decision rule.

## Compact run

The run used:

- 250 Monte Carlo trials per regime;
- 8 synthetic raters;
- 18 observations per item class per rater;
- four item classes;
- fixed seed `20260725`;
- seven-point discretized scores.

## Findings

### Generalized learning

Mean early-to-late shifts were similar across all four classes:

- exact anchors: `+0.473`;
- surface variants: `+0.473`;
- structural transfer: `+0.468`;
- novel items: `+0.463`.

False reassurance occurred in `0.0%` of trials under this designed regime.

### Pure memorization

Mean improvement was concentrated in exact anchors:

- exact anchors: `+0.451`;
- surface variants: approximately `0.001`;
- structural transfer: approximately `-0.006`;
- novel items: approximately `-0.014`.

This shows why exact-anchor improvement alone cannot support generalized rubric learning. The false-reassurance criterion triggered in `1.2%` of trials because noise occasionally produced a material novel decline.

### Memorization plus novel-item drift

The designed adversarial pattern was recovered:

- exact anchors: `+0.455`;
- surface variants: `+0.151`;
- structural transfer: `-0.269`;
- novel items: `-0.554`.

Exact anchors improved in `78.0%` of trials, material novel drift occurred in `95.2%`, and the joint false-reassurance criterion occurred in `73.2%`.

## Supported finding

Within these synthetic regimes, a monitoring system based only on recurring exact anchors would frequently certify improvement while novel-item scoring materially worsened. Surface variants provided partial but incomplete warning; structural-transfer probes more clearly tracked the novel-item direction.

## What is not established

This run does not establish:

- that real EGC raters memorize anchors;
- the prevalence or magnitude of real rater drift;
- that `0.35` is the correct materiality threshold;
- that 18 observations per class are sufficient;
- that the simple early-versus-late estimator has calibrated uncertainty;
- that structural-transfer probes will behave as simulated;
- validity of the semantic-fidelity construct.

## Design implication

Recurring anchors must not be the sole drift monitor. The pilot should include all four classes, keep their identities hidden from raters, and treat divergence between exact-anchor and novel-item trajectories as a fail-closed signal.

## Next methodological requirement

Add uncertainty and threshold calibration. The next simulator version should vary:

- materiality threshold;
- class sample size;
- recognition strength;
- drift magnitude;
- rater heterogeneity;
- item difficulty;
- ordinal ceiling and floor effects.

It should estimate false-reassurance sensitivity and specificity rather than relying on a single designed parameter point.
