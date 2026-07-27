# EGC 2.0 Blind Expert Anchor Review — v0.1 Deprecated

**Status:** Historical development packet; do not use for reviewer distribution  
**Replacement:** `research/egc2/ANCHOR_EXPERT_REVIEW_V0.2_HARDENING_PACKET.md`  
**Non-claim:** Neither version validates anchors, the seven-point scale, EGC, hidden intention, subjectivity, or consciousness.

## Deprecation decision

The v0.1 review path was superseded before live reviewer distribution because its public queues retained sequential source IDs such as `A001` and `A002`. Since designed pair members were created as adjacent source records, those IDs could reveal pair structure even though explicit contrast labels were removed.

Additional v0.1 limitations:

- contrast-pair separation was only six positions;
- public reviewer files retained source anchor IDs;
- public and protected identity layers were not cleanly separated;
- a submission digest was returned by validation but was not required as a verified field in the submitted artifact;
- pre-reveal aggregation was blocked entirely rather than permitting target-free disagreement review;
- suspected pair recognition did not require an explanatory note.

These are instrument-integrity issues, not evidence that any review result was compromised. No live expert submission was collected under v0.1.

## Required replacement

Use:

- `research/egc2/harden_anchor_expert_review.py`
- `research/egc2/anchor_review_submission.v0.2.schema.json`
- `research/egc2/ANCHOR_EXPERT_REVIEW_V0.2_HARDENING_PACKET.md`
- `research/EGC_2_ANCHOR_EXPERT_REVIEW_V0_2_HARDENING_REVIEW.md`

Version 0.2 provides:

- reviewer-specific opaque presentation IDs;
- a separate protected source mapping;
- exact twelve-position pair separation;
- domain balance within both queue halves;
- secret-seeded generation with a public seed commitment;
- independently verified queue, key, bundle, submission, and aggregate digests;
- explicit inadequate-reference score suppression;
- required notes for suspected pair recognition;
- target-free pre-reveal aggregation and explicit post-lock target reveal.

## Historical preservation

The original v0.1 content remains available in repository history. It should be cited only as a superseded engineering stage and must not be used to generate or distribute live reviewer queues.
