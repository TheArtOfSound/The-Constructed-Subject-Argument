# EGC 2.0 — Repository-Bound Output Path Audit

**Status:** Focused integrity repair committed; repository-native execution still pending  
**Date:** 2026-07-27  
**Scope:** Production launcher for preregistered paired adequacy-sensitivity analysis

## Decision

The repository-attested launcher previously verified Git `HEAD` and working-tree cleanliness, but it did not bind the filesystem destination of the report to the attested repository root.

The launcher compared the caller's `--output` string with the preregistered report-path string inside the lower-level runtime validator. A relative path is interpreted against the process working directory, not the declared repository root. In addition, an existing parent-directory symlink can redirect a path that appears to be under `research/egc2/results/` to a target outside the repository.

The production boundary now resolves both the frozen repository-relative target and the requested output before analysis. A run fails closed unless both resolve to the same path and that path remains inside the attested repository root.

## Defect

The prior launcher used:

```python
runtime_output = args.output.as_posix()
```

and later wrote directly to `args.output`.

This permitted two classes of ambiguity:

1. **Working-directory redirection** — the string `research/egc2/results/run.json` could identify different files depending on the process working directory.
2. **Parent-symlink escape** — an existing `research/egc2/results` symlink could redirect the write outside the repository while preserving the expected-looking path string.

The manifest validator already prohibited absolute paths and lexical `..` traversal. That was necessary but not sufficient because lexical validation does not resolve filesystem aliases.

## Repair

`research/egc2/run_preregistered_paired_analysis.py` now provides:

```python
resolve_output_target(repository_root, frozen_report_path, requested_output)
```

The function:

1. resolves the attested repository root;
2. rejects absolute or lexically traversing frozen paths;
3. resolves the frozen path against the repository root;
4. resolves the requested output independently;
5. verifies the frozen target remains inside the repository after symlink resolution;
6. requires exact equality between the resolved requested and frozen targets;
7. returns the frozen POSIX path as the value passed to the preregistered runtime validator;
8. writes only to the resolved repository-bound target.

The final report now records both:

- `frozen_output_path`;
- `resolved_output_target`.

Both fields are incorporated into the final analysis-report digest.

## Validation

Five repository tests were added to the existing launcher suite:

1. exact repository target acceptance;
2. rejection of the same relative-looking path rooted in another directory;
3. rejection of an absolute frozen path;
4. rejection of lexical traversal;
5. rejection of an existing parent symlink that resolves outside the repository.

A focused isolated check of the new path-binding function was executed with standard-library temporary directories and a stubbed lower-level contract exception:

- exact target accepted;
- alternate-root target rejected;
- symlink escape rejected;
- Python compilation of the isolated revised module passed.

The full committed repository suite and GitHub Actions workflow are not claimed as passed because the available commit-status interface still returned no completed status and the repository was not available as a local checkout in this runtime.

## Claims supported

Supported as code-inspection and focused engineering evidence:

- lexical output-path validation alone did not bind a report to the attested repository;
- relative working-directory ambiguity can be blocked by resolved-path equality;
- an existing parent-symlink escape can be detected before analysis;
- the final report can preserve both the frozen logical path and resolved physical target.

## Claims not supported

Not established:

- complete repository compatibility;
- GitHub Actions success;
- protection against a malicious operating system, filesystem, privileged process, or race after validation;
- trusted timestamping or operator authentication;
- correctness of participant records, adequacy decisions, semantic-fidelity scores, or missingness assumptions;
- validation of EGC, hidden intention, subjectivity, or consciousness.

## Residual race

The launcher checks and then writes. A privileged or concurrent actor could theoretically alter filesystem structure after validation and before the write. The current repair addresses ordinary path ambiguity and pre-existing symlink redirection, not adversarial operating-system compromise. A later hardened implementation could use directory file descriptors and no-follow semantics where cross-platform support is acceptable.

## Claim status

```text
measurement_process_not_yet_empirically_validated
uncertainty_method_not_validated_for_confirmatory_EGC_inference
repository_output_path_binding_committed_execution_pending
```

## Highest-leverage next action

Execute the complete repository-attested launcher suite and CLI contract workflow in a repository-capable environment, preserving the exact pass or first failure before freezing a real participant analysis run manifest.
