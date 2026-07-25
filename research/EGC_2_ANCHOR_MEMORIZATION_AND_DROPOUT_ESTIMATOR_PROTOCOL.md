# EGC 2.0 Anchor Memorization, Novel-Item Drift, and Dropout-Estimator Calibration Protocol

**Status:** Preregisterable simulation and pilot-analysis specification  
**Date:** 2026-07-25  
**Scope:** Human semantic-fidelity rating process for EGC 2.0  
**Non-claim:** This protocol does not establish that anchors are valid, that dropout is ignorable, that any proposed estimator is unbiased in real data, or that semantic fidelity has been psychometrically validated.

## 1. Decision problem

The current EGC rater design uses recurring anchor packets to monitor scoring consistency. That creates a serious identification problem:

> Stable performance on repeated anchors can arise because a rater continues to apply the rubric consistently, or because the rater recognizes and memorizes the expected treatment of those specific anchors while drifting on novel responses.

Those mechanisms are observationally similar if the study monitors only recurring-anchor scores.

A second identification problem arises when ratings are missing because raters leave, skip items, slow down, or are removed:

> Complete-case, rater-adjusted, and inverse-probability analyses identify different estimands under different assumptions. None is automatically a correction for informative dropout.

The immediate objective is therefore not to choose a preferred estimator. It is to construct falsifiable synthetic and pilot-data tests that determine when each procedure fails and when the design must return `indeterminate`.

## 2. Constructs

### 2.1 Generalized rubric application

The target scoring capability is the ability to apply the semantic-fidelity rubric to previously unseen response–intention-map pairs.

### 2.2 Anchor-specific learning

Improvement caused by learning the correct application of the rubric from anchor feedback, where that improvement transfers to novel items with relevantly similar scoring demands.

### 2.3 Anchor memorization

Anchor-specific accuracy that does not transfer to novel items and depends on item recognition, repeated exposure, remembered rationale, or remembered expected score.

### 2.4 Novel-item drift

A time-dependent change in severity, discrimination, category use, or rubric application on unfamiliar items.

### 2.5 Dropout mechanism

The conditional probability that a scheduled rating remains observed, given measured history and possibly unmeasured current or future scoring behavior.

These constructs must remain separate. “Anchor accuracy” is not a validated proxy for generalized rubric application until transfer to unseen material is demonstrated.

## 3. Evidence from prior measurement work

Rater severity can change over time, and models that assume constant severity can be misspecified. Time-varying many-facet Rasch extensions have been developed specifically because temporal drift is empirically plausible (Jin & Wang, 2023, *Behavior Research Methods*, doi:10.3758/s13428-022-01997-z).

Operational calibration commonly uses benchmark or anchor performances to compare raters with expert judgments. That supports anchor-based monitoring as an engineering tool, but it does not prove transfer to unseen responses (Engelhard, 1996, *Journal of Educational Measurement*, doi:10.1111/j.1745-3984.1996.tb00479.x).

Rater development can be nonlinear over repeated training rounds, affecting agreement, consistency, and severity differently. Therefore, a single linear learning or fatigue coefficient is not an adequate default model (Yan & Chuang, 2023, *Language Testing*, doi:10.1177/02655322221074913).

Frequent immediate feedback can improve rater accuracy, which means recurring anchors may themselves alter the scoring process rather than merely measure it (Attali, 2020, ETS Research Report RR-20-09, doi:10.1002/ets2.12291).

For missing outcomes under missing at random, inverse-probability weighting requires a correctly specified observation model, while doubly robust procedures require at least one of the observation or outcome models to be correctly specified. Double robustness is not protection against both models being wrong, extreme weights, or missingness not at random (Bang & Robins, 2005, *Biometrics*, doi:10.1111/j.1541-0420.2005.00377.x; Tsiatis, Davidian, & Cao, 2011, *Biometrics*, doi:10.1111/j.1541-0420.2010.01476.x).

## 4. Experimental item classes

Each simulation and eventual rater pilot must distinguish at least four item classes.

### 4.1 Recurring anchors

Exact response–map packets repeated across sessions. Their purpose is to detect item-specific consistency and gross drift.

### 4.2 Surface-variant anchors

Packets preserving the same scoring principle while changing names, setting, wording, and lexical overlap. These test near-transfer rather than exact-item memory.

### 4.3 Structural-transfer probes

Novel packets requiring the same underlying rubric judgment but with different content and presentation. Examples:

- reversed causal relation despite high lexical overlap;
- polished but meaning-distorting response;
- short but fully faithful response;
- uncertainty removed from an otherwise accurate paraphrase;
- tone mismatch that is material in one packet and immaterial in another.

### 4.4 Fully novel production-like items

Previously unseen packets sampled from the target prompt domains. These are the primary evidence for generalized scoring behavior.

The rater-facing interface must not label these classes.

## 5. Anchor-recognition manipulation

To separate generalized learning from memorization, the simulation must include a latent recognition state `R_rit` for rater `r`, item `i`, and occasion `t`.

Recognition probability may depend on:

