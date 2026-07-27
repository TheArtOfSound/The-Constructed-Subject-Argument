# EGC 2.0 Preregistered Paired-Analysis Run Manifest

**Status:** Run-freeze control implemented and focused validation passed.  
**Scope:** Primary lineage-checked paired adequacy-suppression sensitivity analysis.  
**Non-claim:** This control does not validate semantic-fidelity scores, adequacy decisions, missingness assumptions, EGC, hidden intention, subjectivity, or consciousness.

## Decision

A real paired analysis must not begin from a command assembled at execution time. Before access to the locked participant-condition input, one machine-readable run manifest must freeze:

- independently committed expected input digest;
- gamma sensitivity grid;
- repository commit;
- Python version;
- entrypoint schema and path;
- output path and no-overwrite rule;
- permitted fail-closed statuses;
- lock time and operator identity.

The manifest itself receives a canonical SHA-256 digest. Execution should additionally compare it against a digest stored independently of the analysis workspace. This catches a substituted manifest even when every internal digest has been recomputed.

## Files

- `research/egc2/validate_paired_analysis_run_manifest.py`
- `research/egc2/test_validate_paired_analysis_run_manifest.py`
- `research/egc2/paired_analysis_run_manifest.v0.1.schema.json`
- `research/egc2/results/paired_analysis_run_manifest_validation.v0.1.json`

## Fail-closed contract

The validator rejects:

1. an input digest that is not a canonical SHA-256 value;
2. a gamma grid that is unordered, duplicated, outside the 1–7 scale width, or omits `0.0` and `6.0`;
3. a repository commit that is not a full 40-character SHA;
4. an unrecognized Python or entrypoint version;
5. an output outside `research/egc2/results/`, path traversal, or overwrite permission;
6. unknown or missing mandatory failure statuses;
7. a lock made after input access or one allowing post-lock parameter mutation;
8. an internal manifest digest mismatch;
9. disagreement with an independently frozen expected manifest digest.

## Permitted failure semantics

A run must terminate without a scientific result when a declared invariant fails. Mandatory statuses include `input_digest_mismatch`, `input_lineage_invalid`, and `report_digest_failure`. Other permitted failures distinguish software, runtime, count, schema, parameter, output, and unresolved-adequacy failures. An unexpected failure status is itself invalid; it cannot be converted into a successful run after inspection.

## Focused validation

Executed in an isolated Python runtime:

```text
10 tests passed
0 tests failed
py_compile passed
```

The key adversarial test modifies the gamma grid, recomputes the complete manifest digest, and confirms that the altered manifest still fails against the independently frozen expected digest.

## Unresolved uncertainty

- The independently frozen digest must exist outside the mutable analysis workspace.
- A SHA-256 commitment does not authenticate the operator, timestamp, source records, or software environment.
- Python-version equality does not guarantee full dependency or operating-system equivalence.
- No real participant input exists, so no live run manifest has been frozen.
- The confirmatory entrypoint has not yet been modified to require this manifest at runtime.

## Highest-leverage next action

Make the lineage-checked paired-sensitivity entrypoint require a validated run manifest and reject any runtime input digest, gamma grid, software commit, Python version, entrypoint schema, or output path that differs from the frozen contract.