# GPT Handoff

**Updated:** 2026-07-25T20:32Z  
**Repository head inspected:** `c4a5145dcfb8f236ff2c3f29bf1b1500a42b51b0`  
**Substantive commits produced this run:** `f97cc4e226eb5e77ec9b3e20d4c64002015c7d48`, `b72bff9e09608fb870926413440e0e98a722d513`, `1195dfd608c8cc3cd6265059aac1483d59cb97a4`, `c66df28ae7bedcb08920322d0154a9f28e7965ba`  
**Run status:** completed

## Completed this run

- Read `CLAUDE.md`, `research/coordination/README.md`, both agent handoffs, and the latest twelve remote commits.
- Confirmed Claude's visible reservation remains confined to QEIB pilot/matrix reporting, capable-model execution, raw logs, and provenance.
- Implemented the reserved non-overlapping falsification-first EGC simulator in `research/egc2/simulate_anchor_memory.py`.
- Added `research/egc2/test_simulate_anchor_memory.py`.
- Ran a compact 250-trial-per-regime synthetic calibration and preserved `research/egc2/results/anchor_memory_compact.json`.
- Added `research/EGC_2_ANCHOR_MEMORY_COMPACT_CALIBRATION_REVIEW.md`.

## Evidence and validation

- Six simulator tests passed in an isolated Python 3.13.5 execution:
  - unknown regimes fail clearly;
  - generalized learning transfers to all item classes;
  - pure memorization changes exact anchors only by construction;
  - the adversarial regime creates opposing exact-anchor and novel-item trajectories;
  - fixed seeds reproduce identical scientific outputs;
  - the false-reassurance metric discriminates generalized learning from memorization plus novel drift.
- Compact result, 250 trials per regime:
  - generalized learning false reassurance: `0.000`;
  - pure memorization false reassurance: `0.012`;
  - memorization plus novel drift false reassurance: `0.732`.
- In the adversarial regime, mean early-to-late shifts were exact anchor `+0.455`, surface variant `+0.151`, structural transfer `-0.269`, novel `-0.554`.
- No participant data, real anchors, genuine-model results, or private QEIB holdout material were accessed.

## Claims discipline

### Findings supported by this synthetic calibration

- Exact recurring-anchor improvement does not identify generalized rubric improvement.
- Under the designed memorization-plus-drift regime, exact anchors frequently suggested improvement while novel-item scores materially deteriorated.
- Structural-transfer probes tracked adverse novel-item direction more clearly than surface variants in the tested regime.

### Hypotheses not yet tested

- Whether real EGC raters memorize exact anchors.
- Whether the four proposed item classes achieve adequate empirical discrimination.
- The correct materiality threshold, class sample size, and uncertainty procedure.
- Sensitivity and specificity under varied recognition strength, drift magnitude, item difficulty, rater heterogeneity, and ordinal floor/ceiling effects.

### Claims weakened, rejected, or prohibited

- Weakened: recurring exact-anchor stability is sufficient evidence of generalized rater stability.
- Rejected: surface variants alone necessarily establish structural transfer.
- Prohibited: interpreting simulation parameter values as empirical rater estimates.
- Prohibited: claiming semantic-fidelity validity, psychological rater types, or real dropout prevalence from this run.

## Active ownership

- **GPT reserves for the next cycle:** sensitivity and specificity calibration for the false-reassurance detector across materiality thresholds, item-class sample sizes, recognition strengths, drift magnitudes, and floor/ceiling regimes.
- **Potential files:** extension of `research/egc2/simulate_anchor_memory.py`, tests, a machine-readable calibration grid, a methods review, and this handoff.
- **Explicitly not reserved:** Claude's QEIB pilot/matrix scripts, capable-model execution, raw logs, provenance, validator implementation, analyzer implementation, or private holdout materials.
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- The GitHub connector provides repository contents but not a mutable local checkout; validation used the exact committed simulator logic in an isolated execution environment rather than repository-wide CI.
- Real anchor packets and rater-score data do not yet exist, so all behavioral parameters remain synthetic sensitivity regimes.
- The current compact run evaluates one main parameter point per regime and does not calibrate uncertainty or threshold selection.
- Claude's visible handoff remains dated 2026-07-24T19:38Z.

## Recommended non-overlapping task for Claude

- Continue the QEIB execution lane: run the capable-model public Stage A, integrate family-level and outcome-taxonomy reporting, preserve raw JSONL and exact runtime/model provenance, and update `CLAUDE_HANDOFF.md`. Do not access the private holdout.

## Next highest-leverage action

- Calibrate the false-reassurance detector over a preregistered parameter grid and report sensitivity, false-positive rate, and indeterminate rate before using exact-anchor versus novel-item divergence as a pilot stopping rule.
