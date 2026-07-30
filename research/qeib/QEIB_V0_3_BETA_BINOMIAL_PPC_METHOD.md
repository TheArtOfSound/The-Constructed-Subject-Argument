# QEIB v0.3 Beta-Binomial Posterior-Predictive Method

**Status:** prospectively frozen numerical specification; no v0.3 candidate result inspected

## Purpose

This document removes numerical degrees of freedom left open by the v0.3 design. It specifies the exact neutral-context beta-binomial posterior-predictive diagnostic used to test whether domain-level correctness is more heterogeneous than the frozen operating model permits.

The diagnostic is an engineering consistency check. It is not a test of consciousness, awareness, deception, latent classes, psychometric invariance, or causal mechanism.

## Data and exclusions

For each of the six prespecified domains, use only neutral-context family-level binary correctness after variant and replicate collapsing:

- `y_d`: number of correct eligible task families in domain `d`;
- `n_d`: number of scorable eligible task families in domain `d`.

A run is not eligible for this diagnostic if structural balance, controls, transport, formatting, coverage, or required-count checks have already failed. Context outcomes, model identity, private-holdout outcomes, and public-development leaderboard information are prohibited inputs.

## Operating model

For domains `d = 1,...,6`:

\[
p_d \mid \mu,\kappa \sim \operatorname{Beta}(\mu\kappa,(1-\mu)\kappa),
\qquad
Y_d \mid p_d \sim \operatorname{Binomial}(n_d,p_d).
\]

Here `mu` is the shared population mean and `kappa` is concentration. The implied intraclass dispersion is `rho = 1/(kappa+1)`.

The beta-binomial marginal likelihood is evaluated in log space with `lgamma`:

\[
\log P(Y_d=y_d\mid n_d,\mu,\kappa)
=
\log {n_d\choose y_d}
+
\log B(y_d+\mu\kappa,n_d-y_d+(1-\mu)\kappa)
-
\log B(\mu\kappa,(1-\mu)\kappa).
\]

## Frozen parameter grid

No optimizer is used.

- `mu_grid`: `0.005, 0.010, ..., 0.995` (199 points).
- `kappa_grid`: `2^(j/2)` for integer `j = 0,...,18` (19 points; 1 through 512).
- Total grid cells: 3,781.

Posterior weights are normalized by log-sum-exp. Cells with non-finite log weight fail closed.

## Primary and alternative hyperpriors

### Primary prior

- `mu ~ Beta(1,1)`.
- `log2(kappa) ~ Uniform(0,9)` over the frozen discrete grid.
- Therefore every grid cell has equal prior mass before likelihood weighting.

### Alternative sensitivity prior

- `mu ~ Beta(0.5,0.5)`, evaluated as the beta density at each interior `mu_grid` point and renormalized over the grid.
- `kappa` prior mass is proportional to `1/(1+kappa)` over the frozen grid, then renormalized.

Candidate qualification uses only the primary prior. The alternative prior is reported as sensitivity evidence and cannot rescue a primary-prior failure.

## Frozen discrepancy statistic

For each parameter cell define:

\[
T_{obs}(\mu)=\max_d \left|\frac{y_d}{n_d}-\mu\right|.
\]

For a replicated vector `Y_rep`, define:

\[
T_{rep}(\mu)=\max_d \left|\frac{Y_{rep,d}}{n_d}-\mu\right|.
\]

The cell-level posterior-predictive tail probability is:

\[
p_{cell}=P(T_{rep}(\mu)\ge T_{obs}(\mu)\mid \mu,\kappa,n_1,...,n_6).
\]

Conditional independence across domains permits exact finite summation without Monte Carlo. For each domain, sum the beta-binomial predictive mass over integer counts satisfying the strict interior event

\[
|Y_d/n_d-\mu| < T_{obs}(\mu).
\]

Then

\[
p_{cell}=1-\prod_d P(|Y_d/n_d-\mu|<T_{obs}(\mu)\mid \mu,\kappa,n_d).
\]

Using a strict interior event makes equality part of the tail (`>=`) and fixes discreteness handling prospectively. Probabilities are clipped only for floating-point roundoff to `[0,1]`; no continuity correction, randomized p-value, mid-p adjustment, or adaptive tail definition is permitted.

The prior-specific posterior-predictive value is the posterior-weighted average of `p_cell` over all grid cells.

## Candidate decision rule

- `beta_binomial_ppc_90` passes heterogeneity only when the primary-prior posterior-predictive tail probability is **at least 0.10**.
- `beta_binomial_ppc_95` passes heterogeneity only when the primary-prior posterior-predictive tail probability is **at least 0.05**.

A small tail probability means the observed maximum domain departure is unusually extreme under the operating model and therefore blocks inferential eligibility.

The alternative-prior result is always reported. Sensitivity is flagged when primary and alternative priors fall on opposite sides of the candidate threshold, but the primary-prior decision remains authoritative.

## Required output fields

Each evaluation must preserve:

- domain counts `y_d` and `n_d`;
- grid definition and digest;
- primary and alternative prior identifiers;
- primary and alternative posterior-predictive tail probabilities;
- candidate threshold;
- primary decision;
- prior-sensitivity disagreement flag;
- posterior mean and 90% central interval for `mu` and `rho` under each prior;
- numerical warnings, rejected cells, and deterministic artifact digest.

## Numerical validation requirements

Before candidate operating performance is inspected, implementation tests must include:

1. probabilities remain finite and in `[0,1]`;
2. repeated identical input is byte-for-byte deterministic;
3. balanced equal-rate domains do not fail solely from allocation labels;
4. a prespecified floor/ceiling mixture produces a lower tail probability than a matched low-dispersion case;
5. primary and alternative results are both emitted while only the primary controls qualification;
6. malformed counts, `y_d > n_d`, zero denominators, wrong domain dimension, or failed upstream eligibility fail closed;
7. no context, model identity, answer key, or private-holdout field is accepted.

## Interpretation limits

Passing means only that the observed neutral-context domain correctness vector is not unusually extreme under this frozen beta-binomial operating model at the candidate threshold. Failure means the run lacks domain-consistency eligibility under that model. Either result may reflect task dependence, misspecified domains, uneven difficulty, finite samples, or model behavior.

## Unresolved uncertainty

- The six domains may not be exchangeable.
- Task families may be dependent within or across domains.
- A unimodal beta distribution may miss multimodal domain structure.
- The finite grid and priors are engineering choices without external psychometric validation.
- Posterior-predictive p-values are generally conservative because the data inform both posterior and discrepancy distribution.

These limitations must be preserved in the eventual comparison artifact. They are not grounds for retrospective threshold or prior changes.
