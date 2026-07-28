# EGC 2.0 Private Reviewer Administration Store Checklist

**Status:** Implementation checklist; no private store is represented as operational  
**Scope:** Identity, contact, consent, payment, and tax administration for the first expert-review tranche

## 1. Boundary

The private administrative store is separate from:

- the public repository;
- reviewer-facing queues;
- protected source mappings;
- pseudonymous locked research submissions.

It may contain real names, contact details, signed consent, payment records, and legally required tax information. Those fields must not enter public or protected research artifacts.

## 2. Required records

For each candidate or reviewer, the store may contain:

```text
private_candidate_id
real_name
contact_information
screening_response
consent_record
reviewer_pseudonym
payment_status
payment_reference
tax_or_vendor_record_if_required
withdrawal_or_incident_notes
```

The research repository may contain only the pseudonym and non-identifying status codes.

## 3. Access controls

Before operational use, freeze:

- store owner;
- authorized users and least-privilege roles;
- multi-factor authentication requirement;
- encryption at rest and in transit;
- backup and recovery procedure;
- access-log retention;
- account-revocation procedure;
- incident-notification authority.

Shared passwords and publicly accessible links are prohibited.

## 4. Identifier separation

Maintain two mappings:

1. `private_candidate_id ↔ real identity` in the private store;
2. `private_candidate_id ↔ reviewer_pseudonym` in a restricted linkage table.

The research-data custodian should not need payment or tax data. The payment custodian should not need item-level scores.

## 5. Retention and deletion

The following periods must be frozen before outreach:

```text
unselected_candidate_contact_retention:
selected_reviewer_identity_retention:
consent_record_retention:
payment_and_tax_retention:
access_log_retention:
incident_record_retention:
```

Deletion must include active copies, routine exports, and ordinary backups to the extent operationally possible. Legal or accounting retention overrides must be documented rather than silently extending research retention.

## 6. Payment integrity

The store must preserve:

- the uniform offered amount;
- authorization reference;
- valid-submission status;
- payment initiation time;
- payment completion or failure status;
- reason for any delay.

It must not contain a field that conditions compensation on agreement, score direction, consensus, packet retention, or publication outcome.

## 7. Consent integrity

Consent records must be versioned and bind:

- participation-terms version;
- data-use version;
- compensation amount;
- review window;
- acknowledgement time;
- withdrawal status.

A changed consent form requires renewed acknowledgement before queue assignment.

## 8. Security dry run

Before gate verification, perform a synthetic dry run that demonstrates:

1. candidate creation;
2. pseudonym assignment;
3. role-limited access;
4. consent version binding;
5. payment-status recording without score access;
6. access-log creation;
7. record export excluding direct identifiers;
8. account revocation;
9. test-record deletion.

Record only synthetic evidence in the repository.

## 9. Gate rule

Gate `G07_private_identity_and_payment_storage` remains unverified until:

- a named store and owner exist;
- access roles are configured;
- retention periods are frozen;
- the synthetic dry run passes;
- administrative and research exports are proven separated;
- no live reviewer data are placed in the repository.

## 10. Current disposition

```text
private_store_selected: false
private_store_configured: false
retention_periods_frozen: false
synthetic_dry_run_passed: false
live_identity_collection_allowed: false
```

This checklist documents the implementation requirement and preserves the current blocker.