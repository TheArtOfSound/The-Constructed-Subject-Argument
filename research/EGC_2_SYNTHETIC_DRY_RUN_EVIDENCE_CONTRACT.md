# EGC 2.0 Synthetic Dry-Run Evidence Contract

**Status:** Machine-readable contract committed; no cloud dry run executed  
**Date:** 2026-07-28  
**Parent protocol:** `research/egc2/EXPERT_REVIEWER_SYNTHETIC_END_TO_END_DRY_RUN_PROTOCOL.md`

## Decision

The expert-review operational dry run now has two fail-closed JSON Schemas rather than a prose-only result requirement:

1. `research/egc2/expert_reviewer_dry_run_configuration_evidence.v0.1.schema.json`
2. `research/egc2/expert_reviewer_synthetic_dry_run_result.v0.1.schema.json`

The configuration-evidence manifest records the tested Proton/AWS control state before interpreting outcomes. The result schema binds the operational findings, artifact digests, adversarial tests, audit inventory, role-separation checks, incidents, deviations, failure codes, final disposition, and scientific claim limits.

## Weakness closed

The parent protocol defined what must be reported but did not mechanically prevent an operator from:

- omitting a failed control;
- claiming a pass without complete delivery, immutability, and audit evidence;
- recording public evidence paths without digests;
- collapsing multiple failures into a favorable summary;
- omitting incidents or deviations;
- treating an incomplete run as successful;
- removing the explicit prohibition on consciousness, hidden-intention, awareness, deception, or subjectivity inference.

The schemas now reject unknown top-level fields and require the complete evidence structure.

## Configuration evidence contract

The configuration schema requires prospective evidence that:

- Proton Drive delivery is recipient-specific, view-only, password-protected, expiring, and revocable;
- the S3 submission bucket has versioning, Object Lock, compliance retention, encryption, checksum enforcement, short presigned upload expiry, and public-access blocking;
- CloudTrail, S3 data events, signed log validation, and a separate audit store are enabled;
- private administration, protected mapping, and submission stores are separated by roles and encryption keys;
- public evidence contains no account IDs, access keys, presigned URLs, share passwords, KMS material, private identity linkage, or protected mapping content;
- every public-safe evidence file has a path, SHA-256 digest, classification, and synthetic-only declaration.

Documentation alone does not establish that these controls exist. The manifest must reference actual public-safe evidence produced from the configured synthetic environment.

## Result contract

The result schema requires:

- exact repository commit and protocol version;
- synthetic-only attestation;
- configuration-evidence digest;
- digests for queue, submission, protected mapping, private administration record, and freeze record;
- delivery retrieval, unauthorized-access, revocation, and post-revocation outcomes;
- submission version, checksum, compliance retention, deletion, retention-shortening, and first-valid-version outcomes;
- at least six adversarial tests;
- required CloudTrail event inventory and signed-log validation result;
- at least three role-separation checks;
- preserved incidents and deviations;
- explicit failure codes and final disposition;
- a final result digest;
- at least five claim-limit statements, including the mandatory no-consciousness/no-hidden-state inference statement.

## Pass semantics

`passed_all_frozen_controls` is allowed only when:

- execution is complete;
- no failure code exists;
- every delivery control is true;
- the first upload, digest, version, checksum, compliance retention, permanent-deletion denial, retention-shortening denial, and first-version identity checks pass;
- CloudTrail log validation is `valid`;
- every mandatory audit event is identified.

An incomplete or fail-closed execution requires at least one preserved failure code.

## Validation evidence

Both schemas were parsed using Python's standard JSON parser and independently formatted through `python -m json.tool` before commit.

Canonical minified SHA-256 digests:

- result schema: `876a2cafca56882af6e4bdaba726f9eec059411568216a6ba3210066f567a2b9`
- configuration schema: `3976968601e6eb278a525afb5934be9a264d9e9c4791e0e7453a7e4a59016415`

This validates JSON syntax and records exact content commitments. It does not prove full JSON Schema implementation compatibility across validators because no repository-native schema test was executed in this run.

## Claims supported

- The operational dry run now has an explicit machine-readable evidence boundary.
- A successful label cannot be represented without the core frozen delivery, immutability, and audit assertions.
- Incomplete runs require explicit failure evidence.
- Public-safe configuration evidence must be synthetic-only, classified, and digest-bound.
- Scientific claim limits are part of the result object rather than optional prose.

## Claims not supported

- No Proton or AWS resource was configured.
- No synthetic dry run was executed.
- No cloud configuration, access denial, Object Lock behavior, audit event, or log signature was observed.
- No secret-leak validator has yet scanned repository artifacts.
- No invitation launch gate is cleared.
- No anchor, reviewer process, semantic-fidelity measure, EGC hypothesis, hidden intention, subjectivity, awareness, deception, or consciousness claim is validated.

## Highest-leverage next action

Implement a standard-library public-artifact leakage validator that scans the configuration manifest, result artifact, and referenced evidence paths for forbidden keys, credential patterns, presigned URLs, account identifiers, private identity fields, protected mapping content, and target leakage before any dry-run evidence can be committed.