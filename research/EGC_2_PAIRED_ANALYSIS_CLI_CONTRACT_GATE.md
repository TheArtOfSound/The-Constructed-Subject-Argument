# EGC 2.0 — Paired Analysis CLI Contract Gate

**Status:** Repository-native end-to-end test and CI gate committed; execution result pending  
**Date:** 2026-07-27  
**Scope:** Preregistered, lineage-checked participant-paired adequacy sensitivity analysis

## Decision

The function-level runtime tests were not sufficient to establish that the production command-line entrypoint behaves correctly at the filesystem boundary.

A confirmatory analysis can fail even when its pure Python functions are correct. Relevant failure modes include:

- the CLI accepting the wrong manifest or participant artifact;
- a mismatch between the frozen output path and the actual path supplied;
- overwriting a preexisting report;
- returning a partial report after a contract violation;
- printing an unstructured exception rather than a preserved failure artifact;
- failing to clean synthetic test outputs;
- reporting a success digest that does not match the written report.

The repository now contains a subprocess-level contract test and a dedicated GitHub Actions workflow. Live participant analysis remains blocked until this gate has a preserved pass or an explicit failure is repaired and rerun.

## Added gate

`research/egc2/test_paired_analysis_cli_contract.py` invokes the actual production entrypoint through `subprocess.run` from the repository root.

It uses synthetic, internally digested participant records and a synthetic preregistered run manifest. These fixtures test software behavior only and are not EGC observations.

The test covers six command-line outcomes:

1. **Successful run**
   - exits with code `0`;
   - writes the frozen output path;
   - echoes the frozen participant-input digest;
   - echoes the frozen run-manifest digest;
   - prints the same final report digest stored in the report.

2. **Preexisting output**
   - exits with code `2`;
   - returns `output_path_mismatch`;
   - records `analysis_performed: false`;
   - preserves the preexisting file byte-for-byte;
   - does not overwrite it with a report.

3. **Repository commit mismatch**
   - exits with code `2`;
   - returns `software_commit_mismatch`;
   - creates no scientific output.

4. **Independent manifest commitment mismatch**
   - exits with code `2`;
   - returns `input_lineage_invalid`;
   - creates no scientific output.

5. **Fully redigested participant-input substitution**
   - alters a retained score;
   - recomputes the record digest;
   - recomputes the dataset digest;
   - still fails against the manifest's frozen expected input digest with `input_digest_mismatch`.

6. **Malformed participant input**
   - exits with code `2`;
   - returns a machine-readable `input_lineage_invalid` artifact;
   - creates no scientific output.

Every failure artifact is required to contain a 64-character failure digest and `analysis_performed: false`.

## Continuous integration

`.github/workflows/egc-paired-analysis-cli-contract.yml` runs on relevant pushes, pull requests, and manual dispatch.

The workflow:

- installs Python 3.12;
- compiles the paired-analysis implementation and tests;
- runs the existing function-level runtime-contract suite;
- runs the new subprocess CLI suite;
- fails if a synthetic `.cli-contract-*.json` output remains in `research/egc2/results/`.

The workflow has read-only repository permissions and a ten-minute timeout.

## Validation status

The files were inspected and committed through the GitHub connector. Direct repository cloning and local execution failed because the available runtime could not resolve `github.com`.

Therefore, this run does **not** claim:

- that the new tests pass;
- that the workflow passes;
- that Python 3.12 matches a future frozen production runtime;
- that all operating-system or filesystem failures are covered;
- that the production CLI is validated for real participant data.

The correct current status is:

```text
repository_native_cli_contract_committed_execution_pending
```

A failing workflow is a useful result and must be preserved. The test or implementation should be corrected only after the exact failure is recorded.

## Claims supported

Supported as repository engineering:

- the actual CLI boundary now has a committed end-to-end test specification;
- success, non-overwrite behavior, redigested substitution, and machine-readable failure handling are testable in one repository-native environment;
- future changes to the paired-analysis entrypoint or its lineage dependencies can trigger the gate automatically;
- synthetic output leakage can cause CI failure.

## Claims not supported

Not established:

- that the committed test suite currently passes;
- that GitHub Actions reproduces a future real analysis environment;
- that digests authenticate operators, timestamps, source records, or commits;
- that adequacy decisions or semantic-fidelity scores are correct;
- that suppressed outcomes are identified;
- that semantic fidelity or EGC is validated;
- any conclusion about hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Resolve the first GitHub Actions run to a preserved pass or explicit failure. No real paired-analysis run manifest should be frozen until the repository-native CLI contract gate passes on the exact committed code.
