# EGC 2.0 Rater Bias and Informative Dropout Simulation Specification

**Status:** Pre-implementation methods specification  
**Date:** 2026-07-25  
**Scope:** Synthetic calibration of the EGC 2.0 semantic-fidelity rating design  
**Non-claim:** This document does not validate the semantic-fidelity construct, the anchor bank, or any rater-count threshold.

## 1. Purpose

The current EGC 2.0 rater-pilot design guarantees balanced assignment, opaque presentation identifiers, repeated anchors, blind repeats, and a connected co-rating graph after enumerated one- and two-rater dropout. Those are necessary engineering properties. They do not establish that the estimated condition effect remains unbiased when raters differ in severity, respond differently across domains, drift during a session, learn recurring anchors, or drop out for reasons related to their latent severity, fatigue, or disagreement.

This simulation will quantify when graph connectedness remains scientifically useful and when it merely preserves a formally estimable but materially biased design.

## 2. Target estimands

For response `i`, rater `r`, and presentation position `t`, let latent semantic fidelity be `theta_i` and the observed ordinal score be `Y_irt`.

The simulation must recover or diagnose:

1. the mean evaluated-minus-private condition effect on latent fidelity;
2. the bias and interval coverage of the estimated condition effect;
3. single-rater and mean-rating reliability;
4. rater-severity variance;
5. response-by-rater interaction variance;
6. domain-specific differential severity;
7. fatigue and anchor-drift detection;
8. connectedness, effective overlap, and precision after dropout;
9. false confidence under severity-dependent or disagreement-dependent dropout.

## 3. Data-generating model

A continuous latent rating is generated before discretization:

```text
Z_irt = theta_i
        - severity_r
        + domain_bias_r,d(i)
        + fatigue_r * position_irt
        + anchor_learning_r * anchor_exposure_irt
        + response_rater_interaction_ir
        + epsilon_irt
```

The observed seven-category score is produced by applying ordered thresholds to `Z_irt`.

### 3.1 Response truth

```text
theta_i = participant_intercept_p(i)
          + condition_effect * evaluated_i
          + domain_effect_d(i)
          + prompt_effect_j(i)
          + response_noise_i
```

The simulation must include:

- zero, small, and moderate condition effects;
- homogeneous and participant-heterogeneous condition effects;
- domain-specific effects with opposite signs;
- no-effect settings where rater artifacts can create a false condition difference.

### 3.2 Rater severity

Rater severity is sampled from a mean-zero distribution with low, moderate, and high variance. Adversarial settings include one extreme rater and bimodal lenient/severe populations.

### 3.3 Domain-specific differential severity

Each rater may score autobiographical, conceptual, and position/reasoning responses differently. The simulation must include:

- no domain interaction;
- random rater-by-domain interactions;
- systematic severity against one domain;
- severity correlated with dropout.

### 3.4 Fatigue drift

Fatigue is modeled as position-dependent score drift and optionally increased residual variance. Required settings:

- no fatigue;
- linear leniency drift;
- linear severity drift;
- nonlinear late-session collapse;
- domain-dependent fatigue caused by clustered item order.

### 3.5 Anchor learning and anchor drift

Recurring anchors may improve calibration or create recognition and memorization. Simulate:

- stable calibration with no learning;
- gradual convergence toward anchor target scores;
- anchor-specific memorization without transfer to novel items;
- drift detectable on anchors but not on novel items;
- apparent anchor stability while novel-item severity drifts.

Anchor performance and novel-item performance must therefore be reported separately.

### 3.6 Response-by-rater interaction

`response_rater_interaction_ir` represents idiosyncratic disagreement not reducible to global severity. It must vary from negligible to dominant. This term is essential because a connected graph can still provide weak precision when response-by-rater interaction is large.

## 4. Dropout mechanisms

The simulator must distinguish:

### 4.1 MCAR dropout

Dropout probability is independent of all observed and latent rating variables.

### 4.2 MAR-like dropout

Dropout depends on observed session position, prior workload, domain mix, or previously observed anchor discrepancies.

### 4.3 Informative dropout

Dropout depends on latent or partially observed quantities:

- rater severity;
- fatigue slope;
- disagreement with anchor targets;
- low self-consistency;
- extreme use of score categories;
- condition-specific discomfort;
- response difficulty.

### 4.4 Adversarial dropout

Required stress tests:

1. the most severe rater drops out;
2. the most lenient rater drops out;
3. the two raters with highest anchor disagreement drop out;
4. raters disproportionately exposed to one condition drop out;
5. dropout occurs late, after anchor calibration but before difficult novel items;
6. dropout probability rises with absolute disagreement from the provisional consensus.

## 5. Simulation grid

The compact engineering grid should vary:

