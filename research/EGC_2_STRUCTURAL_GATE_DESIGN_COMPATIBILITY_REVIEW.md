# EGC 2.0 Structural-Gate Design Compatibility Review

**Status:** engineering incompatibility identified; Monte Carlo calibration blocked fail-closed  
**Date:** 2026-07-26

## Question

Can the frozen structural-validity gate contract be calibrated directly on the committed 12-rater monitoring assignment generator without first reconciling their design targets?

## Repository evidence

The committed assignment generator defines:

- 12 raters;
- 36 items per monitoring class;
- 4 monitoring classes;
- 4 ratings per item;
- 576 total assignments.

The frozen gate contract identifies a different target:

- design ID `incomplete_12x24_r6`;
- 12 raters;
- 24 items per monitoring class;
- 4 monitoring classes;
- 6 ratings per item;
- 576 total assignments.

The equal total rating budget conceals a material design mismatch. One design spends the budget on broader item coverage; the other spends it on denser replication.

## Fail-fast result

The compatibility evaluator returns:

```text
incompatible_fail_closed
```

with three material mismatches:

1. ratings per item: `4` versus `6`;
2. items per class: `36` versus `24`;
3. G1 baseline infeasibility.

G1 requires every item to retain at least four distinct raters and at least 95% of items to retain five or more ratings. In the committed four-ratings-per-item assignment, the maximum possible baseline fraction with at least five ratings is exactly `0.0`. The assignment therefore fails G1 before any dropout occurs.

## Why calibration was not run

Running one- and two-rater dropout Monte Carlo under this mismatch would answer the wrong question. Every generated dataset would be structurally invalid at baseline under the frozen G1 rule, making its dropout operating characteristics uninterpretable as evidence about the intended `12×24×6` design.

This is not a null result about structural gates. It is a design-contract incompatibility.

## New engineering control

`research/egc2/check_structural_gate_design_compatibility.py` now:

- normalizes assignment-generator and compact design metadata;
- compares raters, ratings per item, items per class, class count, and total assignments;
- evaluates whether G1 is mathematically satisfiable before dropout;
- fails closed when the design and gate target diverge;
- permits calibration only after compatibility passes.

The check deliberately does not claim that a compatible design or passing gate is scientifically valid. It only prevents invalid calibration against the wrong design.

## Validation

Five tests passed:

1. the intended `12×24×6` metadata passes;
2. the committed `12×36×4` metadata fails;
3. total assignments are derived correctly when omitted;
4. four ratings per item cannot satisfy a 95%-at-five requirement;
5. missing metadata fails clearly.

`py_compile` also passed.

## Claim status

### Supported

- The committed generator and frozen gate contract target different allocation designs despite sharing a 576-rating budget.
- The frozen G1 gate is impossible to satisfy at baseline on the committed four-ratings-per-item assignment.
- Calibration on that assignment must be blocked until the design target is reconciled.

### Not supported

- That the `12×24×6` design is preferable to `12×36×4`.
- That G1 should be weakened to fit the existing generator.
- That either allocation provides adequate reliability, power, generalization, or dropout robustness.
- That compatibility validates the gate thresholds.

## Required decision before calibration

Choose one of two scientifically distinct paths:

1. generate and commit the intended `incomplete_12x24_r6` assignment, then calibrate the frozen gates unchanged; or
2. define a separate gate contract for `12×36×4`, with a replication rule that is possible at baseline, and calibrate it as a distinct design rather than silently reusing the `12×24×6` thresholds.

The first path is the cleanest continuation because the restricted-wild N2/N3 work already centered on `12×24×6`.

## Highest-leverage next action

Implement and validate a deterministic connected incomplete-block `12×24×6` assignment generator, including concealed queues and exhaustive one-/two-rater dropout audits, then run the structural-gate calibration on that exact artifact.
