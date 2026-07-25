# EGC 2.0 Human-Rating Reliability and Calibration Protocol

**Status:** Methods specification for integration into the EGC 2.0 preregistration  
**Date:** 2026-07-25  
**Scope:** Blinded ratings of intended-meaning transmission and secondary writing qualities  
**Epistemic limit:** This protocol validates a human judgment process. It does not validate a consciousness measure, prove latent intended meaning, or eliminate construct ambiguity.

## 1. Purpose

EGC 2.0 treats blinded human-rated semantic fidelity between a participant's private intention map and produced response as the primary outcome. That outcome is not scientifically usable merely because three people assign scores. Reliability must be designed around the actual sources of variation:

- participant response;
- prompt domain and prompt form;
- condition;
- rater severity or leniency;
- rater-by-response interaction;
- scoring criterion;
- rating occasion and drift;
- presentation order;
- intention-map quality;
- residual error.

The protocol therefore separates four questions that are often collapsed:

1. **Agreement:** Did raters give the same numerical score?
2. **Consistency:** Did raters preserve the same ordering even if some were systematically harsher?
3. **Generalizability:** Would the response receive a similar score under another admissible rater, task form, or occasion?
4. **Decision precision:** Is the average rating precise enough for the planned condition-effect analysis?

No single coefficient answers all four.

## 2. Target constructs

### 2.1 Primary construct

**Semantic fidelity:** The degree to which the final response communicates the central meaning and essential concepts documented in the participant's private intention map, without requiring stylistic similarity.

The rater must distinguish:

- coverage of intended concepts;
- preservation of relationships among those concepts;
- absence of material distortion;
- communication of the intended central meaning.

The rater must not reward:

- length by itself;
- vocabulary sophistication by itself;
- agreement with the participant's position;
- emotional intensity by itself;
- grammatical polish unless it affects recoverability of intended meaning;
- similarity to another response by the same participant.

### 2.2 Secondary constructs

Secondary dimensions are scored separately:

- essential-concept coverage;
- completeness;
- clarity;
- richness and detail;
- distinct personal voice;
- depth of thought;
- emotional-tone preservation;
- apparent over-editing or unnaturalness.

These are not components of the primary semantic-fidelity score unless a later validation study supports a prespecified composite. Correlation among dimensions does not justify combining them.

## 3. Rating design

### 3.1 Minimum ratings

Every response receives at least **three independent ratings** for semantic fidelity. The primary analysis uses the mean of the admissible ratings only after reliability and information gates pass.

Three ratings are a minimum operational design, not a guarantee of adequate precision. A pilot decision study will determine whether four or more raters are required for specific outcomes.

### 3.2 Crossed incomplete-block assignment

A fully crossed design in which every rater scores every response is unnecessary and can create fatigue and drift. Use a connected incomplete-block design with these properties:

- each response is rated by at least three raters;
- each rater scores responses from every prompt domain and both conditions;
- no rater sees two responses from the same participant;
- no rater sees the participant identifier, condition, trial order, session, or other responses;
- every pair of raters shares a sufficient set of responses to connect the rater network;
- common anchor responses are distributed across all rater batches;
- condition is balanced within rater and batch;
- response order is independently randomized for each rater.

The no-same-participant rule prevents raters from inferring condition through within-person comparison. Condition balance prevents rater severity from becoming aliased with condition.

### 3.3 Anchor structure

Construct an anchor set before confirmatory scoring:

- at least 24 anchor response/intention-map pairs;
- representation from all prompt domains;
- representation across the full score range;
- examples containing omission, distortion, verbosity without fidelity, concise high fidelity, and ambiguous intention maps;
- expert reference distributions rather than one supposedly infallible gold score.

At least 10% of each rater's assignments should be anchors or blind repeats. Anchor exposure is interleaved, not grouped.

### 3.4 Blind repeats

At least 5% of scored pairs are repeated to the same rater under a new item identifier after a sufficient lag. These estimate intra-rater stability and detect inattentive or unstable scoring.

Repeated items are excluded from the substantive response-level mean and retained only for reliability diagnostics.

## 4. Rater recruitment and eligibility

Raters must:

- be fluent in the response language;
- pass a comprehension test on the rubric;
- complete calibration before production scoring;
- disclose professional writing-assessment experience, if any;
- have no access to participant identities or hypotheses;
- agree not to use external generative systems to produce ratings or explanations.

