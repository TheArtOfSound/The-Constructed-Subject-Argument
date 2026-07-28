# EGC 2.0 Synthetic Dry-Run Readiness Consistency Gate

## Purpose

The execution-readiness record is a prospective authorization boundary, not an operational result. A digest-valid JSON file could still be internally contradictory—for example, marking execution as allowed while the operator is unassigned, ownership roles are empty, resources are unnamed, or preflight gates lack evidence.

`research/egc2/validate_dry_run_execution_readiness.py` therefore validates both content integrity and cross-field authorization logic before any Proton/AWS synthetic dry run may be treated as ready.

## Valid blocked state

The committed readiness record is intentionally blocked. It is valid because:

- `synthetic_only` and `live_data_prohibited` are true;
- `status` is `blocked` and `execution_allowed` is false;
- the operator and ownership roles are explicitly unassigned;
- resource aliases and configuration evidence are absent;
- all twelve preflight gates remain `not_verified`;
- explicit blockers are preserved;
- the declared canonical SHA-256 digest matches recomputation.

Acceptance of this blocked state does not clear any execution or reviewer-outreach gate.

## Unlock requirements

An execution-enabled record is valid only when all of the following are simultaneously true:

1. status is `ready` and `execution_allowed` is true;
2. an operator pseudonym and acceptance timestamp are present with `acceptance_status = accepted`;
3. all six ownership roles are assigned;
4. all required Proton/AWS resource aliases are present;
5. at least two distinct KMS aliases and resource-creation evidence paths are present;
6. all twelve preflight gates are `verified` and each carries at least one evidence reference;
7. gate labels are consistent with the underlying operator, ownership, and resource fields;
8. a separate independent-review attestation is complete;
9. no current blocker remains;
10. the record digest and, when supplied, the independently frozen repository-head commitment match.

The independent-review object is required only for an execution-enabled record. It must contain a verified status, reviewer pseudonym, review timestamp, and evidence references. This closes a gap in the prose unlock rule, which required independent review but did not previously specify its machine-checkable minimum fields.

## Fail-closed conditions

The validator rejects:

- record-digest mismatch;
- repository-head substitution against an independently supplied expected SHA;
- false or missing synthetic-only/live-data prohibitions;
- accepted operators without pseudonym and timestamp;
- acceptance data attached to an unaccepted operator;
- duplicate, missing, renamed, unknown, waived, or evidence-free preflight gates;
- verified gates that contradict underlying record fields;
- duplicate KMS aliases;
- drift in the frozen unlock rule;
- `execution_allowed = true` without complete prerequisites or independent review;
- ready records that retain blockers;
- blocked records that conceal all blockers.

The validator emits a deterministic, digest-bound validation report and exits nonzero on inconsistency.

## Validation performed

Focused execution used the committed readiness-record content:

```text
python -m unittest -v test_validate_dry_run_execution_readiness.py
python -m py_compile validate_dry_run_execution_readiness.py test_validate_dry_run_execution_readiness.py
```

Result:

```text
10 tests passed
0 tests failed
Python compilation passed
```

Adversarial tests covered undigested tampering, fully redigested false unlocks, evidence-free verified gates, contradictory operator-gate claims, duplicate gates, acceptance-data inconsistency, independent repository-head substitution, deterministic reports, and a complete synthetic ready-state fixture.

The committed blocked record validated with zero errors and zero warnings. Validation-report digest:

```text
54037ef4ae9f363e566e08d90577a8cee843baaf170f7988573dd4e01575852c
```

This is software-validation evidence only. It does not show that an operator, resource, access control, Object Lock rule, CloudTrail event, reviewer, or scientific measurement exists.

## Claim boundary

Supported:

- internally inconsistent readiness records can be rejected;
- a redigested false unlock cannot bypass cross-field checks;
- the currently blocked record is digest-valid and logically blocked;
- independent review is now a machine-checkable prerequisite for an execution-enabled state.

Not supported:

- authenticity of identities, timestamps, evidence references, cloud resources, or repository execution environment;
- completeness of the readiness model against every operational failure;
- successful Proton/AWS configuration or dry-run execution;
- validation of the anchor bank, semantic-fidelity construct, EGC, hidden intention, awareness, deception, subjectivity, or consciousness.
