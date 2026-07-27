# EGC 2.0 Lineage-Checked Paired Sensitivity Entrypoint

**Status:** Confirmatory consumption boundary implemented; real participant data absent  
**Date:** 2026-07-27  
**Scope:** Participant-paired semantic-fidelity sensitivity analysis under adequacy suppression

## Decision

The lower-level paired sensitivity engine remains useful for method development and unit tests, but it must not be the production entrypoint for a confirmatory EGC analysis.

The required production path is now:

```text
locked participant-condition artifact
→ lineage validation
→ deterministic pair conversion
→ participant-count and digest checks
→ paired suppression sensitivity engine
→ final digest-bound analysis report
```

This closes a concrete weakness: an analyst could previously pass an informal in-memory list of pairs into the sensitivity engine without proving which frozen source records, adequacy decisions, analysis plan, or source export produced those values.

## New entrypoint

`research/egc2/analyze_lineage_checked_paired_sensitivity.py` accepts only the locked artifact defined by `paired_analysis_input.v0.1.schema.json` and validated by `validate_paired_analysis_input.py`.

It requires:

- valid record-level commitments;
- valid dataset-level commitment;
- complete A/B pairing for every participant;
- disposition-score consistency;
- zero unresolved adequacy decisions;
- agreement between validated participant count and converted pair count;
- agreement between the validated input digest and the pair-conversion digest;
- agreement with an independently supplied expected digest when one is provided;
- agreement between the frozen participant count and the sensitivity-engine output.

## Independent expected digest

Internal self-consistency is insufficient when an entirely different but internally valid input artifact could be substituted.

The optional `--expected-input-digest` argument therefore supports an independently frozen commitment from a preregistration, launch record, registry, or witnessed analysis plan. A redigested replacement dataset will fail when it no longer matches that prior commitment.

This is tamper evidence, not authentication. It does not prove who created the source export, whether the timestamps are trustworthy, or whether the scientific records are correct.

## Final report lineage

The final report preserves:

- study ID;
- analysis-plan ID;
- source-export digest;
- exact analysis-input digest;
- analysis lock timestamp and condition order;
- retained, suppressed, unresolved, record, and participant counts;
- pair-conversion schema version;
- sensitivity-engine schema version;
- lower-level engine digest;
- the complete sensitivity analysis;
- a final report digest.

The analysis-input digest is therefore part of the scientific result rather than an external bookkeeping note.

## Fail-closed conditions

Analysis is blocked when:

- any adequacy decision remains unresolved;
- the declared and recomputed input digests differ;
- an independently expected digest differs;
- pair conversion does not echo the validated digest;
- conversion and validation participant counts differ;
- duplicate or malformed converted participants appear;
- the sensitivity engine reports a different participant count;
- the lower-level engine omits a valid analysis digest.

## Validation

Focused isolated validation produced:

```text
8 tests passed
0 tests failed
py_compile passed
```

The tests include an adversarial case where a participant score, its record digest, and the complete dataset digest are all recomputed. The altered artifact still fails when compared with the independently frozen expected digest.

Direct cloning of the full repository remained unavailable because the runtime could not resolve `github.com`. The focused validation used interface-compatible local copies of the committed dependency APIs. Repository-wide CI and full committed-module execution are therefore not claimed.

## Supported claims

- The paired sensitivity analysis can be bound to one exact internally validated input artifact.
- A substituted but redigested artifact can be rejected against a prior expected commitment.
- Unresolved adequacy decisions can be prevented from entering analysis through implicit recoding.
- Participant-count drift between validation, conversion, and analysis can be detected.

## Unsupported claims

- Source-record authenticity.
- Trusted timestamps or reviewer identity.
- Reliability of adequacy decisions.
- Identification of suppressed scores.
- Validity of semantic fidelity.
- Validation of EGC.
- Any inference about hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Create a single preregistered analysis-run manifest that freezes the expected input digest, gamma grid, software commit, Python version, and output location before the first real paired analysis is executed.
