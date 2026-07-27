# EGC 2.0 — Repository-Attested Paired Analysis Launcher

**Status:** Integrity defect corrected in the production launch boundary; repository-native execution still pending  
**Date:** 2026-07-27  
**Scope:** Preregistered participant-paired adequacy-suppression sensitivity analysis

## Decision

The previous command-line contract accepted `--runtime-repository-commit` from the caller. That checked only whether the supplied string matched the preregistered manifest. It did not prove that the executing working tree was actually at that commit.

A caller could therefore run modified code while supplying the frozen SHA. The resulting report would appear to satisfy the software-commit contract even though the code had changed.

The new production launcher derives the commit and working-tree state from Git. Caller-supplied commit attestation is no longer sufficient for a real run.

## New production boundary

`research/egc2/run_preregistered_paired_analysis.py` now:

1. requires an explicit repository root;
2. verifies the path is inside a Git work tree;
3. verifies the supplied root equals Git's reported top-level directory;
4. derives the full 40-character `HEAD` with `git rev-parse --verify HEAD`;
5. inspects tracked and untracked changes using `git status --porcelain=v1 --untracked-files=all`;
6. refuses execution when the tree is dirty;
7. passes the repository-derived commit into the existing preregistered runtime-contract validator;
8. adds the attestation method, repository root, derived commit, and clean-tree result to the final report;
9. recomputes the final analysis-report digest after attaching the attestation.

The lower-level `analyze_lineage_checked_paired_sensitivity.py` remains useful as an analysis library and engineering test boundary, but a real preregistered run should enter through the repository-attested launcher.

## Fail-closed conditions

The launcher returns a machine-readable failure with `analysis_performed: false` when:

- Git cannot be executed;
- the path is not a Git repository;
- the supplied root is not the repository top level;
- `HEAD` is not a full commit SHA;
- tracked files are modified;
- untracked files are present;
- the derived commit differs from the frozen run manifest;
- any preexisting input-lineage, gamma-grid, Python-version, schema, or output-path contract fails.

Repository-attestation failures currently use the preregistered `software_commit_mismatch` status because no broader repository-state failure status was frozen in the existing manifest vocabulary. A future manifest version may separate `repository_dirty`, `repository_unavailable`, and `software_commit_mismatch`, but that vocabulary must be frozen prospectively.

## Focused tests

`research/egc2/test_run_preregistered_paired_analysis.py` specifies seven focused tests:

1. clean exact repository passes;
2. modified tracked file fails;
3. untracked file fails;
4. nested-directory root fails;
5. non-repository execution fails;
6. malformed or abbreviated `HEAD` fails;
7. unavailable Git executable fails.

The dedicated GitHub Actions workflow now compiles the launcher and runs these tests in addition to the existing runtime-contract and subprocess suites.

## Validation status

The defect is established by direct code inspection: the earlier CLI accepted a caller-provided commit string and passed it directly into the runtime validator. The new launcher removes that trust assumption.

The available GitHub connector committed and re-read repository files, but the available CI-status interface previously returned an empty list and no repository-native test result was available during this run. Therefore:

- no test-pass claim is made;
- no GitHub Actions pass is claimed;
- no real participant analysis was executed;
- the new launcher must remain execution-pending until CI or a repository-capable runtime produces an exact result.

## Claims supported

Supported as code and protocol evidence:

- the prior caller-supplied commit argument was not a repository attestation;
- a production launcher can derive `HEAD` and tree cleanliness from Git;
- modified and untracked files can be specified as fail-closed conditions;
- the final report can bind the repository-derived state into its digest.

## Claims not supported

Not established:

- that the new launcher passes in the complete repository;
- that Git metadata proves the identity of the operator or machine;
- that a clean Git tree proves dependency, interpreter, kernel, locale, or hardware reproducibility;
- that the Git repository itself has not been maliciously constructed;
- correctness of participant data, adequacy decisions, or semantic-fidelity scores;
- validation of EGC, hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Resolve the updated paired-analysis workflow to an exact pass or failure. If it passes, freeze the first real run only through `run_preregistered_paired_analysis.py`; if it fails, preserve the logs and make the smallest evidence-backed repair.
