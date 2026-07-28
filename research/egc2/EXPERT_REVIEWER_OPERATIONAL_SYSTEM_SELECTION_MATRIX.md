# EGC 2.0 Expert Reviewer Operational System Selection Matrix

**Status:** Provisional architecture selection for synthetic dry-run only  
**Date:** 2026-07-28  
**Scope:** Delivery of blinded review queues, immutable submission capture, private administration, and audit/timestamp evidence  
**Launch effect:** None. This document does not clear any invitation or live-review gate.

## Decision

Use a **hybrid Proton Drive + AWS evidence stack** for the first public-safe synthetic dry run:

1. **Reviewer queue delivery:** Proton Drive email-specific, view-only share, with expiration and a separately transmitted password.
2. **Submission capture:** Amazon S3 reviewer-specific presigned `PUT` URL to a unique object key in a versioned, Object-Lock-enabled bucket.
3. **Submission immutability:** S3 Object Lock in **compliance mode** for the frozen retention period after upload.
4. **Object integrity:** SHA-256 checksum required at upload and independently recomputed after retrieval.
5. **Access and event logging:** AWS CloudTrail S3 data events for `PutObject`, `GetObject`, and attempted deletion operations.
6. **Audit-log integrity:** CloudTrail log-file integrity validation enabled, with signed digest files preserved separately.
7. **Private administration:** Separate encrypted private store, initially an isolated S3 bucket using SSE-KMS and a distinct IAM role set; no reviewer queue, score, anchor, or protected source mapping may enter this bucket.
8. **Protected research mappings:** Separate S3 bucket/prefix and KMS key from both reviewer-facing and private-administration stores.

This architecture is selected because no single reviewed consumer service satisfies all frozen requirements for recipient-specific delivery, immutable locked submission, cross-artifact digest binding, object-level audit events, and auditable retention.

## Evidence basis

### Amazon S3

Official AWS documentation states that:

- presigned URLs provide time-limited upload or download access without giving the reviewer AWS credentials;
- Signature Version 4 presigned uploads can include SHA-256 and other checksum headers;
- S3 Object Lock stores object versions using a write-once-read-many model;
- compliance mode prevents a protected object version from being overwritten or deleted by any user, including the AWS account root user, until retention expires;
- Object Lock requires versioning and remains enabled once configured on a bucket;
- CloudTrail S3 data events can record object-level operations including `PutObject`, `GetObject`, and `DeleteObject`;
- CloudTrail log integrity validation uses SHA-256 hashing and RSA-signed digest files to detect modification or deletion of delivered logs.

Primary references:

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html

### Proton Drive

Official Proton documentation states that:

- files, filenames, and folder names are end-to-end encrypted;
- shares can be sent to specific email addresses;
- public links can be password-protected and assigned expiration dates;
- access can be revoked;
- editors can upload into shared folders, but editable sharing does not provide the frozen immutable-submission guarantee.

Primary references:

- https://proton.me/support/drive
- https://proton.me/support/drive-how-to-share-files-via-email
- https://proton.me/support/drive-manage-access-shared-files
- https://proton.me/support/password-protect-files-proton-drive

## Selection matrix

| Requirement | Proton Drive | Google Drive / Forms | Amazon S3 + Object Lock + CloudTrail | Selected role |
|---|---|---|---|---|
| Recipient-specific delivery | Strong: email invite and revocation | Strong: restricted sharing | Possible, but presigned URLs are bearer capabilities unless paired with a separate authentication layer | Proton Drive |
| Link expiration | Supported | Limited and plan-dependent | Supported through presigned URL expiry | Proton Drive / S3 |
| End-to-end encrypted delivery | Supported | Not represented here as end-to-end encrypted | Server-side encryption; optional SSE-KMS | Proton Drive |
| Reviewer uploads without cloud account | Shared-folder editor or public link, but mutable | Forms/Drive upload flow available, but not immutable | Presigned `PUT` URL supported | S3 |
| Immutable locked submission | Not established | Not established | Strong with versioning and Object Lock compliance mode | S3 |
| SHA-256 upload integrity | External/manual | External/manual | Supported through SigV4 checksum headers and independent verification | S3 |
| Object-level access log | Limited for this scientific contract | Workspace audit capability depends on account tier and configuration | CloudTrail S3 data events | S3 / CloudTrail |
| Cryptographically verifiable audit-log chain | Not established | Not established | CloudTrail signed digest validation | CloudTrail |
| Protected source mapping separation | Separate folders possible, weak formal isolation | Separate Shared Drives possible | Distinct buckets, KMS keys, and IAM roles | S3 / KMS / IAM |
| Private identity/payment store | Encryption strong, structured audit requirements incomplete | Operationally convenient but access and retention depend on Workspace controls | Separate SSE-KMS bucket and distinct IAM role can satisfy technical isolation | Provisional S3 private bucket |
| Minimal setup burden | Low | Low | High | Hybrid chosen despite burden |
| Meets all frozen contracts alone | No | No | No: recipient authentication remains a separate control | Hybrid, gate remains closed |

