# EGC 2.0 Expert Reviewer Recruitment and Governance Packet

**Status:** Operational recruitment package for the first 24-packet target-blind anchor review  
**Scope:** Independent review of synthetic semantic-fidelity anchor packets only  
**Non-claim:** Participation, agreement, or expertise does not validate any anchor, the seven-point scale, EGC, hidden intention, subjectivity, or consciousness.

## 1. Purpose

This packet governs recruitment, screening, compensation, consent, assignment, and audit records for the first three independent expert reviewers of the synthetic anchor-development tranche.

The objective is narrow: obtain three complete, target-blind, independently locked reviews that can support revision, rejection, or continued development of candidate anchors.

The review is not:

- a test of whether EGC is true;
- a consciousness or sentience assessment;
- an evaluation of any actual AI system;
- a consensus exercise;
- a request to confirm constructor targets.

## 2. Reviewer profile

A candidate may qualify through one or more of the following routes:

- psychometrics, educational measurement, assessment design, or scale development;
- linguistics, discourse analysis, semantics, pragmatics, or qualitative coding;
- cognitive science, psychology, human-subjects research, or research methods;
- professional writing assessment, editing, rubric development, or adjudication;
- demonstrated experience evaluating whether text preserves a specified meaning.

Formal credentials are useful but not sufficient. The screening decision should prioritize demonstrated construct understanding, independence, reliability, and willingness to preserve disagreement.

## 3. Hard exclusion rules

Exclude a candidate from this tranche when any of the following applies:

1. They constructed, edited, or previously reviewed any packet in the tranche.
2. They have seen constructor targets, admissible score ranges, rationales, contrast labels, or protected mappings.
3. They have discussed packet-level answers with another assigned reviewer.
4. They have a direct financial, authorship, or reputational interest in favorable results.
5. They cannot complete the task without generative AI, search, or another person's assistance.
6. They will not accept immutable locking before target reveal.
7. They cannot complete every assigned item.
8. Their English proficiency is insufficient to distinguish semantic fidelity from surface quality.

A disclosed relationship with the project is not automatically disqualifying, but it must be recorded and judged before queue assignment.

## 4. Screening interview

Record answers before assigning a reviewer ID.

### Experience

1. Describe your experience evaluating writing, meaning preservation, rubrics, coding schemes, or research instruments.
2. Give an example of a polished response that could still be semantically unfaithful.
3. Explain the difference between semantic fidelity and agreement with an author's position.
4. Explain when tone should affect fidelity and when it should not.
5. Explain what you would do if the intention map itself were too sparse or internally inconsistent to support a score.

### Independence and exposure

6. Did you help create or edit any EGC anchor packet?
7. Have you seen any proposed target score, rationale, contrast family, pair membership, or protected mapping?
8. Do you know any other candidate reviewer for this tranche?
9. Have you discussed the anchor bank or likely answers with anyone?
10. Do you have any financial, authorship, employment, investment, or reputational interest in a favorable result?

### Operating requirements

11. Can you complete all 24 items independently in assigned order?
12. Can you avoid generative AI, search, external references, and other reviewers while scoring?
13. Can you provide reason codes, map-adequacy judgments, confidence, ambiguity notes, and pair-recognition notes where required?
14. Can you lock the complete submission before learning any constructor target?
15. Can you complete the work within the agreed review window?

## 5. Qualification decision

Use one of four statuses:

- `qualified` — meets all hard requirements;
- `qualified_with_disclosed_relationship` — eligible, but a recorded non-disqualifying relationship exists;
- `hold_for_secondary_screen` — construct understanding or independence remains unclear;
- `excluded` — one or more hard exclusion rules apply.

Every decision must include a short written rationale. Do not record protected-class information or unrelated personal details.

## 6. Compensation contract

Compensation must be fixed before queue delivery and must not depend on:

- agreement with constructor targets;
- agreement with other reviewers;
- retention of any packet;
- direction or magnitude of scores;
- absence of ambiguity or suppression decisions.

Recommended pilot contract:

- fixed payment for one complete admissible submission;
- an explicit estimated workload range stated before acceptance;
- payment for a good-faith complete submission even when results are unfavorable;
- no performance bonus tied to consensus or project outcomes;
- no unpaid revision after target reveal.

A practical budgeting assumption is 90–150 minutes per reviewer, but this is an operational estimate, not observed timing evidence. The final rate must be set before outreach and recorded in the private administrative ledger.

Payment identity and tax information must remain outside research artifacts and outside the public repository.

## 7. Informed participation disclosure

Before acceptance, provide each candidate with:

- the purpose and limits of the review;
- the synthetic nature of the packet content;
- the expected number of items;
- estimated time burden;
- compensation amount and payment trigger;
- independence and no-assistance requirements;
- what data will be retained;
- whether anonymized scores may be published;
- the right to decline before queue assignment;
- the rule that a locked submission cannot be changed after target reveal;
- the project contact for questions or withdrawal before locking.

