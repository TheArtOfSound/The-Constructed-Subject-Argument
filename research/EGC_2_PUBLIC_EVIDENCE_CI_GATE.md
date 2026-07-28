# EGC 2.0 Public Evidence CI Integration Gate

**Status:** committed; first repository-native execution unresolved  
**Scope:** synthetic expert-review dry-run evidence only  
**Scientific status:** no empirical measurement or cloud-control validation

## Purpose

The public-artifact leakage scanner and evidence-reference closure validator were previously validated in focused temporary-filesystem tests, but they were not exercised together through a repository-native workflow. This gate adds a deterministic public-safe fixture and runs both validation boundaries through their production command-line interfaces.

## Components

- `research/egc2/build_public_evidence_ci_fixture.py`
- `research/egc2/test_public_evidence_ci_integration.py`
- `.github/workflows/egc-public-evidence-contract.yml`

The fixture contains exactly two synthetic evidence files:

1. a JSON delivery-control placeholder;
2. a text audit-control placeholder.

Both state explicitly that they are repository integration fixtures and that no external service or event was observed. The fixture contains no reviewer identity, contact information, cloud credential, bearer link, protected mapping, anchor content, score target, private holdout material, or scientific observation.

## Required passing behavior

The clean fixture must:

1. produce `passed_no_detected_leakage` with zero findings;
2. produce `passed_evidence_reference_closure` with zero errors;
3. have equal declared, referenced, and discovered evidence-file counts;
4. pass through both production CLIs, not only imported Python functions.

## Adversarial integration checks

The integration suite also requires:

- a clean but undeclared extra evidence file to pass the pattern scanner but fail reference closure;
- a forbidden nested identity field to fail the leakage scanner and closure gate even after the evidence digest, configuration digest, and result linkage are recomputed.

This distinguishes two independent controls:

- **content admissibility** — whether a public artifact contains detected protected material;
- **set closure** — whether every public artifact is declared, referenced, present, unique, and digest-bound.

Passing one control does not substitute for passing the other.

## Workflow contract

The focused workflow uses Python 3.12 and performs:

1. `py_compile` on the fixture builder, both validators, and all focused tests;
2. the existing leakage-scanner unit suite;
3. the existing closure-validator unit suite;
4. the new end-to-end integration suite;
5. production-CLI execution on a fresh temporary fixture;
6. explicit assertion of the two passing statuses and zero findings/errors.

The temporary fixture is deleted at job exit. No synthetic output is committed by the workflow.

## Evidence status

At the time of this document, the new workflow and integration files are committed, but the available GitHub status interfaces returned no workflow run or completed status for the workflow commit. An empty status response is neither a pass nor a failure.

Therefore the accurate engineering state is:

```text
public_evidence_ci_gate_committed_execution_pending
```

## Supported claims

- The repository now contains a focused, deterministic integration path for the leakage and closure gates.
- The fixture generator is explicitly synthetic and public-safe by construction.
- The workflow specifies both function-level and production-CLI validation.
- Extra clean files and redigested leakage are treated as distinct adversarial failure modes.

## Not supported

- The workflow has not yet been observed to pass.
- No Proton or AWS resource has been configured or tested.
- The fixture does not authenticate cloud configuration, event provenance, timestamps, reviewer identity, or access control.
- A future clean scan cannot prove absence of all secrets, encoded disclosure, or novel credential formats.
- No anchor, scoring rubric, semantic-fidelity construct, EGC hypothesis, hidden intention, subjectivity, awareness, deception, or consciousness claim is validated.

## Falsification and repair rule

If the first workflow run fails, preserve the exact failing assertion or command output. Repair only the smallest demonstrated defect. Do not weaken either validator, broaden safe exceptions to make the fixture pass, or reinterpret a missing workflow result as success.
