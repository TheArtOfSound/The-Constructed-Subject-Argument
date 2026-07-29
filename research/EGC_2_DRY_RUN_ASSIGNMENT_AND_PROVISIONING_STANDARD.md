# EGC 2.0 Synthetic Dry-Run Assignment and Provisioning Standard

**Status:** prospective operational standard; blocked and non-executable  
**Machine-readable record:** `research/egc2/expert_reviewer_dry_run_assignment_and_provisioning.v0.1.json`

## Purpose

The existing execution-readiness record correctly prevents a synthetic Proton/AWS dry run from beginning while operator, ownership, resource, and independent-review fields remain incomplete. This standard defines the evidence required to populate those fields without treating names, aliases, or self-attestation as proof that an operational control exists.

It is an execution-governance artifact, not a scientific result. It does not validate EGC measurement, reviewer behavior, semantic fidelity, the Subject–Report Identification framework, or any consciousness-related inference.

## Assignment evidence

Two functions must be explicitly accepted before provisioning can be represented as complete:

1. a primary synthetic-test operator;
2. an independent audit-evidence reviewer who cannot execute the run.

Six ownership functions must also be assigned: Proton custody, AWS custody, synthetic-artifact custody, incident/rollback authority, public-evidence curation, and execution authorization.

A role is not accepted merely because a pseudonym appears in a file. Acceptance requires all of:

- `accepted=true`;
- a non-secret public pseudonym;
- an ISO-8601 UTC acceptance time;
- a public-safe evidence path preserving the acceptance;
- consistency with the private identity/authentication process, which must remain outside public evidence.

The standard does not specify that one person must fill only one role. Role concentration remains an unresolved governance risk. Any later validator should either prohibit incompatible role combinations or require an explicit independence justification.

## Provisioning evidence

The record defines eight control units:

- **R01:** isolated Proton account;
- **R02:** Proton synthetic queue and delivery controls;
- **R03:** isolated AWS account and frozen region;
- **R04:** versioned S3 evidence store with Object Lock in `COMPLIANCE` mode;
- **R05:** CloudTrail S3 data events and log-file validation;
- **R06:** IAM and KMS separation among execution, evidence, and review roles;
- **R07:** private administration/protected-mapping store separated from public evidence;
- **R08:** digest-frozen synthetic artifact set with leakage and evidence-closure checks.

A resource alias is not evidence. A control may be marked provisioned only when its evidence paths demonstrate every required property. Public artifacts must use non-secret aliases and redact direct account identifiers, credentials, contact data, protected mappings, constructor targets, anchor identities, rationales, and private holdout material.

## Mapping to readiness gates

The machine-readable artifact maps all twelve existing readiness gates, P01–P12, to assignments, ownership functions, and resource controls. The mapping is prospective. It has not been empirically tested against a real cloud setup and may omit dependencies.

The principal methodological reason for the mapping is traceability: a future `verified` gate must resolve to concrete assignment or resource evidence rather than an unstructured narrative claim.

## Fail-closed completion rule

`execution_allowed` must remain `false` while any of the following is incomplete, failed, contradictory, or unresolved:

- primary-operator acceptance;
- independent-reviewer acceptance;
- any ownership role;
- any R01–R08 control;
- leakage scanning;
- evidence-reference closure;
- independent review of P01–P12;
- no-live-data and no-private-holdout attestations.

A stopped or failed run must remain preserved as a stopped or failed run. Recomputing digests, replacing aliases, or adding evidence after the fact must not convert a historical failure into a pass.

## Findings, hypotheses, and uncertainty

### Supported by the committed artifact

- The assignment and provisioning state is explicitly blocked.
- No person is represented as assigned.
- No Proton or AWS resource is represented as provisioned.
- Six ownership functions, eight resource/control units, and all twelve readiness gates have explicit prospective slots.
- The artifact prohibits execution while any prerequisite remains incomplete.

### Proposed but unvalidated

- R01–R08 jointly cover every operational dependency of the first synthetic cloud dry run.
- Pseudonymized public acceptance records plus private identity controls provide sufficient accountability.
- Redacted cloud evidence can demonstrate each control without leaking operational secrets.
- The proposed role separation is strong enough to prevent evidence manipulation or self-review.

### Not supported

- No operator or reviewer identity has been authenticated.
- No external resource, Object Lock setting, CloudTrail event, access denial, key separation, revocation, or audit chain has been observed.
- No reviewer outreach, compensation, consent, ethics, or data-use determination has occurred.
- No EGC hypothesis, hidden intention, evaluation awareness, deception, subjectivity, or consciousness claim is validated.

## Falsification and failure conditions

The standard is inadequate if an adversarial validator can construct a record that appears complete while any required assignment, evidence path, control property, gate mapping, independent-review disposition, or public-safety boundary remains absent or contradictory.

The standard should also be revised if a real synthetic provisioning exercise reveals an operational dependency not represented by R01–R08. Such a result is a design failure to preserve, not a reason to silently broaden a passing record after execution.

## Highest-leverage next action

Implement an adversarial standard-library validator that checks exact O01–O06, R01–R08, and P01–P12 coverage; assignment-field consistency; resource-evidence completeness; mapping referential integrity; prohibited executable transitions; and preservation of the blocked state until independent review is complete.
