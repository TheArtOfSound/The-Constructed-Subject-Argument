# EGC 2.0 — Exclusive Report Creation Audit

**Status:** Focused launcher hardening complete; repository-native suite still pending  
**Date:** 2026-07-27  
**Scope:** Final filesystem write for preregistered paired sensitivity reports

## Decision

The preregistered launcher previously checked `output_target.exists()` and then called `Path.write_text()`. Those are separate filesystem operations. Another process could create or replace the target after the check but before the write, violating the frozen no-overwrite contract.

The launcher now creates the final report with one exclusive kernel operation. The old check-then-write path has been removed.

## Controls added

`atomic_write_report()` now:

1. creates parent directories before the final exclusive operation;
2. opens the target with `O_CREAT | O_EXCL` so an existing path fails atomically;
3. adds `O_NOFOLLOW` when the platform exposes it, rejecting a final-component symlink;
4. creates the report with mode `0600` before ordinary process umask effects;
5. writes UTF-8 with a fixed newline convention;
6. flushes userspace buffers and calls `fsync` on report content;
7. attempts a parent-directory `fsync` for metadata durability;
8. removes the incomplete target if a failure occurs after creation but before completion.

The report records `report_creation_method = exclusive-create-no-overwrite`, and that field is included before the final analysis-report digest is computed.

## Failure behavior

An existing target or final-component symlink produces the preregistered fail-closed status:

```text
output_path_mismatch
```

The prior output is not truncated or replaced.

A storage or write failure after successful creation is surfaced as an execution failure, and the incomplete report is deleted. It is not left behind as a plausible scientific artifact.

## Focused validation

An isolated execution of the exact write logic passed four checks:

- new nested target created with exact content;
- existing target rejected and preserved;
- final-component symlink rejected without altering its target;
- simulated `fsync` failure removed the partial file.

Four corresponding repository tests were added to `research/egc2/test_run_preregistered_paired_analysis.py`.

The committed repository suite and GitHub Actions workflow were not observed running in this cycle. Repository-native execution is therefore not claimed.

## Supported claim

The final report path now enforces the no-overwrite decision atomically at file creation, rather than relying on a race-prone precheck.

## Residual limitations

This repair does not provide complete filesystem or host attestation.

It does not prevent:

- a privileged process from replacing ancestor directories during execution;
- hostile mount-namespace changes;
- kernel or storage-layer compromise;
- false Git metadata supplied by a compromised Git executable;
- operator, machine, clock, interpreter, dependency, or source-record impersonation.

A stronger Linux-specific implementation could traverse and open every ancestor using directory file descriptors and `openat`-style no-follow checks. That would reduce ancestor replacement exposure but add platform-specific complexity. It should not be added before the current repository-native suite is executed and before real participant data exist.

## Scientific limits

This is engineering integrity evidence only. It does not validate:

- participant records;
- adequacy decisions;
- semantic-fidelity scores;
- missingness assumptions;
- EGC;
- hidden intention, subjectivity, or consciousness.

## Highest-leverage next action

Execute the complete repository-attested launcher and CLI contract suites in a repository-capable environment and preserve the exact first pass or failure. Further launcher hardening should pause unless that execution reveals a concrete defect or real participant analysis becomes imminent.
