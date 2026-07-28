# EGC 2.0 Expert Reviewer Administrative Oversight Record

**Status:** Required operational record; incomplete until named responsible people accept each role  
**Scope:** First 24-packet target-blind expert-review tranche  
**Non-claim:** Completing this record does not constitute legal, institutional, or ethics approval.

## 1. Purpose

This record freezes who is responsible for reviewer administration, research-data custody, payment administration, incident response, and release authorization before any invitation is sent or any queue is distributed.

No one person should control reviewer identity, protected source mappings, payments, and target reveal where practical.

## 2. Required roles

### Administrative lead

Responsible for:

- maintaining the private candidate and reviewer identity linkage;
- sending approved invitations;
- collecting screening and consent records;
- confirming compensation authorization;
- coordinating payment without receiving item-level scores unless operationally necessary.

Fields to freeze:

```text
name_or_role_id:
accepted_at_utc:
contact_channel:
authority_scope:
backup_contact:
```

### Research-data custodian

Responsible for:

- storing protected reviewer queues, assignment keys, and locked submissions;
- enforcing access controls and retention rules;
- preserving digests and immutable submission history;
- preventing reviewer identities from entering public research artifacts.

Fields to freeze:

```text
name_or_role_id:
accepted_at_utc:
protected_store_identifier:
backup_and_recovery_method:
access_review_interval:
```

### Payment custodian

Responsible for:

- holding the approved compensation budget;
- initiating payment after a valid locked submission;
- keeping payment and tax data outside research artifacts;
- documenting failed or delayed payments without conditioning payment on review outcome.

Fields to freeze:

```text
name_or_role_id:
accepted_at_utc:
budget_authorization_reference:
payment_method:
payment_deadline_days:
```

### Incident authority

Responsible for deciding whether to pause or terminate the tranche after:

- target leakage;
- queue or submission compromise;
- reviewer collaboration;
- identity-data exposure;
- payment failure affecting independence;
- loss of protected mappings or digest records.

Fields to freeze:

```text
name_or_role_id:
accepted_at_utc:
incident_contact_channel:
maximum_response_time_hours:
```

### Reveal authorizer

Responsible for confirming that all required reviewer submissions are valid and locked before constructor targets are joined.

The reveal authorizer must not authorize reveal when:

- any required submission is incomplete or mutable;
- any reviewer reports target exposure before lock;
- source or submission digests do not validate;
- a known incident remains unresolved.

Fields to freeze:

```text
name_or_role_id:
accepted_at_utc:
independence_from_construction:
reveal_authorization_record_path:
```

## 3. Separation-of-duty matrix

Before launch, record whether one person occupies more than one role.

| Role pair | Same person allowed? | Required mitigation |
|---|---:|---|
| Administrative lead + payment custodian | Yes | Payment remains outcome-independent and item-level scores are not required for payment. |
| Administrative lead + research-data custodian | Discouraged | Access log and second-person review of any identity-to-submission join. |
| Research-data custodian + reveal authorizer | Yes, with caution | Reveal authorization must be separately logged and digest-bound. |
| Constructor + reveal authorizer | No | Replace authorizer. |
| Constructor + incident authority | Discouraged | Independent second decision-maker required for target-leakage incidents. |

## 4. Authority boundaries

No role may:

- alter reviewer scores after lock;
- replace a reviewer because results are unfavorable;
- expose constructor targets before all required valid locks;
- move private identity or payment data into the repository;
- suppress null, failed, contradictory, or excluded outcomes;
- describe the review as validating EGC, hidden intention, subjectivity, or consciousness.

## 5. Required operational evidence

Gate `G04_administrative_contact_and_oversight` remains unverified until this record contains:

1. accepted role assignments;
2. contact and backup channels;
3. authority boundaries;
4. separation-of-duty review;
5. incident response timing;
6. reveal authorization location;
7. signatures or equivalent acceptance records stored privately.

## 6. Current disposition

```text
operational_status: incomplete
invitation_send_allowed: false
queue_assignment_allowed: false
target_reveal_allowed: false
```

No named person has accepted these roles in the public repository record.