Expertise is recorded but not assumed to guarantee accuracy. Experienced raters may still differ systematically in severity or criterion use.

A rater is not excluded because their average severity differs from others. Systematic severity is modeled. Exclusion requires evidence of unusable scoring behavior under prespecified rules.

## 5. Training and calibration

### 5.1 Training sequence

1. Read the construct definitions and prohibited heuristics.
2. Score 12 annotated examples spanning the scale.
3. Review criterion-specific explanations, including why length and polish are not fidelity.
4. Score a second set of 12 unannotated calibration examples.
5. Receive discrepancy feedback.
6. Repeat calibration if the gate is not passed.

### 5.2 Initial calibration gate

A rater enters production scoring only if all conditions are met:

- no more than 2 of 12 calibration scores differ from the expert-panel median by more than two scale points;
- weighted agreement with the expert-panel distribution exceeds a threshold fixed after pilot calibration, not selected after seeing confirmatory data;
- the rater correctly identifies at least 80% of construct-violation vignettes;
- no systematic evidence shows that the rater substitutes length, polish, agreement, or emotional intensity for semantic fidelity.

The final numerical agreement threshold must be fixed from the pilot and recorded before confirmatory scoring. The protocol does not invent a universal cutoff.

### 5.3 Drift checks

Production scoring is divided into batches. After every 75 substantive ratings or seven days, whichever occurs first, the rater receives a drift set of six anchors.

Drift is flagged when any of the following occurs:

- mean anchor deviation changes by more than one scale point from calibration;
- direction of severity reverses materially;
- blind-repeat disagreement increases beyond the pilot-derived tolerance;
- criterion misuse appears in required short rationales;
- response time collapses below the pilot-derived plausible minimum for a sustained block.

Flagged raters pause production scoring and recalibrate. Their prior ratings are retained, marked, and examined in sensitivity analysis; they are not silently deleted.

## 6. Rating interface

Each screen contains:

- the private intention map;
- the produced response;
- the semantic-fidelity rubric;
- separate secondary-dimension rubrics;
- an optional uncertainty flag;
- a required reason code for scores 1, 2, 6, or 7;
- no condition label, participant metadata, timing data, or automated score.

The intention map and response are shown in consistent positions. The interface records:

- rater ID;
- item ID;
- randomized presentation order;
- score by dimension;
- rating duration;
- uncertainty flag;
- reason code;
- batch and timestamp;
- whether the item is an anchor or blind repeat in a protected field unavailable to the rater.

Free-text explanations are not used to alter confirmatory scores unless a prespecified adjudication rule is triggered.

## 7. Rubric architecture

### 7.1 Semantic-fidelity scale

Use a seven-point ordinal scale with behaviorally anchored categories:

- **1:** central meaning is absent or materially contradicted; essential concepts are largely missing.
- **2:** fragments of intended meaning appear, but the response substantially omits or distorts the intended message.
- **3:** partial transmission; the broad topic is recoverable, but major concepts or relationships are missing.
- **4:** substantial transmission with important omissions, ambiguity, or minor distortion.
- **5:** central meaning is clear and most essential concepts are preserved; remaining omissions do not materially alter the message.
- **6:** high-fidelity transmission with nearly complete concept coverage and preserved relationships.
- **7:** exceptionally complete and accurate transmission of the documented intention without material distortion.

The scale is ordinal. Treating it as approximately interval for mixed modeling is a pragmatic approximation that must be checked against ordinal models.

### 7.2 Intention-map adequacy

Raters separately flag whether the intention map is:

- adequate;
- sparse but interpretable;
- internally inconsistent;
- not interpretable.

This flag is not a score adjustment. It identifies cases where the reference target itself is weak. Primary analysis must report sensitivity with and without preregistered inadequate-map cases.

## 8. Reliability analysis

### 8.1 Intraclass correlation

Report both single-rater and average-rating reliability for the primary outcome:

- absolute-agreement ICC for a single admissible rater;
- absolute-agreement ICC for the planned mean of three raters;
- 95% confidence intervals for both.

The model must match the design. When raters are sampled from a broader admissible pool and responses are incompletely crossed, a mixed-effects or generalizability model is preferable to forcing a textbook fully crossed ANOVA ICC.

