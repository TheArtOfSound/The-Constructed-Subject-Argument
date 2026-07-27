# EGC 2.0 Intention-Map Adequacy Adjudication Protocol

**Status:** Provisional pilot rule; not validated for confirmatory inference  
**Scope:** Whether a semantic-fidelity rating has a usable reference target  
**Non-claim:** This protocol does not recover a participant's true intention, score semantic fidelity, validate EGC, or support claims about consciousness.

## Problem

Semantic fidelity is only defined relative to a usable intention map. A low-fidelity response and an unusable reference target are different failure modes:

- **Low fidelity:** the map is interpretable, but the response omits, distorts, or reverses its meaning.
- **Reference inadequacy:** the map is too sparse, internally conflicting, uninterpretable, response-dependent, or otherwise incapable of supporting a defensible comparison.

Forcing a numerical fidelity score when the reference is unusable manufactures precision. Silently deleting such items can create selection bias, especially if map adequacy differs by condition, domain, participant, or response difficulty.

## Frozen pilot decision rule

At least three independent, condition-blind reviewers evaluate map adequacy before constructor targets or condition labels are revealed.

For the initial three-reviewer design:

1. **All three adequate:** retain the numerical semantic-fidelity score.
2. **At least two non-adequate:** suppress the numerical score for confirmatory use because the reference target is inadequate.
3. **One non-adequate and two adequate:** require blind adjudication; do not release a confirmatory score until resolved under a prespecified procedure.
4. **Fewer than three complete unique reviews:** return `indeterminate_insufficient_review`.

When more than three reviewers are used, suppression requires a strict majority unless a different threshold was frozen before review.

Every non-adequate judgment requires reason evidence. Duplicate reviewer identities, invalid adequacy values, or malformed confidence fields fail closed.

## Permitted dispositions

```text
retain_numeric_score
suppress_numeric_score_reference_inadequate
blind_adjudication_required
indeterminate_insufficient_review
```

Raw fidelity scores remain preserved even when suppressed. Suppression changes their inferential status; it does not erase the observations.

## Selection-bias controls

All suppressed, adjudicated, and indeterminate items must remain visible in the item-flow report. Report adequacy outcomes by:

- experimental condition, while keeping adjudication blind until frozen;
- prompt domain and form;
- participant and session;
- monitoring class;
- intention-map length and concept count;
- reviewer and reviewer severity;
- reason category.

The confirmatory EGC effect must not be estimated only among retained items without also reporting:

1. retention rates by condition;
2. the difference in retention rates and uncertainty interval;
3. sensitivity analyses under prespecified bounds for suppressed outcomes;
4. whether the substantive conclusion changes when all inadequate-map cases are treated as a separate outcome rather than deleted.

Replacement items or additional ratings may not be targeted using preliminary condition effects.

## Falsification and revision conditions

The rule is weakened or rejected if pilot evidence shows any of the following:

- majority suppression frequently disagrees with independent adjudication;
- reviewers systematically confuse poor response quality with poor map adequacy;
- adequacy decisions depend strongly on response text despite the map being intended as an independent reference;
- suppression rates differ materially by condition or domain;
- the strict-majority rule produces unstable decisions under leave-one-reviewer-out analysis;
- adjudication reverses a large share of initial decisions;
- the decision materially depends on the provisional reviewer threshold.

The thresholds are engineering rules for the pilot, not universal psychometric cutoffs.

## Executable implementation

`research/egc2/evaluate_intention_map_adequacy.py` implements the rule and returns a deterministic decision digest. The digest provides tamper evidence only; it does not authenticate reviewers or timestamps.

`research/egc2/test_evaluate_intention_map_adequacy.py` tests unanimous retention, majority suppression, mixed-review adjudication, insufficient review, duplicate reviewers, missing reason evidence, invalid confidence, strict-majority behavior with four reviewers, invalid thresholds, and deterministic output.

## Claim status

Supported as engineering design:

- reference inadequacy can be separated from low semantic fidelity;
- forced midpoint or arbitrary numerical scoring can be blocked;
- mixed adequacy judgments can be routed to blind adjudication;
- suppressed cases can remain auditable rather than silently disappearing.

Not established:

- that reviewers can reliably judge map adequacy;
- that majority voting is optimal;
- that suppression is ignorable for condition-effect estimation;
- that the reason categories are exhaustive;
- that any current anchor or participant map is adequate;
- that semantic fidelity or EGC is validated.

## Highest-leverage next action

Apply this evaluator to the first three real locked expert-review submissions, then quantify agreement, suppression, adjudication, and condition-blind leave-one-reviewer-out stability before allowing any anchor to become a pilot candidate.
