# EGC 2.0 Structural Validity Gates and Dropout Stress-Test Preregistration

**Status:** prospective simulation contract; thresholds are provisional and not empirically validated  
**Target design:** `incomplete_12x24_r6`  
**Target regime:** N3  
**Companion machine-readable specification:** `research/egc2/structural_validity_gates.v0.1.json`

## 1. Decision problem

The current restricted wild-cluster candidate can return an apparently calibrated p-value after selective missingness has materially weakened the planned item-rater design. The previous informative-dropout calibration found that approximately 13%–14% row-level dropout did not visibly inflate Type-I error, while some items fell below the planned replication level. That result does not establish robustness. It shows that **inferential computability and structural validity are different questions**.

This preregistration fixes the structural checks before simulating complete rater loss or domain-selective attrition. The purpose is to prevent post-hoc threshold selection and to ensure that an inferential result is withheld when the retained data no longer support the planned comparison.

The primary output is not always a p-value. It is one of:

```text
structurally_valid_inference_defined
indeterminate_due_to_structural_invalidity
indeterminate_due_to_inferential_noncomputability
```

Raw estimates, missingness summaries, graph diagnostics, and failure reasons must still be preserved.

## 2. Evidence basis and limits

Rater-mediated measurement depends on coverage and linkage, not merely the number of retained rows. Sparse-design research shows that incomplete rating structures can conceal rater effects and that analytic performance changes with coverage. Balanced incomplete-block and spiral designs can support estimation efficiently, but extreme or weakly linked raters can still bias results. Benchmark overlap has been used operationally to strengthen sparse rater-linking networks.

Relevant prior work:

- Braun, H. I. (1986), *Calibration of Essay Readers: Final Report*, ETS RR-86-09, DOI: `10.1002/j.2330-8516.1986.tb00164.x`.
- Hombo, C. M., Donoghue, J. R., & Thayer, D. T. (2001), *A Simulation Study of the Effect of Rater Designs on Ability Estimation*, ETS RR-01-05, DOI: `10.1002/j.2333-8504.2001.tb01847.x`.
- Myford, C. M. (2000), *Strengthening the Ties That Bind: Improving the Linking Network in Sparsely Connected Rating Designs*, ETS RR-00-09.
- Wind, S. A. et al. (2023), “Does Sparseness Matter? Examining the Use of Generalizability Theory and Many-Facet Rasch Measurement in Sparse Rating Designs,” PMCID: `PMC10552733`.

These sources justify treating coverage, linkage, and rater effects as explicit design properties. They do **not** validate the numerical thresholds below for EGC. Thresholds are prospective engineering choices to be calibrated by simulation and later revised only through an explicit protocol amendment.

## 3. Fixed complete-data design

The complete assignment contains:

- 12 raters;
- four concealed monitoring classes;
- 24 items per class;
- six planned ratings per item;
- 576 planned ratings;
- multiple confirmatory content domains;
- a connected incomplete-block item-rater graph before missingness.

The inferential target and synthetic data-generating process remain unchanged from the N3 restricted-wild calibration unless a separate amendment states otherwise.

## 4. New missingness mechanisms

All mechanisms operate after complete ratings are generated. Selection parameters are sensitivity settings, not estimates of actual human dropout.

### 4.1 Whole-rater loss

Remove complete rating histories for:

1. one uniformly selected rater;
2. two uniformly selected raters;
3. the most severe rater;
4. the most lenient rater;
5. the two raters with the largest absolute severity;
6. the rater with the greatest complete-data disagreement;
7. the two raters with the greatest complete-data disagreement.

Severity- and disagreement-targeted removals are adversarial oracle analyses. They are not operational missingness models.

### 4.2 Domain-selective row dropout

For a randomly selected confirmatory domain, increase row-level dropout only within that domain. Test target mean domain-specific dropout rates of approximately:

- 15%;
- 30%;
- 50%.

The other domains retain the baseline dropout probability. Preserve the selected domain identity in the audit output.

### 4.3 Domain-selective rater dropout

Select one domain and remove all ratings in that domain from:

1. one uniformly selected rater;
2. two uniformly selected raters;
3. the most severe rater in that domain;
4. the rater with the greatest disagreement in that domain.

This mechanism can preserve an overall active-rater count while collapsing domain-specific support; therefore, overall coverage alone is insufficient.

### 4.4 Combined structural attack

Combine:

- one whole-rater loss;
- 30% domain-selective row dropout;
- severity-plus-disagreement row dropout from the prior calibration.

This is a deliberate stress test, not a realistic prevalence claim.

## 5. Structural gates

The exact machine-readable rules are in `research/egc2/structural_validity_gates.v0.1.json`. Gate order is fixed.

### G0 — Schema and identity

Every retained rating must map to exactly one planned item, rater, monitoring class, and domain. Unknown and duplicate identities fail immediately.

### G1 — Item replication

- Every analyzed item must retain ratings from at least four distinct raters.
- At least 95% of items must retain five or more ratings.

The design plans six ratings per item. Four is a fail-closed floor chosen because the assignment was designed to survive two complete rater losses mechanically. It is **not** asserted to be a validated reliability threshold.

