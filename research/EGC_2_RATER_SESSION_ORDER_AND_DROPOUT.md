# EGC 2.0 Rater Session Ordering and Dropout Robustness

**Status:** Executable pilot engineering design  
**Date:** 2026-07-25  
**Scope:** Presentation-order concealment and assignment-graph robustness  
**Non-claim:** A balanced or connected assignment does not establish rating reliability, construct validity, or adequate statistical power.

## 1. Purpose

The existing EGC 2.0 assignment generator determines which raters receive each primary response, anchor, and blind repeat. It did not determine presentation order. That omission matters because visible item type, adjacent repeats, domain blocks, anchor clustering, and fatigue-position imbalance can change ratings even when the rater-to-item assignment is balanced.

The session scheduler therefore adds a second frozen layer:

1. the assignment layer determines who rates what;
2. the session-order layer determines when each assigned item appears and what metadata the rater can see.

The two layers remain separately auditable.

## 2. Rater-facing concealment

The rater-facing queue contains only:

- an opaque `presentation_id`;
- a one-based session position.

It does not expose:

- `assignment_type`;
- response or anchor identifiers;
- condition;
- prompt domain;
- participant identity;
- repeat linkage.

A separate audit schedule retains those fields for reproducibility and validation. Concealment is an engineering control against obvious item-type recognition. It does not prove that a rater cannot infer item type from substantive content.

## 3. Ordering constraints

For each rater, the scheduler:

1. places any primary response selected for blind repetition early enough to permit a later repeat;
2. interleaves remaining primary responses across prompt domains;
3. spreads anchors approximately across the session;
4. inserts each blind repeat after its original with a preregistered minimum positional gap;
5. rejects schedules with repeat-before-source or repeat-spacing violations;
6. rejects rater-facing queues that leak audit metadata;
7. rejects runs of more than two consecutive anchors.

The default minimum repeat gap is 18 presented items. This is an engineering value, not a validated memory-washout threshold. Pilot evidence must determine whether it is sufficient.

## 4. Dropout robustness estimand

The dropout audit uses the primary-response assignment graph.

- Nodes are retained raters.
- Two raters are connected when they share at least one rated response.
- Every possible one-rater and two-rater dropout combination is enumerated.
- For each scenario, the audit reports graph connectedness, the minimum remaining ratings per response, and the number of responses falling below two ratings.

The default eight-rater/four-ratings-per-response construction guarantees at least three ratings after any one-rater dropout and at least two after any two-rater dropout. Connectivity must still be checked because rating count alone does not guarantee a connected comparison graph.

## 5. Current executable result

The deterministic test fixture based on the committed 30-participant design produced:

- concealed rater-facing queues;
- all blind repeats after their source with at least the configured gap;
- no assignment loss;
- connected rater graphs under every one-rater and two-rater dropout combination;
- at least three ratings per response after one dropout;
- at least two ratings per response after two dropouts.

These are construction and software-validation results. They do not establish that replacement raters can be introduced without bias, that two ratings are scientifically adequate, or that dropout is independent of rater severity.

## 6. Fail-closed rules

The generated schedule is invalid if:

- any assigned item is missing or duplicated;
- rater-facing metadata reveals item type or linkage;
- a repeat appears before its source;
- a repeat violates the minimum gap;
- more than two anchors appear consecutively;
- the audit cannot reconcile all opaque presentation IDs;
- a declared dropout robustness result is based on sampled rather than enumerated one- and two-rater combinations.

Anchor quartile imbalance is currently a warning rather than a hard failure because insertion of blind repeats can shift quartile boundaries slightly. A future version should optimize anchor placement and fatigue balance jointly rather than applying a post-hoc tolerance.

## 7. Interpretation limits

Permitted conclusions:

- the declared schedule satisfies the encoded ordering and concealment constraints;
- the primary assignment graph remains connected under the enumerated dropout scenarios;
- minimum remaining rating counts are known for those scenarios.

Prohibited conclusions:

- four raters are sufficient;
- two ratings after dropout are sufficient;
- the rating instrument is reliable;
- anchors are valid;
- rater dropout is ignorable;
- opaque IDs prevent all item-type inference;
- session ordering eliminates fatigue or carryover effects.

## 8. Highest-leverage next step

Run a simulated rating study with controlled rater severity, domain effects, fatigue drift, anchor drift, and nonrandom dropout. Estimate how often the proposed assignment and session order recover the true condition effect and how much bias remains when severe or lenient raters disproportionately drop out.