Consistency-only ICC is supplementary because systematic rater severity matters when raw score levels determine the outcome.

### 8.2 Generalizability theory

Fit a generalizability model that estimates, where design permits:

- response variance;
- rater variance;
- prompt-domain variance;
- rating-occasion or batch variance;
- response-by-rater interaction;
- response-by-domain interaction where repeated domain forms permit estimation;
- residual variance.

Conduct a decision study estimating reliability under candidate designs:

- 2, 3, 4, and 5 raters per response;
- one versus two rating occasions;
- alternate anchor frequencies;
- domain-specific versus pooled scoring.

The confirmatory rater count must be justified by the decision study rather than inherited from convention.

### 8.3 Many-facet model

As a secondary diagnostic, fit a many-facet ordinal model with facets for:

- response;
- rater severity;
- prompt or task form;
- criterion when analytic dimensions are modeled jointly;
- rating-scale category thresholds.

Use it to identify:

- rater severity and leniency;
- central tendency;
- restriction of range;
- inconsistent category use;
- differential rater severity by domain or condition-balanced item characteristics;
- disordered category thresholds.

Many-facet adjustment is not automatically the primary score. Report raw mean ratings and model-adjusted estimates separately. If substantive conclusions depend on adjustment, that dependence must be explicit.

### 8.4 Ordinal agreement

Report weighted pairwise agreement or an ordinal multi-rater coefficient as a descriptive supplement. Kappa-like statistics are not the primary reliability analysis because prevalence and marginal score distributions can materially affect them.

### 8.5 Intra-rater stability

For blind repeats, report:

- exact agreement;
- agreement within one scale point;
- weighted disagreement;
- direction and magnitude of drift;
- rater-specific repeat counts.

Do not pool repeat ratings as independent evidence about participant responses.

## 9. Reliability gates

Reliability is evaluated through uncertainty intervals and design requirements, not one universal label such as "good."

Before unblinding condition labels, the study must define:

- minimum acceptable lower confidence bound for the reliability of the three-rater mean;
- maximum tolerated response-by-rater interaction variance relative to response variance;
- maximum tolerated anchor drift;
- minimum connectedness of the rater-response graph;
- minimum number of complete ratings per response.

Provisional pilot targets may be used for planning, but confirmatory thresholds must be justified from the consequence of measurement error for the planned condition-effect estimate.

If the reliability gate fails:

1. do not unblind condition labels for confirmatory inference;
2. identify whether failure is driven by ambiguous rubric, sparse intention maps, rater severity, rater interaction, domain differences, or insufficient raters;
3. collect additional blind ratings if the preregistration permits it under a fixed rule;
4. otherwise report the primary outcome as insufficiently reliable and treat condition analyses as exploratory.

Additional ratings cannot be targeted only to responses whose preliminary condition effect appears interesting.

## 10. Rater exclusion and adjudication

### 10.1 Permitted exclusion reasons

A rater may be excluded only for prespecified evidence such as:

- failure to complete calibration after the allowed attempts;
- extensive missingness;
- impossible completion patterns;
- sustained anchor or blind-repeat failure after recalibration;
- documented rubric noncompliance;
- disclosure of condition or participant information;
- use of prohibited external assistance.

Severity or leniency alone is not grounds for exclusion.

### 10.2 Response-level adjudication

Adjudication is triggered only by rules fixed before condition unblinding, such as:

- rating range of four or more scale points;
- at least one `not interpretable` intention-map flag;
- contradictory reason codes;
- missing required rating.

An adjudicator who has not seen condition labels reviews the item. The original ratings remain preserved. Report both pre-adjudication and adjudicated results in sensitivity analysis.

## 11. Missingness and failures

Distinguish:

- rater did not submit;
- interface or transport failure;
- rater marked intention map not interpretable;
- rater marked response not scorable;
- rating excluded under a prespecified rater rule.

Do not treat missing ratings as neutral scores. Replacement ratings are assigned by the randomization system without revealing condition or preliminary scores.

If missingness differs by prompt domain, batch, rater, or any condition-correlated feature, report it and model its possible effect.

## 12. Automated-measure validation

Automated measures are validated against held-out human ratings only after the rating process passes its reliability gate.

Required procedure:

