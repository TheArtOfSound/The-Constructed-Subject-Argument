# EGC 2.0 Expert Reviewer Public/Private Data-Separation Specification

**Status:** Pre-invitation operational specification  
**Scope:** First target-blind expert-review tranche

## 1. Purpose

The review process requires identity, payment, and contact information for administration while the research record requires pseudonymous scores, adequacy decisions, and audit commitments. Combining those data creates unnecessary disclosure and re-identification risk.

This specification separates three storage classes and prohibits cross-contamination.

## 2. Storage classes

### Class A — Public repository research artifacts

Allowed:

- protocols, schemas, blank forms, and synthetic fixtures;
- candidate slot IDs and broad expertise lanes;
- aggregate recruitment counts and dispositions;
- reviewer pseudonyms only after assignment, when necessary;
- queue and submission digests without queue content;
- aggregate review results after authorized release;
- null, failed, contradictory, withdrawal, and exclusion counts without direct identifiers.

Prohibited:

- names, personal email addresses, phone numbers, mailing addresses;
- payment or tax information;
- identity-linkage tables;
- live queue contents or protected source mappings;
- live generation seeds or nonces;
- reviewer-specific item answers before authorized release;
- confidential institutional restrictions.

### Class B — Protected research workspace

Allowed:

- reviewer-specific blinded queues;
- protected opaque-ID-to-anchor mappings;
- locked pseudonymous submissions;
- queue, key, submission, and lineage commitments;
- incident and target-exposure records keyed only by reviewer pseudonym;
- pre-reveal aggregate discrepancy reports without constructor targets.

Requirements:

- access limited to named administrative and analysis roles;
- encryption at rest and in transit where available;
- no public repository commitment;
- separate access control from Class C identity data;
- versioned immutable copies of locked submissions;
- deletion and retention schedule documented before assignment.

### Class C — Private administrative identity and payment store

Allowed:

- legal name and contact details;
- pseudonym-to-identity linkage;
- consent acceptance record;
- payment method, tax, invoice, and institutional clearance information;
- compensation status;
- withdrawal and incident contact records.

Requirements:

- never included in research datasets or repository artifacts;
- access restricted to the administrative contact and payment custodian;
- linkage accessed only for consent, support, payment, withdrawal, or incident response;
- no item-level ratings or constructor targets stored here;
- retention minimized to legal, payment, and oversight needs.

## 3. Identifier model

Use distinct identifiers:

- `candidate_slot_id` for public sourcing;
- `candidate_pseudonym` for screening;
- `reviewer_pseudonym` for assigned review work;
- `presentation_id` for reviewer-facing items;
- `anchor_id` only in protected mappings and constructor-side artifacts.

A public candidate slot must not be treated as a confirmed identity. The mapping from candidate pseudonym to reviewer pseudonym is private administrative data.

## 4. Role separation

Minimum roles:

- **Administrative contact:** identity, consent, scheduling, withdrawal.
- **Payment custodian:** payment and tax records.
- **Review operator:** queue delivery and submission locking using pseudonyms.
- **Analysis custodian:** pseudonymous locked submissions and aggregate analysis.

One person may hold multiple roles in a small project, but the access boundaries and access events must still be documented. The analysis custodian should not access identity data unless operationally necessary.

## 5. Data flow

1. Public outreach references only the role and proposed terms.
2. Positive responses enter Class C under a candidate pseudonym.
3. Screening disposition is exported to Class A or B without direct identity.
4. Eligible consented candidates receive a reviewer pseudonym.
5. The review operator distributes only that reviewer’s Class B queue.
6. Locked submissions remain in Class B and are bound to queue and source commitments.
7. Payment status flows to Class C; only a coarse status code may enter the pseudonymous tracker.
8. Aggregate findings enter Class A only after target-blind locking and authorized release.

## 6. Incident rules

Immediately pause assignment or analysis when:

- direct identity appears in a research artifact;
- a protected mapping or seed enters a public location;
- a reviewer receives another reviewer’s queue;
- constructor targets are exposed before lock;
- a locked submission is altered or replaced without a preserved superseding record;
- identity linkage is accessed without an administrative reason.

The incident record must preserve what happened, affected artifacts, containment, and whether target blindness or independence remains defensible.

## 7. Retention and deletion fields to freeze before invitation

- Class B retention period:
- Class C retention period:
- consent-record retention basis:
- payment-record retention basis:
- deletion authority:
- backup deletion procedure:
- incident-log retention:
- jurisdiction or contractual requirement:

Until these fields and responsible roles are completed, the secure-storage launch gates remain unverified.

## 8. Claims boundary

This separation reduces unnecessary disclosure and limits routine linkage. It does not prove anonymity, prevent privileged access, guarantee encryption, satisfy a specific legal regime, or replace an authorized ethics/data-use determination.