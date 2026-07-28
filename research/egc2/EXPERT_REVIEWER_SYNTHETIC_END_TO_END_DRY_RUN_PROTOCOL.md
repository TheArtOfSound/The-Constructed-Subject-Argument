# EGC 2.0 Expert Reviewer Synthetic End-to-End Dry-Run Protocol

**Status:** Ready for public-safe execution after an operator and test AWS/Proton accounts are assigned  
**Date:** 2026-07-28  
**System selection:** `EXPERT_REVIEWER_OPERATIONAL_SYSTEM_SELECTION_MATRIX.md`  
**Live-data prohibition:** This protocol must use synthetic identities, synthetic queue content, and synthetic submissions only.

## 1. Purpose

Test whether the selected operational stack can satisfy the frozen queue-delivery, submission-locking, public/private separation, and audit requirements before any real reviewer is contacted or any live reviewer identity is collected.

This is an operational systems test. It is not an expert review, rater pilot, anchor validation, EGC result, or evidence about consciousness, hidden intention, or subjectivity.

## 2. Target constructs

The dry run tests four operational constructs:

1. **Delivery integrity:** the retrieved queue is byte-identical to the frozen synthetic queue.
2. **Access containment:** only the intended synthetic access path retrieves the queue during the allowed window.
3. **Submission immutability:** the first accepted synthetic submission object version cannot be overwritten or permanently deleted during retention.
4. **Audit completeness:** the required delivery, upload, read, denial, and lock events can be located and their logs pass integrity validation.

## 3. Competing hypotheses

### H1 — Operational contract satisfied

The stack produces a complete evidence chain with correct digests, access expiration, immutable object-version retention, role separation, and verifiable audit events.

### H0-A — Delivery failure

The queue is unavailable, altered, accessible through an unintended route, or remains available after revocation/expiration.

### H0-B — Submission-lock failure

The uploaded object is altered, replaced without preserved version evidence, permanently deleted, or lacks the frozen retention metadata.

### H0-C — Audit failure

Required S3 data events are absent, ambiguous, associated with the wrong bucket/key/version, or contained in logs that cannot pass integrity validation.

### H0-D — Separation failure

Private-administration, protected-mapping, or reviewer-facing stores expose fields forbidden by the frozen data-separation specification.

## 4. Synthetic artifacts

Generate locally:

### 4.1 Synthetic queue

`dry-run-queue.json` must contain:

- pseudonym `DRY-R01`;
- 24 opaque item IDs;
- short synthetic prompts and synthetic responses unrelated to the committed anchor bank;
- blank score fields;
- no source anchor IDs;
- no constructor targets;
- no protected mapping;
- no real name, email, payment information, or participant material.

Record:

- byte length;
- SHA-256;
- creation timestamp;
- generator version or manual-construction note.

### 4.2 Protected synthetic mapping

`dry-run-protected-map.json` maps opaque item IDs to synthetic source IDs. It must be stored only in the protected-research store and must not be included in the delivery share.

### 4.3 Private synthetic administration record

`dry-run-private-admin.json` contains only:

- synthetic name `Test Reviewer One`;
- synthetic contact `dry-r01@example.invalid`;
- reviewer pseudonym `DRY-R01`;
- consent-version code;
- payment-status code `not_applicable_synthetic`.

### 4.4 Synthetic submission

`dry-run-submission.json` contains:

- pseudonym `DRY-R01`;
- queue digest;
- 24 completed synthetic review rows;
- lock declaration;
- pair-recognition fields;
- no constructor targets or protected source IDs.

Record its SHA-256 before upload.

## 5. Pre-run freeze record

Before configuring links or upload URLs, create a public-safe freeze record containing:

- dry-run ID;
- repository commit;
- selected system versions or service configuration timestamps;
- synthetic artifact digests;
- bucket aliases, not globally identifying account details;
- region;
- Object Lock mode and retention duration;
- CloudTrail trail alias;
- CloudTrail integrity-validation enabled status;
- intended event set;
- expected failure statuses;
- operator pseudonym;
- start and stop conditions.

The freeze record must not contain:

- AWS account ID;
- access key IDs;
- presigned URLs;
- Proton credentials;
- share passwords;
- KMS key material;
- private identity linkage;
- protected mapping content.

## 6. Required configuration

### 6.1 Delivery

- upload the frozen synthetic queue to Proton Drive;
- share by synthetic recipient email where technically possible;
- set view-only permission;
- set 24-hour expiration;
- set a strong dry-run password;
- record the share configuration without recording the secret or link in the public repository;
- transmit the password through a separate synthetic channel;
- verify access from a clean browser session;
- revoke access after successful retrieval rather than waiting for expiration.

### 6.2 Submission bucket

- enable versioning;
- enable Object Lock;
- configure default compliance-mode retention for seven days;
- enable default encryption, preferably SSE-KMS with a test-only customer-managed key;
- deny public access;
- prohibit bucket listing for the synthetic reviewer path;
- configure the object key before generating the URL;
- generate one SigV4 presigned `PUT` URL with a 15-minute expiry;
- require `application/json` and SHA-256 checksum headers.

### 6.3 Audit

- enable CloudTrail S3 data events for relevant buckets;
- enable log-file integrity validation;
- deliver CloudTrail logs and digest files to a separate audit bucket;
- ensure audit-bucket credentials differ from reviewer-submission credentials;
- record the trail ARN privately and a public-safe trail alias in the dry-run record.

### 6.4 Private and protected stores

