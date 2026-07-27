# EGC 2.0 — Preregistered Paired-Analysis Runtime Enforcement Review

**Status:** Runtime contract enforcement committed; full-repository execution still pending  
**Date:** 2026-07-27  
**Scope:** Confirmatory participant-paired adequacy-suppression sensitivity entrypoint

## Decision

The production paired-sensitivity entrypoint now requires two frozen inputs:

1. a lineage-validated participant-condition artifact; and
2. a validated preregistered run manifest.

The analysis no longer accepts an independently supplied gamma grid or output path as authoritative. The run manifest is the authority, and runtime values must match it exactly.

## Enforced invariants

Before any sensitivity calculation, the entrypoint verifies:

- independently expected run-manifest digest;
- expected participant-input digest;
- repository commit SHA;
- Python version;
- entrypoint schema;
- gamma grid;
- output report path;
- study ID;
- analysis-plan ID;
- overwrite prohibition.

A mismatch terminates without producing a scientific result.

## Declared fail-closed statuses

The entrypoint emits a machine-readable failure artifact using only the frozen failure vocabulary. Relevant statuses include:

- `input_digest_mismatch`;
- `input_lineage_invalid`;
- `unresolved_adequacy_decision`;
- `participant_count_mismatch`;
- `gamma_grid_mismatch`;
- `software_commit_mismatch`;
- `python_version_mismatch`;
- `entrypoint_schema_mismatch`;
- `output_path_mismatch`;
- `analysis_engine_failure`;
- `report_digest_failure`.

Every failure artifact states `analysis_performed: false` and receives its own digest.

## Successful report lineage

A completed report now echoes:

- run ID;
- run-manifest digest;
- participant-input digest;
- repository commit;
- Python version;
- entrypoint schema;
- gamma grid;
- output path;
- sensitivity-engine digest;
- final report digest.

The final digest is recomputed after the run-contract block is added.

## Focused validation

An isolated interface-compatible harness executed five tests:

1. valid frozen runtime acceptance;
2. repository-commit mismatch rejection;
3. output-path mismatch rejection;
4. gamma-grid mismatch rejection;
5. redigested run-manifest substitution rejection against an independent commitment.

Result: **5 passed, 0 failed; `py_compile` passed.**

The committed repository test file was also expanded to cover Python-version mismatch, input substitution, study-identity mismatch, and successful run-contract echoing. That full committed suite was not executed in this run because the available runtime could not resolve `github.com`.

## Claims supported

Supported as focused engineering evidence:

- runtime parameter drift can be blocked before analysis;
- an internally consistent but externally substituted run manifest can be rejected;
- a substituted participant input can be rejected against the frozen expected input digest;
- successful reports can carry the exact preregistered run identity;
- failure can be preserved without creating a partial scientific result.

## Claims not supported

Not established:

- full-repository compatibility;
- CI success;
- authenticity of commit, operator, timestamp, or source records;
- reproducibility across operating systems or unrecorded dependencies;
- correctness of adequacy decisions or retained scores;
- identification of suppressed outcomes;
- validity of semantic fidelity or EGC;
- any conclusion about hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Execute the expanded committed integration suite in a repository-capable environment and preserve the exact pass or failure before any real participant analysis run manifest is frozen.