The reviewer must affirm:

> I understand that this is an instrument-development review of synthetic text pairs. I am not being asked to assess consciousness, sentience, or any real person or AI system. I understand the independence, data-use, compensation, and locking rules and consent to participate under those terms.

This language is an operational consent disclosure, not a legal determination that institutional ethics review is unnecessary.

## 8. Data minimization

The research dataset may contain only:

- reviewer pseudonym;
- qualification status;
- broad expertise categories;
- conflict-screen result;
- queue digest;
- locked submission digest;
- item-level review fields;
- lock time;
- payment-status code without payment details.

Store names, emails, payment details, tax information, and contact history in a separate private administrative system.

Do not commit the reviewer linkage table, live reviewer queues, protected assignment keys, private seeds, or completed submissions containing administrative identifiers.

## 9. Assignment protocol

Before queue creation:

1. Confirm three candidates have status `qualified` or `qualified_with_disclosed_relationship`.
2. Confirm no pair of reviewers has discussed packet content.
3. Assign pseudonyms that contain no initials or identifying information.
4. Freeze the compensation terms and review window.
5. Record the exact source-manifest digest.
6. Create the generation precommit before using the protected seed.
7. Generate reviewer-specific opaque queues through the hardened v0.2 path.
8. Validate cross-artifact lineage before distribution.
9. Deliver each reviewer only their own public queue and instructions.

## 10. Submission and lock protocol

A submission is admissible only when:

- all 24 assigned items are complete and in assigned order;
- source and queue digests match;
- reviewer pseudonym matches;
- all required fields validate;
- map-inadequacy suppression is justified with an allowed reason code;
- suspected pair recognition includes a note;
- `targets_seen_before_lock` is false;
- `locked_before_target_reveal` is true;
- the submission digest is recomputed and recorded.

Clerical defects discovered before reveal may be corrected only through a preserved superseding artifact and written reason. No substantive score change is allowed after target reveal.

## 11. Withdrawal and incomplete work

Before locking, a reviewer may withdraw without explanation. Preserve only administrative status and do not treat partial scores as completed expert evidence.

After locking, the submission remains part of the audit record even if the reviewer later asks not to participate in future phases. Publication and withdrawal handling must follow the disclosure accepted before participation and any applicable ethics determination.

Do not replace an unfavorable reviewer. Replacement is allowed only for documented noncompletion, disqualification, or withdrawal before lock. The reason must be preserved, and the replacement must receive a newly generated reviewer-specific queue.

## 12. Independence audit

Before reveal, record for each reviewer:

- no target exposure reported;
- no external assistance reported;
- no discussion with another reviewer reported;
- no queue exchange reported;
- all pair-recognition flags preserved;
- complete submission validated;
- submission digest frozen.

If independence is materially compromised, do not silently exclude the reviewer. Mark the submission `integrity_review_required`, preserve it, and perform sensitivity analyses with and without it.

## 13. Stopping and failure rules

Stop the tranche before target reveal when:

- fewer than three admissible independent submissions exist;
- a reviewer saw protected targets before lock;
- a protected mapping or seed was disclosed;
- queue or submission lineage fails;
- two reviewers collaborated;
- compensation terms changed after scores were observed;
- the source manifest changed after queues were generated.

A stopped tranche is a failed instrument-development run. Preserve the failure and restart with a new tranche identifier, new reviewer assignments, and new commitments.

## 14. Permitted conclusions

After three valid reviews, the program may conclude only that:

- reviewers did or did not use the provisional categories similarly;
- specific packets produced agreement, disagreement, suppression, ambiguity, or recognition concerns;
- specific packets should be retained for further pilot work, revised, rejected, or re-reviewed.

It may not conclude that:

- any packet is a validated gold standard;
- expert agreement proves construct validity;
- semantic fidelity has been psychometrically validated;
- EGC measures hidden intention, subjectivity, or consciousness;
- disagreement proves reviewer incompetence.

## 15. Required administrative records

Maintain a private recruitment log with:

- candidate pseudonym;
- outreach date and source;
- response status;
- qualification decision and rationale;
- exposure and conflict disclosures;
- consent timestamp;
- fixed compensation terms;
- queue assignment date;
- completion, withdrawal, or exclusion status;
- payment-status code;
- notes limited to operationally necessary facts.

The corresponding machine-readable public-safe structure is defined in `expert_reviewer_recruitment_tracker.v0.1.schema.json`.

## 16. Current unresolved uncertainty

This packet does not establish:

- that three reviewers are sufficient;
- that the proposed workload estimate is accurate;
- that compensation will avoid selection bias;
- that qualified experts will interpret the construct consistently;
- that synthetic anchors generalize to participant material;
- that the review qualifies for exemption from formal ethics oversight.

## 17. Next valid action

Set the fixed compensation amount and review window, recruit at least six candidates to obtain three eligible independent reviewers, complete screening and consent, then freeze reviewer pseudonyms before generating any live queue.