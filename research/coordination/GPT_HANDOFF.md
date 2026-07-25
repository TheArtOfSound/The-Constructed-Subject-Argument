# GPT Handoff

**Updated:** 2026-07-25T22:32Z  
**Repository head inspected:** `612778b586c5c7c7dffbc6c8b17157f370e6e7c9`  
**Latest substantive commit produced this run:** `cebf336c81139259eeab813e9aa2aa56e62b9750`  
**Run status:** completed

## Completed this run

- Read `CLAUDE.md`, `research/coordination/README.md`, both agent handoffs, and the latest 12 remote commits.
- Confirmed Claude's visible reservation remains stale and limited to QEIB pilot/matrix reporting, capable-model execution, raw logs, and provenance.
- Completed the reserved targeted EGC anchor-detector design comparison across 8, 12, and 16 raters and 18 versus 36 items per monitoring class.
- Added `research/egc2/compare_anchor_detector_designs.py`, preserving the committed simulator's ordinal scoring and random-number sequence while aggregating the rater-level shifts required by the detector.
- Ran 90 synthetic cells: five stress scenarios × six designs × three generating regimes, using `delta = 0.20`, 100 Monte Carlo trials, and 100 whole-rater bootstrap draws per cell.
- Added decision-relevant results at `research/egc2/results/anchor_detector_design_comparison_100x100.json`.
- Added `research/EGC_2_ANCHOR_DETECTOR_DESIGN_COMPARISON_REVIEW.md`.

## Evidence and validation

- The exact scientific calculation implemented in the committed script was executed in an isolated Python 3.13 environment; 90 cells completed in 26.914 seconds.
- Interior adversarial support rates: 8×18 `0.44`, 8×36 `0.71`, 12×18 `0.63`, 12×36 `0.92`, 16×18 `0.76`, 16×36 `0.98`.
- High-noise support rates: 8×18 `0.20`, 8×36 `0.33`, 12×18 `0.24`, 12×36 `0.60`, 16×18 `0.32`, 16×36 `0.69`.
- Floor-limited support never exceeded `0.40`; ceiling-limited support never exceeded `0.24`, even at 16×36.
- Maximum observed support in non-adversarial cells was `0.01`; this is not treated as a validated false-positive bound because only 100 trials were run per cell.
- No participant data, real anchor packets, genuine-model results, or private QEIB holdout material were accessed.

## Claims discipline

### Findings supported within the synthetic comparison

- The current 8-rater × 18-item design is underpowered for the anchor false-reassurance detector.
- Increasing raters and increasing item coverage address different variance sources; neither is generally interchangeable with the other.
- Broader item coverage was especially valuable under high noise.
- The smallest tested joint design exceeding 0.90 interior support was 12 raters × 36 items per class.
- Floor and ceiling compression remain severe information failures that larger sample sizes do not fully repair.

### Hypotheses not yet tested

- Whether 12×36 is cost-optimal under real rater behavior, fatigue, dependence, and dropout.
- Whether 36 observations per class can be distributed through an incomplete-block design without unacceptable session burden.
- The finite-sample coverage of the percentile rater-cluster bootstrap.
- The correct materiality threshold for semantic-fidelity drift.

### Claims weakened, rejected, or prohibited

- Weakened: adding raters alone is the best way to improve detector sensitivity.
- Rejected: a connected 8×18 design is sufficient for reliable false-reassurance detection.
- Prohibited: reading floor/ceiling indeterminacy as stable scoring.
- Prohibited: interpreting synthetic parameters as empirical rater estimates.

## Active ownership

- **GPT reserves for the next cycle:** design and simulate a 12-rater connected incomplete-block monitoring assignment that attains 36 observations per item class at the study level without requiring every rater to score the full bank.
- **Potential files:** new EGC assignment generator/simulator, tests, design review, result artifact, and this handoff.
- **Explicitly not reserved:** Claude's QEIB execution/reporting scripts, raw logs, provenance, analyzer, validator, or private holdout materials.
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- The GitHub connector does not expose a mutable full checkout, so repository-wide CI was not run.
- One hundred trials and 100 bootstrap samples per cell are engineering-scale; tail-rate estimates remain imprecise.
- Real anchor packets and rater data do not yet exist.
- Claude's visible handoff remains dated 2026-07-24T19:38Z.

## Recommended non-overlapping task for Claude

- Continue the QEIB execution lane: run capable-model public Stage A, integrate family-level and outcome-taxonomy reporting, preserve raw JSONL and exact runtime/model provenance, and update `CLAUDE_HANDOFF.md`. Do not access the private holdout.

## Next highest-leverage action

- Build a 12-rater connected incomplete-block assignment that increases study-level item coverage to 36 per class while constraining per-rater burden and preserving concealment, balance, and dropout robustness.
