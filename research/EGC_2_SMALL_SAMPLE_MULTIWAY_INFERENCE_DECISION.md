# EGC 2.0 Small-Sample Multiway Inference Decision

**Status:** methods decision before further implementation  
**Scope:** crossed item-by-rater inference for the existing `complete_8x18_r8 × N1` calibration cell  
**Decision:** do not implement a one-way CR2/Satterthwaite correction as though it solved the two-way problem; prioritize a two-way cluster-jackknife estimator, with a multiway wild cluster bootstrap retained as the main competing method.

## 1. Problem this decision resolves

The current EGC calibration has rejected or weakened all implemented uncertainty procedures in the tested cell:

- item-only percentile bootstrap: useful power, anti-conservative coverage;
- rater-only percentile bootstrap: materially anti-conservative;
- multinomial pigeonhole percentile bootstrap: strongly conservative and low-powered;
- analytic Cameron–Gelbach–Miller two-way CRVE with `df=min(G)-1`: improved power, but 91% null coverage, 9% two-sided rejection, and occasional negative variance estimates.

The previous handoff reserved either CR2/Satterthwaite or a multiway wild cluster bootstrap as the next implementation. A prior-art review changes that choice.

## 2. Findings from prior art

### 2.1 CR2 is a one-way small-sample correction unless a valid multiway construction is derived

Bell–McCaffrey bias reduction and later CR2/Satterthwaite methods address downward-biased cluster-robust variance estimates with few independent clusters. Pustejovsky and Tipton generalize bias-reduced linearization to fixed-effects models and pair it with Satterthwaite degrees of freedom. Simulation literature reports good behavior in several one-way and nested settings.

That evidence does **not** directly validate the following shortcut for EGC:

1. calculate separate item and rater CR2 components;
2. subtract an item×rater component;
3. attach one Satterthwaite degree of freedom.

The Cameron–Gelbach–Miller multiway estimator is an inclusion–exclusion construction. CR2 adjustments depend on leverage matrices and a working covariance model. Applying separate one-way leverage corrections inside inclusion–exclusion does not automatically yield an unbiased or positive semidefinite multiway estimator, and there is no single obvious Satterthwaite denominator for the resulting signed sum.

**Finding:** implementing “CR2/Satterthwaite” without deriving and validating a specifically multiway version would create methodological theater: a familiar correction name attached to an estimator whose target properties are unknown.

### 2.2 Multiway wild cluster bootstrap is directly targeted, but few-cluster failure remains possible

MacKinnon, Nielsen, and Webb develop wild-bootstrap procedures for two-way clustering and show that bootstrap inference can outperform conventional t-reference inference, especially when one clustering dimension has few clusters. This is directly relevant to EGC's eight-rater dimension.

However, wild cluster bootstrap performance can deteriorate with very few effective clusters, unbalanced clusters, or few treated clusters. Therefore it must be calibrated on the exact EGC assignment and estimand. Its literature support makes it a legitimate candidate, not a validated default.

### 2.3 Two-way cluster jackknife is now the cleaner first implementation target

Recent work by MacKinnon, Nielsen, and Webb proposes two-way cluster-jackknife CRVEs specifically to improve finite-sample inference and address non-positive-definite multiway variance estimates. Their simulations report materially improved inference in two-way clustered linear models, and the method directly targets the pathologies observed in EGC:

- few clusters in one dimension;
- negative inclusion–exclusion variance estimates;
- anti-conservative conventional CRVE;
- need to retain cluster influence diagnostics.

The jackknife also has a practical scientific advantage for EGC: deleting whole raters and whole items exposes influence and fragility rather than hiding them behind a single adjusted variance.

**Decision:** implement a two-way cluster-jackknife candidate before attempting an improvised multiway CR2 correction.

## 3. Required first implementation

Create a standard-library implementation on the frozen `complete_8x18_r8 × N1` seeds with three estimators:

1. **CV1/CGM baseline** — the existing analytic two-way CRVE, retained unchanged;
2. **two-way delete-cluster jackknife candidate** — item and rater delete-cluster components combined using a documented multiway rule from the cited method;
3. **positive-semidefinite repair sensitivity** — the paper's recommended handling for an indefinite/negative variance estimate, reported separately rather than silently substituted.

