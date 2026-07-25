# EGC 2.0 Rater-Pilot Assignment Design

**Status:** Executable design specification; no rater data collected  
**Date:** 2026-07-25  
**Parent protocols:** `EGC_2_HUMAN_RATING_RELIABILITY_PROTOCOL.md` and `EGC_2_SEMANTIC_FIDELITY_ANCHOR_BANK_PROTOCOL.md`

## Purpose

This design operationalizes the proposed 60-response, eight-rater pilot while preventing the most important exposure and balance failures. It does not establish rating reliability. It creates a deterministic assignment that can be inspected before recruitment.

## Default design

- 30 participants;
- two paired responses per participant: private and evaluated;
- 60 participant responses total;
- eight raters;
- four independent ratings per response;
- 240 primary-response assignments;
- 42 candidate anchors, each assigned to four raters;
- 168 anchor assignments;
- 12 blind-repeat assignments, equal to 5% of primary assignments;
- three prompt domains, with ten participants per domain.

## Complementary assignment principle

For each participant, four raters receive the private response and the complementary four receive the evaluated response. Therefore:

1. every response receives four ratings;
2. no rater sees both responses from one participant;
3. every rater sees exactly one response from every participant;
4. every rater receives 30 primary responses.

Within each ten-participant prompt-domain block, five four-rater partitions are paired with their complements. This forces every rater to receive exactly five private and five evaluated responses per domain. Across all domains, each rater receives:

- ten responses per prompt domain;
- fifteen private responses;
- fifteen evaluated responses.

This exact balance is a property of the construction, not a favorable random outcome.

## Anchor and repeat allocation

The initial 42-anchor blueprint produces 168 anchor ratings. A least-loaded deterministic allocator gives every rater 21 anchor packets. Anchor IDs are placeholders until actual packets pass schema validation.

Blind repeats are sampled only from responses already assigned to the same rater. Twelve repeat assignments are distributed as evenly as possible across raters. The generator records the source response ID, but presentation software must hide repeat status and ensure adequate temporal separation. The current generator validates source ownership but does not yet construct a session-order schedule; that remains a required implementation layer.

## Machine-readable artifacts

- `research/egc2/anchor_packet.v0.1.schema.json` validates anchor packet structure and prevents an `active_validated` label without blind-review and pilot metrics.
- `research/egc2/generate_rater_pilot_assignment.py` generates the deterministic assignment and an audit SHA-256 digest.
- `research/egc2/test_generate_rater_pilot_assignment.py` tests exact balance and adversarial failures.

## Fail-closed validation

The generator returns a nonzero status when any of these conditions fail:

- a response does not have exactly four ratings;
- a rater sees both responses from one participant;
- primary rater loads differ;
- prompt-domain or condition exposure is imbalanced;
- anchor rating counts or rater loads are imbalanced;
- a blind repeat lacks a source rating by the same rater;
- blind-repeat count differs from the declared fraction.

## Interpretation limits

A balanced assignment does not prove:

- that the seven score regions are distinguishable;
- that the candidate anchors are valid;
- that four raters per response are sufficient;
- that rater severity or response-by-rater interaction is acceptably small;
- that semantic fidelity is a valid EGC outcome;
- that EGC measures consciousness or private thought.

Those claims require blind expert review, pilot ratings, generalizability analysis, decision studies, category-functioning evidence, and construct-validity tests.

## Highest-leverage next implementation

Add a session-order scheduler that interleaves participant responses, anchors, and blind repeats while enforcing minimum repeat separation, concealed item type, domain mixing, and no adjacent paired-material cues. Then run simulated dropout and replacement-rater scenarios to test whether the assignment graph remains connected.
