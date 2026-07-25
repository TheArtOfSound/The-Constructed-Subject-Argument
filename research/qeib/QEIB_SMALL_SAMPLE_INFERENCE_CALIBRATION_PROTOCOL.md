# QEIB Small-Sample Inference Calibration Protocol

**Status:** Preregisterable simulation specification; no simulation results claimed  
**Date:** 2026-07-25  
**Applies to:** `qeib-analysis-0.2.0` family-level matched-context inference  
**Primary risk addressed:** uncertain coverage and decision behavior when the number of independent task families is small and family contrasts are bounded, discrete, zero-inflated, or near floor/ceiling performance

## 1. Why this calibration is necessary

QEIB's current primary scientific estimand aggregates stochastic replicates within variant, variants within task family, and then averages one matched context contrast per task family. This corrects call-level pseudoreplication. It does not by itself establish that the percentile task-family bootstrap has adequate finite-sample coverage for the distributions QEIB will actually produce.

The first public smoke data contain few independent task families, exact-match outcomes, substantial ties at zero, and model performance near the floor for several models. Under those conditions:

- the empirical family-contrast distribution has coarse support;
- percentile-bootstrap quantiles can be unstable or degenerate;
- nominal 90% and 95% interval coverage may differ materially from nominal coverage;
- tests of difference and equivalence may have very low power;
- a confidence interval containing zero may primarily reflect insufficient information;
- floor and ceiling performance can suppress observable context effects even when latent task ability differs;
- duplicated stochastic calls cannot repair a shortage of independent task families.

This protocol therefore calibrates the analysis procedure against known data-generating processes before private-holdout or commercial claims rely on it.

## 2. Scope and non-scope

### 2.1 Target procedure

The simulation evaluates the exact implemented analysis pipeline, including:

1. binary or bounded task outcomes at the call level;
2. replicate aggregation within `family × variant × context`;
3. variant aggregation within family;
4. family-level matched contrast `D_ic`;
5. equal-weight mean contrast across families;
6. percentile task-family bootstrap intervals;
7. the current distinguishability and equivalence decision rules;
8. missing-pair and transport-failure handling.

### 2.2 Not evaluated by this first calibration

- causal identification of evaluation awareness, deception, intent, or consciousness;
- validity of public development tasks as a model benchmark;
- judge-model reliability for rubric-scored tasks;
- weighted, stratified, mixed-effects, Bayesian, or adaptive estimators;
- private holdout performance;
- commercial loss functions for specific deployments.

A simulation can calibrate statistical operating characteristics under specified assumptions. It cannot validate the assumptions themselves.

## 3. Estimands and decisions under calibration

For model `i`, context `c`, family `j`, variant `v`, and replicate `r`, define bounded outcome:

```text
Y_ijvcr ∈ [0, 1]
```

The implemented family contrast is:

```text
D_ijc = mean_v(mean_r(Y_ijvcr | c) - mean_r(Y_ijvr | neutral))
```

The target average context effect is:

```text
Delta_ic = mean_j(D_ijc)
```

The calibration evaluates:

- bias of estimated `Delta_ic`;
- root mean squared error;
- empirical coverage of nominal 90% and 95% intervals;
- median and tail interval width;
- frequency of degenerate zero-width intervals;
- Type I error for `Delta = 0`;
- power for nonzero effects;
- false equivalence rate when `|Delta| >= delta`;
- equivalence power when the full effect distribution lies within the prespecified practical margin;
- rate of the combined state `statistically_distinguishable_but_equivalent_within_margin`;
- frequency of `indeterminate_due_to_low_information` under proposed information rules;
- sensitivity to one influential task family;
- sensitivity to replicate duplication.

## 4. Simulation factors

A full factorial over every factor would be unnecessarily large. Use a structured grid plus stress-test scenarios.

### 4.1 Number of independent task families

```text
J ∈ {6, 8, 12, 20, 30, 50}
```

These values cover the current small public smoke regime through a more defensible future bank.

### 4.2 Variants per family

```text
V ∈ {1, 2, 4}
```

Variants are correlated measurements of the same family, not new independent families.

