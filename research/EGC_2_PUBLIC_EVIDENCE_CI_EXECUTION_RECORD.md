# EGC Public Evidence Contract — Repository-Native Execution Record

**Status:** focused workflow passed  
**Execution date:** 2026-07-28  
**Pull request:** #9  
**Tested commit:** `5d0b94d786ac70eed8f6a41c6037c0839c6fb642`

## Purpose

This record resolves the previously unobserved execution status of the focused public-evidence contract workflow. It concerns repository plumbing only: public-artifact leakage detection, exact evidence-reference closure, deterministic synthetic fixture construction, and production-CLI integration. It is not evidence about an external cloud system, a reviewer, an anchor, semantic fidelity, EGC, or any internal state of an AI system.

## Observed workflow result

GitHub Actions workflow:

- Name: `EGC public evidence contract`
- Run ID: `30369156143`
- Run number: `3`
- Head branch: `gpt/public-evidence-ci-log-evidence`
- Head SHA: `5d0b94d786ac70eed8f6a41c6037c0839c6fb642`
- Final status: `completed`
- Conclusion: `success`

The single job, `validate-public-evidence-contract`, completed successfully. Every recorded step passed:

1. repository checkout;
2. Python 3.12 setup;
3. validation-log directory creation;
4. module compilation;
5. focused unit and integration tests;
6. production leakage and closure CLI execution on a fresh public-safe fixture;
7. workflow provenance recording;
8. validation-log artifact upload.

## Preserved validation evidence

Artifact:

- Name: `egc-public-evidence-validation-30369156143-1`
- Artifact ID: `8692090450`
- Size: `1,945` bytes
- Created: `2026-07-28T14:36:06Z`
- Expires: `2026-08-27T14:36:06Z`
- Digest: `sha256:5b17f60aee20b4b5e0c84bc9024c4e9be65d4faa8feaaf512ad1d59e38ef8a21`

The workflow change preserves compilation, test, production-CLI, and provenance logs on both success and failure. `pipefail` remains enabled where output is piped through `tee`, so log capture cannot convert a failed command into a passing step.

## Supported findings

- The focused modules compile under the workflow's Python 3.12 environment.
- The committed leakage-scanner, closure-validator, and end-to-end integration suites pass together in one repository-native run.
- The production command-line entrypoints accept the deterministic clean fixture and satisfy the explicit success assertions.
- The workflow can preserve digest-addressed execution logs tied to the tested commit.

## Limits and unresolved uncertainty

This result does **not** establish:

- completeness of the leakage detector against every possible secret or encoded disclosure;
- authenticity or adequacy of future AWS, Proton, reviewer, timestamp, access-control, or event evidence;
- cross-platform equivalence outside the tested GitHub Actions environment;
- correctness of a future live evidence bundle;
- validity of any anchor, rubric, semantic-fidelity construct, EGC hypothesis, hidden intention, awareness, deception, subjectivity, or consciousness claim.

The broader `Research integrity checks` workflow triggered by PR #9 is tracked separately. Its result must not be conflated with the focused workflow result.

## Claim status

`public_evidence_repository_native_contract_passed`

The next operational dependency is no longer CI observability. It is execution of the frozen synthetic cloud dry-run protocol in isolated test resources, with every public evidence artifact admitted only through the now-passing leakage and closure gates.
