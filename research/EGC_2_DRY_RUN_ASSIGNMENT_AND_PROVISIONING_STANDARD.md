# EGC 2.0 Synthetic Dry-Run Assignment and Provisioning Standard

**Status:** prospective operational control; no personnel assigned and no resources provisioned  
**Machine-readable record:** `research/egc2/expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json`  
**Related readiness record:** `research/egc2/expert_reviewer_dry_run_execution_readiness.v0.1.json`

## Purpose

The existing readiness record correctly blocks execution, but its null assignment and resource fields do not specify what evidence is sufficient to populate them. This standard closes that procedural gap without assigning nonexistent personnel, creating cloud resources, or changing `execution_allowed=false`.

It defines the minimum public-safe evidence required for:

1. accountable operator acceptance;
2. independent audit-evidence review;
3. acceptance of six ownership roles;
4. isolated Proton and AWS resource provisioning;
5. Object Lock, CloudTrail, role-separation, and KMS controls;
6. a frozen synthetic artifact set;
7. one-to-one linkage to readiness gates P01–P12.

## Evidence principle

A name, alias, checkbox, or self-assertion is not evidence that a control exists. Each accepted assignment requires a pseudonym, UTC acceptance timestamp, and public-safe evidence path. Each provisioned resource requires a non-secret alias and evidence demonstrating the relevant configuration.

The public record must never contain credentials, direct account identifiers, personal contact information, bearer links, protected reviewer mappings, constructor targets, rationales, anchor identities, or private holdout content.

## Assignment boundary

### Primary operator

The operator must attest that they:

- read the frozen protocol;
- accept every mandatory stop condition;
- will use synthetic data only;
- will not access the private QEIB holdout;
- will preserve failures, incidents, and deviations;
- will publish only evidence that has passed leakage scanning.

An operator assignment is incomplete until the public-safe record contains a pseudonym, acceptance timestamp, and evidence path.

### Independent audit-evidence reviewer

The reviewer must be distinct from the primary operator and must not generate the evidence they review. Their task is control verification, not scientific adjudication. They must record `pass`, `fail`, or `unresolved` for each frozen gate and preserve disagreements rather than converting them into a pass.

The reviewer must not receive private holdout material. Independence here is procedural separation for the synthetic operations test; it is not a claim of institutional independence or conflict-of-interest clearance.

### Ownership roles

The six roles are delivery owner, submission-lock owner, audit-evidence owner, private-store owner, incident authority, and target-reveal authorizer. One person may hold more than one role only when the tested separation controls remain meaningful and the operator cannot self-approve independent review.

## Provisioning evidence requirements

### Proton controls

Public evidence must establish an isolated synthetic-test account, a recipient-specific view-only queue, 24-hour expiration, and separate-channel password handling. The evidence must redact the account address, recipient identity, share URL, password, and recovery information.

### AWS controls

Public evidence must establish an isolated synthetic-test account and region; a submission bucket with versioning, Object Lock in `COMPLIANCE` mode, at least seven days of retention, and public-access blocking; an audit destination with S3 data events and log-file validation; and role/KMS separation with at least one recorded prohibited cross-role denial.

Evidence must not expose account IDs, ARNs, bucket names, key IDs, access keys, session tokens, or presigned URLs. Public aliases are sufficient for cross-document reference only when the underlying redacted evidence demonstrates the control.

### Private stores

The private administration store and protected-mapping store must remain distinct from public evidence storage. No protected mapping, constructor target, rationale, anchor identity, or private holdout material may appear in a public artifact.

### Synthetic artifact freeze

The source-artifact inventory must be synthetic, bound to a repository commit, and digest-addressed with SHA-256. A statement of synthetic use is required but is not sufficient by itself: the public inventory, leakage report, and evidence-closure report must agree.

## Mapping to readiness gates

| Gate | Required evidence source |
|---|---|
| P01 | Operator acceptance record |
| P02 | Acceptance evidence for all six ownership roles |
| P03 | Proton account and queue controls R01–R02 |
| P04 | AWS controls R03–R07 |
| P05 | Submission-bucket versioning and Object Lock R04 |
| P06 | CloudTrail data events and log validation R05 |
| P07 | Role and KMS separation R06 |
| P08 | Synthetic artifact freeze R08 |
| P09 | Final public-artifact leakage report |
| P10 | Final evidence-reference closure report |
| P11 | Incident-authority acceptance and rollback procedure |
| P12 | Operator no-live-data and no-private-holdout attestation |

## Fail-closed completion rule

Any missing acceptance, unresolved review, absent resource evidence, contradictory configuration, leakage finding, or closure error keeps the run blocked. Recomputing hashes around an unsupported assertion does not convert it into evidence.

A completed assignment/provisioning record would establish only that named operational prerequisites were documented under one configuration. It would not authenticate consciousness-related constructs, reviewer psychology, semantic fidelity, hidden intention, awareness, deception, subjectivity, or consciousness.

## Current result

The new record deliberately preserves the null result:

- operator: unassigned;
- independent reviewer: unassigned;
- ownership roles: unassigned;
- Proton resources: not provisioned;
- AWS resources: not provisioned;
- synthetic artifacts: not frozen;
- execution: prohibited.

This is progress in procedural identifiability, not evidence that the dry run can begin.