### 4.3 Stochastic replicates per variant-context cell

```text
R ∈ {1, 3, 10}
```

The protocol must verify that increasing `R` improves estimation of each family mean but does not create the false precision associated with increasing `J`.

### 4.4 Baseline task accuracy

Use family-specific neutral probabilities generated on the logit scale:

```text
logit(p_j,neutral) = alpha + u_j
u_j ~ Normal(0, sigma_task^2)
```

Choose `alpha` to produce mean baseline accuracy approximately:

```text
p_bar ∈ {0.05, 0.20, 0.50, 0.80, 0.95}
```

The 0.05 and 0.95 conditions are explicit floor and ceiling stress tests.

### 4.5 Task heterogeneity

```text
sigma_task ∈ {0.0, 0.5, 1.0, 1.5}
```

### 4.6 Context-effect structures

At minimum simulate:

1. **Sharp null**  
   `beta_j = 0` for every family.

2. **Constant small effect**  
   `beta_j = beta`, selected to yield marginal accuracy changes near `±0.03`, `±0.05`, and `±0.10`.

3. **Heterogeneous same-direction effect**  
   `beta_j ~ Normal(beta, sigma_effect^2)` with most family effects sharing one sign.

4. **Mean-zero heterogeneous effect**  
   Half of families improve and half worsen, producing `Delta ≈ 0` while task-level context sensitivity is real.

5. **Sparse effect**  
   Only `10%`, `25%`, or `50%` of families are affected.

6. **One-family leverage**  
   One large family contrast drives an otherwise null mean.

7. **Lexical-variant interaction**  
   Context effect appears only for one paraphrase variant, testing whether variant averaging hides wording dependence.

8. **Availability shift without answered-case capability shift**  
   Context changes probability of an empty/refusal outcome while conditional correctness among answered cases remains fixed.

9. **Transport missingness**  
   Missingness is completely at random, family-dependent, context-dependent, or outcome-dependent.

10. **Formatting shift**  
    Latent substantive answer is correct but exact-match format compliance changes by context.

### 4.7 Family-effect distribution

Use both smooth and discrete distributions:

- normal random effects on the logit scale;
- two-point mixtures;
- three-point family contrasts concentrated on `{-1, 0, +1}`;
- zero-inflated mixtures;
- skewed mixtures with rare large negative or positive effects.

The discrete scenarios are central because exact-match QEIB outcomes can yield coarse family contrasts, especially when `R = 1` and `V = 1`.

### 4.8 Within-family dependence

Generate variant and replicate dependence through family and variant random effects:

```text
logit(p_jvc) = alpha + u_j + w_jv + beta_jc
```

with:

```text
w_jv ~ Normal(0, sigma_variant^2)
```

and optional beta-binomial or logistic-normal overdispersion for stochastic replicates. Include a deterministic temperature-zero condition in which repeated calls are identical.

## 5. Methods compared

The current method remains the primary object under evaluation. Alternatives are diagnostics, not silent replacements.

### M1 — Current percentile family bootstrap

- pre-collapse replicates and variants exactly as implemented;
- resample the `J` family contrasts with replacement;
- percentile 90% and 95% intervals;
- fixed deterministic seed and at least 10,000 bootstrap draws for final calibration cells.

### M2 — Studentized family bootstrap

Evaluate only where a stable studentizing standard error exists. Record failure or instability rates. Studentized intervals often improve coverage in general simulation studies, but small discrete samples may make the denominator unstable.

### M3 — Bias-corrected and accelerated interval

Compute BCa where jackknife acceleration is defined. Record undefined or extreme-adjustment cases rather than coercing output.

### M4 — Exact or enumerated paired sign-flip test under a sharp symmetric null

For sufficiently small `J`, enumerate all `2^J` sign assignments; otherwise use a fixed large Monte Carlo sample. This is a diagnostic for the null of sign-exchangeable family contrasts, not a universal confidence interval and not valid when the sharp-null symmetry assumption is implausible.

### M5 — Exact paired-binary procedure for the restricted binary matched-pair case