- exact prior exposure count;
- surface similarity;
- time since last exposure;
- feedback received;
- distinctive content;
- rater memory sensitivity.

When recognition occurs, the observed rating may receive an anchor-specific correction toward the stored expected score. That correction must not automatically apply to structural-transfer or novel items.

A minimal generative form is:

```text
latent_rating_rit = true_fidelity_i
                  + severity_rt
                  + domain_bias_rd
                  + fatigue_rt
                  + response_rater_interaction_ri
                  + transfer_learning_rt * transfer_similarity_i
                  + memorization_r * R_rit * anchor_score_error_i
                  + residual_rit
```

The final observed response is obtained through fixed or rater-specific ordinal thresholds.

The simulator must expose every parameter and preserve its value in output artifacts.

## 6. Drift scenarios

The compact grid must include:

1. **No learning, no drift.** Negative control.
2. **Generalized learning.** Anchor and novel accuracy improve together.
3. **Pure memorization.** Exact-anchor accuracy improves; surface variants and novel items do not.
4. **Memorization plus novel-item severity drift.** Anchor scores remain stable while unseen-item scores shift.
5. **Feedback-induced category compression.** Anchors improve while novel scores move toward the center.
6. **Domain-specific drift.** One prompt domain changes while recurring anchors from other domains remain stable.
7. **Fatigue with anchor recovery.** Novel accuracy degrades late in session, but familiar anchors remain accurate.
8. **Recognition decay.** Memorization weakens as spacing increases.
9. **Adversarial anchor overfitting.** Raters optimize recurring anchor accuracy after corrective feedback while applying a construct-irrelevant shortcut to novel items.

## 7. Dropout mechanisms

The simulation must distinguish:

### 7.1 MCAR engineering control

Observation probability is independent of outcomes, latent ratings, severity, disagreement, condition, and item type.

### 7.2 Measured-history MAR

Observation depends only on variables available before the rating, such as:

- rater identity;
- session position;
- prior workload;
- prior observed disagreement;
- previous anchor accuracy;
- prompt domain;
- assigned condition composition.

### 7.3 Current-outcome-dependent missingness

Observation depends on the unrecorded current rating, confidence, difficulty, or disagreement. Standard MAR-based weighting is not identified unless an adequate proxy or sensitivity model is introduced.

### 7.4 Latent-trait-dependent dropout

Observation depends on unobserved rater severity drift, fatigue, or rubric misunderstanding.

### 7.5 Intervention-induced dropout

Calibration feedback or removal rules affect continued participation. The observation process is then partly caused by the quality-control intervention itself.

The simulator must label 7.3–7.5 as nonignorable regimes rather than pretending that known simulated probabilities make the corresponding mechanism empirically observable in a real study.

## 8. Estimators to compare

### 8.1 Complete-case paired estimator

Uses only observed ratings. It is an engineering baseline, not a default causal estimator.

Required outputs:

- condition-effect estimate;
- participant-cluster interval;
- retained rater and response counts;
- condition-specific missingness;
- item-class-specific missingness.

### 8.2 Rater fixed-effects estimator

Adjusts for constant rater severity using indicator terms or within-rater contrasts.

It does not by itself remove:

- time-varying severity;
- rater-by-condition interaction;
- domain-specific bias;
- informative missingness;
- recognition-dependent anchor behavior.

### 8.3 Oracle inverse-probability weighted estimator

Uses the true simulated observation probabilities. This is a diagnostic upper bound on what correctly specified MAR weighting can achieve in the synthetic environment.

Required safeguards:

- stabilized weights;
- distribution and effective sample size reporting;
- maximum-weight reporting;
- prespecified trimming sensitivity analyses;
- no silent normalization changes.

### 8.4 Estimated-probability weighted estimator

Fits the observation model using only variables that would actually be available in the pilot before each rating.

At minimum compare:

- correctly specified model;
- omitted severity-history predictor;
- omitted disagreement-history predictor;
- incorrect linearity;
- incorrect pooling across prompt domains.

### 8.5 Outcome-regression estimator

Predicts missing ratings using measured rater, participant, domain, session, assignment, and prior-rating variables.

### 8.6 Doubly robust estimator

Combines an observation model with an outcome model. It may be labeled doubly robust only under the standard restricted meaning: consistency when one of two specified nuisance models is correct under the assumed missing-at-random identification conditions.

It must not be described as robust to:

- both models being misspecified;
- positivity violations;
- unmeasured current-outcome-dependent dropout;
- anchor recognition omitted from both models;
- extreme weights;
- incorrect dependence or uncertainty structure.

### 8.7 Sensitivity-analysis estimator

For nonignorable dropout, vary a departure parameter linking missingness to the unobserved rating or latent severity drift. Report the tipping point at which the condition-effect conclusion changes.

A sensitivity analysis does not identify the missing-data mechanism; it exposes dependence on untestable assumptions.

## 9. Primary operating characteristics

Under a true zero condition effect, report:

- false-positive rate;
- mean bias;
- root mean squared error;
- 95% interval coverage;
- average interval width;
- indeterminate rate;
- condition-specific and item-class-specific missingness;
- effective sample size for weighted estimators;
- frequency of extreme or trimmed weights;
- sign disagreement among estimators.

