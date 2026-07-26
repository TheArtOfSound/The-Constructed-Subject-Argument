# EGC 2.0 Structural Gate Evaluator and Dropout Smoke Review

## Status

Engineering implementation and deterministic smoke validation. This is not an operating-characteristic calibration and does not validate the provisional thresholds.

## Concrete contribution

A machine-executable evaluator now applies the seven preregistered gates in fixed order and separates structural invalidity from inferential noncomputability. It preserves every failed gate, the first failure under the preregistered precedence rule, graph components, degrees, articulation raters, bridges, retained-row counts, and the decision to suppress or permit a confirmatory p-value.

The same module adds deterministic stress-test generators for random whole-rater loss, score-targeted whole-rater loss, domain-selective row loss, domain-specific rater loss, targeted domain-rater loss, and a combined structural attack. Score-targeted mechanisms are adversarial oracle analyses, not models of observed real-rater behavior.

## Validation

Twelve focused tests passed. They force every gate to pass and fail, verify structural-failure precedence over inferential failure, verify deterministic dropout, and verify that confirmatory reporting is blocked whenever structural validity fails. `python -m py_compile` also passed.

## Smoke grid

The smoke grid used a deterministic synthetic 12-rater, four-class, four-domain, 24-item-per-class, six-ratings-per-item assignment with 576 rows. The inferential inputs were deliberately held computable (`observed_variance = 0.2`, undefined-pattern fraction `0`) so the run isolated structural gates.

- No dropout: all gates passed.
- One random whole-rater loss: all gates passed.
- Two random whole-rater losses: G1 item replication failed because fewer than 95% of items retained at least five ratings.
- Three random whole-rater losses: G1, G2, G3, and G4 failed.
- Thirty-percent and fifty-percent held-out-domain row loss: G1 and G4 failed.
- Two score-targeted raters removed only within the held-out domain: G1 and G4 failed.
- Combined two-rater loss plus 50% held-out-domain attrition: G1, G3, and G4 failed.

## Finding versus hypothesis

### Supported engineering finding

The evaluator detects structural invalidity before confirmatory reporting and does not silently delete affected rows, items, raters, classes, or domains.

The frozen G1 rule is stricter than the phrase “survive two-rater loss” may imply. Two complete rater losses leave every item with at least four ratings, but they do not guarantee that 95% of items retain at least five. Under the tested balanced synthetic assignment, two losses therefore fail G1.

### Hypotheses not tested

The smoke grid does not estimate failure probabilities, Type-I error, power, or realistic missingness prevalence. It does not establish that the synthetic assignment matches the committed production assignment generator. It does not establish that four or five ratings are psychometrically sufficient.

### Unresolved uncertainty

The gate thresholds may be too strict or too permissive. In particular, G1 combines a hard four-rating floor with a 95%-at-five requirement that may reject datasets after two complete losses even when the item-rater graph remains connected. That may be desirable fail-closed behavior, or it may unnecessarily defeat the intended two-loss tolerance. Only preregistered operating-characteristic calibration can decide.

## Permitted conclusion

A confirmatory p-value can now be programmatically withheld when the retained design violates the frozen structural contract.

## Prohibited conclusion

Passing the evaluator does not validate the semantic-fidelity construct, establish unbiasedness, make dropout ignorable, or validate the restricted-wild inference method.

## Next highest-leverage action

Run a Monte Carlo gate operating-characteristic calibration on the exact committed incomplete-block assignment, comparing the current G1 threshold with sensitivity alternatives and reporting structural-indeterminate rates under one- and two-rater loss plus domain-selective attrition.
