# EGC 2.0 — Condition-Dependent Intention-Map Inadequacy Sensitivity Protocol

**Status:** Prospective analysis rule; no participant or reviewer data analyzed  
**Date:** 2026-07-27  
**Scope:** Semantic-fidelity outcomes suppressed because the reference intention map is judged inadequate

## Decision

An EGC condition contrast estimated only from retained semantic-fidelity scores is not automatically valid. If intention-map adequacy differs by condition, deletion can change the estimand and can reverse the sign of the observed contrast.

The confirmatory report must therefore present, before interpretation:

1. retained and suppressed counts by condition;
2. retention rates and their difference;
3. the complete-case contrast;
4. worst-case bounded-outcome contrast limits;
5. assumption-indexed departure bounds;
6. whether the sign survives each bound;
7. the complete item-flow record for suppressed and indeterminate cases.

## Estimand

For conditions `A` and `B`, define the target contrast as:

```text
Delta = mean(B) - mean(A)
```

Semantic fidelity uses the frozen 1–7 scale. Suppressed outcomes remain conceptually present in the target population even though a numerical score is not used in the primary complete-case calculation.

## Worst-case bounds

For condition `c`:

- `n_c` = retained count;
- `m_c` = suppressed count;
- `S_c` = sum of retained scores;
- `N_c = n_c + m_c`.

With no assumption beyond the 1–7 outcome scale:

```text
mu_c_lower = (S_c + 1*m_c) / N_c
mu_c_upper = (S_c + 7*m_c) / N_c
```

The sharp contrast bounds are:

```text
Delta_lower = mu_B_lower - mu_A_upper
Delta_upper = mu_B_upper - mu_A_lower
```

A positive complete-case contrast is not sign-robust when `Delta_lower <= 0`. A negative complete-case contrast is not sign-robust when `Delta_upper >= 0`.

These bounds are deliberately severe. They describe all suppressed outcomes compatible with the scale, not the most plausible missingness process.

## Gamma departure analysis

The analysis also reports a grid of assumptions under which each condition's suppressed-outcome mean may differ from its retained mean by at most `gamma` scale points:

```text
missing_mean_c in [max(1, observed_mean_c - gamma),
                   min(7, observed_mean_c + gamma)]
```

The default prospective grid is:

```text
0.0, 0.5, 1.0, 2.0, 3.0, 6.0
```

Interpretation:

- `gamma = 0` assumes equal retained and suppressed means within each condition;
- increasing `gamma` weakens that assumption;
- `gamma = 6` approaches the full 1–7 worst case.

The gamma analysis is not an identified model and must not be described as correcting selection bias. It shows how much departure from equal means is required before the contrast sign becomes uncertain.

## Mandatory reporting status

Each analysis must return one of:

```text
positive_sign_robust
negative_sign_robust
point_identified_zero
sign_not_robust
```

The report must never replace `sign_not_robust` with a favorable complete-case conclusion.

## Input integrity

The implementation fails closed when:

- a condition has no retained scores;
- counts are negative or non-integral;
- retained score sums are impossible on the 1–7 scale;
- condition names are identical;
- missing-outcome bounds leave the 1–7 scale;
- the gamma grid is negative or decreasing.

Every output receives a deterministic SHA-256 analysis digest.

## Synthetic worked example

Suppose:

```text
Condition A: 8 retained, 2 suppressed, retained sum 32
Condition B: 9 retained, 1 suppressed, retained sum 45
```

The complete-case means are 4 and 5, so the complete-case contrast is `+1`.

Worst-case means are:

```text
A: [3.4, 4.6]
B: [4.6, 5.2]
```

Therefore:

```text
Delta in [0.0, 1.8]
```

The observed positive effect is not strictly sign-robust because zero remains compatible with the suppressed outcomes.

This example is a software fixture, not an EGC result.

## Claims supported

Supported as methodological and engineering statements:

- condition-dependent suppression can make complete-case contrasts selection-sensitive;
- bounded-outcome limits can be computed without imputing fabricated scores;
- retention imbalance and sign robustness can be reported explicitly;
- assumption-indexed bounds can show where a sign conclusion fails.

## Claims not supported

Not established:

- the distribution of suppressed outcomes;
- that missingness is random or ignorable;
- that gamma values are empirically realistic;
- that worst-case bounds are sufficiently informative for a final decision;
- that adequacy judgments are reliable;
- that semantic fidelity, EGC, hidden intention, subjectivity, or consciousness is validated.

## Falsification and revision conditions

Revise the protocol if:

- suppression is common enough that worst-case bounds are almost always vacuous;
- conclusions depend on an unreasonably narrow gamma assumption;
- map adequacy itself is strongly condition-dependent;
- adjudication reverses a material share of suppressions;
- suppressed cases cluster by domain, participant, prompt, or rater;
- individual-level paired structure requires bounds that the aggregate implementation cannot preserve.

## Implementation

- `research/egc2/analyze_adequacy_selection_sensitivity.py`
- `research/egc2/test_analyze_adequacy_selection_sensitivity.py`
- `research/egc2/results/adequacy_selection_sensitivity_validation.v0.1.json`

## Highest-leverage next action

Extend the analysis from aggregate condition counts to participant-paired bounds so the future within-person EGC contrast preserves pairing rather than discarding it during suppression sensitivity analysis.
