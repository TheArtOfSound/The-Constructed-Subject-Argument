# EGC 2.0 Participant-Paired Adequacy-Suppression Sensitivity Protocol

**Status:** Prospective sensitivity-analysis contract  
**Date:** 2026-07-27  
**Scope:** Within-participant semantic-fidelity contrasts when one or both condition outcomes are suppressed because the intention map is inadequate  
**Non-claim:** This protocol does not identify missing scores, establish ignorable missingness, validate semantic fidelity, validate EGC, or support claims about consciousness.

## Decision

The primary EGC contrast is within participant. Aggregate condition-level sensitivity bounds discard that pairing and can answer a different question. The analysis must therefore preserve each participant as the unit of contrast, including participants with:

1. both condition outcomes observed;
2. condition A suppressed only;
3. condition B suppressed only;
4. both condition outcomes suppressed.

No suppressed score is imputed as if observed. Every participant contributes either an exact difference or an interval of differences compatible with the frozen score bounds.

## Estimand

For participant \(i\):

\[
D_i = Y_{iB} - Y_{iA}
\]

The target is:

\[
\Delta = \frac{1}{N}\sum_{i=1}^{N}D_i
\]

where the semantic-fidelity scale is bounded from 1 to 7.

## Participant-level bounds

### Complete pair

When both scores are observed:

\[
D_i = Y_{iB} - Y_{iA}
\]

The interval is a point.

### Condition B suppressed

When \(Y_{iA}\) is observed and \(Y_{iB}\in[1,7]\):

\[
D_i \in [1-Y_{iA},\;7-Y_{iA}]
\]

### Condition A suppressed

When \(Y_{iB}\) is observed and \(Y_{iA}\in[1,7]\):

\[
D_i \in [Y_{iB}-7,\;Y_{iB}-1]
\]

### Both suppressed

When both scores are suppressed:

\[
D_i \in [-6,6]
\]

The mean-difference bounds are the averages of the participant-level lower and upper limits. This preserves the sample's pairing structure and does not replace suppressed values with midpoint scores.

## Mandatory outputs

Every analysis must report:

- total participant count;
- count of complete pairs;
- count with A suppressed only;
- count with B suppressed only;
- count with both suppressed;
- complete-pair mean difference, when any complete pair exists;
- worst-case mean-difference lower and upper bounds;
- whether zero is contained;
- sign-robustness status;
- participant-level intervals;
- analysis digest.

Permitted sign labels are:

```text
positive_sign_robust
negative_sign_robust
point_identified_zero
sign_not_robust
```

A complete-pair contrast must not be described as robust when the all-participant interval includes zero.

## Gamma sensitivity

A supplementary assumption-indexed analysis bounds each suppressed condition score within \(\gamma\) points of that condition's observed mean, truncated to the 1–7 scale.

The prospective grid is:

```text
0.0, 0.5, 1.0, 2.0, 3.0, 6.0
```

This grid is a transparency device, not a claim that any \(\gamma\) is realistic. The report must show the first value at which sign robustness fails, when applicable.

## Leave-one-participant-out diagnostic

The analysis recomputes the bounds after omitting each participant. It reports:

- the range of lower bounds;
- the range of upper bounds;
- the number of omissions that change the full-sample sign-status label;
- the identity of each influential participant using only the study's opaque participant ID.

This is a fragility diagnostic. It is not a multiple-testing procedure or a basis for deleting influential participants.

## Input gates

The analysis fails closed when:

- no participants are supplied;
- participant IDs are blank or duplicated;
- a retained score lies outside 1–7;
- a score is neither numeric nor null;
- gamma values are negative, nonnumeric, or decreasing;
- gamma sensitivity lacks at least one observed score in either condition;
- leave-one-out analysis is requested with fewer than two participants.

## Synthetic validation result

A four-participant software fixture containing one case from each missingness pattern produced:

- complete-pair mean difference: `+2.0`;
- worst-case paired bounds: `[-2.0, 4.0]`;
- worst-case sign status: `sign_not_robust`;
- gamma `0.0` bounds: `[2.0, 2.0]`;
- gamma `2.0` bounds: `[0.0, 3.75]`.

This is software-validation evidence only. It is not participant evidence or an EGC result.

## Falsification and revision conditions

The procedure must be revised when:

- the participant identifier does not uniquely bind both condition records;
- suppression decisions are made after viewing the condition contrast;
- the score range changes;
- condition ordering is ambiguous;
- participant-level pairing is broken by preprocessing;
- the result depends on excluding a participant without a preregistered exclusion rule;
- the gamma grid is selected after inspecting the observed effect;
- repeated sessions or multiple outcomes require a model beyond one paired contrast per participant.

## Claims discipline

Supported by this implementation:

- paired worst-case bounds can preserve all participants without fabricating suppressed scores;
- one-sided and two-sided suppression have different participant-level uncertainty intervals;
- a favorable complete-pair contrast can coexist with an all-participant interval containing zero;
- leave-one-participant-out analysis can expose sign-status dependence.

Not supported:

- missing-at-random assumptions;
- causal identification of suppression;
- correctness or reliability of adequacy judgments;
- validity of the semantic-fidelity scale;
- validity of EGC;
- any inference about hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Integrate the paired bounds with the planned EGC analysis dataset schema so participant IDs, condition records, adequacy dispositions, and retained scores are lineage-checked before any condition contrast is calculated.