The implementation must preserve:

- the exact existing contrast;
- the exact null and power data seeds;
- all undefined, negative, singular, or zero-variance cases;
- item-deletion and rater-deletion estimates;
- maximum deletion influence;
- sign changes and material changes under deletion;
- interval construction details and reference distribution.

## 4. Calibration contract

Use the same operating-characteristic targets as the prior calibrations:

### Null

- 1,000 generated datasets;
- two-sided Type-I error;
- positive- and negative-tail rejection separately;
- coverage;
- interval width;
- undefined/negative/singular rate;
- maximum item and rater deletion influence.

### Power

- 250 matched datasets at true contrasts `0.10`, `0.20`, and `0.30`;
- power, coverage, width, and sign-error rate;
- common random numbers across methods.

### Provisional retention rule

A method is not retained for pilot confirmatory inference unless:

- two-sided null rejection is between `0.035` and `0.065`;
- null coverage is at least `0.935`;
- no null cell exceeds `0.075` rejection;
- undefined or unrepaired variance cases are below `0.5%`;
- power at `0.20` is materially greater than the pigeonhole result (`0.252`) without reproducing the item-only method's anti-conservatism;
- conclusions are stable under a prespecified material deletion-influence threshold.

These are engineering gates for this calibration program, not universal statistical standards.

## 5. Multiway wild bootstrap remains the required rival

If the jackknife candidate fails, the next implementation should be a restricted multiway wild cluster bootstrap-t procedure based on empirical score contributions, not a raw percentile bootstrap. The implementation must specify:

- which clustering dimension receives which wild weights;
- whether weights are Rademacher, Webb six-point, or another distribution;
- whether the null is imposed;
- how the two clustering dimensions are combined;
- the studentizing statistic;
- handling of negative or undefined bootstrap variances;
- exact enumeration versus Monte Carlo draws for eight rater clusters.

Because eight raters permit only `2^8 = 256` Rademacher sign patterns in one dimension, exact or near-exact enumeration should be considered for the rater component. This may reduce Monte Carlo noise, but it does not remove the need for full calibration.

## 6. Claims discipline

### Supported findings

- Existing EGC two-way analytic inference is anti-conservative in the tested synthetic cell.
- A generic one-way CR2 success claim does not identify a valid two-way CR2 construction.
- Two-way wild bootstrap and two-way cluster jackknife methods are closer prior art for the actual crossed design.
- The two-way cluster jackknife is the highest-value next implementation because it directly addresses both finite-sample bias and indefinite variance failures while exposing cluster influence.

### Hypotheses

- A two-way cluster-jackknife interval may improve coverage without the severe power loss of the pigeonhole percentile interval.
- A multiway wild bootstrap-t may produce the best calibration-power tradeoff if the jackknife remains anti-conservative.

### Prohibited conclusions

- This decision does not validate any inferential method.
- It does not imply that CR2 is generally inferior; it says the repository lacks a justified multiway CR2 construction for this estimand.
- It does not establish that synthetic operating characteristics transfer to real EGC raters or items.

## 7. Primary sources

- Bell, R. M., & McCaffrey, D. F. (2002). Bias reduction in standard errors for linear regression with multi-stage samples. *Survey Methodology*, 28, 169–182.
- Pustejovsky, J. E., & Tipton, E. (2018). Small-sample methods for cluster-robust variance estimation and hypothesis testing in fixed effects models. *Journal of Business & Economic Statistics*, 36(4), 672–683.
- Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2011). Robust inference with multiway clustering. *Journal of Business & Economic Statistics*, 29(2), 238–249.
- MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D. Bootstrap and asymptotic inference with multiway clustering. Queen's Economics Department Working Paper 1386.
- MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D. (2024). Jackknife inference with two-way clustering. arXiv:2406.08880.
- MacKinnon, J. G., & Webb, M. D. (2018). The wild bootstrap for few treated clusters. *The Econometrics Journal*, 21(2), 114–135.

## 8. Highest-leverage next action

Implement the two-way cluster-jackknife candidate from the published method on the frozen N1 seeds, preserving deletion-level diagnostics and all indefinite-variance failures, then compare its null calibration and `0.20` power directly with the existing CGM, item-only, and pigeonhole results.
