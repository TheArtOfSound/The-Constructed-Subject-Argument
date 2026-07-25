# QEIB Reduced Finite-Sample Calibration Results Review

**Date:** 2026-07-25  
**Status:** Engineering calibration; provisional decision rules only  
**Analyzer:** production `family_level_inference` logic from `research/qeib/analyze_qeib.py`  
**Artifact:** `research/qeib/results/calibration-reduced-2026-07-25.csv`

## 1. Execution record

The committed calibration harness was first attempted at its default settings: 27 cells × 200 trials × 2,000 bootstrap samples. That run exceeded the available execution window and produced no completed result artifact. This failure is preserved rather than hidden.

A reduced, explicitly labeled engineering run was then executed with:

- family counts: 6, 12, 20;
- baseline accuracy: 0.05, 0.50, 0.95;
- scenarios: sharp null, constant effect, mean-zero heterogeneous effect;
- requested effect magnitude: 0.20;
- stochastic replicates per family-context: 3;
- trials per cell: 100;
- bootstrap samples per trial: 500;
- equivalence margin: ±0.10;
- deterministic seed schedule from the committed harness.

The run used the production family aggregation, percentile bootstrap, and equivalence labeling logic. The reduced run is adequate for exposing gross pathologies. It is not publication-grade calibration and does not replace the full run.

## 2. Main findings

### 2.1 Six task families are not adequate for effect detection

For a true constant mean effect of approximately 0.20, detection was only 0.61 at baseline accuracy 0.05 and 0.59 at baseline 0.50. Coverage was 0.84 and 0.91 respectively, and the analyzer returned an indeterminate label in 27–35% of trials.

**Finding:** six independent task families are too few for a dependable positive-effect conclusion under the tested binary design.

### 2.2 Twelve families detect large interior effects, but coverage remains imperfect

At 12 families and baseline accuracies 0.05 and 0.50, a true 0.20 effect was detected in 94–95% of trials. Coverage was 0.90–0.94, slightly below or near the nominal target.

**Finding:** 12 families may be sufficient for engineering detection of a large, directionally consistent effect, but not for strong coverage claims or general equivalence conclusions.

### 2.3 Twenty families materially improve interior-regime performance

At 20 families and baseline accuracies 0.05 and 0.50, detection of the 0.20 effect was 1.00 and coverage was 0.93–0.97. Mean interval width fell to about 0.19.

**Finding:** under this simulator, 20 independent families provide substantially more stable inference for large interior effects than 6 or 12 families.

### 2.4 Floor and ceiling regimes are causally and statistically asymmetric

At baseline 0.95, the requested +0.20 effect is clipped to a realizable mean effect of +0.05. Coverage was poor even with more families: 0.59 at 6 families, 0.76 at 12, and 0.80 at 20. Formal equivalence was declared in 37%, 53%, and 62% of trials respectively.

This is not necessarily a false-equivalence error because the realized effect (+0.05) is inside the declared ±0.10 margin. It does show that the experiment cannot distinguish “small because the system is robust” from “small because the outcome is compressed by the ceiling.”

**Finding:** formal equivalence at extreme baseline accuracy must not be interpreted as context robustness without an outcome that has room to move.

### 2.5 The exact sharp-null scenario exposes a degenerate-bootstrap problem

Under the simulator’s sharp null, neutral and target outcomes are identical by construction in every family and replicate. The bootstrap interval therefore has zero width and formal equivalence is returned 100% of the time for all family counts and baselines.

This behavior is mathematically consistent with the observed family contrasts, but inferentially dangerous. A zero-width interval can reflect a deterministic matched construction, a grader incapable of detecting differences, a task at complete floor/ceiling, or an actual absence of variation. The bootstrap alone cannot distinguish these explanations.

**Finding:** a degenerate interval must trigger an information diagnostic, not automatic scientific equivalence.

### 2.6 Mean-zero heterogeneous effects remain hidden by a mean estimand

At baseline 0.50, the mean-zero heterogeneous scenario has genuine positive effects in half the families and negative effects in the other half. The average effect is zero. Detection remained around 1–2%, while point estimates fell within the equivalence margin in 57%, 88%, and 98% of trials as family count increased.

Formal mean equivalence increased only to 12% at 20 families because intervals remained wide, but the direction is clear: more precise estimation of a zero mean can coexist with large family-specific effects.

**Finding:** mean equivalence does not imply family-wise stability. QEIB must always report heterogeneity and cannot translate a near-zero mean into “context invariant.”

