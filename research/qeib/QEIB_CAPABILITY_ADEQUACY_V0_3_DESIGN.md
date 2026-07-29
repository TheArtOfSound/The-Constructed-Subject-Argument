# QEIB Capability-Adequacy Policy v0.3: Prospective Balance and Hierarchical-Heterogeneity Design

**Status:** prospective design specification; no v0.3 policy selected  
**Predecessor:** v0.2 comparison returned `select_none`  
**Companion grid:** `capability_adequacy_v0.3_candidate_grid.json`

## Purpose

The v0.2 comparison rejected every candidate under the frozen operating-risk contract. It also exposed a structural defect: minimum per-domain family counts allowed severe allocation imbalance to pass, while maximum raw domain deviation created an unstable tradeoff between false adequacy and false inadequacy.

Version 0.3 therefore tests three changes without weakening the existing risk tolerances:

1. family counts above 96;
2. explicit domain-allocation balance constraints;
3. a hierarchical domain-heterogeneity diagnostic that accounts for finite per-domain sample sizes.

The target construct remains narrow: **neutral-context measurement headroom, structural coverage, and operational adequacy for estimating a prespecified family-level context contrast**. This is not a general capability test, psychometric validation, evaluation-awareness detector, deception test, safety test, welfare measure, or consciousness test.

## Frozen operating-risk contract

A candidate qualifies only if all conditions hold:

- false adequacy is at most 5% in every clearly inadequate regime;
- false inadequacy is at most 10% in every clearly adequate interior regime;
- structural-invalidity pass rate is exactly 0%;
- deterministic regeneration reproduces the candidate record;
- no candidate-specific exception is added after results are observed.

If no candidate qualifies, the mandatory selection is `select_none`.

Boundary and indifference regimes remain diagnostic and are excluded from candidate acceptance. Their outcomes must still be preserved.

## Non-retrospective boundary

Candidate selection must not use:

- observed context deltas or context-effect intervals;
- significance, equivalence, awareness, or deception labels;
- private-holdout outcomes;
- model identity selected because it produces a desired result;
- post hoc task deletion after context results are inspected;
- leaderboard performance on public development tasks.

Only neutral-context adequacy data, frozen synthetic regimes, and later external methodological review may influence policy selection.

## Candidate family counts

The frozen comparison uses 144, 192, and 288 eligible task families across six domains.

These values are engineering candidates, not claims that any count is intrinsically sufficient. They test whether additional information can reduce the v0.2 conflict between permissive point rules and over-conservative Wilson rules.

## Explicit allocation balance

Minimum per-domain counts are necessary but insufficient. Version 0.3 adds three simultaneous allocation checks.

For domain shares \(p_d=n_d/N\):

1. **minimum share:** every domain must exceed a candidate lower bound;
2. **maximum share:** no domain may exceed a candidate upper bound;
3. **effective domain count:**
   \[
   D_{\mathrm{eff}} = \frac{1}{\sum_d p_d^2}.
   \]

The inverse-Herfindahl effective count equals six under perfectly balanced allocation and approaches one as allocation concentrates in one domain.

Two prospective balance candidates are tested:

| Candidate | Minimum domain share | Maximum domain share | Minimum effective domains |
|---|---:|---:|---:|
| strict | 0.12 | 0.22 | 5.5 |
| moderate | 0.10 | 0.25 | 5.0 |

A structural-balance failure blocks inferential eligibility. It does not imply anything about model behavior; it means the benchmark allocation cannot support the planned pooled interpretation.

## Hierarchical heterogeneity diagnostic

Raw maximum domain deviation ignores uncertainty: a small domain can look extreme by chance, while a genuinely heterogeneous large domain can be hidden by pooled averaging.

Version 0.3 replaces that primary safeguard with a beta-binomial posterior-predictive diagnostic. The simulator must:

1. model domain-level correct counts conditional on a shared population distribution;
2. estimate between-domain dispersion without using context outcomes;
3. calculate the posterior-predictive probability that one or more domains are as extreme as observed;
4. fail inferential eligibility when the prespecified tail-probability criterion is crossed.

Two candidates are frozen:

- `beta_binomial_ppc_90`: tail threshold 0.10;
- `beta_binomial_ppc_95`: tail threshold 0.05.

This is a diagnostic for domain inconsistency under the operating model. It does not establish a discrete latent class, measurement invariance, or a causal mechanism. Prior choice and numerical implementation must be documented in the comparison artifact, and sensitivity to at least one weakly informative alternative prior must be reported. Candidate qualification must be based only on the frozen primary prior.

## Interval strategy

The v0.2 one-sided 95% Wilson rule sharply reduced false adequacy but produced extreme false inadequacy. Version 0.3 separates accuracy headroom from operational-failure control:

