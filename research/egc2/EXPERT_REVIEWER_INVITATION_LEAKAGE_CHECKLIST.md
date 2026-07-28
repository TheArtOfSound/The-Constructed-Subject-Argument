# EGC 2.0 Expert Reviewer Invitation Leakage Checklist

**Status:** Pre-send review checklist  
**Scope:** Initial outreach and participation-terms delivery only; no reviewer queues

## 1. Decision rule

An invitation may pass this checklist only when every prohibited-content check is `absent`, every required-boundary check is `present`, and the reviewer records a timestamped decision.

A passed invitation-leakage check does not authorize sending by itself. All other launch gates must also be verified.

## 2. Prohibited content

Confirm that the outreach message and attachments contain none of the following:

- anchor text or candidate responses;
- private intention maps;
- source anchor IDs;
- presentation-to-anchor mappings;
- constructor target scores;
- admissible score ranges;
- constructor rationales;
- contrast-family labels;
- contrast-group or pair IDs;
- prior reviewer scores or consensus claims;
- pilot metrics;
- protected generation seeds, nonces, salts, or keys;
- live queue digests that could identify a reviewer assignment;
- private holdout material;
- language implying that the instrument, EGC, or any consciousness claim is validated;
- language implying that the candidate has agreed or been recruited;
- outcome-dependent compensation or publication promises.

## 3. Required boundary language

Confirm that the message states or clearly conveys:

- the task is instrument development;
- the material is synthetic;
- review is target-blind;
- constructor targets and rationales remain hidden until lock;
- disagreement, ambiguity, rejected packets, and null outcomes are preserved;
- payment is fixed and independent of ratings or outcome;
- the initial contact asks only whether the candidate will consider the full terms;
- participation does not endorse EGC or a consciousness-related claim;
- no anchor content is included in the initial invitation.

## 4. Candidate-specific personalization check

Personalization may reference only publicly documented expertise and the general methodological relevance of that expertise.

Reject personalization that:

- attributes private beliefs or availability;
- implies prior agreement;
- claims the candidate will validate the instrument;
- reveals the expected direction of scoring;
- encourages a specific disciplinary answer;
- offers different substantive terms to different candidates.

## 5. Attachment check

Allowed initial attachments:

- uniform participation terms only after compensation, oversight, and data-use gates are verified;
- screening form;
- consent acknowledgement only after administrative and oversight fields are completed.

Not allowed in initial outreach:

- reviewer queue;
- rubric answer key;
- anchor bank;
- constructor-side methods rationale containing item targets;
- protected mappings;
- other reviewers’ identities or status.

## 6. Header, metadata, and link check

Inspect:

- subject line;
- visible recipients and CC/BCC fields;
- attachment names;
- document properties;
- shared-drive permissions;
- link previews;
- URL paths and query parameters;
- revision history and comments;
- hidden spreadsheet tabs or document text;
- email signature and organizational claims.

A clean message can still leak targets through attachment history, permissions, filenames, or comments.

## 7. Uniformity check

Across all candidates, verify identical:

- compensation;
- review window;
- task size;
- payment condition;
- consent and data-use terms;
- independence requirements;
- withdrawal rules;
- secure-submission rules;
- scientific claim limits.

Candidate-specific expertise language may differ. Material terms may not.

## 8. Independent review record

Required fields:

- invitation version or digest:
- candidate slot ID:
- reviewer pseudonym performing leakage review:
- prohibited-content result: pass / fail
- required-boundary result: pass / fail
- metadata and attachment result: pass / fail
- uniformity result: pass / fail
- unresolved ambiguity:
- decision: approved / revision_required / rejected
- reviewed at UTC:

A person who drafted the final invitation may perform the first check, but a second check is required before send when feasible. Any failure resets approval after revision.

## 9. Applied review of the current six draft invitations

Repository artifact reviewed:

`research/EGC_2_EXPERT_REVIEWER_SIX_CANDIDATE_EXECUTION_PACKET.md`

Current document-level findings:

- no anchor packet text is included;
- no constructor score, rationale, admissible range, pair ID, or protected mapping is included;
- every draft describes target blindness;
- every draft states or implies that disagreement and adverse outcomes are preserved;
- every draft avoids claiming recruitment or availability;
- every draft limits the initial request to willingness to receive or consider the full terms;
- every draft rejects consciousness-test framing or project endorsement.

Current limitation:

The drafts are embedded in a public methods document rather than finalized email artifacts with verified recipients, attachments, permissions, and metadata. Therefore the **document-content leakage review is complete**, but the **actual-send leakage review remains not performed**.

## 10. Claims boundary

This checklist can detect documented content and metadata leakage risks. It cannot prove that a recipient lacks prior exposure, that an external mail system strips no protections, or that a reviewer will remain target-blind after delivery.