# EGC 2.0 Crossed Item–Rater Fixed-Budget Simulation Protocol

**Status:** Preregistered synthetic design specification; no empirical claim about real EGC raters  
**Purpose:** Resolve the item-breadth versus ratings-per-item tradeoff exposed by the workload-aware comparison  
**Primary comparison:** Fixed total rating budget with crossed item and rater heterogeneity

## 1. Decision problem

The current evidence does not justify choosing either the complete 8-rater × 18-item-per-class design or the incomplete-block 12-rater × 36-item-per-class design.

The complete design produced stronger detection under the current pooled estimator because each item received more ratings. The incomplete design sampled more unique items but its broader-content advantage was not represented by a crossed item-and-rater model.

This protocol defines the next simulation required before freezing the EGC 2.0 monitoring design.

The design question is:

> Under a fixed total rating budget, how should ratings be allocated between more independent raters, more unique items, and more ratings per item when rater severity, item difficulty, item ambiguity, domain heterogeneity, fatigue, anchor recognition, and informative dropout are all present?

## 2. Claims this simulation may and may not support

### Permitted conclusions

The simulation may support conditional engineering statements such as:

- one design has lower bias under the specified synthetic regimes;
- one design has better interval coverage or lower false-reassurance rate;
- one design generalizes better to newly sampled items or domains;
- one design is more robust to rater or item dropout;
- one design offers a better precision–generalization tradeoff at the fixed budget.

### Prohibited conclusions

The simulation cannot establish that:

- real EGC raters follow the chosen parameter distributions;
- a selected design is externally valid;
- the semantic-fidelity construct is valid;
- the final number of raters or items is scientifically sufficient;
- observed human reporting differences identify consciousness, hidden subjectivity, deception, intent, or any unique mechanism.

All outputs remain sensitivity analyses until calibrated against pilot data.

## 3. Fixed-budget candidate designs

Every candidate must use the same planned total rating budget per monitoring wave.

The first comparison shall include:

| Design ID | Raters | Unique items/class | Ratings/item | Classes | Planned ratings | Intended tradeoff |
|---|---:|---:|---:|---:|---:|---|
| `complete_8x18_r8` | 8 | 18 | 8 | 4 | 576 | dense item replication, narrow item bank |
| `incomplete_12x36_r4` | 12 | 36 | 4 | 4 | 576 | broad item bank, sparse item replication |
| `incomplete_12x24_r6` | 12 | 24 | 6 | 4 | 576 | intermediate breadth and replication |
| `complete_12x12_r12` | 12 | 12 | 12 | 4 | 576 | maximal within-item replication, narrowest bank |
| `incomplete_16x24_r6` | 16 | 24 | 6 | 4 | 576 | more independent raters with intermediate breadth |

If an exact balanced assignment cannot be generated for a proposed design, it must be rejected or explicitly labeled approximate before simulation. The generator must report per-rater workload, per-item rating count, co-rating graph connectivity, minimum degree, and imbalance.

## 4. Monitoring classes

The four concealed classes remain:

1. exact recurring anchors;
2. surface-variant anchors;
3. structural-transfer probes;
4. novel responses.

The scientific outcome is not the recurring-anchor trajectory alone. The primary failure mode is false reassurance: recurring anchors appear stable or improving while structural-transfer or novel-response scoring materially deteriorates.

## 5. Data-generating model

Let:

- `p` index participants or response sources;
- `i` index study items;
- `r` index raters;
- `d` index prompt domains;
- `c` index monitoring classes;
- `t` index session position or wave;
- `y_{pirdct}` be the observed ordinal rating.

A latent continuous rating shall be generated before ordinal discretization:

`y*_{pirdct} = μ + τ_c(t) + u_p + v_i + w_r + q_d + (vq)_{id} + (wq)_{rd} + h_i + f_r(t) + m_{rc}(t) + z_{pir} + ε_{pirdct}`

where:

- `μ` is the grand mean;
- `τ_c(t)` is the true class-specific early-to-late trajectory;
- `u_p` is participant or response-source heterogeneity;
- `v_i` is item difficulty;
- `w_r` is global rater severity;
- `q_d` is domain difficulty;
- `(vq)_{id}` is item-by-domain ambiguity or differential functioning;
- `(wq)_{rd}` is rater-by-domain severity;
- `h_i` is item-specific interpretability or ambiguity;
- `f_r(t)` is rater-specific fatigue or learning drift;
- `m_{rc}(t)` is class-specific recognition or memorization;
- `z_{pir}` is response-by-rater interaction;
- `ε` is residual noise.

The latent value is mapped to the seven-point ordinal scale through fixed or estimated thresholds. Results must be checked under both continuous-score analysis and ordinal discretization because clipping at 1 and 7 can conceal real changes.

## 6. Required heterogeneity regimes

At minimum, the compact engineering grid must vary:

### Item difficulty variance

- none;
- low;
- moderate;
- high.

### Item ambiguity variance

- none;
- moderate;
- high;
- sparse extreme ambiguity concentrated in 10% of items.

### Rater severity variance

- low;
- moderate;
- high.

### Rater-by-domain interaction

- absent;
- moderate;
- strong.

### Domain composition

- balanced domains;
- one difficult domain;
- one domain with stronger adverse drift;
- train-like domains plus one held-out domain.

### Fatigue and learning

- none;
- linear fatigue;
- nonlinear late-session fatigue;
- generalized rubric learning;
- exact-anchor memorization without transfer;
- memorization plus novel-item drift.

### Missingness and dropout

- missing completely at random;
- observed-covariate-dependent dropout;
- severity-dependent dropout;
- disagreement-dependent dropout;
- item-difficulty-dependent missingness;
- nonignorable sensitivity regimes where missingness depends on latent disagreement.

### Scale boundaries

- interior scores;
- floor-limited scores;
- ceiling-limited scores;
- mixed boundary compression by domain.

## 7. Ground-truth scenarios

Every design must be evaluated under at least these generating truths:

1. **Global stability:** all monitoring classes stable.
2. **Generalized learning:** all classes improve similarly.
3. **Pure memorization:** exact anchors improve; other classes remain stable.
4. **False reassurance:** exact anchors improve while novel and structural-transfer classes worsen.
5. **Directional cancellation:** some domains improve while others worsen, with mean change near zero.
6. **Sparse material failure:** one small domain or item subset deteriorates materially.
7. **Rater-process confounding:** rater composition shifts create an apparent class effect under a true zero scientific effect.
8. **Item-process confounding:** sampled item difficulty changes create an apparent class effect under a true zero effect.

## 8. Estimators to compare

The simulation must compare, at minimum:

### A. Pooled class-shift estimator

Retain the current estimator as a baseline. It is expected to favor dense designs and may understate item-generalization uncertainty.

### B. Rater-fixed-effect estimator

Control for stable global rater severity. This does not solve rater-by-domain interaction, informative dropout, or changing severity.

### C. Item-and-rater fixed-effect estimator

Include both rater and item indicators where estimable. This conditions on sampled items and therefore does not by itself estimate generalization to unseen items.

### D. Crossed random-effects estimator

Fit crossed item and rater effects, with domain and class trajectory terms. The implementation may use a validated external statistical library if standard-library-only code would materially weaken the method.

### E. Generalizability-theory decomposition

Estimate variance attributable to item, rater, domain, response, and major interactions. Use the decomposition to evaluate the expected dependability of each design under alternative numbers of raters and items.

No estimator may be labeled superior solely because it produces narrower intervals.

## 9. Primary operating characteristics

For every design × regime × estimator cell, report:

- bias of the target class-trajectory contrast;
- root mean squared error;
- empirical interval coverage;
- interval width;
- false-positive rate under global stability;
- false-reassurance support rate under the adversarial truth;
- indeterminate rate;
- sign-error rate;
- probability of missing a sparse material failure;
- effective number of independent raters and items;
- convergence or singular-fit rate;
- sensitivity to one-rater and one-item deletion;
- sensitivity to one-domain deletion.