- neutral accuracy candidates use either two-sided 90% Wilson or two-sided 90% Agresti-Coull intervals;
- transport, format, and coverage criteria retain one-sided 95% Wilson bounds;
- count and control failures remain deterministic;
- two-stage variants may pass smoke eligibility while failing inferential eligibility.

The less conservative accuracy intervals are hypotheses to test, not adopted policy. They must still satisfy the unchanged 5% false-adequacy ceiling.

## Prespecified regimes

### Clearly adequate interior

At minimum:

- neutral accuracy 0.45, 0.55, and 0.70;
- transport failure 0.00 or 0.02;
- format failure 0.00 or 0.04;
- balanced and moderately unbalanced-but-valid allocations;
- low and moderate between-domain heterogeneity;
- valid positive and negative controls.

### Clearly inadequate exterior

At minimum:

- floor accuracy 0.05, 0.10, and 0.15;
- ceiling accuracy 0.95 and 0.98;
- transport failure 0.08, 0.10, and 0.15;
- format failure 0.15 and 0.20;
- expected scorable coverage below 0.88;
- one-domain and two-domain concentration profiles;
- a missing-domain profile;
- domain floor/ceiling mixtures with pooled midrange accuracy;
- high between-domain dispersion;
- failed positive or negative controls.

### Boundary diagnostics

The prior indifference values are retained:

- accuracy 0.18-0.22 and 0.88-0.92;
- transport 0.04-0.06;
- format 0.08-0.12;
- scorable coverage 0.88-0.92.

Boundary outcomes cannot approve or reject a candidate.

## Structural oracle correction

Structural invalidity is deterministic in v0.3. A sample that violates the frozen allocation rule, domain count, minimum family count, or controls is oracle-invalid regardless of stochastic correctness outcomes.

This prevents the v0.2 error mode where a severely imbalanced allocation was treated as a probabilistic adequacy question. The simulator must report structural rejection separately from measurement-headroom rejection.

## Candidate generation and selection

The machine-readable grid defines a 48-candidate cross-product:

- 3 family counts;
- 2 rule families;
- 2 accuracy interval methods;
- 2 allocation-balance rules;
- 2 hierarchical heterogeneity rules.

No candidate may be removed after simulation begins.

If multiple candidates qualify, select in this order:

1. smallest family count;
2. lowest worst-case false adequacy;
3. lowest worst-case false inadequacy;
4. lowest structural and computational complexity.

## Required outputs

The comparison must preserve:

- every candidate, including failures;
- every regime-level pass rate;
- worst-case false adequacy and false inadequacy;
- structural rejection and inferential rejection as separate fields;
- prior-sensitivity diagnostics;
- deterministic seed, policy digest, code version, and artifact digest;
- the exact `select_none` result when no candidate qualifies.

## Findings, hypotheses, and uncertainty

### Findings inherited from v0.2

- No tested v0.2 candidate met the frozen operating-risk contract.
- Point rules remained too permissive.
- one-sided 95% Wilson headroom rules were excessively conservative.
- minimum per-domain counts did not prevent severe allocation imbalance.
- maximum raw domain deviation did not produce an acceptable risk tradeoff.

### Prospective hypotheses

- family counts above 96 may reduce sampling-driven misclassification;
- explicit share and effective-domain constraints may eliminate structural leakage;
- hierarchical shrinkage may distinguish chance domain variation from genuine domain inconsistency better than raw maximum deviation;
- separating accuracy and operational interval conservatism may reduce false inadequacy without violating the false-adequacy ceiling.

### Unresolved uncertainty

- synthetic regimes are not an empirical distribution of deployed-model behavior;
- beta-binomial assumptions may be wrong when task families are dependent or multimodal;
- effective-domain thresholds are engineering candidates without external validation;
- larger family counts may be operationally expensive or fail to solve model-specific correlation;
- interval and prior choices may alter candidate rankings.

## Falsification conditions

The v0.3 design fails if:

- no candidate satisfies all frozen risks;
- structural-invalid profiles pass at any nonzero rate;
- independent implementation changes candidate ranking materially;
- plausible dependence or prior sensitivity pushes false adequacy above 5%;
- hierarchical diagnostics merely repackage pooled accuracy and miss floor/ceiling mixtures;
- empirical family dependence invalidates the simulator sufficiently to make its risk estimates uninterpretable.

A failed design remains a valid result and must not trigger retrospective relaxation.

## Permitted conclusion after a future selected gate

A selected and passed v0.3 gate would permit only:

> Under the preregistered operating model, this run had sufficient neutral-context headroom, allocation balance, domain consistency, controls, and operational validity to estimate the prespecified family-level context contrast.

It would not establish context invariance, formal equivalence, evaluation awareness, sandbagging, deception, intent, safety, subjectivity, sentience, or consciousness.

## Single next action

Implement the deterministic v0.3 simulator directly from the frozen JSON grid, including structural-oracle separation and beta-binomial prior-sensitivity output, and select no policy unless every operating-risk condition passes.
