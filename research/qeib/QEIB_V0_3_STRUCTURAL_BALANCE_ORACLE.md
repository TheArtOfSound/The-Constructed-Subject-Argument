# QEIB v0.3 Structural-Balance Oracle

## Purpose

This artifact implements the deterministic structural-allocation component of the frozen QEIB capability-adequacy v0.3 design. It exists to prevent a benchmark with severely concentrated domain allocation from becoming inferentially eligible merely because observed outcomes happen to look favorable.

The oracle evaluates benchmark structure only. It does not inspect model responses, context contrasts, answer keys, private holdouts, or behavioral outcomes.

## Frozen criteria

For domain family counts \(n_d\), total families \(N\), and shares \(p_d=n_d/N\), the effective-domain count is

\[
D_{\mathrm{eff}} = \frac{1}{\sum_d p_d^2}.
\]

A structural candidate passes only when all three conditions hold:

1. every domain share is at least the candidate minimum;
2. every domain share is no greater than the candidate maximum;
3. the inverse-Herfindahl effective-domain count meets the candidate minimum.

The candidate thresholds are loaded directly from `capability_adequacy_v0.3_candidate_grid.json`; they are not duplicated as editable constants in the evaluator.

## Adversarial checks

The test suite freezes the following expected behavior:

- equal six-domain allocation passes both frozen candidates;
- 80% concentration in one domain fails;
- 80% concentration across two domains fails;
- any missing domain fails;
- a moderately unbalanced profile may pass the moderate candidate while failing the strict candidate;
- malformed, negative, zero-total, and wrong-dimension inputs fail closed;
- repeated evaluation of the same allocation is identical and outcome-independent.

## Interpretation boundary

### Supported

- The implementation deterministically classifies allocation structure under the two prospectively frozen v0.3 balance candidates.
- Structural rejection is independent of stochastic accuracy outcomes.
- The severe allocation profiles that leaked through v0.2 minimum-count rules are rejected by the new oracle in the adversarial tests.

### Hypotheses not yet tested

- Passing either balance candidate improves scientific interpretability of context contrasts.
- The strict or moderate thresholds are optimal.
- Effective-domain count is sufficient to capture all harmful allocation structures.

### Not supported

This oracle is not psychometric validation. It does not establish capability adequacy, measurement invariance, context invariance, evaluation awareness, deception, intent, safety, subjectivity, sentience, or consciousness.

## Next integration step

The deterministic v0.3 candidate simulator should call this oracle before any stochastic outcome evaluation. Structurally invalid regimes must retain a pass probability of exactly zero by construction, not approximately zero through Monte Carlo sampling.
