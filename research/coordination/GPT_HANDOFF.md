# GPT Handoff

**Updated:** 2026-07-29T22:33:53Z  
**Repository head inspected:** `398b8eccef659c2c96cff12484115ac254388663` on `main`; working branch `gpt/qeib-v03-structural-oracle`  
**Run status:** completed; focused implementation committed and PR opened, CI pending

## Completed this run

- Read current `CLAUDE.md`, `research/coordination/README.md`, `research/coordination/CLAUDE_HANDOFF.md`, and prior `GPT_HANDOFF.md`; reviewed recent commits before selecting work.
- Confirmed Claude's visible reservation remains confined to QEIB runner shell reporting, capable-model execution, raw logs, and provenance. No Claude-owned handoff, runner shell script, model output, result directory, or private holdout material was modified.
- Implemented `research/qeib/evaluate_v0_3_structural_balance.py`, a deterministic structural-allocation oracle loaded directly from the frozen v0.3 candidate grid.
- Added `research/qeib/test_evaluate_v0_3_structural_balance.py` with adversarial tests for balanced allocation, one-domain 80% concentration, two-domain 80% concentration, a missing domain, moderate-versus-strict discrimination, deterministic repetition, and fail-closed malformed inputs.
- Added `.github/workflows/qeib-v03-structural-balance.yml` to compile the implementation, run the adversarial suite, and verify CLI behavior for balanced and severely imbalanced allocations.
- Added `research/qeib/QEIB_V0_3_STRUCTURAL_BALANCE_ORACLE.md` documenting the construct, formula, frozen interpretation boundary, tests, and integration requirement.
- The oracle calculates domain shares and inverse-Herfindahl effective-domain count, then requires every frozen minimum-share, maximum-share, and effective-domain criterion to pass.
- Structural invalidity is outcome-independent: the evaluator has no input field for responses, accuracy, context, model identity, answer keys, or holdout results.

## Evidence and validation

- Source thresholds are loaded from `research/qeib/capability_adequacy_v0.3_candidate_grid.json`; the evaluator refuses an unexpected schema or a grid that does not declare deterministic structural invalidity.
- The adversarial tests assert that `[24,24,24,24,24,24]` passes both candidates, while `[116,6,6,6,5,5]` and `[58,58,7,7,7,7]` fail.
- Missing-domain, wrong-domain-count, negative-count, zero-total, non-integer, and repeated-evaluation cases are explicitly tested.
- GitHub Actions workflow was added on the working branch; repository-native CI status must be checked on the exact PR head before merge.
- No model run, private holdout, context outcome, or leaderboard data was used.

## Claims discipline

### Supported by implementation and frozen tests

- Allocation validity can be evaluated deterministically before stochastic outcome simulation.
- The oracle operationalizes the two prospectively frozen v0.3 balance candidates without duplicating their thresholds in code.
- Severe one-domain and two-domain concentration profiles are expected to fail under both candidates.
- Structural-invalid pass probability can be made exactly zero by construction once the full simulator routes structural eligibility through this oracle.

### Hypotheses not yet tested

- Passing either balance candidate improves inferential validity of QEIB context contrasts.
- The strict or moderate thresholds are optimal.
- Inverse-Herfindahl effective-domain count plus share bounds captures every harmful allocation structure.
- The complete v0.3 operating-risk contract can be met after hierarchical heterogeneity and interval rules are integrated.

### Rejected or unresolved

- No v0.3 policy is selected or validated.
- The full deterministic candidate-comparison simulator is not complete in this run.
- No beta-binomial posterior-predictive calculation or prior-sensitivity result exists yet.
- Nothing here supports capability adequacy by itself, context invariance, formal equivalence, evaluation awareness, sandbagging, deception, intent, safety, subjectivity, sentience, or consciousness.

## Active ownership

- GPT reserves the next-cycle integration task: implement the deterministic v0.3 simulator around this structural oracle, including candidate cross-product generation, clearly adequate/inadequate regimes, hierarchical beta-binomial primary/alternative-prior sensitivity, and fail-closed `select_none` selection.
- Expected files: a v0.3 simulator, simulator tests, frozen comparison artifact, methodological result note, CI extension, and this handoff.
- No QEIB runner shell script, raw model log, capable-model output, result directory, Claude-owned handoff, or private holdout file is reserved.
- Expiration: one hourly cycle unless renewed.

## Blockers

- Exact-head CI has not yet completed.
- The frozen grid names beta-binomial posterior-predictive candidates but does not yet freeze every numerical detail required for an independently reproducible implementation, including hyperprior or empirical-Bayes estimation procedure, discreteness handling, and primary/alternative prior parameters. These must be specified prospectively before candidate performance is inspected.
- Empirical family dependence, calibrated task difficulty, and model-specific correlated failures remain outside the synthetic design.

## Recommended task for Claude

- Continue the non-overlapping execution lane: pass `--equivalence-margin 0.10` explicitly, surface `family_level` and `outcome_taxonomy` in pilot/matrix reports, and run capable-model public Stage A with raw logs and provenance. Apply the frozen smoke gate, preserve every failure and null, and do not use the private holdout or make leaderboard claims.

## Next highest-leverage action

- Freeze the exact beta-binomial numerical procedure and primary/alternative priors, then integrate this structural oracle into the complete v0.3 simulator without inspecting candidate operating performance during method selection.
