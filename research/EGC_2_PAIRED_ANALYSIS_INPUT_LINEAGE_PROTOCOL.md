# EGC 2.0 Paired Analysis Input Lineage Protocol

**Status:** Prospective analysis-input integrity contract  
**Date:** 2026-07-27  
**Scope:** Participant-level semantic-fidelity records consumed by paired adequacy-suppression sensitivity analysis

## Decision

Paired sensitivity analysis must not consume an informal table assembled after adequacy review. Every participant-condition record must be bound to its source record, adequacy decision, score disposition, decision version, and lock time before conversion into condition-A and condition-B scores.

The validator returns `analysis_ready = false` when any participant-condition record remains `blind_adjudication_required` or `indeterminate_insufficient_review`. Those records cannot be silently treated as suppressed outcomes. A new versioned and locked input must be created after resolution.

## Required lineage

Each record binds:

- participant pseudonym;
- condition label;
- adequacy disposition;
- retained score or explicit null;
- source-record SHA-256 digest;
- adequacy-decision SHA-256 digest;
- decision version;
- decision lock timestamp;
- canonical record digest.

The dataset additionally binds:

- study ID;
- analysis-plan ID;
- source-export digest;
- fixed condition order `A`, `B`;
- analysis lock timestamp;
- canonical analysis-input digest.

## Fail-closed rules

The input is rejected when:

1. a participant-condition record is duplicated;
2. either condition is absent for a participant;
3. a retained score is outside the 1–7 scale;
4. a non-retained disposition carries a score;
5. source-record digests are duplicated;
6. a record, decision, or export digest is malformed;
7. a record digest does not match its committed fields;
8. the dataset digest does not match the complete sorted record set;
9. the analysis plan or lock metadata changes after commitment.

Pair conversion is separately blocked while unresolved adequacy dispositions remain.

## Analysis consumption

Only two dispositions are consumable:

- `retain_numeric_score` → the frozen score is passed through;
- `suppress_numeric_score_reference_inadequate` → the score becomes `null` for bounded analysis.

The conversion artifact carries the exact `analysis_input_digest_sha256` consumed by the paired sensitivity procedure. This permits later reports to identify the precise frozen input underlying every bound.

## Evidence

Focused execution produced:

- 10 tests passed;
- 0 tests failed;
- Python compilation passed.

The adversarial suite rejects duplicate and missing conditions, score-disposition mismatch, post-hoc analysis-plan changes, unresolved decisions, duplicate source digests, and record tampering even when the outer dataset is redigested.

A synthetic two-participant fixture produced analysis-input digest:

```text
aa4c90bc27ea5f044835c5b198c14d9a2fabeac653607fe86d00a6daf24a6645
```

This is software-validation evidence only.

## Claim limits

Supported:

- the participant-condition input can be checked for internal lineage and disposition consistency;
- unresolved adequacy decisions can block analysis;
- the exact input consumed by paired bounds can be committed reproducibly;
- post-hoc changes to committed fields are detectable.

Not established:

- authenticity of source records or reviewer identities;
- trusted timestamps;
- reliability of adequacy decisions;
- correctness of retained scores;
- ignorability or identification of suppressed outcomes;
- validity of semantic fidelity, EGC, hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Connect the lineage-checked conversion artifact directly to `analyze_paired_adequacy_sensitivity.py` and require the paired-analysis report to echo and verify the frozen input digest before computing any bounds.