### G2 — Active-rater coverage

- At least 10 of 12 raters must remain active overall.
- Every monitoring class must include at least eight active raters.
- Every confirmatory domain must include at least eight active raters.

This prevents a pooled analysis from being supported by a narrow rater subset in one class or domain.

### G3 — Monitoring-class balance

- Every class must retain at least 80% of planned assignments.
- The range between the highest and lowest class retention fractions must not exceed 0.10.

### G4 — Domain balance

- Every confirmatory domain must retain at least 75% of planned assignments.
- Within each monitoring class, the range between the highest and lowest domain retention fractions must not exceed 0.15.

### G5 — Graph identifiability

All of the following retained graphs must be connected:

1. the item-rater bipartite graph;
2. the overall rater co-rating graph;
3. every monitoring-class-specific rater co-rating graph.

The audit must also report:

- component memberships;
- minimum item and rater degree;
- articulation raters;
- bridge edges.

Connectivity is necessary for linkage. It does not prove unbiasedness, precision, reliability, or robustness to informative missingness.

### G6 — Inferential computability

The existing provisional restricted-wild requirements remain:

- positive observed two-way variance;
- no more than 10% of exact Rademacher patterns with nonpositive bootstrap variance.

The 10% threshold remains unvalidated and must be included in sensitivity analysis.

## 6. Gate precedence and reporting

Gates are evaluated in the order G0 through G6.

If G0–G5 fail, the result is:

```text
indeterminate_due_to_structural_invalidity
```

The restricted-wild p-value must not be promoted as a confirmatory result, even if it can be calculated.

If G0–G5 pass but G6 fails, the result is:

```text
indeterminate_due_to_inferential_noncomputability
```

If all gates pass, the result is:

```text
structurally_valid_inference_defined
```

This label means only that the preregistered structural and computational checks passed. It does not validate the construct, missingness assumptions, or uncertainty method.

Every failed run must retain:

- the raw point estimate;
- all gate values;
- all failure reasons, not only the first;
- the first failure under the fixed precedence order;
- the missingness mechanism and parameters;
- the selected raters/domains;
- the graph diagnostics;
- the restricted-wild diagnostics when computable.

## 7. Simulation outcomes

For each mechanism, report separately under the true null and effect `0.20`:

1. all-trial rejection or power;
2. rejection or power conditional on all structural gates passing;
3. fraction structurally indeterminate;
4. fraction inferentially indeterminate;
5. each gate’s marginal and first-failure rate;
6. joint gate-failure patterns;
7. retained-rating fraction;
8. active-rater count overall and by class/domain;
9. minimum and distribution of ratings per item;
10. class/domain retention imbalance;
11. graph component, articulation, bridge, and degree diagnostics;
12. undefined-pattern distribution;
13. bias and RMSE of the point estimate.

A low all-trial Type-I error that is achieved by declaring many datasets indeterminate is not sufficient evidence of a useful method. Conditional error must not replace the all-trial denominator; both are required.

## 8. Falsification conditions

The current design or inference procedure is weakened if any plausible mechanism produces:

- all-trial Type-I error above 7.5%;
- conditional Type-I error above 7.5% among structurally valid datasets;
- more than 10% structurally indeterminate datasets under moderate dropout;
- material sign reversal after one rater or one domain is removed;
- a disconnected class-specific graph while the pooled graph remains connected;
- domain retention below threshold without the gate detecting it;
- acceptable p-values paired with systematic item-replication failure;
- power below 50% at effect `0.20` after excluding structurally invalid datasets;
- conclusions that materially depend on the provisional 10% undefined-pattern threshold.

The 7.5%, 10%, and 50% decision boundaries are design-screening criteria, not universal statistical standards.

## 9. Required threshold sensitivity analysis

Repeat summaries across:

- item floors: 3, 4, 5;
- overall active-rater floors: 8, 9, 10, 11;
- minimum class retention: 0.70, 0.80, 0.90;
- minimum domain retention: 0.60, 0.75, 0.90;
- undefined-pattern thresholds: 0.05, 0.10, 0.20.

The primary gate specification remains frozen. Sensitivity results show whether the conclusion is threshold-dependent; they do not authorize selecting the most favorable threshold after the run.

## 10. Permitted conclusions

If the gates behave as intended, the study may conclude narrowly that:

- the preregistered checks detect specified structural failures in synthetic data;
- some missingness mechanisms cause structural invalidity before inferential noncomputability;
- a particular design retains or loses its planned linkage under specified simulated attacks;
- the restricted-wild candidate has stated calibration and power only among the tested synthetic regimes.

## 11. Prohibited conclusions

This work cannot establish that:

- informative dropout is ignorable;
- passing the gates validates semantic fidelity or subjective resistance;
- four ratings per item are generally sufficient;
- graph connectivity proves adequate reliability or unbiasedness;
- the thresholds are empirically validated for human raters;
- one context contrast indicates awareness, concealment, deception, intent, or consciousness.

## 12. Single highest-leverage next action

Implement the gate evaluator and the four missingness families, add deterministic adversarial tests for each gate, then run a small smoke grid to verify that structural invalidity is detected before any high-precision calibration is launched.
