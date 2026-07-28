# EGC 2.0 Secure Reviewer Delivery and Submission Contract

**Status:** Operational specification; no delivery system is represented as active  
**Scope:** First 24-packet target-blind expert-review tranche

## 1. Objective

Bind each reviewer to one opaque queue, preserve target blindness, obtain one immutable complete submission, and prevent ordinary email or shared-document workflows from becoming the scientific record.

## 2. Queue delivery contract

A delivery path is acceptable only when it provides:

1. reviewer-specific authentication or a single-use access secret;
2. one public queue only, with no source IDs or constructor metadata;
3. transport encryption;
4. access expiration after the review window;
5. an access event log containing reviewer pseudonym, queue digest, and UTC time;
6. no public or guessable link;
7. no cross-reviewer directory listing;
8. revocation after exposure, compromise, or withdrawal.

Ordinary unrestricted attachment sharing, public cloud links, and editable shared documents are prohibited.

## 3. Reviewer authentication

The administrative identity linkage remains private. The research system uses only the reviewer pseudonym.

Minimum authentication evidence:

```text
reviewer_pseudonym
queue_digest_sha256
authentication_method
credential_issued_at_utc
first_access_at_utc
credential_revoked_at_utc
```

Authentication proves control of the issued credential, not the reviewer’s real-world identity. Identity verification remains an administrative process.

## 4. Queue integrity

Before delivery:

- validate the public queue and protected mapping;
- preserve the source-manifest digest;
- preserve the queue digest;
- verify opaque presentation identifiers;
- verify pair separation and domain balance;
- confirm no constructor targets or protected mappings are present;
- record the exact delivered bytes or their canonical digest.

A changed queue requires a new queue version and new credential. Silent replacement is prohibited.

## 5. Submission contract

A submission is admissible only when:

- it contains every assigned presentation exactly once and in assigned order;
- all required score, reason, adequacy, confidence, ambiguity, and recognition fields are complete;
- its source and queue digests match;
- `targets_seen_before_lock` is false;
- it receives an immutable lock timestamp;
- its content digest is recomputed and preserved;
- subsequent changes create a superseding artifact rather than overwriting the original.

## 6. Lock implementation requirements

The operational submission path must provide one of:

- append-only object versioning with retention lock;
- exclusive-create immutable file storage plus an independently preserved digest;
- signed form export plus a trusted timestamp and read-only archive.

A mutable spreadsheet, editable form response, or email body alone is insufficient.

## 7. Failure states

Preserve these statuses:

```text
delivery_not_accessed
delivery_credential_failed
queue_digest_mismatch
submission_incomplete
submission_digest_mismatch
submission_unlocked
target_exposure_reported
reviewer_withdrew
reviewer_collaboration_suspected
protected_mapping_compromised
```

No failed state may be converted into a valid review through undocumented manual repair.

## 8. Incident response

On suspected exposure or compromise:

1. pause the affected reviewer;
2. revoke credentials;
3. preserve the original queue and event log;
4. record what was exposed and when;
5. determine whether the reviewer remains target-blind;
6. decide replacement using the pre-frozen rule, not the direction of scores;
7. document whether the full tranche must restart.

## 9. Operational gate evidence

Gate `G05_secure_queue_delivery_path` requires:

- named system and owner;
- authentication method;
- encryption and expiration configuration;
- access-log example;
- queue-digest verification record;
- successful dry run using synthetic content.

Gate `G06_secure_submission_and_lock_path` requires:

- named system and owner;
- immutable-lock mechanism;
- digest and timestamp evidence;
- supersession procedure;
- successful synthetic end-to-end dry run;
- documented recovery and incident process.

## 10. Current disposition

```text
secure_delivery_operational: false
secure_submission_operational: false
live_queue_distribution_allowed: false
```

This specification defines acceptance criteria; it does not claim that any current tool satisfies them.