- split at the participant level;
- keep all responses from one participant in one partition;
- train or tune automated measures only on the development partition;
- freeze preprocessing and model specification;
- evaluate on a held-out partition;
- report prediction error and calibration, not only correlation;
- compare against simple baselines including word count and response duration;
- test domain and condition interactions;
- report performance separately for semantic fidelity and each secondary construct.

A model predicting the rater mean does not become a direct measure of intended meaning. It is a predictor of a calibrated human judgment process under the studied rubric and population.

## 13. Primary statistical integration

The confirmatory condition-effect model should propagate rating uncertainty rather than treating the rater mean as error-free.

Preferred approaches, in descending order of feasibility:

1. joint ordinal hierarchical model with response, condition, participant, prompt, and rater effects;
2. generalizability-theory variance components carried into the condition-effect standard error;
3. mixed model on averaged ratings with explicit reliability sensitivity analysis and rater-count weighting.

At minimum, report whether the condition-effect conclusion changes when:

- using raw means versus rater-adjusted estimates;
- excluding inadequate intention maps under the preregistered rule;
- excluding drift-flagged ratings;
- using ordinal versus approximately continuous outcome models;
- using two versus three versus four raters where available;
- leaving out each rater and each prompt domain.

## 14. Falsification and failure conditions

The human-rating approach is weakened when:

- response-by-rater interaction dominates response variance;
- reliability does not improve materially with additional raters;
- raters cannot separate semantic fidelity from length or polish;
- intention-map adequacy predicts most rating disagreement;
- domain-specific rater behavior reverses the condition effect;
- adjusted and raw estimates lead to opposing conclusions without a principled resolution;
- automated metrics predict superficial features but fail to predict held-out semantic-fidelity judgments.

The stronger claim that evaluative context changes transmission of intended meaning is not supported when the primary outcome lacks sufficient reliability or when effects disappear under rater, domain, rubric, or intention-map sensitivity analyses.

## 15. Permitted conclusions

If all gates pass, the study may conclude within its sampled population and tasks that:

- blinded raters could assess semantic fidelity with quantified precision;
- rater severity and other measured facets contributed specified amounts of variance;
- averaging the preregistered number of ratings achieved the reported reliability;
- evaluated and private conditions differed, did not differ detectably, or were equivalent within a prespecified outcome-specific margin.

## 16. Prohibited conclusions

The rating protocol cannot establish that:

- an intention map perfectly captures private intended meaning;
- a high score measures consciousness, authenticity, or phenomenology;
- rater agreement proves construct validity;
- low disagreement proves objective truth;
- three raters are universally sufficient;
- an automated predictor of ratings directly measures thought transmission;
- a nonsignificant condition effect proves invariance;
- a reliable score is necessarily valid.

## 17. Required preregistration fields

Before confirmatory scoring begins, freeze:

- rubric version and anchors;
- rater eligibility and training materials;
- calibration and drift gates;
- assignment algorithm and randomization seed policy;
- target ratings per response;
- anchor and repeat frequency;
- reliability models and coefficient forms;
- confidence levels;
- generalizability facets;
- adjudication and exclusion rules;
- inadequate-intention-map rule;
- missing-rating replacement rule;
- minimum reliability and information gates;
- automated-validation split and baselines;
- condition-effect integration and sensitivity analyses.

## 18. Evidence basis

This protocol follows established measurement principles:

- ICC selection must match the rater model and intended use; single-rater and average-rating reliability are different quantities.
- Generalizability theory is needed when multiple error facets—not only raters—must be separated.
- Writing assessment research repeatedly finds rater severity, halo, central tendency, restriction of range, and differential severity even after training.
- Many-facet models can place responses, raters, tasks, criteria, and category thresholds in one diagnostic framework, but model adjustment does not replace construct validation.

## 19. Highest-leverage implementation sequence

1. Build the semantic-fidelity rubric and anchor bank.
2. Run a 60-response pilot with at least eight candidate raters, each response receiving four ratings.
3. Estimate rater, response-by-rater, domain, and residual variance.
4. Run a decision study for two through five raters.
5. Fix the confirmatory rater count and reliability gate before recruitment.
6. Validate the assignment system, blindness, anchors, repeats, and drift alerts.
7. Begin confirmatory scoring only after the pilot documents that the construct can be rated with adequate precision.