Under nonzero effects, additionally report:

- power;
- sign error rate;
- magnitude error;
- probability of practical-equivalence misclassification.

For drift detection, report:

- sensitivity and specificity for generalized drift;
- sensitivity and specificity for pure anchor memorization;
- false reassurance rate: recurring anchors appear stable while novel-item drift exceeds the preregistered material threshold;
- detection delay;
- domain-specific false-negative rate.

The false reassurance rate is a primary outcome, not a secondary diagnostic.

## 10. Required contrasts

The analysis must estimate separately:

1. exact recurring-anchor error over time;
2. surface-variant error over time;
3. structural-transfer error over time;
4. fully novel error over time;
5. anchor-minus-novel divergence;
6. transfer-gradient slope as similarity decreases;
7. condition-effect estimates within each item class;
8. dropout probability within each item class and condition.

A stable recurring-anchor trajectory with worsening novel-item performance is evidence against using recurring anchors alone as a validity gate.

## 11. Calibration grid

The compact implementation grid should begin with:

- 30 participants;
- 8 raters;
- 4 planned ratings per response;
- 3 prompt domains;
- 4 item classes;
- 60–120 ratings per rater;
- rater severity SD: `{0.0, 0.4, 0.8}`;
- generalized drift per 10 ratings: `{0.0, 0.15}`;
- memorization gain: `{0.0, 0.5, 1.0}`;
- recognition probability after repetition: `{0.0, 0.5, 0.9}`;
- dropout regime: `{MCAR, measured-history MAR, current-outcome MNAR, latent-drift MNAR}`;
- true condition effect: `{0.0, 0.3}`;
- at least 1,000 trials for the high-risk subset after engineering validation.

The complete Cartesian grid may be too large. The implementation must declare any fractional-factorial or staged selection rule before examining outcomes.

## 12. Fail-closed rules

A confirmatory condition-effect analysis must return `indeterminate_due_to_rater_process` when any of the following occurs:

1. anchor-minus-novel divergence exceeds its preregistered threshold;
2. novel-item drift is material while recurring anchors remain stable;
3. dropout differs materially by condition, item class, domain, or prior disagreement;
4. observation-model positivity is weak or effective sample size collapses;
5. complete-case and adjusted estimators differ in sign or by more than a preregistered magnitude;
6. sensitivity analysis crosses the decision threshold under plausible departure values;
7. one rater or one domain determines the conclusion;
8. the anchor-recognition model cannot distinguish transfer from memorization with acceptable operating characteristics.

These rules block interpretation but do not erase raw ratings or estimates.

## 13. Falsification conditions

The present anchor strategy is weakened if:

- recurring anchors have high apparent accuracy but poor correlation with structural-transfer and novel-item accuracy;
- memorization scenarios routinely pass the planned anchor quality gate;
- anchor feedback improves exact anchors while increasing construct-irrelevant shortcuts on novel items;
- false reassurance remains high despite spacing and surface variants;
- no feasible anchor mixture distinguishes generalized learning from memorization;
- dropout-correction procedures remain anti-conservative under plausible measured-history scenarios;
- the rater count or overlap required for acceptable calibration is operationally infeasible.

If these occur, EGC should reduce the inferential role of recurring anchors, increase unseen transfer probes, redesign feedback, or abandon the current human-rating architecture as the confirmatory primary outcome.

## 14. Permitted conclusions

With successful calibration, the study may conclude narrowly that:

- the selected monitoring design distinguished specified memorization and drift regimes at measured error rates;
- a particular estimator controlled false positives under specified simulated missingness assumptions;
- results were insensitive or sensitive to a declared range of nonignorable-dropout departures;
- recurring anchors alone were or were not adequate for the tested monitoring purpose.

## 15. Prohibited conclusions

The protocol cannot establish that:

- real raters follow the simulated parameter distributions;
- dropout is missing at random;
- doubly robust estimation solves nonignorable missingness;
- repeated-anchor accuracy proves generalized rubric competence;
- reliable ratings prove semantic-fidelity construct validity;
- semantic-fidelity scores reveal a psychological type or internal subjective state.

## 16. Implementation contract

The future implementation should add:

- `research/egc2/simulate_anchor_memory_dropout.py`;
- deterministic tests for pure learning, pure memorization, and false reassurance;
- estimator modules with shared participant-cluster resampling;
- a compact CSV plus full JSON manifest and digest;
- exact Python version, repository SHA, command, seed, runtime, and interrupted-cell reporting;
- a methods review written only after the machine-readable output exists.

The simulator should reuse the current assignment generator and session scheduler where compatible, but must not modify those validated files merely for convenience.

## 17. Highest-leverage next action

Implement the smallest falsification-first simulator containing only three regimes—generalized learning, pure memorization, and memorization plus novel-item drift—and measure the recurring-anchor false reassurance rate before adding inverse-probability or doubly robust estimators. If the monitoring signal cannot distinguish those regimes, estimator sophistication will not repair the construct failure.
