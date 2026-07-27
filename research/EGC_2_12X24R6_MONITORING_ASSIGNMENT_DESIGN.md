# EGC 2.0 — Deterministic 12×24×6 Monitoring Assignment

## Decision

A deterministic connected incomplete-block assignment now exists for the frozen `incomplete_12x24_r6` gate target.

The design contains:

- 12 raters;
- four concealed monitoring classes;
- four explicit domains;
- 24 items per class;
- six items per class × domain cell;
- six ratings per item;
- 96 unique items;
- 576 total assignments;
- 48 items per rater;
- 12 items per class per rater;
- three items per class × domain cell per rater.

This resolves the prior design-contract mismatch between the committed `12×36×4` generator and the frozen structural-gate target.

## Construction

Each monitoring class uses two cyclic six-rater block families, each containing 12 item blocks. Every rater appears six times in each family and therefore 12 times per class.

A fixed domain coloring assigns six items from every class to each of four domains while giving every rater exactly three items in every class × domain cell.

The mapping from cyclic positions to rater IDs is independently shuffled by class. The assignment therefore preserves the combinatorial guarantees without mechanically exposing identical visible block membership across classes.

## Concealed queues

Every rater receives 48 presentations in 12 four-item cycles. Each cycle contains:

- every monitoring class exactly once;
- every domain exactly once.

The rater-facing queue exposes only `position`, `presentation_id`, and `item_id`. Class, domain, block-family, and rater metadata remain in the private audit schedule.

This metadata concealment does not prove that raters cannot recognize recurring anchors from item content.

## Exhaustive dropout audit

All one-rater and two-rater loss combinations were enumerated.

| Dropout | Scenarios | Failures | Minimum ratings/item | Minimum class graph degree | Minimum domain graph degree |
|---|---:|---:|---:|---:|---:|
| One rater | 12 | 0 | 5 | 10 | 10 |
| Two raters | 66 | 0 | 4 | 9 | 9 |

For every enumerated case:

- the overall rater co-rating graph remained connected;
- every class-specific rater graph remained connected;
- every domain-specific rater graph remained connected;
- no item lost more ratings than mechanically implied by the number of removed raters.

## Validation

Eight focused tests passed:

1. complete design validity;
2. exact 96-item and 576-assignment budget;
3. exact rater × class × domain balance;
4. public metadata concealment;
5. four-item cycle balance;
6. exhaustive one-/two-rater dropout robustness;
7. deterministic regeneration;
8. tamper detection.

Deterministic content digest:

```text
3d9012606c5803c6369eea601679cffa298569c8f4f84c48c878f6fc95420cc8
```

## Claims supported

Within the engineering construction:

- the frozen `12×24×6` design is mathematically feasible;
- exact class and domain balance can be guaranteed by construction;
- the design can limit each rater to 48 items while retaining six ratings per item;
- class- and domain-specific linkage survives every one- and two-rater loss combination;
- the previous compatibility blocker is resolved.

## Claims not established

The construction does not establish that:

- 48 items avoids fatigue;
- six ratings per item are psychometrically sufficient;
- four remaining ratings after two-rater loss preserve acceptable reliability;
- connectedness prevents informative-dropout bias;
- the frozen structural thresholds have acceptable Type-I error and power;
- domain labels correspond to empirically homogeneous populations;
- exact anchors cannot be recognized from content.

## Highest-leverage next action

Run the deterministic structural-gate evaluator against this exact generated assignment, then calibrate structural-indeterminate rates under one-/two-rater loss and domain-selective attrition without changing the assignment or gate thresholds.
