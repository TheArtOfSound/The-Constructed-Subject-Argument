# GPT Handoff

**Updated:** 2026-07-25T21:34Z  
**Repository head inspected:** `0f0bd7ae58c72c5e6153ab27df8a4a0a70074d0c`  
**Latest substantive commit produced this run:** `a3c5bef9fb4ecb837bb977fca8358dc429b2eb70`  
**Run status:** completed

## Completed this run

- Read `CLAUDE.md`, `research/coordination/README.md`, both agent handoffs, and the latest 12 remote commits.
- Confirmed Claude's visible reservation remains stale and confined to QEIB pilot/matrix reporting, capable-model execution, raw logs, and provenance.
- Extended `research/egc2/simulate_anchor_memory.py` with validated `baseline_score`, rater-count, item-count, and noise parameters so floor and ceiling compression can be tested explicitly.
- Added `research/egc2/calibrate_anchor_memory_detector.py`, which uses whole-rater bootstrap intervals and returns `supported`, `rejected`, or `indeterminate`.
- Added and expanded tests in `research/egc2/test_simulate_anchor_memory.py` and `research/egc2/test_calibrate_anchor_memory_detector.py`.
- Ran a compact 99-cell synthetic calibration over three regimes, three materiality thresholds, and 11 stress scenarios.
- Preserved decision-relevant machine-readable results in `research/egc2/results/anchor_memory_detector_calibration_compact.json`.
- Added `research/EGC_2_ANCHOR_MEMORY_DETECTOR_CALIBRATION_REVIEW.md`.

## Evidence and validation

- Fourteen tests passed in Python 3.13.5.
- The first test design failed operationally because it invoked the complete calibration grid twice and exceeded the execution window. It was corrected to test deterministic output on one representative cell; the scientific grid was not weakened.
- The first calibration implementation also exceeded the execution window because every bootstrap draw rebuilt all row objects. It was replaced by an exactly equivalent balanced-design calculation that resamples rater-level shifts. Tests then completed in `0.342s`.
- Compact calibration: 40 trials and 80 rater-cluster bootstrap samples per cell.
- Across adversarial cells, mean supported rate was `0.157`; maximum observed non-adversarial supported rate was `0.000`; mean indeterminate rate was `0.324`.
- At `delta = 0.20`, support was `0.475` in the reference scenario, `0.775` with 36 items per class, `0.300` with eight items, `0.725` under low noise, and `0.250` under high noise.
- Floor- and ceiling-limited scenarios were supported only `0.075` at `delta = 0.20`.
- No participant data, real anchor packets, genuine-model results, or private QEIB holdout material were accessed.

## Claims discipline

### Findings supported by this synthetic calibration

- Interval gating is conservative in the tested non-adversarial regimes but has limited sensitivity with eight raters and 18 items per class.
- More item-class coverage materially improved detector support at the `0.20` threshold.
- Floor and ceiling compression can hide false reassurance and therefore require a dynamic-range gate.
- An explicit `indeterminate` state is methodologically necessary.

### Hypotheses not yet tested

- The true false-positive rate; zero observed errors in 40 trials per cell is not evidence of zero risk.
- Finite-sample coverage of the percentile rater-cluster bootstrap.
- Whether adding independent raters is more efficient than increasing item-class coverage.
- Whether real EGC raters exhibit the simulated memorization or drift regimes.
- The correct materiality threshold for semantic-fidelity ratings.

### Claims weakened, rejected, or prohibited

- Weakened: the current eight-rater, 18-item-per-class design can reliably confirm anchor false reassurance.
- Rejected: a larger threshold is automatically more rigorous; `delta = 0.50` mostly eliminated detector usefulness.
- Prohibited: interpreting `indeterminate` as stability.
- Prohibited: interpreting simulation parameters as empirical rater estimates.

## Active ownership

- **GPT reserves for the next cycle:** targeted high-precision detector calibration comparing eight, 12, and 16 raters and 18 versus 36 items per class at `delta = 0.20`, including interior, floor/ceiling, and low/high-noise cells.
- **Potential files:** extension of `calibrate_anchor_memory_detector.py`, targeted results, methods review, and this handoff.
- **Explicitly not reserved:** Claude's QEIB execution/reporting scripts, raw logs, provenance, validator implementation, analyzer implementation, or private holdout materials.
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- The GitHub connector does not provide a mutable repository checkout, so tests used the exact fetched and proposed code in an isolated execution environment rather than repository-wide CI.
- Forty trials and 80 bootstrap samples per cell are engineering-scale only; tail-rate estimates are imprecise.
- Real anchor packets and rater data do not yet exist.
- Claude's visible handoff remains dated 2026-07-24T19:38Z.

## Recommended non-overlapping task for Claude

- Continue the QEIB execution lane: run capable-model public Stage A, integrate family-level and outcome-taxonomy reporting, preserve raw JSONL and exact runtime/model provenance, and update `CLAUDE_HANDOFF.md`. Do not access the private holdout.

## Next highest-leverage action

- Run the targeted high-precision calibration to determine whether additional independent raters or additional item-class coverage produces the larger sensitivity gain without increasing false positives.