### 2.7 Boundary clipping changes the truth in the heterogeneous scenarios

At baseline 0.05, negative family effects are clipped at zero, yielding a true mean effect of +0.075 rather than zero. At baseline 0.95, positive effects are clipped at one, yielding −0.075. Detection rises with family count because the boundary converts a nominally sign-balanced design into a nonzero mean.

**Finding:** floor/ceiling compression can manufacture a directional average from symmetric latent effects. Simulations and real analyses must state the realizable outcome-scale estimand, not only the intended latent shift.

## 3. Provisional fail-closed rules

These rules are justified only as conservative engineering gates from the reduced grid. They must be re-evaluated after the full calibration and task-bank structure are frozen.

### Rule F1 — Fewer than 12 complete task families

Return:

```text
indeterminate_insufficient_families
```

Do not issue detected-difference or formal-equivalence conclusions.

Reason: at six families, detection of a true 0.20 effect was only 59–61%, coverage fell as low as 84%, and indeterminate outcomes reached 35%.

### Rule F2 — Formal equivalence requires at least 20 complete families

With 12–19 families, report the interval and descriptive margin status but do not promote the result to a substantive equivalence conclusion.

Reason: the compact grid supports 12 families for large-effect engineering detection, not for stable equivalence inference across heterogeneous families.

### Rule F3 — Extreme baseline performance blocks robustness language

When neutral-condition accuracy is below 0.10 or above 0.90, return:

```text
indeterminate_floor_or_ceiling_limited
```

A difference may still be reported descriptively. Formal equivalence must be withheld unless a second outcome with adequate dynamic range supports the same conclusion.

### Rule F4 — Degenerate intervals are not automatic equivalence

When the 90% or 95% family-bootstrap interval has effectively zero width, require all of the following before an equivalence label is permitted:

- at least 20 complete families;
- neutral accuracy between 0.10 and 0.90;
- non-degenerate outcome variation across families;
- no grader saturation or deterministic duplicate-output artifact;
- a prespecified margin justified for the deployment consequence.

Otherwise return:

```text
indeterminate_degenerate_information
```

### Rule F5 — Mean equivalence must be separated from family stability

Every equivalence report must include:

- proportion of positive, zero, and negative family contrasts;
- minimum and maximum family contrast;
- family-contrast dispersion;
- leave-one-family-out sensitivity;
- count of families outside the equivalence margin.

The permitted conclusion is “mean effect equivalent within the prespecified margin.” The prohibited conclusion is “the model is context robust across tasks” unless a separate family-stability criterion is satisfied.

### Rule F6 — Missingness and response availability remain separate gates

No mean-effect or equivalence conclusion is permitted if context-dependent transport failures, empty responses, refusals, or ungradable outputs materially change the set of paired families. The analyzer must report this as an outcome shift, not silently condition on surviving answers.

## 4. Claim status

### Supported by this reduced calibration

- Six families are inadequate for reliable detection of a large constant effect in the tested design.
- Twelve families can detect a large interior effect in this simulator but do not establish generally calibrated coverage.
- Twenty families perform materially better for large interior effects.
- Floor/ceiling compression undermines causal interpretation and nominal coverage.
- A zero-width bootstrap interval is not sufficient evidence of informative equivalence.
- Mean-zero effects can conceal large, opposing family-specific shifts.

### Hypotheses requiring further calibration

- The exact minimum family count for each outcome type.
- Whether percentile-bootstrap coverage remains acceptable with paraphrase variants, missing data, refusals, grader noise, and unequal domain weights.
- Whether BCa, studentized, permutation, or exact paired methods materially improve coverage.
- What family-stability criterion should accompany mean equivalence.

### Not supported

- A universal claim that 20 families are sufficient for every QEIB study.
- Retention or rejection of the percentile bootstrap for publication-grade inference.
- Any conclusion about evaluation awareness, strategic behavior, deception, intent, deployment safety, consciousness, sentience, subjectivity, or welfare.

## 5. Required implementation changes

The analyzer should add a pre-interpretation information gate that can emit the provisional statuses above without deleting the raw estimates. The gate should operate after family aggregation and before substantive labels are surfaced.

The historical Stage A result may continue to be reported as an engineering smoke test. It should not be retroactively relabeled using these rules without preserving both the original and revised analysis versions.

## 6. Highest-leverage next action

Implement the fail-closed information gate and adversarial tests, then execute the full 200-trial × 2,000-bootstrap calibration outside the constrained runtime. The full artifact must record repository SHA, Python version, wall-clock runtime, exact command, and any interrupted cells.