- use separate buckets or strongly isolated prefixes with distinct KMS keys and IAM roles;
- deny cross-role access by default;
- write only the corresponding synthetic artifacts;
- test access denial using the wrong role;
- log all access attempts.

## 7. Execution sequence

### Phase A — Freeze and leakage scan

1. Generate all synthetic artifacts.
2. Compute SHA-256 digests.
3. Run the invitation/queue leakage checklist against the synthetic delivery package.
4. Freeze the dry-run record.
5. Confirm that the public repository contains no secret, presigned URL, protected mapping, or private store content.

**Stop condition:** Any prohibited field or secret is found in a public artifact.

### Phase B — Queue delivery

1. Retrieve the queue through the intended Proton route.
2. Record retrieval timestamp privately.
3. Recompute SHA-256 and compare with the frozen digest.
4. Attempt retrieval without the password or intended account.
5. Revoke access.
6. Attempt retrieval after revocation.

**Pass conditions:**

- intended retrieval succeeds;
- digest matches exactly;
- unauthorized route fails;
- post-revocation retrieval fails.

### Phase C — Submission upload

1. Generate the reviewer-specific presigned URL.
2. Upload the exact frozen synthetic submission with required headers.
3. Record response status, S3 version ID, ETag, checksum, retention mode, and retain-until timestamp.
4. Retrieve the exact object version through an administrator read path.
5. Recompute SHA-256.
6. Validate the submission with the committed review-submission validator where compatible.

**Pass conditions:**

- upload succeeds once;
- retrieved bytes match the frozen digest;
- Object Lock metadata show compliance retention;
- source bucket/key/version identity is complete.

### Phase D — Adversarial overwrite and deletion

1. Reuse the same presigned URL after the first upload.
2. Attempt another upload to the same key.
3. Attempt deletion without a version ID.
4. Attempt permanent deletion of the locked version ID.
5. Attempt to shorten retention.
6. Attempt each action using an unauthorized role where applicable.

**Required interpretation:**

- a second version, if technically created, is a preserved failure/supersession artifact and must not replace the first valid version;
- simple delete-marker creation is not equivalent to permanent deletion and must be reported separately;
- permanent deletion of the protected version must fail;
- retention shortening in compliance mode must fail.

### Phase E — Audit reconstruction

Locate and bind:

- queue-share configuration event or equivalent service evidence;
- S3 `PutObject`;
- S3 `GetObject`;
- attempted `DeleteObject` events;
- Object Lock retention metadata queries or changes;
- denied cross-role access;
- KMS operations where available.

Then run CloudTrail log-file integrity validation for the relevant interval.

**Pass conditions:**

- every mandatory S3 event is identifiable by time, principal, bucket, key, and version where supported;
- integrity validation reports the relevant digest/log chain as valid;
- missing events remain explicit failures rather than inferred successes.

### Phase F — Private-store separation and deletion

1. Confirm the private-admin role cannot read the protected mapping or submission.
2. Confirm the protected-research role cannot read private administration.
3. Confirm the submission role cannot list or read either store.
4. Execute the synthetic private-record deletion procedure after its test retention condition.
5. Preserve deletion evidence without preserving the deleted private content publicly.

## 8. Required result artifact

Create `expert_reviewer_synthetic_dry_run_result.v0.1.json` with:

- dry-run ID;
- execution status;
- configuration summary;
- artifact digests;
- delivery results;
- upload and Object Lock results;
- overwrite/deletion test results;
- audit-event inventory;
- CloudTrail validation result;
- role-separation results;
- incident list;
- deviations;
- final disposition;
- claim limits;
- result digest.

Permitted final dispositions:

- `passed_all_frozen_controls`;
- `failed_delivery_integrity`;
- `failed_access_containment`;
- `failed_submission_immutability`;
- `failed_audit_completeness`;
- `failed_log_integrity_validation`;
- `failed_role_separation`;
- `failed_secret_or_metadata_leakage`;
- `incomplete_transient_service_failure`;
- `incomplete_operator_or_configuration_error`.

Multiple failure codes may be recorded. Do not compress multiple failures into one favorable overall label.

## 9. Gate update rule

A successful dry run is necessary but not sufficient for gate verification.

After `passed_all_frozen_controls`, G04–G07 may be reviewed for verification only when:

- the selected live system configuration is materially identical to the tested configuration;
- responsible operators and custodians are assigned;
- retention periods are frozen;
- secrets and identity data remain outside the public repository;
- an ethics/data-use determination approves or does not prohibit the system;
- the exact dry-run result and audit evidence exist.

G02 compensation and G03 ethics/data-use gates remain independent. G09 and G10 require a final actual-send review.

## 10. Falsification conditions

The operational architecture is rejected for live use if:

- any locked submission version is permanently deletable before retention expiry;
- the system cannot distinguish first valid submission from later versions;
- a queue or submission digest mismatch is not detected;
- required audit events are unavailable or unverifiable;
- role separation fails;
- a public artifact exposes a secret, private identity, protected mapping, or target information;
- a failed operation can be silently repaired without a new preserved artifact;
- the live configuration would differ materially from the passed synthetic configuration.

## 11. Claims discipline

### Supported if the dry run passes

Only that the tested synthetic workflow satisfied the enumerated operational controls under one recorded configuration.

### Not supported even if the dry run passes

- reviewer identity authenticity;
- legal or ethics approval;
- compensation fairness;
- human reviewer independence;
- anchor validity;
- semantic-fidelity reliability;
- EGC validity;
- inference about hidden intention, subjectivity, awareness, deception, or consciousness.

## 12. Current status

No system has been configured under this protocol. No dry run has been executed. No gate is cleared by this document.
