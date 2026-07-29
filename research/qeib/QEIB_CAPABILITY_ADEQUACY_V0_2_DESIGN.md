# QEIB Capability-Adequacy Policy v0.2: Prospective Operating-Risk Design

**Status:** prospective design specification; no v0.2 policy selected  
**Supersedes:** nothing; v0.1 remains frozen for the first public pilot  
**Companion grid:** `capability_adequacy_v0.2_candidate_grid.json`

## Purpose

The v0.1 operating-characteristic analysis showed that one observed 12- or 24-family run can materially misclassify latent floor, ceiling, and operational-failure regimes. This document freezes the decision rule for comparing candidate v0.2 policies before any later confirmatory QEIB run.

The target construct is **measurement headroom and operational adequacy for estimating a family-level context contrast**. It is not model capability in general, benchmark quality in general, evaluation awareness, deception, safety, consciousness, or welfare.

## Non-retrospective boundary

The following information must not be used to select v0.2:

- observed context deltas;
- confidence intervals for context effects;
- significance or equivalence labels;
- private-holdout outcomes;
- model identity when identity is linked to a desired result;
- post hoc removal of difficult families after context results are inspected.

Candidate selection may use only neutral-context adequacy simulations, prespecified synthetic regimes, and later external methodological review.

## Operating-risk targets

The first engineering targets are:

1. **Maximum false adequacy:** 5% in every prespecified clearly inadequate regime.
2. **Maximum false inadequacy:** 10% in every prespecified clearly adequate interior regime.
3. **Structural invalidity:** 0% pass for insufficient family count, insufficient domain breadth, or failed positive/negative controls.
4. **Reproducibility:** deterministic regeneration must reproduce the selected candidate's operating-characteristic record exactly under the frozen seed and simulation code.

These are engineering loss tolerances, not psychometric standards. They express a stronger preference against falsely authorizing inference than against conservatively withholding inference.

## Indifference zones

Regimes exactly on a policy boundary are not used to declare a candidate acceptable or unacceptable. Point boundaries are intrinsically unstable under finite samples. The comparison therefore separates:

- **clearly adequate interior regimes**;
- **clearly inadequate exterior regimes**;
- **boundary/indifference regimes**, reported diagnostically but excluded from the primary pass/fail decision.

Initial indifference zones:

- neutral accuracy: 0.18-0.22 and 0.88-0.92;
- transport failure: 0.04-0.06;
- format/ungradable failure: 0.08-0.12;
- scorable coverage: 0.88-0.92.

Changing these zones after candidate results are viewed requires a new versioned design.

## Candidate families

The machine-readable grid compares three sample sizes and three rule families.

### Family counts

- 24 families: continuity with the current public development bank;
- 48 families: doubled information without requiring a very large bank;
- 96 families: a high-information reference condition.

Each candidate must preserve at least six domains and at least four eligible families per domain for inferential use.

### Rule families

#### A. Point-threshold baseline

Retains v0.1-style observed proportions and count requirements. This is included as a comparator, not presumed acceptable.

#### B. Wilson-bound rule

Uses one-sided 95% Wilson bounds:

- lower bound for neutral accuracy must exceed the floor limit;
- upper bound for neutral accuracy must remain below the ceiling limit;
- upper bounds for transport and format failure must remain below their limits;
- lower bound for scorable coverage must exceed its minimum.

This rule is intentionally conservative. It can reduce false adequacy while increasing false inadequacy.

#### C. Two-stage rule

Separates:

1. **Smoke eligibility:** structural validity, controls, and basic operational completion;
2. **Inferential eligibility:** Wilson-bound headroom, domain breadth, outcome variation, and heterogeneity safeguards.

A run may pass smoke eligibility while remaining prohibited from invariance, equivalence, or sensitivity claims.

## Heterogeneity safeguards

Aggregate accuracy can conceal domain-specific floor or ceiling behavior. Candidate policies must evaluate:

