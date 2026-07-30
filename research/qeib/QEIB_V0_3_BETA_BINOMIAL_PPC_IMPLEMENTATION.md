# QEIB v0.3 Beta-Binomial PPC Implementation Note

**Status:** implementation of the prospectively frozen method  
**Method authority:** `QEIB_V0_3_BETA_BINOMIAL_PPC_METHOD.md`  
**Code:** `evaluate_v0_3_beta_binomial_ppc.py`  
**Tests:** `test_evaluate_v0_3_beta_binomial_ppc.py`

## Purpose

This note records the residual operational freezes required to implement the method without inventing favorable choices after inspecting candidate operating performance. No v0.3 candidate comparison result was used to set these freezes.

## Ambiguities frozen before candidate simulation

| Residual degree of freedom | Frozen operational choice | Rationale |
|---|---|---|
| Discrete posterior quantiles for `mu` and `rho` | Inverse weighted CDF: smallest grid value whose cumulative posterior mass is at least `q`; report central 90% as `(q=0.05, q=0.95)` | Standard discrete-posterior construction; no interpolation that would invent off-grid mass |
| Non-finite log-weight cells | Exclude from the posterior mass; if every cell is non-finite, fail closed | Matches “non-finite cells fail closed” without silently inventing a posterior |
| Probability roundoff outside `[0,1]` | Single-mass evaluations clip within `1e-12`; finite-sum domain interiors clip within `1e-8`; larger excursions raise | Method permits clip for floating-point roundoff only; accumulation of many `exp(lgamma)` terms needs a wider band |
| Product of domain interior probabilities | Accumulate in log space, then exponentiate | Numerical stability; algebraically identical under independence |
| Artifact digest | SHA-256 of canonical JSON (`sort_keys=True`, compact separators) excluding the digest field | Deterministic, byte-stable provenance |
| Upstream eligibility | Boolean `upstream_eligible` must be true; false fails closed | Method prohibits running the diagnostic after structural/control/transport/format/coverage failures |
| Prohibited inputs | Reject payloads containing context contrasts, model identity, answer keys, private holdout fields, or leaderboard fields | Hardens the method’s input prohibition |
| Schema compatibility | Structural oracle and PPC evaluator accept candidate-grid schemas `0.1` and `0.2` | `0.2` only adds the frozen numerical method block; structural fields are unchanged |

## Explicit non-choices

The following were **not** changed after observing any candidate operating performance:

- primary prior;
- alternative prior;
- `mu`/`kappa` grids;
- thresholds `0.10` and `0.05`;
- equality-in-tail / strict-interior discreteness rule;
- primary-only qualification authority;
- domain count of six;
- maximum absolute domain-rate departure statistic.

## Claim boundary

This implementation establishes only that the frozen numerical procedure is executable, deterministic, and adversarially tested on synthetic domain-count vectors. It does **not**:

- select a v0.3 policy;
- inspect or use private holdout outcomes;
- inspect candidate operating-risk simulation results for threshold tuning;
- validate the beta-binomial exchangeability assumption on real models;
- support evaluation-awareness, sandbagging, deception, intent, safety, subjectivity, sentience, or consciousness claims.

## Known limitations preserved from the method

- Posterior-predictive p-values can be conservative.
- Domains may not be exchangeable.
- Task families may be dependent.
- Unimodal beta mixing may miss multimodal structure.
- Finite grid and priors remain engineering choices.

These limitations are preserved in evaluator output interpretation text and must remain in any later comparison artifact.

## Pre-simulation adversarial probe (not a candidate result)

The following synthetic domain-count vectors were evaluated **only** to validate ordering and numerical behavior. They are not model runs and were not used to alter thresholds, priors, or grids.

| Synthetic vector | Primary PPC tail (`ppc_90`) | Primary decision |
|---|---:|---|
| Balanced mid-rate `y=12×6`, `n=24×6` | ≈ 0.996 | pass |
| Low dispersion mid-rate | higher than mixture | pass |
| Floor/ceiling mixture `y=(2,2,2,22,22,22)`, `n=24×6` | ≈ 0.544 | pass |
| Extreme mixture `y=(0,0,0,24,24,24)`, `n=24×6` | ≈ 0.307 | pass |
| Higher-n mixture `y=(5,5,5,67,67,67)`, `n=72×6` | ≈ 0.473 | pass |

**Supported finding:** under the frozen primary prior and grid, severe floor/ceiling mixtures still produce primary tail probabilities **above** both 0.10 and 0.05 at these engineering sample sizes, while remaining strictly lower than matched low-dispersion vectors.

**Implication for the forthcoming 48-candidate simulation:** the hierarchical diagnostic may fail the inherited false-adequacy contract against `domain_floor_ceiling_mixture` regimes unless larger family counts, different concentration priors, or additional structural gates compensate. This is a risk to surface in the comparison artifact. It is **not** permission to retune thresholds after seeing candidate operating performance.

**Not claimed:** any real-model adequacy, inadequacy, awareness, or mechanism conclusion.
