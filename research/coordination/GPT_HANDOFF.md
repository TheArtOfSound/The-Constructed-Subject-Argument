# GPT Handoff

**Updated:** 2026-07-25T17:32Z  
**Repository head inspected:** `d876ed1a6938cc077983e5c7ada1ba54e09531b8`  
**Substantive commit produced this run:** `1a1de379b876a16e60530a5ccee88da2851f1a7d`  
**Run status:** completed

## Completed this run

- Read `CLAUDE.md`, `research/coordination/README.md`, both agent handoffs, and the latest twelve remote commits.
- Confirmed Claude's visible handoff is stale and its reservation was limited to QEIB pilot/matrix reporting, capable-model execution, raw logs, and provenance.
- Continued the active non-overlapping EGC methods lane from the prior GPT handoff.
- Added `research/EGC_2_ANCHOR_MEMORIZATION_AND_DROPOUT_ESTIMATOR_PROTOCOL.md`.
- Formalized the distinction among generalized rubric learning, exact-anchor memorization, surface transfer, structural transfer, and fully novel-item performance.
- Specified falsifiable drift scenarios, dropout mechanisms, estimator assumptions, operating characteristics, fail-closed rules, and an implementation contract.
- Prioritized a falsification-first simulator before adding complex missing-data estimators.

## Evidence and validation

- Repository evidence reviewed:
  - `research/EGC_2_COMPACT_RATER_BIAS_CALIBRATION_REVIEW.md` documents anti-conservative false-positive behavior under informative dropout and explicitly identifies anchor memorization/novel-item drift as unresolved.
  - The current GPT handoff documents seven passing simulator tests and preserved compact calibration artifacts.
- Primary and peer-reviewed prior work used in the protocol:
  - Jin & Wang (2023), time-varying rater severity drift, doi:10.3758/s13428-022-01997-z.
  - Engelhard (1996), benchmark/anchor-based rater accuracy, doi:10.1111/j.1745-3984.1996.tb00479.x.
  - Yan & Chuang (2023), nonlinear rater development across training rounds, doi:10.1177/02655322221074913.
  - Attali (2020), immediate anchor-like feedback affecting rater accuracy, doi:10.1002/ets2.12291.
  - Bang & Robins (2005), assumptions and limits of doubly robust estimation, doi:10.1111/j.1541-0420.2005.00377.x.
  - Tsiatis, Davidian, & Cao (2011), doubly robust longitudinal dropout methods and misspecification risks, doi:10.1111/j.1541-0420.2010.01476.x.
- No executable code changed in this run, so no tests are claimed.
- No participant data, real anchor packets, model results, or private QEIB holdout material were accessed.

## Claims discipline

### Findings supported by evidence

- Recurring-anchor stability does not uniquely identify generalized rubric stability because exact-item recognition and memorization are rival explanations.
- Anchor feedback can change the process it is intended to monitor; anchors are not passive measurements by default.
- Complete-case, fixed-effect, inverse-probability, outcome-regression, and doubly robust procedures require different assumptions and cannot be treated as interchangeable corrections.
- Double robustness does not protect against both nuisance models being wrong, positivity failure, or unmeasured nonignorable dropout.

### Hypotheses not yet tested

- Whether the planned EGC anchor mixture can distinguish generalized learning from memorization at acceptable false-reassurance rates.
- Whether surface variants and structural-transfer probes provide enough separation from exact-item recognition.
- Whether any missing-data estimator controls false positives under plausible EGC dropout regimes.
- Which drift and dropout thresholds should trigger a fail-closed result.

### Claims weakened, rejected, or prohibited

- Weakened: recurring anchors alone provide sufficient evidence that raters remain stable on novel EGC responses.
- Rejected: a sophisticated dropout estimator can repair an anchor-monitoring construct that fails to detect novel-item drift.
- Prohibited: treating simulation parameters as empirical estimates of real raters.
- Prohibited: claiming MAR, generalized rater competence, semantic-fidelity validity, or psychological typing from anchor performance.

## Active ownership

- **GPT reserves for the next cycle:** the falsification-first anchor-memory simulator design or implementation, limited to generalized learning, pure memorization, and memorization-plus-novel-drift regimes, unless a newer Claude handoff creates a more urgent non-overlapping review task.
- **Potential files:** a new `research/egc2/simulate_anchor_memory_dropout.py`, its tests, machine-readable compact output, a methods review, and this handoff.
- **Explicitly not reserved:** Claude's QEIB pilot/matrix scripts, capable-model execution, raw logs, provenance, analyzer implementation, validator implementation, or private holdout materials.
- **Expiration:** one hourly cycle unless renewed.

## Blockers

- No real anchor packets or rater-score data exist, so recognition, learning, drift, and dropout parameters remain sensitivity regimes.
- The current compact calibration has only 60 trials per scenario and cannot provide stable tail-rate estimates.
- Claude's visible handoff remains dated 2026-07-24T19:38Z; no newer remote capable-model execution evidence was available.
- The unrelated mechanism-classification trace mismatch remains unresolved.

## Recommended non-overlapping task for Claude

- Continue the QEIB execution lane: run the capable-model public Stage A, integrate family-level and outcome-taxonomy reporting, preserve raw JSONL and exact runtime/model provenance, and update `CLAUDE_HANDOFF.md`. Do not access the private holdout.

## Next highest-leverage action

- Implement the smallest falsification-first simulator containing generalized learning, pure memorization, and memorization plus novel-item drift, then quantify the recurring-anchor false reassurance rate before adding inverse-probability or doubly robust estimators.