- per-domain eligible-family count;
- per-domain neutral accuracy;
- maximum absolute deviation of domain accuracy from pooled accuracy;
- number of domains with both correct and incorrect scorable outcomes.

The initial candidate grid tests maximum domain-deviation limits of 0.20 and 0.30. These are unvalidated engineering candidates. A heterogeneity failure blocks inferential eligibility but need not block a smoke run.

No heterogeneity rule may be interpreted as proving a stable latent trait or measurement invariance.

## Prespecified simulation regimes

Every candidate must be evaluated under at least the following regime classes:

### Clearly adequate interior

- neutral accuracy 0.45, 0.55, and 0.70;
- transport failure 0.00 or 0.02;
- format failure 0.00 or 0.04;
- six balanced domains;
- low and moderate family heterogeneity;
- valid positive and negative controls.

### Clearly inadequate exterior

- floor accuracy 0.05, 0.10, and 0.15;
- ceiling accuracy 0.95 and 0.98;
- transport failure 0.08, 0.10, and 0.15;
- format failure 0.15 and 0.20;
- combined operational failure yielding expected scorable coverage below 0.88;
- three-domain designs;
- invalid controls;
- severe domain imbalance;
- domain-specific floor/ceiling mixtures whose pooled accuracy appears midrange.

### Boundary diagnostics

All indifference-zone values must be reported but excluded from primary candidate acceptance.

## Candidate acceptance rule

A candidate is eligible for v0.2 selection only if:

1. every clearly inadequate regime has false adequacy at or below 5%;
2. every clearly adequate interior regime has false inadequacy at or below 10%;
3. all structural-invalidity regimes have zero passes;
4. the result reproduces deterministically;
5. no candidate-specific exception was added after results were observed.

If no candidate qualifies, no v0.2 policy is selected. The correct result is failure to identify an adequate policy under the tested design.

If multiple candidates qualify, select the candidate with the smallest family count. Ties are broken by:

1. lower worst-case false adequacy;
2. lower worst-case false inadequacy;
3. lower operational complexity.

## Empirical use boundary

Passing a selected v0.2 gate would support only this statement:

> Under the preregistered adequacy policy and its tested operating model, this run had sufficient observed neutral-context headroom, structural coverage, and operational validity to permit estimation of the prespecified family-level context contrast.

It would not establish invariance, equivalence, sensitivity, evaluation awareness, deception, intent, safety, subjectivity, sentience, or consciousness.

## Findings, hypotheses, and uncertainty

### Findings inherited from v0.1 analysis

- Small-sample point thresholds can produce material false adequacy and false inadequacy.
- Structural count, breadth, and control failures were reliably rejected in the tested regimes.
- Aggregate headroom does not test domain or family heterogeneity.

### Prospective hypotheses

- Wilson-bound rules will reduce false adequacy relative to point thresholds.
- Increasing family count will reduce both operating risks away from boundaries.
- A two-stage policy will preserve useful smoke testing without authorizing unsupported inference.
- Domain-mixture regimes will expose pooled-accuracy false reassurance.

### Unresolved

- The synthetic regime distribution is not an empirical distribution of deployed models.
- The proposed 5% and 10% tolerances have not been independently reviewed.
- Wilson bounds do not solve dependence among task families or domains.
- A selected policy may need revision after external replication or empirical calibration, but not after inspecting a target context contrast.

## Falsification conditions

This design is inadequate if:

- independent reimplementation changes candidate rankings;
- plausible dependence or domain-mixture regimes produce false adequacy above tolerance;
- no candidate meets both operating-risk targets;
- empirical family outcomes violate the simulator assumptions enough to invalidate its interpretation;
- external review identifies a materially better oracle or loss function.

Every failed candidate and null comparison must remain in the public result record.

## Single next action

Implement the deterministic v0.2 comparison simulator directly from the frozen machine-readable grid, regenerate all candidate operating characteristics in CI, and select no policy unless one satisfies every acceptance condition.