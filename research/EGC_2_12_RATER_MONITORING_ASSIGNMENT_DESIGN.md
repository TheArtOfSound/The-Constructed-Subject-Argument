# EGC 2.0 — Twelve-Rater Monitoring Assignment Design

**Status:** Engineering design validated in synthetic assignment logic; not yet validated with real raters or real anchor packets.

## 1. Purpose

The previous detector calibration found that the eight-rater, 18-item-per-class design was underpowered, while a 12-rater, 36-item-per-class design exceeded 0.90 support in the interior synthetic regime. The immediate design problem was therefore not whether to collect a larger fully crossed rating matrix, but whether the broader monitoring bank could be distributed without requiring every rater to score every item.

This document specifies a connected incomplete-block design that does that.

## 2. Monitoring classes

The design contains four concealed classes:

1. exact recurring anchors;
2. surface-variant anchors;
3. structural-transfer probes;
4. novel responses.

Each class contains 36 unique study-level items. The class label is retained only in the private audit schedule and is omitted from the rater-facing queue.

## 3. Assignment structure

The default design uses:

- 12 raters;
- 36 items per class;
- four ratings per item;
- 144 unique items in total;
- 576 total item-rating assignments;
- 12 items from each class per rater;
- 48 total items per rater.

Thus, each rater sees one third of each class and one third of the full bank. No rater is required to score all 144 items.

The assignment is generated from three cyclic four-rater block families per class. Each block family contributes 12 items, and every rater appears exactly four times within each family. Across three families, every rater therefore receives exactly 12 assignments per class.

The rater-to-cyclic-index mapping is independently permuted by class. This prevents the same visible four-rater blocks from being mechanically reused across all classes while preserving the balance proof.

## 4. Session ordering and concealment

Every rater receives 48 presentations arranged as 12 four-item cycles. Each cycle contains exactly one item from each monitoring class, with class order randomized subject to no adjacent repeated class across cycle boundaries.

The rater-facing queue contains only:

- presentation position;
- opaque presentation identifier;
- item identifier.

It excludes:

- monitoring class;
- block family;
- rater identifier;
- anchor/novel status.

The private audit schedule preserves those fields for balance, drift, and dropout analysis.

Concealing metadata does not prove that raters cannot infer class membership from content. Exact recurring anchors may still become recognizable. That remains an empirical measurement issue addressed by the anchor-memorization protocol.

## 5. Dropout audit

The generator exhaustively enumerates:

- all 12 possible one-rater dropout scenarios;
- all 66 possible two-rater dropout scenarios.

For every scenario it checks:

1. minimum remaining ratings per item;
2. overall co-rating graph connectivity;
3. class-specific co-rating graph connectivity;
4. minimum class-specific graph degree.

Under the committed seed and construction:

- every one-rater dropout leaves at least three ratings per item;
- every two-rater dropout leaves at least two ratings per item;
- the overall co-rating graph remains connected in every scenario;
- each class-specific co-rating graph remains connected in every scenario;
- no enumerated dropout scenario fails the engineering checks.

These are assignment properties only. They do not establish that two ratings per item are scientifically sufficient after dropout, that missingness is ignorable, or that connectedness prevents condition-effect bias.

## 6. Validation contract

The generator fails closed when any of the following occurs:

- an item does not receive exactly four ratings;
- a class does not contain exactly 36 items;
- a rater does not receive exactly 12 items from every class;
- a rater does not receive exactly 48 items overall;
- monitoring metadata appears in the public queue;
- adjacent class repetition appears in a session;
- class balance differs by more than one item within a session quartile;
- any one- or two-rater dropout disconnects the overall or class-specific graph;
- output is not reproducible from the fixed seed.

## 7. Evidence produced

The executable generator and tests establish the following engineering findings:

- a 12-rater × 36-item-per-class incomplete-block assignment exists;
- exact per-rater and per-class balance can be achieved by construction;
- the full monitoring bank can be distributed with 48 items per rater rather than 144;
- class labels can be withheld from the rater-facing queue;
- the selected block structure remains graph-connected after every one- and two-rater dropout combination;
- deterministic regeneration is possible through a canonical SHA-256 digest.

## 8. Claims not supported

This design does not establish:

- that 48 scored items is an acceptable cognitive workload;
- that fatigue, learning, or anchor memorization will be negligible;
- that four ratings per item are sufficient for the target reliability;
- that two remaining ratings after dropout preserve adequate precision;
- that graph connectivity prevents informative-dropout bias;
- that the four monitoring classes are empirically distinguishable;
- that the detector's percentile bootstrap has correct finite-sample coverage;
- that 12 raters and 36 items per class are cost-optimal.

## 9. Required next validation

The assignment must be coupled to the existing rater-process simulator. The next simulation should impose:

- fatigue across the 48-item session;
- exact-anchor recognition and memorization;
- novel-item drift;
- rater severity heterogeneity;
- one- and two-rater dropout;
- disagreement-dependent and severity-dependent dropout.

The primary decision question is whether the incomplete-block design retains the prior detector's sensitivity gains after realistic session burden and missingness are introduced.

## 10. Highest-leverage next action

Run a workload-aware simulation comparing the new 12-rater × 36-item-per-class incomplete-block design against the prior 8-rater × 18-item design, holding the data-generating regime fixed and measuring detector support, false reassurance, false-positive rate, indeterminate rate, and dropout sensitivity.