## Rejected single-system options

### Proton Drive alone

Rejected as the complete scientific record because encrypted sharing and expiration do not establish immutable submission locking, object-version retention, a signed audit-log chain, or deterministic source-to-submission lineage.

### Google Drive / Google Forms alone

Rejected as the complete scientific record because ordinary sharing and response collection do not by themselves satisfy the frozen WORM retention, protected object-version, independent digest, and signed-log-integrity requirements.

### S3 presigned URLs alone

Rejected as the complete reviewer-authentication system because a presigned URL is a time-limited bearer capability derived from the signer’s permissions. Possession of the URL is not proof of reviewer identity. The synthetic dry run must therefore distinguish **delivery authorization** from **identity authentication** and must not mark reviewer authentication operational merely because the URL works.

## Frozen provisional configuration for the synthetic dry run

### Queue delivery

- one synthetic reviewer pseudonym: `DRY-R01`;
- one Proton Drive email-specific view-only share;
- password delivered through a second synthetic channel;
- expiration: 24 hours;
- no anchor target, constructor rationale, protected mapping, real candidate email, or participant data;
- queue SHA-256 recorded before upload and after download.

### Submission capture

- bucket versioning enabled;
- Object Lock enabled before bucket use;
- default retention mode: compliance;
- synthetic retention period: 7 days;
- unique key: `synthetic-review/DRY-R01/<random-run-id>/submission.json`;
- one presigned `PUT` URL, maximum practical dry-run expiry of 15 minutes;
- required content type: `application/json`;
- required SHA-256 checksum;
- no overwrite is treated as valid even though S3 versioning could retain another version;
- first valid object version is locked and identified by bucket, key, version ID, ETag, checksum, retention mode, and retain-until timestamp.

### Logging

- CloudTrail S3 data events enabled for the synthetic delivery/submission buckets;
- log-file integrity validation enabled;
- log and digest files stored outside the submission bucket;
- dry-run evidence must include the `PutObject` event, attempted deletion denial, and CloudTrail validation output or an explicit documented failure.

### Private administration

- only synthetic identities and payment-status codes;
- separate KMS key and IAM role from research stores;
- no queue content, score, anchor ID, source mapping, or constructor target;
- access-log evidence and deletion test required;
- this provisional S3 private store is not accepted for live tax or payment data until legal/ethics review confirms the design.

## Explicit gaps

The selected stack still does not establish:

- legal or institutional sufficiency;
- reviewer identity authentication;
- fair or funded compensation;
- approved retention duration;
- a named data custodian or incident authority;
- protection against a compromised AWS administrator before compliance retention is applied;
- protection against reviewer-side copying or screenshots;
- trusted proof that a human reviewer, rather than another actor, created the uploaded submission;
- live-system readiness.

## Gate effect

No launch gate may move to `verified` from this selection alone.

The following remain `not_verified`:

- administrative oversight;
- secure queue delivery;
- secure submission and immutable lock;
- private administrative store;
- ethics/data-use determination;
- compensation authorization;
- final invitation approval and leakage review.

## Falsification and rejection conditions

Reject or redesign the architecture if the synthetic dry run shows any of the following:

- a queue can be retrieved after the recorded expiration or revocation;
- a wrong checksum is accepted without detection;
- a locked object version can be overwritten or permanently deleted before retention expiry;
- object-level upload/download/delete events are absent from the intended CloudTrail record;
- CloudTrail integrity validation cannot verify the relevant log interval;
- protected mappings or private identities appear in reviewer-facing artifacts;
- private administrative data are accessible through research-data credentials;
- the same reviewer upload URL can validly create an undocumented replacement submission;
- any failure is repaired without a preserved supersession or incident record.

## Decision boundary

This document selects a stack for testing. It is not evidence that the stack has been configured, that the dry run passed, or that reviewer outreach may begin.