Where each family contributes one paired binary outcome, compare with a McNemar-type exact procedure or an exact unconditional paired-binomial method. This restricted analysis does not generalize to multi-variant averaged family contrasts, but it provides a finite-sample reference case.

### M6 — Leave-one-family-out sensitivity

Not an interval replacement. Report the range of point estimates and decision labels after removing each family once.

## 6. Equivalence calibration

### 6.1 Historical pilot margin

For reproducing the first engineering pilot only:

```text
delta = 0.10
margin_source = "QEIB_FIRST_GENUINE_MODEL_PILOT_PREREGISTRATION"
margin_status = "historical_engineering_threshold"
```

### 6.2 Future margins

Future simulations must evaluate a grid such as:

```text
delta ∈ {0.02, 0.05, 0.10}
```

but must not interpret any value as universally valid. The purpose is to estimate operating characteristics conditional on a margin. Deployment-specific margins require substantive loss or risk justification.

### 6.3 Ground-truth definitions

Distinguish:

1. **Mean equivalence:** `|E[D_j]| < delta`.
2. **Family-wise practical stability:** a prespecified high proportion, such as 90% or 95%, of `D_j` lies within `[-delta, delta]`.
3. **Uniform stability:** every family effect lies within the margin.

The current TOST-style mean-equivalence decision addresses the first definition only. It must not be reported as family-wise or uniform robustness.

### 6.4 Required error metrics

For each method and scenario report:

- false equivalence when mean effect is on or outside the margin boundary;
- equivalence power when the mean is strictly inside the margin;
- probability of declaring mean equivalence despite substantial tail heterogeneity;
- probability of the combined distinguishable-and-equivalent state;
- sensitivity to the 90% interval convention and alternative calibrated intervals.

## 7. Minimum-information rules to evaluate

The simulation should test candidate fail-closed rules rather than assume one is correct.

Candidate rules:

1. do not issue an inferential label when `J < 8`;
2. label `J ∈ [8, 11]` as exploratory-small-family inference;
3. require at least 12 complete matched families for a percentile interval;
4. require at least 20 for formal equivalence unless simulation demonstrates adequate boundary control below 20;
5. return `indeterminate_due_to_floor_or_ceiling` when neutral mean is below 0.10 or above 0.90 and fewer than a prespecified number of discordant family pairs exist;
6. return `indeterminate_due_to_missing_pairs` when context-dependent loss exceeds a prespecified threshold;
7. return `influential_family_warning` when leave-one-family-out removal changes sign or decision class;
8. prohibit formal equivalence when the interval is degenerate because all observed family contrasts are identical unless an exact finite-population interpretation is explicitly justified.

The final thresholds must be selected from operating-characteristic evidence, not convenience.

## 8. Simulation execution plan

### 8.1 Monte Carlo repetitions

Use at least:

```text
10,000 simulated datasets per primary calibration cell
```

A smaller 1,000-dataset engineering run may validate code but cannot support final tail-probability claims near 0.025 or 0.05 without reporting Monte Carlo error.

For an estimated coverage `p_hat`, report Monte Carlo standard error:

```text
MCSE = sqrt(p_hat * (1 - p_hat) / N_sim)
```

At `p_hat = 0.95` and `N_sim = 10,000`, MCSE is approximately 0.0022.

### 8.2 Deterministic reproducibility

Record:

- simulation schema version;
- repository commit;
- Python version;
- master seed;
- per-cell derived seed;
- number of Monte Carlo datasets;
- bootstrap draw count;
- scenario parameters;
- software and dependency versions;
- elapsed time and failed-cell count.

Every summary table must regenerate from raw or compressed scenario-level counts.

### 8.3 Computational staging

1. unit-test generators against analytic means;
2. engineering run on a small scenario subset;
3. verify sharp-null Type I behavior;
4. verify replicate-duplication invariance;
5. execute the primary grid;
6. execute targeted floor, ceiling, sparse-effect, and missingness stress tests;
7. freeze analysis code before interpreting method rankings.

## 9. Adversarial regression fixtures

The implementation must include deterministic fixtures proving:

1. duplicating every call-level replicate does not narrow family-level uncertainty;
2. duplicating every variant within a family does not increase the independent family count;
3. adding genuinely independent task families can narrow uncertainty;
4. a mean-zero mixture of large positive and negative effects is not mislabeled context-invariant;
5. a floor model can yield a null observed contrast despite a nonzero latent logit effect;
6. a context-dependent refusal mechanism can preserve answered-case accuracy while changing overall correctness;
7. a single influential family can drive a detected mean effect;
8. statistical distinguishability and practical mean equivalence can both be true;
9. a point estimate inside the margin without interval containment is not formal equivalence;
10. all-zero observed contrasts produce an explicitly qualified degenerate interval, not an unqualified proof of invariance.

## 10. Decision criteria for retaining the current percentile bootstrap

The percentile family bootstrap may remain the default descriptive interval for a specified regime only if simulation shows, across the relevant scenario envelope:

- 95% interval coverage within a prespecified tolerance, provisionally `[0.925, 0.975]`;
- 90% interval coverage within `[0.875, 0.925]`;
- Type I error at or below 0.06 for the tested difference rule;
- false-equivalence probability at or below 0.06 at the margin boundary;
- no material anti-conservative degradation under the expected discrete and zero-inflated distributions;
- stable behavior under replicate and variant duplication invariance tests;
- explicit warnings or indeterminate labels in regimes that fail calibration.

These tolerances are provisional engineering criteria, not universal statistical laws. The final report must show sensitivity to the tolerance choice.

If the current method fails, the response is not to select the method with the narrowest intervals. Select the method or fail-closed rule with the best calibrated error control and acceptable information requirements.

## 11. Permitted conclusions from the calibration

A successful calibration may support statements such as:

> Under the simulated family counts, bounded-outcome distributions, heterogeneity, and missingness patterns specified here, the selected interval procedure achieved approximately nominal empirical coverage and controlled the prespecified difference or mean-equivalence error rate.

It may not support:

- validity outside the simulated scenario envelope;
- causal identification of why a model changed;
- proof that a null QEIB contrast reflects stochastic noise;
- proof of model invariance;
- safety or deployment guarantees;
- evaluation awareness, deception, intent, self-preservation, consciousness, sentience, or welfare.

## 12. Primary sources and methodological anchors

- MacKinnon, Nielsen, and Webb, *Fast and Reliable Jackknife and Bootstrap Methods for Cluster-Robust Inference* (2023). Their simulation results emphasize that ordinary cluster-robust methods can be unreliable with few clusters and motivate explicit finite-sample calibration rather than assuming asymptotics.
- Neuhäuser and Ruxton, *The Statistical Analysis of Small Data Sets* (2024), Chapter 2. Distinguishes permutation/randomization models from population-bootstrap models and discusses ties and small-data inference.
- Liu et al., *Unconditional Exact Tests for Equivalence or Noninferiority for Paired Binary Endpoints* (2001). Shows that small-sample paired-binary equivalence procedures can be wider and more conservative than asymptotic methods, providing a restricted reference case for QEIB exact-match tasks.
- Klar et al., *An Exact Bootstrap Confidence Interval for kappa in Small Samples* (2002). Demonstrates that interval behavior in small discrete samples is parameter- and distribution-specific and may require exact enumeration or tailored methods.
- DiCiccio, Martin, and Young, *Fast and Accurate Approximate Double Bootstrap Confidence Intervals* (1992). Provides a methodological precedent for seeking improved small-sample coverage rather than relying on a single basic percentile interval.

## 13. Highest-leverage implementation sequence

1. Implement a standard-library simulation harness that imports the actual QEIB aggregation and interval functions rather than duplicating them.
2. Add the ten adversarial regression fixtures.
3. Run a compact engineering grid for `J ∈ {6, 12, 20}`, baseline accuracy `{0.05, 0.50, 0.95}`, and sharp-null / constant-effect / mean-zero heterogeneous scenarios.
4. Use those results to decide whether the full calibration should prioritize percentile, BCa, studentized, exact sign-flip, or fail-closed information rules.
5. Only after calibration, freeze inferential thresholds for the private paraphrase study.
