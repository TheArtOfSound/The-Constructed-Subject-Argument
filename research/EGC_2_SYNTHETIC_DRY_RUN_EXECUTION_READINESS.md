# EGC 2.0 Synthetic Dry-Run Execution Readiness Record

**Status:** Blocked — documentation complete, operator and systems unassigned  
**Record:** `research/egc2/expert_reviewer_dry_run_execution_readiness.v0.1.json`  
**Protocol:** `research/egc2/EXPERT_REVIEWER_SYNTHETIC_END_TO_END_DRY_RUN_PROTOCOL.md`  
**Scope:** Synthetic operational testing only; no live reviewer, participant, candidate, payment, tax, anchor, protected mapping, or private-holdout data.

## Purpose

This record creates the control boundary between a written dry-run protocol and an authorized execution. The protocol must not be executed merely because the selected Proton/AWS architecture and evidence validators exist. Execution requires a named pseudonymous operator, accepted ownership, isolated test resources, frozen public-safe aliases, configuration evidence, and completion of every preflight gate.

The record is intentionally blocked. No person is represented as assigned, no cloud account is represented as configured, and no synthetic result is represented as observed.

## Required accountable roles

Before execution, the readiness record must identify and document acceptance by:

1. **Dry-run operator** — configures the isolated resources, executes the frozen sequence, preserves all outcomes, and stops on any mandatory condition.
2. **Delivery owner** — controls the synthetic Proton delivery route and revocation evidence.
3. **Submission-lock owner** — controls the versioned Object Lock submission path and verifies first-valid-version identity.
4. **Audit-evidence owner** — independently verifies required S3 events and CloudTrail log-file integrity.
5. **Private-store owner** — maintains separation of synthetic administration and protected-mapping stores.
6. **Incident authority** — decides whether an incident requires abort, quarantine, or a new frozen run.
7. **Target-reveal authorizer** — confirms that no target reveal is permitted during this synthetic operational test.

One person may hold more than one role only if the resulting concentration is explicitly documented. The audit-evidence owner should not be the sole person who configured every tested control.

## Frozen resource inventory

Only public-safe aliases may appear in the repository. The readiness record requires aliases for:

- the synthetic Proton account and queue folder;
- the isolated AWS test account and region;
- submission, audit, private-administration, and protected-mapping stores;
- the CloudTrail trail;
- test-only KMS keys and IAM-role boundaries.

The public record must never contain account IDs, access-key IDs, credentials, presigned URLs, share links, passwords, KMS material, reviewer identity linkage, protected mappings, constructor targets, or private holdout content.

## Frozen configuration contract

The readiness record carries forward the protocol's prospective controls:

- recipient-specific, view-only Proton delivery with 24-hour expiry and a separately transmitted password;
- S3 versioning and Object Lock enabled before upload;
- Object Lock compliance mode with seven-day retention;
- 15-minute SigV4 presigned `PUT` URL;
- SHA-256 checksum enforcement and blocked public access;
- CloudTrail S3 data events and log-file integrity validation;
- separate audit storage;
- distinct roles and KMS keys for submission, private administration, and protected mappings.

Changing a frozen control requires a new readiness record and new digest. It must not be silently revised after an execution result is visible.

## Preflight gate

Execution remains prohibited until all twelve gates in the machine-readable record are `verified` with evidence:

1. operator assigned and acceptance recorded;
2. all ownership roles assigned;
3. isolated Proton resources named;
4. isolated AWS resources named;
5. versioning and Object Lock configuration evidenced;
6. CloudTrail data events and log validation evidenced;
7. role and KMS separation evidenced;
8. synthetic artifacts generated and digest-frozen;
9. public-artifact leakage scan passed;
10. evidence-reference closure passed;
11. rollback and incident contacts verified;
12. operator attests that no live data or private holdout is used.

`execution_allowed` must remain `false` while any gate is unverified. Documentation paths alone are not evidence that a service was configured.

## Mandatory stop conditions

The operator must abort and preserve the failure if any of the following occurs:

- real reviewer, participant, candidate, contact, payment, or tax data enters the run;
- private holdout material, protected mappings, constructor targets, rationales, anchor identities, or secrets enter public evidence;
- the repository head differs from the frozen execution commit without a new readiness record;
- an operator, ownership assignment, resource alias, or required configuration is missing;
- a queue or submission digest mismatches;
- Object Lock is absent, not in compliance mode, or shorter than frozen;
- mandatory S3 data events or signed CloudTrail validation are unavailable;
- prohibited cross-role access succeeds;
- an incident, deviation, or failed operation cannot be preserved;
- leakage or evidence-closure validation fails.

A stopped run is an operational result. It must not be repaired into a passing run by editing artifacts in place. A correction requires a new run ID and preserved supersession record.

## Evidence paths

The readiness record prospectively fixes public artifact locations for:

- configuration evidence;
- dry-run result;
- leakage-scan report;
- evidence-reference closure report;
- the complete public evidence directory.

These paths are prospective only. Their presence in the readiness record does not imply the files exist or that any control passed.

## Current disposition

The current record is correctly blocked because:

- no operator has accepted responsibility;
- no ownership role is assigned;
- no Proton or AWS test resource exists;
- no cloud configuration evidence exists;
- no synthetic artifact set is frozen;
- no dry run has been executed.

## Claim status

### Supported

- The transition from protocol to execution now has explicit operator, ownership, resource, evidence, and stopping requirements.
- The run cannot be marked ready without all preflight gates being verified.
- The public evidence locations and frozen configuration requirements are prospectively specified.
- Failure preservation and supersession rules are explicit.

### Not supported

- No operator, custodian, or incident authority has accepted a role.
- No Proton or AWS resource has been created or configured.
- No access denial, Object Lock behavior, CloudTrail event, signed log chain, role separation, or deletion behavior has been observed.
- This record does not clear reviewer outreach, compensation, ethics, consent, or live-data gates.
- Nothing in this record validates anchors, semantic fidelity, EGC, hidden intention, awareness, deception, subjectivity, or consciousness.

## Highest-leverage next action

Assign one responsible synthetic-test operator and the independent audit-evidence owner, record their acceptance pseudonymously outside private identity linkage, then create isolated test resources and attach public-safe configuration evidence without beginning the execution sequence.