## 10. Domain-generalization estimands

The simulation must distinguish:

1. **Conditional sampled-item effect:** inference restricted to the realized item bank.
2. **Item-population effect:** inference to new items drawn from the same domain distribution.
3. **Held-out-domain effect:** inference to an unseen prompt domain.

A design may perform well on the first and poorly on the second or third. Results must not collapse these estimands into one generic “generalization” claim.

For held-out-domain evaluation, simulate at least four domains and rotate each as the held-out domain. The model must be trained or estimated without using the held-out domain's class trajectory, then evaluated against its known generating truth.

## 11. Decision criteria

A candidate design may be provisionally preferred only if it satisfies all of the following across the preregistered core regimes:

- false-positive rate no greater than the prespecified tolerance;
- interval coverage not materially below nominal;
- acceptable false-reassurance sensitivity;
- acceptable held-out-item and held-out-domain error;
- no extreme singular-fit or convergence failure rate;
- no dependence on one rater, item, or domain for the decision;
- per-rater workload remains operationally plausible;
- superiority is not confined to a single favorable parameter regime.

No universal numeric threshold is fixed in this document. Thresholds must be chosen before examining the final high-precision run and justified in the accompanying analysis plan.

## 12. Fail-closed outcomes

Return `design_decision_indeterminate` when:

- estimator conclusions disagree materially;
- the preferred design changes under plausible item-variance values;
- interval coverage is materially sub-nominal;
- false-positive behavior exceeds tolerance;
- boundary compression destroys sensitivity;
- held-out-domain error is unacceptable;
- informative dropout reverses the preferred design;
- model convergence differs systematically by design.

Raw results must remain available even when the decision is blocked.

## 13. Compact engineering run

Before the full grid, run a compact matrix using:

- designs: all five candidate designs;
- item difficulty variance: low and high;
- item ambiguity variance: low and high;
- rater severity variance: moderate;
- domain interaction: absent and strong;
- truth: global stability, generalized learning, false reassurance, sparse material failure;
- dropout: none and severity-dependent;
- scale location: interior and ceiling-limited;
- at least 100 Monte Carlo trials per cell;
- a fixed seed recorded in the result artifact.

The compact run is for implementation debugging and gross failure detection. It must not be used to freeze the final design.

## 14. High-precision run

The final decision run should use enough trials to estimate operating characteristics with useful precision. At minimum:

- 1,000 trials per high-priority cell;
- exact code commit SHA;
- Python and package versions;
- runtime and hardware metadata;
- deterministic seed schedule;
- interrupted or failed cells preserved;
- machine-readable results plus a human-readable review.

## 15. Required tests

The implementation must include tests proving that:

1. every design obeys the fixed rating budget;
2. per-item and per-rater counts match the declared design;
3. fixed seeds reproduce identical scientific outputs;
4. increasing item variance changes item-generalization error;
5. increasing rater severity variance changes rater-related uncertainty;
6. the global-stability truth does not contain a generated class effect;
7. the false-reassurance truth contains opposing exact-anchor and novel trajectories;
8. the sparse-failure truth is confined to the designated subset;
9. ordinal clipping behaves as specified;
10. missingness mechanisms reduce observed data in the intended strata;
11. held-out-domain evaluation never trains on the held-out trajectory;
12. duplicated ratings do not falsely increase the number of independent items or raters;
13. singular or failed fits are preserved rather than silently discarded.

## 16. Evidence and interpretation standard

The simulation is a design-selection instrument, not a validation study. A preferred design remains provisional until pilot ratings provide empirical estimates for rater severity, item ambiguity, fatigue, recognition, domain effects, and missingness.

The highest-value output is not a winner at all costs. It is a defensible decision boundary showing which design is preferred under which assumptions, and where the evidence remains indeterminate.

## 17. Next highest-leverage action

Implement the compact crossed item-and-rater simulator against this protocol, beginning with the global-stability and false-reassurance truths. Preserve estimator failures, convergence diagnostics, item-population error, and held-out-domain error before expanding the parameter grid.