- raters: 6, 8, 10;
- ratings per response: 2, 3, 4, 5;
- responses: 60, 120, 360;
- severity SD: 0, 0.25, 0.50, 1.00 latent units;
- response-by-rater SD: 0.10, 0.35, 0.70;
- fatigue slope: 0, +/-0.005, +/-0.015 per position;
- dropout: none, 10%, 25%, and adversarial removal of one or two raters;
- condition effect: 0, 0.15, 0.30 latent units;
- condition-effect heterogeneity: none, moderate, sign-changing by domain.

A full grid may be staged after the compact run identifies high-risk regimes.

## 6. Analysis procedures to compare

At minimum compare:

1. naive mean-score difference ignoring rater identity;
2. rater-fixed-effect model;
3. crossed response-and-rater mixed model;
4. model with rater-by-domain interaction;
5. inverse-probability or sensitivity-weighted analysis when dropout probabilities are known by construction;
6. complete-case analysis;
7. fail-closed analysis that refuses a condition-effect conclusion under inadequate overlap or severe informative dropout.

The simulation should not assume that the most complex model is automatically correct. Convergence failures, singular fits, boundary estimates, and unstable standard errors must be recorded.

## 7. Primary performance measures

For each scenario report:

- condition-effect bias;
- root mean squared error;
- 95% interval coverage;
- false-positive rate when the true effect is zero;
- power under nonzero effects;
- reliability-estimate bias;
- dropout-induced change in rater-severity variance;
- minimum and median ratings per response;
- connected-component count;
- algebraic connectivity or another explicit overlap-strength diagnostic;
- anchor drift detection sensitivity and false-positive rate;
- discrepancy between anchor-based and novel-item drift estimates;
- rate of fail-closed `indeterminate` outcomes.

## 8. Graph connectedness is not sufficient

The co-rating graph is necessary for separating rater and response effects, but binary connectedness alone ignores edge multiplicity, bridge dependence, severity distribution, and informative missingness.

The simulator must therefore compare designs with the same connected/not-connected status but different:

- minimum degree;
- edge multiplicity;
- number of articulation points;
- spectral gap or algebraic connectivity;
- condition and domain overlap across raters;
- concentration of ratings in a small number of raters.

A connected graph with one weak bridge must not be described as robust merely because all nodes remain in one component.

## 9. Fail-closed decision rules to calibrate

Candidate rules, not yet validated:

- refuse condition-effect inference when the rater graph is disconnected;
- refuse when any condition is effectively scored by fewer than three raters;
- refuse when one rater's removal changes the condition-effect estimate by more than a preregistered tolerance;
- refuse when anchor drift and novel-item drift disagree materially;
- refuse when dropout is associated with severity or disagreement beyond a prespecified threshold;
- refuse when response-by-rater variance exceeds the response variance;
- refuse when interval coverage in the matching simulation regime falls below 90%.

The simulator must estimate operating characteristics before any threshold is adopted.

## 10. Falsification conditions

The current pilot architecture is weakened if simulation shows that plausible severity, fatigue, or dropout produces:

- false-positive condition effects above the preregistered ceiling;
- interval coverage materially below nominal;
- large bias despite graph connectedness;
- anchor stability that fails to detect novel-item drift;
- condition-effect sign reversal after one realistic rater dropout;
- acceptable reliability coefficients alongside biased condition effects.

If those failures persist across reasonable analysis models, the assignment design, rater count, session length, anchor strategy, or primary outcome must be redesigned before confirmatory recruitment.

## 11. Permitted conclusions

A calibrated simulation may support claims such as:

- under specified synthetic assumptions, a design and estimator maintained acceptable bias and coverage;
- a proposed dropout gate detected known informative-dropout failures at a measured sensitivity;
- four ratings per response improved precision relative to three under the tested variance regime.

## 12. Prohibited conclusions

The simulation cannot establish that:

- real raters follow the simulated distributions;
- the semantic-fidelity construct is valid;
- graph connectedness guarantees unbiased inference;
- anchors eliminate severity or fatigue;
- four raters are universally sufficient;
- missingness is ignorable in the real study.

## 13. Required implementation artifacts

The next implementation should produce:

- `research/egc2/simulate_rater_bias_dropout.py`;
- deterministic seeds and canonical JSON output;
- `research/egc2/test_simulate_rater_bias_dropout.py`;
- a compact calibration CSV or JSON artifact;
- a results review separating observed simulation behavior from recommendations;
- exact runtime, Python version, repository SHA, interrupted scenarios, and failed model fits.

## 14. Single highest-leverage next action

Implement the compact simulator against the existing assignment and session-order outputs, then run the zero-effect adversarial-dropout scenarios first. False-positive condition effects under a true null are the most damaging failure mode and should be measured before power or efficiency.